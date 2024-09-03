FROM python:3.12-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN pip install --upgrade git+https://github.com/basic-bgnr/NepseUnofficialApi.git

COPY . .
CMD ["python", "server.py"]
