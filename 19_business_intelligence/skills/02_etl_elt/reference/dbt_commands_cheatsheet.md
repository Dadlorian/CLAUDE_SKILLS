# dbt Commands Cheatsheet

## Essential Commands

### Setup & Initialization
```bash
# Initialize new dbt project
dbt init <project_name>

# Install packages from packages.yml
dbt deps

# Debug connection and configuration
dbt debug

# Compile project (no execution)
dbt compile
```

### Running Models
```bash
# Run all models
dbt run

# Run specific model
dbt run --models model_name
dbt run -m model_name

# Run model and all downstream dependencies
dbt run -m model_name+

# Run model and all upstream dependencies
dbt run -m +model_name

# Run model and all dependencies (up and downstream)
dbt run -m +model_name+

# Run all models in a directory
dbt run -m staging.*
dbt run -m marts.marketing.*

# Run by tag
dbt run -m tag:daily
dbt run -m tag:critical

# Run modified models only (slim CI)
dbt run -m state:modified --state ./target

# Run with specific target
dbt run --target prod
dbt run --target dev

# Full refresh (ignore incremental logic)
dbt run --full-refresh
dbt run -m model_name --full-refresh
```

### Testing
```bash
# Run all tests
dbt test

# Test specific model
dbt test -m model_name

# Run specific test
dbt test -m test_name

# Test sources
dbt test -m source:*

# Run schema tests only
dbt test --schema

# Run data tests only
dbt test --data

# Store failures for investigation
dbt test --store-failures
```

### Documentation
```bash
# Generate documentation
dbt docs generate

# Serve documentation locally (port 8080)
dbt docs serve

# Serve on specific port
dbt docs serve --port 8001
```

### Sources
```bash
# Snapshot source freshness
dbt source freshness

# Snapshot specific source
dbt source freshness --select source:source_name
```

### Snapshots
```bash
# Run all snapshots
dbt snapshot

# Run specific snapshot
dbt snapshot -m snapshot_name
```

### Seeds
```bash
# Load all seed files
dbt seed

# Load specific seed
dbt seed -m seed_name

# Full refresh seed (drop and recreate)
dbt seed --full-refresh
```

### Build (run + test)
```bash
# Run models and tests together
dbt build

# Build specific model with tests
dbt build -m model_name

# Build with resource type selection
dbt build --resource-type model
dbt build --resource-type test
```

## Selection Syntax

### Graph Operators
```bash
# Plus operator (+ before and after)
+model_name     # Model and all parents
model_name+     # Model and all children
+model_name+    # Model and all dependencies

# At operator (limit depth)
+model_name     # All ancestors
1+model_name    # 1 level of ancestors
2+model_name    # 2 levels of ancestors

# Star operator (within package/directory)
staging.*       # All models in staging directory
package_name.*  # All models in package

# Comma (union)
modelA,modelB   # Both models

# Space (intersection)
tag:daily tag:critical  # Models with both tags

# Exclude operator
--exclude model_name
-m +fact_orders --exclude staging.*
```

### Selection Methods
```bash
# By model name
-m model_name
-m stg_customers

# By directory/path
-m staging.*
-m marts.finance.*

# By tag
-m tag:daily
-m tag:hourly

# By source
-m source:postgres.*
-m source:postgres.public.orders

# By package
-m package:dbt_utils

# By config
-m config.materialized:table
-m config.schema:marketing

# By state (for CI)
-m state:modified
-m state:new

# By result
-m result:error
-m result:fail

# By exposure
-m +exposure:my_dashboard
```

## Advanced Usage

### Environment Variables
```bash
# Set target environment
export DBT_TARGET=prod
dbt run

# Set threads
export DBT_THREADS=8
dbt run

# Set profiles directory
export DBT_PROFILES_DIR=~/.dbt
```

### Flags & Options
```bash
# Set number of threads
dbt run --threads 8

# Specify vars (variables)
dbt run --vars '{key: value}'
dbt run --vars '{start_date: "2024-01-01"}'

# Fail fast (stop on first error)
dbt run --fail-fast

# No version check
dbt run --no-version-check

# Debug mode
dbt run --debug

# Specify profile
dbt run --profile my_profile

# Single-threaded execution (easier debugging)
dbt run --threads 1

# Warning as errors
dbt run --warn-error
```

### CI/CD Usage
```bash
# Slim CI: run only modified models
dbt run -m state:modified+ --state ./prod-target

# Defer to production artifacts
dbt run --defer --state ./prod-run-artifacts

# Parse project only (fast validation)
dbt parse

# List resources without running
dbt ls -m tag:daily
dbt ls --resource-type model
dbt ls --output json

# Retry failed tests
dbt retry
```

## Materialization Options

### Configure in Model
```sql
-- View (default)
{{ config(materialized='view') }}

-- Table
{{ config(materialized='table') }}

-- Incremental
{{ config(
    materialized='incremental',
    unique_key='id',
    on_schema_change='fail'  -- or 'append_new_columns', 'sync_all_columns', 'ignore'
) }}

-- Ephemeral (CTE in dependent models)
{{ config(materialized='ephemeral') }}
```

### Run with Override
```bash
# Override materialization at runtime
dbt run -m model_name --vars '{materialized: table}'
```

## Common Workflows

### Development Workflow
```bash
# 1. Run specific model during development
dbt run -m stg_orders

# 2. Test the model
dbt test -m stg_orders

# 3. View compiled SQL
cat target/compiled/project_name/models/staging/stg_orders.sql

# 4. Build model and all dependencies
dbt build -m +stg_orders+
```

### Production Deployment
```bash
# 1. Install dependencies
dbt deps

# 2. Run seeds (reference data)
dbt seed --target prod

# 3. Run snapshots
dbt snapshot --target prod

# 4. Run all models
dbt run --target prod --threads 16

# 5. Test all models
dbt test --target prod

# 6. Check source freshness
dbt source freshness --target prod

# 7. Generate docs
dbt docs generate --target prod
```

### Debugging Failures
```bash
# 1. Run with debug output
dbt run -m failing_model --debug

# 2. Single-threaded for clearer logs
dbt run -m failing_model --threads 1

# 3. View compiled SQL
cat target/compiled/project_name/models/path/failing_model.sql

# 4. View run results
cat target/run_results.json | jq '.results[] | select(.status=="error")'

# 5. Test and store failures
dbt test --store-failures
# Then query the failures table in your warehouse
```

### Performance Investigation
```bash
# 1. Compile to see generated SQL
dbt compile -m slow_model

# 2. Run with logging
dbt run -m slow_model --log-level debug

# 3. Check run results for timing
cat target/run_results.json | jq '.results[] | {name: .unique_id, time: .execution_time}'

# 4. Profile the model in your warehouse
# Copy SQL from target/compiled and run with EXPLAIN in warehouse
```

## dbt Cloud Specific

### Job Commands
```bash
# Trigger job via API
curl -X POST \
  -H "Authorization: Token ${DBT_CLOUD_API_TOKEN}" \
  -H "Content-Type: application/json" \
  https://cloud.getdbt.com/api/v2/accounts/{account_id}/jobs/{job_id}/run/

# Get job status
dbt run --job-id <job_id>
```

### CI Job Patterns
```bash
# Slim CI in dbt Cloud
dbt build -m state:modified+ --defer --state ./prod-artifacts

# Full regression on main
dbt build --target prod
```

## Jinja & Macros

### Using Variables
```bash
# Pass variables at runtime
dbt run --vars '{start_date: "2024-01-01", end_date: "2024-12-31"}'

# Use in model
WHERE date >= '{{ var("start_date") }}'
```

### Common Macros
```sql
-- Current timestamp
{{ dbt_utils.current_timestamp() }}

-- Surrogate key
{{ dbt_utils.surrogate_key(['col1', 'col2']) }}

-- Union tables
{{ dbt_utils.union_relations(relations=[ref('table1'), ref('table2')]) }}

-- Date spine
{{ dbt_utils.date_spine(...) }}

-- Get column values
{{ dbt_utils.get_column_values(table=ref('model'), column='status') }}
```

## Troubleshooting Commands

```bash
# Clear target directory
rm -rf target/
dbt clean

# Validate project configuration
dbt debug

# List all resources
dbt ls

# Show dependency graph
dbt docs generate
# Then view in docs UI: localhost:8080

# Check for circular dependencies
dbt compile --select +model_name

# Validate SQL compilation
dbt parse

# Run with verbose logging
dbt run -m model_name --log-level debug

# Check for orphaned tests
dbt ls --resource-type test --select config.enabled:false
```

## Performance Tips

```bash
# Use appropriate thread count (typically 2x CPU cores)
dbt run --threads 16

# Run incrementals only (skip full refresh)
dbt run -m config.materialized:incremental

# Run critical path first
dbt run -m tag:critical

# Use selectors.yml for complex selections
dbt run --selector critical_path

# Defer to production for CI (avoid rebuilding everything)
dbt run -m state:modified+ --defer --state ./prod
```

## Exit Codes

- **0**: Success
- **1**: Error (compilation, runtime, or test failures)
- **2**: Keyboard interrupt

## Quick Reference Card

| Task | Command |
|------|---------|
| Run everything | `dbt build` |
| Run one model | `dbt run -m model_name` |
| Run model + downstream | `dbt run -m model_name+` |
| Run modified only | `dbt run -m state:modified+` |
| Test everything | `dbt test` |
| Test one model | `dbt test -m model_name` |
| Generate docs | `dbt docs generate && dbt docs serve` |
| Check freshness | `dbt source freshness` |
| Load seeds | `dbt seed` |
| Run snapshots | `dbt snapshot` |
| Full refresh incremental | `dbt run -m model_name --full-refresh` |
| Debug connection | `dbt debug` |
| Install packages | `dbt deps` |

## Resources

- **Official Docs**: https://docs.getdbt.com
- **Command Reference**: https://docs.getdbt.com/reference/dbt-commands
- **Selection Syntax**: https://docs.getdbt.com/reference/node-selection/syntax
- **dbt Slack**: https://getdbt.slack.com
