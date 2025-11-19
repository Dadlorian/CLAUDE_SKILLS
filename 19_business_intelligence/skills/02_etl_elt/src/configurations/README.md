# ETL/ELT Source Code

## Directory Structure

```
src/
├── dbt_project/          # dbt transformation project
│   ├── models/
│   │   ├── staging/     # 1:1 with source tables
│   │   ├── intermediate/ # Reusable components
│   │   └── marts/       # Business-facing models
│   ├── macros/          # Reusable SQL functions
│   ├── tests/           # Custom data tests
│   ├── snapshots/       # SCD Type 2 tracking
│   └── seeds/           # Static reference data
├── airflow_dags/        # Orchestration workflows
├── configurations/      # Tool configurations
└── scripts/             # Python utilities
```

## Usage

### dbt
```bash
# Install dependencies
cd dbt_project && dbt deps

# Run transformations
dbt run --target prod

# Test data quality
dbt test

# Generate documentation
dbt docs generate && dbt docs serve
```

### Airflow
```bash
# Copy DAGs to Airflow
cp airflow_dags/* $AIRFLOW_HOME/dags/

# Test DAG
airflow dags test daily_etl_pipeline 2024-01-15
```

### Scripts
```bash
# Run data quality checks
python scripts/data_quality_check.py

# Run reconciliation
python scripts/reconciliation_check.py

# Monitor pipeline
python scripts/monitor_pipeline.py
```

## Configuration

Set environment variables:
```bash
export SNOWFLAKE_ACCOUNT=xy12345
export SNOWFLAKE_USER=etl_user
export SNOWFLAKE_PASSWORD=secure_password
export POSTGRES_PASSWORD=secure_password
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

## Production Deployment

1. **Test in Dev**: Run all models and tests
2. **CI/CD**: Automated testing on PRs
3. **Deploy to Prod**: Merge to main branch
4. **Monitor**: Track success rates and performance

## Resources

- dbt Docs: https://docs.getdbt.com
- Airflow Docs: https://airflow.apache.org
- Great Expectations: https://docs.greatexpectations.io
