#!/usr/bin/env python3
"""
Data Catalog Automation
Automated metadata extraction and enrichment for analytics assets
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import yaml


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Supported data source types"""
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    POSTGRES = "postgres"
    MYSQL = "mysql"


class CertificationLevel(Enum):
    """Data certification levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


@dataclass
class ColumnMetadata:
    """Column metadata structure"""
    name: str
    data_type: str
    description: str
    nullable: bool = True
    is_primary_key: bool = False
    classifications: List[str] = None

    def __post_init__(self):
        if self.classifications is None:
            self.classifications = []


@dataclass
class TableMetadata:
    """Table metadata structure"""
    table_id: str
    table_name: str
    schema_name: str
    description: str
    owner: str
    owner_email: str
    row_count: int
    size_bytes: int
    columns: List[ColumnMetadata]
    last_modified: datetime
    certifications: List[CertificationLevel]
    business_domain: str
    refresh_interval: str

    def get_schema_hash(self) -> str:
        """Generate hash of current schema for change detection"""
        schema_str = json.dumps(
            {col.name: col.data_type for col in self.columns},
            sort_keys=True
        )
        return hashlib.md5(schema_str.encode()).hexdigest()


class CatalogConnector:
    """Abstract base for data source connections"""

    def __init__(self, source_type: DataSourceType, **kwargs):
        self.source_type = source_type
        self.config = kwargs
        self.connection = None

    def connect(self):
        """Establish connection to data source"""
        raise NotImplementedError

    def disconnect(self):
        """Close connection"""
        raise NotImplementedError

    def list_databases(self) -> List[str]:
        """List all databases"""
        raise NotImplementedError

    def list_tables(self, database: str, schema: str = None) -> List[str]:
        """List tables in database/schema"""
        raise NotImplementedError

    def get_table_metadata(self, database: str, schema: str, table: str) -> TableMetadata:
        """Extract metadata for specific table"""
        raise NotImplementedError


class SnowflakeConnector(CatalogConnector):
    """Snowflake-specific metadata extraction"""

    def __init__(self, **kwargs):
        super().__init__(DataSourceType.SNOWFLAKE, **kwargs)
        self.warehouse = kwargs.get('warehouse')
        self.database = kwargs.get('database')

    def connect(self):
        """Connect to Snowflake"""
        try:
            import snowflake.connector
            self.connection = snowflake.connector.connect(
                user=self.config.get('user'),
                password=self.config.get('password'),
                account=self.config.get('account'),
                warehouse=self.warehouse
            )
            logger.info("Connected to Snowflake")
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            raise

    def disconnect(self):
        """Disconnect from Snowflake"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from Snowflake")

    def list_databases(self) -> List[str]:
        """List Snowflake databases"""
        query = "SHOW DATABASES"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def list_tables(self, database: str, schema: str) -> List[str]:
        """List tables in Snowflake schema"""
        query = f"SHOW TABLES IN {database}.{schema}"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return [row[1] for row in cursor.fetchall()]

    def get_table_metadata(self, database: str, schema: str, table: str) -> TableMetadata:
        """Extract comprehensive table metadata from Snowflake"""
        cursor = self.connection.cursor()

        # Get row count and table size
        cursor.execute(f"""
            SELECT ROW_COUNT, BYTES
            FROM {database}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
        """)
        row_count, size_bytes = cursor.fetchone()

        # Get column information
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM {database}.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
            ORDER BY ORDINAL_POSITION
        """)

        columns = []
        for col_name, data_type, is_nullable in cursor.fetchall():
            columns.append(ColumnMetadata(
                name=col_name,
                data_type=data_type,
                description="",
                nullable=is_nullable == 'YES'
            ))

        # Get table comments
        cursor.execute(f"""
            SELECT COMMENT
            FROM {database}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
        """)
        description = cursor.fetchone()[0] or ""

        table_metadata = TableMetadata(
            table_id=f"{database}.{schema}.{table}",
            table_name=table,
            schema_name=schema,
            description=description,
            owner="unassigned",
            owner_email="unassigned@company.com",
            row_count=row_count,
            size_bytes=size_bytes,
            columns=columns,
            last_modified=datetime.utcnow(),
            certifications=[CertificationLevel.BRONZE],
            business_domain="uncategorized",
            refresh_interval="unknown"
        )

        return table_metadata


class MetadataStore:
    """Central metadata storage and retrieval"""

    def __init__(self, backend_type: str = "json", storage_path: str = "./metadata"):
        self.backend_type = backend_type
        self.storage_path = storage_path
        self.metadata_cache: Dict[str, TableMetadata] = {}

    def store_table_metadata(self, metadata: TableMetadata) -> bool:
        """Store table metadata"""
        try:
            self.metadata_cache[metadata.table_id] = metadata
            logger.info(f"Stored metadata for {metadata.table_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store metadata: {e}")
            return False

    def get_table_metadata(self, table_id: str) -> Optional[TableMetadata]:
        """Retrieve table metadata"""
        return self.metadata_cache.get(table_id)

    def list_all_metadata(self) -> List[TableMetadata]:
        """List all stored metadata"""
        return list(self.metadata_cache.values())

    def update_metadata(self, table_id: str, updates: Dict) -> bool:
        """Update specific metadata fields"""
        if table_id not in self.metadata_cache:
            logger.warning(f"Table {table_id} not found in metadata store")
            return False

        metadata = self.metadata_cache[table_id]
        for key, value in updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        logger.info(f"Updated metadata for {table_id}")
        return True

    def export_as_yaml(self, output_path: str) -> bool:
        """Export metadata as YAML"""
        try:
            metadata_list = []
            for meta in self.metadata_cache.values():
                metadata_list.append({
                    'table_id': meta.table_id,
                    'table_name': meta.table_name,
                    'schema_name': meta.schema_name,
                    'description': meta.description,
                    'owner': meta.owner,
                    'row_count': meta.row_count,
                    'size_bytes': meta.size_bytes,
                    'columns': [
                        {
                            'name': col.name,
                            'type': col.data_type,
                            'description': col.description,
                            'nullable': col.nullable
                        }
                        for col in meta.columns
                    ]
                })

            with open(output_path, 'w') as f:
                yaml.dump(metadata_list, f, default_flow_style=False)

            logger.info(f"Exported metadata to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export metadata: {e}")
            return False

    def export_as_json(self, output_path: str) -> bool:
        """Export metadata as JSON"""
        try:
            metadata_list = []
            for meta in self.metadata_cache.values():
                metadata_list.append({
                    'table_id': meta.table_id,
                    'table_name': meta.table_name,
                    'schema_name': meta.schema_name,
                    'description': meta.description,
                    'owner': meta.owner,
                    'row_count': meta.row_count,
                    'size_bytes': meta.size_bytes,
                    'columns': [
                        {
                            'name': col.name,
                            'type': col.data_type,
                            'description': col.description,
                            'nullable': col.nullable
                        }
                        for col in meta.columns
                    ]
                })

            with open(output_path, 'w') as f:
                json.dump(metadata_list, f, indent=2)

            logger.info(f"Exported metadata to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export metadata: {e}")
            return False


class DataQualityChecker:
    """Data quality validation for catalog assets"""

    def __init__(self, connector: CatalogConnector):
        self.connector = connector

    def check_completeness(self, metadata: TableMetadata) -> Tuple[bool, Dict]:
        """Check metadata completeness"""
        issues = []

        if not metadata.description or len(metadata.description) < 20:
            issues.append("Description too short or missing")

        if metadata.owner == "unassigned":
            issues.append("Owner not assigned")

        for col in metadata.columns:
            if not col.description:
                issues.append(f"Column '{col.name}' missing description")

        return len(issues) == 0, {'issues': issues, 'score': 100 - (len(issues) * 10)}

    def check_freshness(self, metadata: TableMetadata, max_age_hours: int = 24) -> Tuple[bool, Dict]:
        """Check data freshness"""
        age_hours = (datetime.utcnow() - metadata.last_modified).total_seconds() / 3600
        is_fresh = age_hours <= max_age_hours

        return is_fresh, {
            'age_hours': age_hours,
            'max_age_hours': max_age_hours,
            'is_stale': not is_fresh
        }

    def check_lineage(self, metadata: TableMetadata, lineage_map: Dict) -> Tuple[bool, Dict]:
        """Check if data lineage is documented"""
        table_id = metadata.table_id
        has_lineage = table_id in lineage_map

        return has_lineage, {
            'has_upstream': has_lineage,
            'downstream_count': len(lineage_map.get(table_id, []))
        }


class CatalogAutomationEngine:
    """Main automation orchestrator"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.metadata_store = MetadataStore()
        self.dq_checker = None
        self.connector = None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def run_full_scan(self, source_config: Dict) -> bool:
        """Run complete metadata scan of data sources"""
        try:
            # Initialize connector based on source type
            source_type = DataSourceType(source_config.get('type'))

            if source_type == DataSourceType.SNOWFLAKE:
                self.connector = SnowflakeConnector(**source_config)
            else:
                logger.error(f"Unsupported source type: {source_type}")
                return False

            self.connector.connect()
            self.dq_checker = DataQualityChecker(self.connector)

            # Extract metadata for all tables
            databases = self.connector.list_databases()
            logger.info(f"Found {len(databases)} databases")

            for database in databases:
                logger.info(f"Scanning database: {database}")
                # Add schema iteration logic here

            self.connector.disconnect()
            logger.info("Full scan completed successfully")
            return True

        except Exception as e:
            logger.error(f"Full scan failed: {e}")
            return False

    def validate_metadata(self, table_id: str) -> Dict:
        """Validate metadata completeness and quality"""
        metadata = self.metadata_store.get_table_metadata(table_id)
        if not metadata:
            return {'error': 'Table not found'}

        completeness_ok, completeness_report = self.dq_checker.check_completeness(metadata)
        freshness_ok, freshness_report = self.dq_checker.check_freshness(metadata)

        return {
            'table_id': table_id,
            'completeness': completeness_report,
            'freshness': freshness_report,
            'overall_valid': completeness_ok and freshness_ok
        }

    def generate_report(self, output_path: str) -> bool:
        """Generate catalog report"""
        try:
            all_metadata = self.metadata_store.list_all_metadata()

            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'total_tables': len(all_metadata),
                'tables': []
            }

            for metadata in all_metadata:
                validation = self.validate_metadata(metadata.table_id)
                report['tables'].append({
                    'table_id': metadata.table_id,
                    'row_count': metadata.row_count,
                    'columns': len(metadata.columns),
                    'owner': metadata.owner,
                    'validation': validation
                })

            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Generated report: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    logger.info("Starting Data Catalog Automation")

    # Initialize automation engine
    engine = CatalogAutomationEngine("catalog_config.yaml")

    # Run full scan
    source_config = {
        'type': 'snowflake',
        'account': 'xy12345.us-east-1',
        'user': 'catalog_user',
        'password': 'secure_password',
        'warehouse': 'analytics'
    }

    if engine.run_full_scan(source_config):
        # Export metadata
        engine.metadata_store.export_as_json("metadata_export.json")
        engine.metadata_store.export_as_yaml("metadata_export.yaml")

        # Generate validation report
        engine.generate_report("catalog_validation_report.json")

        logger.info("Automation completed successfully")
    else:
        logger.error("Automation failed")
