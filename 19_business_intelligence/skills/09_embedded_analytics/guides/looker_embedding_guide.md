# Looker Embedding Guide

## Prerequisites
- Looker instance
- Embed secret configured
- LookML model with data

## Step 1: Configure Looker for Embedding

```bash
# In Looker Admin
# Settings > Embed > Enable Embed Authentication
# Note your Embed Secret
```

## Step 2: Generate SSO URL

```javascript
const crypto = require('crypto');

function generateLookerSSOUrl(user, embedPath) {
  const LOOKER_HOST = 'looker.example.com';
  const LOOKER_SECRET = process.env.LOOKER_EMBED_SECRET;

  const json_external_user_id = user.id;
  const json_first_name = user.firstName;
  const json_last_name = user.lastName;
  const json_permissions = ['access_data', 'see_looks'];
  const json_models = ['sales'];
  
  // User attributes for RLS
  const json_user_attributes = {
    tenant_id: user.tenantId.toString(),
    department: user.department
  };

  const json_nonce = crypto.randomBytes(16).toString('hex');
  const json_time = Math.floor(Date.now() / 1000);

  // Build JSON object
  const obj = {
    external_user_id: json_external_user_id,
    first_name: json_first_name,
    last_name: json_last_name,
    permissions: json_permissions,
    models: json_models,
    user_attributes: json_user_attributes,
    access_filters: {},
    nonce: json_nonce,
    time: json_time
  };

  // Encode and sign
  const json_str = JSON.stringify(obj);
  const json_b64 = Buffer.from(json_str).toString('base64');

  const signature = crypto
    .createHmac('sha1', LOOKER_SECRET)
    .update(json_b64)
    .digest('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');

  // Build URL
  const params = new URLSearchParams({
    nonce: json_nonce,
    time: json_time,
    signature: signature,
    external_user_id: json_external_user_id,
    permissions: json_permissions.join(','),
    models: json_models.join(','),
    access_filters: JSON.stringify({}),
    first_name: json_first_name,
    last_name: json_last_name,
    user_attributes: JSON.stringify(json_user_attributes),
    force_logout_login: 'true'
  });

  return `https://${LOOKER_HOST}${embedPath}?${params.toString()}`;
}

// API endpoint
app.post('/api/looker-sso', (req, res) => {
  const embedPath = '/embed/dashboards/sales';
  const url = generateLookerSSOUrl(req.user, embedPath);

  res.json({ embedUrl: url });
});
```

## Step 3: Embed with SDK

```javascript
import { LookerEmbedSDK } from '@looker/embed-sdk';

LookerEmbedSDK.init('looker.example.com', '/api/looker-sso');

function embedDashboard(dashboardId) {
  LookerEmbedSDK.createDashboardWithId(dashboardId)
    .appendTo('#dashboard-container')
    .withTheme('custom')
    .withFilters({
      'Date': '30 days'
    })
    .build()
    .connect()
    .then((dashboard) => {
      console.log('Dashboard loaded');

      dashboard.on('dashboard:loaded', () => {
        // Dashboard ready
      });

      dashboard.on('dashboard:run:start', () => {
        // Query started
      });

      dashboard.on('dashboard:run:complete', () => {
        // Query complete
      });
    })
    .catch((error) => {
      console.error('Embed error:', error);
    });
}
```

## Step 4: Implement RLS in LookML

```lookml
# Define user attribute
# Admin > Users > User Attributes
# Name: tenant_id
# Type: String

# In model file
connection: "database"

access_grant: tenant_access {
  user_attribute: tenant_id
  allowed_values: ["*"]
}

explore: sales {
  required_access_grants: [tenant_access]

  # Always filter by tenant
  sql_always_where:
    ${tenant_id} = '{{ _user_attributes["tenant_id"] }}' ;;
  
  # Or for multiple attributes
  sql_always_where:
    ${tenant_id} = '{{ _user_attributes["tenant_id"] }}'
    AND ${department} = '{{ _user_attributes["department"] }}' ;;
}
```

## Step 5: Custom Styling

```javascript
// Create custom theme
const customTheme = {
  key_color: '#0078D4',
  background_color: '#FFFFFF',
  tile_background_color: '#F3F2F1',
  text_tile_text_color: '#252423'
};

// Apply when embedding
LookerEmbedSDK.createDashboardWithId(dashboardId)
  .withTheme(customTheme)
  .build();
```

## Testing

```javascript
describe('Looker Embedding', () => {
  it('should generate valid SSO URL', () => {
    const user = {
      id: '123',
      firstName: 'John',
      lastName: 'Doe',
      tenantId: 1,
      department: 'sales'
    };

    const url = generateLookerSSOUrl(user, '/embed/dashboards/1');

    expect(url).toContain('looker.example.com');
    expect(url).toContain('external_user_id=123');
    expect(url).toContain('signature=');
  });
});
```
