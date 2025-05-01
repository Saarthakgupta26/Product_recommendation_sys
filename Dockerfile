FROM bitnami/spark:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY spark_streaming /app
