# Product_recommendation_sys
In the era of big data, real-time processing and analysis have become crucial for businesses to provide personalized experiences to their customers. Product recommendation systems are a key component in e-commerce platforms, enhancing user engagement and sales by suggesting relevant products. Leveraging technologies like Apache Spark and Kafka allows for the development of scalable and efficient real-time recommendation systems

# Objective
Develop a real-time product recommendation system using Apache Spark and Kafka. 
Process streaming sales data to generate timely and relevant product recommendations.
Visualize the recommendation results for analysis and improvement.

# Key Components and Capabilities
- Stream Processing
- Data Accumulation
- Machine Learning Model
- Model Evaluation
- Graph-based Representation
- Data Visualization
- Data Export
- Error Handling and Logging
- Scalability
- Flexibility
- Real-time Updates

# Stack
1 Docker
2 Python
3 Spark (PySpark)
  -Streaming
  -SQL
  -MLlib
  -Graphx
4 Kafka
5 Zookeeper

# How It Works
# 1. Data Ingestion
 - Sales data is ingested into the system through Kafka.
- Each record carries information on a user's buy (user ID, product ID, quantity, timestamp).
# 2. Stream Processing
 - Apache Spark's structured streaming processes the incoming data.
 - Data is streamed until a substantial amount is reached (configurable threshold).
# 3. Data Preparation
 -After enough data is reached, it's prepared for training of the model:
 -User and product IDs are indexed.
 -Data is grouped to form user-product interaction matrix.
# 4. Model Training
 -An Alternating Least Squares (ALS) collaborative filtering model is trained with Spark MLlib.
 -The data is divided into training and test sets.
# 5. Recommendation Generation
 - he trained model produces top N product recommendations for every user.
# 6. Evaluation
 -The performance of the model is measured using Root Mean Square Error (RMSE) on the test set.
# 7. Graph Construction
 -A graph is formed from the recommendations:
 -Nodes are users and products.
- Edges denote recommendations.
# 8. Data Export
 - The graph data (edges and vertices) is exported in the form of CSV files.
# 9. Visualization
 -Three key visualizations are produced:
    -User-Product Recommendation Graph: Displays the network of users and suggested products.
    -Degree Distribution Plot: Presents the distribution of links in the network.
    -Top Recommended Products Chart: Indicating the most recommended products.
