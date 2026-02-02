FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.inference.txt .
RUN pip install --no-cache-dir -r requirements.inference.txt

COPY . .

EXPOSE 8080

ENV PYTHONPATH=/app/src
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
