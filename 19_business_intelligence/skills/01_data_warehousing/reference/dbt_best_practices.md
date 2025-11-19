# dbt (data build tool) Best Practices

Quick reference for dbt development best practices, project structure, and advanced patterns for data transformation.

## Project Structure

```
dbt_project/
├── dbt_project.yml          # Project configuration
├── packages.yml             # Package dependencies
├── profiles.yml             # Connection profiles (not in git)
├── models/
│   ├── staging/            # Raw data cleaning
│   │   ├── _staging.yml
│   │   ├── stg_customers.sql
│   │   └── stg_orders.sql
│   ├── intermediate/       # Business logic transformations
│   │   ├── _intermediate.yml
│   │   └── int_customer_orders.sql
│   ├── marts/              # Final business-ready models
│   │   ├── core/
│   │   │   ├── _core.yml
│   │   │   ├── fct_orders.sql
│   │   │   └── dim_customers.sql
│   │   └── marketing/
│   │       ├── _marketing.yml
│   │       └── customer_ltv.sql
├── macros/                  # Reusable SQL functions
│   ├── generate_schema_name.sql
│   └── cents_to_dollars.sql
├── tests/                   # Custom tests
│   └── assert_positive_total.sql
├── seeds/                   # CSV reference data
│   └── country_codes.csv
├── snapshots/              # SCD Type 2 tracking
│   └── snap_customers.sql
└── analyses/               # Ad-hoc queries
    └── customer_analysis.sql
```

## Model Organization

### Layering Strategy

**Staging Layer** (`stg_*`):
```sql
-- models/staging/ecommerce/stg_orders.sql
{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select * from {{ source('ecommerce', 'raw_orders') }}
),

renamed as (
    select
        order_id,
        customer_id,
        order_date,
        status,
        -- Clean and standardize
        lower(trim(status)) as order_status,
        round(amount_cents / 100.0, 2) as amount_dollars,
        created_at as _created_at,
        updated_at as _updated_at
    from source
)

select * from renamed
```

**Intermediate Layer** (`int_*`):
```sql
-- models/intermediate/int_customer_orders.sql
{{
    config(
        materialized='ephemeral'  -- Not materialized, used as CTE
    )
}}

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

joined as (
    select
        customers.customer_id,
        customers.customer_name,
        customers.customer_email,
        orders.order_id,
        orders.order_date,
        orders.amount_dollars,
        orders.order_status
    from customers
    left join orders
        on customers.customer_id = orders.customer_id
)

select * from joined
```

**Marts Layer** (`fct_*`, `dim_*`):
```sql
-- models/marts/core/fct_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        partition_by={
            'field': 'order_date',
            'data_type': 'date'
        },
        cluster_by=['customer_id']
    )
}}

with orders as (
    select * from {{ ref('int_customer_orders') }}
),

final as (
    select
        order_id,
        customer_id,
        order_date,
        order_status,
        amount_dollars,
        current_timestamp() as _updated_at
    from orders
    {% if is_incremental() %}
        where order_date > (select max(order_date) from {{ this }})
    {% endif %}
)

select * from final
```

## Materialization Strategies

### View
```sql
-- Fast to build, always fresh
-- Use for: Lightweight transformations, non-queried tables
{{ config(materialized='view') }}

select * from {{ ref('source_table') }}
```

### Table
```sql
-- Slower to build, fast to query
-- Use for: Final marts, heavily queried models
{{ config(materialized='table') }}

select * from {{ ref('complex_transformation') }}
```

### Incremental
```sql
-- Only process new/changed records
-- Use for: Large fact tables, event logs
{{
    config(
        materialized='incremental',
        unique_key='id',
        on_schema_change='fail'
    )
}}

select * from {{ ref('source') }}
{% if is_incremental() %}
    where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

### Ephemeral
```sql
-- Not materialized, used as CTE
-- Use for: Intermediate steps, reusable logic
{{ config(materialized='ephemeral') }}

select * from {{ ref('staging') }}
```

## Incremental Models Patterns

### Timestamp-Based
```sql
{{
    config(
        materialized='incremental',
        unique_key='id'
    )
}}

select * from {{ source('app', 'events') }}
{% if is_incremental() %}
    where event_timestamp > (select max(event_timestamp) from {{ this }})
{% endif %}
```

### Delete and Insert
```sql
{{
    config(
        materialized='incremental',
        unique_key='date_day'
    )
}}

select
    date_trunc('day', created_at) as date_day,
    count(*) as num_events
from {{ source('app', 'events') }}
group by 1

{% if is_incremental() %}
    -- Will delete and re-insert records for these dates
    where date_day >= (select max(date_day) from {{ this }})
{% endif %}
```

### Upsert (Merge)
```sql
{{
    config(
        materialized='incremental',
        unique_key='customer_id',
        merge_update_columns=['customer_name', 'email', 'updated_at']
    )
}}

select
    customer_id,
    customer_name,
    email,
    updated_at
from {{ ref('stg_customers') }}
{% if is_incremental() %}
    where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

## Snapshots (SCD Type 2)

```sql
-- snapshots/snap_customers.sql
{% snapshot snap_customers %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at',
        invalidate_hard_deletes=True
    )
}}

select * from {{ source('app', 'customers') }}

{% endsnapshot %}
```

**Timestamp Strategy:**
```sql
-- Tracks changes based on updated_at column
strategy='timestamp',
updated_at='updated_at'
```

**Check Strategy:**
```sql
-- Tracks changes based on all columns or specific columns
strategy='check',
check_cols=['customer_name', 'email', 'status']
-- Or check all columns
check_cols='all'
```

## Tests

### Schema Tests (YAML)
```yaml
# models/staging/_staging.yml
version: 2

models:
  - name: stg_customers
    description: "Cleaned customer data"
    columns:
      - name: customer_id
        description: "Primary key"
        tests:
          - unique
          - not_null
      - name: customer_email
        tests:
          - not_null
          - unique
      - name: customer_status
        tests:
          - accepted_values:
              values: ['active', 'inactive', 'pending']
      - name: created_at
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= '2020-01-01'"

  - name: stg_orders
    description: "Cleaned order data"
    tests:
      # Relationship test
      - dbt_utils.relationships_where:
          to: ref('stg_customers')
          field: customer_id
          where: "order_status != 'cancelled'"
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
      - name: amount_dollars
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

### Custom Data Tests
```sql
-- tests/assert_positive_total.sql
-- Returns records that fail the test
select
    order_id,
    amount_dollars
from {{ ref('fct_orders') }}
where amount_dollars < 0
```

### Custom Generic Tests
```sql
-- macros/test_is_even.sql
{% test is_even(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} % 2 != 0

{% endtest %}
```

```yaml
# Usage in schema.yml
columns:
  - name: quantity
    tests:
      - is_even
```

## Macros

### Reusable SQL Logic
```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name) %}
    round({{ column_name }} / 100.0, 2)
{% endmacro %}
```

```sql
-- Usage in model
select
    order_id,
    {{ cents_to_dollars('amount_cents') }} as amount_dollars
from {{ source('app', 'orders') }}
```

### Custom Schema Generation
```sql
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}

    {%- if custom_schema_name is none -%}
        {{ default_schema }}

    {%- elif target.name == 'prod' -%}
        {{ custom_schema_name | trim }}

    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}

    {%- endif -%}
{%- endmacro %}
```

## Sources

### Source Configuration
```yaml
# models/staging/sources.yml
version: 2

sources:
  - name: ecommerce
    description: "Raw ecommerce data from production database"
    database: raw
    schema: ecommerce_prod
    tables:
      - name: raw_customers
        description: "Raw customer data"
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}
        loaded_at_field: _loaded_at
        columns:
          - name: customer_id
            description: "Primary key"
            tests:
              - unique
              - not_null

      - name: raw_orders
        description: "Raw order transactions"
        freshness:
          warn_after: {count: 6, period: hour}
        loaded_at_field: created_at
```

### Source Reference
```sql
select * from {{ source('ecommerce', 'raw_customers') }}
```

### Source Freshness Check
```bash
# Check if sources are fresh
dbt source freshness

# Returns warning/error if data is stale
```

## Documentation

### Model Documentation
```yaml
# models/marts/core/_core.yml
version: 2

models:
  - name: fct_orders
    description: >
      Fact table containing one record per order.
      Includes customer details and order metrics.
    columns:
      - name: order_id
        description: "Unique order identifier"
      - name: customer_id
        description: "Foreign key to dim_customers"
      - name: order_date
        description: "Date the order was placed"
      - name: amount_dollars
        description: "Order total in USD"
        meta:
          metric_type: 'sum'
          format: 'currency'
```

### Generate Documentation Site
```bash
# Generate docs
dbt docs generate

# Serve docs locally
dbt docs serve
# Opens at http://localhost:8080
```

## dbt_project.yml Configuration

```yaml
name: 'analytics'
version: '1.0.0'
config-version: 2

profile: 'analytics'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

# Global model configs
models:
  analytics:
    +materialized: view
    +persist_docs:
      relation: true
      columns: true

    staging:
      +materialized: view
      +schema: staging
      +tags: ["staging"]

    intermediate:
      +materialized: ephemeral
      +tags: ["intermediate"]

    marts:
      +materialized: table
      +schema: marts
      +tags: ["marts"]

      core:
        +materialized: table
        +tags: ["core"]

      marketing:
        +materialized: table
        +tags: ["marketing"]

# Seed configs
seeds:
  +schema: seeds
  +tags: ["seeds"]

# Snapshot configs
snapshots:
  +target_schema: snapshots
  +strategy: timestamp
  +updated_at: updated_at
  +tags: ["snapshots"]

# Exposure and metric configs
exposures:
  +enabled: true

# Test configurations
tests:
  +severity: warn  # or 'error'
  +store_failures: true
  +schema: test_failures
```

## Jinja and Macros

### Conditional Logic
```sql
select
    order_id,
    {% if target.name == 'prod' %}
        customer_id  -- Real ID in production
    {% else %}
        md5(customer_id)  -- Hashed in dev
    {% endif %} as customer_id
from orders
```

### Loops
```sql
select
    {% for status in ['pending', 'processing', 'shipped', 'delivered'] %}
        sum(case when status = '{{ status }}' then 1 else 0 end) as {{ status }}_count
        {% if not loop.last %},{% endif %}
    {% endfor %}
from orders
group by 1
```

### Variables
```sql
-- dbt_project.yml
vars:
  start_date: '2023-01-01'
  excluded_customers: ['test_customer']

-- In model
select * from orders
where order_date >= '{{ var("start_date") }}'
  and customer_id not in ({{ var("excluded_customers") | join(", ") }})
```

## Best Practices

### Naming Conventions
```
stg_<source>_<entity>   # Staging: stg_salesforce_contacts
int_<entity>            # Intermediate: int_customer_orders
fct_<entity>            # Facts: fct_orders
dim_<entity>            # Dimensions: dim_customers
rpt_<entity>            # Reports: rpt_monthly_revenue
```

### Style Guide
```sql
-- Use lowercase
-- Use underscores, not camelCase
-- Use descriptive names
-- Align SQL keywords

select
    customer_id,
    customer_name,
    created_at
from {{ ref('stg_customers') }}
where customer_status = 'active'
order by created_at desc
```

### CTE Formatting
```sql
with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

customer_orders as (
    select
        c.customer_id,
        c.customer_name,
        count(o.order_id) as order_count,
        sum(o.amount) as total_amount
    from customers c
    left join orders o
        on c.customer_id = o.customer_id
    group by 1, 2
),

final as (
    select * from customer_orders
)

select * from final
```

### Performance Optimization
1. **Use incremental models** for large tables
2. **Materialize upstream models** that are referenced multiple times
3. **Use ephemeral models** for simple transformations
4. **Partition and cluster** large tables
5. **Limit data in dev** using `{% if target.name != 'prod' %} limit 1000 {% endif %}`
6. **Use refs, not direct table names** for dependency management

### Testing Strategy
1. **Test all primary keys** (unique, not_null)
2. **Test all foreign keys** (relationships)
3. **Test accepted values** for categorical columns
4. **Test data freshness** for critical sources
5. **Custom tests** for business logic
6. **Store test failures** for investigation

### Version Control
```
# .gitignore
target/
dbt_packages/
logs/
profiles.yml  # Contains credentials, never commit
```

## Common Commands

```bash
# Run all models
dbt run

# Run specific model
dbt run --select fct_orders

# Run model and downstream
dbt run --select fct_orders+

# Run model and upstream
dbt run --select +fct_orders

# Run by tag
dbt run --select tag:staging

# Run by path
dbt run --select marts.core.*

# Full refresh (ignore incremental)
dbt run --full-refresh

# Test all models
dbt test

# Test specific model
dbt test --select fct_orders

# Compile (without running)
dbt compile

# Generate documentation
dbt docs generate
dbt docs serve

# Run snapshots
dbt snapshot

# Load seeds
dbt seed

# Debug connection
dbt debug

# Clean artifacts
dbt clean

# Install packages
dbt deps
```

## Packages

### packages.yml
```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.0

  - package: calogica/dbt_expectations
    version: 0.9.0

  - package: dbt-labs/audit_helper
    version: 0.9.0

  - package: dbt-labs/codegen
    version: 0.10.0
```

### Useful Packages
- **dbt_utils**: General utility macros (date_spine, surrogate_key, etc.)
- **dbt_expectations**: Additional tests (Great Expectations style)
- **audit_helper**: Compare query results between runs
- **codegen**: Auto-generate dbt YAML files
- **re_data**: Data quality monitoring

## CI/CD Integration

### GitHub Actions Example
```yaml
name: dbt CI
on: [pull_request]

jobs:
  dbt_run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.9"
      - name: Install dbt
        run: pip install dbt-core dbt-snowflake
      - name: Run dbt
        run: |
          dbt deps
          dbt seed
          dbt run
          dbt test
        env:
          DBT_PROFILES_DIR: .
```

## Troubleshooting

### Common Issues

**Circular Dependency:**
```
Use ephemeral models or restructure dependencies
```

**Incremental Model Not Working:**
```
Check unique_key matches actual unique column
Verify incremental logic with --full-refresh
```

**Test Failures:**
```
Store failures: +store_failures: true
Query failures: select * from <schema>.test_failures
```

**Compilation Errors:**
```
Run dbt compile to see generated SQL
Check Jinja syntax in models
```
