from faker import Faker
import pandas as pd
import random

fake = Faker()

# Generate synthetic data
def generate_synthetic_data(num_records=17000):
    data = []
    for _ in range(num_records):
        user_id = random.randint(1, 1000)
        product_id = random.randint(1, 500)
        rating = random.randint(1, 5)
        timestamp = fake.date_this_decade().strftime('%Y-%m-%d %H:%M:%S')
        data.append([user_id, product_id, rating, timestamp])

    df = pd.DataFrame(data, columns=["user_id", "product_id", "rating", "timestamp"])
    df.to_csv("data/synthetic_data.csv", index=False)
    print("Data generated and saved to 'data/synthetic_data.csv'.")

if __name__ == "__main__":
    generate_synthetic_data()
