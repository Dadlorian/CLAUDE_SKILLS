# Spark Structured Streaming Pipeline Guide

## Read from Kafka
```scala
val df = spark
  .readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "kafka:9092")
  .option("subscribe", "events")
  .load()
```

## Parse and Transform
```scala
val events = df
  .selectExpr("CAST(value AS STRING)")
  .select(from_json($"value", schema).as("data"))
  .select("data.*")
  .withWatermark("timestamp", "10 minutes")
```

## Aggregations
```scala
val stats = events
  .groupBy(window($"timestamp", "5 minutes"), $"event_type")
  .agg(
    count("*").as("count"),
    sum("revenue").as("revenue")
  )
```

## Write to Sink
```scala
stats
  .writeStream
  .format("parquet")
  .option("path", "s3://output/")
  .option("checkpointLocation", "s3://checkpoints/")
  .trigger(Trigger.ProcessingTime("30 seconds"))
  .start()
```
