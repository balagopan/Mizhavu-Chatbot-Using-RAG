FROM node:18-slim AS builder
WORKDIR /app
COPY client/package*.json ./client/
RUN cd client && npm install
COPY client/ .
RUN cd client && npm run build && npm run export

FROM python:3.12-slim
RUN apt-get update && apt-get install -y libmagic1 tesseract-ocr libtesseract-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

COPY --from=builder /app/client/out ./client/out

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]