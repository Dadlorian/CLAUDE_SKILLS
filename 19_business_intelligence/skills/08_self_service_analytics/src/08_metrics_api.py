"""
Metrics API - Production-Grade Self-Service Metrics Endpoints
============================================================

Provides RESTful API endpoints for querying, validating, and managing
centralized metric definitions. Integrates with dbt, semantic layers,
and data catalogs.

Features:
- Metric versioning and evolution
- Definition validation and linting
- Metric discovery and search
- Usage analytics and lineage
- Audit logging and compliance
- Performance caching and optimization
"""

import logging
import hashlib
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aioredis

from fastapi import FastAPI, HTTPException, Depends, Query, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import structlog

# ============================================================================
# Configuration & Setup
# ============================================================================

logger = structlog.get_logger()
Base = declarative_base()

class MetricStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class CalculationMethod(str, Enum):
    SUM = "sum"
    COUNT = "count"
    COUNT_DISTINCT = "count_distinct"
    AVERAGE = "average"
    RATIO = "ratio"
    DERIVED = "derived"
    CUSTOM = "custom"

# ============================================================================
# Database Models
# ============================================================================

class MetricDefinition(Base):
    """Metric definition with versioning support"""
    __tablename__ = "metric_definitions"

    id = Column(String, primary_key=True)
    metric_name = Column(String, unique=True, index=True)
    version = Column(Integer, default=1)
    status = Column(String, default=MetricStatus.DRAFT)
    definition = Column(JSON)
    owner = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deprecated_at = Column(DateTime, nullable=True)
    content_hash = Column(String, index=True)
    lineage = Column(JSON, default=dict)
    tags = Column(JSON, default=list)

class MetricUsage(Base):
    """Track metric usage for analytics and optimization"""
    __tablename__ = "metric_usage"

    id = Column(String, primary_key=True)
    metric_name = Column(String, index=True)
    user_id = Column(String, index=True)
    query_id = Column(String, index=True)
    execution_time_ms = Column(Integer)
    result_rows = Column(Integer)
    cached = Column(Integer)  # 0 or 1
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    query_parameters = Column(JSON)

class MetricAuditLog(Base):
    """Audit trail for metric changes"""
    __tablename__ = "metric_audit_log"

    id = Column(String, primary_key=True)
    metric_name = Column(String, index=True)
    action = Column(String)  # create, update, deprecate, delete
    actor = Column(String)
    old_value = Column(JSON)
    new_value = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    reason = Column(String)
    approved_by = Column(String, nullable=True)

# ============================================================================
# Pydantic Models
# ============================================================================

@dataclass
class Dimension:
    name: str
    type: str
    values: Optional[List[str]] = None

@dataclass
class Filter:
    field: str
    operator: str
    value: str

class MetricDefinitionRequest(BaseModel):
    metric_name: str = Field(..., min_length=3, max_length=100)
    label: str
    description: str = Field(..., min_length=10)
    model: str
    calculation_method: CalculationMethod
    expression: str
    timestamp: Optional[str] = None
    time_grains: Optional[List[str]] = ["day", "month"]
    dimensions: Optional[List[Dict[str, str]]] = []
    filters: Optional[List[Dict[str, str]]] = []
    depends_on: Optional[List[str]] = []
    owner: str
    tags: Optional[List[str]] = []
    sla: Optional[str] = None

    @validator("metric_name")
    def validate_metric_name(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Metric name must be alphanumeric with underscores/hyphens")
        return v

class MetricDefinitionResponse(BaseModel):
    metric_id: str
    metric_name: str
    version: int
    status: str
    definition: Dict[str, Any]
    owner: str
    created_at: datetime
    updated_at: datetime
    lineage: Dict[str, Any]
    tags: List[str]

class MetricUsageStats(BaseModel):
    metric_name: str
    total_queries: int
    unique_users: int
    avg_execution_time_ms: float
    cached_hit_rate: float
    last_queried: datetime
    trending: str  # "up", "down", "stable"

# ============================================================================
# Validators & Linters
# ============================================================================

class MetricValidator:
    """Validates metric definitions against schema and business rules"""

    RESERVED_KEYWORDS = {"SELECT", "FROM", "WHERE", "JOIN", "GROUP BY", "ORDER BY"}
    MAX_EXPRESSION_LENGTH = 10000

    @staticmethod
    def validate_syntax(definition: MetricDefinitionRequest) -> Tuple[bool, List[str]]:
        """Validate metric definition syntax"""
        errors = []

        # Check expression length
        if len(definition.expression) > MetricValidator.MAX_EXPRESSION_LENGTH:
            errors.append(f"Expression exceeds max length of {MetricValidator.MAX_EXPRESSION_LENGTH}")

        # Check for SQL injection patterns
        if any(keyword in definition.expression.upper() for keyword in ["DROP", "DELETE", "TRUNCATE"]):
            errors.append("Expression contains dangerous SQL keywords")

        # Validate dependent metrics exist
        for dep in definition.depends_on or []:
            if not MetricValidator._metric_exists(dep):
                errors.append(f"Dependent metric '{dep}' does not exist")

        # Check timestamp field if specified
        if definition.timestamp and not definition.timestamp.replace("_", "").isalnum():
            errors.append(f"Invalid timestamp field: {definition.timestamp}")

        # Validate calculation method
        if definition.calculation_method == CalculationMethod.RATIO:
            if not ("numerator" in definition.expression and "denominator" in definition.expression):
                errors.append("Ratio metrics require 'numerator' and 'denominator' expressions")

        return len(errors) == 0, errors

    @staticmethod
    def validate_compatibility(definition: MetricDefinitionRequest) -> Tuple[bool, List[str]]:
        """Check compatibility with existing metrics"""
        errors = []

        # Check for naming conflicts
        if MetricValidator._metric_exists(definition.metric_name):
            errors.append(f"Metric '{definition.metric_name}' already exists")

        # Validate dimensions exist in referenced model
        # This would connect to data catalog

        return len(errors) == 0, errors

    @staticmethod
    def _metric_exists(metric_name: str) -> bool:
        """Check if metric exists in registry (placeholder)"""
        # Would query database
        return False

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Metrics API",
    description="Enterprise metrics management and query service",
    version="1.0.0"
)

# Dependency: Database session
def get_db() -> Session:
    # Placeholder - would create actual session
    pass

# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/api/v1/metrics", response_model=MetricDefinitionResponse, status_code=201)
async def create_metric(
    request: MetricDefinitionRequest,
    db: Session = Depends(get_db),
    authorization: str = Header(...)
):
    """
    Create a new metric definition

    Validates syntax, checks compatibility, logs audit trail
    """
    logger.info(
        "metric_creation_requested",
        metric_name=request.metric_name,
        owner=request.owner
    )

    # Validate syntax
    is_valid, syntax_errors = MetricValidator.validate_syntax(request)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": syntax_errors})

    # Validate compatibility
    is_compatible, compat_errors = MetricValidator.validate_compatibility(request)
    if not is_compatible:
        raise HTTPException(status_code=409, detail={"errors": compat_errors})

    # Create metric ID
    metric_id = hashlib.sha256(
        f"{request.metric_name}{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:12]

    # Calculate content hash for versioning
    content_hash = hashlib.sha256(
        json.dumps(asdict(request), default=str).encode()
    ).hexdigest()

    # Create definition
    definition_dict = asdict(request)

    metric_def = MetricDefinition(
        id=metric_id,
        metric_name=request.metric_name,
        version=1,
        status=MetricStatus.DRAFT,
        definition=definition_dict,
        owner=request.owner,
        content_hash=content_hash,
        lineage={
            "depends_on": request.depends_on or [],
            "used_by": []
        },
        tags=request.tags or []
    )

    # Log audit trail
    audit_log = MetricAuditLog(
        id=f"{metric_id}_create",
        metric_name=request.metric_name,
        action="create",
        actor=authorization,
        new_value=definition_dict,
        reason="Initial metric creation"
    )

    db.add(metric_def)
    db.add(audit_log)
    db.commit()

    logger.info(
        "metric_created",
        metric_id=metric_id,
        metric_name=request.metric_name
    )

    return MetricDefinitionResponse(
        metric_id=metric_id,
        metric_name=metric_def.metric_name,
        version=metric_def.version,
        status=metric_def.status,
        definition=metric_def.definition,
        owner=metric_def.owner,
        created_at=metric_def.created_at,
        updated_at=metric_def.updated_at,
        lineage=metric_def.lineage,
        tags=metric_def.tags
    )

@app.get("/api/v1/metrics", response_model=List[MetricDefinitionResponse])
async def list_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    owner: Optional[str] = None,
    status: Optional[MetricStatus] = None,
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """List all metrics with filtering and pagination"""
    query = db.query(MetricDefinition)

    if owner:
        query = query.filter(MetricDefinition.owner == owner)
    if status:
        query = query.filter(MetricDefinition.status == status)

    metrics = query.offset(skip).limit(limit).all()

    return [
        MetricDefinitionResponse(
            metric_id=m.id,
            metric_name=m.metric_name,
            version=m.version,
            status=m.status,
            definition=m.definition,
            owner=m.owner,
            created_at=m.created_at,
            updated_at=m.updated_at,
            lineage=m.lineage,
            tags=m.tags
        ) for m in metrics
    ]

@app.get("/api/v1/metrics/{metric_name}", response_model=MetricDefinitionResponse)
async def get_metric(
    metric_name: str,
    version: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Retrieve metric definition by name"""
    query = db.query(MetricDefinition).filter(
        MetricDefinition.metric_name == metric_name
    )

    if version:
        query = query.filter(MetricDefinition.version == version)
    else:
        query = query.order_by(MetricDefinition.version.desc())

    metric = query.first()

    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    return MetricDefinitionResponse(
        metric_id=metric.id,
        metric_name=metric.metric_name,
        version=metric.version,
        status=metric.status,
        definition=metric.definition,
        owner=metric.owner,
        created_at=metric.created_at,
        updated_at=metric.updated_at,
        lineage=metric.lineage,
        tags=metric.tags
    )

@app.post("/api/v1/metrics/{metric_name}/validate")
async def validate_metric(
    metric_name: str,
    request: MetricDefinitionRequest,
    db: Session = Depends(get_db)
):
    """Validate metric definition without persisting"""
    is_valid, errors = MetricValidator.validate_syntax(request)
    is_compatible, compat_errors = MetricValidator.validate_compatibility(request)

    all_errors = errors + compat_errors

    return {
        "valid": len(all_errors) == 0,
        "syntax_valid": is_valid,
        "compatible": is_compatible,
        "errors": all_errors
    }

@app.get("/api/v1/metrics/{metric_name}/usage")
async def get_metric_usage(
    metric_name: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get usage statistics for a metric"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    usage_records = db.query(MetricUsage).filter(
        MetricUsage.metric_name == metric_name,
        MetricUsage.timestamp >= cutoff_date
    ).all()

    if not usage_records:
        return {"metric_name": metric_name, "total_queries": 0}

    cached_count = sum(1 for u in usage_records if u.cached)
    total_exec_time = sum(u.execution_time_ms for u in usage_records)
    unique_users = len(set(u.user_id for u in usage_records))

    return MetricUsageStats(
        metric_name=metric_name,
        total_queries=len(usage_records),
        unique_users=unique_users,
        avg_execution_time_ms=total_exec_time / len(usage_records),
        cached_hit_rate=cached_count / len(usage_records),
        last_queried=max(u.timestamp for u in usage_records),
        trending="up"  # Would calculate trend
    )

@app.post("/api/v1/metrics/{metric_name}/deprecate")
async def deprecate_metric(
    metric_name: str,
    replacement_metric: Optional[str] = None,
    reason: str = "",
    db: Session = Depends(get_db),
    authorization: str = Header(...)
):
    """Mark a metric as deprecated"""
    metric = db.query(MetricDefinition).filter(
        MetricDefinition.metric_name == metric_name
    ).order_by(MetricDefinition.version.desc()).first()

    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    metric.status = MetricStatus.DEPRECATED
    metric.deprecated_at = datetime.utcnow()

    audit_log = MetricAuditLog(
        id=f"{metric.id}_deprecate",
        metric_name=metric_name,
        action="deprecate",
        actor=authorization,
        old_value={"status": MetricStatus.VERIFIED},
        new_value={
            "status": MetricStatus.DEPRECATED,
            "replacement": replacement_metric
        },
        reason=reason
    )

    db.add(audit_log)
    db.commit()

    return {"status": "deprecated", "metric_name": metric_name}

@app.get("/api/v1/metrics/search")
async def search_metrics(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Full-text search across metric definitions"""
    # Simplified implementation - would use full-text search index
    query = db.query(MetricDefinition).filter(
        (MetricDefinition.metric_name.ilike(f"%{q}%")) |
        (MetricDefinition.definition["label"].astext.ilike(f"%{q}%"))
    ).limit(limit).all()

    return [
        {
            "metric_name": m.metric_name,
            "label": m.definition.get("label"),
            "owner": m.owner,
            "status": m.status
        } for m in query
    ]

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# ============================================================================
# Caching Decorator
# ============================================================================

def cache_metric(ttl_seconds: int = 300):
    """Decorator for caching metric query results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Placeholder for actual caching logic
            # Would use Redis or similar
            result = await func(*args, **kwargs)
            return result
        return wrapper
    return decorator

# ============================================================================
# Background Tasks
# ============================================================================

async def sync_deprecated_metrics():
    """Periodically sync deprecated metric warnings"""
    pass

async def update_metric_lineage():
    """Recalculate metric dependencies and lineage"""
    pass

async def cleanup_old_audit_logs(retention_days: int = 365):
    """Clean up old audit logs beyond retention period"""
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
