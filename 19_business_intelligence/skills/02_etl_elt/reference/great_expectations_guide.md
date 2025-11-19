# Great Expectations Reference Guide

## Overview
Great Expectations is a Python-based data validation framework that helps teams maintain data quality through automated testing and documentation.

## Core Concepts

### Expectations
Assertions about your data.

```python
# Expect column to exist
validator.expect_column_to_exist(column="customer_id")

# Expect no nulls
validator.expect_column_values_to_not_be_null(column="order_id")

# Expect unique values
validator.expect_column_values_to_be_unique(column="email")

# Expect values in set
validator.expect_column_values_to_be_in_set(
    column="status",
    value_set=["pending", "processing", "completed", "cancelled"]
)

# Expect range
validator.expect_column_values_to_be_between(
    column="amount",
    min_value=0,
    max_value=1000000
)
```

### Expectation Suites
Collections of expectations for a dataset.

```python
import great_expectations as gx

# Initialize context
context = gx.get_context()

# Create expectation suite
suite = context.create_expectation_suite(
    expectation_suite_name="orders_suite",
    overwrite_existing=True
)
```

### Checkpoints
Configurations for validation runs.

```yaml
# checkpoints/orders_checkpoint.yml
name: orders_checkpoint
config_version: 1.0
class_name: SimpleCheckpoint

validations:
  - batch_request:
      datasource_name: postgres_datasource
      data_connector_name: default_inferred_data_connector
      data_asset_name: orders
    expectation_suite_name: orders_suite

action_list:
  - name: store_validation_result
    action:
      class_name: StoreValidationResultAction

  - name: update_data_docs
    action:
      class_name: UpdateDataDocsAction
```

## Common Expectations

### Completeness Checks
```python
# No null values
validator.expect_column_values_to_not_be_null(column="customer_id")

# At least X% non-null
validator.expect_column_values_to_not_be_null(
    column="email",
    mostly=0.95  # 95% must be non-null
)

# All columns present
validator.expect_table_columns_to_match_ordered_list(
    column_list=["id", "customer_id", "amount", "created_at"]
)
```

### Uniqueness Checks
```python
# Unique column
validator.expect_column_values_to_be_unique(column="order_id")

# Compound uniqueness
validator.expect_compound_columns_to_be_unique(
    column_list=["customer_id", "order_date", "product_id"]
)

# Unique value proportion
validator.expect_column_proportion_of_unique_values_to_be_between(
    column="customer_id",
    min_value=0.95,
    max_value=1.0
)
```

### Type & Format Checks
```python
# Data type
validator.expect_column_values_to_be_of_type(
    column="amount",
    type_="DECIMAL"
)

# Match regex
validator.expect_column_values_to_match_regex(
    column="email",
    regex="^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

# Match strftime format
validator.expect_column_values_to_match_strftime_format(
    column="order_date",
    strftime_format="%Y-%m-%d"
)

# JSON schema
validator.expect_column_values_to_match_json_schema(
    column="metadata",
    json_schema={
        "type": "object",
        "properties": {
            "user_id": {"type": "integer"},
            "session_id": {"type": "string"}
        }
    }
)
```

### Range & Distribution Checks
```python
# Value range
validator.expect_column_values_to_be_between(
    column="age",
    min_value=0,
    max_value=120
)

# Min/max
validator.expect_column_min_to_be_between(column="price", min_value=0)
validator.expect_column_max_to_be_between(column="quantity", max_value=1000)

# Mean
validator.expect_column_mean_to_be_between(
    column="order_amount",
    min_value=50,
    max_value=200
)

# Standard deviation
validator.expect_column_stdev_to_be_between(
    column="response_time_ms",
    min_value=0,
    max_value=100
)

# Quantiles
validator.expect_column_quantile_values_to_be_between(
    column="revenue",
    quantile_ranges={
        "quantiles": [0.25, 0.5, 0.75],
        "value_ranges": [[100, 200], [200, 300], [300, 400]]
    }
)
```

### Relationship Checks
```python
# Column pair equality
validator.expect_column_pair_values_to_be_equal(
    column_A="calculated_total",
    column_B="order_total"
)

# Column A greater than B
validator.expect_column_pair_values_A_to_be_greater_than_B(
    column_A="ship_date",
    column_B="order_date"
)

# Foreign key relationship (via SQL)
validator.expect_column_values_to_be_in_set(
    column="customer_id",
    value_set=list(customer_ids)  # From customers table
)
```

### Table-Level Checks
```python
# Row count
validator.expect_table_row_count_to_be_between(
    min_value=1000,
    max_value=100000
)

# Row count equals
validator.expect_table_row_count_to_equal(value=5000)

# Column count
validator.expect_table_column_count_to_equal(value=10)

# Column names
validator.expect_table_columns_to_match_set(
    column_set=["id", "name", "email", "created_at"]
)
```

## Setup & Configuration

### Initialize Project
```bash
# Install Great Expectations
pip install great_expectations

# Initialize GE project
great_expectations init

# Project structure created:
# great_expectations/
#   ├── great_expectations.yml
#   ├── expectations/
#   ├── checkpoints/
#   ├── plugins/
#   └── uncommitted/
```

### Configure Data Source
```python
# Python API
import great_expectations as gx

context = gx.get_context()

# PostgreSQL datasource
datasource_config = {
    "name": "postgres_datasource",
    "class_name": "Datasource",
    "execution_engine": {
        "class_name": "SqlAlchemyExecutionEngine",
        "connection_string": "postgresql://user:password@localhost/db"
    },
    "data_connectors": {
        "default_inferred_data_connector": {
            "class_name": "InferredAssetSqlDataConnector",
            "include_schema_name": True
        }
    }
}

context.add_datasource(**datasource_config)
```

### Create Expectation Suite
```python
# Interactive mode
context.create_expectation_suite(
    expectation_suite_name="orders_suite",
    overwrite_existing=True
)

# Get validator
batch_request = {
    "datasource_name": "postgres_datasource",
    "data_connector_name": "default_inferred_data_connector",
    "data_asset_name": "orders"
}

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="orders_suite"
)

# Add expectations
validator.expect_column_values_to_not_be_null(column="order_id")
validator.expect_column_values_to_be_unique(column="order_id")

# Save suite
validator.save_expectation_suite(discard_failed_expectations=False)
```

## Running Validations

### Via Checkpoint
```python
# Run checkpoint
result = context.run_checkpoint(checkpoint_name="orders_checkpoint")

# Check success
if result["success"]:
    print("All validations passed!")
else:
    print("Some validations failed")
    for run_result in result["run_results"].values():
        for validation_result in run_result["validation_result"]["results"]:
            if not validation_result["success"]:
                print(f"Failed: {validation_result['expectation_config']['expectation_type']}")
```

### Programmatic Validation
```python
# Validate batch
batch_request = {
    "datasource_name": "postgres_datasource",
    "data_connector_name": "default_inferred_data_connector",
    "data_asset_name": "orders",
    "batch_spec_passthrough": {
        "sampling_method": "_sample_using_limit",
        "sampling_kwargs": {"n": 10000}  # Validate sample
    }
}

validation_result = context.run_validation_operator(
    "action_list_operator",
    assets_to_validate=[batch_request],
    run_id="manual_validation_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)
```

## Airflow Integration

### GE Operator
```python
from airflow import DAG
from airflow.providers.great_expectations.operators.great_expectations import GreatExpectationsOperator

with DAG('data_quality_pipeline', ...) as dag:

    # Load data
    load_task = PythonOperator(...)

    # Validate with GE
    validate_orders = GreatExpectationsOperator(
        task_id='validate_orders',
        data_context_root_dir='/path/to/great_expectations',
        checkpoint_name='orders_checkpoint',
        return_json_dict=True
    )

    # Continue pipeline only if validation passes
    transform_task = PythonOperator(...)

    load_task >> validate_orders >> transform_task
```

### Custom Validation Task
```python
def run_great_expectations_validation(**context):
    """Run GE validation in Airflow task"""
    import great_expectations as gx

    ge_context = gx.get_context()

    # Run checkpoint
    result = ge_context.run_checkpoint(
        checkpoint_name="orders_checkpoint",
        run_name=f"airflow_{context['execution_date']}"
    )

    # Fail task if validation fails
    if not result["success"]:
        failed_expectations = []
        for run_result in result["run_results"].values():
            for validation in run_result["validation_result"]["results"]:
                if not validation["success"]:
                    failed_expectations.append(
                        validation["expectation_config"]["expectation_type"]
                    )

        raise ValueError(f"Data quality checks failed: {failed_expectations}")

    return result

validate_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=run_great_expectations_validation,
    dag=dag
)
```

## dbt Integration

### dbt Test from GE Expectations
```yaml
# dbt_project.yml
tests:
  great_expectations:
    # Configure GE integration
    enabled: true
```

```python
# Generate dbt tests from GE expectations
from great_expectations.core.batch import RuntimeBatchRequest

# Convert GE expectations to dbt tests
# (Requires custom integration or dbt-expectations package)
```

### dbt-expectations Package
```yaml
# Use GE-inspired tests in dbt
# packages.yml
packages:
  - package: calogica/dbt_expectations
    version: 0.10.0

# models/schema.yml
version: 2
models:
  - name: orders
    tests:
      - dbt_expectations.expect_table_row_count_to_be_between:
          min_value: 1000
          max_value: 100000

    columns:
      - name: order_id
        tests:
          - dbt_expectations.expect_column_values_to_not_be_null
          - dbt_expectations.expect_column_values_to_be_unique

      - name: amount
        tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 1000000
```

## Data Docs

### Generate Documentation
```bash
# Generate data docs
great_expectations docs build

# Open in browser
great_expectations docs open
```

### Custom Data Docs Site
```yaml
# great_expectations.yml
data_docs_sites:
  local_site:
    class_name: SiteBuilder
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: uncommitted/data_docs/local_site/

  s3_site:
    class_name: SiteBuilder
    store_backend:
      class_name: TupleS3StoreBackend
      bucket: my-data-docs-bucket
      prefix: great_expectations/
```

## Advanced Patterns

### Custom Expectations
```python
from great_expectations.expectations.expectation import ColumnExpectation

class ExpectColumnValuesToBeValidPhoneNumber(ColumnExpectation):
    """Expect column values to be valid phone numbers"""

    metric_dependencies = ("column_values.match_regex",)
    success_keys = ("mostly",)

    default_kwarg_values = {
        "regex": r"^\+?[1-9]\d{1,14}$",  # E.164 format
        "mostly": 1.0,
        "result_format": "BASIC"
    }

    def validate_configuration(self, configuration):
        super().validate_configuration(configuration)

# Use custom expectation
validator.expect_column_values_to_be_valid_phone_number(
    column="phone",
    mostly=0.95
)
```

### Profiling Data
```python
# Auto-generate expectations from data
from great_expectations.profile.user_configurable_profiler import (
    UserConfigurableProfiler
)

profiler = UserConfigurableProfiler(
    profile_dataset=validator,
    excluded_expectations=["expect_column_values_to_be_in_set"],
    not_null_only=False,
    value_set_threshold="MANY"
)

suite = profiler.build_suite()
```

### Anomaly Detection
```python
# Statistical anomaly detection
validator.expect_column_values_to_be_between(
    column="daily_revenue",
    min_value=mean - (3 * std_dev),  # 3 sigma
    max_value=mean + (3 * std_dev)
)

# Compare to historical baseline
validator.expect_column_mean_to_be_between(
    column="order_count",
    min_value=historical_mean * 0.8,  # 20% tolerance
    max_value=historical_mean * 1.2
)
```

## Best Practices

1. **Start Simple** - Begin with basic expectations (not null, unique)
2. **Incremental Addition** - Add expectations as you learn data
3. **Use mostly Parameter** - Allow for acceptable error rates
4. **Profile First** - Use profiler to discover data characteristics
5. **Version Control** - Commit expectation suites to git
6. **CI/CD Integration** - Run validations in pipelines
7. **Document Context** - Add notes to expectations
8. **Monitor Trends** - Track expectation pass rates over time

## Troubleshooting

### Common Issues

```python
# Handle failed expectations gracefully
result = validator.expect_column_values_to_not_be_null(column="email")
if not result["success"]:
    print(f"Found {result['result']['unexpected_count']} null values")
    # Log or alert, but don't fail pipeline

# Sample large datasets
batch_request = {
    "datasource_name": "postgres_datasource",
    "data_connector_name": "default_inferred_data_connector",
    "data_asset_name": "large_table",
    "batch_spec_passthrough": {
        "sampling_method": "_sample_using_limit",
        "sampling_kwargs": {"n": 10000}
    }
}
```

## Resources

- **Great Expectations Docs**: https://docs.greatexpectations.io/
- **Expectation Gallery**: https://greatexpectations.io/expectations/
- **Community Slack**: https://greatexpectations.io/slack
- **GitHub**: https://github.com/great-expectations/great_expectations
