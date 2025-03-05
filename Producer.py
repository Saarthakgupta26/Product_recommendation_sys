from faker import Faker
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

faker = Faker()


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



# Kafka Configuration
KAFKA_TOPIC = "sales"
producer = create_producer()

# Define product catalog with categories and prices
product_catalog = [
    {"id": 1, "name": "Laptop", "category": "Electronics", "price": 1200},
    {"id": 2, "name": "Smartphone", "category": "Electronics", "price": 800},
    {"id": 3, "name": "Headphones", "category": "Accessories", "price": 150},
    {"id": 4, "name": "Coffee Maker", "category": "Home Appliances", "price": 100},
    {"id": 5, "name": "Blender", "category": "Home Appliances", "price": 80},
    {"id": 6, "name": "Bookshelf", "category": "Furniture", "price": 200},
    {"id": 7, "name": "Running Shoes", "category": "Clothing", "price": 120},
    {"id": 8, "name": "Jacket", "category": "Clothing", "price": 180},
    {"id": 9, "name": "Yoga Mat", "category": "Fitness", "price": 50},
    {"id": 10, "name": "Dumbbells", "category": "Fitness", "price": 70}
]

# Generate realistic sales events
def generate_sales_data():
    customer = {
        "id": random.randint(1, 1000),  # Simulate 1000 unique customers
        "name": faker.name(),
        "email": faker.email(),
        "location": faker.city(),
        "age": random.randint(18, 65)
    }
    product = random.choice(product_catalog)
    purchase_quantity = random.randint(1, 5)
    sale_event = {
        'user': customer["id"],
        'customer_data': customer,
        'product': product["id"],
        'product_data': product,
        'quantity': purchase_quantity,
        'total_price': product["price"] * purchase_quantity,
        'timestamp': int(time.time())
    }
    return sale_event

# Simulate a continuous data stream
print("Starting to produce sales events...")
try:
    while True:
        sales_data = generate_sales_data()
        producer.send(KAFKA_TOPIC, sales_data)
        print(f"Produced: {sales_data}")
        time.sleep(random.uniform(0.2, 3.0))  # Simulate variable delay between sales
except KeyboardInterrupt:
    print("Stopping producer.")
finally:
    producer.close()
