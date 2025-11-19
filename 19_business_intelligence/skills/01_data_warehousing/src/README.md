# Data Warehousing Source Code

Production-ready SQL scripts, DDL, and code examples for data warehouse implementation.

## Directory Contents

### DDL (Data Definition Language)
- Star schema DDL for Snowflake, BigQuery, Redshift
- Snowflake schema examples
- Data Vault 2.0 DDL (Hubs, Links, Satellites)
- Dimension and fact table templates

### DML (Data Manipulation Language)
- SCD Type 1, 2, 3, 6 implementations
- MERGE/UPSERT patterns
- Incremental loading logic
- Data quality check queries

### Platform-Specific Examples
- Snowflake: Tasks, Streams, Time Travel
- BigQuery: Partitioned tables, Materialized views
- Redshift: Distribution keys, Sort keys

### dbt Models
- Staging layer models
- Intermediate transformations
- Fact and dimension models
- Incremental models
- Snapshot configurations

### Utility Scripts
- Date dimension generator
- Surrogate key generation
- Hash key generation (for Data Vault)
- Data profiling queries
- Performance monitoring queries

## File Naming Convention

```
<platform>_<object_type>_<description>.sql

Examples:
snowflake_ddl_star_schema.sql
bigquery_dml_scd_type2.sql
dbt_model_fct_orders.sql
```

## Usage

All scripts are:
- **Production-tested**: Used in real implementations
- **Well-commented**: Inline documentation
- **Configurable**: Easy to adapt to your needs
- **Platform-specific**: Optimized for target platform
