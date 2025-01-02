import math
import re
from nltk.corpus import stopwords
import nltk
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import uvicorn
from nltk.tokenize import sent_tokenize
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

nepaliNewsSites = ['merolagani', 'bizshala', 'bizpati', 'arthasarokar', 'onlinekhabar', 'ratopati', 'setopati', 'rajdhanidaily',
                   'nagariknews', 'abhiyandaily', 'karobardaily', 'himalkhabar', 'arthapath', 'capitalnepal', 'ukeraa', 'clickmandu',
                   'globalaawaj', 'nepalviews', 'nepalpress', 'khabarhub', 'nepalipatra', 'meroauto', 'gorkhapatraonline', 'annapurnapost',
                   'thehimalayantimes', 'nepalnews', 'newsofnepal', 'souryaonline', 'ujyaaloonline', 'arthakendra', 'bizkhabar', 'news24nepal',
                   'baahrakhari', 'nepalkhabar', 'nepalsamaya', 'techpana']

app = FastAPI()

class URLRequest(BaseModel):
    url: str


@app.get("/summarize")
def summarize_url(url: str = Query(...)):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    lan = 'en'
    if any(site in url for site in nepaliNewsSites):
        lan = 'hi'

    # Extract content using Playwright
    def extract_content_with_playwright(url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            content = page.content()  # Extract HTML
            text = page.inner_text('body')  # Extract readable text from <body>
            browser.close()
            return content, text

    try:
        html_content, text_content = extract_content_with_playwright(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching the URL: {str(e)}")

    if lan == 'en':
        parser = PlaintextParser.from_string(text_content, Tokenizer("english"))
        summarizer = TextRankSummarizer(Stemmer("english"))
        summarizer.stop_words = get_stop_words("english")

        summary = " ".join([str(sentence) for sentence in summarizer(parser.document, 5)])
        return {"summary": summary}

    # Nepali summarization
    sents = re.split('।', text_content)
    documents_size = len(sents)

    def create_frequency_matrix(sentences):
        frequency_matrix = {}
        stopWords = set(stopwords.words("nepali"))

        for sent in sentences:
            freq_table = {}
            words = sent.split()
            for word in words:
                if word in stopWords:
                    continue

                if word in freq_table:
                    freq_table[word] += 1
                else:
                    freq_table[word] = 1

            frequency_matrix[sent[:10]] = freq_table

        return frequency_matrix

    freq_matrix = create_frequency_matrix(sents)

    def create_tf_matrix(freq_matrix):
        tf_matrix = {}

        for sent, f_table in freq_matrix.items():
            tf_table = {}

            count_words_in_sentence = len(f_table)
            for word, count in f_table.items():
                tf_table[word] = count / count_words_in_sentence

            tf_matrix[sent] = tf_table

        return tf_matrix

    tf_matrix = create_tf_matrix(freq_matrix)

    def create_documents_per_words(freq_matrix):
        word_per_doc_table = {}

        for sent, f_table in freq_matrix.items():
            for word, count in f_table.items():
                if word in word_per_doc_table:
                    word_per_doc_table[word] += 1
                else:
                    word_per_doc_table[word] = 1

        return word_per_doc_table

    count_doc_per_words = create_documents_per_words(freq_matrix)

    def create_idf_matrix(freq_matrix, count_doc_per_words, documents_size):
        idf_matrix = {}

        for sent, f_table in freq_matrix.items():
            idf_table = {}

            for word in f_table.keys():
                idf_table[word] = math.log10(documents_size / float(count_doc_per_words[word]))

            idf_matrix[sent] = idf_table

        return idf_matrix

    idf_matrix = create_idf_matrix(freq_matrix, count_doc_per_words, documents_size)

    def create_tf_idf_matrix(tf_matrix, idf_matrix):
        tf_idf_matrix = {}

        for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):

            tf_idf_table = {}

            for (word1, value1), (word2, value2) in zip(f_table1.items(),
                                                        f_table2.items()):
                tf_idf_table[word1] = float(value1 * value2)

            tf_idf_matrix[sent1] = tf_idf_table

        return tf_idf_matrix

    tf_idf_matrix = create_tf_idf_matrix(tf_matrix, idf_matrix)

    def sentence_scores(tf_idf_matrix) -> dict:
        sentenceValue = {}

        for sent, f_table in tf_idf_matrix.items():
            total_score_per_sentence = 0

            count_words_in_sentence = len(f_table)
            for word, score in f_table.items():
                total_score_per_sentence += score
            if count_words_in_sentence != 0:
                sentenceValue[sent] = total_score_per_sentence / count_words_in_sentence
            else:
                sentenceValue[sent] = 0
        return sentenceValue

    sentence_scores = sentence_scores(tf_idf_matrix)

    def find_average_score(sentenceValue) -> int:
        sumValues = 0
        for entry in sentenceValue:
            sumValues += sentenceValue[entry]

        average = (sumValues / len(sentenceValue))

        return average

    threshold = find_average_score(sentence_scores)

    def clean_nepali_text(text: str) -> str:
        # Remove extra newlines and whitespace
        cleaned = re.sub(r'\n+', ' ', text)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        # Replace multiple dots with single dot
        cleaned = re.sub(r'।+', '।', cleaned)
        return cleaned.strip()

    def generate_summary(sentences, sentenceValue, threshold):
        summary = []

        for sentence in sentences:
            if sentence[:10] in sentenceValue and sentenceValue[sentence[:10]] >= threshold:
                summary.append(sentence)

        return summary

    summary = '।'.join(generate_summary(sents, sentence_scores, 0.8 * threshold))

    cleaned_summary = clean_nepali_text(summary)

    return {"summary": cleaned_summary}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8320)
