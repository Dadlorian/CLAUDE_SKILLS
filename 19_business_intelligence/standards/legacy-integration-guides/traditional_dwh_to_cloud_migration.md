# Traditional Data Warehouse to Cloud Migration Guide

## Executive Summary

This guide provides comprehensive strategies for migrating traditional on-premise data warehouses (Oracle, Teradata, SQL Server, IBM Db2) to modern cloud platforms (Snowflake, Google BigQuery, Amazon Redshift, Azure Synapse Analytics). The focus is on minimizing business disruption while maximizing the benefits of cloud-native capabilities.

## Table of Contents

1. [Cloud Platform Selection](#cloud-platform-selection)
2. [Schema Migration Strategies](#schema-migration-strategies)
3. [ETL to ELT Transformation](#etl-to-elt-transformation)
4. [Data Validation and Reconciliation](#data-validation-and-reconciliation)
5. [Performance Optimization](#performance-optimization)
6. [Cost Management](#cost-management)
7. [Migration Checklists](#migration-checklists)

---

## Cloud Platform Selection

### 1.1 Platform Comparison Matrix

| Capability | Snowflake | BigQuery | Redshift | Synapse Analytics |
|------------|-----------|----------|----------|-------------------|
| **Architecture** | Multi-cluster shared data | Serverless | Cluster-based | Hybrid (dedicated/serverless) |
| **Scaling** | Auto-scale compute | Auto-scale everything | Manual resize | Auto-scale compute |
| **Pricing Model** | Compute + Storage | Queries + Storage | Hourly + Storage | DTU/vCore + Storage |
| **Best For** | General purpose, multi-workload | Analytics, ML integration | AWS ecosystem | Microsoft ecosystem |
| **Data Lake Support** | External tables | Native BigLake | Spectrum | Data Lake integration |
| **Concurrency** | Excellent (multi-cluster) | Excellent (serverless) | Good (WLM) | Good (workload groups) |
| **Learning Curve** | Low | Medium | Medium | Medium-High |
| **TCO (Typical)** | $$ | $ - $$$ | $$ | $$ |

### 1.2 Decision Framework

**Selection Criteria:**

```python
def recommend_cloud_dwh(requirements):
    """
    Recommend cloud data warehouse based on requirements
    """
    score = {
        'snowflake': 0,
        'bigquery': 0,
        'redshift': 0,
        'synapse': 0
    }

    # Cloud provider affinity
    if requirements['cloud_provider'] == 'AWS':
        score['redshift'] += 3
        score['snowflake'] += 2
    elif requirements['cloud_provider'] == 'Azure':
        score['synapse'] += 3
        score['snowflake'] += 2
    elif requirements['cloud_provider'] == 'GCP':
        score['bigquery'] += 3
        score['snowflake'] += 2

    # Workload characteristics
    if requirements['workload_type'] == 'analytics_heavy':
        score['bigquery'] += 2
        score['snowflake'] += 2
    elif requirements['workload_type'] == 'mixed':
        score['snowflake'] += 3
        score['synapse'] += 2
    elif requirements['workload_type'] == 'concurrent_users':
        score['snowflake'] += 3
        score['redshift'] += 1

    # Cost sensitivity
    if requirements['cost_priority'] == 'high':
        score['bigquery'] += 2  # Pay per query can be cheaper
        score['redshift'] += 1  # Reserved instances

    # ML/AI requirements
    if requirements['ml_integration']:
        score['bigquery'] += 3
        score['snowflake'] += 1

    # Existing tools
    if requirements['bi_tools'] == 'power_bi':
        score['synapse'] += 2
        score['snowflake'] += 1
    elif requirements['bi_tools'] == 'tableau':
        score['snowflake'] += 2
        score['redshift'] += 1

    # Semi-structured data
    if requirements['semi_structured_data']:
        score['snowflake'] += 3
        score['bigquery'] += 2
        score['redshift'] += 1

    return sorted(score.items(), key=lambda x: x[1], reverse=True)
```

### 1.3 Platform-Specific Migration Paths

**Oracle to Snowflake:**
- Strong SQL compatibility
- PL/SQL → JavaScript stored procedures
- Materialized views → Auto-clustering + search optimization
- Partitioning → Micro-partitions (automatic)

**Teradata to BigQuery:**
- Similar MPP architecture
- BTEQ → bq command-line tool
- Multiset tables → Standard SQL tables
- Teradata functions → BigQuery UDFs

**SQL Server to Redshift:**
- T-SQL compatibility (subset)
- SSIS → AWS Glue
- Linked servers → Federated queries
- Columnstore → Native column storage

**Db2 to Synapse:**
- Microsoft ecosystem alignment
- Db2 stored procedures → T-SQL
- Database links → PolyBase
- Workload management → Resource classes

---

## Schema Migration Strategies

### 2.1 Assessment and Discovery

**Schema Analysis Script:**

```sql
-- Oracle: Analyze schema for migration
SELECT
    owner,
    object_type,
    COUNT(*) as object_count,
    SUM(CASE WHEN status = 'INVALID' THEN 1 ELSE 0 END) as invalid_objects
FROM dba_objects
WHERE owner IN ('SALES_DW', 'FINANCE_DW', 'OPERATIONS_DW')
GROUP BY owner, object_type
ORDER BY owner, object_type;

-- Get table sizes and row counts
SELECT
    segment_name,
    ROUND(bytes/1024/1024/1024, 2) as size_gb,
    num_rows,
    last_analyzed
FROM dba_segments s
JOIN dba_tables t ON s.segment_name = t.table_name AND s.owner = t.owner
WHERE s.owner = 'SALES_DW'
    AND s.segment_type = 'TABLE'
ORDER BY bytes DESC;

-- Identify dependencies
SELECT
    name,
    type,
    referenced_owner,
    referenced_name,
    referenced_type
FROM dba_dependencies
WHERE owner = 'SALES_DW'
    AND type IN ('VIEW', 'PROCEDURE', 'FUNCTION', 'PACKAGE')
ORDER BY name, referenced_name;

-- Find complex data types
SELECT
    table_name,
    column_name,
    data_type,
    data_length,
    data_precision,
    data_scale
FROM dba_tab_columns
WHERE owner = 'SALES_DW'
    AND data_type IN ('BLOB', 'CLOB', 'XMLTYPE', 'LONG', 'LONG RAW')
ORDER BY table_name, column_name;
```

**Teradata Assessment:**

```sql
-- Teradata: Get database statistics
SELECT
    DatabaseName,
    TableName,
    SUM(CurrentPerm) / 1024 / 1024 / 1024 as Size_GB,
    COUNT(DISTINCT ColumnName) as Column_Count
FROM DBC.TableSize
WHERE DatabaseName = 'SALES_DW'
GROUP BY DatabaseName, TableName
ORDER BY Size_GB DESC;

-- Identify Primary Indexes (critical for performance)
SELECT
    DatabaseName,
    TableName,
    ColumnName,
    IndexType,
    IndexNumber
FROM DBC.Indices
WHERE DatabaseName = 'SALES_DW'
    AND IndexType IN ('P', 'Q')  -- Primary and Primary AMP
ORDER BY TableName, IndexNumber;

-- Secondary indexes
SELECT
    DatabaseName,
    TableName,
    IndexName,
    ColumnName,
    UniqueFlag
FROM DBC.Indices
WHERE DatabaseName = 'SALES_DW'
    AND IndexType = 'S'  -- Secondary Index
ORDER BY TableName, IndexName;
```

### 2.2 Schema Conversion

**Automated Conversion Tools:**

1. **AWS Schema Conversion Tool (SCT)**
   - Oracle → Redshift
   - SQL Server → Redshift
   - Teradata → Redshift

2. **Snowflake SnowConvert**
   - Oracle → Snowflake
   - Teradata → Snowflake
   - SQL Server → Snowflake

3. **Google BigQuery Migration Service**
   - Teradata → BigQuery
   - Oracle → BigQuery
   - Redshift → BigQuery

4. **Azure Database Migration Service**
   - SQL Server → Synapse
   - Oracle → Synapse

**Manual Conversion Patterns:**

```sql
-- Oracle to Snowflake Example

-- BEFORE (Oracle):
CREATE TABLE sales_fact (
    sale_id NUMBER PRIMARY KEY,
    sale_date DATE,
    customer_id NUMBER NOT NULL,
    product_id NUMBER NOT NULL,
    quantity NUMBER(10,2),
    amount NUMBER(15,2),
    created_ts TIMESTAMP DEFAULT SYSDATE,
    CONSTRAINT fk_customer FOREIGN KEY (customer_id)
        REFERENCES customer_dim(customer_id),
    CONSTRAINT fk_product FOREIGN KEY (product_id)
        REFERENCES product_dim(product_id)
)
PARTITION BY RANGE (sale_date) (
    PARTITION p_2023_q1 VALUES LESS THAN (TO_DATE('2023-04-01', 'YYYY-MM-DD')),
    PARTITION p_2023_q2 VALUES LESS THAN (TO_DATE('2023-07-01', 'YYYY-MM-DD')),
    PARTITION p_2023_q3 VALUES LESS THAN (TO_DATE('2023-10-01', 'YYYY-MM-DD'))
);

-- AFTER (Snowflake):
CREATE TABLE sales_fact (
    sale_id NUMBER PRIMARY KEY,
    sale_date DATE,
    customer_id NUMBER NOT NULL,
    product_id NUMBER NOT NULL,
    quantity NUMBER(10,2),
    amount NUMBER(15,2),
    created_ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    -- Foreign keys are informational only in Snowflake
    CONSTRAINT fk_customer FOREIGN KEY (customer_id)
        REFERENCES customer_dim(customer_id) NOT ENFORCED,
    CONSTRAINT fk_product FOREIGN KEY (product_id)
        REFERENCES product_dim(product_id) NOT ENFORCED
)
-- Snowflake handles partitioning automatically via micro-partitions
CLUSTER BY (sale_date);  -- Optional clustering for query performance

-- Add search optimization for point lookups
ALTER TABLE sales_fact ADD SEARCH OPTIMIZATION ON EQUALITY(sale_id);
```

**Teradata to BigQuery:**

```sql
-- BEFORE (Teradata):
CREATE MULTISET TABLE sales_fact (
    sale_id INTEGER NOT NULL,
    sale_date DATE FORMAT 'YYYY-MM-DD',
    customer_id INTEGER,
    product_id INTEGER,
    quantity DECIMAL(10,2),
    amount DECIMAL(15,2),
    created_ts TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
)
PRIMARY INDEX (sale_id)
PARTITION BY RANGE_N(sale_date BETWEEN DATE '2023-01-01'
    AND DATE '2023-12-31' EACH INTERVAL '1' MONTH);

-- AFTER (BigQuery):
CREATE TABLE sales_fact (
    sale_id INT64 NOT NULL,
    sale_date DATE,
    customer_id INT64,
    product_id INT64,
    quantity NUMERIC(10,2),
    amount NUMERIC(15,2),
    created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY sale_date
CLUSTER BY customer_id, product_id
OPTIONS(
    description="Sales fact table migrated from Teradata",
    require_partition_filter=true
);
```

### 2.3 Data Type Mapping

**Oracle to Snowflake:**

| Oracle | Snowflake | Notes |
|--------|-----------|-------|
| NUMBER(p,s) | NUMBER(p,s) | Direct mapping |
| VARCHAR2(n) | VARCHAR(n) | Max 16MB in Snowflake |
| DATE | DATE | Snowflake DATE includes time |
| TIMESTAMP | TIMESTAMP_NTZ | No timezone |
| TIMESTAMP WITH TIME ZONE | TIMESTAMP_TZ | With timezone |
| CLOB | VARCHAR | Up to 16MB |
| BLOB | BINARY | Up to 8MB |
| XMLTYPE | VARIANT | Semi-structured |
| RAW | BINARY | Binary data |

**Teradata to BigQuery:**

| Teradata | BigQuery | Notes |
|----------|----------|-------|
| INTEGER | INT64 | 64-bit integer |
| DECIMAL(p,s) | NUMERIC(p,s) | Max p=38, s=9 |
| FLOAT | FLOAT64 | Double precision |
| VARCHAR(n) | STRING | No length limit |
| DATE | DATE | Direct mapping |
| TIMESTAMP | TIMESTAMP | Microsecond precision |
| BYTE | BYTES | Binary data |
| JSON | JSON | Native JSON type |
| PERIOD | STRUCT | Custom type |

**SQL Server to Redshift:**

| SQL Server | Redshift | Notes |
|------------|----------|-------|
| INT | INTEGER | Direct mapping |
| BIGINT | BIGINT | Direct mapping |
| DECIMAL(p,s) | DECIMAL(p,s) | Max p=38 |
| VARCHAR(n) | VARCHAR(n) | Max 65535 |
| NVARCHAR(n) | VARCHAR(n) | UTF-8 encoding |
| DATE | DATE | Direct mapping |
| DATETIME2 | TIMESTAMP | Microsecond precision |
| VARBINARY | VARBINARY | Max 1MB |
| XML | VARCHAR | Store as text |
| GEOGRAPHY | GEOMETRY | Use PostGIS |

### 2.4 Schema Migration Patterns

**Pattern 1: Schema-First Migration**

```yaml
migration_phases:
  phase_1_schema:
    - Create target schema structure
    - Create staging tables
    - Setup constraints (non-enforced if needed)
    - Create views and materialized views
    - Setup security and permissions

  phase_2_data:
    - Bulk load historical data
    - Incremental sync
    - Final cutover load

  phase_3_code:
    - Migrate stored procedures
    - Migrate functions
    - Migrate ETL jobs

  phase_4_validation:
    - Row count validation
    - Data validation
    - Performance testing
```

**Pattern 2: Incremental Schema Evolution**

```sql
-- Week 1: Core fact and dimension tables
CREATE SCHEMA sales_dw_v2;

CREATE TABLE sales_dw_v2.customer_dim AS
SELECT * FROM legacy.customer_dim LIMIT 0;

CREATE TABLE sales_dw_v2.product_dim AS
SELECT * FROM legacy.product_dim LIMIT 0;

CREATE TABLE sales_dw_v2.sales_fact AS
SELECT * FROM legacy.sales_fact LIMIT 0;

-- Week 2: Add dependent objects
CREATE VIEW sales_dw_v2.sales_summary AS
SELECT
    c.customer_name,
    p.product_name,
    SUM(s.amount) as total_sales
FROM sales_dw_v2.sales_fact s
JOIN sales_dw_v2.customer_dim c ON s.customer_id = c.customer_id
JOIN sales_dw_v2.product_dim p ON s.product_id = p.product_id
GROUP BY c.customer_name, p.product_name;

-- Week 3: Migrate stored procedures
CREATE OR REPLACE PROCEDURE sales_dw_v2.refresh_sales_summary()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Refresh logic
    MERGE INTO sales_summary_mat ...;
    RETURN 'SUCCESS';
END;
$$;
```

---

## ETL to ELT Transformation

### 3.1 ETL vs ELT Paradigm Shift

**Traditional ETL (On-Premise):**
```
Extract → Transform (ETL Server) → Load (Data Warehouse)
```

**Modern ELT (Cloud):**
```
Extract → Load (Cloud Data Warehouse) → Transform (In-Database)
```

**Why ELT in Cloud?**

1. **Scalable Compute:** Cloud DWH can handle transformations at scale
2. **Cost Efficiency:** Only pay for compute when transforming
3. **Data Freshness:** Load raw data immediately, transform on-demand
4. **Flexibility:** Raw data available for multiple transformation paths
5. **Auditability:** Transformation logic in SQL, version controlled

### 3.2 Migrating ETL Workflows

**SSIS to Cloud ELT:**

```python
# BEFORE: SSIS Package (Pseudo-code)
# Data Flow Task:
#   1. OLE DB Source (SQL Server)
#   2. Derived Column Transformation
#   3. Lookup Transformation
#   4. Aggregate Transformation
#   5. OLE DB Destination

# AFTER: ELT with dbt (Data Build Tool)

# models/staging/stg_orders.sql
{{ config(materialized='view') }}

SELECT
    order_id,
    customer_id,
    order_date,
    -- Derived columns (SSIS Derived Column Transformation)
    CASE
        WHEN order_status = 'C' THEN 'Completed'
        WHEN order_status = 'P' THEN 'Pending'
        ELSE 'Unknown'
    END as order_status_desc,
    order_amount,
    _loaded_at as etl_timestamp
FROM {{ source('raw', 'orders') }}
WHERE order_date >= CURRENT_DATE - INTERVAL '2 YEARS';

# models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    cluster_by=['order_date']
) }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

-- Lookup Transformation (SSIS Lookup)
customers AS (
    SELECT
        customer_id,
        customer_name,
        customer_segment
    FROM {{ ref('dim_customers') }}
),

enriched_orders AS (
    SELECT
        o.order_id,
        o.customer_id,
        c.customer_name,
        c.customer_segment,
        o.order_date,
        o.order_status_desc,
        o.order_amount
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
)

SELECT * FROM enriched_orders

{% if is_incremental() %}
    WHERE order_date > (SELECT MAX(order_date) FROM {{ this }})
{% endif %};

# models/marts/agg_daily_sales.sql
-- Aggregate Transformation (SSIS Aggregate)
{{ config(materialized='table') }}

SELECT
    order_date,
    customer_segment,
    COUNT(DISTINCT order_id) as order_count,
    SUM(order_amount) as total_sales,
    AVG(order_amount) as avg_order_value
FROM {{ ref('fct_orders') }}
GROUP BY order_date, customer_segment;
```

**Informatica to Cloud ELT:**

```sql
-- BEFORE: Informatica PowerCenter Mapping
-- Source Qualifier -> Expression -> Router -> Aggregator -> Target

-- AFTER: Cloud DWH SQL (Snowflake example)

-- Step 1: Load raw data (simple COPY command)
COPY INTO raw.customer_transactions
FROM @s3_stage/customer_transactions/
FILE_FORMAT = (TYPE = 'PARQUET')
PATTERN = '.*\.parquet';

-- Step 2: Transform (Expression + Router logic)
CREATE OR REPLACE TABLE staging.customer_transactions_processed AS
SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,
    -- Expression transformation
    UPPER(TRIM(customer_name)) as customer_name_clean,
    CASE
        WHEN amount >= 1000 THEN 'High Value'
        WHEN amount >= 100 THEN 'Medium Value'
        ELSE 'Low Value'
    END as transaction_tier,
    -- Date calculations
    DATE_TRUNC('month', transaction_date) as transaction_month,
    YEAR(transaction_date) as transaction_year
FROM raw.customer_transactions
-- Router transformation (filter logic)
WHERE transaction_date >= DATEADD(year, -2, CURRENT_DATE())
    AND amount > 0
    AND customer_id IS NOT NULL;

-- Step 3: Aggregate
CREATE OR REPLACE TABLE analytics.customer_monthly_summary AS
SELECT
    customer_id,
    transaction_month,
    transaction_tier,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    MAX(amount) as max_amount,
    MIN(amount) as min_amount
FROM staging.customer_transactions_processed
GROUP BY customer_id, transaction_month, transaction_tier;
```

**DataStage to AWS Glue:**

```python
# AWS Glue PySpark Script (converted from DataStage job)

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'SOURCE_PATH', 'TARGET_TABLE'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read from S3 (DataStage Sequential File stage)
source_df = spark.read.parquet(args['SOURCE_PATH'])

# Transformer stage logic
transformed_df = source_df \
    .filter(col("order_date") >= date_sub(current_date(), 730)) \
    .withColumn("order_year", year(col("order_date"))) \
    .withColumn("order_month", month(col("order_date"))) \
    .withColumn("order_amount_usd",
                when(col("currency") == "EUR", col("amount") * 1.1)
                .when(col("currency") == "GBP", col("amount") * 1.3)
                .otherwise(col("amount"))) \
    .select("order_id", "customer_id", "order_date", "order_year",
            "order_month", "order_amount_usd")

# Aggregator stage
aggregated_df = transformed_df \
    .groupBy("customer_id", "order_year", "order_month") \
    .agg(
        count("order_id").alias("order_count"),
        sum("order_amount_usd").alias("total_spent"),
        avg("order_amount_usd").alias("avg_order_value")
    )

# Write to Redshift (DataStage Target stage)
glueContext.write_dynamic_frame.from_options(
    frame = DynamicFrame.fromDF(aggregated_df, glueContext, "aggregated"),
    connection_type = "redshift",
    connection_options = {
        "url": "jdbc:redshift://cluster.region.redshift.amazonaws.com:5439/dwh",
        "dbtable": args['TARGET_TABLE'],
        "redshiftTmpDir": "s3://temp-bucket/glue-temp/",
        "aws_iam_role": "arn:aws:iam::account:role/RedshiftGlueRole"
    }
)

job.commit()
```

### 3.3 ELT Orchestration

**Modern ELT Stack:**

```yaml
# Airflow DAG for ELT orchestration

from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.dbt.operators.dbt import DbtRunOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email': ['data-alerts@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'daily_sales_elt',
    default_args=default_args,
    description='Daily sales data ELT pipeline',
    schedule_interval='0 6 * * *',  # 6 AM daily
    catchup=False
)

# Task 1: Extract and Load (EL)
extract_load = SnowflakeOperator(
    task_id='extract_load_raw_data',
    snowflake_conn_id='snowflake_default',
    sql='''
        -- Copy from S3 to Snowflake
        COPY INTO raw.sales_transactions
        FROM @s3_sales_stage
        FILE_FORMAT = (TYPE = 'PARQUET')
        PATTERN = 'sales_{{ ds }}.*\.parquet'
        ON_ERROR = 'CONTINUE';

        -- Track load
        INSERT INTO audit.etl_log (job_name, load_date, status, rows_loaded)
        SELECT 'daily_sales_elt', CURRENT_TIMESTAMP(), 'SUCCESS',
               (SELECT COUNT(*) FROM raw.sales_transactions
                WHERE load_date = '{{ ds }}');
    ''',
    dag=dag
)

# Task 2: Transform (T) - dbt models
transform_staging = DbtRunOperator(
    task_id='transform_staging_models',
    dbt_conn_id='dbt_default',
    models='staging',
    dag=dag
)

transform_marts = DbtRunOperator(
    task_id='transform_mart_models',
    dbt_conn_id='dbt_default',
    models='marts',
    dag=dag
)

# Task 3: Data quality checks
def run_data_quality_checks(**context):
    # Custom data quality validation
    from snowflake.connector import connect

    conn = connect(...)
    cursor = conn.cursor()

    # Check 1: Row count validation
    cursor.execute("""
        SELECT COUNT(*) FROM analytics.fct_sales
        WHERE sale_date = '{{ ds }}'
    """)
    row_count = cursor.fetchone()[0]

    if row_count == 0:
        raise ValueError("No data loaded for {{ ds }}")

    # Check 2: Amount validation
    cursor.execute("""
        SELECT SUM(amount) FROM analytics.fct_sales
        WHERE sale_date = '{{ ds }}'
    """)
    total_amount = cursor.fetchone()[0]

    if total_amount is None or total_amount < 0:
        raise ValueError("Invalid total amount for {{ ds }}")

    print(f"Data quality checks passed: {row_count} rows, ${total_amount:,.2f} total")

data_quality = PythonOperator(
    task_id='data_quality_checks',
    python_callable=run_data_quality_checks,
    provide_context=True,
    dag=dag
)

# Task 4: Refresh materialized views
refresh_mvs = SnowflakeOperator(
    task_id='refresh_materialized_views',
    snowflake_conn_id='snowflake_default',
    sql='''
        -- Refresh key materialized views
        ALTER MATERIALIZED VIEW analytics.mv_daily_sales_summary REFRESH;
        ALTER MATERIALIZED VIEW analytics.mv_customer_ltv REFRESH;
    ''',
    dag=dag
)

# Define dependencies
extract_load >> transform_staging >> transform_marts >> data_quality >> refresh_mvs
```

---

## Data Validation and Reconciliation

### 4.1 Validation Framework

**Multi-Level Validation Strategy:**

```python
# Comprehensive data validation framework

import pandas as pd
from dataclasses import dataclass
from typing import List, Dict
import snowflake.connector

@dataclass
class ValidationResult:
    check_name: str
    status: str  # PASS, FAIL, WARNING
    source_value: any
    target_value: any
    variance: float
    details: str

class DataMigrationValidator:
    def __init__(self, source_conn, target_conn):
        self.source_conn = source_conn
        self.target_conn = target_conn
        self.results = []

    def validate_row_counts(self, table_name: str) -> ValidationResult:
        """Level 1: Row count validation"""
        source_query = f"SELECT COUNT(*) FROM {table_name}"
        target_query = f"SELECT COUNT(*) FROM {table_name}"

        source_count = self.execute_query(self.source_conn, source_query)[0][0]
        target_count = self.execute_query(self.target_conn, target_query)[0][0]

        variance = abs(source_count - target_count) / source_count if source_count > 0 else 0

        status = 'PASS' if variance == 0 else ('WARNING' if variance < 0.01 else 'FAIL')

        return ValidationResult(
            check_name=f"Row Count - {table_name}",
            status=status,
            source_value=source_count,
            target_value=target_count,
            variance=variance,
            details=f"Difference: {abs(source_count - target_count)} rows"
        )

    def validate_column_sums(self, table_name: str, numeric_columns: List[str]) -> List[ValidationResult]:
        """Level 2: Aggregate validation"""
        results = []

        for column in numeric_columns:
            source_query = f"SELECT SUM({column}) FROM {table_name}"
            target_query = f"SELECT SUM({column}) FROM {table_name}"

            source_sum = self.execute_query(self.source_conn, source_query)[0][0] or 0
            target_sum = self.execute_query(self.target_conn, target_query)[0][0] or 0

            variance = abs(source_sum - target_sum) / source_sum if source_sum != 0 else 0

            status = 'PASS' if variance < 0.0001 else ('WARNING' if variance < 0.01 else 'FAIL')

            results.append(ValidationResult(
                check_name=f"Sum - {table_name}.{column}",
                status=status,
                source_value=source_sum,
                target_value=target_sum,
                variance=variance,
                details=f"Variance: {variance*100:.4f}%"
            ))

        return results

    def validate_data_distribution(self, table_name: str, column: str) -> ValidationResult:
        """Level 3: Statistical distribution validation"""
        source_query = f"""
            SELECT
                MIN({column}) as min_val,
                MAX({column}) as max_val,
                AVG({column}) as avg_val,
                STDDEV({column}) as stddev_val,
                MEDIAN({column}) as median_val
            FROM {table_name}
        """

        source_stats = self.execute_query(self.source_conn, source_query)[0]
        target_stats = self.execute_query(self.target_conn, source_query)[0]

        # Calculate variance across all statistics
        variances = []
        for i in range(len(source_stats)):
            if source_stats[i] and source_stats[i] != 0:
                var = abs(source_stats[i] - target_stats[i]) / source_stats[i]
                variances.append(var)

        max_variance = max(variances) if variances else 0
        status = 'PASS' if max_variance < 0.01 else ('WARNING' if max_variance < 0.05 else 'FAIL')

        return ValidationResult(
            check_name=f"Distribution - {table_name}.{column}",
            status=status,
            source_value=source_stats,
            target_value=target_stats,
            variance=max_variance,
            details=f"Max variance in statistics: {max_variance*100:.2f}%"
        )

    def validate_sample_records(self, table_name: str, sample_size: int = 1000) -> ValidationResult:
        """Level 4: Row-level sample validation"""
        # Get primary key column
        pk_column = self.get_primary_key(table_name)

        # Get random sample
        source_query = f"""
            SELECT * FROM {table_name}
            ORDER BY RANDOM()
            LIMIT {sample_size}
        """

        source_sample = pd.DataFrame(self.execute_query(self.source_conn, source_query))

        # Fetch same records from target
        pk_values = source_sample[pk_column].tolist()
        target_query = f"""
            SELECT * FROM {table_name}
            WHERE {pk_column} IN ({','.join(map(str, pk_values))})
        """

        target_sample = pd.DataFrame(self.execute_query(self.target_conn, target_query))

        # Compare
        mismatches = 0
        for idx, source_row in source_sample.iterrows():
            target_row = target_sample[target_sample[pk_column] == source_row[pk_column]]
            if not target_row.equals(source_row):
                mismatches += 1

        variance = mismatches / sample_size
        status = 'PASS' if variance == 0 else ('WARNING' if variance < 0.01 else 'FAIL')

        return ValidationResult(
            check_name=f"Sample Records - {table_name}",
            status=status,
            source_value=sample_size,
            target_value=sample_size - mismatches,
            variance=variance,
            details=f"{mismatches} mismatches out of {sample_size} samples"
        )

    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        report = "# Data Migration Validation Report\n\n"
        report += f"**Generated:** {datetime.now()}\n\n"

        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == 'PASS')
        warnings = sum(1 for r in self.results if r.status == 'WARNING')
        failed = sum(1 for r in self.results if r.status == 'FAIL')

        report += "## Summary\n"
        report += f"- Total Checks: {total}\n"
        report += f"- Passed: {passed} ({passed/total*100:.1f}%)\n"
        report += f"- Warnings: {warnings} ({warnings/total*100:.1f}%)\n"
        report += f"- Failed: {failed} ({failed/total*100:.1f}%)\n\n"

        # Details
        report += "## Detailed Results\n\n"
        for result in self.results:
            report += f"### {result.check_name}\n"
            report += f"- **Status:** {result.status}\n"
            report += f"- **Source Value:** {result.source_value}\n"
            report += f"- **Target Value:** {result.target_value}\n"
            report += f"- **Variance:** {result.variance*100:.4f}%\n"
            report += f"- **Details:** {result.details}\n\n"

        return report
```

### 4.2 Reconciliation Queries

**Daily Reconciliation Script:**

```sql
-- Snowflake: Daily reconciliation between legacy and cloud DWH

CREATE OR REPLACE PROCEDURE reconcile_daily_data(
    p_table_name VARCHAR,
    p_date DATE
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    v_source_count INTEGER;
    v_target_count INTEGER;
    v_source_sum FLOAT;
    v_target_sum FLOAT;
    v_status VARCHAR;
BEGIN
    -- Count comparison
    SELECT COUNT(*) INTO :v_source_count
    FROM IDENTIFIER(:p_table_name || '_legacy')
    WHERE load_date = :p_date;

    SELECT COUNT(*) INTO :v_target_count
    FROM IDENTIFIER(:p_table_name)
    WHERE load_date = :p_date;

    -- Sum comparison (for amount columns)
    SELECT COALESCE(SUM(amount), 0) INTO :v_source_sum
    FROM IDENTIFIER(:p_table_name || '_legacy')
    WHERE load_date = :p_date;

    SELECT COALESCE(SUM(amount), 0) INTO :v_target_sum
    FROM IDENTIFIER(:p_table_name)
    WHERE load_date = :p_date;

    -- Determine status
    IF (v_source_count = v_target_count AND ABS(v_source_sum - v_target_sum) < 0.01) THEN
        v_status := 'PASS';
    ELSE
        v_status := 'FAIL';
    END IF;

    -- Log results
    INSERT INTO reconciliation_log (
        table_name,
        recon_date,
        source_count,
        target_count,
        source_sum,
        target_sum,
        status,
        created_at
    )
    VALUES (
        :p_table_name,
        :p_date,
        :v_source_count,
        :v_target_count,
        :v_source_sum,
        :v_target_sum,
        :v_status,
        CURRENT_TIMESTAMP()
    );

    RETURN v_status || ': Source=' || v_source_count || ', Target=' || v_target_count;
END;
$$;

-- Run reconciliation for all tables
CALL reconcile_daily_data('sales_fact', CURRENT_DATE());
CALL reconcile_daily_data('inventory_fact', CURRENT_DATE());
CALL reconcile_daily_data('customer_dim', CURRENT_DATE());
```

---

## Performance Optimization

### 5.1 Pre-Migration Performance Baseline

**Baseline Metrics to Capture:**

```sql
-- Oracle: Capture query performance baseline
SELECT
    sql_id,
    sql_text,
    executions,
    elapsed_time / 1000000 as elapsed_sec,
    cpu_time / 1000000 as cpu_sec,
    disk_reads,
    buffer_gets,
    rows_processed,
    ROUND(elapsed_time / executions / 1000000, 2) as avg_elapsed_sec
FROM v$sql
WHERE parsing_schema_name = 'SALES_DW'
    AND executions > 10
    AND elapsed_time / executions > 1000000  -- > 1 second avg
ORDER BY elapsed_time DESC
FETCH FIRST 50 ROWS ONLY;

-- Export to baseline file for comparison
```

### 5.2 Cloud Platform Optimization

**Snowflake Optimization:**

```sql
-- 1. Clustering for large tables
ALTER TABLE sales_fact CLUSTER BY (sale_date, customer_id);

-- Monitor clustering effectiveness
SELECT SYSTEM$CLUSTERING_INFORMATION('sales_fact', '(sale_date, customer_id)');

-- 2. Search optimization for point lookups
ALTER TABLE customer_dim ADD SEARCH OPTIMIZATION ON EQUALITY(customer_id, email);

-- 3. Materialized views for common aggregations
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
    sale_date,
    product_category,
    SUM(amount) as total_sales,
    COUNT(DISTINCT customer_id) as unique_customers
FROM sales_fact
GROUP BY sale_date, product_category;

-- 4. Result caching (automatic, but monitor)
ALTER SESSION SET USE_CACHED_RESULT = TRUE;

-- 5. Warehouse sizing
-- Start small, scale up based on query patterns
CREATE WAREHOUSE analytics_wh WITH
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 300  -- 5 minutes
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Monitor warehouse usage
SELECT
    warehouse_name,
    AVG(avg_running) as avg_queries_running,
    AVG(avg_queued_load) as avg_queue_load,
    SUM(credits_used) as total_credits
FROM snowflake.account_usage.warehouse_load_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY warehouse_name;
```

**BigQuery Optimization:**

```sql
-- 1. Partitioning
CREATE OR REPLACE TABLE analytics.sales_fact
PARTITION BY DATE(sale_date)
CLUSTER BY customer_id, product_id
AS SELECT * FROM legacy.sales_fact;

-- 2. Require partition filter
ALTER TABLE analytics.sales_fact
SET OPTIONS (require_partition_filter = true);

-- 3. Materialized views
CREATE MATERIALIZED VIEW analytics.mv_monthly_sales
AS
SELECT
    DATE_TRUNC(sale_date, MONTH) as month,
    product_category,
    SUM(amount) as total_sales,
    COUNT(DISTINCT customer_id) as unique_customers
FROM analytics.sales_fact
GROUP BY month, product_category;

-- 4. Table expiration for staging tables
CREATE TABLE staging.temp_data
OPTIONS(
    expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
)
AS SELECT * FROM source;

-- 5. BI Engine reservation for dashboard queries
-- (Configure in Cloud Console based on workload)

-- Monitor query performance
SELECT
    query,
    total_bytes_processed,
    total_slot_ms,
    TIMESTAMP_DIFF(end_time, start_time, SECOND) as duration_sec,
    total_bytes_billed / POW(10, 12) as tb_billed
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    AND job_type = 'QUERY'
    AND state = 'DONE'
ORDER BY total_slot_ms DESC
LIMIT 100;
```

**Redshift Optimization:**

```sql
-- 1. Distribution keys
CREATE TABLE sales_fact (
    sale_id BIGINT,
    sale_date DATE,
    customer_id BIGINT,
    product_id BIGINT,
    amount DECIMAL(15,2)
)
DISTKEY(customer_id)  -- Distribute by frequently joined column
SORTKEY(sale_date);   -- Sort by date for range queries

-- 2. Analyze tables regularly
ANALYZE sales_fact;
ANALYZE customer_dim;

-- 3. Vacuum to reclaim space
VACUUM DELETE ONLY sales_fact;
VACUUM SORT ONLY sales_fact TO 95 PERCENT;

-- 4. Workload Management (WLM)
-- Configure WLM queues in Redshift Console or parameter group
-- Example WLM configuration:
/*
[
  {
    "query_group": "dashboard",
    "memory_percent_to_use": 30,
    "max_execution_time": 30000,
    "query_concurrency": 10
  },
  {
    "query_group": "etl",
    "memory_percent_to_use": 50,
    "max_execution_time": 300000,
    "query_concurrency": 3
  },
  {
    "query_group": "default",
    "memory_percent_to_use": 20,
    "max_execution_time": 60000,
    "query_concurrency": 5
  }
]
*/

-- 5. Monitor query performance
SELECT
    query,
    trim(querytxt) as sql_text,
    starttime,
    endtime,
    datediff(ms, starttime, endtime) as duration_ms,
    aborted
FROM stl_query
WHERE userid > 1  -- Exclude system queries
    AND starttime >= DATEADD(day, -7, GETDATE())
ORDER BY duration_ms DESC
LIMIT 100;

-- Identify table scans (potential optimization opportunities)
SELECT
    TRIM(s.perm_table_name) as table_name,
    COUNT(*) as scan_count,
    SUM(s.rows) as rows_scanned,
    SUM(s.rows) / COUNT(*) as avg_rows_per_scan
FROM stl_scan s
WHERE s.starttime >= DATEADD(day, -7, GETDATE())
GROUP BY s.perm_table_name
ORDER BY scan_count DESC
LIMIT 50;
```

### 5.3 Post-Migration Performance Comparison

**Performance Comparison Report:**

```markdown
## Performance Comparison: Legacy vs Cloud

### Query Performance Benchmarks

| Query Category | Legacy Avg (sec) | Cloud Avg (sec) | Improvement |
|----------------|------------------|-----------------|-------------|
| Dashboard refresh | 45 | 8 | 82% faster |
| Daily sales report | 120 | 15 | 87% faster |
| Customer analysis | 300 | 30 | 90% faster |
| Ad-hoc queries | 60 | 12 | 80% faster |
| ETL batch jobs | 7200 | 1800 | 75% faster |

### Concurrency Testing

| Concurrent Users | Legacy (avg response) | Cloud (avg response) |
|------------------|----------------------|---------------------|
| 10 | 15 sec | 8 sec |
| 50 | 45 sec | 12 sec |
| 100 | 180 sec | 20 sec |
| 200 | Timeout (>300 sec) | 35 sec |

### Resource Utilization

- **Legacy:** 24/7 hardware running at 60-80% utilization
- **Cloud:** Auto-scaling, average 30% utilization, 70% cost savings
```

---

## Cost Management

### 6.1 TCO Analysis

**Total Cost of Ownership Comparison:**

```python
# TCO Calculator for Cloud DWH Migration

def calculate_legacy_tco(years=3):
    """Calculate TCO for legacy on-premise DWH"""
    costs = {
        'hardware': {
            'servers': 250000,  # Initial purchase
            'storage': 100000,
            'network': 50000,
            'refresh_cycle': 3,  # Replace every 3 years
        },
        'software': {
            'licenses': 150000,  # Annual
            'support': 30000,    # Annual 20% of license
        },
        'facilities': {
            'datacenter_space': 24000,  # Annual
            'power': 18000,              # Annual
            'cooling': 12000,            # Annual
        },
        'personnel': {
            'dba_count': 2,
            'dba_salary': 120000,  # Annual per DBA
            'admin_count': 1,
            'admin_salary': 90000,  # Annual
        },
        'other': {
            'backup': 15000,     # Annual
            'monitoring': 10000, # Annual
        }
    }

    total_tco = 0

    # Hardware (upfront + refresh)
    hardware_total = sum(costs['hardware'].values() - {'refresh_cycle'})
    refresh_cycles = years // costs['hardware']['refresh_cycle']
    total_tco += hardware_total * (refresh_cycles + 1)

    # Annual costs
    annual_costs = (
        costs['software']['licenses'] +
        costs['software']['support'] +
        costs['facilities']['datacenter_space'] +
        costs['facilities']['power'] +
        costs['facilities']['cooling'] +
        costs['personnel']['dba_count'] * costs['personnel']['dba_salary'] +
        costs['personnel']['admin_count'] * costs['personnel']['admin_salary'] +
        costs['other']['backup'] +
        costs['other']['monitoring']
    )

    total_tco += annual_costs * years

    return {
        'total_tco': total_tco,
        'annual_average': total_tco / years,
        'breakdown': {
            'hardware': hardware_total * (refresh_cycles + 1),
            'software': (costs['software']['licenses'] + costs['software']['support']) * years,
            'facilities': (costs['facilities']['datacenter_space'] +
                          costs['facilities']['power'] +
                          costs['facilities']['cooling']) * years,
            'personnel': (costs['personnel']['dba_count'] * costs['personnel']['dba_salary'] +
                         costs['personnel']['admin_count'] * costs['personnel']['admin_salary']) * years,
            'other': (costs['other']['backup'] + costs['other']['monitoring']) * years
        }
    }

def calculate_cloud_tco(platform='snowflake', years=3):
    """Calculate TCO for cloud DWH"""

    # Platform-specific pricing
    pricing = {
        'snowflake': {
            'compute_credits_per_hour': 4,  # X-Large warehouse
            'avg_hours_per_day': 8,
            'storage_per_tb_per_month': 40,
            'avg_storage_tb': 10,
        },
        'bigquery': {
            'queries_per_tb': 5,  # $5 per TB scanned
            'avg_tb_scanned_per_month': 50,
            'storage_per_tb_per_month': 20,
            'avg_storage_tb': 10,
        },
        'redshift': {
            'node_type': 'ra3.4xlarge',
            'node_price_per_hour': 3.26,
            'node_count': 4,
            'hours_per_month': 730,
            'storage_per_tb_per_month': 24,
            'avg_storage_tb': 10,
        },
        'synapse': {
            'dwu': 1000,  # DWU level
            'price_per_hour': 15,
            'avg_hours_per_day': 8,
            'storage_per_tb_per_month': 23,
            'avg_storage_tb': 10,
        }
    }

    config = pricing[platform]

    # Calculate monthly costs
    if platform == 'snowflake':
        monthly_compute = (config['compute_credits_per_hour'] *
                          config['avg_hours_per_day'] * 30 * 4)  # $4 per credit
        monthly_storage = config['storage_per_tb_per_month'] * config['avg_storage_tb']

    elif platform == 'bigquery':
        monthly_compute = config['queries_per_tb'] * config['avg_tb_scanned_per_month']
        monthly_storage = config['storage_per_tb_per_month'] * config['avg_storage_tb']

    elif platform == 'redshift':
        monthly_compute = (config['node_price_per_hour'] *
                          config['node_count'] *
                          config['hours_per_month'])
        monthly_storage = config['storage_per_tb_per_month'] * config['avg_storage_tb']

    elif platform == 'synapse':
        monthly_compute = config['price_per_hour'] * config['avg_hours_per_day'] * 30
        monthly_storage = config['storage_per_tb_per_month'] * config['avg_storage_tb']

    # Additional costs
    monthly_network = 500  # Data egress
    monthly_support = (monthly_compute + monthly_storage) * 0.10  # 10% of cloud costs

    # Personnel (reduced from on-prem)
    annual_personnel = 1 * 100000  # 1 cloud DBA

    total_monthly = monthly_compute + monthly_storage + monthly_network + monthly_support
    total_annual = (total_monthly * 12) + annual_personnel
    total_tco = total_annual * years

    return {
        'total_tco': total_tco,
        'annual_average': total_annual,
        'monthly_average': total_monthly,
        'breakdown': {
            'compute': monthly_compute * 12 * years,
            'storage': monthly_storage * 12 * years,
            'network': monthly_network * 12 * years,
            'support': monthly_support * 12 * years,
            'personnel': annual_personnel * years
        }
    }

# Example usage
legacy_tco = calculate_legacy_tco(years=3)
snowflake_tco = calculate_cloud_tco('snowflake', years=3)
bigquery_tco = calculate_cloud_tco('bigquery', years=3)

print(f"Legacy 3-Year TCO: ${legacy_tco['total_tco']:,.2f}")
print(f"Snowflake 3-Year TCO: ${snowflake_tco['total_tco']:,.2f}")
print(f"Savings: ${legacy_tco['total_tco'] - snowflake_tco['total_tco']:,.2f}")
print(f"ROI: {((legacy_tco['total_tco'] - snowflake_tco['total_tco']) / legacy_tco['total_tco'] * 100):.1f}%")
```

### 6.2 Cost Optimization Strategies

**Snowflake Cost Optimization:**

```sql
-- 1. Monitor credit usage
SELECT
    warehouse_name,
    SUM(credits_used) as total_credits,
    SUM(credits_used) * 4 as estimated_cost_usd  -- $4 per credit
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
ORDER BY total_credits DESC;

-- 2. Identify inefficient queries
SELECT
    query_id,
    user_name,
    warehouse_name,
    execution_time / 1000 as execution_sec,
    credits_used_cloud_services,
    bytes_scanned / POW(1024, 3) as gb_scanned
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND execution_time > 60000  -- > 1 minute
ORDER BY credits_used_cloud_services DESC
LIMIT 100;

-- 3. Auto-suspend and auto-resume
ALTER WAREHOUSE analytics_wh SET
    AUTO_SUSPEND = 60  -- 1 minute (reduce from 5 minutes)
    AUTO_RESUME = TRUE;

-- 4. Right-size warehouses
-- Start with smaller warehouse and scale up if needed
ALTER WAREHOUSE analytics_wh SET WAREHOUSE_SIZE = 'SMALL';

-- 5. Use clustering strategically (only for very large tables)
-- Clustering has ongoing cost, use only when beneficial
```

**BigQuery Cost Optimization:**

```sql
-- 1. Monitor query costs
SELECT
    user_email,
    DATE(creation_time) as query_date,
    SUM(total_bytes_billed) / POW(10, 12) as tb_billed,
    SUM(total_bytes_billed) / POW(10, 12) * 5 as estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    AND job_type = 'QUERY'
    AND state = 'DONE'
GROUP BY user_email, query_date
ORDER BY tb_billed DESC;

-- 2. Partition pruning
-- Before optimization
SELECT * FROM sales_fact
WHERE customer_id = 12345;  -- Scans entire table

-- After optimization
SELECT * FROM sales_fact
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'  -- Partition filter
    AND customer_id = 12345;  -- Reduces scan significantly

-- 3. Use materialized views for repeated aggregations
CREATE MATERIALIZED VIEW analytics.mv_daily_summary
AS
SELECT
    sale_date,
    product_category,
    SUM(amount) as total_sales,
    COUNT(*) as transaction_count
FROM analytics.sales_fact
GROUP BY sale_date, product_category;

-- Querying MV costs less than recomputing aggregation

-- 4. Set maximum bytes billed
-- Prevent runaway queries
SELECT * FROM sales_fact
WHERE ...
OPTIONS(maximum_bytes_billed=1000000000);  -- 1 GB limit
```

---

## Migration Checklists

### 7.1 Pre-Migration Checklist

```markdown
## Pre-Migration Readiness Checklist

### Assessment Phase
- [ ] Complete schema inventory (tables, views, procedures, functions)
- [ ] Document data volumes and growth rates
- [ ] Analyze query patterns and performance baselines
- [ ] Identify dependencies (applications, reports, integrations)
- [ ] Map data lineage
- [ ] Document current ETL jobs and schedules
- [ ] Capture current costs (TCO analysis)

### Platform Selection
- [ ] Define requirements (performance, scale, cost, features)
- [ ] Evaluate cloud platforms (POC if needed)
- [ ] Calculate projected cloud costs
- [ ] Review compliance and security requirements
- [ ] Select target platform
- [ ] Choose migration tools

### Planning
- [ ] Create migration project plan
- [ ] Define migration strategy (big bang, phased, strangler)
- [ ] Establish success criteria
- [ ] Build migration team
- [ ] Setup communication plan
- [ ] Define rollback procedures
- [ ] Schedule migration windows

### Technical Preparation
- [ ] Provision cloud environment (compute, storage, networking)
- [ ] Configure security (VPN, firewall rules, encryption)
- [ ] Setup user authentication (SSO, Active Directory integration)
- [ ] Establish data transfer mechanism (network link, Snowpipe, etc.)
- [ ] Create development and test environments
- [ ] Configure monitoring and alerting
- [ ] Setup backup and disaster recovery

### Team Readiness
- [ ] Complete cloud platform training
- [ ] Document migration procedures
- [ ] Conduct dry run migrations
- [ ] Establish support model
- [ ] Create runbooks for common issues
```

### 7.2 Migration Execution Checklist

```markdown
## Migration Execution Checklist

### T-1 Week
- [ ] Final communication to stakeholders
- [ ] Freeze schema changes in legacy system
- [ ] Backup legacy database
- [ ] Verify cloud environment readiness
- [ ] Test rollback procedures
- [ ] Confirm migration team availability

### T-1 Day
- [ ] Send reminder notifications
- [ ] Verify data transfer connectivity
- [ ] Pre-stage reference/dimension data
- [ ] Prepare monitoring dashboards
- [ ] Establish war room/bridge line

### Migration Day - Phase 1: Schema (Hour 0-2)
- [ ] Create target database and schemas
- [ ] Create all tables (DDL execution)
- [ ] Create indexes (non-unique first)
- [ ] Create views
- [ ] Setup table partitioning/clustering
- [ ] Validate schema structure

### Migration Day - Phase 2: Data Load (Hour 2-8)
- [ ] Load dimension tables
- [ ] Validate dimension data
- [ ] Load fact tables (historical data)
- [ ] Validate fact data (row counts, sums)
- [ ] Load staging/working tables
- [ ] Final validation queries

### Migration Day - Phase 3: Code Migration (Hour 8-12)
- [ ] Deploy stored procedures
- [ ] Deploy functions
- [ ] Deploy ETL jobs
- [ ] Test critical workflows
- [ ] Validate permissions

### Migration Day - Phase 4: Validation (Hour 12-16)
- [ ] Execute validation test suite
- [ ] Run sample queries and compare results
- [ ] Performance testing
- [ ] User acceptance testing
- [ ] Resolve any discrepancies

### Migration Day - Phase 5: Cutover (Hour 16-18)
- [ ] Switch connection strings in applications
- [ ] Redirect BI tools to new platform
- [ ] Update documentation
- [ ] Enable monitoring and alerts
- [ ] Final smoke tests

### Post-Migration - Day 1
- [ ] Monitor system performance
- [ ] Address user issues
- [ ] Validate overnight batch jobs
- [ ] Collect user feedback
- [ ] Review incident log

### Post-Migration - Week 1
- [ ] Daily health checks
- [ ] Performance optimization
- [ ] Cost monitoring
- [ ] User support (hypercare mode)
- [ ] Document lessons learned

### Post-Migration - Month 1
- [ ] Conduct post-migration review
- [ ] Finalize documentation
- [ ] Train additional users
- [ ] Optimize costs
- [ ] Plan legacy system decommissioning
```

### 7.3 Validation Checklist

```markdown
## Data Validation Checklist

### Level 1: Row Count Validation
- [ ] Compare row counts for all migrated tables
- [ ] Document any discrepancies
- [ ] Acceptable variance: 0%

### Level 2: Aggregate Validation
- [ ] Sum of numeric columns (amount, quantity, etc.)
- [ ] Count distinct values for key columns
- [ ] Min/Max values comparison
- [ ] Acceptable variance: < 0.01%

### Level 3: Sample Validation
- [ ] Random sample of 1000 records per table
- [ ] Row-by-row comparison
- [ ] Document data type conversions
- [ ] Acceptable mismatch: 0%

### Level 4: Query Result Validation
- [ ] Execute top 20 most-used queries on both platforms
- [ ] Compare result sets
- [ ] Document any differences in query syntax/performance
- [ ] Acceptable variance: < 0.01%

### Level 5: End-to-End Testing
- [ ] Run complete ETL workflow
- [ ] Generate standard reports
- [ ] Execute analytical queries
- [ ] Test data refresh processes
- [ ] Validate dashboard data

### Signoff
- [ ] Data Owner approval
- [ ] Technical Lead approval
- [ ] Business Stakeholder approval
```

---

## Appendix: Platform-Specific Migration Guides

### A.1 Oracle to Snowflake Quick Reference

**Key Differences:**
- No indexes (except unique constraints)
- Micro-partitions instead of manual partitioning
- VARIANT data type for JSON/semi-structured
- Time Travel for historical queries
- Zero-copy cloning

**Common Conversions:**
```sql
-- Oracle SEQUENCE → Snowflake IDENTITY
-- Oracle:
CREATE SEQUENCE customer_seq START WITH 1 INCREMENT BY 1;

-- Snowflake:
CREATE TABLE customer (
    customer_id NUMBER AUTOINCREMENT START 1 INCREMENT 1,
    ...
);

-- Oracle NVL → Snowflake COALESCE or NVL
-- Oracle:
SELECT NVL(commission_pct, 0) FROM employees;

-- Snowflake (both work):
SELECT NVL(commission_pct, 0) FROM employees;
SELECT COALESCE(commission_pct, 0) FROM employees;

-- Oracle ROWNUM → Snowflake ROW_NUMBER()
-- Oracle:
SELECT * FROM employees WHERE ROWNUM <= 10;

-- Snowflake:
SELECT * FROM employees LIMIT 10;
-- or
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY hire_date) as rn
    FROM employees
) WHERE rn <= 10;
```

### A.2 Teradata to BigQuery Quick Reference

**Key Differences:**
- Standard SQL syntax (less proprietary functions)
- Automatic partitioning and clustering
- Nested and repeated fields support
- Built-in ML capabilities
- Serverless architecture

**Common Conversions:**
```sql
-- Teradata QUALIFY → BigQuery window function in WHERE
-- Teradata:
SELECT employee_id, salary, dept_id
FROM employees
QUALIFY ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) = 1;

-- BigQuery:
SELECT employee_id, salary, dept_id
FROM (
    SELECT
        employee_id,
        salary,
        dept_id,
        ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) as rn
    FROM employees
)
WHERE rn = 1;

-- Teradata CAST with FORMAT → BigQuery FORMAT or PARSE
-- Teradata:
SELECT CAST(order_date AS VARCHAR(10) FORMAT 'YYYY-MM-DD')

-- BigQuery:
SELECT FORMAT_DATE('%Y-%m-%d', order_date)
```

### A.3 SQL Server to Redshift Quick Reference

**Key Differences:**
- No clustered indexes (use sort keys)
- Distribution keys for data distribution
- Column-oriented storage
- No stored procedure support (use Python UDFs)
- Limited T-SQL function support

**Common Conversions:**
```sql
-- SQL Server GETDATE() → Redshift GETDATE() or CURRENT_TIMESTAMP
SELECT GETDATE();  -- Works in both

-- SQL Server TOP → Redshift LIMIT
-- SQL Server:
SELECT TOP 10 * FROM employees ORDER BY hire_date;

-- Redshift:
SELECT * FROM employees ORDER BY hire_date LIMIT 10;

-- SQL Server TRY_CONVERT → Redshift custom handling
-- SQL Server:
SELECT TRY_CONVERT(INT, column_value) FROM table;

-- Redshift:
SELECT
    CASE
        WHEN column_value ~ '^[0-9]+$' THEN column_value::INT
        ELSE NULL
    END
FROM table;
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-19
**Maintained By:** Data Engineering Center of Excellence
**Review Cycle:** Quarterly
