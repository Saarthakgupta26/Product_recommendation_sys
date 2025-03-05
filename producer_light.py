from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_producer():
    retries = 0
    max_retries = 10
    while retries < max_retries:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['kafka:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Successfully connected to Kafka")
            return producer
        except NoBrokersAvailable:
            retries += 1
            logger.warning(f"No brokers available. Retrying in 5 seconds... (Attempt {retries}/{max_retries})")
            time.sleep(5)
    
    raise Exception("Failed to connect to Kafka after maximum retries")

products = ['product1', 'product2', 'product3', 'product4', 'product5']
users = ['user1', 'user2', 'user3', 'user4', 'user5']

producer = create_producer()

while True:
    user = random.choice(users)
    product = random.choice(products)
    quantity = random.randint(1, 10)
    
    sale = {
        'user': user,
        'product': product,
        'quantity': quantity,
        'timestamp': int(time.time())
    }
    
    producer.send('sales', sale)
    logger.info(f"Sent: {sale}")
    time.sleep(1)
