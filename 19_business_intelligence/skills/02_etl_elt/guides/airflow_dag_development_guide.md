# Airflow DAG Development: Complete Guide

## Introduction

Apache Airflow is a platform to programmatically author, schedule, and monitor workflows. DAGs (Directed Acyclic Graphs) define the relationships and dependencies between tasks.

## DAG Basics

### Simple DAG Structure
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default arguments applied to all tasks
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'email': ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'example_etl_pipeline',
    default_args=default_args,
    description='Extract, transform, and load customer data',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'customers'],
) as dag:

    # Define tasks
    def extract_data(**context):
        print(f"Extracting data for {context['ds']}")
        # Your extraction logic
        return {'records_extracted': 1000}

    extract = PythonOperator(
        task_id='extract_customers',
        python_callable=extract_data,
    )

    transform = BashOperator(
        task_id='transform_customers',
        bash_command='dbt run --models stg_customers',
    )

    load = PythonOperator(
        task_id='load_to_warehouse',
        python_callable=lambda: print("Loading data"),
    )

    # Define dependencies
    extract >> transform >> load
```

## TaskFlow API (Modern Approach)

### Using Decorators
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'modern'],
)
def customer_etl_pipeline():
    """
    Modern ETL pipeline using TaskFlow API
    """

    @task
    def extract_customers():
        """Extract customer data from source"""
        import pandas as pd

        # Simulate extraction
        customers = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com']
        })

        return customers.to_dict('records')

    @task
    def transform_customers(customers: list) -> list:
        """Clean and transform customer data"""
        transformed = []
        for customer in customers:
            transformed.append({
                'customer_id': customer['id'],
                'full_name': customer['name'].upper(),
                'email': customer['email'].lower(),
                'created_at': datetime.now().isoformat()
            })
        return transformed

    @task
    def load_customers(customers: list):
        """Load customers to warehouse"""
        print(f"Loading {len(customers)} customers")
        # Your load logic here
        return len(customers)

    # Define workflow
    raw_customers = extract_customers()
    cleaned_customers = transform_customers(raw_customers)
    load_count = load_customers(cleaned_customers)

# Instantiate the DAG
dag = customer_etl_pipeline()
```

## Advanced DAG Patterns

### Dynamic Task Generation
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule_interval='@daily', start_date=datetime(2024, 1, 1))
def process_multiple_tables():

    @task
    def get_tables() -> list:
        """Get list of tables to process"""
        return ['customers', 'orders', 'products', 'inventory']

    @task
    def process_table(table_name: str) -> dict:
        """Process a single table"""
        print(f"Processing table: {table_name}")

        # Simulate processing
        import time
        time.sleep(2)

        return {
            'table': table_name,
            'rows_processed': 1000,
            'status': 'success'
        }

    @task
    def summarize_results(results: list) -> None:
        """Summarize all processing results"""
        total_rows = sum(r['rows_processed'] for r in results)
        print(f"Total rows processed: {total_rows}")
        print(f"Tables processed: {len(results)}")

    # Dynamic task mapping
    tables = get_tables()
    results = process_table.expand(table_name=tables)
    summarize_results(results)

dag = process_multiple_tables()
```

### Conditional Branching
```python
from airflow import DAG
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime

with DAG('conditional_pipeline', start_date=datetime(2024, 1, 1)) as dag:

    def decide_which_path(**context):
        """Decide processing path based on execution date"""
        execution_date = context['execution_date']

        # Full refresh on first day of month
        if execution_date.day == 1:
            return 'full_refresh'
        else:
            return 'incremental_load'

    start = DummyOperator(task_id='start')

    branch = BranchPythonOperator(
        task_id='branch_decision',
        python_callable=decide_which_path,
    )

    full_refresh = PythonOperator(
        task_id='full_refresh',
        python_callable=lambda: print("Running full refresh"),
    )

    incremental = PythonOperator(
        task_id='incremental_load',
        python_callable=lambda: print("Running incremental load"),
    )

    # Both paths converge here
    join = DummyOperator(
        task_id='join',
        trigger_rule='none_failed_min_one_success',
    )

    validate = PythonOperator(
        task_id='validate',
        python_callable=lambda: print("Validating data"),
    )

    start >> branch >> [full_refresh, incremental] >> join >> validate
```

### Sensor-Based Workflows
```python
from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

with DAG(
    'sensor_based_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@hourly',
) as dag:

    # Wait for S3 file
    wait_for_file = S3KeySensor(
        task_id='wait_for_data_file',
        bucket_name='data-bucket',
        bucket_key='uploads/{{ ds }}/data.csv',
        aws_conn_id='aws_default',
        timeout=3600,  # 1 hour max wait
        poke_interval=60,  # Check every minute
        mode='reschedule',  # Don't block worker while waiting
    )

    process = PythonOperator(
        task_id='process_file',
        python_callable=lambda: print("Processing file"),
    )

    wait_for_file >> process
```

## Error Handling

### Retry Configuration
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def flaky_operation():
    """Operation that might fail"""
    import random
    if random.random() < 0.5:
        raise Exception("Random failure!")
    print("Success!")

with DAG('error_handling_example', start_date=datetime(2024, 1, 1)) as dag:

    task = PythonOperator(
        task_id='flaky_task',
        python_callable=flaky_operation,
        retries=5,  # Retry up to 5 times
        retry_delay=timedelta(minutes=1),  # Wait 1 minute between retries
        retry_exponential_backoff=True,  # 1min, 2min, 4min, 8min, 16min
        max_retry_delay=timedelta(minutes=10),  # Max 10 minutes
    )
```

### Failure Callbacks
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

def send_failure_notification(context):
    """Send alert on task failure"""
    task_instance = context['task_instance']

    slack_msg = f"""
    :red_circle: Task Failed
    *Task*: {task_instance.task_id}
    *DAG*: {task_instance.dag_id}
    *Execution Date*: {context['execution_date']}
    *Log*: {task_instance.log_url}
    """

    slack_alert = SlackWebhookOperator(
        task_id='slack_alert',
        http_conn_id='slack_webhook',
        message=slack_msg,
    )
    return slack_alert.execute(context=context)

with DAG('dag_with_alerts', ...) as dag:

    risky_task = PythonOperator(
        task_id='risky_operation',
        python_callable=lambda: 1 / 0,  # Will fail
        on_failure_callback=send_failure_notification,
    )
```

## Data Passing with XCom

### Push and Pull Data
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule_interval='@daily', start_date=datetime(2024, 1, 1))
def xcom_example():

    @task
    def extract() -> dict:
        """Extract and return data via XCom"""
        data = {
            'record_count': 1000,
            'source': 'postgres',
            'extracted_at': datetime.now().isoformat()
        }
        return data  # Automatically pushed to XCom

    @task
    def process(extraction_result: dict) -> dict:
        """Process using data from previous task"""
        print(f"Processing {extraction_result['record_count']} records")
        print(f"Source: {extraction_result['source']}")

        return {
            'processed_count': extraction_result['record_count'],
            'status': 'success'
        }

    @task
    def report(process_result: dict):
        """Generate report"""
        print(f"Processed: {process_result['processed_count']} records")
        print(f"Status: {process_result['status']}")

    # Data flows automatically via XCom
    extraction = extract()
    processing = process(extraction)
    report(processing)

dag = xcom_example()
```

## dbt Integration

### Running dbt in Airflow
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'dbt_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
) as dag:

    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command='cd /dbt && dbt deps',
    )

    dbt_source_freshness = BashOperator(
        task_id='check_source_freshness',
        bash_command='cd /dbt && dbt source freshness',
    )

    dbt_snapshot = BashOperator(
        task_id='snapshot_tables',
        bash_command='cd /dbt && dbt snapshot',
    )

    dbt_run_staging = BashOperator(
        task_id='run_staging_models',
        bash_command='cd /dbt && dbt run --models staging.*',
    )

    dbt_test_staging = BashOperator(
        task_id='test_staging_models',
        bash_command='cd /dbt && dbt test --models staging.*',
    )

    dbt_run_marts = BashOperator(
        task_id='run_marts_models',
        bash_command='cd /dbt && dbt run --models marts.*',
    )

    dbt_test_all = BashOperator(
        task_id='test_all_models',
        bash_command='cd /dbt && dbt test',
    )

    # Workflow
    dbt_deps >> dbt_source_freshness >> dbt_snapshot
    dbt_snapshot >> dbt_run_staging >> dbt_test_staging
    dbt_test_staging >> dbt_run_marts >> dbt_test_all
```

## Best Practices

### 1. Idempotency
```python
# ✅ Idempotent: Safe to re-run
@task
def load_data(date: str):
    """Delete and reload pattern"""
    # Delete existing data for date
    db.execute(f"DELETE FROM table WHERE date = '{date}'")

    # Insert fresh data
    db.execute(f"INSERT INTO table SELECT * FROM staging WHERE date = '{date}'")

# ❌ Not idempotent: Creates duplicates
@task
def load_data_bad():
    """Appends without deduplication"""
    db.execute("INSERT INTO table SELECT * FROM staging")
```

### 2. Atomic Operations
```python
@task
def atomic_load():
    """Use transactions for atomicity"""
    with db.begin() as transaction:
        try:
            # Delete old data
            transaction.execute("DELETE FROM target WHERE date = :date")

            # Insert new data
            transaction.execute("INSERT INTO target SELECT * FROM source")

            # Commit if all succeeds
            transaction.commit()
        except Exception as e:
            # Rollback on any error
            transaction.rollback()
            raise
```

### 3. Resource Management
```python
# Define resource pools in Airflow UI
# airflow pools set heavy_compute 5 "Heavy computation tasks"

with DAG('resource_managed', ...) as dag:

    heavy_task = PythonOperator(
        task_id='heavy_processing',
        python_callable=process_large_dataset,
        pool='heavy_compute',  # Use specific pool
        pool_slots=2,  # Consumes 2 of 5 slots
        priority_weight=10,  # Higher priority
    )
```

### 4. Documentation
```python
@dag(
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    doc_md="""
    ## Customer ETL Pipeline

    This DAG performs the following:
    1. Extracts customer data from PostgreSQL
    2. Transforms data using dbt
    3. Loads to Snowflake warehouse

    **Schedule**: Daily at 2 AM UTC
    **Owner**: Data Engineering Team
    **SLA**: 2 hours
    """,
)
def documented_pipeline():

    @task(doc_md="Extract customer records from production database")
    def extract():
        pass

    @task(doc_md="Transform using dbt staging models")
    def transform():
        pass

dag = documented_pipeline()
```

## Testing DAGs

### Unit Testing
```python
# tests/test_customer_pipeline.py
import pytest
from airflow.models import DagBag
from datetime import datetime

def test_dag_loads():
    """Test that DAG loads without errors"""
    dagbag = DagBag()
    dag = dagbag.get_dag('customer_etl_pipeline')

    assert dag is not None
    assert len(dag.tasks) > 0
    assert dagbag.import_errors == {}

def test_dag_structure():
    """Test DAG structure and dependencies"""
    dagbag = DagBag()
    dag = dagbag.get_dag('customer_etl_pipeline')

    # Check tasks exist
    assert 'extract_customers' in dag.task_ids
    assert 'transform_customers' in dag.task_ids
    assert 'load_customers' in dag.task_ids

    # Check dependencies
    extract = dag.get_task('extract_customers')
    transform = dag.get_task('transform_customers')

    assert transform in extract.downstream_list

def test_task_execution():
    """Test individual task execution"""
    from airflow.models import TaskInstance
    from customer_etl_pipeline import extract_customers

    # Execute task
    result = extract_customers()

    assert result is not None
    assert 'records_extracted' in result
```

## Deployment

### Local Development
```bash
# Initialize Airflow
export AIRFLOW_HOME=~/airflow
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start webserver
airflow webserver --port 8080

# Start scheduler (in another terminal)
airflow scheduler
```

### Production Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow

  airflow-webserver:
    image: apache/airflow:2.7.1
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    ports:
      - "8080:8080"
    command: webserver

  airflow-scheduler:
    image: apache/airflow:2.7.1
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    command: scheduler

  airflow-worker:
    image: apache/airflow:2.7.1
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    command: celery worker
```

## Resources

- **Official Docs**: https://airflow.apache.org/docs/
- **Best Practices**: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html
- **TaskFlow API**: https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html
- **Astronomer Guides**: https://www.astronomer.io/guides/
