# Data Warehouse Integration for Product Analytics

## Overview

Data warehouses like Snowflake and BigQuery provide the foundation for product analytics at scale. This guide covers integration patterns for connecting product management systems to data warehouses for comprehensive analytics and insights.

### Why Data Warehouse Integration Matters for PMs

Product Managers benefit from data warehouse integration to:
- Access unified customer and product data
- Perform complex product analytics queries
- Build custom dashboards and reports
- Track KPIs and metrics over time
- Correlate user behavior with business outcomes
- Enable self-service analytics for teams
- Create data-driven product roadmaps
- Conduct cohort analysis and retention studies

---

## Snowflake Integration

### Authentication & Connection

Snowflake supports multiple authentication methods including username/password, OAuth, and SSO.

```bash
# Environment configuration
SNOWFLAKE_ACCOUNT=your_account_id
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=PRODUCT_ANALYTICS
SNOWFLAKE_SCHEMA=PUBLIC
```

#### Snowflake Python Connector

```bash
pip install snowflake-connector-python snowflake-sqlalchemy
```

#### Connection Implementation

```python
import snowflake.connector
from sqlalchemy import create_engine
from typing import List, Dict, Optional
import pandas as pd

class SnowflakeProductAnalytics:
    def __init__(self, account: str, user: str, password: str,
                 warehouse: str, database: str, schema: str):
        self.account = account
        self.user = user
        self.password = password
        self.warehouse = warehouse
        self.database = database
        self.schema = schema

        # Create connection
        self.connection = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema
        )

        # Create SQLAlchemy engine
        self.engine = create_engine(
            f"snowflake://{user}:{password}@{account}/{database}/{schema}"
            f"?warehouse={warehouse}"
        )

    def query(self, sql: str) -> pd.DataFrame:
        """Execute query and return pandas DataFrame"""
        return pd.read_sql(sql, self.engine)

    def execute(self, sql: str) -> None:
        """Execute query without returning results"""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        cursor.close()

    def insert_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
        """Insert DataFrame into Snowflake table"""
        df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)

    def close(self):
        """Close connection"""
        self.connection.close()

class ProductMetricsQueries:
    def __init__(self, snowflake_client: SnowflakeProductAnalytics):
        self.client = snowflake_client

    def get_daily_active_users(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get daily active users"""
        sql = f"""
            SELECT
                DATE(event_timestamp) as date,
                COUNT(DISTINCT user_id) as dau,
                COUNT(DISTINCT session_id) as sessions
            FROM events
            WHERE event_timestamp BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY DATE(event_timestamp)
            ORDER BY date DESC
        """

        return self.client.query(sql)

    def get_feature_adoption(self, feature_name: str, days: int = 30) -> pd.DataFrame:
        """Get feature adoption metrics"""
        sql = f"""
            SELECT
                DATE(event_timestamp) as date,
                COUNT(DISTINCT user_id) as users_using_feature,
                COUNT(*) as feature_events
            FROM events
            WHERE event_type = 'feature_used'
            AND event_properties['feature_name'] = '{feature_name}'
            AND event_timestamp >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY DATE(event_timestamp)
            ORDER BY date DESC
        """

        return self.client.query(sql)

    def get_conversion_funnel(self, funnel_steps: List[str], days: int = 30) -> Dict:
        """Get conversion funnel metrics"""
        funnel_sql = f"""
            WITH funnel_users AS (
                SELECT DISTINCT user_id
                FROM events
                WHERE event_type = '{funnel_steps[0]}'
                AND event_timestamp >= DATEADD(day, -{days}, CURRENT_DATE())
            )
        """

        step_conversions = {}

        for i, step in enumerate(funnel_steps):
            sql = f"""
                SELECT COUNT(DISTINCT user_id) as users
                FROM events
                WHERE event_type = '{step}'
                AND event_timestamp >= DATEADD(day, -{days}, CURRENT_DATE())
            """

            result = self.client.query(sql)
            step_conversions[step] = result['users'].values[0]

        return {
            'funnel_steps': funnel_steps,
            'conversions': step_conversions,
            'conversion_rates': self._calculate_conversion_rates(step_conversions)
        }

    def get_user_retention(self, cohort_date: str, retention_days: int = 30) -> pd.DataFrame:
        """Get user retention by cohort"""
        sql = f"""
            WITH first_seen AS (
                SELECT
                    user_id,
                    MIN(DATE(event_timestamp)) as first_date
                FROM events
                GROUP BY user_id
            ),
            cohort_users AS (
                SELECT user_id
                FROM first_seen
                WHERE first_date = '{cohort_date}'
            ),
            retention_data AS (
                SELECT
                    c.user_id,
                    DATE(e.event_timestamp) as active_date,
                    DATEDIFF(day, '{cohort_date}', DATE(e.event_timestamp)) as days_retained
                FROM cohort_users c
                JOIN events e ON c.user_id = e.user_id
                WHERE e.event_timestamp >= '{cohort_date}'
            )
            SELECT
                days_retained,
                COUNT(DISTINCT user_id) as users_retained,
                ROUND(100.0 * COUNT(DISTINCT user_id) /
                    (SELECT COUNT(*) FROM cohort_users), 2) as retention_percentage
            FROM retention_data
            WHERE days_retained <= {retention_days}
            GROUP BY days_retained
            ORDER BY days_retained
        """

        return self.client.query(sql)

    def get_product_health_metrics(self) -> Dict:
        """Get overall product health metrics"""
        metrics = {}

        # DAU
        dau_sql = """
            SELECT COUNT(DISTINCT user_id) as value
            FROM events
            WHERE DATE(event_timestamp) = CURRENT_DATE()
        """
        metrics['dau'] = self.client.query(dau_sql)['value'].values[0]

        # Churn rate
        churn_sql = """
            SELECT
                ROUND(100.0 * COUNT(DISTINCT CASE
                    WHEN last_active < DATEADD(day, -7, CURRENT_DATE()) THEN user_id
                END) / COUNT(DISTINCT user_id), 2) as value
            FROM user_summary
        """
        metrics['churn_rate'] = self.client.query(churn_sql)['value'].values[0]

        # Feature discovery
        feature_sql = """
            SELECT COUNT(DISTINCT event_properties['feature_name']) as value
            FROM events
            WHERE event_type = 'feature_used'
        """
        metrics['features_used'] = self.client.query(feature_sql)['value'].values[0]

        return metrics

    @staticmethod
    def _calculate_conversion_rates(conversions: Dict) -> Dict:
        """Calculate step-to-step conversion rates"""
        rates = {}
        values = list(conversions.values())

        for i in range(len(values) - 1):
            if values[i] > 0:
                rate = (values[i + 1] / values[i]) * 100
                step_name = f"step_{i}_to_{i+1}"
                rates[step_name] = round(rate, 2)

        return rates
```

### Data Modeling Best Practices

```python
class DataWarehouseSchema:
    """Define recommended schema for product analytics"""

    @staticmethod
    def create_events_table(client: SnowflakeProductAnalytics):
        """Create events table"""
        sql = """
            CREATE TABLE IF NOT EXISTS events (
                event_id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                session_id VARCHAR,
                event_type VARCHAR NOT NULL,
                event_timestamp TIMESTAMP NOT NULL,
                event_properties VARIANT,
                user_properties VARIANT,
                platform VARCHAR,
                country VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            CLUSTER BY (user_id, event_timestamp)
        """

        client.execute(sql)

    @staticmethod
    def create_users_table(client: SnowflakeProductAnalytics):
        """Create users table"""
        sql = """
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR PRIMARY KEY,
                email VARCHAR,
                signup_date DATE,
                plan VARCHAR,
                company_id VARCHAR,
                user_properties VARIANT,
                last_active TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        client.execute(sql)

    @staticmethod
    def create_features_table(client: SnowflakeProductAnalytics):
        """Create features table"""
        sql = """
            CREATE TABLE IF NOT EXISTS features (
                feature_id VARCHAR PRIMARY KEY,
                feature_name VARCHAR NOT NULL,
                description VARCHAR,
                launch_date DATE,
                rollout_percentage NUMBER(3, 1),
                status VARCHAR,
                team_owner VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        client.execute(sql)

    @staticmethod
    def create_user_segments_table(client: SnowflakeProductAnalytics):
        """Create user segments table"""
        sql = """
            CREATE TABLE IF NOT EXISTS user_segments (
                segment_id VARCHAR PRIMARY KEY,
                segment_name VARCHAR NOT NULL,
                segment_definition OBJECT,
                user_count INTEGER,
                created_date DATE,
                updated_date DATE
            )
        """

        client.execute(sql)
```

---

## BigQuery Integration

### Authentication & Setup

BigQuery uses Google Cloud credentials for authentication.

```bash
# Environment setup
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GCP_PROJECT_ID=your-project-id
BIGQUERY_DATASET=product_analytics
```

#### BigQuery Client Implementation

```python
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from typing import List, Dict, Optional

class BigQueryProductAnalytics:
    def __init__(self, project_id: str, dataset_id: str, credentials_path: str = None):
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = bigquery.Client(project=project_id, credentials=credentials)
        else:
            self.client = bigquery.Client(project=project_id)

        self.project_id = project_id
        self.dataset_id = dataset_id

    def query(self, sql: str) -> pd.DataFrame:
        """Execute query and return results as DataFrame"""
        query_job = self.client.query(sql)
        return query_job.result().to_dataframe()

    def insert_dataframe(self, df: pd.DataFrame, table_id: str,
                        if_exists: str = 'append') -> bool:
        """Insert DataFrame into BigQuery table"""
        full_table_id = f"{self.project_id}.{self.dataset_id}.{table_id}"

        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")

        job = self.client.load_table_from_dataframe(
            df,
            full_table_id,
            job_config=job_config
        )

        job.result()

        return True

    def create_table(self, table_id: str, schema: List):
        """Create BigQuery table"""
        full_table_id = f"{self.project_id}.{self.dataset_id}.{table_id}"

        table = bigquery.Table(full_table_id, schema=schema)
        table = self.client.create_table(table)

        print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

class BigQueryProductMetrics:
    def __init__(self, bq_client: BigQueryProductAnalytics):
        self.client = bq_client

    def get_user_journey_funnel(self, user_id: str) -> pd.DataFrame:
        """Get user's journey through product"""
        sql = f"""
            SELECT
                event_id,
                event_timestamp,
                event_type,
                event_properties,
                ROW_NUMBER() OVER (ORDER BY event_timestamp) as step_number
            FROM `{self.client.project_id}.{self.client.dataset_id}.events`
            WHERE user_id = '{user_id}'
            ORDER BY event_timestamp
        """

        return self.client.query(sql)

    def get_cohort_analysis(self, cohort_property: str, cohort_value: str,
                           retention_weeks: int = 12) -> pd.DataFrame:
        """Perform cohort analysis"""
        sql = f"""
            WITH cohort_users AS (
                SELECT DISTINCT user_id
                FROM `{self.client.project_id}.{self.client.dataset_id}.users`
                WHERE {cohort_property} = '{cohort_value}'
            ),
            user_activity AS (
                SELECT
                    e.user_id,
                    DATE_TRUNC(DATE(e.event_timestamp), WEEK) as activity_week,
                    COUNT(*) as event_count
                FROM `{self.client.project_id}.{self.client.dataset_id}.events` e
                JOIN cohort_users c ON e.user_id = c.user_id
                GROUP BY user_id, activity_week
            ),
            cohort_start_week AS (
                SELECT
                    user_id,
                    MIN(activity_week) as cohort_week
                FROM user_activity
                GROUP BY user_id
            )
            SELECT
                DATE_DIFF(ua.activity_week, cs.cohort_week, WEEK) as weeks_since_start,
                COUNT(DISTINCT ua.user_id) as active_users,
                ROUND(100.0 * COUNT(DISTINCT ua.user_id) /
                    (SELECT COUNT(*) FROM cohort_users), 2) as retention_percentage
            FROM user_activity ua
            JOIN cohort_start_week cs ON ua.user_id = cs.user_id
            WHERE DATE_DIFF(ua.activity_week, cs.cohort_week, WEEK) <= {retention_weeks}
            GROUP BY weeks_since_start
            ORDER BY weeks_since_start
        """

        return self.client.query(sql)

    def get_segment_comparison(self, segments: Dict[str, str]) -> Dict:
        """Compare metrics across user segments"""
        segment_metrics = {}

        for segment_name, segment_filter in segments.items():
            sql = f"""
                SELECT
                    COUNT(DISTINCT user_id) as total_users,
                    COUNT(DISTINCT CASE WHEN last_active >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
                        THEN user_id END) as active_users,
                    ROUND(SUM(lifetime_value) / COUNT(DISTINCT user_id), 2) as avg_ltv
                FROM `{self.client.project_id}.{self.client.dataset_id}.users`
                WHERE {segment_filter}
            """

            result = self.client.query(sql)
            segment_metrics[segment_name] = result.to_dict('records')[0]

        return segment_metrics

    def get_feature_impact_analysis(self, feature_name: str, days: int = 30) -> Dict:
        """Analyze impact of feature on product metrics"""
        sql = f"""
            WITH feature_users AS (
                SELECT DISTINCT user_id
                FROM `{self.client.project_id}.{self.client.dataset_id}.events`
                WHERE event_type = 'feature_used'
                AND event_properties.feature_name = '{feature_name}'
                AND event_timestamp >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            ),
            metrics AS (
                SELECT
                    CASE WHEN user_id IN (SELECT user_id FROM feature_users)
                        THEN 'used_feature'
                        ELSE 'not_used' END as group_type,
                    COUNT(DISTINCT user_id) as user_count,
                    AVG(session_duration_minutes) as avg_session_duration,
                    COUNT(DISTINCT event_id) / COUNT(DISTINCT user_id) as events_per_user
                FROM `{self.client.project_id}.{self.client.dataset_id}.events`
                WHERE event_timestamp >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                GROUP BY group_type
            )
            SELECT * FROM metrics
        """

        result = self.client.query(sql)

        metrics_dict = result.to_dict('records')

        return {
            'feature_name': feature_name,
            'analysis_period_days': days,
            'group_comparison': metrics_dict
        }
```

### Scheduled Analytics Queries

```python
from google.cloud import bigquery
from google.cloud import scheduler_v1
from google.protobuf.duration_pb2 import Duration
import json

class ScheduledAnalyticsQueries:
    def __init__(self, project_id: str, location: str = 'us-central1'):
        self.project_id = project_id
        self.location = location
        self.scheduler_client = scheduler_v1.CloudSchedulerClient()

    def create_daily_metrics_report(self) -> str:
        """Create scheduled daily metrics report"""
        parent = self.scheduler_client.common_project_path(self.project_id, self.location)

        job = {
            'display_name': 'Daily Product Metrics Report',
            'http_target': {
                'uri': 'https://your-function-url.cloudfunctions.net/daily-metrics',
                'http_method': 'POST',
                'headers': {
                    'Content-Type': 'application/json'
                }
            },
            'schedule': '0 6 * * *',  # 6 AM daily
            'time_zone': 'America/New_York'
        }

        response = self.scheduler_client.create_job(request={'parent': parent, 'job': job})

        return response.name

    def create_weekly_cohort_report(self) -> str:
        """Create scheduled weekly cohort analysis"""
        parent = self.scheduler_client.common_project_path(self.project_id, self.location)

        job = {
            'display_name': 'Weekly Cohort Analysis',
            'http_target': {
                'uri': 'https://your-function-url.cloudfunctions.net/weekly-cohorts',
                'http_method': 'POST'
            },
            'schedule': '0 9 ? * MON',  # 9 AM Mondays
            'time_zone': 'America/New_York'
        }

        response = self.scheduler_client.create_job(request={'parent': parent, 'job': job})

        return response.name
```

---

## Data Pipeline Integration

### ETL from Product Systems to Data Warehouse

```python
import asyncio
from typing import List, Callable

class ProductDataPipeline:
    def __init__(self, source_apis: dict, warehouse_client):
        self.source_apis = source_apis
        self.warehouse = warehouse_client
        self.transformations = {}

    def register_transformation(self, source_name: str, transform_func: Callable):
        """Register data transformation function"""
        self.transformations[source_name] = transform_func

    async def extract_data(self, source_name: str) -> List[dict]:
        """Extract data from source"""
        if source_name not in self.source_apis:
            raise ValueError(f"Unknown source: {source_name}")

        source_client = self.source_apis[source_name]

        # Implementation depends on source type
        return await source_client.fetch_data()

    def transform_data(self, source_name: str, raw_data: List[dict]) -> List[dict]:
        """Transform raw data"""
        if source_name not in self.transformations:
            return raw_data

        transform_func = self.transformations[source_name]

        return [transform_func(record) for record in raw_data]

    def load_data(self, table_name: str, data: List[dict]):
        """Load transformed data into warehouse"""
        import pandas as pd

        df = pd.DataFrame(data)

        self.warehouse.insert_dataframe(df, table_name)

    async def run_full_pipeline(self, source_name: str, table_name: str):
        """Run complete ETL pipeline"""
        # Extract
        raw_data = await self.extract_data(source_name)

        print(f"Extracted {len(raw_data)} records from {source_name}")

        # Transform
        transformed_data = self.transform_data(source_name, raw_data)

        print(f"Transformed {len(transformed_data)} records")

        # Load
        self.load_data(table_name, transformed_data)

        print(f"Loaded data into {table_name}")

        return len(transformed_data)

class DataQualityChecks:
    def __init__(self, warehouse_client):
        self.warehouse = warehouse_client

    def validate_table_freshness(self, table_name: str, max_age_hours: int = 24) -> bool:
        """Check if table data is fresh"""
        sql = f"""
            SELECT
                EXTRACT(HOUR FROM CURRENT_TIMESTAMP() - MAX(updated_at)) as hours_old
            FROM {table_name}
        """

        try:
            result = self.warehouse.query(sql)
            hours_old = result['hours_old'].values[0]

            return hours_old < max_age_hours

        except Exception as e:
            print(f"Data freshness check failed: {e}")

            return False

    def validate_data_completeness(self, table_name: str, required_columns: List[str]) -> bool:
        """Check if required columns have data"""
        for column in required_columns:
            sql = f"""
                SELECT COUNT(*) as null_count
                FROM {table_name}
                WHERE {column} IS NULL
            """

            result = self.warehouse.query(sql)
            null_count = result['null_count'].values[0]

            if null_count > 0:
                print(f"Column {column} has {null_count} null values")

                return False

        return True

    def detect_anomalies(self, table_name: str, metric_column: str,
                        threshold_std_dev: float = 3.0) -> List[dict]:
        """Detect anomalies in metric data"""
        sql = f"""
            SELECT
                {metric_column},
                AVG({metric_column}) OVER () as mean_value,
                STDDEV({metric_column}) OVER () as std_dev,
                ABS({metric_column} - AVG({metric_column}) OVER ()) /
                    STDDEV({metric_column}) OVER () as z_score
            FROM {table_name}
            WHERE ABS({metric_column} - AVG({metric_column}) OVER ()) /
                    STDDEV({metric_column}) OVER () > {threshold_std_dev}
        """

        result = self.warehouse.query(sql)

        return result.to_dict('records')
```

---

## Advanced Analytics

### Product Health Dashboard Queries

```python
class ProductHealthDashboard:
    def __init__(self, warehouse_client):
        self.warehouse = warehouse_client

    def get_core_metrics(self) -> Dict:
        """Get core product health metrics"""
        return {
            'dau': self._get_dau(),
            'mau': self._get_mau(),
            'churn_rate': self._get_churn_rate(),
            'engagement_score': self._get_engagement_score(),
            'feature_adoption': self._get_feature_adoption()
        }

    def _get_dau(self) -> int:
        """Daily Active Users"""
        sql = """
            SELECT COUNT(DISTINCT user_id)
            FROM events
            WHERE DATE(event_timestamp) = CURRENT_DATE()
        """

        result = self.warehouse.query(sql)

        return result.iloc[0, 0]

    def _get_mau(self) -> int:
        """Monthly Active Users"""
        sql = """
            SELECT COUNT(DISTINCT user_id)
            FROM events
            WHERE event_timestamp >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        """

        result = self.warehouse.query(sql)

        return result.iloc[0, 0]

    def _get_churn_rate(self) -> float:
        """Calculate churn rate"""
        sql = """
            SELECT
                ROUND(100.0 * COUNT(CASE WHEN days_since_active > 30 THEN 1 END) /
                    COUNT(*), 2) as churn_rate
            FROM (
                SELECT user_id,
                    DATE_DIFF(CURRENT_DATE(), MAX(DATE(event_timestamp)), DAY) as days_since_active
                FROM events
                GROUP BY user_id
            )
        """

        result = self.warehouse.query(sql)

        return result['churn_rate'].values[0]

    def _get_engagement_score(self) -> float:
        """Calculate overall engagement score"""
        sql = """
            SELECT
                ROUND(
                    (dau_score * 0.3 +
                     session_score * 0.3 +
                     feature_score * 0.4), 2
                ) as engagement_score
            FROM (
                SELECT
                    (COUNT(DISTINCT user_id) / MAX_DAU) * 100 as dau_score,
                    (AVG(sessions_per_user)) as session_score,
                    (COUNT(DISTINCT feature_id) / MAX_FEATURES) * 100 as feature_score
                FROM events_summary,
                (SELECT 100 as MAX_DAU, 50 as MAX_FEATURES)
            )
        """

        result = self.warehouse.query(sql)

        return result['engagement_score'].values[0]

    def _get_feature_adoption(self) -> Dict:
        """Get adoption rates for top features"""
        sql = """
            SELECT
                event_properties['feature_name'] as feature_name,
                COUNT(DISTINCT user_id) as adopted_users,
                ROUND(100.0 * COUNT(DISTINCT user_id) /
                    (SELECT COUNT(*) FROM users), 2) as adoption_rate
            FROM events
            WHERE event_type = 'feature_used'
            GROUP BY feature_name
            ORDER BY adopted_users DESC
            LIMIT 10
        """

        result = self.warehouse.query(sql)

        return result.to_dict('records')
```

---

## Conclusion

Data warehouse integration is essential for scaling product analytics. By connecting product systems to Snowflake or BigQuery, product managers gain access to powerful analytics capabilities needed for data-driven decision making.

Key takeaways:
- Design schema for efficient product analytics queries
- Implement data quality checks and anomaly detection
- Create ETL pipelines for consistent data flow
- Build reusable metric definitions for consistency
- Schedule automated reports and dashboards
- Monitor data freshness and quality
- Document schema and calculation methods
- Use proper authentication and security practices
