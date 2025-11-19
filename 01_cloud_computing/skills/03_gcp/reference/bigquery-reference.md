# BigQuery Reference Guide

## Overview

BigQuery is a serverless, highly scalable, cost-effective multi-cloud data warehouse designed for business agility. It provides built-in machine learning capabilities and integrates with popular BI tools.

## Architecture

### Core Components
- **Datasets**: Top-level containers organizing tables
- **Tables**: Structured data storage (standard, partitioned, clustered)
- **Views**: Virtual tables based on SQL queries
- **Materialized Views**: Pre-computed query results
- **External Tables**: Query data in Cloud Storage, Drive, Bigtable
- **Routines**: User-defined functions and stored procedures

### Storage Architecture
- **Capacitor**: Columnar storage format
- **Separation**: Compute and storage are independent
- **Replication**: Automatic multi-zone replication
- **Encryption**: Automatic encryption at rest

### Compute Architecture
- **Slots**: Units of computational capacity (1 slot = ~2,000 MB memory, variable CPU)
- **On-Demand**: Pay per TB scanned
- **Reservations**: Flat-rate committed slots

## Table Types

### Standard Tables
Regular tables with rows stored in BigQuery.

```sql
CREATE TABLE mydataset.mytable (
    id INT64,
    name STRING,
    created_at TIMESTAMP
)
OPTIONS(
    description="User table",
    labels=[("env", "prod")]
);
```

### Partitioned Tables
Tables divided into segments for better performance and cost control.

**Time-Unit Partitioning**:
```sql
CREATE TABLE mydataset.events
PARTITION BY DATE(timestamp)
OPTIONS(
    partition_expiration_days=90
) AS
SELECT * FROM source_table;
```

**Integer Range Partitioning**:
```sql
CREATE TABLE mydataset.sales
PARTITION BY RANGE_BUCKET(customer_id, GENERATE_ARRAY(0, 100000, 1000))
AS SELECT * FROM source_table;
```

**Partitioning Types**:
- **Daily** (default): One partition per day
- **Hourly**: More granular, more partitions
- **Monthly/Yearly**: Coarser granularity
- **Integer Range**: Partition by numeric column

**Benefits**:
- Query only relevant partitions (reduced cost)
- Faster queries
- Automatic partition expiration
- DML operations on specific partitions

### Clustered Tables
Tables organized by column values for better performance.

```sql
CREATE TABLE mydataset.users
PARTITION BY DATE(created_at)
CLUSTER BY country, city
AS SELECT * FROM source_table;
```

**Clustering Columns**:
- Up to 4 columns
- Order matters (most to least selective)
- Best for columns with:
  - High cardinality
  - Frequently used in WHERE clauses
  - Used in GROUP BY

**Benefits**:
- Automatic sort
- Improved query performance
- Reduced cost (prune unnecessary data)
- No additional cost

### External Tables
Query data without loading into BigQuery.

**Cloud Storage**:
```sql
CREATE EXTERNAL TABLE mydataset.external_table
OPTIONS (
    format = 'CSV',
    uris = ['gs://bucket/path/*.csv'],
    skip_leading_rows = 1
);
```

**Supported Formats**:
- CSV, JSON, Avro, Parquet, ORC
- Datastore backups
- Firestore exports
- Google Sheets

**Bigtable**:
```sql
CREATE EXTERNAL TABLE mydataset.bigtable_table
OPTIONS (
    format = 'CLOUD_BIGTABLE',
    uris = ['https://googleapis.com/bigtable/projects/PROJECT/instances/INSTANCE/tables/TABLE']
);
```

### Materialized Views
Pre-computed views with automatic refresh.

```sql
CREATE MATERIALIZED VIEW mydataset.daily_sales
PARTITION BY DATE(order_date)
CLUSTER BY product_id
AS
SELECT
    DATE(order_timestamp) AS order_date,
    product_id,
    SUM(amount) AS total_sales,
    COUNT(*) AS order_count
FROM mydataset.orders
GROUP BY order_date, product_id;
```

**Characteristics**:
- Automatic refresh (eventually consistent)
- Query directly or auto-substitution in base queries
- Support partitioning and clustering
- Cost: Storage + refresh compute

**Best For**:
- Frequently run aggregations
- Expensive joins
- Dashboards and reports

## Data Types

### Numeric
```sql
INT64          -- Integer (-9223372036854775808 to 9223372036854775807)
NUMERIC        -- Decimal (38 digits precision, 9 decimal places)
BIGNUMERIC     -- Decimal (76 digits precision, 38 decimal places)
FLOAT64        -- Double precision floating point
```

### String & Bytes
```sql
STRING         -- Variable-length character string (up to 16 MB)
BYTES          -- Variable-length binary data (up to 16 MB)
```

### Temporal
```sql
DATE           -- Calendar date (YYYY-MM-DD)
DATETIME       -- Date and time (no timezone)
TIME           -- Time of day (no timezone)
TIMESTAMP      -- Absolute point in time (microsecond precision, UTC)
```

### Boolean
```sql
BOOL           -- TRUE, FALSE, NULL
```

### Geographic
```sql
GEOGRAPHY      -- Point, line, polygon (WGS84)
```

### Complex
```sql
ARRAY          -- Ordered list of zero or more elements
STRUCT         -- Container of ordered fields (records)
JSON           -- JSON data (preview)
```

**Array Example**:
```sql
SELECT [1, 2, 3] AS numbers;
SELECT ARRAY_AGG(name) AS names FROM table;
```

**Struct Example**:
```sql
SELECT STRUCT(1 AS id, "Alice" AS name) AS user;
SELECT user.name FROM (SELECT STRUCT(1 AS id, "Alice" AS name) AS user);
```

## Query Optimization

### Best Practices

**1. Avoid SELECT ***:
```sql
-- Bad
SELECT * FROM large_table;

-- Good
SELECT id, name, email FROM large_table;
```

**2. Use Partitioning**:
```sql
-- Scans specific partition only
SELECT * FROM partitioned_table
WHERE DATE(timestamp) = '2024-01-01';

-- Use _PARTITIONTIME for ingestion-time partitioned tables
SELECT * FROM partitioned_table
WHERE _PARTITIONTIME = '2024-01-01';
```

**3. Filter Early**:
```sql
-- Good - filter before join
WITH filtered_users AS (
    SELECT user_id, name
    FROM users
    WHERE created_at >= '2024-01-01'
)
SELECT * FROM filtered_users
JOIN orders ON filtered_users.user_id = orders.user_id;
```

**4. Use APPROX Functions**:
```sql
-- Exact (expensive)
SELECT COUNT(DISTINCT user_id) FROM large_table;

-- Approximate (faster, cheaper, 98%+ accuracy)
SELECT APPROX_COUNT_DISTINCT(user_id) FROM large_table;
```

**5. Denormalize Data**:
```sql
-- Instead of joins, use nested/repeated fields
CREATE TABLE mydataset.orders (
    order_id INT64,
    customer STRUCT<
        id INT64,
        name STRING,
        email STRING
    >,
    items ARRAY<STRUCT<
        product_id INT64,
        quantity INT64,
        price FLOAT64
    >>
);
```

**6. Use BI Engine**:
```sql
-- Create BI Engine reservation for caching
-- Accelerates queries from BI tools
```

**7. Optimize JOINs**:
```sql
-- Put largest table first
SELECT * FROM large_table
JOIN small_table ON large_table.id = small_table.id;

-- Use INNER JOIN when possible (faster than LEFT JOIN)
```

**8. Use INFORMATION_SCHEMA**:
```sql
-- Analyze table size before querying
SELECT
    table_name,
    size_bytes / POW(10, 9) AS size_gb,
    row_count
FROM mydataset.INFORMATION_SCHEMA.TABLES
WHERE table_name = 'large_table';
```

### Query Execution Plan
```sql
-- Add EXPLAIN to see execution plan
EXPLAIN SELECT * FROM large_table WHERE id = 123;
```

## Streaming Inserts

### Streaming API
Real-time data insertion (microsecond latency).

**Python Example**:
```python
from google.cloud import bigquery

client = bigquery.Client()
table_id = "project.dataset.table"

rows_to_insert = [
    {"id": 1, "name": "Alice", "timestamp": "2024-01-01T00:00:00"},
    {"id": 2, "name": "Bob", "timestamp": "2024-01-01T00:01:00"},
]

errors = client.insert_rows_json(table_id, rows_to_insert)
if errors:
    print(f"Errors: {errors}")
```

**Characteristics**:
- **Latency**: Sub-second
- **Cost**: $0.010 per 200 MB (1st 100 GB/day free)
- **Best-effort deduplication**: Based on insertId (1 minute window)
- **Quota**: 100,000 rows/sec per table (can be increased)

### Storage Write API
High-throughput streaming with exactly-once semantics.

**Types**:
- **Default Stream**: Immediately available
- **Committed Stream**: Transactional writes
- **Pending Stream**: Commit before availability

**Benefits**:
- Lower cost than streaming inserts
- Exactly-once delivery
- Higher throughput
- No quota on rows/sec

### Dataflow Streaming
For complex streaming ETL pipelines.

```python
import apache_beam as beam
from apache_beam.io.gcp.bigquery import WriteToBigQuery

with beam.Pipeline() as pipeline:
    (pipeline
     | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(subscription=SUBSCRIPTION)
     | 'Parse JSON' >> beam.Map(json.loads)
     | 'Write to BigQuery' >> WriteToBigQuery(
         table=TABLE_SPEC,
         write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
         create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED))
```

## Data Transfer

### Batch Loading
Load data from Cloud Storage, Drive, or local files.

**bq Command**:
```bash
# Load CSV from Cloud Storage
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    mydataset.mytable \
    gs://bucket/file.csv

# Load Parquet (faster, more efficient)
bq load \
    --source_format=PARQUET \
    --use_avro_logical_types \
    mydataset.mytable \
    gs://bucket/*.parquet

# Load JSON (newline-delimited)
bq load \
    --source_format=NEWLINE_DELIMITED_JSON \
    mydataset.mytable \
    gs://bucket/data.jsonl
```

**Python**:
```python
from google.cloud import bigquery

client = bigquery.Client()

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
)

uri = "gs://bucket/file.csv"
load_job = client.load_table_from_uri(
    uri, "project.dataset.table", job_config=job_config
)

load_job.result()  # Wait for job to complete
```

### BigQuery Data Transfer Service
Automated data loads from SaaS applications.

**Supported Sources**:
- Google Ads
- Google Ad Manager
- Google Play
- YouTube Channel/Content Owner
- Campaign Manager 360
- Amazon S3
- Teradata
- Amazon Redshift

**Schedule Transfer**:
```bash
bq mk --transfer_config \
    --project_id=PROJECT_ID \
    --data_source=google_cloud_storage \
    --target_dataset=mydataset \
    --display_name='Daily CSV Import' \
    --schedule='every day 00:00' \
    --params='{"data_path_template":"gs://bucket/daily/*.csv","destination_table_name_template":"daily_data","file_format":"CSV","skip_leading_rows":1}'
```

### Data Migration Patterns

**1. Full Load**:
```sql
TRUNCATE TABLE mydataset.target_table;

INSERT INTO mydataset.target_table
SELECT * FROM external_source;
```

**2. Incremental Load**:
```sql
-- Merge pattern (upsert)
MERGE mydataset.target_table AS target
USING external_source AS source
ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET
        target.name = source.name,
        target.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (id, name, created_at)
    VALUES (source.id, source.name, CURRENT_TIMESTAMP());
```

**3. Change Data Capture**:
```sql
-- Append changes with operation type
INSERT INTO mydataset.change_log
SELECT *, 'INSERT' AS operation, CURRENT_TIMESTAMP() AS log_time
FROM new_records;
```

## Access Control

### Dataset-Level IAM
```bash
# Grant BigQuery Data Viewer
bq add-iam-policy-binding \
    --member=user:user@example.com \
    --role=roles/bigquery.dataViewer \
    mydataset

# Grant BigQuery Data Editor
bq add-iam-policy-binding \
    --member=serviceAccount:sa@project.iam.gserviceaccount.com \
    --role=roles/bigquery.dataEditor \
    mydataset
```

### Table-Level Access
```sql
-- Authorized views pattern
CREATE VIEW mydataset.public_view AS
SELECT id, name  -- Exclude sensitive columns
FROM mydataset.private_table
WHERE is_public = TRUE;

-- Grant access to view only
GRANT `roles/bigquery.dataViewer`
ON TABLE mydataset.public_view
TO "user:user@example.com";
```

### Column-Level Security
```sql
-- Use policy tags from Data Catalog
CREATE TABLE mydataset.sensitive_data (
    id INT64,
    name STRING,
    ssn STRING OPTIONS(description="Social Security Number")
)
OPTIONS(
    description="Customer data with PII"
);
```

### Row-Level Security
```sql
-- Create row access policy
CREATE ROW ACCESS POLICY region_filter
ON mydataset.sales
GRANT TO ("user:analyst@example.com")
FILTER USING (region = 'US');

-- Users only see rows matching filter
```

## BigQuery ML

### Supported Models
- **Linear Regression**: Continuous predictions
- **Logistic Regression**: Binary/multiclass classification
- **K-Means**: Clustering
- **Matrix Factorization**: Recommendation systems
- **Time Series (ARIMA_PLUS)**: Forecasting
- **Boosted Trees (XGBoost)**: Classification/regression
- **Deep Neural Networks (DNN)**: Classification/regression
- **AutoML Tables**: Automated model selection
- **Imported Models**: TensorFlow, ONNX

### Model Lifecycle

**1. Create Model**:
```sql
CREATE OR REPLACE MODEL mydataset.classification_model
OPTIONS(
    model_type='LOGISTIC_REG',
    input_label_cols=['label'],
    max_iterations=10
) AS
SELECT
    feature1,
    feature2,
    feature3,
    label
FROM mydataset.training_data;
```

**2. Evaluate Model**:
```sql
SELECT
    *
FROM
    ML.EVALUATE(MODEL mydataset.classification_model,
        (SELECT * FROM mydataset.test_data));
```

**3. Predict**:
```sql
SELECT
    predicted_label,
    predicted_label_probs
FROM
    ML.PREDICT(MODEL mydataset.classification_model,
        (SELECT * FROM mydataset.new_data));
```

**4. Export Model**:
```bash
bq extract -m mydataset.classification_model gs://bucket/model
```

## Monitoring and Optimization

### Query Insights
```sql
-- View query history
SELECT
    job_id,
    user_email,
    total_bytes_processed,
    total_slot_ms,
    TIMESTAMP_DIFF(end_time, start_time, MILLISECOND) AS duration_ms
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY total_bytes_processed DESC
LIMIT 100;
```

### Slot Usage Monitoring
```sql
-- Monitor slot usage
SELECT
    TIMESTAMP_TRUNC(period_start, HOUR) AS hour,
    project_id,
    AVG(total_slot_ms) / (1000 * 60 * 60) AS avg_slots
FROM `region-us`.INFORMATION_SCHEMA.JOBS_TIMELINE_BY_PROJECT
WHERE period_start > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY hour, project_id
ORDER BY hour DESC;
```

### Cost Tracking
```sql
-- Query cost analysis
SELECT
    user_email,
    SUM(total_bytes_billed) / POW(10, 12) AS tb_billed,
    SUM(total_bytes_billed) / POW(10, 12) * 5 AS estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    AND statement_type = 'SELECT'
GROUP BY user_email
ORDER BY tb_billed DESC;
```

## Pricing

### On-Demand Pricing
- **Analysis**: $5 per TB scanned (first 1 TB/month free)
- **Storage**: $0.020 per GB/month (active), $0.010 per GB/month (long-term)
- **Streaming**: $0.010 per 200 MB

### Flat-Rate Pricing (Slots)
- **Baseline**: 100 slots minimum
- **Standard**: $2,000/month per 100 slots
- **Enterprise**: $3,000/month per 100 slots (includes BI Engine, 99.99% SLA)
- **Flex Slots**: 500 slots minimum, 60-second commitment

### Cost Optimization
1. Use partitioning and clustering
2. Avoid SELECT *
3. Use query caching (24-hour cache)
4. Preview data with table metadata
5. Set maximum bytes billed
6. Use flat-rate for predictable high-volume usage
7. Leverage long-term storage (90+ days)
8. Use approximate aggregation functions
9. Sample data for exploratory analysis
10. Monitor and optimize expensive queries

## Best Practices Summary

1. **Schema Design**: Use appropriate data types, consider denormalization
2. **Partitioning**: Partition large tables by date or integer range
3. **Clustering**: Cluster frequently filtered/grouped columns
4. **Query Optimization**: Filter early, avoid SELECT *, use LIMIT for testing
5. **Cost Management**: Monitor query costs, use flat-rate for high volume
6. **Security**: Implement appropriate IAM, use authorized views, row-level security
7. **Data Loading**: Use efficient formats (Parquet, Avro), batch when possible
8. **Monitoring**: Track slot usage, query performance, costs
9. **ML Integration**: Use BigQuery ML for in-database machine learning
10. **Documentation**: Comment schemas, use descriptive names, document datasets
