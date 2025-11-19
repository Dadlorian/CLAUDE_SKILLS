# Real-Time Analytics Architecture Pattern

## Overview

Real-time analytics enables organizations to process, analyze, and act on data with minimal latency—from milliseconds to seconds. This pattern covers architectural approaches, technologies, and implementation strategies for building systems that deliver insights at the speed of business.

## Architecture Patterns

### 1. Lambda Architecture

Lambda architecture combines batch and stream processing to provide comprehensive and accurate analytics.

```
┌─────────────────┐
│   Data Sources  │
│  (Events, Logs) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│Batch │  │Stream │
│Layer │  │Layer  │
└───┬──┘  └──┬────┘
    │        │
    └───┬────┘
        │
   ┌────▼────┐
   │ Serving │
   │  Layer  │
   └─────────┘
```

#### Components

**Batch Layer**: Historical data processing
- Complete, immutable data store
- Batch views for complex analytics
- High latency, high accuracy

**Speed Layer**: Real-time processing
- Recent data processing
- Real-time views for immediate insights
- Low latency, eventual consistency

**Serving Layer**: Query interface
- Merges batch and speed views
- Serves queries to end users
- Handles both historical and real-time data

#### Implementation with Kafka + Spark + Druid

```python
# lambda_architecture.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

class LambdaArchitecture:
    """Lambda architecture implementation"""

    def __init__(self, config):
        self.config = config
        self.spark = self._init_spark()

    def _init_spark(self):
        """Initialize Spark session"""
        return SparkSession.builder \
            .appName("Lambda Architecture") \
            .config("spark.sql.streaming.checkpointLocation", "/checkpoints") \
            .config("spark.sql.shuffle.partitions", "200") \
            .getOrCreate()

    def batch_layer(self, start_date, end_date):
        """
        Batch layer: Process historical data
        Runs periodically (daily, hourly) for complete accuracy
        """

        # Read from data lake (S3, HDFS, etc.)
        events = self.spark.read.parquet(
            f"s3a://data-lake/events/date={start_date}/*"
        )

        # Complex aggregations with full history
        user_metrics = events \
            .groupBy("user_id", window("timestamp", "1 hour")) \
            .agg(
                count("*").alias("event_count"),
                countDistinct("session_id").alias("session_count"),
                sum("revenue").alias("total_revenue"),
                avg("page_load_time").alias("avg_page_load_time"),
                collect_list("event_type").alias("event_sequence")
            )

        # Calculate complex derived metrics
        user_engagement = user_metrics \
            .withColumn(
                "engagement_score",
                col("event_count") * 0.3 +
                col("session_count") * 0.5 +
                when(col("total_revenue") > 0, 10).otherwise(0)
            )

        # Write to serving layer (Druid)
        user_engagement.write \
            .format("druid") \
            .option("dataSource", "user_metrics_batch") \
            .option("timestampColumn", "window.start") \
            .option("timestampFormat", "iso") \
            .mode("append") \
            .save()

        return user_engagement

    def speed_layer(self):
        """
        Speed layer: Process real-time streams
        Low latency, approximate results
        """

        # Read from Kafka
        stream = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "events") \
            .option("startingOffsets", "latest") \
            .load()

        # Parse JSON events
        schema = StructType([
            StructField("user_id", StringType(), True),
            StructField("event_type", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("session_id", StringType(), True),
            StructField("revenue", DoubleType(), True),
            StructField("properties", MapType(StringType(), StringType()), True)
        ])

        events = stream.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")

        # Real-time aggregations (approximations acceptable)
        real_time_metrics = events \
            .withWatermark("timestamp", "10 minutes") \
            .groupBy(
                "user_id",
                window("timestamp", "5 minutes", "1 minute")
            ) \
            .agg(
                approx_count_distinct("session_id").alias("session_count"),
                count("*").alias("event_count"),
                sum("revenue").alias("revenue"),
                collect_set("event_type").alias("event_types")
            )

        # Write to serving layer
        query = real_time_metrics.writeStream \
            .format("druid") \
            .outputMode("append") \
            .option("dataSource", "user_metrics_realtime") \
            .option("checkpointLocation", "/checkpoints/speed_layer") \
            .start()

        return query

    def serving_layer_query(self, user_id, time_range):
        """
        Serving layer: Merge batch and real-time views
        """

        # Query batch view (complete historical data)
        batch_query = f"""
        SELECT
            user_id,
            SUM(event_count) as total_events,
            SUM(session_count) as total_sessions,
            SUM(total_revenue) as total_revenue
        FROM user_metrics_batch
        WHERE user_id = '{user_id}'
        AND __time < TIMESTAMP '{time_range['real_time_start']}'
        GROUP BY user_id
        """

        # Query real-time view (recent data)
        realtime_query = f"""
        SELECT
            user_id,
            SUM(event_count) as total_events,
            SUM(session_count) as total_sessions,
            SUM(revenue) as total_revenue
        FROM user_metrics_realtime
        WHERE user_id = '{user_id}'
        AND __time >= TIMESTAMP '{time_range['real_time_start']}'
        GROUP BY user_id
        """

        # Execute queries against Druid
        batch_result = self.execute_druid_query(batch_query)
        realtime_result = self.execute_druid_query(realtime_query)

        # Merge results
        return {
            "user_id": user_id,
            "total_events": batch_result["total_events"] + realtime_result["total_events"],
            "total_sessions": batch_result["total_sessions"] + realtime_result["total_sessions"],
            "total_revenue": batch_result["total_revenue"] + realtime_result["total_revenue"],
            "last_updated": realtime_result["max_timestamp"]
        }
```

### 2. Kappa Architecture

Kappa architecture simplifies Lambda by using only stream processing.

```
┌─────────────────┐
│   Data Sources  │
└────────┬────────┘
         │
    ┌────▼────────┐
    │   Stream    │
    │ Processing  │
    │   Layer     │
    └────┬────────┘
         │
    ┌────▼────────┐
    │   Serving   │
    │    Layer    │
    └─────────────┘
```

#### Implementation with Kafka Streams + ksqlDB

```sql
-- ksqlDB Stream Processing

-- Create source stream from Kafka topic
CREATE STREAM raw_events (
    event_id VARCHAR KEY,
    user_id VARCHAR,
    event_type VARCHAR,
    timestamp BIGINT,
    session_id VARCHAR,
    properties MAP<VARCHAR, VARCHAR>
) WITH (
    KAFKA_TOPIC = 'events',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'timestamp'
);

-- Create enriched stream with user context
CREATE STREAM enriched_events AS
SELECT
    e.event_id,
    e.user_id,
    e.event_type,
    e.timestamp,
    e.session_id,
    u.user_name,
    u.user_segment,
    u.signup_date,
    e.properties
FROM raw_events e
LEFT JOIN users_table u ON e.user_id = u.user_id
EMIT CHANGES;

-- Real-time aggregations - 5 minute windows
CREATE TABLE user_activity_5m AS
SELECT
    user_id,
    WINDOWSTART as window_start,
    WINDOWEND as window_end,
    COUNT(*) as event_count,
    COUNT_DISTINCT(session_id) as session_count,
    COLLECT_LIST(event_type) as event_types,
    LATEST_BY_OFFSET(user_segment) as user_segment
FROM enriched_events
WINDOW TUMBLING (SIZE 5 MINUTES)
GROUP BY user_id
EMIT CHANGES;

-- Real-time aggregations - 1 hour windows with hopping
CREATE TABLE user_activity_1h AS
SELECT
    user_id,
    WINDOWSTART as window_start,
    WINDOWEND as window_end,
    COUNT(*) as event_count,
    COUNT_DISTINCT(session_id) as session_count,
    SUM(CAST(properties['revenue'] AS DOUBLE)) as total_revenue,
    AVG(CAST(properties['duration'] AS DOUBLE)) as avg_duration
FROM enriched_events
WINDOW HOPPING (SIZE 1 HOUR, ADVANCE BY 5 MINUTES)
GROUP BY user_id
EMIT CHANGES;

-- Anomaly detection - sudden spikes
CREATE TABLE anomaly_detection AS
SELECT
    user_id,
    window_start,
    event_count,
    LAG(event_count, 1) OVER (PARTITION BY user_id) as prev_event_count,
    CASE
        WHEN event_count > LAG(event_count, 1) OVER (PARTITION BY user_id) * 3
        THEN true
        ELSE false
    END as is_anomaly
FROM user_activity_5m
WHERE event_count > 100
EMIT CHANGES;

-- Funnel analysis
CREATE TABLE conversion_funnel AS
SELECT
    session_id,
    user_id,
    COLLECT_LIST(event_type) as event_sequence,
    CASE
        WHEN ARRAY_CONTAINS(COLLECT_LIST(event_type), 'page_view')
        AND ARRAY_CONTAINS(COLLECT_LIST(event_type), 'add_to_cart')
        AND ARRAY_CONTAINS(COLLECT_LIST(event_type), 'purchase')
        THEN 'converted'
        WHEN ARRAY_CONTAINS(COLLECT_LIST(event_type), 'add_to_cart')
        THEN 'cart_abandoned'
        ELSE 'browsing'
    END as funnel_stage
FROM enriched_events
WINDOW SESSION (60 MINUTES)
GROUP BY session_id, user_id
EMIT CHANGES;

-- Create materialized view for queries
CREATE TABLE user_metrics_current AS
SELECT
    user_id,
    LATEST_BY_OFFSET(user_segment) as user_segment,
    SUM(event_count) as total_events,
    SUM(session_count) as total_sessions,
    SUM(total_revenue) as total_revenue,
    MAX(window_end) as last_active
FROM user_activity_1h
GROUP BY user_id
EMIT CHANGES;
```

#### Kafka Streams Application

```java
// KafkaStreamsProcessor.java
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.common.serialization.Serdes;
import java.time.Duration;

public class RealTimeAnalytics {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "realtime-analytics");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

        StreamsBuilder builder = new StreamsBuilder();

        // Source stream
        KStream<String, Event> events = builder.stream(
            "events",
            Consumed.with(Serdes.String(), EventSerdes.Event())
        );

        // Windowed aggregations
        KTable<Windowed<String>, UserMetrics> userMetrics = events
            .groupBy(
                (key, event) -> event.getUserId(),
                Grouped.with(Serdes.String(), EventSerdes.Event())
            )
            .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)))
            .aggregate(
                UserMetrics::new,
                (key, event, metrics) -> metrics.update(event),
                Materialized.with(Serdes.String(), UserMetricsSerdes.UserMetrics())
            );

        // Join streams for enrichment
        KTable<String, User> users = builder.table(
            "users",
            Consumed.with(Serdes.String(), UserSerdes.User())
        );

        KStream<String, EnrichedEvent> enrichedEvents = events
            .leftJoin(
                users,
                (event, user) -> new EnrichedEvent(event, user),
                Joined.with(Serdes.String(), EventSerdes.Event(), UserSerdes.User())
            );

        // Pattern detection - sequential events
        KStream<String, Pattern> patterns = enrichedEvents
            .groupByKey()
            .windowedBy(SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(30)))
            .aggregate(
                PatternDetector::new,
                (key, event, detector) -> detector.addEvent(event),
                Merged.with(Serdes.String(), PatternDetectorSerdes.PatternDetector())
            )
            .toStream()
            .filter((key, detector) -> detector.hasPattern())
            .mapValues(detector -> detector.getPattern());

        // Output to Kafka topics
        userMetrics
            .toStream()
            .map((key, metrics) -> KeyValue.pair(key.key(), metrics))
            .to("user-metrics", Produced.with(Serdes.String(), UserMetricsSerdes.UserMetrics()));

        patterns.to("patterns-detected", Produced.with(Serdes.String(), PatternSerdes.Pattern()));

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}

// UserMetrics aggregation class
class UserMetrics {
    private long eventCount = 0;
    private long sessionCount = 0;
    private double totalRevenue = 0.0;
    private Set<String> sessions = new HashSet<>();

    public UserMetrics update(Event event) {
        this.eventCount++;
        this.sessions.add(event.getSessionId());
        this.sessionCount = this.sessions.size();
        this.totalRevenue += event.getRevenue();
        return this;
    }

    // Getters and setters
    public long getEventCount() { return eventCount; }
    public long getSessionCount() { return sessionCount; }
    public double getTotalRevenue() { return totalRevenue; }
}
```

### 3. Streaming Database: Apache Druid

Druid is purpose-built for real-time analytics on event streams.

#### Data Ingestion Spec

```json
{
  "type": "kafka",
  "spec": {
    "dataSchema": {
      "dataSource": "events",
      "timestampSpec": {
        "column": "timestamp",
        "format": "iso"
      },
      "dimensionsSpec": {
        "dimensions": [
          "event_type",
          "user_id",
          "session_id",
          {
            "type": "string",
            "name": "country",
            "createBitmapIndex": true
          },
          {
            "type": "string",
            "name": "device_type",
            "createBitmapIndex": true
          },
          {
            "type": "string",
            "name": "user_segment",
            "createBitmapIndex": true
          }
        ],
        "dimensionExclusions": [
          "timestamp"
        ]
      },
      "metricsSpec": [
        {
          "type": "count",
          "name": "count"
        },
        {
          "type": "longSum",
          "name": "revenue",
          "fieldName": "revenue"
        },
        {
          "type": "doubleSum",
          "name": "duration",
          "fieldName": "duration"
        },
        {
          "type": "hyperUnique",
          "name": "unique_users",
          "fieldName": "user_id"
        },
        {
          "type": "hyperUnique",
          "name": "unique_sessions",
          "fieldName": "session_id"
        },
        {
          "type": "thetaSketch",
          "name": "user_sketch",
          "fieldName": "user_id"
        }
      ],
      "granularitySpec": {
        "type": "uniform",
        "segmentGranularity": "HOUR",
        "queryGranularity": "MINUTE",
        "rollup": true
      }
    },
    "ioConfig": {
      "topic": "events",
      "consumerProperties": {
        "bootstrap.servers": "kafka:9092"
      },
      "taskCount": 4,
      "replicas": 2,
      "taskDuration": "PT1H",
      "useEarliestOffset": false
    },
    "tuningConfig": {
      "type": "kafka",
      "maxRowsPerSegment": 5000000,
      "maxRowsInMemory": 1000000,
      "intermediatePersistPeriod": "PT10M",
      "maxPendingPersists": 0,
      "indexSpec": {
        "bitmap": {
          "type": "roaring"
        },
        "dimensionCompression": "lz4",
        "metricCompression": "lz4",
        "longEncoding": "longs"
      }
    }
  }
}
```

#### Druid Query Examples

```python
# druid_queries.py
import requests
import json
from datetime import datetime, timedelta

class DruidClient:
    """Client for querying Apache Druid"""

    def __init__(self, broker_url):
        self.broker_url = broker_url

    def execute_query(self, query):
        """Execute Druid query"""
        response = requests.post(
            f"{self.broker_url}/druid/v2",
            headers={"Content-Type": "application/json"},
            data=json.dumps(query)
        )
        return response.json()

    def timeseries_query(self, datasource, start_time, end_time, granularity="minute"):
        """Time series aggregation query"""
        query = {
            "queryType": "timeseries",
            "dataSource": datasource,
            "granularity": granularity,
            "intervals": [f"{start_time}/{end_time}"],
            "aggregations": [
                {"type": "count", "name": "total_events"},
                {"type": "longSum", "name": "total_revenue", "fieldName": "revenue"},
                {"type": "hyperUnique", "name": "unique_users", "fieldName": "user_id"}
            ],
            "postAggregations": [
                {
                    "type": "arithmetic",
                    "name": "revenue_per_user",
                    "fn": "/",
                    "fields": [
                        {"type": "fieldAccess", "fieldName": "total_revenue"},
                        {"type": "fieldAccess", "fieldName": "unique_users"}
                    ]
                }
            ]
        }
        return self.execute_query(query)

    def topn_query(self, datasource, dimension, metric, threshold=10):
        """Top N query"""
        query = {
            "queryType": "topN",
            "dataSource": datasource,
            "dimension": dimension,
            "threshold": threshold,
            "metric": metric,
            "granularity": "all",
            "intervals": [f"{datetime.now() - timedelta(hours=1)}/{datetime.now()}"],
            "aggregations": [
                {"type": "count", "name": "event_count"},
                {"type": "longSum", "name": "total_revenue", "fieldName": "revenue"}
            ]
        }
        return self.execute_query(query)

    def group_by_query(self, datasource, dimensions, filters=None):
        """Group by query with optional filters"""
        query = {
            "queryType": "groupBy",
            "dataSource": datasource,
            "granularity": "minute",
            "dimensions": dimensions,
            "intervals": [f"{datetime.now() - timedelta(hours=1)}/{datetime.now()}"],
            "aggregations": [
                {"type": "count", "name": "count"},
                {"type": "longSum", "name": "revenue", "fieldName": "revenue"},
                {"type": "hyperUnique", "name": "unique_users", "fieldName": "user_id"}
            ],
            "having": {
                "type": "greaterThan",
                "aggregation": "count",
                "value": 100
            }
        }

        if filters:
            query["filter"] = filters

        return self.execute_query(query)

    def scan_query(self, datasource, columns, limit=1000):
        """Scan query for raw data"""
        query = {
            "queryType": "scan",
            "dataSource": datasource,
            "intervals": [f"{datetime.now() - timedelta(minutes=5)}/{datetime.now()}"],
            "columns": columns,
            "limit": limit,
            "resultFormat": "list"
        }
        return self.execute_query(query)

    def realtime_dashboard_query(self):
        """Example: Real-time dashboard metrics"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)

        # Multiple queries in parallel
        queries = {
            "overview": self.timeseries_query(
                "events",
                last_hour.isoformat(),
                now.isoformat(),
                granularity="minute"
            ),
            "top_users": self.topn_query(
                "events",
                "user_id",
                "total_revenue",
                threshold=20
            ),
            "by_country": self.group_by_query(
                "events",
                ["country", "device_type"]
            )
        }

        return queries

# Usage
client = DruidClient("http://druid-broker:8082")

# Real-time metrics
metrics = client.realtime_dashboard_query()
print(f"Current active users: {metrics['overview'][-1]['unique_users']}")
print(f"Revenue last minute: ${metrics['overview'][-1]['total_revenue']}")
```

### 4. ClickHouse for Real-Time Analytics

ClickHouse is a columnar database optimized for analytical queries.

#### Table Schema

```sql
-- ClickHouse table for event analytics
CREATE TABLE events
(
    event_id String,
    event_type LowCardinality(String),
    timestamp DateTime,
    user_id String,
    session_id String,
    country LowCardinality(String),
    device_type LowCardinality(String),
    revenue Decimal(10, 2),
    duration UInt32,
    properties Map(String, String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp)
SETTINGS index_granularity = 8192;

-- Materialized view for pre-aggregation
CREATE MATERIALIZED VIEW user_metrics_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMMDD(window_start)
ORDER BY (user_id, window_start)
AS SELECT
    user_id,
    toStartOfFiveMinutes(timestamp) as window_start,
    count() as event_count,
    uniq(session_id) as session_count,
    sum(revenue) as total_revenue,
    avg(duration) as avg_duration
FROM events
GROUP BY user_id, window_start;

-- Kafka table engine for real-time ingestion
CREATE TABLE events_queue
(
    event_id String,
    event_type String,
    timestamp DateTime,
    user_id String,
    session_id String,
    country String,
    device_type String,
    revenue Decimal(10, 2),
    duration UInt32,
    properties String
)
ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'events',
    kafka_group_name = 'clickhouse_consumer',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 4;

-- Materialized view to move data from Kafka to main table
CREATE MATERIALIZED VIEW events_consumer TO events AS
SELECT
    event_id,
    event_type,
    timestamp,
    user_id,
    session_id,
    country,
    device_type,
    revenue,
    duration,
    JSONExtract(properties, 'Map(String, String)') as properties
FROM events_queue;

-- Distributed table for clustering
CREATE TABLE events_distributed AS events
ENGINE = Distributed(cluster_name, default, events, rand());
```

#### Advanced Queries

```sql
-- Real-time user activity (last 5 minutes)
SELECT
    user_id,
    count() as events,
    uniq(session_id) as sessions,
    sum(revenue) as revenue,
    groupArray(event_type) as event_sequence
FROM events
WHERE timestamp >= now() - INTERVAL 5 MINUTE
GROUP BY user_id
HAVING events > 10
ORDER BY revenue DESC
LIMIT 100;

-- Funnel analysis with time constraints
SELECT
    session_id,
    user_id,
    sequenceMatch('(?1)(?2)(?3)')(
        timestamp,
        event_type = 'page_view',
        event_type = 'add_to_cart',
        event_type = 'purchase'
    ) as completed_funnel,
    sequenceMatch('(?1)(?2)')(
        timestamp,
        event_type = 'page_view',
        event_type = 'add_to_cart'
    ) as added_to_cart
FROM events
WHERE timestamp >= today()
GROUP BY session_id, user_id;

-- Retention cohort analysis
WITH cohorts AS (
    SELECT
        user_id,
        toStartOfMonth(min(timestamp)) as cohort_month
    FROM events
    GROUP BY user_id
)
SELECT
    c.cohort_month,
    dateDiff('month', c.cohort_month, toStartOfMonth(e.timestamp)) as month_number,
    uniq(e.user_id) as active_users
FROM events e
INNER JOIN cohorts c ON e.user_id = c.user_id
GROUP BY c.cohort_month, month_number
ORDER BY c.cohort_month, month_number;

-- Real-time anomaly detection
SELECT
    toStartOfMinute(timestamp) as minute,
    count() as current_events,
    avg(count()) OVER (
        ORDER BY toStartOfMinute(timestamp)
        ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING
    ) as avg_events_previous_10min,
    stddevPop(count()) OVER (
        ORDER BY toStartOfMinute(timestamp)
        ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING
    ) as stddev_events,
    CASE
        WHEN count() > avg_events_previous_10min + 3 * stddev_events
        THEN 'ANOMALY'
        ELSE 'NORMAL'
    END as status
FROM events
WHERE timestamp >= now() - INTERVAL 1 HOUR
GROUP BY minute
ORDER BY minute DESC;

-- Windowed aggregation with lag
SELECT
    toStartOfFiveMinutes(timestamp) as window,
    count() as events,
    lagInFrame(count()) OVER (ORDER BY toStartOfFiveMinutes(timestamp)) as prev_events,
    (count() - prev_events) / prev_events * 100 as growth_rate
FROM events
WHERE timestamp >= now() - INTERVAL 1 HOUR
GROUP BY window
ORDER BY window;
```

## Real-Time Dashboards

### Grafana Integration

```yaml
# grafana_dashboard.yaml
apiVersion: 1
providers:
  - name: 'Real-Time Analytics'
    folder: 'Analytics'
    type: file
    options:
      path: /etc/grafana/provisioning/dashboards

dashboard:
  title: Real-Time Analytics Dashboard
  refresh: "5s"
  time:
    from: now-1h
    to: now

  panels:
    - title: "Events per Second"
      type: graph
      datasource: ClickHouse
      targets:
        - query: |
            SELECT
              toStartOfMinute(timestamp) as time,
              count() / 60 as events_per_second
            FROM events
            WHERE $__timeFilter(timestamp)
            GROUP BY time
            ORDER BY time

    - title: "Active Users (5min window)"
      type: stat
      datasource: ClickHouse
      targets:
        - query: |
            SELECT uniq(user_id) as active_users
            FROM events
            WHERE timestamp >= now() - INTERVAL 5 MINUTE

    - title: "Revenue Stream"
      type: graph
      datasource: ClickHouse
      targets:
        - query: |
            SELECT
              toStartOfMinute(timestamp) as time,
              sum(revenue) as total_revenue
            FROM events
            WHERE $__timeFilter(timestamp)
            AND event_type = 'purchase'
            GROUP BY time
            ORDER BY time

    - title: "Top Events"
      type: table
      datasource: ClickHouse
      targets:
        - query: |
            SELECT
              event_type,
              count() as count,
              uniq(user_id) as unique_users
            FROM events
            WHERE timestamp >= now() - INTERVAL 5 MINUTE
            GROUP BY event_type
            ORDER BY count DESC
            LIMIT 10

    - title: "Geographic Distribution"
      type: map
      datasource: ClickHouse
      targets:
        - query: |
            SELECT
              country,
              count() as events,
              uniq(user_id) as users
            FROM events
            WHERE timestamp >= now() - INTERVAL 5 MINUTE
            GROUP BY country
```

### Superset Real-Time Charts

```python
# superset_realtime_config.py
from superset import db
from superset.models.core import Database
from superset.models.slice import Slice

# Configure real-time database connection
realtime_db = Database(
    database_name="RealTime ClickHouse",
    sqlalchemy_uri="clickhouse://user:pass@clickhouse:8123/default",
    cache_timeout=5,  # 5 second cache
    extra=json.dumps({
        "allows_virtual_table_explore": True,
        "disable_data_preview": False
    })
)

# Real-time chart configuration
realtime_chart = Slice(
    slice_name="Real-Time Events",
    viz_type="line",
    datasource_type="table",
    datasource_name="events",
    params=json.dumps({
        "metrics": ["count"],
        "groupby": [],
        "time_range": "Last 5 minutes",
        "time_grain_sqla": "minute",
        "refresh_frequency": 5,  # Refresh every 5 seconds
        "rolling_type": "None",
        "comparison_type": "values"
    })
)
```

## Performance Optimization

### Indexing Strategies

```sql
-- ClickHouse skip indexes for faster queries
ALTER TABLE events
ADD INDEX user_idx (user_id) TYPE bloom_filter() GRANULARITY 4;

ALTER TABLE events
ADD INDEX event_type_idx (event_type) TYPE set(100) GRANULARITY 4;

-- Projection for common query patterns
ALTER TABLE events
ADD PROJECTION events_by_country
(
    SELECT
        country,
        device_type,
        count(),
        sum(revenue),
        uniq(user_id)
    GROUP BY country, device_type
);

-- Materialize the projection
ALTER TABLE events MATERIALIZE PROJECTION events_by_country;
```

### Caching Strategy

```python
# redis_cache_layer.py
import redis
import json
from datetime import timedelta

class RealtimeCache:
    """Cache layer for real-time analytics"""

    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)

    def get_cached_metrics(self, metric_key, ttl_seconds=30):
        """Get cached metrics with TTL"""
        cached = self.redis.get(metric_key)
        if cached:
            return json.loads(cached)
        return None

    def cache_metrics(self, metric_key, data, ttl_seconds=30):
        """Cache metrics with expiration"""
        self.redis.setex(
            metric_key,
            timedelta(seconds=ttl_seconds),
            json.dumps(data)
        )

    def get_or_compute(self, metric_key, compute_func, ttl_seconds=30):
        """Get from cache or compute and cache"""
        cached = self.get_cached_metrics(metric_key, ttl_seconds)

        if cached:
            return {"data": cached, "cached": True}

        # Compute and cache
        result = compute_func()
        self.cache_metrics(metric_key, result, ttl_seconds)

        return {"data": result, "cached": False}
```

## Monitoring and Alerting

```python
# alerting_system.py
from prometheus_client import Counter, Histogram, Gauge
import asyncio

# Metrics
events_processed = Counter('events_processed_total', 'Total events processed')
processing_latency = Histogram('event_processing_seconds', 'Event processing latency')
active_users = Gauge('active_users', 'Current active users')

class RealtimeMonitor:
    """Monitor real-time analytics system"""

    def __init__(self, clickhouse_client, alert_manager):
        self.clickhouse = clickhouse_client
        self.alert_manager = alert_manager

    async def check_lag(self):
        """Check processing lag"""
        query = """
        SELECT max(timestamp) as latest_event
        FROM events
        """
        result = self.clickhouse.execute(query)
        lag = datetime.now() - result[0]['latest_event']

        if lag.total_seconds() > 300:  # 5 minutes
            await self.alert_manager.send_alert(
                severity="critical",
                message=f"Processing lag: {lag.total_seconds()}s"
            )

    async def check_throughput(self):
        """Check events per second"""
        query = """
        SELECT count() / 60 as eps
        FROM events
        WHERE timestamp >= now() - INTERVAL 1 MINUTE
        """
        result = self.clickhouse.execute(query)
        eps = result[0]['eps']

        if eps < 100:  # Expected minimum
            await self.alert_manager.send_alert(
                severity="warning",
                message=f"Low throughput: {eps} events/sec"
            )
```

## Best Practices

1. **Idempotency**: Ensure duplicate events don't corrupt metrics
2. **Watermarks**: Handle late-arriving data gracefully
3. **Backpressure**: Implement flow control
4. **Partitioning**: Distribute load across nodes
5. **Monitoring**: Track lag, throughput, and errors
6. **Testing**: Validate with synthetic data streams

## Conclusion

Real-time analytics requires careful architecture choices balancing latency, accuracy, and cost. Lambda and Kappa architectures, combined with modern streaming technologies like Kafka, Druid, and ClickHouse, enable organizations to build scalable, reliable real-time analytics systems.
