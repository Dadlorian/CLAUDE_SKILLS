# Apache Airflow Operators Reference

## Core Operators

### BashOperator
Execute bash commands or scripts.

```python
from airflow.operators.bash import BashOperator

run_script = BashOperator(
    task_id='run_data_export',
    bash_command='python /scripts/export_data.py',
    env={'ENV': 'production'},
    append_env=True,
    cwd='/opt/airflow/scripts',
    dag=dag
)

# Multi-line bash
complex_bash = BashOperator(
    task_id='complex_bash',
    bash_command='''
    set -e
    echo "Starting process..."
    cd /data
    ./process.sh {{ ds }}
    echo "Completed"
    ''',
    dag=dag
)
```

**Key Parameters**:
- `bash_command`: Command to execute
- `env`: Environment variables
- `append_env`: Add to existing env vs replace
- `cwd`: Working directory
- `skip_exit_code`: Exit code to skip task

### PythonOperator
Execute Python callables.

```python
from airflow.operators.python import PythonOperator

def process_data(execution_date, **context):
    """Process data for given date"""
    print(f"Processing data for {execution_date}")
    # Your logic here
    return {"records_processed": 1000}

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    op_kwargs={'param1': 'value1'},
    op_args=['arg1', 'arg2'],
    provide_context=True,
    dag=dag
)

# Using decorators (Airflow 2.0+)
from airflow.decorators import task

@task
def process_data_decorated(date: str) -> dict:
    """Modern way using TaskFlow API"""
    return {"records": 1000}
```

**Key Parameters**:
- `python_callable`: Function to execute
- `op_kwargs`: Keyword arguments to pass
- `op_args`: Positional arguments
- `provide_context`: Pass context variables
- `templates_dict`: Dict with Jinja templates

### PythonVirtualenvOperator
Run Python in isolated virtualenv.

```python
from airflow.operators.python import PythonVirtualenvOperator

def run_with_requirements():
    import pandas as pd
    import requests
    # Code using specific package versions
    return pd.__version__

venv_task = PythonVirtualenvOperator(
    task_id='run_in_venv',
    python_callable=run_with_requirements,
    requirements=['pandas==1.5.0', 'requests==2.28.0'],
    system_site_packages=False,
    dag=dag
)
```

### EmailOperator
Send emails from workflows.

```python
from airflow.operators.email import EmailOperator

send_alert = EmailOperator(
    task_id='send_failure_email',
    to=['data-team@company.com'],
    subject='Data Pipeline Failed: {{ dag.dag_id }}',
    html_content='''
    <h3>Pipeline Failure</h3>
    <p>DAG: {{ dag.dag_id }}</p>
    <p>Execution Date: {{ ds }}</p>
    <p>Task: {{ task.task_id }}</p>
    ''',
    trigger_rule='one_failed',
    dag=dag
)
```

## SQL Operators

### PostgresOperator
Execute SQL on PostgreSQL.

```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

create_table = PostgresOperator(
    task_id='create_staging_table',
    postgres_conn_id='postgres_default',
    sql='''
        CREATE TABLE IF NOT EXISTS staging.orders (
            order_id BIGINT PRIMARY KEY,
            customer_id BIGINT,
            order_date DATE,
            amount DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''',
    dag=dag
)

# From SQL file
load_data = PostgresOperator(
    task_id='load_data',
    postgres_conn_id='postgres_prod',
    sql='sql/load_orders.sql',
    parameters={'start_date': '{{ ds }}'},
    dag=dag
)

# Multiple statements
multi_query = PostgresOperator(
    task_id='multi_queries',
    postgres_conn_id='postgres_default',
    sql=[
        "DELETE FROM staging.orders WHERE date = '{{ ds }}'",
        "INSERT INTO staging.orders SELECT * FROM raw.orders WHERE date = '{{ ds }}'",
    ],
    dag=dag
)
```

### SnowflakeOperator
Execute SQL on Snowflake.

```python
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator

snowflake_query = SnowflakeOperator(
    task_id='transform_data',
    snowflake_conn_id='snowflake_default',
    warehouse='TRANSFORM_WH',
    database='ANALYTICS',
    schema='PUBLIC',
    role='TRANSFORMER',
    sql='''
        INSERT INTO fact_orders
        SELECT
            order_id,
            customer_id,
            order_date,
            SUM(amount) as total_amount
        FROM staging_orders
        WHERE date = '{{ ds }}'
        GROUP BY 1, 2, 3;
    ''',
    autocommit=True,
    dag=dag
)
```

### BigQueryOperator
Execute SQL on BigQuery.

```python
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

bigquery_query = BigQueryInsertJobOperator(
    task_id='transform_in_bigquery',
    gcp_conn_id='google_cloud_default',
    configuration={
        "query": {
            "query": '''
                SELECT
                    DATE(timestamp) as date,
                    user_id,
                    COUNT(*) as events
                FROM `project.dataset.events`
                WHERE DATE(timestamp) = '{{ ds }}'
                GROUP BY 1, 2
            ''',
            "destinationTable": {
                "projectId": "my-project",
                "datasetId": "analytics",
                "tableId": "daily_user_events"
            },
            "writeDisposition": "WRITE_APPEND",
            "useLegacySql": False
        }
    },
    dag=dag
)
```

## Transfer Operators

### S3ToSnowflakeOperator
Load data from S3 to Snowflake.

```python
from airflow.providers.snowflake.transfers.s3_to_snowflake import S3ToSnowflakeOperator

s3_to_snowflake = S3ToSnowflakeOperator(
    task_id='load_s3_to_snowflake',
    snowflake_conn_id='snowflake_default',
    s3_keys=['s3://bucket/path/data_{{ ds }}.csv'],
    table='raw_data',
    schema='staging',
    stage='my_stage',
    file_format='my_csv_format',
    dag=dag
)
```

### GCSToBigQueryOperator
Load from GCS to BigQuery.

```python
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

load_csv = GCSToBigQueryOperator(
    task_id='load_csv_to_bigquery',
    bucket='my-bucket',
    source_objects=['data/orders_{{ ds }}.csv'],
    destination_project_dataset_table='project.dataset.orders',
    schema_fields=[
        {'name': 'order_id', 'type': 'INTEGER', 'mode': 'REQUIRED'},
        {'name': 'amount', 'type': 'FLOAT', 'mode': 'NULLABLE'},
    ],
    write_disposition='WRITE_APPEND',
    skip_leading_rows=1,
    autodetect=False,
    dag=dag
)
```

### PostgresToGCSOperator
Export PostgreSQL to GCS.

```python
from airflow.providers.google.cloud.transfers.postgres_to_gcs import PostgresToGCSOperator

export_to_gcs = PostgresToGCSOperator(
    task_id='export_postgres_to_gcs',
    postgres_conn_id='postgres_prod',
    sql='SELECT * FROM orders WHERE date = \'{{ ds }}\'',
    bucket='data-exports',
    filename='orders/{{ ds }}/orders.json',
    export_format='json',
    dag=dag
)
```

## Cloud-Specific Operators

### ECSOperator (AWS)
Run tasks on AWS ECS/Fargate.

```python
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator

ecs_task = EcsRunTaskOperator(
    task_id='run_etl_container',
    cluster='data-cluster',
    task_definition='etl-task:5',
    launch_type='FARGATE',
    overrides={
        'containerOverrides': [
            {
                'name': 'etl-container',
                'command': ['python', 'etl.py', '--date', '{{ ds }}'],
                'environment': [
                    {'name': 'ENV', 'value': 'production'},
                ],
            },
        ],
    },
    network_configuration={
        'awsvpcConfiguration': {
            'subnets': ['subnet-xxxxx'],
            'securityGroups': ['sg-xxxxx'],
            'assignPublicIp': 'ENABLED',
        },
    },
    awslogs_group='/ecs/etl-task',
    awslogs_stream_prefix='ecs',
    dag=dag
)
```

### DataprocSubmitJobOperator (GCP)
Submit jobs to Google Cloud Dataproc.

```python
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator

pyspark_job = {
    "reference": {"project_id": "my-project"},
    "placement": {"cluster_name": "spark-cluster"},
    "pyspark_job": {
        "main_python_file_uri": "gs://bucket/scripts/spark_etl.py",
        "args": ["{{ ds }}"],
    },
}

submit_pyspark = DataprocSubmitJobOperator(
    task_id="run_spark_job",
    job=pyspark_job,
    region="us-central1",
    project_id="my-project",
    dag=dag
)
```

### GlueJobOperator (AWS)
Run AWS Glue jobs.

```python
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

glue_job = GlueJobOperator(
    task_id='run_glue_etl',
    job_name='customer-etl-job',
    script_args={
        '--execution_date': '{{ ds }}',
        '--output_path': 's3://bucket/output/'
    },
    dag=dag
)
```

## dbt Operators

### DbtRunOperator
Run dbt models.

```python
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

# dbt Cloud
dbt_cloud_run = DbtCloudRunJobOperator(
    task_id='run_dbt_models',
    job_id=12345,
    check_interval=10,
    timeout=300,
    dag=dag
)

# Using BashOperator for dbt Core
from airflow.operators.bash import BashOperator

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /dbt && dbt run --profiles-dir . --target prod',
    dag=dag
)

dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /dbt && dbt test --profiles-dir . --target prod',
    dag=dag
)
```

## Sensor Operators

### S3KeySensor
Wait for S3 file to exist.

```python
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

wait_for_file = S3KeySensor(
    task_id='wait_for_s3_file',
    bucket_name='data-bucket',
    bucket_key='data/orders_{{ ds }}.csv',
    aws_conn_id='aws_default',
    timeout=3600,  # 1 hour
    poke_interval=60,  # Check every 60 seconds
    mode='poke',  # or 'reschedule'
    dag=dag
)
```

### SqlSensor
Wait for SQL query condition.

```python
from airflow.providers.common.sql.sensors.sql import SqlSensor

wait_for_data = SqlSensor(
    task_id='wait_for_new_orders',
    conn_id='postgres_default',
    sql='''
        SELECT COUNT(*)
        FROM orders
        WHERE date = '{{ ds }}'
        HAVING COUNT(*) > 0
    ''',
    timeout=600,
    poke_interval=30,
    dag=dag
)
```

### ExternalTaskSensor
Wait for another DAG's task.

```python
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_upstream = ExternalTaskSensor(
    task_id='wait_for_data_ingestion',
    external_dag_id='data_ingestion_dag',
    external_task_id='load_complete',
    allowed_states=['success'],
    failed_states=['failed', 'skipped'],
    mode='reschedule',
    dag=dag
)
```

## Branch Operators

### BranchPythonOperator
Conditional branching logic.

```python
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator

def choose_branch(**context):
    """Decide which branch to take"""
    execution_date = context['execution_date']
    if execution_date.day == 1:  # First day of month
        return 'full_refresh_task'
    else:
        return 'incremental_task'

branch = BranchPythonOperator(
    task_id='branch_decision',
    python_callable=choose_branch,
    dag=dag
)

full_refresh = DummyOperator(task_id='full_refresh_task', dag=dag)
incremental = DummyOperator(task_id='incremental_task', dag=dag)

branch >> [full_refresh, incremental]
```

### BranchSQLOperator
Branch based on SQL query result.

```python
from airflow.operators.sql import BranchSQLOperator

branch_on_count = BranchSQLOperator(
    task_id='check_record_count',
    conn_id='postgres_default',
    sql='SELECT COUNT(*) FROM staging_orders WHERE date = \'{{ ds }}\'',
    follow_task_ids_if_true='process_data',
    follow_task_ids_if_false='skip_processing',
    dag=dag
)
```

## Custom Operators

### Example Custom Operator
```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class CustomDataQualityOperator(BaseOperator):
    """
    Custom operator for data quality checks
    """

    @apply_defaults
    def __init__(
        self,
        table: str,
        checks: list,
        conn_id: str = 'postgres_default',
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table = table
        self.checks = checks
        self.conn_id = conn_id

    def execute(self, context):
        """Execute data quality checks"""
        from airflow.hooks.postgres_hook import PostgresHook

        hook = PostgresHook(postgres_conn_id=self.conn_id)

        for check in self.checks:
            sql = f"SELECT {check['sql']} FROM {self.table}"
            result = hook.get_first(sql)[0]

            if not check['condition'](result):
                raise ValueError(
                    f"Data quality check failed: {check['name']}"
                )

        self.log.info(f"All {len(self.checks)} checks passed")

# Usage
quality_check = CustomDataQualityOperator(
    task_id='quality_checks',
    table='fact_orders',
    checks=[
        {
            'name': 'row_count',
            'sql': 'COUNT(*)',
            'condition': lambda x: x > 0
        },
        {
            'name': 'null_check',
            'sql': 'COUNT(*) - COUNT(customer_id)',
            'condition': lambda x: x == 0
        }
    ],
    dag=dag
)
```

## Operator Best Practices

### 1. Idempotency
```python
# ❌ Not idempotent
insert_data = PostgresOperator(
    task_id='insert',
    sql="INSERT INTO table VALUES (...)",
    dag=dag
)

# ✅ Idempotent
upsert_data = PostgresOperator(
    task_id='upsert',
    sql='''
        DELETE FROM table WHERE date = '{{ ds }}';
        INSERT INTO table SELECT * FROM staging WHERE date = '{{ ds }}';
    ''',
    dag=dag
)
```

### 2. Error Handling
```python
task = PythonOperator(
    task_id='risky_task',
    python_callable=my_function,
    retries=3,
    retry_delay=timedelta(minutes=5),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(hours=1),
    dag=dag
)
```

### 3. Resource Management
```python
# Specify resources for scheduling
resource_heavy_task = BashOperator(
    task_id='heavy_processing',
    bash_command='./process_large_file.sh',
    pool='heavy_compute',  # Use specific pool
    priority_weight=10,  # Higher priority
    dag=dag
)
```

### 4. XCom for Data Passing
```python
@task
def extract_data():
    return {'record_count': 1000}

@task
def process_data(data: dict):
    print(f"Processing {data['record_count']} records")

data = extract_data()
process_data(data)
```

## Common Patterns

### Pattern: Multi-DB Sync
```python
extract = PostgresOperator(task_id='extract', ...)
transform = PythonOperator(task_id='transform', ...)
load_bq = BigQueryOperator(task_id='load_bq', ...)
load_sf = SnowflakeOperator(task_id='load_sf', ...)

extract >> transform >> [load_bq, load_sf]
```

### Pattern: Error Notification
```python
def notify_failure(context):
    send_email(
        to='team@company.com',
        subject=f"DAG Failed: {context['dag'].dag_id}",
        html_content=context['exception']
    )

task = PythonOperator(
    task_id='important_task',
    python_callable=my_func,
    on_failure_callback=notify_failure,
    dag=dag
)
```

### Pattern: Dynamic Tasks
```python
from airflow.decorators import task

@task
def get_table_list():
    return ['orders', 'customers', 'products']

@task
def process_table(table_name: str):
    print(f"Processing {table_name}")

tables = get_table_list()
process_table.expand(table_name=tables)  # Dynamic mapping
```

## Resources

- **Airflow Docs**: https://airflow.apache.org/docs/
- **Provider Packages**: https://airflow.apache.org/docs/apache-airflow-providers/
- **Astronomer Registry**: https://registry.astronomer.io/
- **Airflow GitHub**: https://github.com/apache/airflow
