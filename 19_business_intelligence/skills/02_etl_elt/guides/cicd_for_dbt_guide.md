# CI/CD for dbt: Complete Guide

## GitHub Actions CI/CD Pipeline

### Slim CI (Run Only Changed Models)
```yaml
# .github/workflows/dbt_ci.yml
name: dbt CI

on:
  pull_request:
    branches: [main]

jobs:
  dbt-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dbt
        run: |
          pip install dbt-snowflake==1.6.0

      - name: Install dbt packages
        run: dbt deps

      - name: Download production artifacts
        run: |
          # Download manifest.json from production
          aws s3 cp s3://dbt-artifacts/prod/manifest.json ./prod-manifest.json

      - name: Run dbt (modified models only)
        run: |
          dbt run \
            --models state:modified+ \
            --state ./ \
            --defer \
            --target ci
        env:
          DBT_SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          DBT_SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          DBT_SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}

      - name: Run dbt tests
        run: dbt test --models state:modified+

      - name: Comment PR with results
        uses: actions/github-script@v6
        if: always()
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('target/run_results.json'));
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `dbt CI Results: ${results.stats.passed} passed, ${results.stats.failed} failed`
            });
