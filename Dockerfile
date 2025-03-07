# Builder stage
FROM python:3.12.8-alpine AS builder

# Install only necessary build dependencies
RUN apk add --no-cache git gcc musl-dev

WORKDIR /app
COPY requirements.txt .

# Install requirements
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12.8-alpine
WORKDIR /app

# Copy built packages and app code
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY server.py ./
COPY socketServer.py ./

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost:8000'); conn.request('GET', '/health'); response = conn.getresponse(); exit(0) if response.status == 200 else exit(1)"

EXPOSE 8000 5555

CMD ["sh", "-c", "python server.py & python socketServer.py & wait"]