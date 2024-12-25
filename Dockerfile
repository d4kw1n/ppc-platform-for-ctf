# Sử dụng Python base image
FROM python:3.9-slim

RUN apt-get update && apt-get install -y software-properties-common && \
    apt-add-repository 'deb http://deb.debian.org/debian bookworm main' && \
    apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    openjdk-17-jdk \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/problems

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run"]
