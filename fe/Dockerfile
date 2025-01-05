FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask requests

EXPOSE 5000

ENV NAME World

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
