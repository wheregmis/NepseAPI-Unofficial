FROM python:3.10-slim

# Install git
RUN apt-get update && apt-get install -y git

COPY ./requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

RUN pip install --upgrade git+https://github.com/basic-bgnr/NepseUnofficialApi.git

COPY . .
CMD ["python", "server.py"]
