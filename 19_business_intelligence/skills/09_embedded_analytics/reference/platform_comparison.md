# BI Platform Comparison for Embedding

## Overview

Detailed comparison of major BI platforms for embedded analytics use cases.

## Platform Feature Matrix

| Feature | Tableau | Power BI Embedded | Looker | Metabase | Superset | Qlik |
|---------|---------|-------------------|--------|----------|----------|------|
| **Embedding Ease** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **White-Labeling** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **SSO Support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **RLS Capability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **API Completeness** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Mobile Support** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Pricing (SaaS)** | 💰💰💰💰💰 | 💰💰💰💰 | 💰💰💰💰💰 | 💰💰 | Free | 💰💰💰💰 |
| **Learning Curve** | Steep | Moderate | Moderate | Easy | Moderate | Steep |

---

## Tableau Embedded

### Strengths
- **Best-in-class visualizations**: Industry-leading viz capabilities
- **Mature embedding API**: Well-documented JavaScript API
- **Enterprise features**: Robust security, governance, scalability
- **Connected Apps**: Modern authentication for embedding
- **Large ecosystem**: Extensions, integrations, community

### Limitations
- **Cost**: Most expensive option
- **Complex licensing**: Multiple SKUs, user types
- **Limited white-labeling**: Cannot fully remove Tableau branding
- **Server management**: On-premise requires significant ops
- **Performance**: Can be slow with large datasets without extracts

### Embedding Example
```javascript
// Tableau Connected Apps (modern approach)
const token = jwt.sign({
  iss: connectedAppClientId,
  sub: user.email,
  aud: 'tableau',
  jti: uuidv4(),
  scp: ['tableau:views:embed'],
  exp: Math.floor(Date.now() / 1000) + 600,
  'https://tableau.com/oda': {
    tenant_id: user.tenantId
  }
}, connectedAppSecret);

const viz = new tableau.Viz(container, viewUrl, {
  width: '100%',
  height: '800px',
  hideTabs: true,
  hideToolbar: false,
  onFirstInteractive: () => {
    console.log('Loaded');
  }
});
```

### Best For
- Enterprise B2B SaaS
- Complex data visualization needs
- Organizations already using Tableau
- High-value customers willing to pay premium

### Pricing
- **Tableau Online**: $15-70/user/month
- **Embedded Analytics**: Custom pricing, typically $1000+/month
- **Server**: License + infrastructure costs

---

## Power BI Embedded

### Strengths
- **Best embedding story**: Purpose-built for embedding
- **Excellent white-labeling**: Complete branding control
- **Cost-effective**: Consumption-based pricing
- **Azure integration**: Seamless with Azure ecosystem
- **Strong RLS**: Dynamic RLS with DAX
- **Active development**: Frequent updates, new features

### Limitations
- **Microsoft ecosystem lock-in**: Requires Azure
- **DAX learning curve**: Complex for beginners
- **Report development**: Desktop app (Windows only)
- **Limited customization**: Less flexible than code-based solutions
- **Capacity management**: Need to understand A SKUs

### Embedding Example
```javascript
// Power BI Embedded with RLS
const embedToken = await powerbi.generateEmbedToken({
  reportId: reportId,
  datasetId: datasetId,
  identities: [{
    username: user.email,
    roles: ['TenantUser'],
    datasets: [datasetId]
  }],
  lifetimeInMinutes: 30
});

const config = {
  type: 'report',
  tokenType: models.TokenType.Embed,
  accessToken: embedToken,
  embedUrl: embedUrl,
  id: reportId,
  permissions: models.Permissions.Read,
  settings: {
    panes: {
      filters: { visible: false },
      pageNavigation: { visible: false }
    },
    bars: {
      actionBar: { visible: false }
    },
    background: models.BackgroundType.Transparent
  }
};

const report = powerbi.embed(container, config);
```

### Best For
- Modern SaaS applications
- Microsoft/Azure shops
- Budget-conscious startups
- Need for flexible pricing
- White-label requirements

### Pricing
- **Power BI Embedded**: $1/hour for A1 SKU (~$730/month 24/7)
- **A4 SKU**: $4/hour (~$2920/month) - typical for production
- **Per-user licensing**: $10-20/user/month (alternative)

---

## Looker (Google Cloud)

### Strengths
- **Best for embedding**: Originally designed for white-label
- **LookML**: Version-controlled data modeling
- **Excellent API**: Comprehensive REST API
- **Strong governance**: Centralized business logic
- **Git integration**: Version control for analytics
- **Google Cloud integration**: BigQuery native

### Limitations
- **Cost**: Premium pricing tier
- **LookML learning curve**: SQL-like but different
- **Requires Looker instance**: Cannot use Looker Studio for embedding
- **Performance**: Real-time queries can be slow
- **Limited offline**: Primarily online/real-time

### Embedding Example
```javascript
// Looker Embed SDK
LookerEmbedSDK.init('looker.example.com', '/auth/url');

LookerEmbedSDK.createDashboardWithId(dashboardId)
  .appendTo('#embed-container')
  .withFilters({
    'tenant_id': user.tenantId,
    'region': user.region
  })
  .withTheme('custom_theme')
  .build()
  .connect()
  .then((dashboard) => {
    console.log('Dashboard loaded');

    dashboard.on('dashboard:loaded', () => {
      // Custom handling
    });
  });
```

### Best For
- Product analytics embedding
- White-label requirements
- Data-driven SaaS products
- Google Cloud users
- API-first architectures

### Pricing
- **Looker**: Custom pricing, typically $3000-5000/month base
- **Per-user**: $30-50/user/month
- **Embedded**: Custom pricing based on usage

---

## Metabase

### Strengths
- **Open source**: Free self-hosted option
- **Easy to use**: Lowest learning curve
- **Fast setup**: Running in minutes
- **Good embedding**: JWT-based embedding
- **Active development**: Regular releases
- **Multi-database**: Connects to 20+ databases

### Limitations
- **Limited advanced analytics**: Basic compared to enterprise tools
- **Scaling challenges**: Self-hosted can be complex
- **Basic visualizations**: Limited chart types
- **RLS limitations**: Open source has basic RLS
- **Mobile experience**: Not optimized for mobile

### Embedding Example
```javascript
// Metabase JWT embedding
const jwt = require('jsonwebtoken');

const payload = {
  resource: { dashboard: 123 },
  params: {
    tenant_id: user.tenantId
  },
  exp: Math.round(Date.now() / 1000) + (10 * 60) // 10 minutes
};

const token = jwt.sign(payload, METABASE_SECRET_KEY);

const iframeUrl = `https://metabase.example.com/embed/dashboard/${token}#bordered=false&titled=false`;

// Embed iframe
document.getElementById('container').innerHTML =
  `<iframe src="${iframeUrl}" width="100%" height="600" frameborder="0"></iframe>`;
```

### Best For
- Startups and small teams
- Budget-constrained projects
- Internal tools
- Quick MVPs
- Self-hosted requirements

### Pricing
- **Open Source**: Free
- **Cloud**: $85/month for 5 users
- **Enterprise**: Custom pricing (~$15000/year+)

---

## Apache Superset

### Strengths
- **Open source**: Completely free
- **Modern UI**: React-based, responsive
- **SQL Lab**: Interactive SQL editor
- **Extensible**: Python-based, customizable
- **Many databases**: 40+ database connectors
- **Active community**: Airbnb, Apache backing

### Limitations
- **Self-hosted complexity**: Requires ops expertise
- **Limited embedding docs**: Less mature embedding
- **Performance**: Can be slow without caching
- **RLS complexity**: Requires code for advanced RLS
- **Enterprise features**: Missing some enterprise needs

### Embedding Example
```javascript
// Superset guest token embedding
const response = await fetch('https://superset.example.com/api/v1/security/guest_token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiToken}`
  },
  body: JSON.stringify({
    user: {
      username: user.email,
      first_name: user.firstName,
      last_name: user.lastName
    },
    resources: [{
      type: 'dashboard',
      id: dashboardId
    }],
    rls: [{
      clause: `tenant_id = ${user.tenantId}`
    }]
  })
});

const { token } = await response.json();

const embedUrl = `https://superset.example.com/embedded/${token}`;
```

### Best For
- Self-hosted requirements
- Python/data engineering teams
- Custom analytics platforms
- Cost-sensitive projects
- Need full control

### Pricing
- **Open Source**: Free
- **Managed hosting**: $50-500/month (Preset.io)
- **Enterprise support**: Custom

---

## Qlik Sense

### Strengths
- **Associative engine**: Unique data exploration
- **Strong performance**: In-memory processing
- **Robust RLS**: Section access for security
- **Mobile apps**: Native iOS/Android apps
- **Enterprise features**: Governance, security, scale

### Limitations
- **Complex**: Steep learning curve
- **Cost**: Premium pricing
- **Embedding complexity**: More complex than competitors
- **Modern UI**: Less modern than Power BI/Looker
- **Documentation**: Can be fragmented

### Embedding Example
```javascript
// Qlik Sense embedding
const config = {
  host: 'qlik.example.com',
  prefix: '/',
  port: 443,
  isSecure: true
};

require.config({
  baseUrl: `https://${config.host}${config.prefix}resources`
});

require(['js/qlik'], (qlik) => {
  qlik.setOnError((error) => {
    console.error('Qlik error:', error);
  });

  const app = qlik.openApp('app-id', config);

  app.visualization.create('line-chart', {
    dimensions: ['Month'],
    measures: ['=Sum(Sales)']
  }).then((viz) => {
    viz.show('container');
  });
});
```

### Best For
- Enterprise deployments
- Complex associative analytics
- Existing Qlik users
- Performance-critical applications

### Pricing
- **Qlik Sense Business**: $30/user/month
- **Enterprise**: Custom pricing
- **OEM/Embedded**: Custom pricing

---

## Redash

### Strengths
- **Open source**: Free to use
- **SQL-first**: Great for SQL users
- **Simple**: Easy setup and use
- **Query sharing**: Collaborative queries
- **Alerts**: Built-in alerting

### Limitations
- **Limited embedding**: Basic embedding support
- **Basic visualizations**: Simple chart types
- **No RLS**: Must implement externally
- **Limited support**: Small company backing
- **Scaling**: Not designed for large deployments

### Best For
- Internal dashboards
- SQL-savvy teams
- Simple embedding needs
- Ad-hoc analysis

### Pricing
- **Open Source**: Free
- **Managed**: Discontinued (use self-hosted)

---

## Comparison by Use Case

### Best for SaaS Embedding
1. **Power BI Embedded** - Best value, excellent features
2. **Looker** - Best white-labeling, premium option
3. **Tableau** - Best visualizations, premium option

### Best for Budget
1. **Metabase** (Open Source) - Free, easy to use
2. **Superset** - Free, more powerful
3. **Power BI Embedded** - Pay-as-you-go

### Best for White-Labeling
1. **Looker** - Purpose-built for embedding
2. **Power BI Embedded** - Excellent branding control
3. **Metabase** - Good white-labeling

### Best for API Integration
1. **Looker** - Most comprehensive API
2. **Power BI** - Extensive REST API
3. **Tableau** - Good API coverage

### Best for Ease of Use
1. **Metabase** - Simplest learning curve
2. **Power BI** - Familiar to Excel users
3. **Looker** - Intuitive for SQL users

### Best for Performance
1. **Qlik** - In-memory engine
2. **Power BI** - DAX performance
3. **Tableau** - With extracts

---

## Migration Considerations

### From Tableau to Power BI Embedded
```javascript
// Considerations:
// - Rewrite reports in Power BI Desktop
// - Convert Tableau calculations to DAX
// - Migrate data sources
// - Update embedding code
// - Retrain users

// Cost savings: ~50-70% reduction
// Time investment: 2-6 months for large deployments
```

### From Metabase to Looker
```javascript
// Considerations:
// - Model data in LookML
// - Recreate dashboards
// - Implement SSO
// - Update embedding code
// - Budget for increased costs

// Cost increase: 10-20x
// Features gain: Significant (governance, RLS, API)
// Time investment: 3-6 months
```

---

## Decision Framework

```javascript
function recommendPlatform(requirements) {
  const {
    budget,
    userCount,
    complexity,
    whiteLabel,
    selfHosted,
    existingStack
  } = requirements;

  if (budget === 'low') {
    if (selfHosted) {
      return complexity === 'high' ? 'Superset' : 'Metabase';
    }
    return 'Power BI Embedded';
  }

  if (budget === 'medium') {
    if (existingStack === 'microsoft') {
      return 'Power BI Embedded';
    }
    return 'Tableau';
  }

  if (budget === 'high') {
    if (whiteLabel === 'critical') {
      return 'Looker';
    }
    if (existingStack === 'google') {
      return 'Looker';
    }
    if (complexity === 'high') {
      return 'Tableau';
    }
    return 'Power BI Embedded';
  }
}
```

---

## Platform Selection Checklist

- [ ] Evaluate total cost of ownership (TCO)
- [ ] Test embedding capabilities with POC
- [ ] Verify RLS meets security requirements
- [ ] Check mobile experience
- [ ] Assess white-labeling capabilities
- [ ] Review API documentation
- [ ] Test performance with realistic data
- [ ] Evaluate learning curve for team
- [ ] Check vendor roadmap and support
- [ ] Consider existing technology stack
- [ ] Review compliance and certifications
- [ ] Test with target user personas
- [ ] Evaluate migration complexity (if applicable)
- [ ] Check community and ecosystem
- [ ] Review SLA and support options
