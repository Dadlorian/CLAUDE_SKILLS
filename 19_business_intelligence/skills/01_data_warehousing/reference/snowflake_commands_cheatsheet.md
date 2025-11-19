# Snowflake Commands Cheatsheet

Quick reference for essential Snowflake SQL commands and features.

## Database Objects

### Database Management
```sql
-- Create database
CREATE DATABASE my_database;
CREATE DATABASE IF NOT EXISTS my_database;

-- Use database
USE DATABASE my_database;

-- Show databases
SHOW DATABASES;
SHOW DATABASES LIKE 'PROD%';

-- Drop database
DROP DATABASE my_database;
DROP DATABASE IF EXISTS my_database CASCADE;

-- Clone database (zero-copy)
CREATE DATABASE dev_db CLONE prod_db;
```

### Schema Management
```sql
-- Create schema
CREATE SCHEMA my_schema;
CREATE TRANSIENT SCHEMA temp_schema;

-- Show schemas
SHOW SCHEMAS IN DATABASE my_database;

-- Drop schema
DROP SCHEMA my_schema CASCADE;
```

### Table Management
```sql
-- Create table
CREATE TABLE customers (
    customer_id NUMBER(38,0),
    name VARCHAR(100),
    email VARCHAR(200),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create transient table (no fail-safe)
CREATE TRANSIENT TABLE staging_data (...);

-- Create temporary table (session-scoped)
CREATE TEMPORARY TABLE temp_results (...);

-- Clone table (zero-copy)
CREATE TABLE customers_backup CLONE customers;

-- Create table from query
CREATE TABLE summary AS SELECT ...;

-- Show tables
SHOW TABLES IN SCHEMA my_schema;

-- Describe table
DESC TABLE customers;
SHOW COLUMNS IN customers;
```

## Virtual Warehouses

### Warehouse Management
```sql
-- Create warehouse
CREATE WAREHOUSE analytics_wh
    WAREHOUSE_SIZE = 'X-LARGE'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Alter warehouse size
ALTER WAREHOUSE analytics_wh SET WAREHOUSE_SIZE = 'MEDIUM';

-- Suspend/resume warehouse
ALTER WAREHOUSE analytics_wh SUSPEND;
ALTER WAREHOUSE analytics_wh RESUME;

-- Show warehouses
SHOW WAREHOUSES;

-- Drop warehouse
DROP WAREHOUSE analytics_wh;
```

### Warehouse Sizes
```
X-Small:  1 credit/hour  (1 server)
Small:    2 credits/hour (2 servers)
Medium:   4 credits/hour (4 servers)
Large:    8 credits/hour (8 servers)
X-Large: 16 credits/hour (16 servers)
2X-Large: 32 credits/hour (32 servers)
3X-Large: 64 credits/hour (64 servers)
4X-Large: 128 credits/hour (128 servers)
```

## Time Travel & Cloning

### Time Travel Queries
```sql
-- Query table as of specific time
SELECT * FROM customers AT(TIMESTAMP => '2024-01-01 00:00:00'::TIMESTAMP);

-- Query table before statement
SELECT * FROM customers BEFORE(STATEMENT => '019c8ff6-0001-8c3f-0000-0001abcd1234');

-- Query table as of offset (seconds ago)
SELECT * FROM customers AT(OFFSET => -3600);

-- Undrop table (within retention period)
UNDROP TABLE customers;

-- Set data retention time
ALTER TABLE customers SET DATA_RETENTION_TIME_IN_DAYS = 90;
```

### Zero-Copy Cloning
```sql
-- Clone table
CREATE TABLE customers_dev CLONE customers;

-- Clone at specific timestamp
CREATE TABLE customers_jan1 CLONE customers
    AT(TIMESTAMP => '2024-01-01 00:00:00'::TIMESTAMP);

-- Clone schema
CREATE SCHEMA analytics_dev CLONE analytics_prod;

-- Clone database
CREATE DATABASE dev_db CLONE prod_db;
```

## Clustering

### Clustering Keys
```sql
-- Create table with clustering
CREATE TABLE events (
    event_time TIMESTAMP,
    user_id NUMBER,
    event_type VARCHAR
) CLUSTER BY (event_time, user_id);

-- Add clustering to existing table
ALTER TABLE events CLUSTER BY (event_time, user_id);

-- Drop clustering
ALTER TABLE events DROP CLUSTERING KEY;

-- Show clustering information
SHOW TABLES LIKE 'events';
SELECT SYSTEM$CLUSTERING_INFORMATION('events');
```

### Automatic Clustering
```sql
-- Enable automatic clustering
ALTER TABLE events SUSPEND RECLUSTER;
ALTER TABLE events RESUME RECLUSTER;

-- Check clustering depth (lower is better)
SELECT SYSTEM$CLUSTERING_DEPTH('events');
```

## Streams & Tasks

### Streams (Change Data Capture)
```sql
-- Create stream on table
CREATE STREAM customer_stream ON TABLE customers;

-- Create stream with append-only
CREATE STREAM customer_append_stream ON TABLE customers
    APPEND_ONLY = TRUE;

-- Query stream (shows changes)
SELECT * FROM customer_stream;

-- Show streams
SHOW STREAMS;
```

### Tasks (Scheduling)
```sql
-- Create task
CREATE TASK load_daily
    WAREHOUSE = etl_wh
    SCHEDULE = 'USING CRON 0 9 * * * America/Los_Angeles'
AS
    INSERT INTO summary_table SELECT ...;

-- Create task with stream dependency
CREATE TASK process_changes
    WAREHOUSE = etl_wh
    SCHEDULE = '5 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('customer_stream')
AS
    MERGE INTO target USING customer_stream ...;

-- Task management
ALTER TASK load_daily RESUME;
ALTER TASK load_daily SUSPEND;
SHOW TASKS;
DESCRIBE TASK load_daily;
```

## Data Loading

### COPY INTO
```sql
-- Load from S3
COPY INTO customers
FROM s3://mybucket/data/customers/
CREDENTIALS = (AWS_KEY_ID='...' AWS_SECRET_KEY='...')
FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = ',' SKIP_HEADER = 1);

-- Load from Azure Blob
COPY INTO customers
FROM 'azure://myaccount.blob.core.windows.net/mycontainer/data/'
CREDENTIALS = (AZURE_SAS_TOKEN='...')
FILE_FORMAT = (TYPE = 'PARQUET');

-- Load from stage
COPY INTO customers
FROM @my_stage/customers/
FILE_FORMAT = my_csv_format
ON_ERROR = 'CONTINUE';

-- Load with transformations
COPY INTO customers (customer_id, name, email)
FROM (
    SELECT $1, UPPER($2), LOWER($3)
    FROM @my_stage/customers/
)
FILE_FORMAT = my_csv_format;
```

### Stages
```sql
-- Create internal stage
CREATE STAGE my_internal_stage;

-- Create external stage (S3)
CREATE STAGE my_s3_stage
    URL = 's3://mybucket/path/'
    CREDENTIALS = (AWS_KEY_ID='...' AWS_SECRET_KEY='...');

-- List files in stage
LIST @my_stage;

-- Put file into stage (from SnowSQL)
PUT file:///tmp/data.csv @my_stage;

-- Remove files from stage
REMOVE @my_stage/data.csv;
```

## File Formats

```sql
-- Create CSV file format
CREATE FILE FORMAT my_csv_format
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    COMPRESSION = 'GZIP';

-- Create JSON file format
CREATE FILE FORMAT my_json_format
    TYPE = 'JSON'
    COMPRESSION = 'AUTO'
    STRIP_OUTER_ARRAY = TRUE;

-- Create Parquet file format
CREATE FILE FORMAT my_parquet_format
    TYPE = 'PARQUET'
    COMPRESSION = 'SNAPPY';

-- Show file formats
SHOW FILE FORMATS;
```

## Semi-Structured Data

### Variant Column
```sql
-- Create table with VARIANT
CREATE TABLE events (
    event_id NUMBER,
    event_data VARIANT,
    created_at TIMESTAMP
);

-- Insert JSON
INSERT INTO events (event_id, event_data)
SELECT 1, PARSE_JSON('{"user_id": 123, "action": "click"}');

-- Query JSON fields
SELECT
    event_data:user_id::NUMBER as user_id,
    event_data:action::STRING as action
FROM events;

-- Flatten nested arrays
SELECT
    event_id,
    f.value:name::STRING as item_name,
    f.value:price::NUMBER as item_price
FROM events,
LATERAL FLATTEN(input => event_data:items) f;
```

## Security & Access Control

### Roles
```sql
-- Create role
CREATE ROLE analyst_role;

-- Grant role to user
GRANT ROLE analyst_role TO USER john_doe;

-- Show grants
SHOW GRANTS TO ROLE analyst_role;
SHOW GRANTS TO USER john_doe;
```

### Privileges
```sql
-- Grant database privileges
GRANT USAGE ON DATABASE my_database TO ROLE analyst_role;
GRANT USAGE ON SCHEMA my_schema TO ROLE analyst_role;

-- Grant table privileges
GRANT SELECT ON TABLE customers TO ROLE analyst_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA my_schema TO ROLE etl_role;

-- Grant warehouse privileges
GRANT USAGE ON WAREHOUSE analytics_wh TO ROLE analyst_role;

-- Revoke privileges
REVOKE SELECT ON TABLE customers FROM ROLE analyst_role;
```

### Row Access Policies
```sql
-- Create row access policy
CREATE ROW ACCESS POLICY customer_policy AS (user_region VARCHAR)
RETURNS BOOLEAN ->
    CURRENT_ROLE() = 'ADMIN'
    OR user_region = CURRENT_USER();

-- Apply policy to table
ALTER TABLE customers
    ADD ROW ACCESS POLICY customer_policy ON (region);

-- Drop policy
ALTER TABLE customers
    DROP ROW ACCESS POLICY customer_policy;
```

## Query Optimization

### Query Profile
```sql
-- View query history
SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE QUERY_TEXT LIKE '%customers%'
ORDER BY START_TIME DESC
LIMIT 10;

-- Get query ID
SELECT LAST_QUERY_ID();

-- View query profile (in UI or via query ID)
```

### Result Caching
```sql
-- Disable result cache for session
ALTER SESSION SET USE_CACHED_RESULT = FALSE;

-- Check if query used cache
SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE QUERY_ID = LAST_QUERY_ID();
-- Look at QUERY_RESULT_CACHE column
```

## Materialized Views

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW customer_summary AS
SELECT
    region,
    COUNT(*) as customer_count,
    SUM(total_sales) as total_sales
FROM customers
GROUP BY region;

-- Refresh materialized view (manual)
ALTER MATERIALIZED VIEW customer_summary REFRESH;

-- Show materialized views
SHOW MATERIALIZED VIEWS;

-- Drop materialized view
DROP MATERIALIZED VIEW customer_summary;
```

## Information Schema

```sql
-- List all tables
SELECT * FROM information_schema.tables
WHERE table_schema = 'PUBLIC';

-- List all columns
SELECT * FROM information_schema.columns
WHERE table_name = 'CUSTOMERS';

-- View usage
SELECT * FROM snowflake.account_usage.warehouse_metering_history
WHERE warehouse_name = 'ANALYTICS_WH'
AND start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP());

-- Storage usage
SELECT * FROM snowflake.account_usage.storage_usage
ORDER BY usage_date DESC;

-- Query history
SELECT * FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -1, CURRENT_TIMESTAMP())
ORDER BY total_elapsed_time DESC
LIMIT 10;
```

## Data Sharing

```sql
-- Create share
CREATE SHARE my_share;

-- Grant database to share
GRANT USAGE ON DATABASE shared_db TO SHARE my_share;
GRANT USAGE ON SCHEMA shared_db.public TO SHARE my_share;
GRANT SELECT ON TABLE shared_db.public.customers TO SHARE my_share;

-- Add account to share
ALTER SHARE my_share ADD ACCOUNTS = xy12345;

-- Show shares
SHOW SHARES;

-- Create database from share (consumer)
CREATE DATABASE shared_data FROM SHARE provider_account.my_share;
```

## Best Practices

1. **Warehouse Management**
   - Use auto-suspend to save costs
   - Right-size warehouses for workloads
   - Separate warehouses by workload type

2. **Performance**
   - Cluster large tables on filter columns
   - Use appropriate data types (avoid VARCHAR(16777216))
   - Leverage result caching

3. **Cost Optimization**
   - Monitor warehouse usage regularly
   - Use transient tables for temporary data
   - Leverage time travel retention settings appropriately

4. **Security**
   - Use role-based access control
   - Implement row-level security where needed
   - Audit access and queries regularly

5. **Data Loading**
   - Use COPY INTO for bulk loading
   - Load compressed files when possible
   - Validate data with ON_ERROR options
