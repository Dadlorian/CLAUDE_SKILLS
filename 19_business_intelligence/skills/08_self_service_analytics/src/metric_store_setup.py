"""
Metric Store Setup and Configuration
Production-ready setup for centralized metric management system.

This module handles:
- Metric definition registration
- Store initialization and schema creation
- Metric versioning and lineage tracking
- Performance indexing
- Metadata catalog updates
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricCalculationType(Enum):
    """Types of metric calculations supported."""
    SUM = "sum"
    COUNT = "count"
    COUNT_DISTINCT = "count_distinct"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    RATIO = "ratio"
    DERIVED = "derived"
    CUSTOM = "custom"


class MetricCertification(Enum):
    """Certification status for metrics."""
    DRAFT = "draft"
    PROPOSED = "proposed"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"


@dataclass
class MetricDefinition:
    """Represents a metric definition."""
    name: str
    label: str
    description: str
    calculation_type: MetricCalculationType
    owner_team: str
    expression: str
    source_table: str
    timestamp_column: Optional[str] = None
    grain: Optional[str] = None
    dimensions: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    sla: Optional[str] = None
    certification: MetricCertification = MetricCertification.DRAFT
    tags: Optional[List[str]] = None
    depends_on: Optional[List[str]] = None
    time_grains: Optional[List[str]] = None

    def compute_hash(self) -> str:
        """Generate hash of metric definition for versioning."""
        definition_str = json.dumps(asdict(self), default=str, sort_keys=True)
        return hashlib.sha256(definition_str.encode()).hexdigest()[:12]

    def validate(self) -> tuple[bool, List[str]]:
        """Validate metric definition."""
        errors = []

        # Required fields
        if not self.name or not self.name.replace('_', '').isalnum():
            errors.append("Metric name must be alphanumeric with underscores")

        if not self.owner_team:
            errors.append("Owner team is required")

        if not self.expression or len(self.expression.strip()) < 5:
            errors.append("Expression must be non-empty and meaningful")

        # Expression validation
        if self.calculation_type == MetricCalculationType.RATIO:
            if not self.depends_on or len(self.depends_on) < 2:
                errors.append("Ratio metrics must have exactly 2 dependencies")

        # Timestamp required for time-series metrics
        if self.time_grains and not self.timestamp_column:
            errors.append("Timestamp column required when defining time grains")

        return len(errors) == 0, errors


class MetricStore:
    """
    Production metric store management system.
    Handles registration, versioning, and querying of metrics.
    """

    def __init__(self, warehouse_connection, metadata_db_connection):
        """
        Initialize metric store.

        Args:
            warehouse_connection: Connection to data warehouse
            metadata_db_connection: Connection to metadata database (PostgreSQL)
        """
        self.warehouse_conn = warehouse_connection
        self.metadata_conn = metadata_db_connection
        self.metrics_registry: Dict[str, MetricDefinition] = {}
        logger.info("MetricStore initialized")

    def initialize_schema(self) -> bool:
        """Create required schema and tables in metadata database."""
        try:
            cursor = self.metadata_conn.cursor()

            # Metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics_registry (
                    metric_id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    label VARCHAR(512) NOT NULL,
                    description TEXT,
                    calculation_type VARCHAR(50) NOT NULL,
                    owner_team VARCHAR(255) NOT NULL,
                    expression TEXT NOT NULL,
                    source_table VARCHAR(255) NOT NULL,
                    timestamp_column VARCHAR(255),
                    grain VARCHAR(50),
                    dimensions JSONB,
                    filters JSONB,
                    sla VARCHAR(100),
                    certification VARCHAR(50) NOT NULL DEFAULT 'draft',
                    tags JSONB,
                    depends_on JSONB,
                    time_grains JSONB,
                    definition_hash VARCHAR(12),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(255),
                    updated_by VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            # Metric versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics_versions (
                    version_id SERIAL PRIMARY KEY,
                    metric_id VARCHAR(255) NOT NULL REFERENCES metrics_registry(metric_id),
                    definition_hash VARCHAR(12) NOT NULL,
                    definition_json JSONB NOT NULL,
                    changed_by VARCHAR(255),
                    change_reason TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_current BOOLEAN DEFAULT FALSE
                )
            """)

            # Metric lineage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics_lineage (
                    lineage_id SERIAL PRIMARY KEY,
                    source_metric_id VARCHAR(255),
                    target_metric_id VARCHAR(255) REFERENCES metrics_registry(metric_id),
                    dependency_type VARCHAR(50),
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            # Query execution log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metric_query_log (
                    query_id VARCHAR(255) PRIMARY KEY,
                    metric_id VARCHAR(255) REFERENCES metrics_registry(metric_id),
                    query_sql TEXT,
                    execution_time_ms INT,
                    result_rows INT,
                    status VARCHAR(50),
                    error_message TEXT,
                    executed_by VARCHAR(255),
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    warehouse_credits DECIMAL(10, 2)
                )
            """)

            # Create indexes for performance
            cursor.execute("CREATE INDEX idx_metrics_name ON metrics_registry(name)")
            cursor.execute("CREATE INDEX idx_metrics_owner ON metrics_registry(owner_team)")
            cursor.execute("CREATE INDEX idx_metrics_cert ON metrics_registry(certification)")
            cursor.execute("CREATE INDEX idx_versions_metric ON metrics_versions(metric_id)")
            cursor.execute("CREATE INDEX idx_lineage_target ON metrics_lineage(target_metric_id)")

            self.metadata_conn.commit()
            logger.info("Metric store schema initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize schema: {str(e)}")
            self.metadata_conn.rollback()
            return False

    def register_metric(self, metric: MetricDefinition, created_by: str) -> tuple[bool, str]:
        """
        Register a new metric in the store.

        Args:
            metric: MetricDefinition object
            created_by: Email of user registering metric

        Returns:
            Tuple of (success, message_or_metric_id)
        """
        # Validate metric
        is_valid, errors = metric.validate()
        if not is_valid:
            error_msg = "; ".join(errors)
            logger.warning(f"Metric validation failed: {error_msg}")
            return False, error_msg

        try:
            definition_hash = metric.compute_hash()
            metric_id = f"{metric.name}_{definition_hash}"

            cursor = self.metadata_conn.cursor()

            # Insert into metrics_registry
            cursor.execute("""
                INSERT INTO metrics_registry (
                    metric_id, name, label, description, calculation_type,
                    owner_team, expression, source_table, timestamp_column,
                    grain, dimensions, filters, sla, certification, tags,
                    depends_on, time_grains, definition_hash, created_by, updated_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                metric_id, metric.name, metric.label, metric.description,
                metric.calculation_type.value, metric.owner_team, metric.expression,
                metric.source_table, metric.timestamp_column, metric.grain,
                json.dumps(metric.dimensions), json.dumps(metric.filters),
                metric.sla, metric.certification.value, json.dumps(metric.tags),
                json.dumps(metric.depends_on), json.dumps(metric.time_grains),
                definition_hash, created_by, created_by
            ))

            # Record initial version
            cursor.execute("""
                INSERT INTO metrics_versions (
                    metric_id, definition_hash, definition_json, changed_by, is_current
                ) VALUES (%s, %s, %s, %s, TRUE)
            """, (
                metric_id, definition_hash,
                json.dumps(asdict(metric), default=str),
                created_by
            ))

            self.metadata_conn.commit()
            self.metrics_registry[metric.name] = metric

            logger.info(f"Metric '{metric.name}' registered with ID: {metric_id}")
            return True, metric_id

        except Exception as e:
            logger.error(f"Failed to register metric: {str(e)}")
            self.metadata_conn.rollback()
            return False, str(e)

    def update_metric(self, metric_id: str, metric: MetricDefinition, updated_by: str, reason: str = None) -> bool:
        """Update existing metric definition."""
        try:
            definition_hash = metric.compute_hash()

            cursor = self.metadata_conn.cursor()

            # Update registry
            cursor.execute("""
                UPDATE metrics_registry
                SET label = %s, description = %s, expression = %s,
                    dimensions = %s, filters = %s, sla = %s,
                    definition_hash = %s, updated_at = CURRENT_TIMESTAMP,
                    updated_by = %s
                WHERE metric_id = %s
            """, (
                metric.label, metric.description, metric.expression,
                json.dumps(metric.dimensions), json.dumps(metric.filters),
                metric.sla, definition_hash, updated_by, metric_id
            ))

            # Record new version
            cursor.execute("""
                UPDATE metrics_versions SET is_current = FALSE WHERE metric_id = %s;
                INSERT INTO metrics_versions (
                    metric_id, definition_hash, definition_json, changed_by, change_reason, is_current
                ) VALUES (%s, %s, %s, %s, %s, TRUE)
            """, (
                metric_id, metric_id, definition_hash,
                json.dumps(asdict(metric), default=str),
                updated_by, reason
            ))

            self.metadata_conn.commit()
            logger.info(f"Metric {metric_id} updated")
            return True

        except Exception as e:
            logger.error(f"Failed to update metric: {str(e)}")
            self.metadata_conn.rollback()
            return False

    def get_metric(self, metric_name: str) -> Optional[MetricDefinition]:
        """Retrieve metric definition by name."""
        try:
            cursor = self.metadata_conn.cursor()
            cursor.execute("""
                SELECT * FROM metrics_registry
                WHERE name = %s AND is_active = TRUE
            """, (metric_name,))

            row = cursor.fetchone()
            if row:
                # Reconstruct MetricDefinition from row
                logger.info(f"Retrieved metric: {metric_name}")
                return row  # In production, properly deserialize
            return None

        except Exception as e:
            logger.error(f"Failed to get metric: {str(e)}")
            return None

    def set_certification(self, metric_id: str, certification: MetricCertification, updated_by: str) -> bool:
        """Update metric certification status."""
        try:
            cursor = self.metadata_conn.cursor()
            cursor.execute("""
                UPDATE metrics_registry
                SET certification = %s, updated_by = %s, updated_at = CURRENT_TIMESTAMP
                WHERE metric_id = %s
            """, (certification.value, updated_by, metric_id))

            self.metadata_conn.commit()
            logger.info(f"Metric {metric_id} certification set to {certification.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to update certification: {str(e)}")
            return False

    def get_lineage_graph(self) -> Dict[str, List[str]]:
        """Get metric dependency graph."""
        try:
            cursor = self.metadata_conn.cursor()
            cursor.execute("""
                SELECT source_metric_id, target_metric_id
                FROM metrics_lineage
                WHERE is_active = TRUE
            """)

            graph = {}
            for source, target in cursor.fetchall():
                if target not in graph:
                    graph[target] = []
                graph[target].append(source)

            return graph

        except Exception as e:
            logger.error(f"Failed to get lineage: {str(e)}")
            return {}


# Example usage
if __name__ == "__main__":
    # This would be called during system initialization
    # In production, actual database connections would be used

    mrr_metric = MetricDefinition(
        name="monthly_recurring_revenue",
        label="Monthly Recurring Revenue",
        description="Sum of all active subscription amounts",
        calculation_type=MetricCalculationType.SUM,
        owner_team="finance_analytics",
        expression="SUM(subscription_amount)",
        source_table="fct_subscriptions",
        timestamp_column="subscription_date",
        sla="daily_by_9am",
        certification=MetricCertification.VERIFIED,
        tags=["revenue", "finance"],
        time_grains=["day", "week", "month"],
        dimensions=["subscription_tier", "region"]
    )

    is_valid, errors = mrr_metric.validate()
    print(f"Metric valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
