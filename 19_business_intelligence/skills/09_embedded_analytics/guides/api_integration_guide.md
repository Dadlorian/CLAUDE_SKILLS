# API Integration Guide

## Dashboard Management API

### Create Dashboard Programmatically

```javascript
class DashboardManager {
  async createDashboard(config) {
    // Tableau
    const workbook = await tableau.createWorkbook({
      name: config.name,
      projectId: config.projectId
    });

    // Power BI
    const report = await powerbi.createReport({
      name: config.name,
      datasetId: config.datasetId
    });

    return workbook || report;
  }

  async cloneDashboard(sourceId, tenantId) {
    const source = await this.getDashboard(sourceId);

    return await this.createDashboard({
      name: `${source.name} - Tenant ${tenantId}`,
      template: source.layout,
      tenantId
    });
  }

  async updateDashboard(dashboardId, changes) {
    await api.patch(`/dashboards/${dashboardId}`, changes);
  }

  async deleteDashboard(dashboardId) {
    await api.delete(`/dashboards/${dashboardId}`);
  }
}
```

### User Management API

```javascript
class UserManager {
  async syncUser(user) {
    const biUser = await this.getBIUser(user.email);

    if (biUser) {
      await this.updateBIUser(biUser.id, {
        role: this.mapRole(user.role),
        permissions: user.permissions
      });
    } else {
      await this.createBIUser(user);
    }
  }

  async createBIUser(user) {
    return await api.post('/users', {
      email: user.email,
      name: `${user.firstName} ${user.lastName}`,
      role: this.mapRole(user.role)
    });
  }

  async deleteUser(email) {
    const biUser = await this.getBIUser(email);
    if (biUser) {
      await api.delete(`/users/${biUser.id}`);
    }
  }
}
```

### Data Refresh API

```javascript
class DataRefreshManager {
  async refreshDataSource(dataSourceId) {
    const refresh = await api.post(
      `/datasources/${dataSourceId}/refresh`
    );

    return refresh.id;
  }

  async getRefreshStatus(refreshId) {
    const status = await api.get(`/refreshes/${refreshId}`);

    return {
      status: status.state,
      progress: status.progress,
      error: status.error
    };
  }

  async scheduleRefresh(dataSourceId, schedule) {
    await api.post(`/datasources/${dataSourceId}/schedules`, {
      frequency: schedule.frequency,
      time: schedule.time,
      timezone: schedule.timezone
    });
  }
}
```

## Webhooks

### Setup Webhooks

```javascript
async function setupWebhooks() {
  await api.post('/webhooks', {
    event: 'dashboard.refreshed',
    url: 'https://yourapp.com/webhooks/refresh',
    secret: process.env.WEBHOOK_SECRET
  });

  await api.post('/webhooks', {
    event: 'user.created',
    url: 'https://yourapp.com/webhooks/user',
    secret: process.env.WEBHOOK_SECRET
  });
}
```

### Handle Webhooks

```javascript
app.post('/webhooks/:event', (req, res) => {
  const signature = req.headers['x-webhook-signature'];

  if (!verifySignature(req.body, signature)) {
    return res.status(401).send('Invalid signature');
  }

  const { event, payload } = req.body;

  switch (event) {
    case 'dashboard.refreshed':
      handleRefresh(payload);
      break;

    case 'dashboard.failed':
      handleFailure(payload);
      break;
  }

  res.sendStatus(200);
});

function verifySignature(body, signature) {
  const expected = crypto
    .createHmac('sha256', process.env.WEBHOOK_SECRET)
    .update(JSON.stringify(body))
    .digest('hex');

  return signature === expected;
}
```

## API Checklist
- [ ] Authentication configured
- [ ] Rate limiting respected
- [ ] Error handling implemented
- [ ] Retry logic for failures
- [ ] Webhooks secured
- [ ] API versioning handled
- [ ] Timeouts configured
- [ ] Logging enabled
