"""
Time-Series Database Integration for Industrial IoT

This module provides interfaces and implementations for:
- InfluxDB integration (high-volume metrics)
- TimescaleDB/PostgreSQL integration (complex queries)
- Data retention and rollup policies
- Time-series specific optimizations
- Batch writing and buffering
- Data downsampling
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesPoint:
    """Single time-series data point"""
    timestamp: datetime
    measurement: str  # e.g., "equipment_metrics"
    tags: Dict[str, str]  # e.g., {"facility": "plant-01", "equipment": "robot-01"}
    fields: Dict[str, float]  # e.g., {"temperature": 45.5, "vibration": 0.25}
    value: Optional[float] = None  # For single-value points

    def to_line_protocol(self) -> str:
        """Convert to InfluxDB line protocol format"""
        # Build tag string
        tag_str = ",".join(f"{k}={v}" for k, v in self.tags.items())

        # Build field string
        if self.value is not None:
            field_str = f"value={self.value}"
        else:
            field_str = ",".join(
                f"{k}={v}" if isinstance(v, (int, float)) else f'{k}="{v}"'
                for k, v in self.fields.items()
            )

        # Convert timestamp to nanoseconds
        timestamp_ns = int(self.timestamp.timestamp() * 1e9)

        return f"{self.measurement},{tag_str} {field_str} {timestamp_ns}"


class TimeSeriesDatabase(ABC):
    """Abstract base class for time-series databases"""

    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection"""
        pass

    @abstractmethod
    def write_point(self, point: TimeSeriesPoint) -> bool:
        """Write single point"""
        pass

    @abstractmethod
    def write_batch(self, points: List[TimeSeriesPoint]) -> bool:
        """Write multiple points"""
        pass

    @abstractmethod
    def query(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Execute query"""
        pass

    @abstractmethod
    def delete_old_data(self, older_than: datetime) -> int:
        """Delete data older than specified time"""
        pass

    @abstractmethod
    def get_data_size(self) -> int:
        """Get total data size"""
        pass


class InfluxDBClient(TimeSeriesDatabase):
    """InfluxDB client for high-performance metrics storage"""

    def __init__(
        self,
        url: str = "http://localhost:8086",
        token: str = "",
        org: str = "manufacturing",
        bucket: str = "manufacturing",
        timeout: int = 5000
    ):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.timeout = timeout
        self.client = None
        self.write_api = None
        self.query_api = None

    def connect(self) -> bool:
        """Connect to InfluxDB"""
        try:
            from influxdb_client import InfluxDBClient as InfluxClient
            from influxdb_client.client.write_api import SYNCHRONOUS

            self.client = InfluxClient(
                url=self.url,
                token=self.token,
                org=self.org,
                timeout=self.timeout
            )

            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()

            # Test connection
            health = self.client.health()
            logger.info(f"Connected to InfluxDB: {health}")
            return True

        except ImportError:
            logger.error("influxdb-client not installed: pip install influxdb-client")
            return False
        except Exception as e:
            logger.error(f"InfluxDB connection failed: {e}")
            return False

    def write_point(self, point: TimeSeriesPoint) -> bool:
        """Write single point to InfluxDB"""
        try:
            self.write_api.write(
                bucket=self.bucket,
                record=point.to_line_protocol()
            )
            return True
        except Exception as e:
            logger.error(f"Write failed: {e}")
            return False

    def write_batch(self, points: List[TimeSeriesPoint]) -> bool:
        """Write batch of points"""
        try:
            records = [p.to_line_protocol() for p in points]
            self.write_api.write(bucket=self.bucket, records=records)
            logger.debug(f"Wrote {len(points)} points")
            return True
        except Exception as e:
            logger.error(f"Batch write failed: {e}")
            return False

    def query(
        self,
        query: str,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """Execute Flux query"""
        try:
            if start_time is None:
                start_time = datetime.utcnow() - timedelta(hours=1)
            if end_time is None:
                end_time = datetime.utcnow()

            # Build Flux query
            flux_query = f"""
            from(bucket: "{self.bucket}")
            |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
            |> {query}
            """

            result = self.query_api.query(query=flux_query)

            records = []
            for table in result:
                for record in table.records:
                    records.append({
                        "time": record.get_time(),
                        "measurement": record.get_measurement(),
                        "field": record.get_field(),
                        "value": record.get_value(),
                        "tags": record.tags
                    })

            return records

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

    def query_aggregated(
        self,
        measurement: str,
        aggregation: str = "mean",  # mean, sum, max, min
        interval: str = "1h",
        start_time: datetime = None,
        end_time: datetime = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Query with aggregation"""
        try:
            if start_time is None:
                start_time = datetime.utcnow() - timedelta(hours=24)
            if end_time is None:
                end_time = datetime.utcnow()

            # Build filter
            filter_str = f'|> filter(fn: (r) => r._measurement == "{measurement}")'
            if tags:
                for key, value in tags.items():
                    filter_str += f' |> filter(fn: (r) => r.{key} == "{value}")'

            flux_query = f"""
            from(bucket: "{self.bucket}")
            |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
            {filter_str}
            |> aggregateWindow(every: {interval}, fn: {aggregation})
            """

            result = self.query_api.query(query=flux_query)

            records = []
            for table in result:
                for record in table.records:
                    records.append({
                        "time": record.get_time(),
                        "value": record.get_value(),
                        "field": record.get_field()
                    })

            return records

        except Exception as e:
            logger.error(f"Aggregated query failed: {e}")
            return []

    def delete_old_data(self, older_than: datetime) -> int:
        """Delete data older than specified time"""
        try:
            # InfluxDB 2.x uses delete API
            self.client.delete_api().delete(
                start=datetime.min,
                stop=older_than,
                bucket=self.bucket
            )
            logger.info(f"Deleted data older than {older_than}")
            return 1
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return 0

    def get_data_size(self) -> int:
        """Get approximate data size"""
        try:
            # Query bucket info
            buckets_api = self.client.buckets_api()
            buckets = buckets_api.find_bucket_by_name(self.bucket)
            # Note: Size info may not be directly available
            return 0
        except Exception as e:
            logger.error(f"Size query failed: {e}")
            return 0


class TimescaleDBClient(TimeSeriesDatabase):
    """TimescaleDB (PostgreSQL) client for time-series data"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "manufacturing",
        user: str = "postgres",
        password: str = "password"
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None

    def connect(self) -> bool:
        """Connect to TimescaleDB"""
        try:
            import psycopg2

            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )

            # Enable TimescaleDB extension
            cursor = self.conn.cursor()
            cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
            self.conn.commit()
            cursor.close()

            logger.info(f"Connected to TimescaleDB at {self.host}:{self.port}")
            return True

        except ImportError:
            logger.error("psycopg2 not installed: pip install psycopg2-binary")
            return False
        except Exception as e:
            logger.error(f"TimescaleDB connection failed: {e}")
            return False

    def create_hypertable(
        self,
        table_name: str,
        time_column: str = "timestamp"
    ) -> bool:
        """Create hypertable for time-series data"""
        try:
            cursor = self.conn.cursor()

            # Create regular table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {time_column} TIMESTAMP NOT NULL,
                    measurement TEXT NOT NULL,
                    tag_facility TEXT,
                    tag_equipment TEXT,
                    tag_device TEXT,
                    field_name TEXT,
                    value DOUBLE PRECISION
                )
            """)

            # Create hypertable
            cursor.execute(
                f"SELECT create_hypertable('{table_name}', '{time_column}', if_not_exists => TRUE)"
            )

            # Create indexes
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_measurement ON {table_name} (measurement, {time_column} DESC)"
            )
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_tags ON {table_name} (tag_facility, tag_equipment, tag_device)"
            )

            self.conn.commit()
            logger.info(f"Created hypertable: {table_name}")
            return True

        except Exception as e:
            logger.error(f"Hypertable creation failed: {e}")
            return False

    def write_point(self, point: TimeSeriesPoint) -> bool:
        """Write single point"""
        try:
            cursor = self.conn.cursor()

            for field_name, value in point.fields.items():
                cursor.execute("""
                    INSERT INTO metrics (
                        timestamp, measurement, tag_facility, tag_equipment,
                        tag_device, field_name, value
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    point.timestamp,
                    point.measurement,
                    point.tags.get("facility"),
                    point.tags.get("equipment"),
                    point.tags.get("device"),
                    field_name,
                    value
                ))

            self.conn.commit()
            return True

        except Exception as e:
            logger.error(f"Write failed: {e}")
            self.conn.rollback()
            return False

    def write_batch(self, points: List[TimeSeriesPoint]) -> bool:
        """Write batch of points"""
        try:
            cursor = self.conn.cursor()

            for point in points:
                for field_name, value in point.fields.items():
                    cursor.execute("""
                        INSERT INTO metrics (
                            timestamp, measurement, tag_facility, tag_equipment,
                            tag_device, field_name, value
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        point.timestamp,
                        point.measurement,
                        point.tags.get("facility"),
                        point.tags.get("equipment"),
                        point.tags.get("device"),
                        field_name,
                        value
                    ))

            self.conn.commit()
            logger.debug(f"Wrote {len(points)} points")
            return True

        except Exception as e:
            logger.error(f"Batch write failed: {e}")
            self.conn.rollback()
            return False

    def query(
        self,
        query: str,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """Execute SQL query"""
        try:
            if start_time is None:
                start_time = datetime.utcnow() - timedelta(hours=1)
            if end_time is None:
                end_time = datetime.utcnow()

            cursor = self.conn.cursor()
            cursor.execute(query, (start_time, end_time))

            columns = [desc[0] for desc in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()

            return records

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

    def query_recent(
        self,
        measurement: str,
        facility: str,
        equipment: str,
        hours: int = 1
    ) -> List[Dict[str, Any]]:
        """Query recent data"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT timestamp, field_name, value
                FROM metrics
                WHERE measurement = %s
                  AND tag_facility = %s
                  AND tag_equipment = %s
                  AND timestamp > NOW() - INTERVAL '%s hours'
                ORDER BY timestamp DESC
            """, (measurement, facility, equipment, hours))

            columns = [desc[0] for desc in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()

            return records

        except Exception as e:
            logger.error(f"Recent query failed: {e}")
            return []

    def delete_old_data(self, older_than: datetime) -> int:
        """Delete data older than specified time"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM metrics WHERE timestamp < %s",
                (older_than,)
            )
            deleted_rows = cursor.rowcount
            self.conn.commit()
            cursor.close()

            logger.info(f"Deleted {deleted_rows} rows older than {older_than}")
            return deleted_rows

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return 0

    def get_data_size(self) -> int:
        """Get data size in bytes"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT pg_total_relation_size('metrics')")
            size = cursor.fetchone()[0]
            cursor.close()
            return size

        except Exception as e:
            logger.error(f"Size query failed: {e}")
            return 0


class DataRetentionPolicy:
    """Manage data retention and rollup policies"""

    def __init__(self, database: TimeSeriesDatabase):
        self.database = database
        self.policies: Dict[str, Dict[str, Any]] = {}

    def add_policy(
        self,
        name: str,
        measurement: str,
        retention_hours: int,
        rollup_interval: str = "1h",
        rollup_function: str = "mean"
    ) -> None:
        """Add retention and rollup policy"""
        self.policies[name] = {
            "measurement": measurement,
            "retention_hours": retention_hours,
            "rollup_interval": rollup_interval,
            "rollup_function": rollup_function
        }

        logger.info(f"Added retention policy: {name}")

    def apply_policies(self) -> None:
        """Apply all retention policies"""
        for policy_name, policy in self.policies.items():
            retention_hours = policy["retention_hours"]
            older_than = datetime.utcnow() - timedelta(hours=retention_hours)

            logger.info(
                f"Applying {policy_name}: "
                f"deleting data older than {retention_hours} hours"
            )
            self.database.delete_old_data(older_than)


class BufferedWriter:
    """Buffer writes for efficiency"""

    def __init__(
        self,
        database: TimeSeriesDatabase,
        buffer_size: int = 1000,
        flush_interval: float = 60.0
    ):
        self.database = database
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.buffer: List[TimeSeriesPoint] = []
        self.last_flush = datetime.utcnow()

    def add_point(self, point: TimeSeriesPoint) -> None:
        """Add point to buffer"""
        self.buffer.append(point)

        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def should_flush(self) -> bool:
        """Check if buffer should be flushed"""
        time_since_flush = (datetime.utcnow() - self.last_flush).total_seconds()
        return time_since_flush >= self.flush_interval or len(self.buffer) >= self.buffer_size

    def flush(self) -> bool:
        """Flush buffer to database"""
        if not self.buffer:
            return True

        success = self.database.write_batch(self.buffer)

        if success:
            logger.debug(f"Flushed {len(self.buffer)} points")
            self.buffer.clear()
            self.last_flush = datetime.utcnow()

        return success


# Example usage
if __name__ == "__main__":
    # Example with InfluxDB
    influx = InfluxDBClient(
        url="http://localhost:8086",
        token="your-token-here",
        org="manufacturing",
        bucket="manufacturing"
    )

    if influx.connect():
        # Write test point
        point = TimeSeriesPoint(
            timestamp=datetime.utcnow(),
            measurement="equipment_metrics",
            tags={
                "facility": "plant-01",
                "equipment": "robot-01"
            },
            fields={
                "temperature": 45.5,
                "vibration": 0.25,
                "power": 125.8
            }
        )

        if influx.write_point(point):
            print("Point written successfully")

        # Query recent data
        try:
            results = influx.query_aggregated(
                measurement="equipment_metrics",
                aggregation="mean",
                interval="5m"
            )
            print(f"Query results: {len(results)} records")
        except:
            pass

    # Example with TimescaleDB
    timescale = TimescaleDBClient(
        host="localhost",
        database="manufacturing",
        user="postgres"
    )

    if timescale.connect():
        # Create hypertable
        timescale.create_hypertable("metrics", time_column="timestamp")

        # Setup retention policy
        policy = DataRetentionPolicy(timescale)
        policy.add_policy(
            name="standard_30day",
            measurement="equipment_metrics",
            retention_hours=30 * 24,
            rollup_interval="1h",
            rollup_function="mean"
        )

        # Use buffered writer for efficiency
        writer = BufferedWriter(timescale, buffer_size=100, flush_interval=30.0)

        for i in range(10):
            point = TimeSeriesPoint(
                timestamp=datetime.utcnow(),
                measurement="equipment_metrics",
                tags={"facility": "plant-01", "equipment": "motor-01"},
                fields={"speed": 1500 + i}
            )
            writer.add_point(point)

        writer.flush()
        print("TimescaleDB example completed")
