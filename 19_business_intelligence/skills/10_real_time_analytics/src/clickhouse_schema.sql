-- ClickHouse Tables for Real-Time Analytics

-- Events table
CREATE TABLE events (
    event_id String,
    user_id UInt64,
    event_time DateTime,
    event_type LowCardinality(String),
    country LowCardinality(String),
    device_type LowCardinality(String),
    revenue Nullable(Float64),
    session_duration UInt32,
    properties String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id)
SETTINGS index_granularity = 8192;

-- Hourly statistics
CREATE MATERIALIZED VIEW hourly_stats
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, event_type, country)
AS SELECT
    toStartOfHour(event_time) AS hour,
    event_type,
    country,
    count() AS event_count,
    sum(revenue) AS total_revenue,
    uniq(user_id) AS unique_users,
    avg(session_duration) AS avg_duration
FROM events
GROUP BY hour, event_type, country;

-- User daily metrics
CREATE TABLE user_daily_metrics (
    date Date,
    user_id UInt64,
    event_count UInt32,
    session_count UInt16,
    total_revenue Float64,
    first_seen DateTime,
    last_seen DateTime
)
ENGINE = ReplacingMergeTree(last_seen)
PARTITION BY toYYYYMM(date)
ORDER BY (date, user_id);

-- Kafka engine for real-time ingestion
CREATE TABLE events_queue (
    event_id String,
    user_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'events',
    kafka_group_name = 'clickhouse_consumer',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 4;

-- Materialized view to consume from Kafka
CREATE MATERIALIZED VIEW events_consumer TO events AS
SELECT * FROM events_queue;
