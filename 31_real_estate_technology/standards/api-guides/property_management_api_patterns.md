# Property Management API Patterns

**Version:** 3.0
**Last Updated:** 2025-01-15
**Status:** Active Standard
**Authority:** PropTech API Standards Committee
**References:** REST API Design Guidelines (Microsoft), Stripe API, Yardi WebServices, Buildium API, AppFolio API

## Table of Contents

1. [Overview](#overview)
2. [RESTful API Design Principles](#restful-api-design-principles)
3. [Resource Design Patterns](#resource-design-patterns)
4. [Authentication and Authorization](#authentication-and-authorization)
5. [Multi-Tenancy and Data Isolation](#multi-tenancy-and-data-isolation)
6. [Rate Limiting Strategies](#rate-limiting-strategies)
7. [Pagination, Filtering, and Search](#pagination-filtering-and-search)
8. [Webhook Patterns](#webhook-patterns)
9. [Error Handling](#error-handling)
10. [Versioning Strategy](#versioning-strategy)
11. [Performance Optimization](#performance-optimization)
12. [Real-World Examples](#real-world-examples)

## Overview

This document establishes comprehensive API design patterns for Property Management Systems (PMS), drawing from industry leaders like Yardi Voyager WebServices, Buildium API, AppFolio, and RealPage, combined with modern REST API best practices from Stripe, GitHub, and Microsoft.

### Design Philosophy

1. **Developer Experience First**: APIs should be intuitive, well-documented, and consistent
2. **Predictable**: Follow REST conventions and industry standards (RESO, RETS)
3. **Resilient**: Handle errors gracefully, provide clear error messages
4. **Secure**: Multi-layered security with OAuth 2.0, API keys, and role-based access
5. **Performant**: Optimized for high-volume property management operations
6. **Evolvable**: Support versioning and backward compatibility

### API Maturity Model

| Level | Characteristics | Example |
|-------|----------------|---------|
| **Level 0** | HTTP as transport | Legacy XML-RPC, SOAP |
| **Level 1** | Resources | Individual URIs for properties, leases |
| **Level 2** | HTTP Verbs | GET, POST, PATCH, DELETE |
| **Level 3** | HATEOAS | Hypermedia controls, next actions |
| **Level 4** | GraphQL | Client-specified queries |

**Target:** Level 2-3 (REST with selective HATEOAS for discoverability)

## RESTful API Design Principles

### Resource Naming

**Standard:** Use plural nouns, hierarchical where appropriate, kebab-case for multi-word resources

```
# Good Examples
GET    /properties
GET    /properties/{property_id}
GET    /properties/{property_id}/units
GET    /properties/{property_id}/financial-summary
GET    /leases/{lease_id}/payment-schedule

# Bad Examples (Avoid)
GET    /property              # Singular noun
GET    /getProperties         # Verb in URL
GET    /properties/123/units  # Not using path parameter convention
POST   /createLease           # RPC-style naming
```

### HTTP Methods

**Standard:** Use appropriate HTTP methods for CRUD operations

| Method | Purpose | Idempotent | Safe | Example |
|--------|---------|------------|------|---------|
| **GET** | Retrieve resource(s) | Yes | Yes | `GET /properties/123` |
| **POST** | Create new resource | No | No | `POST /leases` |
| **PUT** | Full replacement | Yes | No | `PUT /properties/123` (rarely used) |
| **PATCH** | Partial update | No* | No | `PATCH /leases/456` |
| **DELETE** | Delete resource | Yes | No | `DELETE /properties/123` |

*PATCH can be made idempotent with proper implementation

**Custom Actions:** Use POST for non-CRUD operations

```
POST   /leases/{id}/activate          # State transition
POST   /leases/{id}/terminate         # State transition
POST   /leases/{id}/send-renewal-notice
POST   /payments/bulk-process         # Batch operation
POST   /reports/rent-roll/generate    # Report generation
POST   /properties/{id}/sync-from-mls # External sync
```

### Status Codes

**Standard:** Use appropriate HTTP status codes

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| **200 OK** | Success | Successful GET, PATCH, DELETE |
| **201 Created** | Resource created | Successful POST (with Location header) |
| **202 Accepted** | Async processing | Long-running operations |
| **204 No Content** | Success, no body | Successful DELETE, or empty results |
| **400 Bad Request** | Invalid input | Validation errors, malformed JSON |
| **401 Unauthorized** | Authentication required | Missing/invalid API key or token |
| **403 Forbidden** | Access denied | User lacks permission |
| **404 Not Found** | Resource not found | Invalid property/lease ID |
| **409 Conflict** | Business rule violation | Overlapping lease dates, duplicate records |
| **422 Unprocessable Entity** | Semantic errors | Valid JSON but business logic errors |
| **429 Too Many Requests** | Rate limit exceeded | Exceeded API quota |
| **500 Internal Server Error** | Server error | Unexpected server errors |
| **503 Service Unavailable** | Service down | Maintenance, overload |

## Resource Design Patterns

### Properties Resource

```
Base Path: /v1/properties

# Collection Operations
GET    /properties                    # List properties
POST   /properties                    # Create property

# Single Resource Operations
GET    /properties/{id}               # Get property details
PATCH  /properties/{id}               # Update property
DELETE /properties/{id}               # Soft delete property

# Sub-Resources
GET    /properties/{id}/units         # List units in property
GET    /properties/{id}/amenities     # List property amenities
GET    /properties/{id}/documents     # List property documents
POST   /properties/{id}/documents     # Upload document
GET    /properties/{id}/images        # List property images
POST   /properties/{id}/images        # Upload image

# Computed Resources
GET    /properties/{id}/financial-summary    # Aggregated financials
GET    /properties/{id}/occupancy-history    # Historical occupancy
GET    /properties/{id}/maintenance-summary  # Work order stats

# Actions
POST   /properties/{id}/sync-from-yardi      # Sync from Yardi
POST   /properties/{id}/generate-insurance-report
```

**Property Object Schema:**

```json
{
  "id": "prop_2zXj9mK8vN",
  "object": "property",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "property_name": "Sunset Towers",
  "property_type": "multifamily",
  "property_code": "SUNST001",
  "year_built": 2015,
  "total_units": 120,
  "rentable_square_feet": 85000,
  "land_area_acres": 2.5,
  "address": {
    "street_address_line_1": "123 Main Street",
    "street_address_line_2": null,
    "city": "San Francisco",
    "state_province_code": "CA",
    "postal_code": "94102",
    "country_code": "US",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "amenities": [
    {
      "id": "amenity_abc123",
      "amenity_type": "swimming_pool",
      "description": "Heated outdoor pool",
      "is_available": true,
      "additional_fee_amount": 0
    },
    {
      "id": "amenity_def456",
      "amenity_type": "fitness_center",
      "description": "24/7 gym access",
      "is_available": true,
      "additional_fee_amount": 0
    }
  ],
  "management": {
    "property_manager_id": "user_xyz789",
    "management_company": "PropTech Management LLC",
    "management_start_date": "2020-01-01"
  },
  "financial_summary": {
    "total_monthly_rent": 360000,
    "total_annual_revenue": 4320000,
    "average_rent_per_unit": 3000,
    "average_rent_per_sqft": 4.24,
    "occupancy_rate_percentage": 95.5,
    "collection_rate_percentage": 98.5,
    "net_operating_income": 3240000,
    "operating_expense_ratio": 0.25
  },
  "external_integrations": {
    "yardi_property_code": "SUNST001",
    "mls_listing_ids": ["ML123456"],
    "quickbooks_class_id": "QB789"
  },
  "metadata": {
    "portfolio_segment": "premium",
    "acquisition_date": "2020-01-01",
    "last_appraisal_date": "2024-06-15",
    "last_appraisal_value": 24000000
  },
  "links": {
    "self": "/v1/properties/prop_2zXj9mK8vN",
    "units": "/v1/properties/prop_2zXj9mK8vN/units",
    "leases": "/v1/leases?property_id=prop_2zXj9mK8vN",
    "documents": "/v1/properties/prop_2zXj9mK8vN/documents"
  }
}
```

### Units Resource

```
# Top-Level Collection
GET    /units                         # List all units (with filters)
GET    /units/{id}                    # Get unit details
PATCH  /units/{id}                    # Update unit

# As Sub-Resource
GET    /properties/{property_id}/units
POST   /properties/{property_id}/units

# Unit-Specific Operations
GET    /units/{id}/lease-history      # Historical leases
GET    /units/{id}/maintenance-history # Work orders
GET    /units/{id}/valuation          # Current market rent estimate
POST   /units/{id}/schedule-showing   # Schedule showing

# Filtered Queries
GET    /units?is_vacant=true          # Vacant units only
GET    /units?bedrooms=2&bathrooms[gte]=2
GET    /units?monthly_rent_amount[between]=2000,3000
```

**Unit Object Schema:**

```json
{
  "id": "unit_abc123",
  "object": "unit",
  "property_id": "prop_2zXj9mK8vN",
  "unit_number": "2B-304",
  "unit_type": "apartment",
  "floor_number": 3,
  "building": "Building B",
  "bedrooms": 2,
  "bathrooms_full": 2,
  "bathrooms_half": 0,
  "square_feet": 950,
  "is_occupied": false,
  "is_available_for_lease": true,
  "market_rent_amount": 3200,
  "current_lease": null,
  "features": {
    "has_balcony": true,
    "has_washer_dryer": true,
    "has_dishwasher": true,
    "has_air_conditioning": true,
    "has_fireplace": false,
    "parking_spaces": 1,
    "storage_units": 0
  },
  "pet_policy": {
    "allows_pets": true,
    "allows_dogs": true,
    "allows_cats": true,
    "max_pets": 2,
    "pet_deposit_amount": 500,
    "monthly_pet_rent": 50
  },
  "accessibility": {
    "is_ada_compliant": false,
    "has_elevator_access": true,
    "has_wheelchair_access": false
  },
  "last_renovation_date": "2023-06-15",
  "created_at": "2020-01-15T10:00:00Z",
  "updated_at": "2025-01-10T14:30:00Z"
}
```

### Leases Resource

```
# Collection Operations
GET    /leases                        # List leases (filterable)
POST   /leases                        # Create lease
GET    /leases/{id}                   # Get lease details
PATCH  /leases/{id}                   # Update lease
DELETE /leases/{id}                   # Cancel/void lease

# Sub-Resources
GET    /leases/{id}/terms             # Lease financial terms
GET    /leases/{id}/occupants         # All occupants
GET    /leases/{id}/documents         # Lease documents
POST   /leases/{id}/documents         # Upload signed lease
GET    /leases/{id}/payment-schedule  # Payment schedule
GET    /leases/{id}/charges           # All charges
GET    /leases/{id}/payments          # All payments
GET    /leases/{id}/amendments        # Lease amendments
POST   /leases/{id}/amendments        # Add amendment

# State Transitions (POST for actions)
POST   /leases/{id}/activate          # Activate lease
POST   /leases/{id}/terminate         # Early termination
POST   /leases/{id}/renew             # Create renewal lease
POST   /leases/{id}/send-renewal-notice # Send renewal reminder
POST   /leases/{id}/transfer          # Transfer to new unit

# Computed Resources
GET    /leases/{id}/balance           # Current balance
GET    /leases/{id}/delinquency-status # Delinquency details
```

**Lease Object Schema:**

```json
{
  "id": "lease_def456",
  "object": "lease",
  "property_id": "prop_2zXj9mK8vN",
  "unit_id": "unit_abc123",
  "primary_tenant_id": "tenant_xyz789",
  "lease_status": "active",
  "lease_type": "fixed_term",
  "lease_start_date": "2025-02-01",
  "lease_end_date": "2026-01-31",
  "move_in_date": "2025-02-01",
  "move_out_date": null,
  "notice_date": null,
  "notice_period_days": 60,
  "terms": {
    "monthly_rent_amount": 3200,
    "security_deposit_amount": 3200,
    "pet_deposit_amount": 500,
    "parking_fee_amount": 150,
    "storage_fee_amount": 0,
    "total_monthly_charges": 3400
  },
  "rent_schedule": {
    "rent_due_day_of_month": 1,
    "grace_period_days": 5,
    "late_fee_type": "percentage",
    "late_fee_percentage": 5.0,
    "late_fee_flat_amount": null
  },
  "occupants": [
    {
      "tenant_id": "tenant_xyz789",
      "is_primary": true,
      "relationship": "self"
    },
    {
      "tenant_id": "tenant_pqr345",
      "is_primary": false,
      "relationship": "spouse"
    }
  ],
  "guarantors": [],
  "pets": [
    {
      "pet_type": "dog",
      "breed": "Golden Retriever",
      "name": "Max",
      "weight_pounds": 65
    }
  ],
  "balance_summary": {
    "current_balance": 0,
    "total_charges": 6800,
    "total_payments": 6800,
    "total_credits": 0,
    "is_delinquent": false,
    "days_delinquent": 0
  },
  "renewal": {
    "is_eligible_for_renewal": true,
    "renewal_notice_sent_at": "2025-10-01T09:00:00Z",
    "renewal_decision_due_date": "2025-11-30",
    "renewal_decision": null
  },
  "created_at": "2025-01-10T11:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z",
  "metadata": {
    "source": "direct_sign",
    "agent_id": "agent_123",
    "commission_paid": true
  }
}
```

### Tenants Resource

```
GET    /tenants                       # List tenants
POST   /tenants                       # Create tenant profile
GET    /tenants/{id}                  # Get tenant details
PATCH  /tenants/{id}                  # Update tenant
DELETE /tenants/{id}                  # Soft delete (GDPR right to be forgotten)

# Sub-Resources
GET    /tenants/{id}/leases           # Tenant's lease history
GET    /tenants/{id}/payment-history  # Payment history
GET    /tenants/{id}/documents        # Tenant documents
GET    /tenants/{id}/communications   # Communication history
GET    /tenants/{id}/work-orders      # Tenant's work orders

# Actions
POST   /tenants/{id}/send-notice      # Send notice to tenant
POST   /tenants/{id}/schedule-screening # Request background check
POST   /tenants/{id}/export-data      # GDPR data export
```

### Payments Resource

```
GET    /payments                      # List payments
POST   /payments                      # Create payment
GET    /payments/{id}                 # Get payment details
PATCH  /payments/{id}                 # Update payment (limited)

# Actions
POST   /payments/{id}/refund          # Process refund
POST   /payments/{id}/void            # Void payment
POST   /payments/bulk-process         # Batch payment processing
POST   /payments/retry-failed         # Retry failed ACH payments

# Filtering
GET    /payments?lease_id=lease_def456
GET    /payments?status=completed
GET    /payments?payment_date[gte]=2025-01-01
GET    /payments?payment_method_type=ach
```

**Payment Object Schema:**

```json
{
  "id": "pay_ghi789",
  "object": "payment",
  "lease_id": "lease_def456",
  "tenant_id": "tenant_xyz789",
  "property_id": "prop_2zXj9mK8vN",
  "amount": 3400,
  "currency": "usd",
  "payment_status": "completed",
  "payment_type": "rent",
  "payment_method": {
    "type": "ach",
    "last_four": "6789",
    "bank_name": "Chase",
    "account_type": "checking"
  },
  "payment_date": "2025-02-01",
  "processed_at": "2025-02-01T08:30:00Z",
  "settled_at": "2025-02-03T10:00:00Z",
  "payment_processor": "stripe",
  "processor_payment_id": "pi_abc123xyz",
  "fees": {
    "processing_fee_amount": 10,
    "convenience_fee_amount": 0,
    "total_fees": 10
  },
  "allocation": [
    {
      "charge_type": "rent",
      "amount": 3200
    },
    {
      "charge_type": "parking",
      "amount": 150
    },
    {
      "charge_type": "pet_rent",
      "amount": 50
    }
  ],
  "metadata": {
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "initiated_by": "tenant_portal"
  },
  "created_at": "2025-02-01T08:25:00Z",
  "updated_at": "2025-02-03T10:00:00Z"
}
```

## Authentication and Authorization

### OAuth 2.0 Implementation

**Recommended Flow:** Authorization Code with PKCE (for web/mobile apps)

**Token Endpoint:**
```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE&
redirect_uri=https://yourapp.com/callback&
client_id=CLIENT_ID&
code_verifier=CODE_VERIFIER
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_abc123xyz",
  "scope": "properties.read leases.write payments.read"
}
```

**Using Access Token:**
```
GET /v1/properties
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key Authentication

**For Server-to-Server Integrations:**

```
GET /v1/properties
Authorization: Bearer sk_live_abc123xyz
```

**API Key Types:**
- `sk_live_*`: Production secret keys
- `sk_test_*`: Test environment keys
- `pk_live_*`: Publishable keys (client-side, limited scope)

**Key Management:**
- Rotate keys every 90 days
- Support multiple active keys (for zero-downtime rotation)
- Revoke compromised keys immediately
- Audit key usage in logs

### Role-Based Access Control (RBAC)

**Roles:**

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Property Manager** | Full access to assigned properties | Day-to-day management |
| **Leasing Agent** | Read properties/units, create/edit leases | Leasing operations |
| **Maintenance** | Read work orders, update status | Field technicians |
| **Accountant** | Read financial data, generate reports | Accounting team |
| **Owner** | Read-only access to owned properties | Property owners |
| **Admin** | Full access, user management | System administrators |
| **API Integration** | Custom scopes | Third-party integrations |

**Scope-Based Access (OAuth 2.0):**

```
properties.read
properties.write
leases.read
leases.write
tenants.read
tenants.write (includes PII)
payments.read
payments.write
financials.read
reports.read
admin.users.read
admin.users.write
```

**JWT Claims:**

```json
{
  "sub": "user_abc123",
  "email": "manager@proptech.com",
  "organization_id": "org_xyz789",
  "roles": ["property_manager"],
  "scopes": ["properties.read", "properties.write", "leases.read", "leases.write"],
  "property_ids": ["prop_123", "prop_456"],
  "exp": 1737014400,
  "iat": 1737010800
}
```

### Tenant Isolation

**Organization-Level Isolation:**

Every API request is scoped to an organization:

```
GET /v1/properties
Authorization: Bearer {token_with_org_context}

# Automatically filters to organization_id from JWT
# No cross-organization data leakage
```

**Database-Level Isolation:**

```sql
-- Row-Level Security (PostgreSQL)
CREATE POLICY tenant_isolation ON properties
  USING (organization_id = current_setting('app.current_organization_id')::bigint);

-- Application enforces organization_id in all queries
SELECT * FROM properties
WHERE organization_id = $1  -- From JWT claim
  AND property_type = $2;
```

## Multi-Tenancy and Data Isolation

### Multi-Tenancy Strategies

**1. Schema-Per-Tenant (High Isolation)**

```
Advantages:
✅ Strong data isolation
✅ Easy backup/restore per tenant
✅ Customizable schema per tenant
✅ Simple compliance (GDPR data deletion)

Disadvantages:
❌ Schema migration complexity (N schemas)
❌ Limited scalability (schema limits)
❌ Higher database costs

Use Case: Enterprise clients requiring dedicated schemas
```

**2. Row-Level Security (Balanced)**

```
Advantages:
✅ Single schema (easier migrations)
✅ Scalable to 10,000+ tenants
✅ Cost-effective
✅ Flexible querying

Disadvantages:
❌ Requires careful query filtering
❌ Risk of data leakage if bug

Use Case: Standard SaaS (Yardi, Buildium model)

Implementation:
-- PostgreSQL RLS
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
CREATE POLICY org_isolation ON properties
  USING (organization_id = current_setting('app.org_id')::uuid);

-- Application sets context per request
SET app.org_id = '123e4567-e89b-12d3-a456-426614174000';
```

**3. Separate Databases (Highest Isolation)**

```
Advantages:
✅ Complete isolation
✅ Independent scaling
✅ Regulatory compliance (data residency)

Disadvantages:
❌ High operational overhead
❌ Complex cross-tenant analytics
❌ Expensive

Use Case: Enterprise contracts, regulated industries
```

**Recommended Approach:** Row-level security with organization_id for most PropTech SaaS applications

## Rate Limiting Strategies

### Rate Limit Tiers

| Tier | Rate Limit | Burst Limit | Use Case |
|------|-----------|-------------|----------|
| **Free** | 100 req/min | 200 req/min | Trial users, demos |
| **Starter** | 500 req/min | 1,000 req/min | Small property managers |
| **Professional** | 2,000 req/min | 4,000 req/min | Mid-sized portfolios |
| **Enterprise** | 10,000 req/min | 20,000 req/min | Large integrations |
| **Custom** | Negotiated | Negotiated | Yardi, MRI integrations |

### Implementation (Token Bucket Algorithm)

**Redis-Based Rate Limiting:**

```python
import redis
import time

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    def check_rate_limit(self, api_key: str, max_requests: int, window_seconds: int) -> tuple[bool, dict]:
        """
        Returns (is_allowed, headers)
        """
        key = f"rate_limit:{api_key}"
        current_time = int(time.time())
        window_start = current_time - window_seconds

        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        current_requests = self.redis.zcard(key)

        headers = {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(max(0, max_requests - current_requests)),
            "X-RateLimit-Reset": str(current_time + window_seconds)
        }

        if current_requests >= max_requests:
            headers["Retry-After"] = str(window_seconds)
            return False, headers

        # Add current request
        self.redis.zadd(key, {current_time: current_time})
        self.redis.expire(key, window_seconds)

        return True, headers
```

**Response Headers:**

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 2000
X-RateLimit-Remaining: 1847
X-RateLimit-Reset: 1737014460
```

**Rate Limit Exceeded Response:**

```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 2000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1737014460
Retry-After: 60

{
  "error": {
    "type": "rate_limit_error",
    "code": "rate_limit_exceeded",
    "message": "API rate limit exceeded. Limit: 2000 requests per minute.",
    "retry_after": 60
  }
}
```

### Endpoint-Specific Limits

**More Restrictive Limits for Expensive Operations:**

```
# Standard Endpoints
GET    /properties           → 2000/min
GET    /leases               → 2000/min

# Report Generation (CPU-intensive)
POST   /reports/rent-roll    → 10/min
POST   /reports/financial    → 10/min

# Bulk Operations
POST   /payments/bulk-process → 100/min
POST   /leases/bulk-create    → 50/min

# Webhooks (prevent abuse)
POST   /webhooks/test         → 5/min
```

## Pagination, Filtering, and Search

### Cursor-Based Pagination (Recommended)

**Stripe-Style Cursor Pagination:**

```
GET /v1/properties?limit=20&starting_after=prop_xyz789

Response:
{
  "object": "list",
  "data": [
    { "id": "prop_abc123", ... },
    { "id": "prop_def456", ... },
    ...
  ],
  "has_more": true,
  "url": "/v1/properties"
}

# Next Page
GET /v1/properties?limit=20&starting_after=prop_def456

# Previous Page
GET /v1/properties?limit=20&ending_before=prop_abc123
```

**Advantages:**
- Consistent results even with concurrent writes
- No "page drift" problem
- Better performance (no OFFSET)

**Implementation:**

```sql
-- Next page
SELECT * FROM properties
WHERE id > $starting_after
  AND organization_id = $org_id
ORDER BY id ASC
LIMIT $limit + 1;  -- Fetch N+1 to determine has_more

-- Previous page
SELECT * FROM properties
WHERE id < $ending_before
  AND organization_id = $org_id
ORDER BY id DESC
LIMIT $limit + 1;
```

### Offset-Based Pagination (Alternative)

```
GET /v1/properties?limit=20&offset=40

Response:
{
  "data": [...],
  "pagination": {
    "total": 1250,
    "limit": 20,
    "offset": 40,
    "current_page": 3,
    "total_pages": 63
  }
}
```

**Use Case:** When total count is needed, UI pagination with page numbers

### Filtering

**Query Parameter Patterns:**

```
# Exact Match
GET /properties?city=San Francisco&state_province_code=CA

# Range Filters
GET /properties?year_built[gte]=2010&year_built[lte]=2020
GET /units?monthly_rent_amount[between]=2000,3000

# Array Filters (multiple values)
GET /properties?property_type[in]=multifamily,mixed_use
GET /leases?lease_status[in]=active,pending

# Boolean Filters
GET /units?is_vacant=true&has_parking=true

# Pattern Matching
GET /properties?property_name[like]=Sunset%
GET /tenants?email[contains]=gmail.com

# Date Filters
GET /leases?lease_start_date[gte]=2025-01-01
GET /payments?payment_date[between]=2025-01-01,2025-01-31

# Geospatial Filters
GET /properties?near=-122.419,37.775&radius=5mi
GET /properties?bbox=-122.5,37.7,-122.3,37.8

# Null/Not Null
GET /leases?move_out_date[null]=true   # Leases without move-out
GET /units?current_lease_id[null]=false # Occupied units
```

### Sorting

```
GET /properties?sort=created_at          # Ascending (oldest first)
GET /properties?sort=-created_at         # Descending (newest first)
GET /properties?sort=city,-monthly_rent  # Multi-field sort
```

### Field Selection (Sparse Fieldsets)

```
GET /properties?fields=id,property_name,total_units,occupancy_rate

Response:
{
  "data": [
    {
      "id": "prop_123",
      "property_name": "Sunset Towers",
      "total_units": 120,
      "occupancy_rate_percentage": 95.5
    }
  ]
}
```

**Benefits:**
- Reduced payload size
- Faster response times
- Lower bandwidth costs

### Search

**Full-Text Search (Elasticsearch):**

```
GET /properties/search?q=luxury apartment downtown&search_fields=property_name,description,amenities

GET /tenants/search?q=john smith&search_fields=first_name,last_name,email
```

**Advanced Search (Structured Query):**

```json
POST /properties/search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "property_type": "multifamily" } },
        { "range": { "total_units": { "gte": 100 } } }
      ],
      "filter": [
        { "term": { "city": "San Francisco" } },
        { "range": { "year_built": { "gte": 2010 } } }
      ]
    }
  },
  "sort": [
    { "occupancy_rate_percentage": { "order": "desc" } }
  ]
}
```

## Webhook Patterns

### Webhook Events

**Event Types:**

```
# Lease Events
lease.created
lease.activated
lease.updated
lease.terminated
lease.renewed
lease.expiring_soon

# Payment Events
payment.created
payment.processing
payment.completed
payment.failed
payment.refunded

# Work Order Events
work_order.created
work_order.assigned
work_order.completed
work_order.escalated

# Property Events
property.created
property.updated
unit.occupied
unit.vacant

# Tenant Events
tenant.created
tenant.application_submitted
tenant.screening_completed
tenant.move_in
tenant.move_out
```

### Webhook Configuration

**Register Webhook Endpoint:**

```
POST /v1/webhook-endpoints
{
  "url": "https://yourapp.com/webhooks/proptech",
  "enabled_events": [
    "lease.activated",
    "payment.completed",
    "payment.failed"
  ],
  "description": "Production webhook for lease and payment events"
}

Response:
{
  "id": "we_abc123",
  "url": "https://yourapp.com/webhooks/proptech",
  "enabled_events": ["lease.activated", "payment.completed", "payment.failed"],
  "secret": "whsec_xyz789...",
  "created_at": "2025-01-15T10:00:00Z"
}
```

### Webhook Payload

```json
{
  "id": "evt_abc123",
  "type": "payment.completed",
  "created_at": "2025-02-01T10:30:00Z",
  "data": {
    "object": {
      "id": "pay_ghi789",
      "object": "payment",
      "lease_id": "lease_def456",
      "amount": 3400,
      "payment_status": "completed",
      "payment_date": "2025-02-01",
      "processed_at": "2025-02-01T10:30:00Z"
    }
  },
  "previous_attributes": {
    "payment_status": "processing"
  }
}
```

### Webhook Signature Verification

**HMAC SHA-256 Signature (Stripe Pattern):**

```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature_header: str, secret: str) -> bool:
    """
    Verify webhook signature to prevent spoofing
    """
    # Extract timestamp and signature
    # Format: "t=1737014400,v1=abc123..."
    timestamp, signature = parse_signature_header(signature_header)

    # Construct signed payload
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"

    # Compute expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Compare signatures (constant-time comparison)
    return hmac.compare_digest(expected_signature, signature)

# Usage in webhook handler
@app.post("/webhooks/proptech")
async def handle_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-PropTech-Signature")
    webhook_secret = "whsec_xyz789..."

    if not verify_webhook_signature(payload, signature, webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = json.loads(payload)
    # Process event...
```

### Webhook Retry Logic

**Delivery Guarantees:**
- At least once delivery (may receive duplicates)
- Idempotency required in webhook handlers
- Exponential backoff retry: 1s, 5s, 30s, 2m, 10m, 1h
- Maximum 3 days of retries
- Disable endpoint after 10 consecutive failures

**Response Requirements:**
- Return 2xx status code within 10 seconds
- Process asynchronously (queue event, respond immediately)
- Include idempotency key handling

```python
from fastapi import FastAPI, Request, BackgroundTasks

app = FastAPI()

@app.post("/webhooks/proptech")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.body()

    # Verify signature first
    verify_webhook_signature(...)

    # Parse event
    event = json.loads(payload)

    # Queue for async processing
    background_tasks.add_task(process_webhook_event, event)

    # Respond immediately (< 10 seconds)
    return {"received": True}

async def process_webhook_event(event: dict):
    # Idempotency check
    event_id = event["id"]
    if await event_already_processed(event_id):
        return  # Skip duplicate

    # Process event
    if event["type"] == "payment.completed":
        await handle_payment_completed(event["data"]["object"])
    elif event["type"] == "lease.activated":
        await handle_lease_activated(event["data"]["object"])

    # Mark as processed
    await mark_event_processed(event_id)
```

## Error Handling

### Error Response Format

**RFC 7807 Problem Details:**

```json
{
  "error": {
    "type": "validation_error",
    "code": "invalid_lease_dates",
    "message": "Lease end date must be after start date",
    "param": "lease_end_date",
    "request_id": "req_abc123xyz",
    "details": [
      {
        "field": "lease_end_date",
        "message": "Must be after lease_start_date (2025-01-01)",
        "code": "date_range_invalid"
      }
    ],
    "documentation_url": "https://docs.proptech.com/errors/invalid_lease_dates"
  }
}
```

### Error Types and Codes

| HTTP Status | Error Type | Code | Description |
|-------------|-----------|------|-------------|
| 400 | `validation_error` | `invalid_parameters` | Malformed request |
| 400 | `validation_error` | `invalid_lease_dates` | Business rule violation |
| 401 | `authentication_error` | `invalid_api_key` | Missing/invalid API key |
| 401 | `authentication_error` | `expired_token` | Expired OAuth token |
| 403 | `authorization_error` | `insufficient_permissions` | Lacks required permission |
| 404 | `resource_not_found` | `property_not_found` | Property doesn't exist |
| 409 | `conflict_error` | `lease_overlap` | Unit already leased |
| 422 | `business_rule_error` | `unit_already_occupied` | Semantic error |
| 429 | `rate_limit_error` | `rate_limit_exceeded` | Too many requests |
| 500 | `server_error` | `internal_error` | Server failure |
| 503 | `server_error` | `service_unavailable` | Temporary outage |

### Detailed Validation Errors

```json
{
  "error": {
    "type": "validation_error",
    "code": "invalid_parameters",
    "message": "One or more parameters are invalid",
    "details": [
      {
        "field": "monthly_rent_amount",
        "message": "Must be greater than 0",
        "code": "out_of_range",
        "value": -1000
      },
      {
        "field": "lease_start_date",
        "message": "Must be in format YYYY-MM-DD",
        "code": "invalid_format",
        "value": "01/15/2025"
      },
      {
        "field": "tenant_id",
        "message": "Tenant with ID 'tenant_invalid' not found",
        "code": "not_found",
        "value": "tenant_invalid"
      }
    ]
  }
}
```

## Versioning Strategy

### URL Versioning (Recommended)

```
https://api.proptech.com/v1/properties
https://api.proptech.com/v2/properties
```

**Advantages:**
- Clear, explicit versioning
- Easy to route at gateway level
- Simple client implementation

### Version Lifecycle

| Version | Status | Support Level | End of Life |
|---------|--------|---------------|-------------|
| v3 | Beta | Preview only | - |
| v2 | Current | Full support | - |
| v1 | Deprecated | Security fixes only | 2025-12-31 |

**Deprecation Process:**
1. **Announce**: 12 months before sunset
2. **Deprecation Headers**: Add `Sunset` header (RFC 8594)
3. **Migration Guide**: Publish comprehensive migration docs
4. **Grace Period**: Maintain for 12 months
5. **Sunset**: Disable endpoint, return 410 Gone

**Deprecation Header Example:**

```
HTTP/1.1 200 OK
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
Deprecation: true
Link: <https://docs.proptech.com/api/v2/migration>; rel="successor-version"
```

## Performance Optimization

### Response Times

**Target SLAs:**

| Endpoint Type | P50 | P95 | P99 |
|--------------|-----|-----|-----|
| Simple GET (by ID) | < 50ms | < 100ms | < 200ms |
| List/Search | < 200ms | < 500ms | < 1s |
| POST/PATCH | < 300ms | < 800ms | < 1.5s |
| Reports | < 2s | < 5s | < 10s |

### Caching Strategies

**Cache-Control Headers:**

```
# Cacheable resources (rarely change)
GET /properties/prop_123
Cache-Control: public, max-age=300, stale-while-revalidate=60

# Dynamic resources (frequently change)
GET /leases?status=active
Cache-Control: private, max-age=60

# Never cache
GET /payments
Cache-Control: no-store, no-cache
```

**ETags for Conditional Requests:**

```
# Initial request
GET /properties/prop_123
Response:
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
{ ... }

# Subsequent request
GET /properties/prop_123
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# Response (if unchanged)
HTTP/1.1 304 Not Modified
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

### Database Query Optimization

**N+1 Query Prevention:**

```
# Bad: N+1 queries
GET /properties?include=units

SELECT * FROM properties WHERE organization_id = $1;
-- For each property:
SELECT * FROM units WHERE property_id = $1;

# Good: Single query with JOIN
SELECT p.*, json_agg(u.*) as units
FROM properties p
LEFT JOIN units u ON u.property_id = p.id
WHERE p.organization_id = $1
GROUP BY p.id;
```

**Eager Loading:**

```python
# SQLAlchemy example
properties = db.query(Property)\
    .options(joinedload(Property.units))\
    .filter(Property.organization_id == org_id)\
    .all()
```

## Real-World Examples

### Example: Yardi Voyager Integration Pattern

```python
# Sync properties from Yardi to PropTech platform
import requests
from xml.etree import ElementTree as ET

class YardiIntegration:
    def __init__(self, yardi_username, yardi_password, yardi_entity):
        self.username = yardi_username
        self.password = yardi_password
        self.entity = yardi_entity
        self.base_url = "https://www.yardipcv.com/apis/webservices"

    def sync_properties(self):
        # Fetch properties from Yardi
        yardi_properties = self.get_yardi_properties()

        # Transform and sync to PropTech API
        for yardi_prop in yardi_properties:
            proptech_property = self.transform_yardi_to_proptech(yardi_prop)
            self.upsert_proptech_property(proptech_property)

    def get_yardi_properties(self):
        # Yardi WebServices SOAP request
        soap_envelope = f"""
        <Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
          <Header>
            <UserName>{self.username}</UserName>
            <Password>{self.password}</Password>
          </Header>
          <Body>
            <GetProperties xmlns="http://www.yardi.com/webservices">
              <EntityCode>{self.entity}</EntityCode>
            </GetProperties>
          </Body>
        </Envelope>
        """

        response = requests.post(
            f"{self.base_url}/PropertyService.asmx",
            data=soap_envelope,
            headers={"Content-Type": "text/xml"}
        )

        # Parse XML response
        tree = ET.fromstring(response.content)
        properties = tree.findall(".//Property")
        return properties

    def transform_yardi_to_proptech(self, yardi_prop):
        return {
            "property_name": yardi_prop.find("PropertyName").text,
            "property_code": yardi_prop.find("PropertyCode").text,
            "total_units": int(yardi_prop.find("UnitCount").text),
            "address": {
                "street_address_line_1": yardi_prop.find("Address1").text,
                "city": yardi_prop.find("City").text,
                "state_province_code": yardi_prop.find("State").text,
                "postal_code": yardi_prop.find("ZipCode").text
            },
            "external_integrations": {
                "yardi_property_code": yardi_prop.find("PropertyCode").text
            }
        }

    def upsert_proptech_property(self, property_data):
        # Check if property exists
        yardi_code = property_data["external_integrations"]["yardi_property_code"]
        existing = self.find_property_by_yardi_code(yardi_code)

        if existing:
            # Update existing property
            response = requests.patch(
                f"https://api.proptech.com/v1/properties/{existing['id']}",
                json=property_data,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        else:
            # Create new property
            response = requests.post(
                "https://api.proptech.com/v1/properties",
                json=property_data,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

        return response.json()
```

---

## References

1. **Stripe API Design**: https://stripe.com/docs/api
2. **Microsoft REST API Guidelines**: https://github.com/microsoft/api-guidelines
3. **Yardi Voyager WebServices**: https://www.yardi.com/products/voyager/
4. **Buildium API**: https://api.buildium.com/
5. **AppFolio API**: https://developer.appfolio.com/
6. **RESO Web API**: https://www.reso.org/reso-web-api/
7. **OAuth 2.0 RFC 6749**: https://tools.ietf.org/html/rfc6749
8. **RFC 7807 Problem Details**: https://tools.ietf.org/html/rfc7807

---

*This document is maintained by the PropTech API Standards Committee. For questions or updates, contact api@proptech.com.*
