# Property Multi-Tenancy Pattern

**Version:** 2.5
**Last Updated:** 2025-01-15
**Status:** Active Standard
**References:** Salesforce Multi-Tenant Architecture, Yardi Multi-Org, AWS Multi-Tenancy SaaS

## Table of Contents

1. [Overview](#overview)
2. [Data Isolation Strategies](#data-isolation-strategies)
3. [Performance Patterns](#performance-patterns)
4. [Tenant Customization](#tenant-customization)
5. [Billing and Subscription Management](#billing-and-subscription-management)
6. [Cross-Tenant Reporting](#cross-tenant-reporting)

## Overview

Multi-tenancy enables a single PropTech platform to serve multiple property management companies (organizations) while maintaining data isolation, security, and performance.

### Tenancy Models

| Model | Description | Isolation | Cost | Use Case |
|-------|-------------|-----------|------|----------|
| **Shared Database, Shared Schema** | All tenants share tables, filtered by org_id | Row-level | Low | SaaS (Buildium, AppFolio) |
| **Shared Database, Separate Schemas** | Each tenant has own schema in same DB | Schema-level | Medium | Enterprise customers |
| **Separate Databases** | Each tenant has own database | Database-level | High | Regulated industries |

**Recommended:** Shared Database, Shared Schema with row-level security for most PropTech SaaS applications.

## Data Isolation Strategies

### Row-Level Security (PostgreSQL)

**Schema Design:**

```sql
-- All tables include organization_id for tenant isolation
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    property_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_properties_org ON properties(organization_id);

-- Enable row-level security
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see properties in their organization
CREATE POLICY tenant_isolation ON properties
    USING (organization_id = current_setting('app.current_organization_id')::uuid);

-- Grant access
GRANT SELECT, INSERT, UPDATE, DELETE ON properties TO app_user;
```

**Application-Level Enforcement:**

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

app = FastAPI()

def get_current_organization(token: str) -> uuid.UUID:
    """
    Extract organization_id from JWT token
    """
    payload = decode_jwt(token)
    return uuid.UUID(payload["organization_id"])

def get_db_session(organization_id: uuid.UUID = Depends(get_current_organization)):
    """
    Create database session with organization context
    """
    db = SessionLocal()
    try:
        # Set organization context for RLS
        db.execute(f"SET app.current_organization_id = '{organization_id}'")
        yield db
    finally:
        db.close()

@app.get("/properties")
async def list_properties(db: Session = Depends(get_db_session)):
    """
    List properties (automatically filtered by RLS)
    """
    properties = db.query(Property).all()  # RLS enforces organization_id filter
    return properties
```

### Multi-Database Pattern (Enterprise)

**Database Routing:**

```python
class TenantDatabaseRouter:
    """
    Route database connections based on tenant
    """

    def __init__(self):
        self.tenant_databases = {
            "org_greystar": "postgresql://host1/greystar_db",
            "org_equity": "postgresql://host2/equity_db",
            "org_invesco": "postgresql://host3/invesco_db"
        }

    def get_database_for_tenant(self, organization_id: str) -> str:
        """
        Return database connection string for tenant
        """
        return self.tenant_databases.get(
            organization_id,
            "postgresql://default/shared_db"  # Fallback for small tenants
        )

    def get_session(self, organization_id: str):
        """
        Create database session for specific tenant
        """
        db_url = self.get_database_for_tenant(organization_id)
        engine = create_engine(db_url)
        SessionClass = sessionmaker(bind=engine)
        return SessionClass()

# Usage
router = TenantDatabaseRouter()

@app.get("/properties")
async def list_properties(org_id: str = Depends(get_current_organization)):
    db = router.get_session(org_id)
    properties = db.query(Property).all()
    return properties
```

## Performance Patterns

### Tenant-Level Caching

```python
from redis import Redis
import json

class TenantAwareCache:
    """
    Cache with tenant isolation
    """

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def get_cache_key(self, organization_id: str, key: str) -> str:
        """
        Generate tenant-scoped cache key
        """
        return f"org:{organization_id}:{key}"

    def get(self, organization_id: str, key: str):
        """
        Get cached value for tenant
        """
        cache_key = self.get_cache_key(organization_id, key)
        value = self.redis.get(cache_key)
        return json.loads(value) if value else None

    def set(self, organization_id: str, key: str, value, ttl: int = 3600):
        """
        Set cached value for tenant
        """
        cache_key = self.get_cache_key(organization_id, key)
        self.redis.setex(cache_key, ttl, json.dumps(value))

    def invalidate(self, organization_id: str, pattern: str = "*"):
        """
        Invalidate cache for tenant
        """
        cache_pattern = self.get_cache_key(organization_id, pattern)
        keys = self.redis.keys(cache_pattern)
        if keys:
            self.redis.delete(*keys)

# Usage
cache = TenantAwareCache(redis_client)

@app.get("/properties")
async def list_properties(org_id: str = Depends(get_current_organization)):
    # Check cache first
    cached = cache.get(org_id, "properties:list")
    if cached:
        return cached

    # Query database
    properties = db.query(Property).filter_by(organization_id=org_id).all()

    # Cache results
    cache.set(org_id, "properties:list", properties, ttl=300)

    return properties
```

### Database Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class TenantConnectionPool:
    """
    Manage connection pools per tenant
    """

    def __init__(self, max_connections_per_tenant: int = 20):
        self.max_connections = max_connections_per_tenant
        self.pools = {}

    def get_engine(self, organization_id: str, db_url: str):
        """
        Get or create connection pool for tenant
        """
        if organization_id not in self.pools:
            self.pools[organization_id] = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=self.max_connections,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600  # Recycle connections every hour
            )

        return self.pools[organization_id]

# Large tenant gets dedicated pool, small tenants share
def get_database_engine(org_id: str):
    if is_large_tenant(org_id):
        return tenant_pool.get_engine(org_id, get_dedicated_db_url(org_id))
    else:
        return shared_pool
```

### Query Performance Optimization

```sql
-- Composite indexes for multi-tenant queries
CREATE INDEX idx_properties_org_created ON properties(organization_id, created_at DESC);
CREATE INDEX idx_leases_org_status ON leases(organization_id, lease_status);
CREATE INDEX idx_payments_org_date ON payments(organization_id, payment_date DESC);

-- Analyze query plan
EXPLAIN ANALYZE
SELECT * FROM properties
WHERE organization_id = 'org_greystar'
  AND property_type = 'multifamily'
ORDER BY created_at DESC
LIMIT 20;

-- Result should use index scan, not sequential scan
```

## Tenant Customization

### Custom Fields Pattern

```python
from sqlalchemy.dialects.postgresql import JSONB

class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID, primary_key=True)
    organization_id = Column(UUID, ForeignKey("organizations.id"))
    property_name = Column(String(255))
    # ... standard fields ...

    # Custom fields (tenant-specific)
    custom_fields = Column(JSONB, default={})

    def set_custom_field(self, field_name: str, value):
        """
        Set custom field value
        """
        if self.custom_fields is None:
            self.custom_fields = {}
        self.custom_fields[field_name] = value

    def get_custom_field(self, field_name: str, default=None):
        """
        Get custom field value
        """
        return self.custom_fields.get(field_name, default) if self.custom_fields else default

# Usage - Tenant A stores "portfolio_segment"
property.set_custom_field("portfolio_segment", "luxury")

# Usage - Tenant B stores "acquisition_date"
property.set_custom_field("acquisition_date", "2020-01-15")

# Query custom fields
properties_luxury = db.query(Property).filter(
    Property.organization_id == org_id,
    Property.custom_fields["portfolio_segment"].astext == "luxury"
).all()
```

### White-Label Configuration

```python
class OrganizationBranding(Base):
    """
    Tenant-specific branding and configuration
    """
    __tablename__ = "organization_branding"

    organization_id = Column(UUID, ForeignKey("organizations.id"), primary_key=True)

    # Branding
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color
    secondary_color = Column(String(7))
    company_name = Column(String(255))

    # Configuration
    custom_domain = Column(String(255))  # e.g., "greystar.proptech.com"
    tenant_portal_url = Column(String(500))
    support_email = Column(String(255))
    support_phone = Column(String(20))

    # Feature flags
    features_enabled = Column(JSONB, default={})

def get_branding_for_request(request):
    """
    Determine branding based on domain or subdomain
    """
    host = request.headers.get("host")

    # Check for custom domain
    branding = db.query(OrganizationBranding).filter_by(custom_domain=host).first()

    if not branding:
        # Extract subdomain (e.g., "greystar" from "greystar.proptech.com")
        subdomain = host.split(".")[0]
        org = db.query(Organization).filter_by(subdomain=subdomain).first()
        if org:
            branding = org.branding

    return branding or get_default_branding()
```

## Billing and Subscription Management

### Usage-Based Pricing

```python
class UsageTracking:
    """
    Track tenant usage for billing
    """

    def __init__(self, db: Session):
        self.db = db

    def track_event(self, organization_id: str, event_type: str, quantity: int = 1):
        """
        Track billable event
        """
        usage = UsageEvent(
            organization_id=organization_id,
            event_type=event_type,
            quantity=quantity,
            timestamp=datetime.utcnow()
        )
        self.db.add(usage)
        self.db.commit()

    def get_monthly_usage(self, organization_id: str, year: int, month: int):
        """
        Get usage for billing period
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        usage = self.db.query(
            UsageEvent.event_type,
            func.sum(UsageEvent.quantity).label("total")
        ).filter(
            UsageEvent.organization_id == organization_id,
            UsageEvent.timestamp >= start_date,
            UsageEvent.timestamp < end_date
        ).group_by(UsageEvent.event_type).all()

        return {event_type: total for event_type, total in usage}

# Track usage
tracker = UsageTracking(db)

@app.post("/leases")
async def create_lease(org_id: str = Depends(get_current_organization)):
    # Create lease
    lease = create_lease_in_database(...)

    # Track billable event
    tracker.track_event(org_id, "lease_created", quantity=1)

    return lease
```

### Pricing Tiers

```python
class PricingTier:
    """
    Tiered pricing model
    """

    TIERS = {
        "starter": {
            "max_units": 100,
            "monthly_fee": 99,
            "per_unit_fee": 1.50,
            "features": ["basic_pms", "rent_collection", "maintenance"]
        },
        "professional": {
            "max_units": 1000,
            "monthly_fee": 299,
            "per_unit_fee": 1.00,
            "features": ["basic_pms", "rent_collection", "maintenance", "accounting", "reporting"]
        },
        "enterprise": {
            "max_units": None,  # Unlimited
            "monthly_fee": 999,
            "per_unit_fee": 0.50,
            "features": ["all_features", "api_access", "custom_integrations", "dedicated_support"]
        }
    }

    def calculate_monthly_bill(self, organization):
        """
        Calculate monthly bill based on tier and usage
        """
        tier = self.TIERS[organization.pricing_tier]

        # Base fee
        monthly_fee = tier["monthly_fee"]

        # Per-unit fee
        unit_count = self.get_unit_count(organization.id)
        per_unit_fee = unit_count * tier["per_unit_fee"]

        # Usage overage (if applicable)
        overage_fee = 0
        if tier["max_units"] and unit_count > tier["max_units"]:
            overage = unit_count - tier["max_units"]
            overage_fee = overage * 2.00  # Overage rate

        total = monthly_fee + per_unit_fee + overage_fee

        return {
            "monthly_fee": monthly_fee,
            "per_unit_fee": per_unit_fee,
            "overage_fee": overage_fee,
            "total": total,
            "unit_count": unit_count
        }
```

## Cross-Tenant Reporting

### Aggregated Analytics for Platform Operator

```python
class PlatformAnalytics:
    """
    Cross-tenant analytics for platform operator
    """

    def get_platform_metrics(self, start_date, end_date):
        """
        Aggregated metrics across all tenants
        """
        return {
            "total_tenants": self.count_active_tenants(),
            "total_properties": self.count_total_properties(),
            "total_units": self.count_total_units(),
            "total_leases": self.count_total_leases(start_date, end_date),
            "total_revenue": self.calculate_total_revenue(start_date, end_date),
            "avg_occupancy_rate": self.calculate_avg_occupancy(),
            "tenant_growth_rate": self.calculate_tenant_growth_rate()
        }

    def get_tenant_segmentation(self):
        """
        Segment tenants by size, usage, revenue
        """
        tenants = db.query(Organization).all()

        segments = {
            "small": [],  # < 100 units
            "medium": [],  # 100-1000 units
            "large": [],  # 1000+ units
        }

        for tenant in tenants:
            unit_count = self.get_unit_count(tenant.id)
            if unit_count < 100:
                segments["small"].append(tenant)
            elif unit_count < 1000:
                segments["medium"].append(tenant)
            else:
                segments["large"].append(tenant)

        return segments

    def get_feature_adoption_rates(self):
        """
        Feature usage across platform
        """
        return {
            "mobile_app": self.count_tenants_using_feature("mobile_app") / self.count_active_tenants(),
            "online_payments": self.count_tenants_using_feature("online_payments") / self.count_active_tenants(),
            "maintenance_portal": self.count_tenants_using_feature("maintenance") / self.count_active_tenants()
        }
```

---

## References

1. **Salesforce Multi-Tenant Architecture**: https://developer.salesforce.com/docs/atlas.en-us.fundamentals.meta/fundamentals/
2. **AWS SaaS Factory**: https://aws.amazon.com/partners/saas-factory/
3. **Yardi Multi-Organization Setup**: https://www.yardi.com/

---

*This document is maintained by the PropTech Architecture Committee. For questions or updates, contact architecture@proptech.com.*
