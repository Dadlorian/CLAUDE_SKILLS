from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['incremental', 'hourly'],
)
def incremental_load_pipeline():
    """Hourly incremental data loading"""

    @task
    def extract_incremental():
        """Extract new/updated records"""
        import psycopg2

        conn = psycopg2.connect(
            host="database.example.com",
            database="production",
            user="etl_user",
            password="password"
        )

        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM orders
            WHERE updated_at > NOW() - INTERVAL '1 hour'
        """)

        records = cursor.fetchall()
        print(f"Extracted {len(records)} records")

        return len(records)

    @task
    def run_dbt_incremental(record_count: int):
        """Run dbt incremental models if we have new data"""
        if record_count > 0:
            import subprocess
            subprocess.run([
                'dbt', 'run',
                '--models', 'fct_orders',
                '--target', 'prod'
            ], check=True)

            print(f"Processed {record_count} new records")
        else:
            print("No new records to process")

    @task
    def validate_data():
        """Quick validation of loaded data"""
        import subprocess
        subprocess.run([
            'dbt', 'test',
            '--models', 'fct_orders',
            '--target', 'prod'
        ], check=True)

    # Define workflow
    count = extract_incremental()
    run_dbt_incremental(count)
    validate_data()

dag = incremental_load_pipeline()
