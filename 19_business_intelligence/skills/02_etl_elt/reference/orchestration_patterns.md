# Orchestration Patterns Reference

## DAG Design Patterns

### Pattern 1: Linear Pipeline
Simple sequential execution.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

with DAG(
    'linear_pipeline',
    default_args={'owner': 'data_team'},
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
) as dag:

    extract = PythonOperator(task_id='extract', python_callable=extract_data)
    transform = PythonOperator(task_id='transform', python_callable=transform_data)
    load = PythonOperator(task_id='load', python_callable=load_data)
    validate = PythonOperator(task_id='validate', python_callable=validate_data)

    extract >> transform >> load >> validate
```

### Pattern 2: Fan-Out/Fan-In
Parallel processing with synchronization.

```python
with DAG('fan_out_fan_in', ...) as dag:

    start = DummyOperator(task_id='start')

    # Fan-out: Process multiple sources in parallel
    extract_postgres = PythonOperator(task_id='extract_postgres', ...)
    extract_mongodb = PythonOperator(task_id='extract_mongodb', ...)
    extract_api = PythonOperator(task_id='extract_api', ...)

    # Fan-in: Wait for all extracts to complete
    merge = PythonOperator(task_id='merge_data', ...)

    # Continue processing
    transform = PythonOperator(task_id='transform', ...)
    load = PythonOperator(task_id='load', ...)

    start >> [extract_postgres, extract_mongodb, extract_api] >> merge >> transform >> load
```

### Pattern 3: Conditional Branching
Execute different paths based on conditions.

```python
from airflow.operators.python import BranchPythonOperator

def decide_branch(**context):
    """Decide which branch to take"""
    execution_date = context['execution_date']

    # Full refresh on first day of month
    if execution_date.day == 1:
        return 'full_refresh'
    else:
        return 'incremental_load'

with DAG('conditional_branch', ...) as dag:

    check_date = BranchPythonOperator(
        task_id='check_date',
        python_callable=decide_branch
    )

    full_refresh = PythonOperator(task_id='full_refresh', ...)
    incremental = PythonOperator(task_id='incremental_load', ...)

    # Both paths converge
    validate = PythonOperator(
        task_id='validate',
        trigger_rule='none_failed_min_one_success',
        ...
    )

    check_date >> [full_refresh, incremental] >> validate
```

### Pattern 4: Dynamic Task Generation
Generate tasks at runtime.

```python
from airflow.decorators import dag, task

@dag(schedule_interval='@daily', start_date=datetime(2024, 1, 1))
def dynamic_tasks():

    @task
    def get_tables():
        """Return list of tables to process"""
        return ['orders', 'customers', 'products', 'inventory']

    @task
    def process_table(table_name: str):
        """Process a single table"""
        print(f"Processing {table_name}")
        # Run dbt model
        import subprocess
        subprocess.run(['dbt', 'run', '-m', f'stg_{table_name}'])

    @task
    def aggregate_results(results: list):
        """Combine results from all tables"""
        print(f"Processed {len(results)} tables")

    # Dynamic task mapping
    tables = get_tables()
    results = process_table.expand(table_name=tables)
    aggregate_results(results)

dag = dynamic_tasks()
```

### Pattern 5: Sensor-Based Triggering
Wait for external events.

```python
from airflow.sensors.s3 import S3KeySensor
from airflow.sensors.external_task import ExternalTaskSensor

with DAG('sensor_triggered', ...) as dag:

    # Wait for S3 file
    wait_for_file = S3KeySensor(
        task_id='wait_for_file',
        bucket_name='data-bucket',
        bucket_key='uploads/{{ ds }}/data.csv',
        timeout=3600,
        poke_interval=300,  # Check every 5 minutes
        mode='reschedule'  # Don't block worker
    )

    # Wait for upstream DAG
    wait_for_upstream = ExternalTaskSensor(
        task_id='wait_for_data_ingestion',
        external_dag_id='data_ingestion',
        external_task_id='ingestion_complete',
        mode='reschedule'
    )

    process = PythonOperator(task_id='process', ...)

    [wait_for_file, wait_for_upstream] >> process
```

## Advanced Orchestration

### Pattern 6: Sub-DAG Pattern
Reusable DAG components.

```python
from airflow.operators.subdag import SubDagOperator
from airflow.utils.task_group import TaskGroup

# Modern approach: TaskGroup (preferred over SubDAG)
with DAG('main_dag', ...) as dag:

    with TaskGroup('data_quality_checks') as quality_checks:
        check_nulls = PythonOperator(task_id='check_nulls', ...)
        check_duplicates = PythonOperator(task_id='check_duplicates', ...)
        check_referential = PythonOperator(task_id='check_referential', ...)

        check_nulls >> check_duplicates >> check_referential

    extract = PythonOperator(task_id='extract', ...)
    load = PythonOperator(task_id='load', ...)

    extract >> quality_checks >> load
```

### Pattern 7: dbt + Airflow Integration
```python
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.operators.bash import BashOperator

with DAG('dbt_pipeline', ...) as dag:

    # Install dbt packages
    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command='cd /dbt && dbt deps'
    )

    # Run source freshness check
    dbt_freshness = BashOperator(
        task_id='dbt_source_freshness',
        bash_command='cd /dbt && dbt source freshness'
    )

    # Run snapshots (SCD Type 2)
    dbt_snapshot = BashOperator(
        task_id='dbt_snapshot',
        bash_command='cd /dbt && dbt snapshot'
    )

    # Run models by layer
    dbt_run_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command='cd /dbt && dbt run --models staging.*'
    )

    dbt_run_intermediate = BashOperator(
        task_id='dbt_run_intermediate',
        bash_command='cd /dbt && dbt run --models intermediate.*'
    )

    dbt_run_marts = BashOperator(
        task_id='dbt_run_marts',
        bash_command='cd /dbt && dbt run --models marts.*'
    )

    # Test data quality
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /dbt && dbt test'
    )

    # Generate documentation
    dbt_docs = BashOperator(
        task_id='dbt_docs_generate',
        bash_command='cd /dbt && dbt docs generate'
    )

    dbt_deps >> dbt_freshness >> dbt_snapshot
    dbt_snapshot >> dbt_run_staging >> dbt_run_intermediate >> dbt_run_marts
    dbt_run_marts >> dbt_test >> dbt_docs
```

### Pattern 8: Multi-DAG Coordination
```python
# DAG 1: Data Ingestion
with DAG('01_data_ingestion', ...) as ingestion_dag:
    ingest_orders = PythonOperator(...)
    ingest_customers = PythonOperator(...)
    ingestion_complete = DummyOperator(task_id='ingestion_complete')

    [ingest_orders, ingest_customers] >> ingestion_complete

# DAG 2: Data Transformation (depends on DAG 1)
with DAG('02_data_transformation', ...) as transform_dag:
    wait_for_ingestion = ExternalTaskSensor(
        task_id='wait_for_ingestion',
        external_dag_id='01_data_ingestion',
        external_task_id='ingestion_complete'
    )

    run_dbt = BashOperator(task_id='run_dbt', ...)
    transform_complete = DummyOperator(task_id='transform_complete')

    wait_for_ingestion >> run_dbt >> transform_complete

# DAG 3: Data Quality (depends on DAG 2)
with DAG('03_data_quality', ...) as quality_dag:
    wait_for_transformation = ExternalTaskSensor(
        task_id='wait_for_transformation',
        external_dag_id='02_data_transformation',
        external_task_id='transform_complete'
    )

    run_quality_checks = PythonOperator(...)

    wait_for_transformation >> run_quality_checks
```

## Dependency Management

### XCom for Data Passing
```python
@task
def extract_data():
    """Extract and return metadata"""
    records_extracted = 1000
    extraction_time = datetime.now()

    # Return data to XCom
    return {
        'record_count': records_extracted,
        'extraction_time': extraction_time.isoformat()
    }

@task
def transform_data(metadata: dict):
    """Use metadata from previous task"""
    print(f"Transforming {metadata['record_count']} records")
    print(f"Extracted at {metadata['extraction_time']}")

    # Transform logic here
    return {'transformed_count': metadata['record_count']}

@task
def load_data(transform_result: dict):
    """Load transformed data"""
    print(f"Loading {transform_result['transformed_count']} records")

# Chain tasks with data passing
extract_result = extract_data()
transform_result = transform_data(extract_result)
load_data(transform_result)
```

### Trigger Rules
```python
from airflow.utils.trigger_rule import TriggerRule

with DAG('trigger_rules_example', ...) as dag:

    start = DummyOperator(task_id='start')

    task_a = PythonOperator(task_id='task_a', ...)
    task_b = PythonOperator(task_id='task_b', ...)
    task_c = PythonOperator(task_id='task_c', ...)

    # Run only if ALL parents succeeded (default)
    all_success = PythonOperator(
        task_id='all_success',
        trigger_rule=TriggerRule.ALL_SUCCESS,
        ...
    )

    # Run if ANY parent succeeded
    any_success = PythonOperator(
        task_id='any_success',
        trigger_rule=TriggerRule.ONE_SUCCESS,
        ...
    )

    # Run if at least one parent failed
    one_failed = PythonOperator(
        task_id='send_alert',
        trigger_rule=TriggerRule.ONE_FAILED,
        ...
    )

    # Always run (cleanup, notifications)
    always_run = PythonOperator(
        task_id='cleanup',
        trigger_rule=TriggerRule.ALL_DONE,
        ...
    )

    start >> [task_a, task_b, task_c]
    [task_a, task_b, task_c] >> all_success
    [task_a, task_b, task_c] >> any_success
    [task_a, task_b, task_c] >> one_failed
    [task_a, task_b, task_c] >> always_run
```

## Scheduling Strategies

### Cron-Based Scheduling
```python
# Every day at 2 AM
schedule_interval='0 2 * * *'

# Every Monday at 3 AM
schedule_interval='0 3 * * 1'

# Every hour
schedule_interval='@hourly'

# Every 30 minutes
schedule_interval='*/30 * * * *'

# First day of month
schedule_interval='0 0 1 * *'
```

### Data-Interval Scheduling
```python
with DAG(
    'data_interval_dag',
    # Process yesterday's data every day at 2 AM
    schedule_interval='0 2 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=True,  # Backfill historical runs
) as dag:

    process_data = PythonOperator(
        task_id='process_data',
        python_callable=lambda **ctx: process_for_date(ctx['ds']),  # ds = YYYY-MM-DD
    )
```

### Dataset-Based Scheduling (Airflow 2.4+)
```python
from airflow.datasets import Dataset

# Define datasets
orders_dataset = Dataset('postgres://warehouse/orders')
customers_dataset = Dataset('postgres://warehouse/customers')

# Producer DAG
with DAG('data_ingestion', schedule_interval='@hourly') as dag:
    ingest = PythonOperator(
        task_id='ingest',
        outlets=[orders_dataset, customers_dataset],  # Produces these datasets
        ...
    )

# Consumer DAG (runs when datasets are updated)
with DAG(
    'analytics',
    schedule=[orders_dataset, customers_dataset],  # Triggered by datasets
) as dag:
    analyze = PythonOperator(task_id='analyze', ...)
```

## Error Handling & SLAs

### Task-Level Error Handling
```python
def handle_failure(context):
    """Custom failure handler"""
    task = context['task_instance']
    print(f"Task {task.task_id} failed!")
    send_slack_alert(f"Pipeline failed: {task.dag_id}")

default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'on_failure_callback': handle_failure,
    'email_on_failure': True,
    'email': ['data-team@company.com'],
}
```

### SLA Management
```python
def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """Alert on SLA miss"""
    print(f"SLA missed for {dag.dag_id}")
    print(f"Tasks: {[t.task_id for t in task_list]}")
    send_pagerduty_alert(f"Critical SLA missed: {dag.dag_id}")

with DAG(
    'critical_pipeline',
    default_args={
        'sla': timedelta(hours=2),  # Task must complete within 2 hours
    },
    sla_miss_callback=sla_miss_callback,
    ...
) as dag:

    critical_task = PythonOperator(
        task_id='critical_task',
        sla=timedelta(minutes=30),  # Override: 30-minute SLA
        ...
    )
```

## Resource Management

### Pools
```python
# Define pool in Airflow UI or via CLI
# airflow pools set heavy_compute 5 "Heavy computation tasks"

with DAG('resource_managed', ...) as dag:

    # Limit concurrent heavy tasks
    heavy_task_1 = PythonOperator(
        task_id='heavy_task_1',
        pool='heavy_compute',
        pool_slots=2,  # Uses 2 of 5 available slots
        ...
    )

    heavy_task_2 = PythonOperator(
        task_id='heavy_task_2',
        pool='heavy_compute',
        pool_slots=2,
        ...
    )
```

### Priority & Queues
```python
with DAG('prioritized', ...) as dag:

    # High priority task
    critical = PythonOperator(
        task_id='critical',
        priority_weight=10,  # Higher runs first
        queue='high_priority',  # Specific worker queue
        ...
    )

    # Normal priority
    regular = PythonOperator(
        task_id='regular',
        priority_weight=5,
        queue='default',
        ...
    )
```

## Monitoring & Observability

### Custom Metrics
```python
from airflow.providers.statsd.stats import Stats

stats = Stats()

def monitored_task(**context):
    """Task with custom metrics"""
    start_time = time.time()

    try:
        # Your logic
        records_processed = process_data()

        # Record metrics
        stats.incr('pipeline.success')
        stats.gauge('pipeline.records_processed', records_processed)
        stats.timing('pipeline.duration', time.time() - start_time)

    except Exception as e:
        stats.incr('pipeline.failure')
        raise
```

### Logging Best Practices
```python
import logging

def well_logged_task(**context):
    """Task with comprehensive logging"""
    logger = logging.getLogger(__name__)

    execution_date = context['execution_date']
    logger.info(f"Starting processing for {execution_date}")

    try:
        # Extract
        logger.info("Extracting data from source")
        data = extract_data()
        logger.info(f"Extracted {len(data)} records")

        # Transform
        logger.info("Transforming data")
        transformed = transform_data(data)
        logger.info(f"Transformed to {len(transformed)} records")

        # Load
        logger.info("Loading to warehouse")
        load_data(transformed)
        logger.info("Load completed successfully")

        return {'status': 'success', 'records': len(transformed)}

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise
```

## Testing DAGs

### Unit Testing
```python
import pytest
from datetime import datetime
from airflow.models import DagBag

def test_dag_loaded():
    """Test that DAG loads without errors"""
    dagbag = DagBag()
    dag = dagbag.get_dag('my_dag')
    assert dag is not None
    assert len(dag.tasks) > 0

def test_dag_structure():
    """Test DAG structure"""
    dagbag = DagBag()
    dag = dagbag.get_dag('my_dag')

    # Check tasks exist
    assert 'extract' in dag.task_ids
    assert 'transform' in dag.task_ids
    assert 'load' in dag.task_ids

    # Check dependencies
    extract_task = dag.get_task('extract')
    transform_task = dag.get_task('transform')

    assert transform_task in extract_task.downstream_list

def test_task_execution():
    """Test individual task execution"""
    from airflow.models import TaskInstance
    from airflow import settings

    dag = DagBag().get_dag('my_dag')
    task = dag.get_task('extract')

    # Create task instance
    ti = TaskInstance(task=task, execution_date=datetime(2024, 1, 1))

    # Run task
    ti.run(ignore_ti_state=True)

    # Assert success
    assert ti.state == 'success'
```

## Best Practices

### Idempotency
```python
# ✅ Idempotent: Safe to re-run
def idempotent_load(**context):
    """Delete and reload pattern"""
    date = context['ds']

    # Delete existing data
    conn.execute(f"DELETE FROM table WHERE date = '{date}'")

    # Insert fresh data
    conn.execute(f"INSERT INTO table SELECT * FROM staging WHERE date = '{date}'")

# ❌ Not idempotent: Re-run causes duplicates
def non_idempotent_load(**context):
    """Append pattern without dedup"""
    conn.execute("INSERT INTO table SELECT * FROM staging")
```

### Modularity
```python
# ✅ Good: Reusable, testable functions
def extract_from_api(endpoint: str, params: dict) -> list:
    """Reusable extraction function"""
    response = requests.get(endpoint, params=params)
    return response.json()

def transform_records(records: list) -> list:
    """Reusable transformation"""
    return [transform_record(r) for r in records]

# Use in DAG
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_from_api,
    op_kwargs={'endpoint': 'https://api.example.com/data', 'params': {}}
)
```

## Resources

- **Airflow Best Practices**: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html
- **DAG Writing**: https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html
- **TaskFlow API**: https://airflow.apache.org/docs/apache-airflow/stable/concepts/taskflow.html
