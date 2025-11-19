# BI DevOps and CI/CD Pattern

## Overview

BI DevOps applies software engineering practices to business intelligence development, ensuring reliable, scalable, and maintainable analytics code. This pattern covers version control, testing, continuous integration, and deployment for modern BI platforms including dbt, LookML, Power BI, and Tableau.

## Core Principles

1. **Version Control**: All BI code in Git
2. **Testing**: Automated data quality and logic tests
3. **Code Review**: Peer review before production
4. **CI/CD**: Automated build, test, and deploy
5. **Documentation**: Code as documentation
6. **Monitoring**: Production data quality checks
7. **Rollback**: Quick revert capabilities

## Git Workflow for BI Projects

### Repository Structure

```
analytics-repo/
├── .github/
│   └── workflows/
│       ├── dbt_ci.yml
│       ├── lookml_ci.yml
│       └── power_bi_ci.yml
├── dbt_project/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   ├── marts/
│   │   └── metrics/
│   ├── tests/
│   ├── macros/
│   ├── seeds/
│   └── packages.yml
├── lookml/
│   ├── models/
│   ├── views/
│   ├── dashboards/
│   └── manifest.lkml
├── power_bi/
│   ├── reports/
│   ├── datasets/
│   └── dataflows/
├── tableau/
│   ├── workbooks/
│   ├── datasources/
│   └── flows/
├── scripts/
│   ├── deploy.sh
│   ├── test.sh
│   └── validate.py
├── docs/
│   ├── style_guide.md
│   ├── testing_strategy.md
│   └── deployment_process.md
├── .gitignore
├── .pre-commit-config.yaml
├── requirements.txt
└── README.md
```

### Branch Strategy

```yaml
# branching_strategy.yml
branching_model: trunk-based

branches:
  main:
    description: "Production code"
    protection:
      required_reviews: 2
      require_ci_pass: true
      restrict_push: true
      auto_merge: false

  develop:
    description: "Integration branch for features"
    protection:
      required_reviews: 1
      require_ci_pass: true

  feature/*:
    description: "Feature development branches"
    naming_convention: "feature/TICKET-123-description"
    merge_target: develop
    lifetime: "< 2 weeks"

  hotfix/*:
    description: "Production hotfixes"
    naming_convention: "hotfix/TICKET-456-description"
    merge_target: main
    require_approval: true

workflow:
  1. Create feature branch from develop
  2. Develop and test locally
  3. Push and create PR to develop
  4. CI runs automatically
  5. Code review and approval
  6. Merge to develop
  7. Integration testing
  8. PR from develop to main
  9. Production deployment
```

## dbt CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/dbt_ci.yml
name: dbt CI/CD

on:
  pull_request:
    branches: [develop, main]
    paths:
      - 'dbt_project/**'
  push:
    branches: [main]

env:
  DBT_PROFILES_DIR: ./dbt_project
  DBT_PROJECT_DIR: ./dbt_project

jobs:
  lint:
    name: SQL Linting
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install SQLFluff
        run: |
          pip install sqlfluff sqlfluff-templater-dbt

      - name: Lint SQL files
        run: |
          sqlfluff lint ${{ env.DBT_PROJECT_DIR }}/models \
            --dialect snowflake \
            --config .sqlfluff

      - name: Check SQL formatting
        run: |
          sqlfluff fix ${{ env.DBT_PROJECT_DIR }}/models \
            --dialect snowflake \
            --check \
            --config .sqlfluff

  compile:
    name: Compile dbt Project
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          dbt deps --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Configure dbt profile
        run: |
          mkdir -p ~/.dbt
          cat > ~/.dbt/profiles.yml << EOF
          analytics:
            target: ci
            outputs:
              ci:
                type: snowflake
                account: ${{ secrets.SNOWFLAKE_ACCOUNT }}
                user: ${{ secrets.SNOWFLAKE_USER }}
                password: ${{ secrets.SNOWFLAKE_PASSWORD }}
                role: ${{ secrets.SNOWFLAKE_ROLE }}
                database: ANALYTICS_CI
                warehouse: TRANSFORMING_CI
                schema: DBT_CI_${{ github.event.pull_request.number }}
                threads: 4
          EOF

      - name: Compile dbt project
        run: |
          dbt compile --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Upload compiled SQL
        uses: actions/upload-artifact@v3
        with:
          name: compiled-sql
          path: ${{ env.DBT_PROJECT_DIR }}/target/compiled

  test:
    name: Run dbt Tests
    runs-on: ubuntu-latest
    needs: compile
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          dbt deps --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Configure dbt profile
        run: |
          # Same as compile step
          mkdir -p ~/.dbt
          cat > ~/.dbt/profiles.yml << EOF
          # Profile configuration
          EOF

      - name: Create CI schema
        run: |
          dbt run-operation create_schema \
            --args "{schema: DBT_CI_${{ github.event.pull_request.number }}}" \
            --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Seed data
        run: |
          dbt seed --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Run models
        run: |
          dbt run --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Run tests
        run: |
          dbt test --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Run data quality checks
        run: |
          python scripts/data_quality_checks.py

      - name: Generate documentation
        run: |
          dbt docs generate --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: ${{ env.DBT_PROJECT_DIR }}/target/run_results.json

  slim-ci:
    name: Slim CI (Modified Models Only)
    runs-on: ubuntu-latest
    needs: lint
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          dbt deps --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Download production manifest
        run: |
          aws s3 cp s3://dbt-artifacts/manifest.json \
            ${{ env.DBT_PROJECT_DIR }}/target/manifest.json

      - name: Run modified models only
        run: |
          dbt run \
            --select state:modified+ \
            --state ${{ env.DBT_PROJECT_DIR }}/target \
            --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Test modified models only
        run: |
          dbt test \
            --select state:modified+ \
            --state ${{ env.DBT_PROJECT_DIR }}/target \
            --project-dir ${{ env.DBT_PROJECT_DIR }}

  performance-test:
    name: Performance Testing
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run performance benchmarks
        run: |
          python scripts/benchmark_queries.py \
            --models changed \
            --threshold 30

      - name: Check query costs
        run: |
          python scripts/check_query_costs.py \
            --max-cost 10.00

      - name: Analyze query plans
        run: |
          dbt run-operation analyze_query_plans \
            --project-dir ${{ env.DBT_PROJECT_DIR }}

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [test, performance-test]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          dbt deps --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Deploy to staging
        run: |
          dbt run --target staging --project-dir ${{ env.DBT_PROJECT_DIR }}
          dbt test --target staging --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Upload manifest
        run: |
          aws s3 cp ${{ env.DBT_PROJECT_DIR }}/target/manifest.json \
            s3://dbt-artifacts/staging/manifest.json

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          dbt deps --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Deploy to production
        run: |
          dbt run --target production --project-dir ${{ env.DBT_PROJECT_DIR }}
          dbt test --target production --project-dir ${{ env.DBT_PROJECT_DIR }}

      - name: Upload artifacts
        run: |
          aws s3 cp ${{ env.DBT_PROJECT_DIR }}/target/manifest.json \
            s3://dbt-artifacts/production/manifest.json
          aws s3 cp ${{ env.DBT_PROJECT_DIR }}/target/run_results.json \
            s3://dbt-artifacts/production/run_results.json

      - name: Publish documentation
        run: |
          dbt docs generate --project-dir ${{ env.DBT_PROJECT_DIR }}
          aws s3 sync ${{ env.DBT_PROJECT_DIR }}/target/ \
            s3://dbt-docs-bucket/ --delete

      - name: Notify deployment
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "dbt production deployment completed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "dbt models deployed to production\nCommit: ${{ github.sha }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  cleanup:
    name: Cleanup CI Environments
    runs-on: ubuntu-latest
    needs: [test, slim-ci]
    if: always()
    steps:
      - name: Drop CI schema
        run: |
          python scripts/cleanup_ci_schema.py \
            --schema DBT_CI_${{ github.event.pull_request.number }}
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 2.3.0
    hooks:
      - id: sqlfluff-lint
        args: [--dialect, snowflake, --config, .sqlfluff]
        files: \.sql$

      - id: sqlfluff-fix
        args: [--dialect, snowflake, --config, .sqlfluff]
        files: \.sql$

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: local
    hooks:
      - id: dbt-compile
        name: dbt compile
        entry: dbt compile --project-dir dbt_project
        language: system
        pass_filenames: false
        always_run: true

      - id: dbt-test
        name: dbt test (modified models)
        entry: python scripts/test_modified_models.py
        language: system
        pass_filenames: false
```

### SQLFluff Configuration

```ini
# .sqlfluff
[sqlfluff]
dialect = snowflake
templater = dbt
max_line_length = 100
indent_unit = space

[sqlfluff:indentation]
indented_joins = true
indented_using_on = true
template_blocks_indent = true

[sqlfluff:rules]
tab_space_size = 4
indent_unit = space

[sqlfluff:rules:L003]
# Indent size
indent_size = 4

[sqlfluff:rules:L010]
# Keywords should be uppercase
capitalisation_policy = upper

[sqlfluff:rules:L014]
# Unquoted identifiers should be lowercase
extended_capitalisation_policy = lower

[sqlfluff:rules:L030]
# Function names should be uppercase
capitalisation_policy = upper

[sqlfluff:rules:L063]
# Data types should be lowercase
extended_capitalisation_policy = lower

[sqlfluff:rules:L016]
# Line length
max_line_length = 100

[sqlfluff:templater:dbt]
project_dir = ./dbt_project
profiles_dir = ./dbt_project
profile = analytics
target = dev
```

## dbt Testing Framework

### Schema Tests

```yaml
# models/schema.yml
version: 2

models:
  - name: fct_orders
    description: "Order facts table with revenue and customer information"

    config:
      materialized: incremental
      unique_key: order_id
      on_schema_change: fail

    tests:
      - dbt_utils.expression_is_true:
          expression: "total_amount >= 0"
          config:
            severity: error

      - dbt_utils.recency:
          datepart: day
          field: order_date
          interval: 1
          config:
            severity: warn

    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - unique
          - not_null

      - name: customer_id
        description: "Foreign key to customers"
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id

      - name: order_date
        description: "Date of order"
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: "'2020-01-01'"
              max_value: "current_date"

      - name: order_status
        description: "Current status of order"
        tests:
          - not_null
          - accepted_values:
              values: ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

      - name: total_amount
        description: "Total order amount"
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_of_type:
              column_type: number
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 1000000

      - name: line_item_count
        description: "Number of line items"
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 1
              max_value: 100

  - name: dim_customers
    description: "Customer dimension table"

    tests:
      - dbt_utils.equal_rowcount:
          compare_model: source('raw', 'customers')

    columns:
      - name: customer_id
        tests:
          - unique
          - not_null

      - name: email
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_match_regex:
              regex: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'

      - name: created_at
        tests:
          - not_null
```

### Custom Tests

```sql
-- tests/assert_revenue_matches_sum_of_orders.sql
-- Test that aggregate revenue matches sum of individual orders

WITH order_totals AS (
    SELECT SUM(total_amount) as total_from_orders
    FROM {{ ref('fct_orders') }}
    WHERE order_status = 'completed'
),

revenue_totals AS (
    SELECT SUM(revenue) as total_from_revenue
    FROM {{ ref('fct_revenue') }}
)

SELECT
    order_totals.total_from_orders,
    revenue_totals.total_from_revenue,
    ABS(order_totals.total_from_orders - revenue_totals.total_from_revenue) as difference
FROM order_totals
CROSS JOIN revenue_totals
WHERE ABS(order_totals.total_from_orders - revenue_totals.total_from_revenue) > 0.01
```

```sql
-- tests/assert_no_duplicate_customers.sql
-- Test for duplicate customers across systems

SELECT
    customer_email,
    COUNT(*) as duplicate_count
FROM {{ ref('dim_customers') }}
GROUP BY customer_email
HAVING COUNT(*) > 1
```

### Macro for Automated Testing

```sql
-- macros/test_column_distribution.sql
{% macro test_column_distribution(model, column, expected_distribution) %}

WITH distribution AS (
    SELECT
        {{ column }},
        COUNT(*) as count,
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
    FROM {{ model }}
    GROUP BY {{ column }}
)

SELECT
    {{ column }},
    percentage,
    {{ expected_distribution[column] }} as expected_percentage,
    ABS(percentage - {{ expected_distribution[column] }}) as difference
FROM distribution
WHERE ABS(percentage - {{ expected_distribution[column] }}) > 5

{% endmacro %}
```

## LookML CI/CD

### LookML Validation

```yaml
# .github/workflows/lookml_ci.yml
name: LookML CI/CD

on:
  pull_request:
    branches: [main]
    paths:
      - 'lookml/**'

jobs:
  validate:
    name: Validate LookML
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Looker SDK
        run: pip install looker-sdk

      - name: Validate LookML syntax
        run: |
          python scripts/validate_lookml.py \
            --project lookml \
            --api-url ${{ secrets.LOOKER_API_URL }} \
            --client-id ${{ secrets.LOOKER_CLIENT_ID }} \
            --client-secret ${{ secrets.LOOKER_CLIENT_SECRET }}

      - name: Run LookML tests
        run: |
          python scripts/run_lookml_tests.py \
            --project lookml

      - name: Check content validation
        run: |
          python scripts/validate_content.py \
            --project lookml

      - name: Check SQL validation
        run: |
          python scripts/validate_sql.py \
            --project lookml \
            --connection production

  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: validate
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Deploy LookML
        run: |
          python scripts/deploy_lookml.py \
            --project lookml \
            --environment production
```

### LookML Validation Script

```python
# scripts/validate_lookml.py
import looker_sdk
from looker_sdk import models40 as models
import sys

def validate_lookml(project_name: str):
    """Validate LookML project"""

    sdk = looker_sdk.init40()

    # Validate project
    try:
        validation = sdk.validate_project(project_id=project_name)

        if validation.errors:
            print(f"❌ LookML Validation Errors:")
            for error in validation.errors:
                print(f"  - {error.message}")
                print(f"    File: {error.file_path}")
                print(f"    Line: {error.line_number}")
            return False

        print("✅ LookML validation passed")

    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return False

    # Run content validation
    try:
        content_validation = sdk.content_validation()

        if content_validation.content_with_errors:
            print(f"❌ Content Validation Errors:")
            for content in content_validation.content_with_errors:
                print(f"  - {content.name}: {content.errors}")
            return False

        print("✅ Content validation passed")

    except Exception as e:
        print(f"❌ Content validation failed: {str(e)}")
        return False

    # Check SQL validation
    try:
        # Get all explores
        explores = sdk.all_lookml_models()

        for model in explores:
            for explore in model.explores:
                # Run SQL validation for each explore
                sql_query = sdk.create_sql_query(
                    models.WriteSqlQuery(
                        connection="production",
                        sql=f"SELECT * FROM {explore.name} LIMIT 1"
                    )
                )

                result = sdk.run_sql_query(sql_query.slug, "json")

                if "error" in result:
                    print(f"❌ SQL error in explore {explore.name}")
                    return False

        print("✅ SQL validation passed")

    except Exception as e:
        print(f"❌ SQL validation failed: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    project = sys.argv[1] if len(sys.argv) > 1 else "analytics"
    success = validate_lookml(project)
    sys.exit(0 if success else 1)
```

## Power BI CI/CD

### Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - power_bi/**

pool:
  vmImage: 'windows-latest'

variables:
  - group: PowerBI-Variables

stages:
  - stage: Validate
    displayName: 'Validate Power BI Files'
    jobs:
      - job: ValidatePBIX
        displayName: 'Validate PBIX Files'
        steps:
          - task: PowerShell@2
            displayName: 'Install Power BI PowerShell Module'
            inputs:
              targetType: 'inline'
              script: |
                Install-Module -Name MicrosoftPowerBIMgmt -Force -Scope CurrentUser

          - task: PowerShell@2
            displayName: 'Validate PBIX Files'
            inputs:
              targetType: 'filePath'
              filePath: 'scripts/validate_pbix.ps1'
              arguments: '-Path "power_bi/reports"'

          - task: PowerShell@2
            displayName: 'Check DAX Syntax'
            inputs:
              targetType: 'filePath'
              filePath: 'scripts/validate_dax.ps1'

  - stage: Test
    displayName: 'Test Power BI Reports'
    dependsOn: Validate
    jobs:
      - job: TestReports
        displayName: 'Test Report Logic'
        steps:
          - task: PowerShell@2
            displayName: 'Run DAX Tests'
            inputs:
              targetType: 'filePath'
              filePath: 'scripts/test_dax_measures.ps1'

          - task: PowerShell@2
            displayName: 'Validate Data Refresh'
            inputs:
              targetType: 'filePath'
              filePath: 'scripts/test_data_refresh.ps1'

  - stage: Deploy
    displayName: 'Deploy to Power BI Service'
    dependsOn: Test
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployProduction
        displayName: 'Deploy to Production'
        environment: 'Production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: PowerShell@2
                  displayName: 'Connect to Power BI'
                  inputs:
                    targetType: 'inline'
                    script: |
                      $credential = New-Object -TypeName System.Management.Automation.PSCredential `
                        -ArgumentList $(PowerBI-ServicePrincipal), $(ConvertTo-SecureString -String $(PowerBI-Secret) -AsPlainText -Force)
                      Connect-PowerBIServiceAccount -ServicePrincipal -Credential $credential -TenantId $(PowerBI-TenantId)

                - task: PowerShell@2
                  displayName: 'Deploy Reports'
                  inputs:
                    targetType: 'filePath'
                    filePath: 'scripts/deploy_power_bi.ps1'
                    arguments: '-WorkspaceName "Production" -Path "power_bi/reports"'

                - task: PowerShell@2
                  displayName: 'Update Dataset Connections'
                  inputs:
                    targetType: 'inline'
                    script: |
                      # Update datasource credentials
                      $datasets = Get-PowerBIDataset -WorkspaceId $(PowerBI-WorkspaceId)
                      foreach ($dataset in $datasets) {
                        Update-PowerBIDatasetDatasource -DatasetId $dataset.Id `
                          -DatasourceId $(Datasource-Id) `
                          -UpdateDetails @{
                            connectionDetails = @{
                              server = "$(SQL-Server)"
                              database = "$(SQL-Database)"
                            }
                          }
                      }

                - task: PowerShell@2
                  displayName: 'Trigger Data Refresh'
                  inputs:
                    targetType: 'inline'
                    script: |
                      $datasets = Get-PowerBIDataset -WorkspaceId $(PowerBI-WorkspaceId)
                      foreach ($dataset in $datasets) {
                        Invoke-PowerBIDatasetRefresh -DatasetId $dataset.Id
                      }
```

### Power BI Validation Script

```powershell
# scripts/validate_pbix.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$Path
)

# Import required modules
Import-Module MicrosoftPowerBIMgmt

Write-Host "Validating Power BI files in: $Path"

# Get all PBIX files
$pbixFiles = Get-ChildItem -Path $Path -Filter "*.pbix" -Recurse

foreach ($file in $pbixFiles) {
    Write-Host "Validating: $($file.Name)"

    # Extract PBIX (it's a ZIP file)
    $tempDir = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $tempDir | Out-Null

    try {
        # Extract PBIX contents
        Expand-Archive -Path $file.FullName -DestinationPath $tempDir -Force

        # Validate DataModel
        $dataModelPath = Join-Path $tempDir "DataModel"
        if (Test-Path $dataModelPath) {
            Write-Host "✓ DataModel found"

            # Check for common issues
            $layoutPath = Join-Path $tempDir "Report/Layout"
            if (Test-Path $layoutPath) {
                $layout = Get-Content $layoutPath -Raw | ConvertFrom-Json

                # Check for excessive visuals
                $visualCount = $layout.sections | ForEach-Object { $_.visualContainers.Count } | Measure-Object -Sum
                if ($visualCount.Sum -gt 50) {
                    Write-Warning "High visual count ($($visualCount.Sum)). Consider optimization."
                }
            }
        }
        else {
            Write-Error "DataModel not found in $($file.Name)"
            exit 1
        }

        # Validate measures
        $measuresPath = Join-Path $tempDir "DataModelSchema"
        if (Test-Path $measuresPath) {
            # Check DAX syntax (basic validation)
            $measures = Get-Content $measuresPath -Raw
            if ($measures -match "CALCULATE\s*\(\s*\)") {
                Write-Warning "Empty CALCULATE found in $($file.Name)"
            }
        }

        Write-Host "✓ Validation passed for $($file.Name)"
    }
    finally {
        # Cleanup
        Remove-Item -Path $tempDir -Recurse -Force
    }
}

Write-Host "All validations completed successfully"
```

## Monitoring and Observability

### dbt Cloud Monitoring

```python
# scripts/monitor_dbt_jobs.py
import requests
from datetime import datetime, timedelta
import json

class DBTCloudMonitor:
    """Monitor dbt Cloud jobs and send alerts"""

    def __init__(self, account_id, api_token):
        self.account_id = account_id
        self.api_token = api_token
        self.base_url = "https://cloud.getdbt.com/api/v2"
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }

    def get_recent_runs(self, job_id, hours=24):
        """Get recent job runs"""
        url = f"{self.base_url}/accounts/{self.account_id}/runs/"
        params = {
            "job_definition_id": job_id,
            "include_related": '["job", "trigger", "run_steps"]'
        }

        response = requests.get(url, headers=self.headers, params=params)
        runs = response.json()["data"]

        # Filter by time
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_runs = [
            run for run in runs
            if datetime.fromisoformat(run["created_at"].replace("Z", "+00:00")) > cutoff
        ]

        return recent_runs

    def check_job_health(self, job_id):
        """Check job health metrics"""
        runs = self.get_recent_runs(job_id, hours=24)

        if not runs:
            return {"status": "no_data", "message": "No recent runs"}

        # Calculate metrics
        total_runs = len(runs)
        failed_runs = sum(1 for run in runs if run["status"] == 10)  # 10 = Error
        success_rate = ((total_runs - failed_runs) / total_runs) * 100

        # Average duration
        durations = [
            run["duration_humanized"] for run in runs
            if run["status"] == 10  # Success
        ]

        latest_run = runs[0]

        return {
            "status": "healthy" if success_rate >= 95 else "degraded",
            "success_rate": success_rate,
            "total_runs": total_runs,
            "failed_runs": failed_runs,
            "latest_run_status": latest_run["status"],
            "latest_run_duration": latest_run.get("duration_humanized", "N/A")
        }

    def get_model_execution_times(self, run_id):
        """Get execution times for each model"""
        url = f"{self.base_url}/accounts/{self.account_id}/runs/{run_id}/artifacts/"
        response = requests.get(url, headers=self.headers)

        run_results = response.json()

        model_times = []
        for result in run_results.get("results", []):
            model_times.append({
                "model": result["unique_id"],
                "status": result["status"],
                "execution_time": result["execution_time"],
                "rows_affected": result.get("adapter_response", {}).get("rows_affected", 0)
            })

        return sorted(model_times, key=lambda x: x["execution_time"], reverse=True)

    def detect_anomalies(self, job_id):
        """Detect anomalies in job performance"""
        runs = self.get_recent_runs(job_id, hours=168)  # 7 days

        if len(runs) < 10:
            return {"status": "insufficient_data"}

        # Calculate baseline
        durations = [run.get("duration", 0) for run in runs if run.get("duration")]
        avg_duration = sum(durations) / len(durations)
        std_duration = (sum((x - avg_duration) ** 2 for x in durations) / len(durations)) ** 0.5

        # Check latest run
        latest_duration = runs[0].get("duration", 0)
        z_score = (latest_duration - avg_duration) / std_duration if std_duration > 0 else 0

        anomalies = []
        if abs(z_score) > 2:
            anomalies.append({
                "type": "duration_anomaly",
                "message": f"Duration {latest_duration}s is {abs(z_score):.1f} std devs from mean",
                "severity": "high" if abs(z_score) > 3 else "medium"
            })

        return {
            "status": "anomalies_detected" if anomalies else "normal",
            "anomalies": anomalies,
            "baseline_duration": avg_duration,
            "latest_duration": latest_duration
        }
```

### Data Quality Monitoring

```python
# scripts/data_quality_monitor.py
from datetime import datetime
import pandas as pd

class DataQualityMonitor:
    """Monitor data quality metrics over time"""

    def __init__(self, connection):
        self.connection = connection

    def check_freshness(self, table, timestamp_column, max_age_hours=24):
        """Check data freshness"""
        query = f"""
        SELECT
            MAX({timestamp_column}) as latest_timestamp,
            TIMESTAMPDIFF(HOUR, MAX({timestamp_column}), CURRENT_TIMESTAMP()) as age_hours
        FROM {table}
        """

        result = pd.read_sql(query, self.connection)
        age_hours = result['age_hours'].iloc[0]

        return {
            "table": table,
            "latest_timestamp": result['latest_timestamp'].iloc[0],
            "age_hours": age_hours,
            "status": "ok" if age_hours < max_age_hours else "stale"
        }

    def check_completeness(self, table, required_columns):
        """Check for null values in required columns"""
        issues = []

        for column in required_columns:
            query = f"""
            SELECT
                COUNT(*) as total_rows,
                SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) as null_count
            FROM {table}
            """

            result = pd.read_sql(query, self.connection)
            null_pct = (result['null_count'].iloc[0] / result['total_rows'].iloc[0]) * 100

            if null_pct > 0:
                issues.append({
                    "column": column,
                    "null_percentage": null_pct,
                    "severity": "high" if null_pct > 5 else "low"
                })

        return {
            "table": table,
            "status": "ok" if not issues else "issues_found",
            "issues": issues
        }

    def check_uniqueness(self, table, key_columns):
        """Check for duplicate records"""
        key_columns_str = ", ".join(key_columns)

        query = f"""
        SELECT
            {key_columns_str},
            COUNT(*) as duplicate_count
        FROM {table}
        GROUP BY {key_columns_str}
        HAVING COUNT(*) > 1
        """

        duplicates = pd.read_sql(query, self.connection)

        return {
            "table": table,
            "key_columns": key_columns,
            "duplicate_count": len(duplicates),
            "status": "ok" if len(duplicates) == 0 else "duplicates_found"
        }

    def check_distribution_drift(self, table, column, baseline_distribution):
        """Check for distribution drift"""
        query = f"""
        SELECT
            {column},
            COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
        FROM {table}
        WHERE created_at >= CURRENT_DATE - INTERVAL 1 DAY
        GROUP BY {column}
        """

        current = pd.read_sql(query, self.connection)

        drift_detected = []
        for _, row in current.iterrows():
            value = row[column]
            current_pct = row['percentage']
            baseline_pct = baseline_distribution.get(value, 0)

            if abs(current_pct - baseline_pct) > 10:  # 10% threshold
                drift_detected.append({
                    "value": value,
                    "current_percentage": current_pct,
                    "baseline_percentage": baseline_pct,
                    "drift": current_pct - baseline_pct
                })

        return {
            "table": table,
            "column": column,
            "status": "ok" if not drift_detected else "drift_detected",
            "drifts": drift_detected
        }
```

## Best Practices Summary

### Version Control
- ✅ All BI code in Git
- ✅ Meaningful commit messages
- ✅ Branch protection rules
- ✅ Code review required
- ✅ Squash merge for clean history

### Testing
- ✅ Schema tests for all models
- ✅ Custom business logic tests
- ✅ Performance benchmarks
- ✅ Data quality checks
- ✅ Integration tests

### CI/CD
- ✅ Automated testing on PR
- ✅ Slim CI for efficiency
- ✅ Staging environment
- ✅ Production deployment gating
- ✅ Rollback procedures

### Monitoring
- ✅ Job execution monitoring
- ✅ Data quality alerts
- ✅ Performance tracking
- ✅ Cost monitoring
- ✅ Usage analytics

## Conclusion

BI DevOps brings reliability, quality, and speed to analytics engineering. By implementing version control, automated testing, CI/CD pipelines, and monitoring, teams can deliver trusted analytics at scale while maintaining code quality and reducing manual errors.
