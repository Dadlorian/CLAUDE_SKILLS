# Embedded Analytics Patterns Reference

## Embedding Approaches Overview

| Approach | Description | Use Cases | Complexity |
|----------|-------------|-----------|------------|
| **iFrame** | Simple HTML iframe embedding | Quick integration, basic needs | Low |
| **JavaScript SDK** | Native SDK integration | Rich interactions, custom UX | Medium |
| **REST API** | Build custom visualization layer | Full control, custom rendering | High |
| **White-Label** | Completely branded experience | SaaS products, customer-facing | Medium-High |

## Tableau Embedded Analytics

### Embedding API v3 (Current)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Embedded Tableau Dashboard</title>
    <script type="module" src="https://tableau.company.com/javascripts/api/tableau.embedding.3.latest.min.js"></script>
</head>
<body>
    <tableau-viz id="tableauViz"
        src="https://tableau.company.com/views/SalesDashboard/Overview"
        width="1200"
        height="800"
        hide-tabs
        toolbar="bottom">
    </tableau-viz>

    <script type="module">
        const viz = document.getElementById('tableauViz');

        // Listen for events
        viz.addEventListener('firstinteractive', function() {
            console.log('Viz loaded');

            // Apply dynamic filter
            const sheet = viz.workbook.activeSheet;
            sheet.applyFilterAsync('Region', ['West', 'East'], 'replace');
        });

        // Get data
        viz.addEventListener('markselectionchanged', async function(event) {
            const marks = await event.detail.getMarksAsync();
            console.log('Selected marks:', marks);
        });
    </script>
</body>
</html>
```

### Connected Apps (Secure Embedding with JWT)
```javascript
// Server-side: Generate JWT token
const jwt = require('jsonwebtoken');

function generateTableauToken(username, clientId) {
    const payload = {
        "iss": clientId,  // Connected App Client ID
        "exp": Math.floor(Date.now() / 1000) + (10 * 60),  // 10 min expiry
        "jti": generateUUID(),
        "aud": "tableau",
        "sub": username,
        "scp": ["tableau:views:embed", "tableau:metrics:embed"]
    };

    const secretId = 'your-secret-id';
    const secretValue = 'your-secret-value';

    return jwt.sign(payload, secretValue, {
        algorithm: 'HS256',
        keyid: secretId,
        issuer: clientId
    });
}

// Client-side: Use JWT
const token = await fetch('/api/tableau-token').then(r => r.text());

const viz = new tableau.Viz({
    container: document.getElementById('vizContainer'),
    url: 'https://tableau.company.com/views/Dashboard',
    token: token,
    height: 800,
    width: 1200,
    hideTabs: true,
    onFirstInteractive: function() {
        // Apply user-specific filters
        viz.getWorkbook().getActiveSheet()
            .applyFilterAsync('CustomerID', currentUser.customerId);
    }
});
```

### Dynamic Row-Level Security
```javascript
// Tableau Trusted Ticket (legacy) or Connected Apps
// Server-side endpoint
app.post('/api/tableau-embed-url', async (req, res) => {
    const { username, dashboardUrl } = req.body;

    // Get user's data permissions from your database
    const userPermissions = await getUserPermissions(username);

    // Method 1: URL parameters (less secure)
    const filteredUrl = `${dashboardUrl}?Region=${userPermissions.region}&:embed=yes`;

    // Method 2: Connected Apps JWT (secure)
    const token = generateTableauToken(username, CLIENT_ID);

    res.json({
        url: dashboardUrl,
        token: token,
        // These will be applied as filters in client-side code
        filters: {
            'Region': userPermissions.region,
            'Department': userPermissions.department
        }
    });
});
```

### Multi-Tenancy Pattern
```javascript
// SaaS application with tenant isolation
class TableauEmbedding {
    constructor(tenantId) {
        this.tenantId = tenantId;
        this.baseUrl = 'https://tableau.company.com';
    }

    async embedDashboard(containerId, dashboardPath) {
        // Get tenant-specific token
        const token = await this.getTenantToken();

        const viz = new tableau.Viz({
            container: document.getElementById(containerId),
            url: `${this.baseUrl}${dashboardPath}`,
            token: token,
            // Apply tenant filter
            onFirstInteractive: async () => {
                const sheet = viz.getWorkbook().getActiveSheet();
                await sheet.applyFilterAsync('TenantID', this.tenantId);
            }
        });

        return viz;
    }

    async getTenantToken() {
        const response = await fetch('/api/embed-token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tenantId: this.tenantId,
                scope: ['read:dashboards']
            })
        });

        return response.json().then(data => data.token);
    }
}

// Usage
const embedding = new TableauEmbedding('tenant-123');
embedding.embedDashboard('viz1', '/views/TenantMetrics/Overview');
```

## Power BI Embedded

### Embed for Your Organization (User Owns Data)
```javascript
// Users have Power BI licenses
// Authenticate with Azure AD

const models = window['powerbi-client'].models;

// Get embed token from backend
fetch('/api/powerbi/embed-info')
    .then(response => response.json())
    .then(data => {
        const config = {
            type: 'report',
            id: data.reportId,
            embedUrl: data.embedUrl,
            accessToken: data.accessToken,  // Azure AD token
            tokenType: models.TokenType.Aad,
            permissions: models.Permissions.All,
            settings: {
                panes: {
                    filters: { visible: false },
                    pageNavigation: { visible: true }
                },
                background: models.BackgroundType.Transparent
            }
        };

        const reportContainer = document.getElementById('reportContainer');
        const report = powerbi.embed(reportContainer, config);

        // Handle events
        report.on('loaded', function() {
            console.log('Report loaded');
        });

        report.on('rendered', function() {
            console.log('Report rendered');
        });

        report.on('error', function(event) {
            console.error(event.detail);
        });
    });
```

### Embed for Your Customers (App Owns Data)
```csharp
// Server-side: Generate embed token (C#/.NET)
using Microsoft.PowerBI.Api;
using Microsoft.PowerBI.Api.Models;
using Microsoft.Rest;

public class PowerBIEmbedService
{
    private readonly PowerBIClient _client;

    public async Task<EmbedConfig> GetEmbedConfig(string reportId, string tenantId)
    {
        // Authenticate as service principal
        var credential = new ClientCredential(clientId, clientSecret);
        var authContext = new AuthenticationContext(authority);
        var authResult = await authContext.AcquireTokenAsync(
            resourceUrl,
            credential
        );

        var tokenCredentials = new TokenCredentials(authResult.AccessToken, "Bearer");
        _client = new PowerBIClient(new Uri(apiUrl), tokenCredentials);

        // Get report
        var report = await _client.Reports.GetReportInGroupAsync(workspaceId, reportId);

        // Generate embed token with RLS
        var generateTokenRequest = new GenerateTokenRequest(
            accessLevel: "View",
            identities: new List<EffectiveIdentity>
            {
                new EffectiveIdentity(
                    username: $"tenant-{tenantId}",
                    roles: new List<string> { "TenantRole" },
                    datasets: new List<string> { report.DatasetId }
                )
            }
        );

        var embedToken = await _client.Reports.GenerateTokenInGroupAsync(
            workspaceId,
            reportId,
            generateTokenRequest
        );

        return new EmbedConfig
        {
            EmbedToken = embedToken.Token,
            EmbedUrl = report.EmbedUrl,
            ReportId = report.Id.ToString(),
            ExpiresAt = embedToken.Expiration
        };
    }
}
```

### Multi-Tenant RLS Implementation
```dax
// In Power BI Desktop: Security roles

// Role: TenantRole
[TenantID] = USERPRINCIPALNAME()

// Or more sophisticated:
VAR CurrentUser = USERPRINCIPALNAME()
VAR TenantID =
    LOOKUPVALUE(
        UserTenantMapping[TenantID],
        UserTenantMapping[UserIdentity], CurrentUser
    )
RETURN
    Sales[TenantID] = TenantID

// Also filter related tables
VAR AllowedCustomers =
    CALCULATETABLE(
        VALUES(Customers[CustomerID]),
        Sales[TenantID] = TenantID
    )
RETURN
    Customers[CustomerID] IN AllowedCustomers
```

### Custom Visuals for White-Label
```typescript
// Create custom Power BI visual with branded colors
// In capabilities.json
{
    "dataRoles": [
        {
            "displayName": "Values",
            "name": "values",
            "kind": "Measure"
        }
    ],
    "objects": {
        "branding": {
            "properties": {
                "primaryColor": {
                    "type": { "fill": { "solid": { "color": true } } }
                },
                "logo": {
                    "type": { "image": {} }
                }
            }
        }
    }
}

// In visual.ts
export class Visual implements IVisual {
    private settings: VisualSettings;

    public update(options: VisualUpdateOptions) {
        this.settings = Visual.parseSettings(options.dataViews[0]);

        // Apply custom branding
        const primaryColor = this.settings.branding.primaryColor;
        const logo = this.settings.branding.logo;

        // Render with branded colors
        this.renderChart(data, primaryColor, logo);
    }
}
```

## Looker Embedded Analytics

### SSO Embed URL Generation
```ruby
# Ruby: Generate signed embed URL
require 'cgi'
require 'securerandom'
require 'uri'
require 'base64'
require 'openssl'
require 'json'

class LookerEmbedURL
  def self.generate(host, secret, external_user_id, permissions, models, dashboard_id, filters = {})
    # Build embed user JSON
    embed_user = {
      external_user_id: external_user_id,
      first_name: external_user_id.split('@')[0],
      last_name: 'User',
      permissions: permissions,
      models: models,
      access_filters: filters
    }

    # Path to dashboard
    path = "/embed/dashboards/#{dashboard_id}"

    # Create signature
    json_embed_user = JSON.generate(embed_user)
    nonce = SecureRandom.hex(16)
    timestamp = Time.now.to_i.to_s

    string_to_sign = [
      host,
      path,
      nonce,
      timestamp,
      session_length.to_s,
      external_user_id,
      permissions.join(','),
      models.join(','),
      group_ids.join(','),
      external_group_id || '',
      user_attributes.to_json,
      access_filters.to_json
    ].join("\n")

    signature = Base64.strict_encode64(
      OpenSSL::HMAC.digest('sha1', secret, string_to_sign)
    )

    # Build query parameters
    params = {
      nonce: nonce,
      time: timestamp,
      session_length: session_length,
      external_user_id: external_user_id,
      permissions: permissions.join(','),
      models: models.join(','),
      signature: signature,
      first_name: embed_user[:first_name],
      last_name: embed_user[:last_name]
    }

    # Add filters
    filters.each do |key, value|
      params["filter[#{key}]"] = value
    end

    # Construct final URL
    "https://#{host}#{path}?" + URI.encode_www_form(params)
  end
end

# Usage
url = LookerEmbedURL.generate(
  'company.looker.com',
  ENV['LOOKER_EMBED_SECRET'],
  'user@company.com',
  ['access_data', 'see_lookml_dashboards'],
  ['sales', 'marketing'],
  '123',
  {
    'tenant_id' => 'tenant-abc',
    'region' => 'West'
  }
)
```

### JavaScript SDK Embedding
```javascript
// Client-side: Looker Embedding SDK
import { LookerEmbedSDK } from '@looker/embed-sdk';

// Initialize SDK
LookerEmbedSDK.init('company.looker.com', {
    url: '/api/looker/auth',  // Your backend auth endpoint
    withCredentials: true
});

// Embed dashboard
LookerEmbedSDK.createDashboardWithId(dashboardId)
    .appendTo('#dashboard-container')
    .withClassName('looker-embed')
    .withFilters({
        'Orders Created Date': '90 days',
        'Users Region': currentUser.region
    })
    .withParams({
        'theme': 'custom_theme'
    })
    .on('dashboard:loaded', (event) => {
        console.log('Dashboard loaded');
    })
    .on('dashboard:run:complete', (event) => {
        console.log('Dashboard run complete');
    })
    .on('drillmenu:click', (event) => {
        console.log('Drill clicked:', event);
    })
    .build()
    .connect()
    .then((dashboard) => {
        // Dashboard object for further interaction
        window.lookerDashboard = dashboard;

        // Update filters dynamically
        dashboard.updateFilters({
            'Product Category': 'Electronics'
        });

        // Run dashboard
        dashboard.run();
    });
```

### Whitelabeling with Themes
```lookml
# Define custom theme in LookML
# themes/customer_theme.json
{
  "show_title": false,
  "show_filters_bar": true,
  "font_family": "Customer Sans, Arial, sans-serif",
  "font_source": "https://fonts.company.com/customer-sans.css",
  "background_color": "#FFFFFF",
  "base_font_size": "14px",
  "page_color": "#F5F5F5",
  "title_color": "#333333",
  "text_tile_text_color": "#666666",
  "tile_background_color": "#FFFFFF",
  "tile_text_color": "#333333"
}
```

## Qlik Sense Embedded

### Mashup API (iframe with API control)
```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://qlik.company.com/resources/assets/external/requirejs/require.js"></script>
</head>
<body>
    <div id="qlik-object"></div>

    <script>
        require.config({
            baseUrl: 'https://qlik.company.com/resources'
        });

        require(['js/qlik'], function(qlik) {
            // Configuration
            const config = {
                host: 'qlik.company.com',
                prefix: '/',
                port: 443,
                isSecure: true
            };

            // Open app
            const app = qlik.openApp('app-id', config);

            // Create object
            app.getObject('qlik-object', 'object-id').then(function(vis) {
                // Object embedded
                console.log('Visualization rendered');

                // Apply selection
                app.field('Region').selectValues(['West'], false, false);
            });

            // Listen to selections
            app.selectionState().OnData.bind(function() {
                const selections = app.selectionState().selections;
                console.log('Current selections:', selections);
            });
        });
    </script>
</body>
</html>
```

### Capability APIs (Advanced)
```javascript
// Qlik Engine API via enigma.js
const enigma = require('enigma.js');
const schema = require('enigma.js/schemas/12.612.0.json');
const WebSocket = require('ws');

const config = {
    schema,
    url: `wss://qlik.company.com/app/${appId}`,
    createSocket: (url) => new WebSocket(url, {
        headers: {
            'Authorization': `Bearer ${jwtToken}`
        }
    })
};

async function embedQlikWithAPI() {
    const session = enigma.create(config);
    const global = await session.open();
    const doc = await global.openDoc(appId);

    // Create hypercube (data for custom viz)
    const object = await doc.createSessionObject({
        qInfo: {
            qType: 'my-custom-viz'
        },
        qHyperCubeDef: {
            qDimensions: [{
                qDef: {
                    qFieldDefs: ['Product'],
                    qSortCriterias: [{
                        qSortByLoadOrder: 1
                    }]
                }
            }],
            qMeasures: [{
                qDef: {
                    qDef: 'Sum(Sales)',
                    qLabel: 'Total Sales'
                }
            }],
            qInitialDataFetch: [{
                qTop: 0,
                qLeft: 0,
                qHeight: 100,
                qWidth: 2
            }]
        }
    });

    // Get data
    const layout = await object.getLayout();
    const data = layout.qHyperCube.qDataPages[0].qMatrix;

    // Render custom visualization
    renderCustomChart(data);

    // Make selection
    await object.selectHyperCubeValues('/qHyperCubeDef', 0, [0, 2, 5]);

    await session.close();
}
```

### Multi-Tenant Section Access
```qlik
// In load script
Section Access;
LOAD * INLINE [
    ACCESS, USERID, TENANTID, REDUCTION
    USER, tenant1@company.com, TENANT001, *
    USER, tenant2@company.com, TENANT002, *
    ADMIN, admin@company.com, *, *
];

Section Application;
// Main data with TenantID field
Orders:
LOAD
    OrderID,
    TenantID,
    Product,
    Sales
FROM [data.qvd] (qvd);

// Qlik automatically filters based on Section Access
```

## Apache Superset Embedded

### Guest Token API
```python
# Server-side: Generate guest token
from superset import security_manager
from superset.utils.core import get_example_default_schema
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/superset/guest-token', methods=['POST'])
def get_guest_token():
    # Define what the guest user can see
    user = {
        'username': 'guest_user',
        'first_name': 'Guest',
        'last_name': 'User'
    }

    resources = [{
        'type': 'dashboard',
        'id': '123'  # Dashboard ID to embed
    }]

    # Row-level security
    rls = [{
        'clause': f"tenant_id = '{request.json['tenant_id']}'"
    }]

    # Generate token (valid for 5 minutes)
    guest_token = security_manager.create_guest_access_token(
        user=user,
        resources=resources,
        rls_rules=rls
    )

    return jsonify({
        'token': guest_token,
        'dashboard_id': '123'
    })
```

### Client-Side Embedding
```javascript
// Embed Superset dashboard
async function embedSupersetDashboard(containerId, dashboardId, tenantId) {
    // Get guest token from backend
    const response = await fetch('/api/superset/guest-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_id: tenantId })
    });

    const { token } = await response.json();

    // Build embed URL
    const supersetDomain = 'https://superset.company.com';
    const embedUrl = `${supersetDomain}/embedded/${dashboardId}`;

    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.src = `${embedUrl}?standalone=3&guest_token=${token}`;
    iframe.width = '100%';
    iframe.height = '800px';
    iframe.frameBorder = '0';

    document.getElementById(containerId).appendChild(iframe);

    // postMessage communication
    window.addEventListener('message', (event) => {
        if (event.origin !== supersetDomain) return;

        console.log('Message from Superset:', event.data);
    });
}

// Usage
embedSupersetDashboard('dashboard-container', '123', 'tenant-abc');
```

## Common Embedding Patterns

### Pattern 1: Single Dashboard per Customer
```
Customer A → Dashboard A (filtered to Customer A data)
Customer B → Dashboard B (filtered to Customer B data)
Customer C → Dashboard C (filtered to Customer C data)

Implementation:
- Separate workspace/project per customer
- Customer-specific branding
- Isolated content
```

### Pattern 2: Shared Dashboard with RLS
```
All Customers → Same Dashboard

Implementation:
- Single dashboard/report
- Row-level security filters by customer
- Dynamic branding via URL parameters
- More maintainable, single source
```

### Pattern 3: Hybrid Multi-Tier
```
Tier 1 Customers → Full custom dashboards
Tier 2 Customers → Shared dashboards with RLS
Tier 3 Customers → Standard reports only

Implementation:
- Premium customers get white-label
- Standard customers share infrastructure
- Billing/licensing aligned with tiers
```

## Security Best Practices

### Authentication Checklist
- [ ] Use JWT or signed URLs (never API keys in client)
- [ ] Implement token expiration (5-60 minutes)
- [ ] Rotate signing secrets regularly
- [ ] Validate token on every request
- [ ] Use HTTPS only
- [ ] Implement rate limiting

### Authorization Checklist
- [ ] Row-level security configured
- [ ] Column-level masking for sensitive data
- [ ] Principle of least privilege
- [ ] Audit logging enabled
- [ ] Regular permission reviews
- [ ] Separate admin and embed users

### Multi-Tenancy Checklist
- [ ] Tenant ID in all data tables
- [ ] Automated tenant filtering
- [ ] No cross-tenant data leakage
- [ ] Tenant-level usage monitoring
- [ ] Tenant isolation testing
- [ ] Emergency tenant suspension capability

## Performance Optimization

### Embedding Performance Tips
```
1. Lazy Loading
   - Load dashboards on-demand, not page load
   - Use intersection observer for scroll-based loading

2. Caching
   - Cache embed tokens (with expiry)
   - Use CDN for static assets
   - Enable query result caching

3. Data Limits
   - Paginate large result sets
   - Use aggregations
   - Implement date range defaults

4. Network
   - Use same domain embedding when possible
   - Minimize postMessage frequency
   - Compress API responses
```

## Monitoring Embedded Analytics

```javascript
// Track embedded analytics usage
function trackEmbedUsage(event) {
    analytics.track('Embedded Dashboard', {
        customer_id: currentCustomer.id,
        dashboard_id: event.dashboardId,
        event_type: event.type,  // load, filter, drill, export
        load_time_ms: event.loadTime,
        error: event.error || null,
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString()
    });
}

// Monitor performance
const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
        if (entry.name.includes('embed')) {
            trackEmbedUsage({
                type: 'performance',
                metric: entry.name,
                value: entry.duration
            });
        }
    }
});

observer.observe({ entryTypes: ['measure', 'navigation'] });
```

## Resources
- Tableau Embedding: https://help.tableau.com/current/api/embedding_api/en-us/
- Power BI Embedded: https://docs.microsoft.com/en-us/power-bi/developer/embedded/
- Looker Embed SDK: https://github.com/looker-open-source/embed-sdk
- Qlik Mashup API: https://help.qlik.com/en-US/sense-developer/
- Superset Embedding: https://superset.apache.org/docs/installation/embedded-dashboard
