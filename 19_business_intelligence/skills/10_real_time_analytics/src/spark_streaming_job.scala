package com.analytics.spark

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger

object RealTimeAnalytics {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Real-Time Analytics")
      .config("spark.sql.shuffle.partitions", "100")
      .getOrCreate()
    
    import spark.implicits._
    
    // Read from Kafka
    val events = spark
      .readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "kafka:9092")
      .option("subscribe", "events")
      .option("startingOffsets", "latest")
      .load()
      .selectExpr("CAST(value AS STRING)")
      .select(from_json($"value", schema).as("data"))
      .select("data.*")
      .withWatermark("timestamp", "10 minutes")
    
    // Hourly aggregations
    val hourlyStats = events
      .groupBy(
        window($"timestamp", "1 hour"),
        $"event_type",
        $"country"
      )
      .agg(
        count("*").as("event_count"),
        sum("revenue").as("total_revenue"),
        approx_count_distinct("user_id").as("unique_users"),
        avg("session_duration").as("avg_duration")
      )
    
    // Write to ClickHouse
    val query = hourlyStats
      .writeStream
      .foreachBatch { (batchDF, batchId) =>
        batchDF.write
          .format("jdbc")
          .option("url", "jdbc:clickhouse://clickhouse:8123/analytics")
          .option("dbtable", "hourly_stats")
          .mode("append")
          .save()
      }
      .trigger(Trigger.ProcessingTime("1 minute"))
      .start()
    
    query.awaitTermination()
  }
}
