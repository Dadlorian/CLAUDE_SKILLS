# ELT Best Practices Guide

## Architecture Principles

### 1. ELT Over ETL
Extract → Load → Transform (in warehouse) vs Extract → Transform → Load
- Leverage warehouse compute power
- Separate storage from compute
- SQL-based transformations
- Better collaboration

### 2. Medallion Architecture
**Bronze (Raw)**: Exactly as extracted
**Silver (Cleaned)**: Deduplicated, typed, conformed
**Gold (Business)**: Business logic, aggregations, denormalized

### 3. Modular Design
- Single Responsibility: Each model does one thing
- DRY: Don't Repeat Yourself
- Reusable components in intermediate layer
- Clear dependencies

## dbt Project Structure

```
models/
├── staging/          # 1:1 with sources
│   ├── _sources.yml
│   ├── stg_customers.sql
│   └── stg_orders.sql
├── intermediate/     # Reusable logic
│   ├── int_customer_orders.sql
│   └── int_order_metrics.sql
└── marts/           # Business-facing
    ├── core/
    ├── marketing/
    └── finance/
```

## Best Practices

### 1. Naming Conventions
- `stg_` for staging models
- `int_` for intermediate models
- `fct_` for fact tables
- `dim_` for dimensions

### 2. Configuration Management
```yaml
# dbt_project.yml
models:
  my_project:
    staging:
      +materialized: view
      +schema: staging
    marts:
      +materialized: table
      +schema: analytics
```

### 3. Testing Strategy
- Test at every layer
- Schema tests for all primary keys
- Relationships between fact and dimensions
- Custom business logic tests

### 4. Documentation
- Describe all models and columns
- Use dbt docs generate
- Keep docs in version control

### 5. Performance Optimization
- Use incremental models for large tables
- Partition by date where possible
- Cluster on frequently filtered columns
- Monitor query costs

## Resources

- **dbt Best Practices**: https://docs.getdbt.com/guides/best-practices
