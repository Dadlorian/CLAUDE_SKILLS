# Testing Strategies Guide

## Testing Pyramid

```
        ┌──────────┐
        │ Business │ Custom tests for business logic
        │  Logic   │
        ├──────────┤
        │  Data    │ Great Expectations, dbt tests
        │ Quality  │
        ├──────────┤
        │  Schema  │ unique, not_null, relationships
        └──────────┘
```

## 1. Schema Tests (Foundation)
```yaml
models:
  - name: dim_customers
    columns:
      - name: customer_key
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - unique
```

## 2. Data Quality Tests
```yaml
      - name: email
        tests:
          - dbt_expectations.expect_column_values_to_match_regex:
              regex: "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$"

      - name: lifetime_value
        tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
```

## 3. Business Logic Tests
```sql
-- tests/assert_revenue_matches.sql
SELECT
    order_date,
    reported_revenue,
    calculated_revenue,
    ABS(reported_revenue - calculated_revenue) as difference
FROM {{ ref('fct_sales_summary') }}
WHERE ABS(reported_revenue - calculated_revenue) > 0.01
```

## 4. Integration Tests
```python
# tests/test_pipeline.py
def test_end_to_end_pipeline():
    # Run extraction
    airbyte.sync('connection_id')

    # Run dbt
    dbt.run()

    # Validate results
    result = db.query("SELECT COUNT(*) FROM dim_customers")
    assert result > 0
```

## Test Execution Strategies

### Development
```bash
# Test specific model
dbt test --models dim_customers

# Test modified models
dbt test --models state:modified+
```

### CI/CD
```bash
# Slim CI
dbt test --models state:modified+ --defer
```

### Production
```bash
# Full test suite
dbt test

# Alert on failures
dbt test || send_alert "Tests failed"
```

## Best Practices

1. **Test Early**: Add tests with models
2. **Layer Tests**: Test at each transformation layer
3. **Set Severity**: warn vs error
4. **Monitor Pass Rates**: Track over time
5. **Document Tests**: Explain what they validate

