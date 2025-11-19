"""
Data Lineage Tracking and Visualization System
Production-ready lineage tracking for analytics platform.

This module provides:
- Data source to output lineage mapping
- Query-to-table relationship tracking
- Impact analysis for schema changes
- Lineage visualization data generation
"""

import json
import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LineageType(Enum):
    """Types of data lineage relationships."""
    DIRECT_DEPENDENCY = "direct"
    CALCULATED_FIELD = "calculated"
    FILTERED_VIEW = "filtered"
    AGGREGATED = "aggregated"
    JOINED = "joined"
    TRANSFORMED = "transformed"
    EXTERNAL_SOURCE = "external"


@dataclass
class DataAsset:
    """Represents a data asset (table, view, query, metric)."""
    asset_id: str
    asset_type: str  # table, view, query, metric, dashboard
    name: str
    owner: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class LineageEdge:
    """Represents a relationship between two data assets."""
    source_asset_id: str
    target_asset_id: str
    lineage_type: LineageType
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    description: Optional[str] = None
    columns_affected: List[str] = field(default_factory=list)
    transformation_logic: Optional[str] = None


class LineageTracker:
    """
    Production lineage tracking system.
    Maintains complete data flow graphs and impact analysis.
    """

    def __init__(self, metadata_db_connection):
        """
        Initialize lineage tracker.

        Args:
            metadata_db_connection: Connection to metadata database
        """
        self.metadata_conn = metadata_db_connection
        self.assets: Dict[str, DataAsset] = {}
        self.edges: List[LineageEdge] = []
        logger.info("LineageTracker initialized")

    def initialize_schema(self) -> bool:
        """Create required schema for lineage tracking."""
        try:
            cursor = self.metadata_conn.cursor()

            # Data assets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_assets (
                    asset_id VARCHAR(255) PRIMARY KEY,
                    asset_type VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    owner VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags JSONB,
                    metadata JSONB
                )
            """)

            # Lineage edges table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lineage_edges (
                    edge_id SERIAL PRIMARY KEY,
                    source_asset_id VARCHAR(255) NOT NULL REFERENCES data_assets(asset_id),
                    target_asset_id VARCHAR(255) NOT NULL REFERENCES data_assets(asset_id),
                    lineage_type VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(255),
                    description TEXT,
                    columns_affected JSONB,
                    transformation_logic TEXT,
                    UNIQUE(source_asset_id, target_asset_id, lineage_type)
                )
            """)

            # Query lineage tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_lineage (
                    query_id VARCHAR(255) PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    source_tables JSONB,
                    target_tables JSONB,
                    intermediate_tables JSONB,
                    execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed_by VARCHAR(255),
                    query_hash VARCHAR(64)
                )
            """)

            # Impact analysis cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lineage_impact_analysis (
                    analysis_id SERIAL PRIMARY KEY,
                    asset_id VARCHAR(255) NOT NULL REFERENCES data_assets(asset_id),
                    change_type VARCHAR(50),
                    affected_downstream JSONB,
                    affected_count INT,
                    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analyzed_by VARCHAR(255)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX idx_assets_type ON data_assets(asset_type)")
            cursor.execute("CREATE INDEX idx_assets_owner ON data_assets(owner)")
            cursor.execute("CREATE INDEX idx_edges_source ON lineage_edges(source_asset_id)")
            cursor.execute("CREATE INDEX idx_edges_target ON lineage_edges(target_asset_id)")
            cursor.execute("CREATE INDEX idx_query_hash ON query_lineage(query_hash)")

            self.metadata_conn.commit()
            logger.info("Lineage tracking schema initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize schema: {str(e)}")
            self.metadata_conn.rollback()
            return False

    def register_asset(self, asset: DataAsset) -> bool:
        """Register a data asset in the lineage system."""
        try:
            cursor = self.metadata_conn.cursor()

            cursor.execute("""
                INSERT INTO data_assets (
                    asset_id, asset_type, name, owner, description, tags, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (asset_id) DO UPDATE SET
                    updated_at = CURRENT_TIMESTAMP,
                    metadata = EXCLUDED.metadata
            """, (
                asset.asset_id, asset.asset_type, asset.name, asset.owner,
                asset.description, json.dumps(asset.tags), json.dumps(asset.metadata)
            ))

            self.metadata_conn.commit()
            self.assets[asset.asset_id] = asset
            logger.info(f"Asset registered: {asset.asset_id} ({asset.asset_type})")
            return True

        except Exception as e:
            logger.error(f"Failed to register asset: {str(e)}")
            self.metadata_conn.rollback()
            return False

    def add_lineage_edge(self, edge: LineageEdge, force: bool = False) -> bool:
        """Add a lineage relationship between assets."""
        try:
            cursor = self.metadata_conn.cursor()

            cursor.execute("""
                INSERT INTO lineage_edges (
                    source_asset_id, target_asset_id, lineage_type,
                    created_by, description, columns_affected, transformation_logic
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_asset_id, target_asset_id, lineage_type)
                DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            """, (
                edge.source_asset_id, edge.target_asset_id, edge.lineage_type.value,
                edge.created_by, edge.description,
                json.dumps(edge.columns_affected), edge.transformation_logic
            ))

            self.metadata_conn.commit()
            self.edges.append(edge)
            logger.info(
                f"Lineage edge added: {edge.source_asset_id} -> "
                f"{edge.target_asset_id} ({edge.lineage_type.value})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add lineage edge: {str(e)}")
            self.metadata_conn.rollback()
            return False

    def extract_lineage_from_query(self, query_id: str, query_text: str, executed_by: str) -> bool:
        """Extract and track lineage from a SQL query."""
        try:
            source_tables = self._extract_tables_from_sql(query_text, "FROM|JOIN")
            target_tables = self._extract_tables_from_sql(query_text, "INTO|TABLE")

            query_hash = self._hash_query(query_text)

            cursor = self.metadata_conn.cursor()
            cursor.execute("""
                INSERT INTO query_lineage (
                    query_id, query_text, source_tables, target_tables,
                    executed_by, query_hash
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                query_id, query_text,
                json.dumps(source_tables),
                json.dumps(target_tables),
                executed_by,
                query_hash
            ))

            self.metadata_conn.commit()
            logger.info(f"Query lineage extracted: {query_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to extract query lineage: {str(e)}")
            self.metadata_conn.rollback()
            return False

    def get_upstream_lineage(self, asset_id: str, depth: int = 5) -> Dict:
        """Get all upstream data sources for an asset."""
        try:
            cursor = self.metadata_conn.cursor()

            # Use recursive CTE to find upstream assets
            cursor.execute("""
                WITH RECURSIVE upstream AS (
                    SELECT source_asset_id, target_asset_id, lineage_type, 1 as depth
                    FROM lineage_edges
                    WHERE target_asset_id = %s AND depth <= %s

                    UNION ALL

                    SELECT le.source_asset_id, le.target_asset_id, le.lineage_type, up.depth + 1
                    FROM lineage_edges le
                    INNER JOIN upstream up ON le.target_asset_id = up.source_asset_id
                    WHERE up.depth < %s
                )
                SELECT DISTINCT source_asset_id, lineage_type, depth
                FROM upstream
                ORDER BY depth
            """, (asset_id, depth, depth))

            upstream_assets = []
            for source_id, lineage_type, dep in cursor.fetchall():
                upstream_assets.append({
                    'asset_id': source_id,
                    'lineage_type': lineage_type,
                    'depth': dep
                })

            logger.info(f"Retrieved {len(upstream_assets)} upstream assets for {asset_id}")
            return {
                'asset_id': asset_id,
                'upstream_sources': upstream_assets,
                'depth': depth
            }

        except Exception as e:
            logger.error(f"Failed to get upstream lineage: {str(e)}")
            return {}

    def get_downstream_lineage(self, asset_id: str, depth: int = 5) -> Dict:
        """Get all downstream dependent assets."""
        try:
            cursor = self.metadata_conn.cursor()

            cursor.execute("""
                WITH RECURSIVE downstream AS (
                    SELECT source_asset_id, target_asset_id, lineage_type, 1 as depth
                    FROM lineage_edges
                    WHERE source_asset_id = %s AND depth <= %s

                    UNION ALL

                    SELECT le.source_asset_id, le.target_asset_id, le.lineage_type, down.depth + 1
                    FROM lineage_edges le
                    INNER JOIN downstream down ON le.source_asset_id = down.target_asset_id
                    WHERE down.depth < %s
                )
                SELECT DISTINCT target_asset_id, lineage_type, depth
                FROM downstream
                ORDER BY depth
            """, (asset_id, depth, depth))

            downstream_assets = []
            for target_id, lineage_type, dep in cursor.fetchall():
                downstream_assets.append({
                    'asset_id': target_id,
                    'lineage_type': lineage_type,
                    'depth': dep
                })

            logger.info(f"Retrieved {len(downstream_assets)} downstream assets for {asset_id}")
            return {
                'asset_id': asset_id,
                'downstream_dependents': downstream_assets,
                'depth': depth
            }

        except Exception as e:
            logger.error(f"Failed to get downstream lineage: {str(e)}")
            return {}

    def analyze_impact(self, asset_id: str, change_type: str = "schema_change") -> Dict:
        """Analyze impact of changes to an asset on downstream consumers."""
        try:
            downstream = self.get_downstream_lineage(asset_id, depth=10)
            affected_assets = downstream.get('downstream_dependents', [])

            cursor = self.metadata_conn.cursor()

            # Cache analysis results
            cursor.execute("""
                INSERT INTO lineage_impact_analysis (
                    asset_id, change_type, affected_downstream, affected_count
                ) VALUES (%s, %s, %s, %s)
            """, (
                asset_id, change_type,
                json.dumps(affected_assets),
                len(affected_assets)
            ))

            self.metadata_conn.commit()

            logger.info(
                f"Impact analysis: {asset_id} affects "
                f"{len(affected_assets)} downstream assets"
            )

            return {
                'asset_id': asset_id,
                'change_type': change_type,
                'affected_count': len(affected_assets),
                'affected_assets': affected_assets,
                'risk_level': self._calculate_risk_level(len(affected_assets))
            }

        except Exception as e:
            logger.error(f"Failed to analyze impact: {str(e)}")
            return {}

    def generate_lineage_graph(self, root_asset_id: str, direction: str = "both") -> Dict:
        """Generate graph data for visualization."""
        try:
            nodes = set()
            edges_list = []

            if direction in ["upstream", "both"]:
                upstream = self.get_upstream_lineage(root_asset_id, depth=5)
                for asset in upstream.get('upstream_sources', []):
                    nodes.add(asset['asset_id'])

            if direction in ["downstream", "both"]:
                downstream = self.get_downstream_lineage(root_asset_id, depth=5)
                for asset in downstream.get('downstream_dependents', []):
                    nodes.add(asset['asset_id'])

            nodes.add(root_asset_id)

            # Fetch edge details
            cursor = self.metadata_conn.cursor()
            for node_id in nodes:
                cursor.execute("""
                    SELECT source_asset_id, target_asset_id, lineage_type
                    FROM lineage_edges
                    WHERE (source_asset_id IN ({nodes}) AND target_asset_id IN ({nodes}))
                """.format(nodes=','.join(['%s'] * len(nodes))), tuple(nodes))

                for source, target, ltype in cursor.fetchall():
                    edges_list.append({
                        'source': source,
                        'target': target,
                        'type': ltype
                    })

            return {
                'root_asset': root_asset_id,
                'nodes': list(nodes),
                'edges': edges_list,
                'node_count': len(nodes),
                'edge_count': len(edges_list)
            }

        except Exception as e:
            logger.error(f"Failed to generate lineage graph: {str(e)}")
            return {}

    # Helper methods
    def _extract_tables_from_sql(self, query_text: str, keyword_pattern: str) -> List[str]:
        """Extract table names from SQL query."""
        try:
            # Simple regex-based extraction (production would use SQL parser)
            pattern = rf'{keyword_pattern}\s+(?:FROM\s+)?([a-zA-Z0-9_\.]+)'
            matches = re.findall(pattern, query_text, re.IGNORECASE)
            return list(set(matches))
        except Exception as e:
            logger.warning(f"Failed to extract tables: {str(e)}")
            return []

    def _hash_query(self, query_text: str) -> str:
        """Generate hash of query for deduplication."""
        import hashlib
        normalized = ' '.join(query_text.split()).upper()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def _calculate_risk_level(self, affected_count: int) -> str:
        """Calculate risk level based on number of affected assets."""
        if affected_count > 20:
            return "critical"
        elif affected_count > 10:
            return "high"
        elif affected_count > 3:
            return "medium"
        else:
            return "low"


if __name__ == "__main__":
    # Example usage
    asset1 = DataAsset(
        asset_id="source_raw_events",
        asset_type="table",
        name="raw_events",
        owner="data_eng_team",
        description="Raw event data from production"
    )

    asset2 = DataAsset(
        asset_id="transformed_events",
        asset_type="table",
        name="fct_events",
        owner="analytics_team",
        description="Cleaned and transformed events"
    )

    edge = LineageEdge(
        source_asset_id="source_raw_events",
        target_asset_id="transformed_events",
        lineage_type=LineageType.TRANSFORMED,
        created_by="data_engineer@company.com",
        description="Events transformation pipeline"
    )

    print("Lineage tracking module loaded successfully")
