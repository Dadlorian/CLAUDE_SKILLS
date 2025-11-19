from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'email': ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'daily_etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline for analytics data',
    schedule_interval='0 2 * * *',  # 2 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'daily', 'production'],
) as dag:

    # Check source data freshness
    check_freshness = PostgresOperator(
        task_id='check_source_freshness',
        postgres_conn_id='postgres_prod',
        sql='''
            SELECT
                CASE
                    WHEN MAX(created_at) < CURRENT_TIMESTAMP - INTERVAL '24 hours'
                    THEN RAISE_EXCEPTION('Stale data detected')
                    ELSE 'OK'
                END
            FROM orders;
        ''',
    )

    # Install dbt dependencies
    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command='cd /dbt && dbt deps',
    )

    # Run snapshots (SCD Type 2)
    dbt_snapshot = BashOperator(
        task_id='dbt_snapshot',
        bash_command='cd /dbt && dbt snapshot --target prod',
    )

    # Run staging models
    dbt_run_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command='cd /dbt && dbt run --models staging.* --target prod',
    )

    # Test staging models
    dbt_test_staging = BashOperator(
        task_id='dbt_test_staging',
        bash_command='cd /dbt && dbt test --models staging.* --target prod',
    )

    # Run marts models
    dbt_run_marts = BashOperator(
        task_id='dbt_run_marts',
        bash_command='cd /dbt && dbt run --models marts.* --target prod',
    )

    # Test all models
    dbt_test_all = BashOperator(
        task_id='dbt_test_all',
        bash_command='cd /dbt && dbt test --target prod',
    )

    # Generate documentation
    dbt_docs = BashOperator(
        task_id='dbt_docs_generate',
        bash_command='cd /dbt && dbt docs generate --target prod',
    )

    # Define dependencies
    check_freshness >> dbt_deps >> dbt_snapshot
    dbt_snapshot >> dbt_run_staging >> dbt_test_staging
    dbt_test_staging >> dbt_run_marts >> dbt_test_all
    dbt_test_all >> dbt_docs
