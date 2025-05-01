#!/bin/sh

echo "Waiting for Kafka to be ready..."
while ! nc -z kafka 9092; do
  sleep 1
done
echo "Kafka is ready."

python producer.py
