# Quick Start: Power BI Embedded

## Prerequisites
- Azure subscription
- Power BI Pro license
- Workspace in Power BI Service
- Report published to workspace

## Step 1: Azure Setup

```bash
# Create Azure AD App Registration
az ad app create --display-name "Analytics Embedded App"

# Note the Application (client) ID

# Create client secret
az ad app credential reset --id <app-id>

# Grant Power BI API permissions
az ad app permission add \
  --id <app-id> \
  --api 00000009-0000-0000-c000-000000000000 \
  --api-permissions 4ae1bf56-f562-4747-b7bc-2fa0874ed46f=Scope
```

## Step 2: Power BI Embedded Capacity

```bash
# Create Power BI Embedded capacity (A SKU)
az powerbi embedded-capacity create \
  --resource-group analytics-rg \
  --name analytics-capacity \
  --location eastus \
  --sku-name A1 \
  --sku-tier A

# Assign workspace to capacity (do in Power BI portal)
```

## Step 3: Backend Implementation

```javascript
// powerbi-service.js
const axios = require('axios');
const msal = require('@azure/msal-node');

class PowerBIService {
  constructor() {
    this.msalClient = new msal.ConfidentialClientApplication({
      auth: {
        clientId: process.env.AZURE_CLIENT_ID,
        clientSecret: process.env.AZURE_CLIENT_SECRET,
        authority: 'https://login.microsoftonline.com/organizations'
      }
    });
  }

  async getAccessToken() {
    const result = await this.msalClient.acquireTokenByClientCredential({
      scopes: ['https://analysis.windows.net/powerbi/api/.default']
    });
    return result.accessToken;
  }

  async generateEmbedToken(reportId, datasetId, user) {
    const accessToken = await this.getAccessToken();

    const response = await axios.post(
      `https://api.powerbi.com/v1.0/myorg/GenerateToken`,
      {
        datasets: [{ id: datasetId }],
        reports: [{ id: reportId }],
        identities: [{
          username: user.email,
          roles: [user.role],
          datasets: [datasetId]
        }]
      },
      {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      }
    );

    return response.data.token;
  }
}

// API endpoint
app.post('/api/powerbi-embed', async (req, res) => {
  const service = new PowerBIService();
  
  const token = await service.generateEmbedToken(
    req.body.reportId,
    req.body.datasetId,
    req.user
  );

  res.json({
    token,
    embedUrl: `https://app.powerbi.com/reportEmbed?reportId=${req.body.reportId}`,
    expiration: new Date(Date.now() + 60 * 60 * 1000).toISOString()
  });
});
```

## Step 4: Frontend Embedding

```javascript
import { models } from 'powerbi-client';
import { PowerBIEmbed } from 'powerbi-client-react';

export default function PowerBIDashboard() {
  const [embedConfig, setEmbedConfig] = useState(null);

  useEffect(() => {
    fetchEmbedConfig();
  }, []);

  async function fetchEmbedConfig() {
    const response = await fetch('/api/powerbi-embed', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reportId: 'YOUR_REPORT_ID',
        datasetId: 'YOUR_DATASET_ID'
      })
    });

    const { token, embedUrl } = await response.json();

    setEmbedConfig({
      type: 'report',
      tokenType: models.TokenType.Embed,
      accessToken: token,
      embedUrl: embedUrl,
      settings: {
        panes: {
          filters: { visible: false },
          pageNavigation: { visible: true }
        },
        background: models.BackgroundType.Transparent
      }
    });
  }

  return embedConfig ? (
    <PowerBIEmbed
      embedConfig={embedConfig}
      cssClassName="report-container"
    />
  ) : (
    <div>Loading...</div>
  );
}
```

## Step 5: RLS Setup

```dax
-- In Power BI Desktop, define role
-- Modeling > Manage Roles > New

-- Role: TenantUser
[tenant_id] = USERPRINCIPALNAME()

-- Or use lookup table
[tenant_id] = LOOKUPVALUE(
    Users[tenant_id],
    Users[email],
    USERPRINCIPALNAME()
)
```

## Cost Optimization

```javascript
// Auto-pause capacity during off-hours
const cron = require('node-cron');

cron.schedule('0 20 * * *', async () => {
  await pauseCapacity('analytics-capacity');
});

cron.schedule('0 6 * * *', async () => {
  await resumeCapacity('analytics-capacity');
});

async function pauseCapacity(name) {
  await exec(`az powerbi embedded-capacity suspend --name ${name}`);
}

async function resumeCapacity(name) {
  await exec(`az powerbi embedded-capacity resume --name ${name}`);
}
```

## Common Issues

**"Invalid embed token"**: Check Azure AD permissions
**"Report not loading"**: Verify workspace assigned to capacity
**"RLS not working"**: Ensure role defined and user mapped correctly
