"""
Platform API Implementation Example
FastAPI implementation of the internal developer platform API
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Query, Path
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import uuid


# FastAPI app
app = FastAPI(
    title="Internal Developer Platform API",
    description="Self-service platform for developers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Enums
class Runtime(str, Enum):
    NODE18 = "node18"
    NODE20 = "node20"
    PYTHON311 = "python311"
    PYTHON312 = "python312"
    GO121 = "go121"
    JAVA17 = "java17"


class ServiceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROVISIONING = "provisioning"
    FAILED = "failed"
    UPDATING = "updating"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseType(str, Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    MONGODB = "mongodb"


class InstanceSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


# Pydantic Models
class Resources(BaseModel):
    cpu: str = Field(default="500m", pattern=r"^\d+m?$")
    memory: str = Field(default="512Mi", pattern=r"^\d+(Mi|Gi)$")


class Autoscaling(BaseModel):
    enabled: bool = True
    minReplicas: int = Field(default=2, ge=1)
    maxReplicas: int = Field(default=10, ge=1)
    targetCPU: int = Field(default=70, ge=1, le=100)


class DatabaseConfig(BaseModel):
    type: DatabaseType
    size: InstanceSize = InstanceSize.SMALL


class ServiceCreate(BaseModel):
    name: str = Field(..., pattern=r"^[a-z0-9-]+$", min_length=3, max_length=63)
    runtime: Runtime
    team: str
    replicas: int = Field(default=3, ge=1, le=100)
    resources: Optional[Resources] = None
    autoscaling: Optional[Autoscaling] = None
    database: Optional[DatabaseConfig] = None
    cache: bool = False

    @validator('name')
    def validate_name(cls, v):
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Name cannot start or end with hyphen')
        return v


class ServiceUpdate(BaseModel):
    replicas: Optional[int] = Field(None, ge=1, le=100)
    resources: Optional[Resources] = None
    autoscaling: Optional[Autoscaling] = None


class Service(BaseModel):
    id: str
    name: str
    runtime: Runtime
    team: str
    replicas: int
    resources: Resources
    autoscaling: Optional[Autoscaling] = None
    status: ServiceStatus
    createdAt: datetime
    updatedAt: datetime
    url: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DatabaseCreate(BaseModel):
    name: str
    type: DatabaseType
    version: Optional[str] = None
    size: InstanceSize = InstanceSize.SMALL


class Database(BaseModel):
    id: str
    name: str
    type: DatabaseType
    version: str
    size: InstanceSize
    status: str
    endpoint: str
    port: int
    createdAt: datetime


class SecretCreate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SecretMetadata(BaseModel):
    id: str
    key: str
    createdAt: datetime
    updatedAt: datetime


class DeploymentCreate(BaseModel):
    serviceId: str
    environment: Environment
    version: str
    strategy: Literal["rolling", "blue_green", "canary"] = "rolling"


class Deployment(BaseModel):
    id: str
    serviceId: str
    environment: Environment
    version: str
    status: str
    strategy: str
    createdAt: datetime
    completedAt: Optional[datetime] = None


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[List[dict]] = None
    requestId: str


class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verify API token and return user"""
    # In production, verify token against OAuth2 provider
    # For demo purposes, we'll return a mock user
    return {"username": "demo-user", "team": "platform-team"}


async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from header"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    # Verify API key against database
    return True


# Mock data store (replace with real database)
services_db = {}
databases_db = {}
secrets_db = {}
deployments_db = {}


# API Endpoints

# Services
@app.get("/v1/services", response_model=dict, tags=["Services"])
async def list_services(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    team: Optional[str] = None,
    environment: Optional[str] = None,
    status: Optional[ServiceStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all services with filtering and pagination"""

    services = list(services_db.values())

    # Apply filters
    if team:
        services = [s for s in services if s["team"] == team]
    if status:
        services = [s for s in services if s["status"] == status]

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_services = services[start:end]

    return {
        "data": paginated_services,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(services),
            "pages": (len(services) + limit - 1) // limit
        }
    }


@app.post("/v1/services", response_model=Service, status_code=201, tags=["Services"])
async def create_service(
    service: ServiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new service"""

    # Check if service already exists
    if service.name in [s["name"] for s in services_db.values()]:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "RESOURCE_CONFLICT",
                "message": f"Service '{service.name}' already exists"
            }
        )

    # Validate team ownership
    if service.team != current_user["team"]:
        # In production, verify user has access to the team
        pass

    # Create service
    service_id = str(uuid.uuid4())
    now = datetime.utcnow()

    new_service = {
        "id": service_id,
        "name": service.name,
        "runtime": service.runtime,
        "team": service.team,
        "replicas": service.replicas,
        "resources": service.resources or Resources(),
        "autoscaling": service.autoscaling,
        "status": ServiceStatus.PROVISIONING,
        "createdAt": now,
        "updatedAt": now,
        "url": f"https://{service.name}.company.com"
    }

    services_db[service_id] = new_service

    # Trigger infrastructure provisioning (async task)
    # await provision_infrastructure(service_id, service)

    # If database requested, create it
    if service.database:
        # await create_database_for_service(service_id, service.database)
        pass

    return Service(**new_service)


@app.get("/v1/services/{service_id}", response_model=Service, tags=["Services"])
async def get_service(
    service_id: str = Path(..., description="Service identifier"),
    current_user: dict = Depends(get_current_user)
):
    """Get service details"""

    if service_id not in services_db:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": f"Service '{service_id}' not found"
            }
        )

    service = services_db[service_id]
    return Service(**service)


@app.put("/v1/services/{service_id}", response_model=Service, tags=["Services"])
async def update_service(
    service_id: str,
    update: ServiceUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update service configuration"""

    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")

    service = services_db[service_id]

    # Update fields
    if update.replicas is not None:
        service["replicas"] = update.replicas
    if update.resources is not None:
        service["resources"] = update.resources
    if update.autoscaling is not None:
        service["autoscaling"] = update.autoscaling

    service["updatedAt"] = datetime.utcnow()
    service["status"] = ServiceStatus.UPDATING

    # Trigger infrastructure update (async)
    # await update_infrastructure(service_id, update)

    return Service(**service)


@app.delete("/v1/services/{service_id}", status_code=204, tags=["Services"])
async def delete_service(
    service_id: str,
    force: bool = Query(False),
    current_user: dict = Depends(get_current_user)
):
    """Delete service"""

    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")

    # Check for dependencies
    if not force:
        # Check if service has active deployments, databases, etc.
        pass

    # Delete service and associated resources
    del services_db[service_id]

    # Trigger infrastructure cleanup (async)
    # await cleanup_infrastructure(service_id)

    return None


@app.post("/v1/services/{service_id}/scale", tags=["Services"])
async def scale_service(
    service_id: str,
    replicas: int = Field(..., ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Scale service replicas"""

    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")

    service = services_db[service_id]
    service["replicas"] = replicas
    service["updatedAt"] = datetime.utcnow()

    operation_id = str(uuid.uuid4())

    # Trigger scaling operation (async)
    # await scale_infrastructure(service_id, replicas)

    return {
        "operationId": operation_id,
        "status": "in_progress",
        "message": f"Scaling service to {replicas} replicas"
    }


@app.get("/v1/services/{service_id}/logs", tags=["Services"])
async def get_service_logs(
    service_id: str,
    follow: bool = Query(False),
    tail: int = Query(100, ge=1, le=10000),
    since: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get service logs"""

    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")

    # In production, fetch logs from logging system (e.g., Loki, CloudWatch)
    logs = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "info",
            "message": f"Sample log message {i}",
            "pod": f"service-pod-{i}"
        }
        for i in range(tail)
    ]

    return {"logs": logs}


# Databases
@app.get("/v1/databases", response_model=List[Database], tags=["Databases"])
async def list_databases(
    type: Optional[DatabaseType] = None,
    current_user: dict = Depends(get_current_user)
):
    """List databases"""
    databases = list(databases_db.values())

    if type:
        databases = [d for d in databases if d["type"] == type]

    return databases


@app.post("/v1/databases", response_model=Database, status_code=201, tags=["Databases"])
async def create_database(
    database: DatabaseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new database"""

    db_id = str(uuid.uuid4())

    new_database = {
        "id": db_id,
        "name": database.name,
        "type": database.type,
        "version": database.version or "latest",
        "size": database.size,
        "status": "provisioning",
        "endpoint": f"{database.name}.db.company.com",
        "port": 5432 if database.type == DatabaseType.POSTGRES else 3306,
        "createdAt": datetime.utcnow()
    }

    databases_db[db_id] = new_database

    return Database(**new_database)


# Secrets
@app.get("/v1/secrets", response_model=List[SecretMetadata], tags=["Secrets"])
async def list_secrets(
    current_user: dict = Depends(get_current_user)
):
    """List secrets (metadata only, no values)"""
    secrets = [
        {
            "id": s["id"],
            "key": s["key"],
            "createdAt": s["createdAt"],
            "updatedAt": s["updatedAt"]
        }
        for s in secrets_db.values()
    ]
    return secrets


@app.post("/v1/secrets", status_code=201, tags=["Secrets"])
async def create_secret(
    secret: SecretCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new secret"""

    secret_id = str(uuid.uuid4())
    now = datetime.utcnow()

    new_secret = {
        "id": secret_id,
        "key": secret.key,
        "value": secret.value,  # In production, encrypt this
        "description": secret.description,
        "createdAt": now,
        "updatedAt": now,
        "createdBy": current_user["username"]
    }

    secrets_db[secret_id] = new_secret

    return SecretMetadata(
        id=secret_id,
        key=secret.key,
        createdAt=now,
        updatedAt=now
    )


# Deployments
@app.get("/v1/deployments", response_model=List[Deployment], tags=["Deployments"])
async def list_deployments(
    serviceId: Optional[str] = None,
    environment: Optional[Environment] = None,
    current_user: dict = Depends(get_current_user)
):
    """List deployments"""
    deployments = list(deployments_db.values())

    if serviceId:
        deployments = [d for d in deployments if d["serviceId"] == serviceId]
    if environment:
        deployments = [d for d in deployments if d["environment"] == environment]

    return deployments


@app.post("/v1/deployments", response_model=Deployment, status_code=201, tags=["Deployments"])
async def create_deployment(
    deployment: DeploymentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new deployment"""

    if deployment.serviceId not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")

    deployment_id = str(uuid.uuid4())

    new_deployment = {
        "id": deployment_id,
        "serviceId": deployment.serviceId,
        "environment": deployment.environment,
        "version": deployment.version,
        "status": "pending",
        "strategy": deployment.strategy,
        "createdAt": datetime.utcnow(),
        "completedAt": None
    }

    deployments_db[deployment_id] = new_deployment

    # Trigger deployment pipeline (async)
    # await trigger_deployment(deployment_id)

    return Deployment(**new_deployment)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# Metrics endpoint (for Prometheus)
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # In production, use prometheus_client library
    return """
# HELP platform_api_requests_total Total API requests
# TYPE platform_api_requests_total counter
platform_api_requests_total{method="GET",endpoint="/v1/services"} 1234
platform_api_requests_total{method="POST",endpoint="/v1/services"} 456
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
