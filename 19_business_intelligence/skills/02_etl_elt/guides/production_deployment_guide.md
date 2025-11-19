# Production Deployment Guide

## Environment Strategy

### Development
- Personal schemas: `dbt_firstname_lastname`
- Small data samples
- Fast iteration

### Staging
- Production-like environment
- Subset of production data
- Pre-deployment testing

### Production
- Shared analytics schema
- Full data volume
- Monitored and alerted

## dbt Cloud Deployment

### 1. Configure Environments
```yaml
# Development
target: dev
schema: dbt_{{ env_var('USER') }}
threads: 4

# Production
target: prod
schema: analytics
threads: 16
```

### 2. Create Jobs
**Daily Production Run**:
- Schedule: `0 2 * * *`
- Commands:
  - `dbt deps`
  - `dbt source freshness`
  - `dbt snapshot`
  - `dbt run`
  - `dbt test`

**CI Job** (on PR):
- Commands:
  - `dbt run --models state:modified+ --defer`
  - `dbt test --models state:modified+`

### 3. Set Up Alerts
- Email on job failure
- Slack notifications
- PagerDuty for critical jobs

## Self-Hosted Airflow Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  airflow-webserver:
    image: apache/airflow:2.7.1
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    ports:
      - "8080:8080"
    command: webserver

  airflow-scheduler:
    image: apache/airflow:2.7.1
    command: scheduler

  airflow-worker:
    image: apache/airflow:2.7.1
    command: celery worker
```

## Deployment Checklist

- [ ] All tests passing in staging
- [ ] Data quality checks configured
- [ ] Monitoring and alerting set up
- [ ] Secrets managed securely
- [ ] Documentation updated
- [ ] Rollback plan documented
- [ ] Team notified of deployment

## Rollback Procedures

1. **Immediate Rollback**
   ```bash
   # Revert to previous dbt version
   git revert HEAD
   dbt run --full-refresh
   ```

2. **Data Restore**
   ```sql
   -- Use time travel (Snowflake)
   CREATE TABLE analytics.orders AS
   SELECT * FROM analytics.orders
   AT(TIMESTAMP => '2024-01-15 10:00:00');
   ```

## Resources

- **dbt Cloud Docs**: https://docs.getdbt.com/docs/cloud/about-cloud
- **Airflow Production**: https://airflow.apache.org/docs/apache-airflow/stable/production-deployment.html
