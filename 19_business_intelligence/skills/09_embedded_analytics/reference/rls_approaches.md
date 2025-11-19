# Row-Level Security (RLS) Approaches

## Overview

Row-Level Security ensures users only see data they're authorized to access in embedded analytics. Critical for multi-tenant SaaS applications.

## RLS Implementation Levels

### 1. Database-Level RLS (Most Secure)

**PostgreSQL Example**:
```sql
-- Enable RLS on table
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;

-- Create policy for tenant isolation
CREATE POLICY tenant_isolation ON sales
  FOR ALL
  TO app_user
  USING (tenant_id = current_setting('app.current_tenant')::int);

-- Set tenant context in session
SET app.current_tenant = '123';

-- All queries automatically filtered
SELECT * FROM sales; -- Only returns data for tenant 123
```

**Pros**:
- Enforced at data layer
- Cannot be bypassed
- Works with any BI tool
- Centralized security logic

**Cons**:
- Database-specific syntax
- Performance overhead
- Complexity in migration
- Limited dynamic filtering

---

### 2. View-Based RLS

**SQL View Example**:
```sql
-- Create view with RLS logic
CREATE VIEW sales_filtered AS
SELECT s.*
FROM sales s
INNER JOIN user_tenant_access uta
  ON s.tenant_id = uta.tenant_id
WHERE uta.user_id = current_user_id();

-- Grant access only to view
GRANT SELECT ON sales_filtered TO bi_user;
REVOKE SELECT ON sales FROM bi_user;

-- BI tool uses view instead of table
SELECT * FROM sales_filtered;
```

**Pros**:
- Simple to implement
- Database-agnostic
- Easy to audit
- Can combine multiple filters

**Cons**:
- Must remember to use view
- View proliferation
- Performance concerns with complex joins
- Less flexible than policies

---

### 3. BI Platform RLS (Application-Level)

**Tableau Data Source Filter**:
```javascript
// Backend: Generate token with RLS
const token = tableau.generateToken({
  username: user.email,
  filters: {
    'tenant_id': user.tenantId,
    'region': user.region,
    'department': user.department
  }
});

// Tableau applies filter to all queries
```

**Power BI RLS Roles**:
```dax
-- Define role in Power BI Desktop
[tenant_id] = USERPRINCIPALNAME()

-- Or dynamic using custom data
[tenant_id] = LOOKUPVALUE(
  Users[tenant_id],
  Users[email],
  USERPRINCIPALNAME()
)
```

**Looker Access Filters**:
```javascript
// User attributes in Looker
{
  "tenant_id": "123",
  "department": "sales",
  "region": "west"
}

// LookML model
access_grant: tenant_access {
  user_attribute: tenant_id
  allowed_values: ["123"]
}
```

**Pros**:
- Platform-native
- Easy to configure
- Good performance
- UI for management

**Cons**:
- Platform-specific
- Can be bypassed if misconfigured
- Migration complexity
- Requires platform expertise

---

### 4. Query-Injection RLS

**Dynamic SQL Example**:
```javascript
// Backend: Inject filter into queries
function buildSecureQuery(user, baseQuery) {
  const tenantFilter = `tenant_id = ${sanitize(user.tenantId)}`;

  // Parse and modify query
  const parsedQuery = sqlParser.parse(baseQuery);

  if (!parsedQuery.where) {
    parsedQuery.where = tenantFilter;
  } else {
    parsedQuery.where = `(${parsedQuery.where}) AND ${tenantFilter}`;
  }

  return sqlParser.stringify(parsedQuery);
}

// Original query
const query = "SELECT * FROM sales WHERE date > '2024-01-01'";

// Injected query
const secureQuery = buildSecureQuery(user, query);
// Result: "SELECT * FROM sales WHERE date > '2024-01-01' AND tenant_id = 123"
```

**Pros**:
- Flexible
- Works with any backend
- Can combine multiple filters
- Full control

**Cons**:
- Complex implementation
- SQL injection risks
- Hard to maintain
- Error-prone

---

### 5. Materialized View Per Tenant

**Materialized View Example**:
```sql
-- Create materialized view per tenant
CREATE MATERIALIZED VIEW sales_tenant_123 AS
SELECT * FROM sales WHERE tenant_id = 123;

-- Refresh on schedule
REFRESH MATERIALIZED VIEW sales_tenant_123;

-- BI tool connects to tenant-specific view
SELECT * FROM sales_tenant_123;
```

**Pros**:
- Excellent performance
- Complete isolation
- Simple queries
- Easy to understand

**Cons**:
- Storage overhead
- Refresh complexity
- View management at scale
- Stale data between refreshes

---

## Multi-Tenant Data Model Patterns

### Pattern 1: Shared Schema with tenant_id Column

```sql
-- Single table for all tenants
CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL,
  amount DECIMAL(10,2),
  date DATE,
  product_id INTEGER,

  -- Index for performance
  INDEX idx_tenant_sales (tenant_id, date)
);

-- RLS policy
CREATE POLICY tenant_isolation ON sales
  USING (tenant_id = current_setting('app.current_tenant')::int);
```

**Best for**: Small to medium SaaS, simple data models

---

### Pattern 2: Separate Schema Per Tenant

```sql
-- Schema per tenant
CREATE SCHEMA tenant_123;
CREATE SCHEMA tenant_456;

-- Identical table structure in each schema
CREATE TABLE tenant_123.sales (
  id SERIAL PRIMARY KEY,
  amount DECIMAL(10,2),
  date DATE,
  product_id INTEGER
);

CREATE TABLE tenant_456.sales (
  id SERIAL PRIMARY KEY,
  amount DECIMAL(10,2),
  date DATE,
  product_id INTEGER
);

-- Set search path based on tenant
SET search_path TO tenant_123;
SELECT * FROM sales; -- Queries tenant_123.sales
```

**Best for**: Large enterprise customers, data isolation requirements

---

### Pattern 3: Separate Database Per Tenant

```javascript
// Connection pool per tenant
class TenantDatabaseManager {
  constructor() {
    this.pools = new Map();
  }

  getConnection(tenantId) {
    if (!this.pools.has(tenantId)) {
      this.pools.set(tenantId, new Pool({
        host: 'postgres.example.com',
        database: `tenant_${tenantId}`,
        user: 'bi_user',
        password: process.env.DB_PASSWORD
      }));
    }

    return this.pools.get(tenantId);
  }
}

// Query tenant-specific database
const pool = dbManager.getConnection(user.tenantId);
const result = await pool.query('SELECT * FROM sales');
```

**Best for**: Highest isolation needs, regulatory requirements

---

## Advanced RLS Patterns

### Hierarchical RLS (Organization Structure)

```sql
-- Users table with hierarchy
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255),
  tenant_id INTEGER,
  department_id INTEGER,
  manager_id INTEGER
);

-- Recursive CTE to get subordinates
WITH RECURSIVE subordinates AS (
  -- Base case: current user
  SELECT id FROM users WHERE id = current_user_id()

  UNION ALL

  -- Recursive case: direct reports
  SELECT u.id
  FROM users u
  INNER JOIN subordinates s ON u.manager_id = s.id
)
SELECT s.*
FROM sales s
INNER JOIN subordinates sub ON s.created_by = sub.id;
```

**Use case**: Managers see team data, executives see department data

---

### Time-Based RLS

```sql
-- Historical data retention per tier
CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  tenant_id INTEGER,
  date DATE,
  amount DECIMAL(10,2)
);

-- RLS based on subscription tier
CREATE POLICY time_based_access ON sales
  USING (
    CASE
      WHEN get_tenant_tier(tenant_id) = 'enterprise' THEN TRUE
      WHEN get_tenant_tier(tenant_id) = 'professional'
        THEN date >= CURRENT_DATE - INTERVAL '1 year'
      WHEN get_tenant_tier(tenant_id) = 'basic'
        THEN date >= CURRENT_DATE - INTERVAL '90 days'
    END
  );
```

**Use case**: Different data retention by pricing tier

---

### Column-Level Security

```sql
-- Mask sensitive columns based on role
CREATE VIEW sales_filtered AS
SELECT
  id,
  tenant_id,
  date,
  product_id,
  CASE
    WHEN has_role('admin') THEN customer_name
    ELSE 'REDACTED'
  END AS customer_name,
  CASE
    WHEN has_role('finance') THEN amount
    ELSE NULL
  END AS amount
FROM sales
WHERE tenant_id = current_tenant_id();
```

**Use case**: Hide PII or financial data from certain users

---

### Geographic RLS

```sql
-- GDPR compliance: data residency
CREATE POLICY geo_isolation ON customer_data
  USING (
    data_region = get_user_region(current_user_id())
    OR has_role('global_admin')
  );

-- Ensure EU data stays in EU
ALTER TABLE customer_data
ADD CONSTRAINT check_data_residency
CHECK (
  (data_region = 'EU' AND server_location = 'EU')
  OR data_region != 'EU'
);
```

**Use case**: Data residency compliance, GDPR

---

## Platform-Specific RLS Implementation

### Tableau RLS

**Method 1: Data Source Filters**
```javascript
// Backend: Tableau Connected App JWT
const jwt = require('jsonwebtoken');

const token = jwt.sign({
  sub: user.email,
  'https://tableau.com/oda': {
    tenant_id: user.tenantId,
    region: user.region,
    role: user.role
  }
}, secret);

// Tableau workbook: Use user attributes in calculated field
// [tenant_id] = ATTR([Tenant ID User Attribute])
```

**Method 2: Initial SQL**
```sql
-- In Tableau data source
CREATE TEMP TABLE user_context AS
SELECT
  '{{tenant_id}}' AS tenant_id,
  '{{user_role}}' AS user_role;

-- Join in custom SQL
SELECT s.*
FROM sales s
INNER JOIN user_context uc ON s.tenant_id = uc.tenant_id;
```

---

### Power BI RLS

**Define Roles in Power BI Desktop**:
```dax
-- Role: Tenant User
[tenant_id] = USERPRINCIPALNAME()

-- Role: Regional Manager
[region] IN PATHCONTAINS("West;East;Central", [region])

-- Role: Dynamic from table
[tenant_id] = LOOKUPVALUE(
  UserTenantMap[tenant_id],
  UserTenantMap[user_email],
  USERPRINCIPALNAME()
)
```

**Backend: Assign Users to Roles**:
```javascript
// Generate embed token with RLS
const embedToken = await powerbi.generateToken({
  reportId: reportId,
  identities: [{
    username: user.email,
    roles: ['Tenant User'],
    datasets: [datasetId]
  }]
});
```

---

### Looker RLS

**User Attributes**:
```javascript
// Set user attributes in SSO URL
const userAttributes = {
  tenant_id: user.tenantId,
  department: user.department,
  region: user.region
};
```

**LookML Access Grants**:
```lookml
access_grant: tenant_access {
  user_attribute: tenant_id
  allowed_values: ["123", "456"]
}

explore: sales {
  required_access_grants: [tenant_access]

  sql_always_where:
    ${tenant_id} = '{{ _user_attributes["tenant_id"] }}' ;;
}
```

---

### Metabase RLS

**Sandboxing (Enterprise)**:
```javascript
// Set user attributes
{
  "tenant_id": 123,
  "region": "west"
}

// Metabase automatically filters:
// WHERE tenant_id = 123 AND region = 'west'
```

**Manual Approach (Open Source)**:
```sql
-- Parameterized native query
SELECT * FROM sales
WHERE tenant_id = {{tenant_id}}
  AND date >= {{start_date}}

-- Pass parameters via embedding URL
https://metabase.example.com/embed/question/123
  ?tenant_id=123&start_date=2024-01-01
```

---

## Testing RLS Implementation

### Unit Tests

```javascript
// Test RLS enforcement
describe('Row-Level Security', () => {
  it('should only return tenant-specific data', async () => {
    const tenant1User = { tenantId: 1 };
    const tenant2User = { tenantId: 2 };

    const data1 = await fetchSalesData(tenant1User);
    const data2 = await fetchSalesData(tenant2User);

    // Verify no overlap
    expect(data1.every(row => row.tenant_id === 1)).toBe(true);
    expect(data2.every(row => row.tenant_id === 2)).toBe(true);

    const ids1 = new Set(data1.map(r => r.id));
    const ids2 = new Set(data2.map(r => r.id));
    const intersection = [...ids1].filter(id => ids2.has(id));

    expect(intersection).toHaveLength(0);
  });

  it('should prevent SQL injection in RLS filter', async () => {
    const maliciousUser = {
      tenantId: "1 OR 1=1" // SQL injection attempt
    };

    await expect(fetchSalesData(maliciousUser)).rejects.toThrow();
  });
});
```

---

### Integration Tests

```javascript
// Test RLS in embedded analytics
describe('Embedded Analytics RLS', () => {
  it('should apply RLS in Tableau embed', async () => {
    const user = { tenantId: 123, email: 'user@example.com' };

    // Generate embed token
    const token = await generateTableauToken(user);

    // Embed dashboard
    const dashboard = await embedTableauDashboard(token);

    // Verify data filtered
    const data = await dashboard.getData();
    expect(data.every(row => row.tenant_id === 123)).toBe(true);
  });
});
```

---

### Penetration Testing

```javascript
// Attempt to bypass RLS
describe('RLS Security Tests', () => {
  it('should not allow tenant_id override in query params', async () => {
    const user = { tenantId: 1 };

    // Try to override tenant_id
    const maliciousUrl = `/embed/dashboard/123?tenant_id=2`;

    const response = await fetch(maliciousUrl, {
      headers: { 'Authorization': `Bearer ${generateToken(user)}` }
    });

    const data = await response.json();

    // Should still only see tenant 1 data
    expect(data.every(row => row.tenant_id === 1)).toBe(true);
  });

  it('should not allow UNION-based data leakage', async () => {
    const user = { tenantId: 1 };

    // Attempt UNION injection
    const maliciousFilter = "' UNION SELECT * FROM sales WHERE tenant_id=2--";

    await expect(
      queryWithFilter(user, maliciousFilter)
    ).rejects.toThrow();
  });
});
```

---

## Performance Optimization

### Indexing for RLS

```sql
-- Composite index for tenant filtering
CREATE INDEX idx_sales_tenant_date
  ON sales(tenant_id, date DESC);

-- Covering index to avoid table lookups
CREATE INDEX idx_sales_tenant_covering
  ON sales(tenant_id)
  INCLUDE (date, amount, product_id);

-- Partial index for active tenants only
CREATE INDEX idx_sales_active_tenants
  ON sales(tenant_id, date)
  WHERE tenant_status = 'active';
```

---

### Query Plan Analysis

```sql
-- Check if RLS filter is using index
EXPLAIN ANALYZE
SELECT * FROM sales
WHERE tenant_id = 123
  AND date >= '2024-01-01';

-- Look for:
-- Index Scan using idx_sales_tenant_date
-- NOT Seq Scan
```

---

### Caching with RLS

```javascript
// Cache per tenant
class TenantAwareCacheManager {
  getCacheKey(tenantId, query) {
    return `tenant:${tenantId}:${hash(query)}`;
  }

  async get(tenantId, query) {
    const key = this.getCacheKey(tenantId, query);
    return await redis.get(key);
  }

  async set(tenantId, query, data, ttl = 300) {
    const key = this.getCacheKey(tenantId, query);
    await redis.setex(key, ttl, JSON.stringify(data));
  }
}

// Use in queries
const cached = await cache.get(user.tenantId, query);
if (cached) return JSON.parse(cached);

const data = await executeQuery(user.tenantId, query);
await cache.set(user.tenantId, query, data);
return data;
```

---

## Common RLS Pitfalls

### Pitfall 1: RLS Not Applied to All Queries

**Problem**: Direct table access bypasses RLS
```sql
-- BAD: Direct access
SELECT * FROM sales; -- No RLS applied

-- GOOD: Use RLS-enabled view
SELECT * FROM sales_filtered;
```

**Solution**: Revoke direct table access, grant only to views

---

### Pitfall 2: Trusting Client-Side Filters

**Problem**: Client can modify filters
```javascript
// BAD: Client controls filter
const tenantId = req.query.tenant_id; // User can change this!
const data = await db.query('SELECT * FROM sales WHERE tenant_id = ?', [tenantId]);
```

**Solution**: Always derive tenant from authenticated user
```javascript
// GOOD: Server controls filter
const tenantId = req.user.tenantId; // From JWT/session
const data = await db.query('SELECT * FROM sales WHERE tenant_id = ?', [tenantId]);
```

---

### Pitfall 3: Performance Degradation

**Problem**: RLS adds overhead to every query

**Solution**: Use indexed columns, materialized views, caching

---

### Pitfall 4: Complex JOIN Scenarios

**Problem**: RLS may not apply to joined tables
```sql
-- BAD: Only filters sales, not customers
SELECT s.*, c.*
FROM sales s
LEFT JOIN customers c ON s.customer_id = c.id
WHERE s.tenant_id = 123; -- customers not filtered!
```

**Solution**: Apply RLS to all tables or use RLS policies
```sql
-- GOOD: Filter both tables
SELECT s.*, c.*
FROM sales s
LEFT JOIN customers c ON s.customer_id = c.id
WHERE s.tenant_id = 123 AND c.tenant_id = 123;
```

---

## RLS Checklist

- [ ] RLS applied at database or BI platform level
- [ ] Tenant ID derived from authenticated user, never from client
- [ ] All tables have appropriate RLS policies or filters
- [ ] Indexes created for RLS filter columns
- [ ] RLS tested with multiple tenants
- [ ] Penetration testing performed
- [ ] Performance impact measured and optimized
- [ ] RLS applies to all query types (SELECT, UPDATE, DELETE)
- [ ] Admin override capability documented and secured
- [ ] RLS rules version controlled
- [ ] Monitoring for RLS policy violations
- [ ] Regular audits of data access patterns
- [ ] Documentation for adding new RLS rules
- [ ] Training for developers on RLS requirements
