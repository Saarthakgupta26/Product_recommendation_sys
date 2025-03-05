from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode, collect_list
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import StringIndexer
from graphframes import GraphFrame

# Spark session
spark = SparkSession.builder \
    .appName("ProductRecommendation") \
    .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.2-s_2.12") \
    .getOrCreate()

# Schema for incoming data
schema = StructType([
    StructField("user", StringType(), True),
    StructField("product", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("timestamp", LongType(), True)
])

# Kafka streaming
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "sales") \
    .load()

# Parse JSON data
parsed_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

print("parsed_df", parsed_df)


# Init
accumulated_data = spark.createDataFrame([], schema)


# Process streaming data
def process_batch(df, epoch_id):
    global accumulated_data
    
    print(f"Received batch with {df.count()} rows")
    
    # Accumulate data
    if accumulated_data is None:
        accumulated_data = df
    else:
        accumulated_data = accumulated_data.union(df)
    
    print(f"Accumulated data count: {accumulated_data.count()}")
    
    # Check if we have enough data
    if accumulated_data.count() < 10:  # Lowered threshold for testing
        print(f"Not enough data yet. Current count: {accumulated_data.count()}")
        return
    
    print("Processing accumulated data...")
    
    # Convert string IDs to numeric IDs
    userIndexer = StringIndexer(inputCol="user", outputCol="userId")
    productIndexer = StringIndexer(inputCol="product", outputCol="productId")
    
    # Fit and transform the data
    user_product_df = userIndexer.fit(accumulated_data).transform(accumulated_data)
    user_product_df = productIndexer.fit(user_product_df).transform(user_product_df)
    
    # Prepare data for ALS model
    als_data = user_product_df.select("userId", "productId", "quantity") \
        .groupBy("userId", "productId") \
        .agg({"quantity": "sum"}) \
        .withColumnRenamed("sum(quantity)", "rating")
    
    # Split data into training and test sets
    (training, test) = als_data.randomSplit([0.8, 0.2])

    print("Training data schema:")
    training.printSchema()
    print(f"Training data count: {training.count()}")
    print(f"User count: {training.select('userId').distinct().count()}")
    print(f"Product count: {training.select('productId').distinct().count()}")

    print("Test data schema:")
    test.printSchema()
    print(f"Test data count: {test.count()}")
    
    # Build the recommendation model using ALS on the training data
    als = ALS(maxIter=10, regParam=0.01, userCol="userId", itemCol="productId", ratingCol="rating",
            coldStartStrategy="drop", nonnegative=True)
    model = als.fit(training)
    
    # Generate top 5 product recommendations for each user
    userRecs = model.recommendForAllUsers(5)
    
    print("userRecs schema:")
    userRecs.printSchema()
    
    # Create edges DataFrame
    edges = userRecs.select(
        col("userId").alias("src"),
        explode("recommendations").alias("rec")
    ).select(
        "src",
        col("rec.productId").alias("dst")
    )
    
    # Create vertices DataFrame
    users = user_product_df.select("userId").distinct()
    products = user_product_df.select("productId").distinct()
    vertices = users.withColumnRenamed("userId", "id").unionAll(products.withColumnRenamed("productId", "id"))
    
    # Create GraphFrame
    g = GraphFrame(vertices, edges)
    
    # Export the graph as CSV
    g.vertices.write.csv("/app/results/vertices.csv", mode="overwrite", header=True)
    g.edges.write.csv("/app/results/edges.csv", mode="overwrite", header=True)
    
    print(f"Graph data saved to /app/results/")
    
    # Join with original data to get string user and product names
    userMapping = user_product_df.select("user", "userId").distinct()
    productMapping = user_product_df.select("product", "productId").distinct()
    
    recommendations = userRecs \
        .join(userMapping, userRecs.userId == userMapping.userId) \
        .join(productMapping, col("productId") == productMapping.productId) \
        .select("user", "product")
    
    print("Recommendations:")
    recommendations.show(truncate=False)
    
    # Evaluate the model
    try:
        print(f"Test data count: {test.count()}")
        print(f"Distinct products in test set: {test.select('productId').distinct().count()}")
        
        with open("/app/results/test_info.txt", "w") as f:
            f.write(f"Test data count: {test.count()}\n")
            f.write(f"Distinct products in test set: {test.select('productId').distinct().count()}\n")
        
        if test.select('productId').distinct().count() > 0:
            print("Transforming test data...")
            predictions = model.transform(test)
            print(f"Predictions count: {predictions.count()}")
            
            with open("/app/results/predictions_info.txt", "w") as f:
                f.write(f"Predictions count: {predictions.count()}\n")
                f.write("Predictions schema:\n")
                predictions.printSchema(f)
            
            if predictions.count() > 0:
                evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
                rmse = evaluator.evaluate(predictions)
                print(f"Root-mean-square error = {rmse}")
                with open("/app/results/rmse.txt", "w") as f:
                    f.write(f"RMSE: {rmse}\n")
            else:
                print("No predictions were made. The model might not have enough data to make predictions.")
        else:
            print("Test set is empty or has no distinct products. Cannot evaluate the model.")
    except Exception as e:
        print(f"Error during model evaluation: {str(e)}")
        with open("/app/results/evaluation_error.txt", "w") as f:
            f.write(f"Error during model evaluation: {str(e)}\n")



# Start streaming query
query = parsed_df \
    .writeStream \
    .foreachBatch(process_batch) \
    .start()

query.awaitTermination()
