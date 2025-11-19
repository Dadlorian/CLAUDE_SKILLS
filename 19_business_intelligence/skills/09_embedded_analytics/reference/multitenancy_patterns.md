# Multi-Tenancy Patterns for Embedded Analytics

## Overview

Multi-tenancy architecture patterns for serving embedded analytics to multiple customers/organizations while ensuring data isolation, performance, and scalability.

## Multi-Tenancy Models

### 1. Shared Database, Shared Schema (Most Common)

**Architecture**:
```
Single Database
  └── Single Schema
      └── Tables with tenant_id column
          ├── sales (tenant_id, ...)
          ├── customers (tenant_id, ...)
          └── products (tenant_id, ...)
```

**Implementation**:
```sql
-- All tenants share same tables
CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL,
  amount DECIMAL(10,2),
  date DATE,
  customer_id INTEGER,

  -- Indexes for performance
  INDEX idx_tenant_sales (tenant_id, date DESC),
  INDEX idx_tenant_customer (tenant_id, customer_id),

  -- Foreign key with tenant check
  FOREIGN KEY (tenant_id, customer_id)
    REFERENCES customers(tenant_id, id)
);

-- Row-level security
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON sales
  USING (tenant_id = current_setting('app.current_tenant')::int);
```

**Pros**:
- Simple to implement
- Easy to scale horizontally
- Shared resources = cost efficient
- Simple schema migrations
- Cross-tenant analytics possible

**Cons**:
- Data leakage risk if RLS fails
- "Noisy neighbor" performance issues
- Difficult to customize per tenant
- Compliance challenges for some industries
- Backup/restore affects all tenants

**Best for**: B2B SaaS with 100s-1000s of tenants, similar data models

---

### 2. Shared Database, Separate Schemas

**Architecture**:
```
Single Database
  ├── Schema: tenant_001
  │   ├── sales
  │   └── customers
  ├── Schema: tenant_002
  │   ├── sales
  │   └── customers
  └── Schema: tenant_003
      ├── sales
      └── customers
```

**Implementation**:
```sql
-- Create schema per tenant
CREATE SCHEMA tenant_001;
CREATE SCHEMA tenant_002;

-- Identical table structure in each
CREATE TABLE tenant_001.sales (
  id SERIAL PRIMARY KEY,
  amount DECIMAL(10,2),
  date DATE,
  customer_id INTEGER
);

CREATE TABLE tenant_002.sales (
  id SERIAL PRIMARY KEY,
  amount DECIMAL(10,2),
  date DATE,
  customer_id INTEGER
);

-- Set search path based on tenant
SET search_path TO tenant_001;
SELECT * FROM sales; -- Queries tenant_001.sales
```

**Node.js Implementation**:
```javascript
class TenantSchemaManager {
  async getConnection(tenantId) {
    const pool = this.connectionPool;
    const client = await pool.connect();

    // Set schema for this connection
    await client.query(`SET search_path TO tenant_${tenantId}`);

    return client;
  }

  async executeQuery(tenantId, query, params) {
    const client = await this.getConnection(tenantId);

    try {
      const result = await client.query(query, params);
      return result.rows;
    } finally {
      client.release();
    }
  }
}

// Usage
const data = await schemaManager.executeQuery(
  user.tenantId,
  'SELECT * FROM sales WHERE date >= $1',
  [startDate]
);
```

**Pros**:
- Better isolation than shared schema
- Schema-level customization possible
- Easier to backup/restore single tenant
- Simpler queries (no tenant_id everywhere)
- Better performance isolation

**Cons**:
- More complex migrations (N schemas)
- Database connection overhead
- Limited by database schema count
- Harder to implement cross-tenant features
- Provisioning complexity

**Best for**: 10s-100s of tenants, need customization, medium security requirements

---

### 3. Separate Database Per Tenant

**Architecture**:
```
Database Server
  ├── tenant_001_db
  │   ├── sales
  │   └── customers
  ├── tenant_002_db
  │   ├── sales
  │   └── customers
  └── tenant_003_db
      ├── sales
      └── customers
```

**Implementation**:
```javascript
class TenantDatabaseManager {
  constructor() {
    this.pools = new Map();
  }

  getPool(tenantId) {
    if (!this.pools.has(tenantId)) {
      this.pools.set(tenantId, new Pool({
        host: this.getDBHost(tenantId),
        database: `tenant_${tenantId}`,
        user: 'app_user',
        password: process.env.DB_PASSWORD,
        max: 10 // Connection pool size
      }));
    }

    return this.pools.get(tenantId);
  }

  async executeQuery(tenantId, query, params) {
    const pool = this.getPool(tenantId);
    const result = await pool.query(query, params);
    return result.rows;
  }

  // Distribute databases across servers for scale
  getDBHost(tenantId) {
    const shard = tenantId % this.dbShards.length;
    return this.dbShards[shard].host;
  }
}

// BI platform configuration
async function configureBIPlatform(tenant) {
  // Create dedicated data source per tenant
  await tableau.createDataSource({
    name: `Tenant ${tenant.id} Data`,
    connectionType: 'postgres',
    server: dbManager.getDBHost(tenant.id),
    database: `tenant_${tenant.id}`,
    username: 'bi_reader',
    password: process.env.BI_PASSWORD
  });
}
```

**Pros**:
- Maximum isolation and security
- Independent backups and restores
- Can use different database versions
- Easy to move tenant to different server
- Meet strict compliance requirements
- Dedicated resources per tenant

**Cons**:
- Highest infrastructure cost
- Complex provisioning and management
- Schema migrations across N databases
- Connection pool overhead
- Difficult to do cross-tenant analytics
- Monitoring and maintenance complexity

**Best for**: Enterprise customers, strict compliance, high-value tenants, 10s of tenants

---

## Tenant Provisioning Automation

### Automated Tenant Onboarding

```javascript
class TenantProvisioningService {
  async provisionNewTenant(tenant) {
    console.log(`Provisioning tenant: ${tenant.name}`);

    try {
      // 1. Create database resources
      await this.createDatabaseResources(tenant);

      // 2. Create BI platform resources
      await this.createBIResources(tenant);

      // 3. Configure security
      await this.configureSecurity(tenant);

      // 4. Load sample data (optional)
      if (tenant.wantsSampleData) {
        await this.loadSampleData(tenant);
      }

      // 5. Send welcome email
      await this.sendWelcomeEmail(tenant);

      console.log(`Tenant ${tenant.id} provisioned successfully`);
      return { success: true, tenantId: tenant.id };

    } catch (error) {
      console.error(`Provisioning failed: ${error}`);
      await this.rollbackProvisioning(tenant);
      throw error;
    }
  }

  async createDatabaseResources(tenant) {
    const dbConfig = this.getTenantDBConfig(tenant);

    if (dbConfig.model === 'shared-schema') {
      // Just add tenant record
      await db.query(
        'INSERT INTO tenants (id, name, created_at) VALUES ($1, $2, NOW())',
        [tenant.id, tenant.name]
      );

    } else if (dbConfig.model === 'separate-schema') {
      // Create dedicated schema
      await db.query(`CREATE SCHEMA tenant_${tenant.id}`);

      // Create tables from template
      const tables = await this.getTableTemplates();
      for (const table of tables) {
        await db.query(`
          CREATE TABLE tenant_${tenant.id}.${table.name} (
            ${table.columns.join(',\n')}
          )
        `);
      }

      // Create indexes
      for (const index of table.indexes) {
        await db.query(`
          CREATE INDEX ${index.name}
            ON tenant_${tenant.id}.${table.name} (${index.columns.join(',')})
        `);
      }

    } else if (dbConfig.model === 'separate-database') {
      // Create dedicated database
      await db.query(`CREATE DATABASE tenant_${tenant.id}`);

      // Run migrations
      await this.runMigrations(`tenant_${tenant.id}`);
    }
  }

  async createBIResources(tenant) {
    // Create Tableau site/project
    if (this.biPlatform === 'tableau') {
      const site = await tableau.createSite({
        name: `tenant_${tenant.id}`,
        contentUrl: `tenant-${tenant.id}`,
        adminMode: 'ContentAndUsers',
        storageQuota: tenant.storageQuotaGB
      });

      // Create data source
      await tableau.createDataSource({
        siteId: site.id,
        name: `${tenant.name} Data`,
        connectionConfig: this.getTenantDBConnection(tenant)
      });

      // Publish starter dashboards
      await this.publishStarterDashboards(tenant, site.id);
    }

    // Create Power BI workspace
    if (this.biPlatform === 'powerbi') {
      const workspace = await powerbi.createWorkspace({
        name: `Tenant ${tenant.id}`,
        capacity: this.getPowerBICapacity(tenant.tier)
      });

      // Create dataset
      await powerbi.createDataset({
        workspaceId: workspace.id,
        name: `${tenant.name} Data`,
        connection: this.getTenantDBConnection(tenant)
      });

      // Deploy reports
      await this.deployPowerBIReports(tenant, workspace.id);
    }

    // Create Looker project
    if (this.biPlatform === 'looker') {
      const project = await looker.createProject({
        name: `tenant_${tenant.id}`,
        gitRemoteUrl: this.getGitRepo(tenant)
      });

      // Create connection
      await looker.createConnection({
        name: `tenant_${tenant.id}_db`,
        database: this.getTenantDatabase(tenant),
        username: 'looker_user',
        password: process.env.LOOKER_DB_PASSWORD
      });

      // Deploy LookML
      await this.deployLookML(tenant, project.id);
    }
  }

  async configureSecurity(tenant) {
    // Create RLS rules
    await this.createRLSRules(tenant);

    // Create initial users
    for (const user of tenant.initialUsers) {
      await this.createUser({
        tenantId: tenant.id,
        email: user.email,
        role: user.role
      });
    }

    // Set up SSO
    if (tenant.ssoConfig) {
      await this.configureSSOForTenant(tenant);
    }
  }

  async rollbackProvisioning(tenant) {
    console.log(`Rolling back tenant ${tenant.id}`);

    try {
      // Delete BI resources
      await this.deleteBIResources(tenant);

      // Delete database resources
      await this.deleteDatabaseResources(tenant);

      // Clean up any created files
      await this.cleanupFiles(tenant);

    } catch (error) {
      console.error(`Rollback failed: ${error}`);
      // Alert ops team for manual cleanup
      await this.alertOps({
        type: 'provisioning_rollback_failed',
        tenantId: tenant.id,
        error: error.message
      });
    }
  }
}

// Usage
const provisioner = new TenantProvisioningService();

app.post('/api/tenants', async (req, res) => {
  const tenant = {
    id: generateTenantId(),
    name: req.body.name,
    tier: req.body.tier,
    wantsSampleData: req.body.includeSamples,
    initialUsers: req.body.users
  };

  try {
    const result = await provisioner.provisionNewTenant(tenant);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

---

## Tenant-Aware BI Embedding

### Dynamic Tenant Routing

```javascript
class TenantAwareEmbedManager {
  async getEmbedConfig(user) {
    const tenant = await this.getTenant(user.tenantId);

    // Route to correct BI instance/site based on tenant
    const embedConfig = {
      tableau: () => this.getTableauConfig(tenant, user),
      powerbi: () => this.getPowerBIConfig(tenant, user),
      looker: () => this.getLookerConfig(tenant, user)
    }[tenant.biPlatform]();

    return embedConfig;
  }

  async getTableauConfig(tenant, user) {
    // Generate token for tenant's specific site
    const token = await tableau.generateConnectedAppToken({
      username: user.email,
      siteId: tenant.tableauSiteId,
      scope: ['tableau:views:embed'],
      customClaims: {
        tenant_id: tenant.id,
        tenant_tier: tenant.tier
      }
    });

    return {
      platform: 'tableau',
      embedUrl: `https://tableau.example.com/t/${tenant.tableauSiteUrl}/views/Dashboard`,
      token: token,
      options: {
        hideTabs: !tenant.features.includes('tabs'),
        hideToolbar: !tenant.features.includes('toolbar'),
        device: 'desktop'
      }
    };
  }

  async getPowerBIConfig(tenant, user) {
    // Generate embed token for tenant's workspace
    const embedToken = await powerbi.generateEmbedToken({
      workspaceId: tenant.powerBIWorkspaceId,
      reportId: tenant.powerBIReportId,
      identities: [{
        username: user.email,
        roles: [user.role],
        datasets: [tenant.powerBIDatasetId]
      }]
    });

    return {
      platform: 'powerbi',
      embedUrl: `https://app.powerbi.com/reportEmbed?` +
                `reportId=${tenant.powerBIReportId}&` +
                `groupId=${tenant.powerBIWorkspaceId}`,
      token: embedToken,
      settings: {
        filterPaneEnabled: tenant.features.includes('filters'),
        navContentPaneEnabled: tenant.features.includes('navigation')
      }
    };
  }

  async getLookerConfig(tenant, user) {
    // Generate SSO URL for tenant's Looker instance
    const ssoUrl = looker.generateSSOUrl({
      userId: user.id,
      email: user.email,
      permissions: this.getLookerPermissions(user.role),
      models: [tenant.lookerId],
      userAttributes: {
        tenant_id: tenant.id,
        department: user.department
      },
      embedDomain: tenant.customDomain || 'app.example.com'
    });

    return {
      platform: 'looker',
      embedUrl: ssoUrl,
      dashboardId: tenant.lookerDashboardId
    };
  }
}
```

---

## Performance Isolation Strategies

### Resource Quotas Per Tenant

```javascript
class TenantResourceManager {
  constructor() {
    this.quotas = new Map();
    this.usage = new Map();
  }

  async checkQuota(tenantId, resource) {
    const quota = await this.getQuota(tenantId, resource);
    const current = await this.getUsage(tenantId, resource);

    if (current >= quota) {
      throw new Error(`Quota exceeded for ${resource}`);
    }

    return { allowed: true, remaining: quota - current };
  }

  async getQuota(tenantId, resource) {
    const tenant = await db.tenants.findOne({ id: tenantId });

    const quotas = {
      basic: {
        queries_per_hour: 1000,
        storage_gb: 10,
        concurrent_users: 5,
        dashboards: 10
      },
      professional: {
        queries_per_hour: 10000,
        storage_gb: 100,
        concurrent_users: 50,
        dashboards: 100
      },
      enterprise: {
        queries_per_hour: 100000,
        storage_gb: 1000,
        concurrent_users: 500,
        dashboards: 1000
      }
    };

    return quotas[tenant.tier][resource];
  }

  async trackUsage(tenantId, resource, amount = 1) {
    const key = `usage:${tenantId}:${resource}:${this.getCurrentHour()}`;

    await redis.incrby(key, amount);
    await redis.expire(key, 3600); // 1 hour TTL
  }

  async enforceQueryLimit(tenantId) {
    const allowed = await this.checkQuota(tenantId, 'queries_per_hour');

    if (!allowed) {
      throw new Error('Query quota exceeded. Please upgrade your plan.');
    }

    await this.trackUsage(tenantId, 'queries_per_hour');
  }
}

// Middleware to enforce quotas
app.use('/api/analytics/*', async (req, res, next) => {
  const tenantId = req.user.tenantId;

  try {
    await resourceManager.enforceQueryLimit(tenantId);
    next();
  } catch (error) {
    res.status(429).json({
      error: error.message,
      quotaReset: resourceManager.getNextResetTime()
    });
  }
});
```

### Query Timeout Per Tenant

```javascript
// Database query timeout based on tier
class TenantQueryExecutor {
  async executeQuery(tenantId, query) {
    const tenant = await this.getTenant(tenantId);

    const timeouts = {
      basic: 30000,       // 30 seconds
      professional: 120000, // 2 minutes
      enterprise: 600000   // 10 minutes
    };

    const timeout = timeouts[tenant.tier];

    return Promise.race([
      this.runQuery(tenantId, query),
      this.timeoutPromise(timeout)
    ]);
  }

  timeoutPromise(ms) {
    return new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Query timeout after ${ms}ms`));
      }, ms);
    });
  }
}
```

---

## Tenant Data Migration

### Moving Tenant Between Isolation Models

```javascript
class TenantMigrationService {
  async migrateToSeparateSchema(tenantId) {
    console.log(`Migrating tenant ${tenantId} to separate schema`);

    const transaction = await db.transaction();

    try {
      // 1. Create new schema
      await transaction.query(`CREATE SCHEMA tenant_${tenantId}`);

      // 2. Create tables in new schema
      await this.createSchemaStructure(transaction, tenantId);

      // 3. Copy data
      const tables = ['sales', 'customers', 'products', 'orders'];

      for (const table of tables) {
        console.log(`Copying ${table}...`);

        await transaction.query(`
          INSERT INTO tenant_${tenantId}.${table}
          SELECT * FROM ${table}
          WHERE tenant_id = $1
        `, [tenantId]);

        console.log(`Copied ${table}`);
      }

      // 4. Update BI platform connections
      await this.updateBIConnection(tenantId, {
        schema: `tenant_${tenantId}`
      });

      // 5. Verify data integrity
      await this.verifyMigration(tenantId);

      // 6. Delete old data (after verification period)
      // await this.scheduleOldDataDeletion(tenantId);

      await transaction.commit();
      console.log(`Migration complete for tenant ${tenantId}`);

    } catch (error) {
      await transaction.rollback();
      console.error(`Migration failed: ${error}`);
      throw error;
    }
  }

  async verifyMigration(tenantId) {
    const tables = ['sales', 'customers', 'products'];

    for (const table of tables) {
      // Count in old location
      const oldCount = await db.query(
        `SELECT COUNT(*) FROM ${table} WHERE tenant_id = $1`,
        [tenantId]
      );

      // Count in new location
      const newCount = await db.query(
        `SELECT COUNT(*) FROM tenant_${tenantId}.${table}`
      );

      if (oldCount.rows[0].count !== newCount.rows[0].count) {
        throw new Error(`Data mismatch in ${table}`);
      }
    }
  }
}
```

---

## Monitoring and Observability

### Per-Tenant Metrics

```javascript
class TenantMetricsCollector {
  async collectMetrics(tenantId) {
    return {
      // Usage metrics
      queries: await this.getQueryCount(tenantId),
      users: await this.getActiveUserCount(tenantId),
      dashboards: await this.getDashboardCount(tenantId),
      dataVolume: await this.getDataVolume(tenantId),

      // Performance metrics
      avgQueryTime: await this.getAvgQueryTime(tenantId),
      p95QueryTime: await this.getP95QueryTime(tenantId),
      errorRate: await this.getErrorRate(tenantId),
      uptime: await this.getUptime(tenantId),

      // Resource metrics
      storageUsed: await this.getStorageUsed(tenantId),
      cpuUsage: await this.getCPUUsage(tenantId),
      memoryUsage: await this.getMemoryUsage(tenantId),

      // Business metrics
      dailyActiveUsers: await this.getDAU(tenantId),
      monthlyActiveUsers: await this.getMAU(tenantId),
      featureUsage: await this.getFeatureUsage(tenantId)
    };
  }

  async getQueryCount(tenantId) {
    return await redis.get(`metrics:${tenantId}:queries:24h`);
  }

  async logSlowQuery(tenantId, query, duration) {
    if (duration > 10000) { // > 10 seconds
      await db.slowQueries.insert({
        tenant_id: tenantId,
        query: query,
        duration: duration,
        timestamp: new Date()
      });

      // Alert if chronic issue
      const recentSlowQueries = await this.getRecentSlowQueries(tenantId);
      if (recentSlowQueries.length > 10) {
        await this.alertSlowQueries(tenantId);
      }
    }
  }
}
```

---

## Cost Allocation

### Per-Tenant Cost Tracking

```javascript
class TenantCostTracker {
  async calculateMonthlyCost(tenantId, month) {
    const costs = {
      // Infrastructure
      database: await this.getDatabaseCost(tenantId, month),
      compute: await this.getComputeCost(tenantId, month),
      storage: await this.getStorageCost(tenantId, month),

      // BI Platform
      biLicenses: await this.getBILicenseCost(tenantId, month),
      biCompute: await this.getBIComputeCost(tenantId, month),

      // Networking
      bandwidth: await this.getBandwidthCost(tenantId, month),
      cdn: await this.getCDNCost(tenantId, month)
    };

    const total = Object.values(costs).reduce((sum, cost) => sum + cost, 0);

    return {
      tenantId,
      month,
      breakdown: costs,
      total,
      perUser: total / await this.getUserCount(tenantId)
    };
  }

  async getStorageCost(tenantId, month) {
    const storageGB = await this.getTenantStorageUsage(tenantId, month);
    const ratePerGB = 0.10; // $0.10 per GB per month
    return storageGB * ratePerGB;
  }

  async getBIComputeCost(tenantId, month) {
    const queryCount = await this.getQueryCount(tenantId, month);
    const avgDuration = await this.getAvgQueryDuration(tenantId, month);

    // Cost based on compute time
    const computeHours = (queryCount * avgDuration) / 3600000;
    const ratePerHour = 0.50; // $0.50 per compute hour

    return computeHours * ratePerHour;
  }
}
```

---

## Multi-Tenant Backup and Recovery

```javascript
class TenantBackupService {
  async backupTenant(tenantId) {
    const backupId = generateBackupId();

    console.log(`Starting backup for tenant ${tenantId}`);

    try {
      // Backup database
      await this.backupDatabase(tenantId, backupId);

      // Backup BI artifacts
      await this.backupBIArtifacts(tenantId, backupId);

      // Backup configurations
      await this.backupConfigurations(tenantId, backupId);

      // Store backup metadata
      await this.storeBackupMetadata({
        tenantId,
        backupId,
        timestamp: new Date(),
        size: await this.getBackupSize(backupId),
        status: 'completed'
      });

      console.log(`Backup completed: ${backupId}`);
      return backupId;

    } catch (error) {
      console.error(`Backup failed: ${error}`);
      await this.markBackupFailed(backupId, error);
      throw error;
    }
  }

  async restoreTenant(tenantId, backupId) {
    console.log(`Restoring tenant ${tenantId} from backup ${backupId}`);

    // Restore database
    await this.restoreDatabase(tenantId, backupId);

    // Restore BI artifacts
    await this.restoreBIArtifacts(tenantId, backupId);

    // Restore configurations
    await this.restoreConfigurations(tenantId, backupId);

    // Verify restoration
    await this.verifyRestore(tenantId, backupId);

    console.log(`Restore completed for tenant ${tenantId}`);
  }
}
```

---

## Multi-Tenancy Best Practices

### Security
- ✅ Always validate tenant context from authenticated user
- ✅ Never trust client-provided tenant ID
- ✅ Implement RLS at multiple layers (app + database)
- ✅ Regular security audits for data leakage
- ✅ Separate encryption keys per tenant (if required)

### Performance
- ✅ Index tenant_id columns with compound indexes
- ✅ Implement per-tenant caching
- ✅ Set query timeouts based on tenant tier
- ✅ Monitor for "noisy neighbors"
- ✅ Consider tenant-specific read replicas

### Operations
- ✅ Automate tenant provisioning/deprovisioning
- ✅ Version control all tenant configurations
- ✅ Regular backups with point-in-time recovery
- ✅ Tenant-aware monitoring and alerting
- ✅ Cost allocation and tracking per tenant

### Scalability
- ✅ Plan migration path between isolation models
- ✅ Design for horizontal scaling from day one
- ✅ Consider multi-region deployment for global tenants
- ✅ Implement tenant sharding for large-scale
- ✅ Regular capacity planning reviews

### Compliance
- ✅ Document data residency per tenant
- ✅ Support tenant data export (GDPR)
- ✅ Implement tenant data deletion
- ✅ Audit logs for all tenant access
- ✅ Compliance certifications per tenant if needed
