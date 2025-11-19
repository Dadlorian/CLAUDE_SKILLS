# Data Warehouse API Integration Patterns

## Table of Contents

1. [Overview](#overview)
2. [Snowflake APIs](#snowflake-apis)
3. [Google BigQuery APIs](#google-bigquery-apis)
4. [Amazon Redshift APIs](#amazon-redshift-apis)
5. [Connection Pooling](#connection-pooling)
6. [Query Optimization](#query-optimization)
7. [Cost Management](#cost-management)
8. [Best Practices](#best-practices)

---

## Overview

Modern data warehouses provide robust APIs for programmatic access, enabling automated workflows, cost optimization, and seamless integration with BI tools. This guide covers API patterns for the three major cloud data warehouses.

**Key Integration Scenarios:**
- Automated query execution
- Data loading and transformation
- Resource and cost monitoring
- User and permission management
- Metadata extraction
- Performance optimization

---

## Snowflake APIs

Snowflake provides multiple API interfaces for different use cases.

### Snowflake SQL API

The SQL API enables execution of SQL statements via REST endpoints.

```python
import requests
import json
import time
from typing import Dict, List, Any, Optional

class SnowflakeSQLAPI:
    def __init__(self, account, warehouse, database, schema):
        """
        Initialize Snowflake SQL API client

        account: account identifier (e.g., 'xy12345.us-east-1')
        """
        self.account = account
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.base_url = f"https://{account}.snowflakecomputing.com/api/v2"
        self.session_token = None

    def authenticate(self, username: str, password: str) -> str:
        """Authenticate and get session token"""
        url = f"{self.base_url}/statements"

        auth_header = {
            'Authorization': f'Basic {self._encode_credentials(username, password)}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Initial authentication statement
        payload = {
            'statement': 'SELECT CURRENT_VERSION()',
            'timeout': 60,
            'warehouse': self.warehouse
        }

        try:
            response = requests.post(url, json=payload, headers=auth_header)
            response.raise_for_status()

            # Store session token from response headers
            self.session_token = response.headers.get('Snowflake-Session-Token')

            return self.session_token

        except requests.exceptions.RequestException as e:
            raise Exception(f"Authentication failed: {str(e)}")

    def _encode_credentials(self, username: str, password: str) -> str:
        """Encode credentials for Basic Auth"""
        import base64
        credentials = f"{username}:{password}"
        return base64.b64encode(credentials.encode()).decode()

    def execute_statement(self, statement: str, bindings: Optional[Dict] = None,
                         async_exec: bool = False) -> Dict[str, Any]:
        """
        Execute a SQL statement

        statement: SQL statement to execute
        bindings: Optional parameter bindings
        async_exec: If True, return immediately without waiting for results
        """
        url = f"{self.base_url}/statements"

        headers = {
            'X-Snowflake-Authorization-Token-Type': 'KEYPAIR_JWT',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'statement': statement,
            'timeout': 60,
            'warehouse': self.warehouse,
            'database': self.database,
            'schema': self.schema,
            'async': async_exec
        }

        if bindings:
            payload['bindings'] = bindings

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            if async_exec:
                # Return statement handle for polling
                return {
                    'statementHandle': result['statementHandle'],
                    'status': 'running'
                }
            else:
                # Return results immediately
                return self._parse_results(result)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Statement execution failed: {str(e)}")

    def check_statement_status(self, statement_handle: str) -> Dict[str, Any]:
        """Check status of an asynchronously executed statement"""
        url = f"{self.base_url}/statements/{statement_handle}"

        headers = {
            'X-Snowflake-Authorization-Token-Type': 'KEYPAIR_JWT',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            result = response.json()

            return {
                'status': result['statementStatusUrl'],
                'data': self._parse_results(result) if result.get('resultSetMetaData') else None
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to check statement status: {str(e)}")

    def cancel_statement(self, statement_handle: str) -> bool:
        """Cancel a running statement"""
        url = f"{self.base_url}/statements/{statement_handle}/cancel"

        headers = {
            'X-Snowflake-Authorization-Token-Type': 'KEYPAIR_JWT',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to cancel statement: {str(e)}")

    def _parse_results(self, response: Dict) -> Dict[str, Any]:
        """Parse SQL API response into structured results"""
        if 'data' not in response:
            return {'rows': [], 'rowCount': 0}

        # Extract column metadata
        columns = []
        if 'resultSetMetaData' in response:
            for col in response['resultSetMetaData']['rowType']:
                columns.append({
                    'name': col['name'],
                    'type': col['type'],
                    'nullable': col.get('nullable', True)
                })

        # Extract data rows
        rows = response['data']

        return {
            'columns': columns,
            'rows': rows,
            'rowCount': len(rows),
            'queryId': response.get('queryId')
        }

# Usage example
sf_api = SnowflakeSQLAPI(
    account='xy12345.us-east-1',
    warehouse='COMPUTE_WH',
    database='ANALYTICS',
    schema='PUBLIC'
)

sf_api.authenticate('username', 'password')

# Synchronous query
result = sf_api.execute_statement(
    "SELECT * FROM sales WHERE region = ? AND date >= ?",
    bindings={'1': 'West', '2': '2024-01-01'}
)

print(f"Query returned {result['rowCount']} rows")

# Asynchronous query for long-running operations
handle = sf_api.execute_statement(
    "SELECT * FROM large_table",
    async_exec=True
)

# Poll for results
while True:
    status = sf_api.check_statement_status(handle['statementHandle'])
    if status['data']:
        print(f"Query completed: {status['data']['rowCount']} rows")
        break
    time.sleep(5)
```

### Snowflake Python Connector

For more feature-rich interactions, use the official Python connector.

```python
import snowflake.connector
from snowflake.connector import DictCursor
from contextlib import contextmanager
import pandas as pd

class SnowflakeConnector:
    def __init__(self, account, user, password, warehouse, database, schema, role='SYSADMIN'):
        self.connection_params = {
            'account': account,
            'user': user,
            'password': password,
            'warehouse': warehouse,
            'database': database,
            'schema': schema,
            'role': role
        }

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = snowflake.connector.connect(**self.connection_params)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Execute query and return results as list of dictionaries"""
        with self.get_connection() as conn:
            cursor = conn.cursor(DictCursor)
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                results = cursor.fetchall()
                return results

            finally:
                cursor.close()

    def execute_query_to_dataframe(self, query: str) -> pd.DataFrame:
        """Execute query and return results as pandas DataFrame"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query)

                # Fetch results and column names
                df = cursor.fetch_pandas_all()
                return df

            finally:
                cursor.close()

    def execute_many(self, query: str, data: List[tuple]) -> int:
        """Execute parameterized query for multiple rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(query, data)
                return cursor.rowcount

            finally:
                cursor.close()

    def copy_into_table(self, table_name: str, stage_location: str,
                       file_format: str = 'CSV', pattern: str = '.*'):
        """Load data from stage into table using COPY INTO"""
        query = f"""
        COPY INTO {table_name}
        FROM {stage_location}
        FILE_FORMAT = (TYPE = {file_format})
        PATTERN = '{pattern}'
        ON_ERROR = 'CONTINUE'
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query)

                # Get load statistics
                results = cursor.fetchall()

                stats = {
                    'files_loaded': 0,
                    'rows_loaded': 0,
                    'errors': 0
                }

                for row in results:
                    if row[1] == 'LOADED':
                        stats['files_loaded'] += 1
                        stats['rows_loaded'] += row[2]
                    else:
                        stats['errors'] += 1

                return stats

            finally:
                cursor.close()

    def put_file_to_stage(self, local_file_path: str, stage_name: str,
                         auto_compress: bool = True) -> Dict:
        """Upload file to Snowflake internal stage"""
        query = f"""
        PUT file://{local_file_path} @{stage_name}
        AUTO_COMPRESS = {auto_compress}
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                results = cursor.fetchall()

                return {
                    'source': results[0][0],
                    'target': results[0][1],
                    'status': results[0][6]
                }

            finally:
                cursor.close()

    def get_query_history(self, limit: int = 100) -> List[Dict]:
        """Retrieve recent query history"""
        query = """
        SELECT
            query_id,
            query_text,
            user_name,
            warehouse_name,
            execution_status,
            total_elapsed_time,
            rows_produced,
            start_time,
            end_time
        FROM table(information_schema.query_history())
        ORDER BY start_time DESC
        LIMIT %s
        """

        return self.execute_query(query, (limit,))

# Usage
sf = SnowflakeConnector(
    account='xy12345.us-east-1',
    user='analytics_user',
    password='password',
    warehouse='ANALYTICS_WH',
    database='PROD',
    schema='PUBLIC'
)

# Query to DataFrame
df = sf.execute_query_to_dataframe("SELECT * FROM sales WHERE date >= '2024-01-01'")

# Bulk insert
data = [
    (1, 'Product A', 100.50),
    (2, 'Product B', 200.75),
    (3, 'Product C', 150.25)
]
rows_inserted = sf.execute_many(
    "INSERT INTO products (id, name, price) VALUES (%s, %s, %s)",
    data
)

# Load from stage
sf.put_file_to_stage('/data/sales.csv', 'my_stage')
stats = sf.copy_into_table('sales', '@my_stage', file_format='CSV')
print(f"Loaded {stats['rows_loaded']} rows from {stats['files_loaded']} files")
```

---

## Google BigQuery APIs

BigQuery provides REST API and client libraries for programmatic access.

### BigQuery REST API

```python
from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core import retry
import time

class BigQueryAPI:
    def __init__(self, project_id, credentials_path=None):
        """
        Initialize BigQuery client

        project_id: GCP project ID
        credentials_path: Path to service account JSON key file
        """
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/bigquery']
            )
            self.client = bigquery.Client(project=project_id, credentials=credentials)
        else:
            # Use default credentials (e.g., from GOOGLE_APPLICATION_CREDENTIALS)
            self.client = bigquery.Client(project=project_id)

    def execute_query(self, query: str, use_query_cache: bool = True,
                     max_results: Optional[int] = None) -> List[Dict]:
        """
        Execute SQL query and return results

        query: SQL query string
        use_query_cache: Whether to use cached results if available
        max_results: Maximum number of rows to return
        """
        job_config = bigquery.QueryJobConfig(
            use_query_cache=use_query_cache,
            use_legacy_sql=False
        )

        try:
            query_job = self.client.query(query, job_config=job_config)

            # Wait for query to complete
            results = query_job.result(max_results=max_results)

            # Convert to list of dictionaries
            rows = [dict(row) for row in results]

            # Get job statistics
            stats = {
                'total_bytes_processed': query_job.total_bytes_processed,
                'total_bytes_billed': query_job.total_bytes_billed,
                'cache_hit': query_job.cache_hit,
                'total_rows': query_job.total_rows,
                'job_id': query_job.job_id
            }

            return {
                'rows': rows,
                'statistics': stats
            }

        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")

    def execute_query_async(self, query: str) -> str:
        """Execute query asynchronously and return job ID"""
        job_config = bigquery.QueryJobConfig(use_legacy_sql=False)

        query_job = self.client.query(query, job_config=job_config)

        return query_job.job_id

    def get_job_status(self, job_id: str) -> Dict:
        """Check status of a query job"""
        job = self.client.get_job(job_id)

        return {
            'job_id': job.job_id,
            'state': job.state,
            'created': job.created,
            'started': job.started,
            'ended': job.ended,
            'error_result': job.error_result
        }

    def create_table_from_query(self, query: str, destination_table: str,
                               write_disposition: str = 'WRITE_TRUNCATE') -> Dict:
        """
        Create or replace table from query results

        write_disposition: WRITE_TRUNCATE, WRITE_APPEND, or WRITE_EMPTY
        """
        job_config = bigquery.QueryJobConfig(
            destination=destination_table,
            write_disposition=write_disposition
        )

        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()  # Wait for completion

            return {
                'destination_table': destination_table,
                'rows_written': query_job.total_rows,
                'bytes_processed': query_job.total_bytes_processed
            }

        except Exception as e:
            raise Exception(f"Table creation failed: {str(e)}")

    def load_table_from_dataframe(self, df, table_id: str,
                                  write_disposition: str = 'WRITE_TRUNCATE') -> Dict:
        """Load pandas DataFrame into BigQuery table"""
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            autodetect=True
        )

        try:
            load_job = self.client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            load_job.result()  # Wait for completion

            table = self.client.get_table(table_id)

            return {
                'table_id': table_id,
                'rows_loaded': table.num_rows,
                'schema': [field.name for field in table.schema]
            }

        except Exception as e:
            raise Exception(f"DataFrame load failed: {str(e)}")

    def load_table_from_uri(self, source_uris: List[str], table_id: str,
                           source_format: str = 'CSV', skip_leading_rows: int = 1) -> Dict:
        """Load table from GCS URIs"""
        job_config = bigquery.LoadJobConfig(
            source_format=getattr(bigquery.SourceFormat, source_format),
            skip_leading_rows=skip_leading_rows,
            autodetect=True
        )

        try:
            load_job = self.client.load_table_from_uri(
                source_uris, table_id, job_config=job_config
            )
            load_job.result()

            return {
                'table_id': table_id,
                'source_uris': source_uris,
                'output_rows': load_job.output_rows
            }

        except Exception as e:
            raise Exception(f"GCS load failed: {str(e)}")

    def export_table_to_gcs(self, table_id: str, destination_uri: str,
                           destination_format: str = 'CSV') -> Dict:
        """Export table to Google Cloud Storage"""
        job_config = bigquery.ExtractJobConfig(
            destination_format=getattr(bigquery.DestinationFormat, destination_format)
        )

        try:
            extract_job = self.client.extract_table(
                table_id, destination_uri, job_config=job_config
            )
            extract_job.result()

            return {
                'table_id': table_id,
                'destination_uri': destination_uri,
                'destination_uris': extract_job.destination_uris
            }

        except Exception as e:
            raise Exception(f"Table export failed: {str(e)}")

    def create_dataset(self, dataset_id: str, location: str = 'US',
                      description: str = '') -> Dict:
        """Create a new dataset"""
        dataset = bigquery.Dataset(f"{self.client.project}.{dataset_id}")
        dataset.location = location
        dataset.description = description

        try:
            dataset = self.client.create_dataset(dataset, exists_ok=True)

            return {
                'dataset_id': dataset.dataset_id,
                'location': dataset.location,
                'created': dataset.created
            }

        except Exception as e:
            raise Exception(f"Dataset creation failed: {str(e)}")

    def get_table_metadata(self, table_id: str) -> Dict:
        """Get table metadata and statistics"""
        table = self.client.get_table(table_id)

        return {
            'table_id': table.table_id,
            'num_rows': table.num_rows,
            'num_bytes': table.num_bytes,
            'created': table.created,
            'modified': table.modified,
            'schema': [
                {
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode
                }
                for field in table.schema
            ],
            'partitioning': table.time_partitioning,
            'clustering': table.clustering_fields
        }

    def estimate_query_cost(self, query: str) -> Dict:
        """Estimate bytes processed and cost for a query"""
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

        try:
            query_job = self.client.query(query, job_config=job_config)

            bytes_processed = query_job.total_bytes_processed

            # BigQuery pricing: $5 per TB processed (as of 2024)
            cost_per_tb = 5.0
            estimated_cost = (bytes_processed / (1024**4)) * cost_per_tb

            return {
                'bytes_processed': bytes_processed,
                'gigabytes_processed': bytes_processed / (1024**3),
                'estimated_cost_usd': round(estimated_cost, 4)
            }

        except Exception as e:
            raise Exception(f"Query cost estimation failed: {str(e)}")

# Usage
bq = BigQueryAPI(project_id='my-gcp-project', credentials_path='service-account.json')

# Execute query
result = bq.execute_query("""
    SELECT
        region,
        COUNT(*) as order_count,
        SUM(total_amount) as total_sales
    FROM `my-project.sales.orders`
    WHERE date >= '2024-01-01'
    GROUP BY region
""")

print(f"Rows returned: {len(result['rows'])}")
print(f"Bytes processed: {result['statistics']['total_bytes_processed']:,}")
print(f"Cache hit: {result['statistics']['cache_hit']}")

# Estimate query cost before running
cost_estimate = bq.estimate_query_cost("SELECT * FROM `my-project.large_table`")
print(f"Estimated cost: ${cost_estimate['estimated_cost_usd']}")

# Load DataFrame
import pandas as pd
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'Los Angeles', 'Chicago']
})

bq.load_table_from_dataframe(df, 'my-project.my_dataset.users')
```

---

## Amazon Redshift APIs

Redshift Data API enables query execution without managing connections.

```python
import boto3
import time
from typing import List, Dict, Any, Optional

class RedshiftDataAPI:
    def __init__(self, cluster_id, database, db_user, region='us-east-1'):
        """
        Initialize Redshift Data API client

        cluster_id: Redshift cluster identifier
        database: Database name
        db_user: Database user
        """
        self.client = boto3.client('redshift-data', region_name=region)
        self.cluster_id = cluster_id
        self.database = database
        self.db_user = db_user

    def execute_statement(self, sql: str, wait_for_completion: bool = True,
                         timeout: int = 300) -> Dict[str, Any]:
        """
        Execute SQL statement

        sql: SQL statement to execute
        wait_for_completion: Wait for query to complete before returning
        timeout: Maximum time to wait in seconds
        """
        try:
            # Submit query
            response = self.client.execute_statement(
                ClusterIdentifier=self.cluster_id,
                Database=self.database,
                DbUser=self.db_user,
                Sql=sql
            )

            query_id = response['Id']

            if not wait_for_completion:
                return {'query_id': query_id, 'status': 'SUBMITTED'}

            # Wait for completion
            start_time = time.time()
            while True:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Query timeout after {timeout} seconds")

                status_response = self.client.describe_statement(Id=query_id)
                status = status_response['Status']

                if status == 'FINISHED':
                    # Get results
                    results = self._get_statement_results(query_id)
                    return {
                        'query_id': query_id,
                        'status': 'FINISHED',
                        'rows': results['rows'],
                        'columns': results['columns'],
                        'row_count': len(results['rows'])
                    }

                elif status == 'FAILED':
                    error = status_response.get('Error', 'Unknown error')
                    raise Exception(f"Query failed: {error}")

                elif status == 'ABORTED':
                    raise Exception("Query was aborted")

                time.sleep(1)

        except Exception as e:
            raise Exception(f"Statement execution failed: {str(e)}")

    def execute_batch(self, sql_statements: List[str]) -> Dict[str, Any]:
        """Execute multiple SQL statements in a batch"""
        try:
            response = self.client.batch_execute_statement(
                ClusterIdentifier=self.cluster_id,
                Database=self.database,
                DbUser=self.db_user,
                Sqls=sql_statements
            )

            return {
                'query_id': response['Id'],
                'status': 'SUBMITTED',
                'statement_count': len(sql_statements)
            }

        except Exception as e:
            raise Exception(f"Batch execution failed: {str(e)}")

    def cancel_statement(self, query_id: str) -> bool:
        """Cancel a running query"""
        try:
            self.client.cancel_statement(Id=query_id)
            return True
        except Exception as e:
            raise Exception(f"Failed to cancel statement: {str(e)}")

    def _get_statement_results(self, query_id: str) -> Dict[str, Any]:
        """Retrieve query results"""
        try:
            response = self.client.get_statement_result(Id=query_id)

            # Parse column metadata
            columns = []
            for col in response.get('ColumnMetadata', []):
                columns.append({
                    'name': col['name'],
                    'type': col['typeName'],
                    'length': col.get('length', 0)
                })

            # Parse rows
            rows = []
            for record in response.get('Records', []):
                row = {}
                for i, value in enumerate(record):
                    col_name = columns[i]['name']
                    # Extract value based on type
                    if 'stringValue' in value:
                        row[col_name] = value['stringValue']
                    elif 'longValue' in value:
                        row[col_name] = value['longValue']
                    elif 'doubleValue' in value:
                        row[col_name] = value['doubleValue']
                    elif 'booleanValue' in value:
                        row[col_name] = value['booleanValue']
                    elif 'isNull' in value and value['isNull']:
                        row[col_name] = None
                rows.append(row)

            return {
                'columns': columns,
                'rows': rows
            }

        except Exception as e:
            raise Exception(f"Failed to get results: {str(e)}")

    def list_tables(self, schema: str = 'public') -> List[str]:
        """List tables in a schema"""
        sql = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{schema}'
        ORDER BY table_name
        """

        result = self.execute_statement(sql)
        return [row['table_name'] for row in result['rows']]

    def get_table_info(self, table_name: str, schema: str = 'public') -> Dict:
        """Get table metadata"""
        sql = f"""
        SELECT
            column_name,
            data_type,
            character_maximum_length,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = '{schema}'
        AND table_name = '{table_name}'
        ORDER BY ordinal_position
        """

        result = self.execute_statement(sql)

        return {
            'table_name': table_name,
            'schema': schema,
            'columns': result['rows']
        }

    def copy_from_s3(self, table_name: str, s3_path: str, iam_role: str,
                    file_format: str = 'CSV', delimiter: str = ',',
                    ignore_header: int = 1) -> Dict:
        """Load data from S3 using COPY command"""
        sql = f"""
        COPY {table_name}
        FROM '{s3_path}'
        IAM_ROLE '{iam_role}'
        FORMAT AS {file_format}
        DELIMITER '{delimiter}'
        IGNOREHEADER {ignore_header}
        """

        return self.execute_statement(sql)

    def unload_to_s3(self, query: str, s3_path: str, iam_role: str,
                    file_format: str = 'CSV', parallel: bool = True) -> Dict:
        """Unload query results to S3"""
        parallel_clause = 'PARALLEL ON' if parallel else 'PARALLEL OFF'

        sql = f"""
        UNLOAD ('{query}')
        TO '{s3_path}'
        IAM_ROLE '{iam_role}'
        FORMAT AS {file_format}
        {parallel_clause}
        ALLOWOVERWRITE
        """

        return self.execute_statement(sql)

# Usage
redshift = RedshiftDataAPI(
    cluster_id='my-redshift-cluster',
    database='analytics',
    db_user='admin',
    region='us-east-1'
)

# Execute query
result = redshift.execute_statement("""
    SELECT
        product_category,
        COUNT(*) as product_count,
        AVG(price) as avg_price
    FROM products
    GROUP BY product_category
    ORDER BY product_count DESC
""")

print(f"Query returned {result['row_count']} rows")

# Load from S3
redshift.copy_from_s3(
    table_name='sales',
    s3_path='s3://my-bucket/data/sales/',
    iam_role='arn:aws:iam::123456789:role/RedshiftCopyRole',
    file_format='CSV'
)

# Unload to S3
redshift.unload_to_s3(
    query='SELECT * FROM sales WHERE date >= \'2024-01-01\'',
    s3_path='s3://my-bucket/exports/sales/',
    iam_role='arn:aws:iam::123456789:role/RedshiftUnloadRole'
)
```

---

## Connection Pooling

Efficient connection management is critical for performance.

```python
from sqlalchemy import create_engine, pool
from contextlib import contextmanager

class DataWarehouseConnectionPool:
    def __init__(self, connection_string, pool_size=5, max_overflow=10):
        """
        Create connection pool using SQLAlchemy

        pool_size: Number of persistent connections
        max_overflow: Maximum overflow connections
        """
        self.engine = create_engine(
            connection_string,
            poolclass=pool.QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=False
        )

    @contextmanager
    def get_connection(self):
        """Get connection from pool"""
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def execute_query(self, query, params=None):
        """Execute query using pooled connection"""
        with self.get_connection() as conn:
            result = conn.execute(query, params or {})
            return result.fetchall()

    def dispose(self):
        """Dispose of connection pool"""
        self.engine.dispose()

# Snowflake example
snowflake_pool = DataWarehouseConnectionPool(
    connection_string='snowflake://user:pass@account/db/schema?warehouse=WH&role=ROLE',
    pool_size=10,
    max_overflow=20
)

# BigQuery example (using SQLAlchemy BigQuery)
bigquery_pool = DataWarehouseConnectionPool(
    connection_string='bigquery://project-id/dataset',
    pool_size=5
)
```

---

## Query Optimization

### Query Cost Analysis

```python
class QueryOptimizer:
    def __init__(self, warehouse_api):
        self.api = warehouse_api

    def analyze_query_plan(self, query: str) -> Dict:
        """Analyze query execution plan"""
        # For Snowflake
        explain_query = f"EXPLAIN {query}"
        result = self.api.execute_statement(explain_query)

        return self._parse_explain_output(result)

    def identify_expensive_operations(self, query_plan: Dict) -> List[str]:
        """Identify expensive operations in query plan"""
        expensive_ops = []

        # Look for full table scans
        if 'TableScan' in str(query_plan):
            expensive_ops.append("Full table scan detected - consider adding filters or indexes")

        # Look for cartesian products
        if 'CartesianProduct' in str(query_plan):
            expensive_ops.append("Cartesian product detected - review JOIN conditions")

        return expensive_ops

    def suggest_optimizations(self, query: str) -> List[str]:
        """Suggest query optimizations"""
        suggestions = []

        query_lower = query.lower()

        # Check for SELECT *
        if 'select *' in query_lower:
            suggestions.append("Avoid SELECT * - specify only needed columns")

        # Check for filtering in WHERE vs HAVING
        if 'having' in query_lower and 'group by' in query_lower:
            suggestions.append("Move non-aggregate filters to WHERE clause for better performance")

        # Check for subqueries that could be CTEs
        if query_lower.count('select') > 2:
            suggestions.append("Consider using CTEs for better readability and potential optimization")

        return suggestions

# Usage
optimizer = QueryOptimizer(snowflake_api)
suggestions = optimizer.suggest_optimizations(query)
```

---

## Cost Management

### Query Cost Tracking

```python
class CostTracker:
    def __init__(self):
        self.query_costs = []

    def track_query_cost(self, platform: str, query_id: str,
                        bytes_processed: int, execution_time: float):
        """Track query cost"""
        # Calculate cost based on platform pricing
        if platform == 'bigquery':
            cost = (bytes_processed / (1024**4)) * 5.0  # $5 per TB
        elif platform == 'snowflake':
            # Snowflake charges by compute time
            cost = (execution_time / 3600) * 2.0  # $2 per compute hour (example)
        else:
            cost = 0

        self.query_costs.append({
            'platform': platform,
            'query_id': query_id,
            'bytes_processed': bytes_processed,
            'execution_time': execution_time,
            'cost_usd': cost,
            'timestamp': time.time()
        })

        return cost

    def get_daily_cost(self, platform: Optional[str] = None) -> float:
        """Calculate daily cost"""
        today = time.time() - 86400  # Last 24 hours

        costs = [
            q['cost_usd'] for q in self.query_costs
            if q['timestamp'] > today and (platform is None or q['platform'] == platform)
        ]

        return sum(costs)

    def get_cost_by_user(self) -> Dict[str, float]:
        """Calculate cost by user"""
        # Implementation depends on tracking user info with queries
        pass
```

---

## Best Practices

### 1. Secure Credential Management

```python
import boto3
import json

def get_db_credentials_from_secrets_manager(secret_name, region='us-east-1'):
    """Retrieve database credentials from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])

        return {
            'host': secret['host'],
            'port': secret['port'],
            'database': secret['database'],
            'username': secret['username'],
            'password': secret['password']
        }
    except Exception as e:
        raise Exception(f"Failed to retrieve credentials: {str(e)}")
```

### 2. Retry Logic with Exponential Backoff

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise

                    delay = min(base_delay * (2 ** attempt), max_delay)
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                    time.sleep(delay)

        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=2)
def execute_critical_query(query):
    return warehouse_api.execute_statement(query)
```

### 3. Query Result Caching

```python
import hashlib
import json
from functools import lru_cache

class QueryCache:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds

    def _generate_key(self, query: str, params: Dict) -> str:
        """Generate cache key from query and parameters"""
        content = f"{query}{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, query: str, params: Dict = None) -> Optional[Any]:
        """Get cached query result"""
        key = self._generate_key(query, params or {})

        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
            else:
                del self.cache[key]

        return None

    def set(self, query: str, result: Any, params: Dict = None):
        """Cache query result"""
        key = self._generate_key(query, params or {})
        self.cache[key] = (result, time.time())

# Usage
cache = QueryCache(ttl_seconds=1800)  # 30 minute TTL

def execute_with_cache(query, params=None):
    cached = cache.get(query, params)
    if cached:
        print("Returning cached result")
        return cached

    result = warehouse_api.execute_statement(query)
    cache.set(query, result, params)
    return result
```

---

## Summary

This guide covers comprehensive API patterns for the major cloud data warehouses:

- **Snowflake**: SQL API and Python connector for flexible integration
- **BigQuery**: REST API and client libraries with strong GCP integration
- **Redshift**: Data API for serverless query execution

**Key Takeaways:**
1. Use connection pooling for better performance and resource utilization
2. Implement retry logic with exponential backoff for resilience
3. Track query costs to optimize spend
4. Cache frequently-run queries to reduce latency and costs
5. Use dry-run/explain features to estimate costs before execution
6. Secure credentials using secrets management services
7. Monitor query performance and optimize expensive operations

For detailed API documentation, refer to vendor resources:
- Snowflake: https://docs.snowflake.com/en/developer-guide/sql-api/index.html
- BigQuery: https://cloud.google.com/bigquery/docs/reference/rest
- Redshift: https://docs.aws.amazon.com/redshift/latest/mgmt/data-api.html
