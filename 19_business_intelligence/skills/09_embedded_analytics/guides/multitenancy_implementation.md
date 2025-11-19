# Multi-Tenancy Implementation Guide

## Architecture Choice

### Option 1: Shared Database, Shared Schema

**Best for**: 100s-1000s of small tenants

```sql
CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL,
  amount DECIMAL(10,2),
  date DATE,
  INDEX idx_tenant_sales (tenant_id, date DESC)
);

ALTER TABLE sales ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON sales
  USING (tenant_id = current_setting('app.current_tenant')::int);
```

### Option 2: Separate Schema Per Tenant

**Best for**: 10s-100s of tenants

```sql
-- Create schema per tenant
CREATE SCHEMA tenant_123;
CREATE SCHEMA tenant_456;

-- Same table structure in each
CREATE TABLE tenant_123.sales (
  id SERIAL PRIMARY KEY,
  amount DECIMAL(10,2),
  date DATE
);

-- Set search path based on tenant
SET search_path TO tenant_123;
SELECT * FROM sales; -- Queries tenant_123.sales
```

### Option 3: Separate Database Per Tenant

**Best for**: Enterprise customers, 10s of tenants

```javascript
class TenantDatabaseManager {
  getConnection(tenantId) {
    if (!this.pools.has(tenantId)) {
      this.pools.set(tenantId, new Pool({
        database: `tenant_${tenantId}`,
        // ...
      }));
    }
    return this.pools.get(tenantId);
  }
}
```

## Tenant Provisioning

```javascript
class TenantProvisioner {
  async provisionTenant(tenant) {
    // 1. Create database resources
    await this.createDatabase(tenant);
    
    // 2. Create BI workspace/site
    await this.createBIWorkspace(tenant);
    
    // 3. Configure RLS
    await this.setupRLS(tenant);
    
    // 4. Create admin user
    await this.createAdminUser(tenant);
    
    // 5. Deploy starter dashboards
    await this.deployDashboards(tenant);
  }
  
  async createDatabase(tenant) {
    if (DB_MODEL === 'shared-schema') {
      await db.query(
        'INSERT INTO tenants (id, name) VALUES ($1, $2)',
        [tenant.id, tenant.name]
      );
    } else if (DB_MODEL === 'separate-schema') {
      await db.query(`CREATE SCHEMA tenant_${tenant.id}`);
      await this.runMigrations(`tenant_${tenant.id}`);
    }
  }
  
  async createBIWorkspace(tenant) {
    // Tableau
    const site = await tableau.createSite({
      name: `tenant_${tenant.id}`,
      contentUrl: `tenant-${tenant.id}`
    });
    
    // Or Power BI
    const workspace = await powerbi.createWorkspace({
      name: `Tenant ${tenant.id}`
    });
    
    return site || workspace;
  }
}
```

## Tenant Routing

```javascript
app.use((req, res, next) => {
  // Extract tenant from subdomain
  const subdomain = req.hostname.split('.')[0];
  const tenant = await db.tenants.findOne({ subdomain });
  
  if (!tenant) {
    return res.status(404).send('Tenant not found');
  }
  
  req.tenant = tenant;
  next();
});

app.get('/api/analytics', async (req, res) => {
  const data = await getAnalyticsData(req.tenant.id, req.user);
  res.json(data);
});
```

## Testing Multi-Tenancy

```javascript
describe('Multi-Tenancy Isolation', () => {
  it('tenant 1 cannot access tenant 2 data', async () => {
    const tenant1Data = await getData({ tenantId: 1 });
    const tenant2Data = await getData({ tenantId: 2 });
    
    // No overlap
    const ids1 = new Set(tenant1Data.map(r => r.id));
    const ids2 = new Set(tenant2Data.map(r => r.id));
    
    expect([...ids1].filter(id => ids2.has(id))).toHaveLength(0);
  });
});
```
