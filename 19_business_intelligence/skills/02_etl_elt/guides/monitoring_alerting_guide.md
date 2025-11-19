# Monitoring & Alerting Guide

## What to Monitor

### Pipeline Health
- Job success/failure rates
- Execution time trends
- Data freshness
- Row counts and volumes
- Cost per run

### Data Quality
- Test pass rates
- Schema changes
- Anomaly detection
- Source-to-target reconciliation

### System Performance
- Warehouse utilization
- Query performance
- Concurrency limits
- Resource consumption

## Airflow Monitoring

### Task Metrics
```python
from airflow.providers.statsd.stats import Stats

stats = Stats()

def monitored_task():
    start = time.time()

    try:
        # Your logic
        result = process_data()

        stats.incr('pipeline.success')
        stats.gauge('pipeline.rows_processed', result['count'])
        stats.timing('pipeline.duration', time.time() - start)

    except Exception as e:
        stats.incr('pipeline.failure')
        raise
```

### Alerting
```python
def send_failure_alert(context):
    task = context['task_instance']

    slack_msg = f"""
    :red_circle: Pipeline Failed
    Task: {task.task_id}
    DAG: {task.dag_id}
    Log: {task.log_url}
    """

    slack.chat_postMessage(
        channel='#data-alerts',
        text=slack_msg
    )

default_args = {
    'on_failure_callback': send_failure_alert,
    'sla': timedelta(hours=2),
}
```

## dbt Monitoring

### run_results.json
```python
import json

with open('target/run_results.json') as f:
    results = json.load(f)

# Track execution times
for result in results['results']:
    model = result['unique_id']
    time = result['execution_time']
    print(f"{model}: {time}s")

# Alert on failures
failures = [r for r in results['results'] if r['status'] == 'error']
if failures:
    send_alert(f"{len(failures)} models failed")
```

### Elementary dbt Package
```yaml
# packages.yml
packages:
  - package: elementary-data/elementary
    version: 0.10.0

# Generates monitoring dashboard and alerts
```

## Data Quality Monitoring

### Track Test Results
```sql
-- Create monitoring table
CREATE TABLE dbt_test_results AS
SELECT
    test_name,
    model_name,
    status,
    failure_count,
    executed_at
FROM {{ ref('test_results_history') }}
```

### Alert on Quality Issues
```python
def check_data_quality():
    query = """
        SELECT COUNT(*) as failures
        FROM dbt_test_results
        WHERE status = 'fail'
        AND executed_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
    """

    failures = db.execute(query)[0]['failures']

    if failures > 0:
        send_alert(f"{failures} data quality tests failed")
```

## Cost Monitoring

### Snowflake
```sql
SELECT
    warehouse_name,
    SUM(credits_used) as total_credits,
    SUM(credits_used) * 3.00 as estimated_cost
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= CURRENT_DATE - 7
GROUP BY warehouse_name
HAVING total_credits > 100  -- Alert threshold
```

### BigQuery
```sql
SELECT
    user_email,
    SUM(total_bytes_billed) / 1099511627776 as tb_billed,
    SUM(total_bytes_billed) / 1099511627776 * 5 as cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY user_email
HAVING cost_usd > 100
```

## Dashboards

### Key Metrics to Track
- Pipeline success rate (target: >99%)
- Average execution time (trending)
- Data freshness (vs SLA)
- Test pass rate (target: >99%)
- Daily costs (trending)

### Tools
- **Grafana**: For metrics/logs
- **dbt Cloud**: Built-in run history
- **Elementary**: dbt-specific monitoring
- **Custom**: SQL dashboards in BI tool

## Best Practices

1. **Set Clear SLAs**: Define acceptable performance
2. **Alert Smartly**: Avoid alert fatigue
3. **Escalate Appropriately**: Critical vs warning
4. **Track Trends**: Monitor over time
5. **Document Runbooks**: How to respond to alerts

