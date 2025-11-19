# dbt Macros Reference

## Built-in Macros

### ref() - Reference Models
```sql
-- Reference another model
SELECT *
FROM {{ ref('stg_customers') }}

-- Reference model from different project/package
SELECT *
FROM {{ ref('dbt_utils', 'surrogate_key') }}
```

### source() - Reference Sources
```sql
-- Reference source table
SELECT *
FROM {{ source('postgres', 'customers') }}

-- Multi-source union
SELECT * FROM {{ source('postgres', 'orders') }}
UNION ALL
SELECT * FROM {{ source('shopify', 'orders') }}
```

### config() - Model Configuration
```sql
{{
    config(
        materialized='incremental',
        unique_key='id',
        on_schema_change='sync_all_columns',
        tags=['daily', 'critical'],
        schema='analytics',
        alias='customers_dimension',
        partition_by={
            'field': 'created_date',
            'data_type': 'date'
        },
        cluster_by=['customer_id', 'country']
    )
}}

SELECT * FROM ...
```

### var() - Variables
```sql
-- Use variable with default
WHERE created_at >= '{{ var("start_date", "2024-01-01") }}'

-- Use variable (required)
WHERE region = '{{ var("region") }}'

-- Set at runtime: dbt run --vars '{start_date: "2024-06-01", region: "US"}'
```

### this - Current Model Reference
```sql
{% if is_incremental() %}
    -- Reference current table
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

## dbt_utils Package Macros

### surrogate_key() - Generate Hash Keys
```sql
-- Generate surrogate key from multiple columns
{{ dbt_utils.surrogate_key(['order_id', 'line_number']) }} as order_line_key

-- Example output: MD5 hash of concatenated values
```

### union_relations() - Union Tables
```sql
-- Union multiple tables/models
{{ dbt_utils.union_relations(
    relations=[
        ref('orders_2023'),
        ref('orders_2024')
    ]
) }}

-- With column subset
{{ dbt_utils.union_relations(
    relations=[ref('orders_us'), ref('orders_eu')],
    include=['order_id', 'customer_id', 'amount']
) }}
```

### generate_surrogate_key() - New Version
```sql
-- dbt_utils v1.0+
{{ dbt_utils.generate_surrogate_key(['customer_id', 'order_date']) }} as daily_customer_key
```

### star() - Select All Columns
```sql
-- Select all columns from a relation
SELECT
    {{ dbt_utils.star(from=ref('stg_orders')) }},
    CURRENT_TIMESTAMP as loaded_at
FROM {{ ref('stg_orders') }}

-- Exclude columns
SELECT
    {{ dbt_utils.star(
        from=ref('stg_orders'),
        except=['created_at', 'updated_at']
    ) }}
FROM {{ ref('stg_orders') }}

-- Add prefix
SELECT
    {{ dbt_utils.star(
        from=ref('stg_orders'),
        prefix='order_'
    ) }}
FROM {{ ref('stg_orders') }}
```

### pivot() - Pivot Data
```sql
-- Pivot table
SELECT
    customer_id,
    {{ dbt_utils.pivot(
        column='product_category',
        values=dbt_utils.get_column_values(
            table=ref('orders'),
            column='product_category'
        ),
        agg='sum',
        then_value='amount'
    ) }}
FROM {{ ref('orders') }}
GROUP BY customer_id
```

### get_column_values() - Get Distinct Values
```sql
-- Get unique column values
{% set categories = dbt_utils.get_column_values(
    table=ref('products'),
    column='category'
) %}

-- Use in query
SELECT
    product_id,
    category,
    CASE
        {% for cat in categories %}
        WHEN category = '{{ cat }}' THEN 1
        {% endfor %}
        ELSE 0
    END as category_flag
FROM {{ ref('products') }}
```

### date_spine() - Generate Date Series
```sql
-- Generate date range
{{ dbt_utils.date_spine(
    datepart="day",
    start_date="cast('2024-01-01' as date)",
    end_date="cast('2024-12-31' as date)"
) }}

-- Use for missing date filling
WITH date_spine AS (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="to_date('2024-01-01', 'yyyy-mm-dd')",
        end_date="current_date()"
    ) }}
),
daily_sales AS (
    SELECT
        DATE(order_date) as date,
        SUM(amount) as revenue
    FROM {{ ref('orders') }}
    GROUP BY DATE(order_date)
)
SELECT
    d.date_day,
    COALESCE(s.revenue, 0) as revenue
FROM date_spine d
LEFT JOIN daily_sales s ON d.date_day = s.date
```

### group_by() - Numeric GROUP BY
```sql
-- Generate GROUP BY with column numbers
SELECT
    customer_id,
    product_id,
    SUM(amount) as total_amount
FROM {{ ref('orders') }}
{{ dbt_utils.group_by(n=2) }}
-- Generates: GROUP BY 1, 2
```

### deduplicate() - Remove Duplicates
```sql
-- Deduplicate based on partition key and order
{{ dbt_utils.deduplicate(
    relation=source('raw', 'orders'),
    partition_by='order_id',
    order_by='updated_at DESC'
) }}
```

## Custom Macro Examples

### cents_to_dollars() - Currency Conversion
```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name, precision=2) %}
    ROUND({{ column_name }} / 100.0, {{ precision }})
{% endmacro %}

-- Usage in model
SELECT
    order_id,
    {{ cents_to_dollars('amount_cents') }} as amount_dollars,
    {{ cents_to_dollars('tax_cents', 4) }} as tax_dollars
FROM {{ ref('stg_orders') }}
```

### generate_schema_name() - Custom Schema Logic
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

### grant_select() - Manage Permissions
```sql
-- macros/grant_select.sql
{% macro grant_select(role, schema=target.schema) %}
    {% set sql %}
        GRANT SELECT ON ALL TABLES IN SCHEMA {{ schema }} TO {{ role }};
    {% endset %}

    {% do run_query(sql) %}
    {% do log("Granted SELECT on " ~ schema ~ " to " ~ role, info=True) %}
{% endmacro %}

-- Use in post-hook
{{ config(
    post_hook="{{ grant_select('analyst_role') }}"
) }}
```

### safe_divide() - Null-Safe Division
```sql
-- macros/safe_divide.sql
{% macro safe_divide(numerator, denominator) %}
    CASE
        WHEN {{ denominator }} = 0 OR {{ denominator }} IS NULL
        THEN NULL
        ELSE {{ numerator }}::FLOAT / {{ denominator }}
    END
{% endmacro %}

-- Usage
SELECT
    customer_id,
    {{ safe_divide('total_revenue', 'order_count') }} as avg_order_value
FROM {{ ref('customer_metrics') }}
```

### unpivot() - Unpivot Columns
```sql
-- macros/unpivot.sql
{% macro unpivot(relation, cast_to='varchar', exclude=[], remove=[], field_name='field_name', value_name='value') %}

    {% set cols = adapter.get_columns_in_relation(relation) %}

    {% set fields_to_unpivot = [] %}
    {% for col in cols %}
        {% if col.name|lower not in exclude|map('lower')
           and col.name|lower not in remove|map('lower') %}
            {% do fields_to_unpivot.append(col.name) %}
        {% endif %}
    {% endfor %}

    SELECT
        {% for col in exclude %}
        {{ col }},
        {% endfor %}

        {{ field_name }},
        CAST({{ value_name }} AS {{ cast_to }}) AS {{ value_name }}

    FROM {{ relation }}

    UNPIVOT (
        {{ value_name }}
        FOR {{ field_name }} IN (
            {% for field in fields_to_unpivot %}
                {{ field }}{% if not loop.last %},{% endif %}
            {% endfor %}
        )
    )
{% endmacro %}
```

### log_execution_time() - Performance Tracking
```sql
-- macros/log_execution_time.sql
{% macro log_execution_time() %}
    {% if execute %}
        {% set start_time = modules.datetime.datetime.now() %}
        {{ log("Model execution started at: " ~ start_time, info=True) }}

        {% set sql %}
            SELECT 1  -- Your actual query
        {% endset %}

        {% set result = run_query(sql) %}

        {% set end_time = modules.datetime.datetime.now() %}
        {% set duration = (end_time - start_time).total_seconds() %}
        {{ log("Model execution completed in: " ~ duration ~ " seconds", info=True) }}
    {% endif %}
{% endmacro %}
```

### create_udfs() - User-Defined Functions
```sql
-- macros/create_udfs.sql (BigQuery example)
{% macro create_udfs() %}

    {% set sql %}
    CREATE TEMP FUNCTION parse_user_agent(ua STRING)
    RETURNS STRUCT<browser STRING, os STRING>
    LANGUAGE js AS """
        var parser = new UAParser(ua);
        return {
            browser: parser.getBrowser().name,
            os: parser.getOS().name
        };
    """;
    {% endset %}

    {% do run_query(sql) %}

{% endmacro %}

-- Use in model
{% if execute %}
    {{ create_udfs() }}
{% endif %}

SELECT
    user_id,
    parse_user_agent(user_agent) as ua_info
FROM {{ ref('events') }}
```

### generate_alias_name() - Custom Table Names
```sql
-- macros/generate_alias_name.sql
{% macro generate_alias_name(custom_alias_name=none, node=none) -%}

    {%- if custom_alias_name is none -%}
        {{ node.name }}

    {%- elif target.name == 'prod' -%}
        {{ custom_alias_name | trim }}

    {%- else -%}
        {{ node.name }}_{{ target.name }}

    {%- endif -%}

{%- endmacro %}
```

## Advanced Patterns

### Incremental with Merge Delete
```sql
-- macros/incremental_merge_with_deletes.sql
{% macro incremental_merge_with_deletes(
    target_relation,
    source_relation,
    unique_key,
    deleted_flag_column
) %}

    MERGE INTO {{ target_relation }} AS target
    USING {{ source_relation }} AS source
    ON target.{{ unique_key }} = source.{{ unique_key }}

    WHEN MATCHED AND source.{{ deleted_flag_column }} = TRUE THEN
        DELETE

    WHEN MATCHED THEN
        UPDATE SET *

    WHEN NOT MATCHED THEN
        INSERT *

{% endmacro %}
```

### Dynamic SQL Generation
```sql
-- macros/generate_funnel_metrics.sql
{% macro generate_funnel_metrics(events_list) %}

    SELECT
        user_id,
        MIN(event_timestamp) as first_event,
        {% for event in events_list %}
        MIN(CASE WHEN event_name = '{{ event }}' THEN event_timestamp END) as {{ event }}_at,
        {% endfor %}

        -- Funnel conversion flags
        {% for i in range(1, events_list|length) %}
        CASE
            WHEN {{ events_list[i] }}_at > {{ events_list[i-1] }}_at
            THEN 1 ELSE 0
        END as converted_{{ events_list[i-1] }}_to_{{ events_list[i] }}
        {% if not loop.last %},{% endif %}
        {% endfor %}

    FROM {{ ref('events') }}
    GROUP BY user_id

{% endmacro %}

-- Usage
{{ generate_funnel_metrics(['signup', 'activation', 'purchase']) }}
```

### Cross-Database Compatibility
```sql
-- macros/date_trunc.sql
{% macro date_trunc(datepart, column) %}
    {% if target.type == 'bigquery' %}
        DATE_TRUNC({{ column }}, {{ datepart }})
    {% elif target.type == 'snowflake' %}
        DATE_TRUNC('{{ datepart }}', {{ column }})
    {% elif target.type == 'postgres' %}
        DATE_TRUNC('{{ datepart }}', {{ column }})
    {% elif target.type == 'redshift' %}
        DATE_TRUNC('{{ datepart }}', {{ column }})
    {% endif %}
{% endmacro %}

-- Usage
SELECT
    {{ date_trunc('month', 'order_date') }} as order_month,
    COUNT(*) as order_count
FROM {{ ref('orders') }}
GROUP BY 1
```

### Test Generation Macro
```sql
-- macros/generate_tests.sql
{% macro generate_not_null_tests(model, columns) %}

    {% for column in columns %}
    - name: {{ column }}
      tests:
        - not_null
        - dbt_utils.not_null_proportion:
            at_least: 0.95
    {% endfor %}

{% endmacro %}
```

## Jinja Templating Tricks

### Loops and Conditionals
```sql
-- Dynamic column generation
SELECT
    {% for i in range(1, 13) %}
    SUM(CASE WHEN MONTH(order_date) = {{ i }} THEN amount ELSE 0 END) as month_{{ i }}_revenue
    {% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ ref('orders') }}

-- Conditional SQL
{% if var('include_test_data', false) %}
    WHERE is_test = FALSE
{% endif %}
```

### String Manipulation
```sql
-- Convert to uppercase
{{ 'customer_name' | upper }}

-- Strip whitespace
{{ '  value  ' | trim }}

-- Replace
{{ 'snake_case_column' | replace('_', ' ') | title }}

-- Join list
{% set columns = ['id', 'name', 'email'] %}
{{ columns | join(', ') }}
```

### Filters and Functions
```sql
-- Check if variable is defined
{% if var('region', None) is not none %}
    WHERE region = '{{ var("region") }}'
{% endif %}

-- Default value
{{ var('limit', 100) }}

-- Length
{% set items = ['a', 'b', 'c'] %}
{% if items | length > 0 %}
    -- Do something
{% endif %}

-- Map
{% set ids = [1, 2, 3] %}
{{ ids | map('string') | join(', ') }}
```

## Package Management

### Installing Packages
```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1

  - package: calogica/dbt_expectations
    version: 0.10.0

  - package: dbt-labs/codegen
    version: 0.12.0

  - git: https://github.com/your-org/custom-macros.git
    revision: v1.0.0

  - local: ../local-packages/my-macros
```

### Using Package Macros
```sql
-- Call macro from package
{{ dbt_utils.surrogate_key(['col1', 'col2']) }}

-- Override package macro
{{ your_package.custom_surrogate_key(['col1', 'col2']) }}
```

## Best Practices

1. **Keep macros focused** - Single responsibility
2. **Use descriptive names** - `cents_to_dollars` not `convert`
3. **Document parameters** - Add docstrings
4. **Handle edge cases** - Null values, empty lists
5. **Make them reusable** - Avoid hard-coded values
6. **Test macros** - Unit test complex logic
7. **Use packages** - Don't reinvent the wheel
8. **Version control** - Track macro changes

## Resources

- **dbt Jinja**: https://docs.getdbt.com/docs/building-a-dbt-project/jinja-macros
- **dbt_utils**: https://github.com/dbt-labs/dbt-utils
- **Jinja Docs**: https://jinja.palletsprojects.com/
- **dbt Package Hub**: https://hub.getdbt.com/
