# API Integration Patterns for Embedded Analytics

## Overview

Comprehensive patterns for integrating BI platform APIs into SaaS applications for programmatic dashboard management, user provisioning, and data operations.

## Common API Operations

### 1. Dashboard/Report Management

#### Create Dashboard Programmatically

```javascript
// Tableau: Create workbook via REST API
class TableauDashboardManager {
  async createDashboard(tenantId, dashboardConfig) {
    const { name, dataSourceId, layout } = dashboardConfig;

    // 1. Sign in and get token
    const authToken = await this.signIn();

    // 2. Create workbook
    const response = await axios.post(
      `https://tableau.example.com/api/3.19/sites/${this.siteId}/workbooks`,
      {
        workbook: {
          name: `${tenantId}_${name}`,
          projectId: this.getProjectForTenant(tenantId),
          showTabs: false
        }
      },
      {
        headers: {
          'X-Tableau-Auth': authToken,
          'Content-Type': 'application/json'
        }
      }
    );

    const workbookId = response.data.workbook.id;

    // 3. Add views/sheets
    for (const view of layout.views) {
      await this.addViewToWorkbook(workbookId, view);
    }

    return workbookId;
  }

  async addViewToWorkbook(workbookId, viewConfig) {
    // Add view using Tableau's Document API or REST API
    await axios.post(
      `https://tableau.example.com/api/3.19/sites/${this.siteId}/workbooks/${workbookId}/views`,
      viewConfig,
      {
        headers: { 'X-Tableau-Auth': this.authToken }
      }
    );
  }
}

// Power BI: Create report via REST API
class PowerBIDashboardManager {
  async createReport(tenantId, reportConfig) {
    const { name, datasetId, pages } = reportConfig;

    // Get access token
    const accessToken = await this.getAccessToken();

    // Create report
    const response = await axios.post(
      `https://api.powerbi.com/v1.0/myorg/groups/${this.getWorkspaceId(tenantId)}/reports`,
      {
        name: `${tenantId}_${name}`,
        datasetId: datasetId
      },
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const reportId = response.data.id;

    // Update report layout
    await this.updateReportLayout(reportId, pages);

    return reportId;
  }

  async updateReportLayout(reportId, pages) {
    const accessToken = await this.getAccessToken();

    await axios.put(
      `https://api.powerbi.com/v1.0/myorg/reports/${reportId}/pages`,
      { pages },
      {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      }
    );
  }
}
```

#### Clone Dashboard for New Tenant

```javascript
class DashboardCloner {
  async cloneDashboardForTenant(sourceDashboardId, targetTenantId) {
    // 1. Get source dashboard metadata
    const sourceMetadata = await this.getDashboardMetadata(sourceDashboardId);

    // 2. Create data source for new tenant
    const dataSource = await this.createTenantDataSource(targetTenantId);

    // 3. Clone dashboard structure
    const newDashboard = await this.createDashboard(targetTenantId, {
      name: sourceMetadata.name,
      description: sourceMetadata.description,
      dataSourceId: dataSource.id,
      layout: sourceMetadata.layout
    });

    // 4. Update RLS for new tenant
    await this.applyRLS(newDashboard.id, targetTenantId);

    // 5. Set permissions
    await this.setDashboardPermissions(newDashboard.id, targetTenantId);

    return newDashboard;
  }

  async getDashboardMetadata(dashboardId) {
    const response = await axios.get(
      `https://api.bi-platform.com/dashboards/${dashboardId}/metadata`,
      {
        headers: { 'Authorization': `Bearer ${this.apiToken}` }
      }
    );

    return response.data;
  }

  async applyRLS(dashboardId, tenantId) {
    await axios.post(
      `https://api.bi-platform.com/dashboards/${dashboardId}/rls`,
      {
        rules: [
          {
            field: 'tenant_id',
            operator: 'equals',
            value: tenantId
          }
        ]
      },
      {
        headers: { 'Authorization': `Bearer ${this.apiToken}` }
      }
    );
  }
}
```

---

### 2. User and Permission Management

#### Create Users Programmatically

```javascript
class BIUserManager {
  async createUser(user, tenantId) {
    const biUser = {
      email: user.email,
      name: `${user.firstName} ${user.lastName}`,
      role: this.mapRoleToBIRole(user.role),
      tenantId: tenantId
    };

    // Tableau: Add user to site
    if (this.platform === 'tableau') {
      return await this.createTableauUser(biUser);
    }

    // Power BI: Add user to workspace
    if (this.platform === 'powerbi') {
      return await this.createPowerBIUser(biUser);
    }
  }

  async createTableauUser(user) {
    const response = await axios.post(
      `https://tableau.example.com/api/3.19/sites/${this.siteId}/users`,
      {
        user: {
          name: user.email,
          siteRole: user.role, // Viewer, Explorer, Creator
          authSetting: 'ServerDefault'
        }
      },
      {
        headers: { 'X-Tableau-Auth': this.authToken }
      }
    );

    return response.data.user;
  }

  async createPowerBIUser(user) {
    const response = await axios.post(
      `https://api.powerbi.com/v1.0/myorg/groups/${this.workspaceId}/users`,
      {
        emailAddress: user.email,
        groupUserAccessRight: user.role, // Member, Admin, Contributor, Viewer
        principalType: 'User'
      },
      {
        headers: { 'Authorization': `Bearer ${this.accessToken}` }
      }
    );

    return response.data;
  }

  mapRoleToBIRole(appRole) {
    const roleMap = {
      admin: { tableau: 'SiteAdministratorExplorer', powerbi: 'Admin' },
      analyst: { tableau: 'Explorer', powerbi: 'Contributor' },
      viewer: { tableau: 'Viewer', powerbi: 'Viewer' }
    };

    return roleMap[appRole][this.platform];
  }

  // Sync user when updated in app
  async syncUser(userId) {
    const appUser = await db.users.findOne({ id: userId });
    const biUser = await this.getBIUser(appUser.email);

    // Update if exists, create if not
    if (biUser) {
      await this.updateBIUser(biUser.id, {
        role: this.mapRoleToBIRole(appUser.role),
        name: `${appUser.firstName} ${appUser.lastName}`
      });
    } else {
      await this.createUser(appUser, appUser.tenantId);
    }
  }

  // Delete user from BI platform
  async deleteUser(email) {
    const biUser = await this.getBIUser(email);

    if (!biUser) return;

    if (this.platform === 'tableau') {
      await axios.delete(
        `https://tableau.example.com/api/3.19/sites/${this.siteId}/users/${biUser.id}`,
        {
          headers: { 'X-Tableau-Auth': this.authToken }
        }
      );
    }

    if (this.platform === 'powerbi') {
      await axios.delete(
        `https://api.powerbi.com/v1.0/myorg/groups/${this.workspaceId}/users/${email}`,
        {
          headers: { 'Authorization': `Bearer ${this.accessToken}` }
        }
      );
    }
  }
}
```

#### Permission Management

```javascript
class PermissionManager {
  async setDashboardPermissions(dashboardId, userEmail, permissions) {
    // Tableau: Set content permissions
    if (this.platform === 'tableau') {
      await axios.put(
        `https://tableau.example.com/api/3.19/sites/${this.siteId}/workbooks/${dashboardId}/permissions`,
        {
          permissions: {
            granteeCapabilities: [{
              user: { id: await this.getUserId(userEmail) },
              capabilities: {
                capability: permissions.map(p => ({
                  name: p,
                  mode: 'Allow'
                }))
              }
            }]
          }
        },
        {
          headers: { 'X-Tableau-Auth': this.authToken }
        }
      );
    }

    // Power BI: Add user to report
    if (this.platform === 'powerbi') {
      await axios.post(
        `https://api.powerbi.com/v1.0/myorg/reports/${dashboardId}/users`,
        {
          emailAddress: userEmail,
          reportUserAccessRight: permissions.includes('edit') ? 'Edit' : 'Read',
          principalType: 'User'
        },
        {
          headers: { 'Authorization': `Bearer ${this.accessToken}` }
        }
      );
    }
  }

  // Bulk permission updates
  async syncPermissions(tenantId) {
    const users = await db.users.find({ tenantId });
    const dashboards = await db.dashboards.find({ tenantId });

    for (const dashboard of dashboards) {
      for (const user of users) {
        const permissions = this.calculatePermissions(user.role, dashboard);
        await this.setDashboardPermissions(dashboard.biId, user.email, permissions);
      }
    }
  }

  calculatePermissions(userRole, dashboard) {
    const permissionMatrix = {
      admin: ['read', 'write', 'delete', 'share'],
      analyst: ['read', 'write', 'share'],
      viewer: ['read']
    };

    return permissionMatrix[userRole] || ['read'];
  }
}
```

---

### 3. Data Operations

#### Trigger Data Refresh

```javascript
class DataRefreshManager {
  async refreshDataSource(dataSourceId) {
    // Tableau: Refresh extract
    if (this.platform === 'tableau') {
      await axios.post(
        `https://tableau.example.com/api/3.19/sites/${this.siteId}/datasources/${dataSourceId}/refresh`,
        {},
        {
          headers: { 'X-Tableau-Auth': this.authToken }
        }
      );
    }

    // Power BI: Refresh dataset
    if (this.platform === 'powerbi') {
      await axios.post(
        `https://api.powerbi.com/v1.0/myorg/datasets/${dataSourceId}/refreshes`,
        {
          notifyOption: 'MailOnFailure'
        },
        {
          headers: { 'Authorization': `Bearer ${this.accessToken}` }
        }
      );
    }
  }

  async getRefreshStatus(dataSourceId, refreshId) {
    if (this.platform === 'powerbi') {
      const response = await axios.get(
        `https://api.powerbi.com/v1.0/myorg/datasets/${dataSourceId}/refreshes/${refreshId}`,
        {
          headers: { 'Authorization': `Bearer ${this.accessToken}` }
        }
      );

      return {
        status: response.data.status,
        startTime: response.data.startTime,
        endTime: response.data.endTime,
        error: response.data.serviceExceptionJson
      };
    }
  }

  async scheduleRefresh(dataSourceId, schedule) {
    if (this.platform === 'powerbi') {
      await axios.patch(
        `https://api.powerbi.com/v1.0/myorg/datasets/${dataSourceId}/refreshSchedule`,
        {
          enabled: true,
          days: schedule.days,
          times: schedule.times,
          localTimeZoneId: schedule.timezone
        },
        {
          headers: { 'Authorization': `Bearer ${this.accessToken}` }
        }
      );
    }
  }
}
```

#### Query Data via API

```javascript
class DataQueryManager {
  async queryData(query, params) {
    // Looker: Run inline query
    if (this.platform === 'looker') {
      return await this.runLookerQuery(query);
    }

    // Metabase: Run native query
    if (this.platform === 'metabase') {
      return await this.runMetabaseQuery(query, params);
    }
  }

  async runLookerQuery(query) {
    const response = await axios.post(
      'https://looker.example.com/api/4.0/queries',
      {
        model: query.model,
        view: query.view,
        fields: query.fields,
        filters: query.filters,
        limit: query.limit || 500
      },
      {
        headers: { 'Authorization': `Bearer ${this.apiToken}` }
      }
    );

    const queryId = response.data.id;

    // Run query
    const resultResponse = await axios.get(
      `https://looker.example.com/api/4.0/queries/${queryId}/run/json`,
      {
        headers: { 'Authorization': `Bearer ${this.apiToken}` }
      }
    );

    return resultResponse.data;
  }

  async runMetabaseQuery(query, params) {
    const response = await axios.post(
      'https://metabase.example.com/api/dataset',
      {
        database: this.databaseId,
        type: 'native',
        native: {
          query: query,
          'template-tags': params
        }
      },
      {
        headers: { 'X-Metabase-Session': this.sessionToken }
      }
    );

    return response.data.data.rows;
  }
}
```

---

### 4. Metadata Extraction

#### Extract Dashboard Metadata

```javascript
class MetadataExtractor {
  async extractDashboardMetadata(dashboardId) {
    const metadata = {
      id: dashboardId,
      name: null,
      description: null,
      views: [],
      dataSource: null,
      filters: [],
      parameters: [],
      lastUpdated: null,
      owner: null
    };

    // Tableau: Get workbook details
    if (this.platform === 'tableau') {
      const workbook = await this.getTableauWorkbook(dashboardId);
      metadata.name = workbook.name;
      metadata.description = workbook.description;
      metadata.lastUpdated = workbook.updatedAt;

      // Get views
      const views = await this.getTableauViews(dashboardId);
      metadata.views = views.map(v => ({
        id: v.id,
        name: v.name,
        fields: v.fields
      }));

      // Get data source
      const dataSources = await this.getTableauDataSources(dashboardId);
      metadata.dataSource = dataSources[0];
    }

    // Power BI: Get report details
    if (this.platform === 'powerbi') {
      const report = await this.getPowerBIReport(dashboardId);
      metadata.name = report.name;
      metadata.lastUpdated = report.modifiedDateTime;

      // Get pages
      const pages = await this.getPowerBIPages(dashboardId);
      metadata.views = pages.map(p => ({
        id: p.name,
        name: p.displayName,
        visuals: p.visuals
      }));

      // Get dataset
      metadata.dataSource = await this.getPowerBIDataset(report.datasetId);
    }

    return metadata;
  }

  async listDashboards(tenantId) {
    const dashboards = [];

    if (this.platform === 'tableau') {
      const response = await axios.get(
        `https://tableau.example.com/api/3.19/sites/${this.siteId}/workbooks`,
        {
          headers: { 'X-Tableau-Auth': this.authToken },
          params: { filter: `projectName:eq:tenant_${tenantId}` }
        }
      );

      dashboards.push(...response.data.workbooks.workbook);
    }

    if (this.platform === 'powerbi') {
      const response = await axios.get(
        `https://api.powerbi.com/v1.0/myorg/groups/${this.getWorkspaceId(tenantId)}/reports`,
        {
          headers: { 'Authorization': `Bearer ${this.accessToken}` }
        }
      );

      dashboards.push(...response.data.value);
    }

    return dashboards;
  }
}
```

---

### 5. Usage Analytics

#### Track Dashboard Usage

```javascript
class UsageAnalytics {
  async trackDashboardView(userId, dashboardId) {
    // Log view event
    await db.analyticsViews.insert({
      user_id: userId,
      dashboard_id: dashboardId,
      viewed_at: new Date(),
      session_id: this.sessionId
    });

    // Track in BI platform if supported
    if (this.platform === 'tableau') {
      await this.trackTableauView(userId, dashboardId);
    }
  }

  async getDashboardStats(dashboardId, startDate, endDate) {
    // Query from local tracking
    const stats = await db.query(`
      SELECT
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(*) as total_views,
        AVG(EXTRACT(EPOCH FROM (last_interaction_at - viewed_at))) as avg_duration_seconds
      FROM analytics_views
      WHERE dashboard_id = $1
        AND viewed_at BETWEEN $2 AND $3
    `, [dashboardId, startDate, endDate]);

    // Augment with BI platform stats if available
    if (this.platform === 'tableau') {
      const tableauStats = await this.getTableauViewStats(dashboardId, startDate, endDate);
      return {
        ...stats.rows[0],
        ...tableauStats
      };
    }

    return stats.rows[0];
  }

  async getTableauViewStats(workbookId, startDate, endDate) {
    // Use Tableau Repository API or Postgres metadata DB
    const response = await axios.get(
      `https://tableau.example.com/api/3.19/sites/${this.siteId}/workbooks/${workbookId}/views/stats`,
      {
        headers: { 'X-Tableau-Auth': this.authToken },
        params: {
          filter: `viewTime:gte:${startDate},viewTime:lte:${endDate}`
        }
      }
    );

    return {
      totalViews: response.data.totalViewCount,
      uniqueUsers: response.data.uniqueUserCount
    };
  }

  async getMostViewedDashboards(tenantId, limit = 10) {
    const result = await db.query(`
      SELECT
        dashboard_id,
        COUNT(*) as view_count,
        COUNT(DISTINCT user_id) as unique_users
      FROM analytics_views
      WHERE tenant_id = $1
        AND viewed_at > NOW() - INTERVAL '30 days'
      GROUP BY dashboard_id
      ORDER BY view_count DESC
      LIMIT $2
    `, [tenantId, limit]);

    return result.rows;
  }
}
```

---

### 6. Webhook Integration

#### Set Up Webhooks

```javascript
class WebhookManager {
  async setupWebhooks() {
    // Tableau: Configure webhooks for events
    if (this.platform === 'tableau') {
      await this.setupTableauWebhook('workbook-refresh-succeeded', '/webhooks/tableau/refresh-success');
      await this.setupTableauWebhook('workbook-refresh-failed', '/webhooks/tableau/refresh-failed');
      await this.setupTableauWebhook('datasource-updated', '/webhooks/tableau/datasource-updated');
    }

    // Power BI: Use Azure Event Grid (no direct webhooks)
    if (this.platform === 'powerbi') {
      await this.setupEventGridSubscription();
    }
  }

  async setupTableauWebhook(event, url) {
    await axios.post(
      `https://tableau.example.com/api/3.19/sites/${this.siteId}/webhooks`,
      {
        webhook: {
          'webhook-source': {
            'webhook-source-event-name': event
          },
          'webhook-destination': {
            'webhook-destination-http': {
              method: 'POST',
              url: `https://yourapp.example.com${url}`
            }
          },
          name: `${event}_webhook`,
          isEnabled: true
        }
      },
      {
        headers: { 'X-Tableau-Auth': this.authToken }
      }
    );
  }

  // Handle incoming webhooks
  async handleWebhook(event) {
    const { type, payload } = event;

    switch (type) {
      case 'workbook-refresh-succeeded':
        await this.onRefreshSuccess(payload);
        break;

      case 'workbook-refresh-failed':
        await this.onRefreshFailure(payload);
        break;

      case 'datasource-updated':
        await this.onDataSourceUpdated(payload);
        break;
    }
  }

  async onRefreshSuccess(payload) {
    const { workbookId, refreshTime } = payload;

    // Invalidate cache
    await cache.invalidate(`dashboard:${workbookId}`);

    // Notify users if subscribed
    await this.notifySubscribers(workbookId, 'refresh_complete');

    // Log event
    await db.refreshLog.insert({
      workbook_id: workbookId,
      status: 'success',
      completed_at: refreshTime
    });
  }

  async onRefreshFailure(payload) {
    const { workbookId, error } = payload;

    // Alert admins
    await this.alertAdmins({
      type: 'refresh_failed',
      workbookId,
      error
    });

    // Log failure
    await db.refreshLog.insert({
      workbook_id: workbookId,
      status: 'failed',
      error: error,
      failed_at: new Date()
    });
  }
}

// Express endpoint to receive webhooks
app.post('/webhooks/tableau/:event', async (req, res) => {
  const { event } = req.params;
  const payload = req.body;

  // Verify webhook signature
  const signature = req.headers['x-tableau-signature'];
  if (!webhookManager.verifySignature(payload, signature)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // Process webhook
  await webhookManager.handleWebhook({
    type: event,
    payload
  });

  res.json({ received: true });
});
```

---

### 7. Error Handling and Retry Logic

```javascript
class ResilientAPIClient {
  constructor(baseURL, apiToken) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Authorization': `Bearer ${apiToken}`
      },
      timeout: 30000
    });

    // Add retry interceptor
    this.client.interceptors.response.use(
      response => response,
      async error => {
        const config = error.config;

        // Don't retry if no config or already retried max times
        if (!config || config.__retryCount >= 3) {
          return Promise.reject(error);
        }

        config.__retryCount = config.__retryCount || 0;
        config.__retryCount++;

        // Exponential backoff
        const delay = Math.pow(2, config.__retryCount) * 1000;
        await this.sleep(delay);

        // Retry request
        return this.client(config);
      }
    );
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async callWithRetry(method, url, data = null) {
    try {
      const response = await this.client[method](url, data);
      return response.data;
    } catch (error) {
      console.error(`API call failed after retries: ${error.message}`);
      throw error;
    }
  }
}
```

---

## API Integration Checklist

- [ ] Authentication tokens properly managed and refreshed
- [ ] Rate limiting respected (check API docs)
- [ ] Retry logic implemented for transient failures
- [ ] Webhooks set up for important events
- [ ] Error handling for all API calls
- [ ] Logging of all API interactions
- [ ] API versioning strategy documented
- [ ] Timeouts configured appropriately
- [ ] Bulk operations optimized (batch APIs if available)
- [ ] API quota monitoring
- [ ] Backup/fallback for critical operations
- [ ] Testing of API integration in staging
- [ ] Documentation of API usage patterns
- [ ] Security: API keys in environment variables
- [ ] Regular API compatibility checks
