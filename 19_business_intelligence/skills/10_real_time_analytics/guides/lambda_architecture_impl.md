# Lambda Architecture Implementation Guide

## Overview

This guide provides a step-by-step implementation of Lambda Architecture for real-time analytics, combining batch and speed layers for comprehensive data processing.

## Architecture Design

```
┌─────────────────┐
│  Data Sources   │
│ (Kafka/Kinesis) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼─────┐
│ Batch │ │ Speed  │
│ Layer │ │ Layer  │
│(Spark)│ │(Flink) │
└───┬───┘ └──┬─────┘
    │         │
    ↓         ↓
┌───┴─────────┴────┐
│  Serving Layer   │
│   (ClickHouse/   │
│     Druid)       │
└──────────────────┘
```

## Prerequisites

- Kafka cluster
- Spark cluster
- Flink cluster
- ClickHouse or Druid
- S3 or HDFS for data lake
- Schema Registry

## Step 1: Data Ingestion

### Kafka Topic Setup

```bash
# Create topic for raw events
kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic raw-events \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=604800000 \  # 7 days
  --config compression.type=lz4

# Create topic for batch processing trigger
kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic batch-trigger \
  --partitions 1 \
  --replication-factor 3
```

### Schema Definition

```json
{
  "type": "record",
  "name": "Event",
  "namespace": "com.analytics.events",
  "fields": [
    {"name": "event_id", "type": "string"},
    {"name": "user_id", "type": "long"},
    {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
    {"name": "event_type", "type": "string"},
    {"name": "properties", "type": {"type": "map", "values": "string"}},
    {"name": "revenue", "type": ["null", "double"], "default": null}
  ]
}
```

## Step 2: Batch Layer Implementation

### Spark Batch Job

```scala
package com.analytics.batch

import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._

object BatchProcessor {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Lambda-Batch-Layer")
      .config("spark.sql.adaptive.enabled", "true")
      .getOrCreate()

    import spark.implicits._

    // Read from data lake
    val startDate = args(0)  // "2025-01-15"
    val endDate = args(1)    // "2025-01-16"

    val events = spark.read
      .parquet(s"s3://data-lake/events/date=$startDate/*")
      .filter($"timestamp" >= startDate && $"timestamp" < endDate)

    // Compute aggregations
    val hourlyStats = computeHourlyStats(events)
    val userMetrics = computeUserMetrics(events)
    val productAnalytics = computeProductAnalytics(events)

    // Write to serving layer
    writeToClickHouse(hourlyStats, "hourly_stats_batch")
    writeToClickHouse(userMetrics, "user_metrics_batch")
    writeToClickHouse(productAnalytics, "product_analytics_batch")

    // Archive processed data
    events.write
      .mode("overwrite")
      .parquet(s"s3://data-lake/processed/date=$startDate/")

    spark.stop()
  }

  def computeHourlyStats(events: DataFrame): DataFrame = {
    events
      .withColumn("hour", date_trunc("hour", $"timestamp"))
      .groupBy($"hour", $"event_type", $"country")
      .agg(
        count("*").as("event_count"),
        sum("revenue").as("total_revenue"),
        approx_count_distinct("user_id").as("unique_users"),
        avg("session_duration").as("avg_session_duration"),
        percentile_approx("session_duration", 0.95).as("p95_session_duration")
      )
  }

  def computeUserMetrics(events: DataFrame): DataFrame = {
    events
      .groupBy($"user_id", date_trunc("day", $"timestamp").as("date"))
      .agg(
        count("*").as("daily_events"),
        countDistinct("session_id").as("sessions"),
        sum("revenue").as("daily_revenue"),
        min("timestamp").as("first_seen"),
        max("timestamp").as("last_seen")
      )
  }

  def computeProductAnalytics(events: DataFrame): DataFrame = {
    events
      .filter($"event_type" === "purchase")
      .groupBy($"product_id", date_trunc("day", $"timestamp").as("date"))
      .agg(
        count("*").as("purchase_count"),
        sum("quantity").as("total_quantity"),
        sum("revenue").as("total_revenue"),
        countDistinct("user_id").as("unique_buyers")
      )
  }

  def writeToClickHouse(df: DataFrame, table: String): Unit = {
    df.write
      .format("jdbc")
      .option("url", "jdbc:clickhouse://clickhouse:8123/analytics")
      .option("dbtable", table)
      .option("user", "default")
      .option("password", "")
      .option("batchsize", 10000)
      .mode("append")
      .save()
  }
}
```

### Scheduled Batch Processing

```yaml
# Airflow DAG
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'analytics',
    'depends_on_past': True,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email': ['team@example.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'lambda_batch_processing',
    default_args=default_args,
    description='Lambda architecture batch layer',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False
)

batch_job = SparkSubmitOperator(
    task_id='process_batch',
    application='/opt/spark/jobs/batch-processor.jar',
    java_class='com.analytics.batch.BatchProcessor',
    application_args=[
        '{{ ds }}',  # Start date
        '{{ tomorrow_ds }}'  # End date
    ],
    conf={
        'spark.executor.instances': '20',
        'spark.executor.memory': '8g',
        'spark.executor.cores': '4'
    },
    dag=dag
)
```

## Step 3: Speed Layer Implementation

### Flink Streaming Job

```java
package com.analytics.speed;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;

public class SpeedLayerProcessor {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Enable checkpointing
        env.enableCheckpointing(60000);  // Every minute

        // Kafka source
        DataStream<Event> events = env
            .addSource(new FlinkKafkaConsumer<>(
                "raw-events",
                new EventDeserializationSchema(),
                kafkaProps
            ))
            .assignTimestampsAndWatermarks(
                WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofMinutes(1))
                    .withTimestampAssigner((event, timestamp) -> event.getTimestamp())
            );

        // Hourly statistics (real-time)
        DataStream<HourlyStats> hourlyStats = events
            .keyBy(event -> new Tuple3<>(event.getEventType(), event.getCountry(),
                                         getHourBucket(event.getTimestamp())))
            .window(TumblingEventTimeWindows.of(Time.hours(1)))
            .aggregate(new HourlyStatsAggregator());

        // User metrics (real-time)
        DataStream<UserMetrics> userMetrics = events
            .keyBy(Event::getUserId)
            .window(TumblingEventTimeWindows.of(Time.hours(1)))
            .aggregate(new UserMetricsAggregator());

        // Write to serving layer
        hourlyStats.addSink(new ClickHouseSink<>("hourly_stats_realtime"));
        userMetrics.addSink(new ClickHouseSink<>("user_metrics_realtime"));

        env.execute("Lambda Speed Layer");
    }

    private static class HourlyStatsAggregator
            implements AggregateFunction<Event, StatsAccumulator, HourlyStats> {

        @Override
        public StatsAccumulator createAccumulator() {
            return new StatsAccumulator();
        }

        @Override
        public StatsAccumulator add(Event event, StatsAccumulator acc) {
            acc.count++;
            acc.totalRevenue += event.getRevenue() != null ? event.getRevenue() : 0;
            acc.userIds.add(event.getUserId());
            acc.sessionDurations.add(event.getSessionDuration());
            return acc;
        }

        @Override
        public HourlyStats getResult(StatsAccumulator acc) {
            return new HourlyStats(
                acc.hour,
                acc.eventType,
                acc.country,
                acc.count,
                acc.totalRevenue,
                acc.userIds.size(),  // Approximate unique users
                acc.sessionDurations.stream()
                    .mapToLong(Long::longValue)
                    .average()
                    .orElse(0)
            );
        }

        @Override
        public StatsAccumulator merge(StatsAccumulator a, StatsAccumulator b) {
            a.count += b.count;
            a.totalRevenue += b.totalRevenue;
            a.userIds.addAll(b.userIds);
            a.sessionDurations.addAll(b.sessionDurations);
            return a;
        }
    }
}
```

### ClickHouse Sink

```java
public class ClickHouseSink<T> extends RichSinkFunction<T> {
    private final String tableName;
    private transient ClickHouseConnection connection;
    private transient PreparedStatement statement;
    private transient List<T> buffer;
    private static final int BATCH_SIZE = 1000;

    public ClickHouseSink(String tableName) {
        this.tableName = tableName;
    }

    @Override
    public void open(Configuration parameters) throws Exception {
        connection = ClickHouseDataSource.createConnection(
            "jdbc:clickhouse://clickhouse:8123/analytics"
        );
        buffer = new ArrayList<>(BATCH_SIZE);
    }

    @Override
    public void invoke(T value, Context context) throws Exception {
        buffer.add(value);

        if (buffer.size() >= BATCH_SIZE) {
            flush();
        }
    }

    private void flush() throws Exception {
        if (buffer.isEmpty()) return;

        String sql = buildInsertSQL(tableName);
        statement = connection.prepareStatement(sql);

        for (T record : buffer) {
            setStatementParameters(statement, record);
            statement.addBatch();
        }

        statement.executeBatch();
        buffer.clear();
    }

    @Override
    public void close() throws Exception {
        flush();
        if (statement != null) statement.close();
        if (connection != null) connection.close();
    }
}
```

## Step 4: Serving Layer Setup

### ClickHouse Tables

```sql
-- Batch layer table
CREATE TABLE hourly_stats_batch (
    hour DateTime,
    event_type String,
    country String,
    event_count UInt64,
    total_revenue Float64,
    unique_users UInt64,
    avg_session_duration Float64,
    p95_session_duration Float64
)
ENGINE = ReplacingMergeTree(hour)
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, event_type, country);

-- Speed layer table
CREATE TABLE hourly_stats_realtime (
    hour DateTime,
    event_type String,
    country String,
    event_count UInt64,
    total_revenue Float64,
    unique_users UInt64,
    avg_session_duration Float64
)
ENGINE = ReplacingMergeTree(hour)
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, event_type, country)
SETTINGS index_granularity = 8192;

-- Unified view (merges batch and speed layers)
CREATE VIEW hourly_stats AS
SELECT
    hour,
    event_type,
    country,
    sum(event_count) AS event_count,
    sum(total_revenue) AS total_revenue,
    sum(unique_users) AS unique_users,
    avg(avg_session_duration) AS avg_session_duration
FROM (
    SELECT * FROM hourly_stats_batch
    WHERE hour < toStartOfHour(now() - INTERVAL 2 HOUR)
    UNION ALL
    SELECT
        hour,
        event_type,
        country,
        event_count,
        total_revenue,
        unique_users,
        avg_session_duration
    FROM hourly_stats_realtime
    WHERE hour >= toStartOfHour(now() - INTERVAL 2 HOUR)
)
GROUP BY hour, event_type, country
ORDER BY hour DESC;
```

## Step 5: Query API

### REST API Implementation

```python
from flask import Flask, jsonify, request
from clickhouse_driver import Client

app = Flask(__name__)
clickhouse = Client(host='clickhouse', port=9000)

@app.route('/api/stats/hourly', methods=['GET'])
def get_hourly_stats():
    start_time = request.args.get('start', required=True)
    end_time = request.args.get('end', required=True)
    event_type = request.args.get('event_type')
    country = request.args.get('country')

    query = """
        SELECT
            hour,
            event_type,
            country,
            event_count,
            total_revenue,
            unique_users,
            avg_session_duration
        FROM hourly_stats
        WHERE hour >= %(start)s
          AND hour < %(end)s
    """

    params = {'start': start_time, 'end': end_time}

    if event_type:
        query += " AND event_type = %(event_type)s"
        params['event_type'] = event_type

    if country:
        query += " AND country = %(country)s"
        params['country'] = country

    query += " ORDER BY hour DESC"

    results = clickhouse.execute(query, params)

    return jsonify([{
        'hour': row[0],
        'event_type': row[1],
        'country': row[2],
        'event_count': row[3],
        'total_revenue': row[4],
        'unique_users': row[5],
        'avg_session_duration': row[6]
    } for row in results])

@app.route('/api/users/<user_id>/metrics', methods=['GET'])
def get_user_metrics(user_id):
    query = """
        SELECT
            date,
            daily_events,
            sessions,
            daily_revenue
        FROM (
            SELECT * FROM user_metrics_batch WHERE user_id = %(user_id)s
            UNION ALL
            SELECT * FROM user_metrics_realtime WHERE user_id = %(user_id)s
        )
        ORDER BY date DESC
        LIMIT 30
    """

    results = clickhouse.execute(query, {'user_id': int(user_id)})

    return jsonify([{
        'date': row[0],
        'events': row[1],
        'sessions': row[2],
        'revenue': row[3]
    } for row in results])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Step 6: Data Archival

### S3 Lifecycle Policy

```json
{
  "Rules": [
    {
      "Id": "ArchiveOldEvents",
      "Status": "Enabled",
      "Prefix": "events/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

## Step 7: Monitoring

### Metrics to Track

```yaml
# Prometheus metrics
- name: batch_processing_duration_seconds
  type: histogram
  help: Batch job processing duration

- name: speed_layer_lag_seconds
  type: gauge
  help: Speed layer processing lag

- name: serving_layer_query_duration_seconds
  type: histogram
  help: Query response time

- name: data_freshness_seconds
  type: gauge
  help: Age of latest data in serving layer
```

### Alerting Rules

```yaml
groups:
  - name: lambda_architecture
    rules:
      - alert: BatchJobFailed
        expr: batch_job_success == 0
        for: 5m
        annotations:
          summary: "Batch processing job failed"

      - alert: HighSpeedLayerLag
        expr: speed_layer_lag_seconds > 300
        for: 5m
        annotations:
          summary: "Speed layer is lagging behind"

      - alert: StaleData
        expr: data_freshness_seconds > 600
        for: 5m
        annotations:
          summary: "Data in serving layer is stale"
```

## Best Practices

1. **Idempotent Processing**: Ensure reprocessing produces same results
2. **Separate Concerns**: Keep batch and speed layers independent
3. **Monitor Overlap**: Ensure smooth handoff between layers
4. **Version Data**: Track schema and processing versions
5. **Test Reprocessing**: Regularly test batch reprocessing
6. **Gradual Cutover**: Batch should overwrite speed layer data
7. **Capacity Planning**: Size clusters for peak load
8. **Cost Optimization**: Use spot instances for batch processing

## Troubleshooting

### Common Issues

1. **Duplicate Data**: Check batch/speed layer overlap period
2. **Missing Data**: Verify Kafka retention and batch schedule
3. **Query Inconsistency**: Ensure view merges layers correctly
4. **High Latency**: Check speed layer processing lag

## Resources

- Lambda Architecture book (Nathan Marz)
- Apache Spark documentation
- Apache Flink documentation
- ClickHouse best practices
