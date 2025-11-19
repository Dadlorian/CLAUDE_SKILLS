# dbt Fundamentals: Complete Guide

## Introduction to dbt

dbt (data build tool) transforms data in your warehouse using SQL SELECT statements. It enables analytics engineers to work like software engineers with version control, testing, and documentation.

### Why dbt?

**Traditional ETL Problems:**
- SQL scattered across tools
- No version control
- Manual testing
- Unclear data lineage
- No collaboration

**dbt Solutions:**
- All transformations in SQL
- Git-based workflow
- Automated testing
- Auto-generated documentation
- Team collaboration

## Project Structure

### Anatomy of a dbt Project
```
my_dbt_project/
├── dbt_project.yml          # Project configuration
├── packages.yml             # Dependencies
├── profiles.yml             # Connection configs (gitignored)
├── models/                  # SQL transformations
│   ├── staging/            # 1:1 with source tables
│   │   ├── _staging.yml    # Source definitions
│   │   ├── stg_customers.sql
│   │   └── stg_orders.sql
│   ├── intermediate/       # Reusable components
│   │   └── int_customer_orders.sql
│   └── marts/             # Business-facing models
│       ├── core/          # Shared
│       ├── marketing/     # Domain-specific
│       └── finance/
├── macros/                # Reusable SQL snippets
│   └── cents_to_dollars.sql
├── tests/                 # Custom data tests
│   └── assert_positive_amounts.sql
├── snapshots/            # SCD Type 2 tracking
│   └── customers_snapshot.sql
├── analyses/             # Ad-hoc queries
│   └── revenue_analysis.sql
├── seeds/                # Static lookup data
│   └── country_codes.csv
└── target/               # Compiled SQL (gitignored)
```

## Getting Started

### Installation
```bash
# Install dbt for your warehouse
pip install dbt-snowflake  # or dbt-bigquery, dbt-postgres, dbt-redshift

# Verify installation
dbt --version
```

### Initialize Project
```bash
# Create new project
dbt init my_project

# Navigate to project
cd my_project

# Project structure created automatically
```

### Configure Connection
```yaml
# profiles.yml (in ~/.dbt/ or project root)
my_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: xy12345.us-east-1
      user: dbt_user
      password: "{{ env_var('DBT_PASSWORD') }}"
      role: TRANSFORMER
      database: DEV_DB
      warehouse: TRANSFORM_WH
      schema: dbt_{{ env_var('USER') }}  # Personal schema
      threads: 4
      client_session_keep_alive: False

    prod:
      type: snowflake
      account: xy12345.us-east-1
      user: dbt_user_prod
      password: "{{ env_var('DBT_PROD_PASSWORD') }}"
      role: TRANSFORMER
      database: PROD_DB
      warehouse: TRANSFORM_WH
      schema: analytics
      threads: 16
      client_session_keep_alive: False
```

### Test Connection
```bash
dbt debug

# Should see:
# Connection test: OK
# All checks passed!
```

## Building Your First Model

### Define Sources
```yaml
# models/staging/_sources.yml
version: 2

sources:
  - name: postgres
    description: Production PostgreSQL database
    database: raw_data
    schema: public

    tables:
      - name: customers
        description: Customer records from application database
        loaded_at_field: _loaded_at
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}
        columns:
          - name: id
            description: Primary key
            tests:
              - unique
              - not_null

      - name: orders
        description: Order records
        columns:
          - name: id
            tests:
              - unique
              - not_null
          - name: customer_id
            tests:
              - not_null
              - relationships:
                  to: source('postgres', 'customers')
                  field: id
```

### Create Staging Model
```sql
-- models/staging/stg_customers.sql
{{
    config(
        materialized='view',
        tags=['staging', 'daily']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('postgres', 'customers') }}
),

renamed AS (
    SELECT
        -- IDs
        id AS customer_id,

        -- Attributes
        first_name,
        last_name,
        email,
        phone,

        -- Metadata
        created_at,
        updated_at,
        _loaded_at

    FROM source
)

SELECT * FROM renamed
```

### Create Business Model
```sql
-- models/marts/core/dim_customers.sql
{{
    config(
        materialized='table',
        tags=['core', 'daily']
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) AS lifetime_orders,
        SUM(order_total) AS lifetime_value,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date
    FROM orders
    GROUP BY customer_id
)

SELECT
    customers.customer_id,
    customers.first_name,
    customers.last_name,
    customers.email,

    -- Order metrics
    COALESCE(customer_orders.lifetime_orders, 0) AS lifetime_orders,
    COALESCE(customer_orders.lifetime_value, 0) AS lifetime_value,
    customer_orders.first_order_date,
    customer_orders.last_order_date,

    -- Computed fields
    customers.first_name || ' ' || customers.last_name AS full_name,
    CASE
        WHEN customer_orders.lifetime_orders > 10 THEN 'VIP'
        WHEN customer_orders.lifetime_orders > 5 THEN 'Regular'
        ELSE 'Casual'
    END AS customer_segment,

    -- Metadata
    customers.created_at,
    CURRENT_TIMESTAMP AS dbt_updated_at

FROM customers
LEFT JOIN customer_orders USING (customer_id)
```

### Run Models
```bash
# Run all models
dbt run

# Run specific model
dbt run --models dim_customers

# Run model and all upstream dependencies
dbt run --models +dim_customers

# Run model and all downstream dependencies
dbt run --models dim_customers+
```

## Materializations

### View (Default)
```sql
{{ config(materialized='view') }}

-- Creates a database view
-- Pros: Always fresh, no storage
-- Cons: Query time on read, no optimization
-- Use for: Simple transformations, low query volume
```

### Table
```sql
{{ config(materialized='table') }}

-- Creates a physical table
-- Pros: Fast queries, can be indexed
-- Cons: Takes time to build, storage cost
-- Use for: Complex transformations, high query volume
```

### Incremental
```sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        on_schema_change='sync_all_columns'
    )
}}

SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    updated_at
FROM {{ source('postgres', 'orders') }}

{% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}

-- Pros: Fast runs, processes only changed data
-- Cons: More complex, requires unique_key
-- Use for: Large tables with frequent updates
```

### Ephemeral
```sql
{{ config(materialized='ephemeral') }}

-- Not materialized, compiled as CTE
-- Pros: No storage, reusable logic
-- Cons: Recalculated every time
-- Use for: Intermediate logic, CTEs
```

## Testing

### Schema Tests
```yaml
# models/schema.yml
version: 2

models:
  - name: dim_customers
    description: Customer dimension table
    columns:
      - name: customer_id
        description: Primary key
        tests:
          - unique
          - not_null

      - name: email
        tests:
          - unique

      - name: lifetime_value
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              inclusive: true

      - name: customer_segment
        tests:
          - accepted_values:
              values: ['VIP', 'Regular', 'Casual']
```

### Data Tests
```sql
-- tests/assert_customer_lifetime_value_positive.sql
-- Returns records that fail the test

SELECT
    customer_id,
    lifetime_value
FROM {{ ref('dim_customers') }}
WHERE lifetime_value < 0
```

### Run Tests
```bash
# Test all models
dbt test

# Test specific model
dbt test --models dim_customers

# Test sources
dbt test --models source:*
```

## Documentation

### Add Descriptions
```yaml
# models/schema.yml
version: 2

models:
  - name: dim_customers
    description: |
      Customer dimension table containing all customer attributes
      and aggregated order metrics. Updated daily.

    columns:
      - name: customer_id
        description: Unique identifier for each customer (PK)

      - name: lifetime_value
        description: Total revenue from customer across all orders
```

### Generate Docs
```bash
# Generate documentation
dbt docs generate

# Serve documentation site
dbt docs serve

# Opens http://localhost:8080
# Shows:
# - Model lineage (DAG)
# - Column descriptions
# - Tests
# - Source freshness
```

## Advanced Features

### Macros
```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name, precision=2) %}
    ROUND({{ column_name }} / 100.0, {{ precision }})
{% endmacro %}

-- Use in model
SELECT
    order_id,
    {{ cents_to_dollars('amount_cents') }} AS amount_dollars
FROM {{ ref('stg_orders') }}
```

### Snapshots (SCD Type 2)
```sql
-- snapshots/customers_snapshot.sql
{% snapshot customers_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

SELECT * FROM {{ source('postgres', 'customers') }}

{% endsnapshot %}
```

Run snapshots:
```bash
dbt snapshot

# Creates table with:
# - dbt_valid_from
# - dbt_valid_to
# - dbt_scd_id
```

### Seeds (Static Data)
```csv
<!-- seeds/country_codes.csv -->
country_code,country_name,region
US,United States,North America
UK,United Kingdom,Europe
CA,Canada,North America
```

```bash
# Load seeds
dbt seed

# Reference in models
SELECT
    o.*,
    c.country_name
FROM {{ ref('orders') }} o
LEFT JOIN {{ ref('country_codes') }} c
    ON o.country_code = c.country_code
```

### Packages
```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1

  - package: calogica/dbt_expectations
    version: 0.10.0
```

```bash
# Install packages
dbt deps

# Use package macros
SELECT {{ dbt_utils.surrogate_key(['customer_id', 'order_date']) }} AS key
```

## Project Organization Best Practices

### Layer Structure
```
models/
├── staging/           # 1:1 with sources, light transformations
│   ├── crm/          # Grouped by source
│   ├── ecommerce/
│   └── marketing/
├── intermediate/      # Reusable components, not exposed
│   ├── int_customer_orders.sql
│   └── int_daily_metrics.sql
└── marts/            # Business-facing, exposed to BI tools
    ├── core/         # Cross-functional (customers, orders, products)
    ├── marketing/    # Marketing-specific
    ├── finance/      # Finance-specific
    └── sales/        # Sales-specific
```

### Naming Conventions
```sql
-- Staging models: stg_{source}_{table}
stg_shopify_orders.sql
stg_postgres_customers.sql

-- Intermediate models: int_{description}
int_customer_daily_orders.sql
int_product_margins.sql

-- Fact tables: fct_{description}
fct_orders.sql
fct_sessions.sql

-- Dimension tables: dim_{description}
dim_customers.sql
dim_products.sql
```

### Config Inheritance
```yaml
# dbt_project.yml
models:
  my_project:
    # Default for all models
    +materialized: view

    staging:
      # All staging models
      +materialized: view
      +tags: ["staging"]
      +schema: staging

    intermediate:
      +materialized: ephemeral
      +tags: ["intermediate"]

    marts:
      # All marts models
      +materialized: table
      +tags: ["marts"]

      core:
        +schema: core
      marketing:
        +schema: marketing
```

## Development Workflow

### 1. Create Branch
```bash
git checkout -b feature/customer-segmentation
```

### 2. Develop Model
```bash
# Run in development
dbt run --models +dim_customers --target dev

# Test
dbt test --models dim_customers
```

### 3. Review Compiled SQL
```bash
# View generated SQL
cat target/compiled/my_project/models/marts/core/dim_customers.sql
```

### 4. Commit & Push
```bash
git add models/marts/core/dim_customers.sql
git commit -m "feat: add customer segmentation to dim_customers"
git push origin feature/customer-segmentation
```

### 5. CI/CD
```yaml
# .github/workflows/dbt_ci.yml
name: dbt CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install dbt
        run: pip install dbt-snowflake

      - name: Run dbt deps
        run: dbt deps

      - name: Run dbt run (modified models)
        run: dbt run --models state:modified+ --state ./prod-artifacts

      - name: Run dbt test
        run: dbt test
```

## Common Patterns

### Date Spine
```sql
-- models/utils/date_spine.sql
{{ dbt_utils.date_spine(
    datepart="day",
    start_date="cast('2020-01-01' as date)",
    end_date="current_date()"
) }}
```

### Surrogate Keys
```sql
SELECT
    {{ dbt_utils.generate_surrogate_key(['customer_id', 'order_date']) }} AS daily_key,
    customer_id,
    order_date,
    SUM(amount) AS total_amount
FROM {{ ref('orders') }}
GROUP BY customer_id, order_date
```

### Union Tables
```sql
{{ dbt_utils.union_relations(
    relations=[
        ref('orders_2022'),
        ref('orders_2023'),
        ref('orders_2024')
    ]
) }}
```

## Troubleshooting

### Issue: Model Not Found
```
Compilation Error in model dim_customers
  Model 'stg_customers' not found
```
**Solution**: Check spelling, ensure `ref()` is used, run `dbt compile`

### Issue: Circular Dependency
```
Found a cycle in the dependency graph
```
**Solution**: Review model dependencies, remove circular references

### Issue: Column Not Found
```
Database Error in model dim_customers
  column "customer_id" does not exist
```
**Solution**: Check column names in source, verify schema hasn't changed

## Next Steps

1. **Learn Incremental Models**: [incremental_models_guide.md](./incremental_models_guide.md)
2. **Master Testing**: [data_quality_testing_guide.md](./data_quality_testing_guide.md)
3. **CI/CD Setup**: [cicd_for_dbt_guide.md](./cicd_for_dbt_guide.md)
4. **Production Deployment**: [production_deployment_guide.md](./production_deployment_guide.md)

## Resources

- **Official Docs**: https://docs.getdbt.com
- **Best Practices**: https://docs.getdbt.com/guides/best-practices
- **dbt Slack**: https://getdbt.slack.com
- **dbt Learn**: https://courses.getdbt.com
