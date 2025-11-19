"""Session Analytics with Spark Streaming"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder.appName("SessionAnalytics").getOrCreate()

events = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "events") \
    .load()

parsed = events.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Sessionize using 30-minute gap
sessions = parsed \
    .withWatermark("timestamp", "30 minutes") \
    .groupBy("user_id", session_window("timestamp", "30 minutes")) \
    .agg(
        count("*").alias("events_in_session"),
        collect_list("page").alias("pages_visited"),
        sum("revenue").alias("session_revenue"),
        min("timestamp").alias("session_start"),
        max("timestamp").alias("session_end")
    )

query = sessions.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()
