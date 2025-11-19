# SSO Patterns for Embedded Analytics

## Overview

Single Sign-On (SSO) patterns enable seamless authentication between your SaaS application and embedded analytics without requiring users to log in separately.

## Core SSO Patterns

### 1. Trusted Authentication (Most Common)

**How it works**:
1. User authenticates to your SaaS app
2. Your backend requests embed token from BI platform
3. BI platform trusts your backend and generates signed token
4. Token contains user identity and permissions
5. Frontend uses token to embed analytics

**Pros**:
- No user-facing redirects
- Complete control over user experience
- Can inject custom attributes
- Works with any authentication method

**Cons**:
- Requires backend integration
- Token management complexity
- Must secure backend-to-BI communication

**Implementation**:
```javascript
// Backend (Node.js)
app.post('/api/embed-token', async (req, res) => {
  const user = req.user; // From your auth middleware

  const token = await biPlatform.generateEmbedToken({
    username: user.email,
    tenantId: user.tenantId,
    roles: user.roles,
    rls: { tenant_id: user.tenantId },
    expiresIn: '30m'
  });

  res.json({ token });
});

// Frontend
const tokenResponse = await fetch('/api/embed-token', {
  method: 'POST',
  credentials: 'include'
});
const { token } = await tokenResponse.json();

// Embed with token
embedDashboard(dashboardUrl, token);
```

---

### 2. SAML SSO

**How it works**:
1. User clicks embedded analytics link
2. Redirect to BI platform with SAML request
3. BI platform redirects to your SAML IdP
4. User authenticates (or uses existing session)
5. SAML assertion sent to BI platform
6. BI platform validates and creates session
7. User redirected back to embedded analytics

**Pros**:
- Enterprise standard
- Centralized identity management
- Audit trail
- Supports complex auth scenarios

**Cons**:
- User-facing redirects
- Complex configuration
- Requires SAML IdP setup
- Slower user experience

**Best for**: Enterprise deployments, existing SAML infrastructure

**Configuration Example**:
```xml
<!-- SAML 2.0 Assertion -->
<saml:Assertion>
  <saml:Subject>
    <saml:NameID>user@example.com</saml:NameID>
  </saml:Subject>
  <saml:AttributeStatement>
    <saml:Attribute Name="tenant_id">
      <saml:AttributeValue>tenant_123</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="roles">
      <saml:AttributeValue>analyst</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

---

### 3. OAuth 2.0 / OpenID Connect

**How it works**:
1. User initiates analytics access
2. OAuth authorization flow starts
3. User consents (first time only)
4. Authorization code exchanged for token
5. Token used to access embedded analytics

**Pros**:
- Modern standard
- Delegated authorization
- Refresh tokens for long sessions
- Industry best practice

**Cons**:
- Requires OAuth server
- Initial consent flow
- Token refresh complexity
- Redirect-based flow

**Best for**: Modern SaaS apps, API-first architectures

**Implementation**:
```javascript
// OAuth 2.0 Authorization Code Flow
// Step 1: Redirect to authorization endpoint
const authUrl = `https://bi.example.com/oauth/authorize?` +
  `client_id=${clientId}&` +
  `redirect_uri=${redirectUri}&` +
  `response_type=code&` +
  `scope=embed:dashboards&` +
  `state=${secureRandomState}`;

window.location.href = authUrl;

// Step 2: Handle callback
app.get('/oauth/callback', async (req, res) => {
  const { code, state } = req.query;

  // Verify state to prevent CSRF
  if (state !== storedState) {
    throw new Error('Invalid state');
  }

  // Exchange code for token
  const tokenResponse = await fetch('https://bi.example.com/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'authorization_code',
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri
    })
  });

  const { access_token, refresh_token } = await tokenResponse.json();

  // Store tokens securely
  req.session.accessToken = access_token;
  req.session.refreshToken = refresh_token;

  res.redirect('/dashboard');
});
```

---

### 4. JWT-Based SSO

**How it works**:
1. Your app generates signed JWT
2. JWT contains user claims and tenant context
3. JWT passed to BI platform
4. BI platform validates signature and claims
5. Analytics embedded with user context

**Pros**:
- Stateless authentication
- No backend calls per request
- Fast and efficient
- Self-contained tokens

**Cons**:
- Token size can be large
- Revocation complexity
- Clock synchronization needed
- Secret management critical

**Best for**: Microservices, serverless, high-scale deployments

**Implementation**:
```javascript
// Backend: Generate JWT
const jwt = require('jsonwebtoken');

function generateEmbedJWT(user) {
  const payload = {
    sub: user.id,
    email: user.email,
    tenant_id: user.tenantId,
    roles: user.roles,
    rls: {
      tenant_id: user.tenantId,
      department: user.department
    },
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (30 * 60) // 30 mins
  };

  return jwt.sign(payload, process.env.JWT_SECRET, {
    algorithm: 'HS256'
  });
}

// Frontend: Use JWT
const embedToken = await fetch('/api/jwt-token').then(r => r.text());

embedDashboard(dashboardUrl, embedToken);
```

**BI Platform Validation**:
```javascript
// BI platform validates JWT
const jwt = require('jsonwebtoken');

function validateEmbedToken(token) {
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET, {
      algorithms: ['HS256']
    });

    // Extract RLS context
    const tenantId = decoded.tenant_id;
    const roles = decoded.roles;

    // Apply row-level security
    applyRLS(tenantId, roles);

    return decoded;
  } catch (err) {
    throw new Error('Invalid token');
  }
}
```

---

### 5. Session-Based SSO

**How it works**:
1. User authenticates to your app
2. Your app creates session in BI platform
3. Session cookie shared between domains
4. Analytics accessed via shared session

**Pros**:
- Simple implementation
- No tokens to manage
- Familiar session model
- Server-side session control

**Cons**:
- Requires same-domain or CORS
- Cookie restrictions (SameSite, 3rd party)
- Scaling challenges
- Session fixation risks

**Best for**: Single-domain deployments, simple integrations

**Implementation**:
```javascript
// Create session in BI platform
app.post('/api/analytics-session', async (req, res) => {
  const user = req.user;

  // Create session in BI platform
  const session = await biPlatform.createSession({
    username: user.email,
    attributes: {
      tenant_id: user.tenantId
    }
  });

  // Set session cookie (must be same domain or CORS)
  res.cookie('bi_session', session.id, {
    domain: '.example.com', // Shared domain
    httpOnly: true,
    secure: true,
    sameSite: 'none'
  });

  res.json({ success: true });
});
```

---

## Platform-Specific Implementations

### Tableau Connected Apps (Recommended for Tableau)

```javascript
// Backend: Generate Tableau JWT
const jwt = require('jsonwebtoken');

function generateTableauJWT(user, connectedAppClientId, connectedAppSecret) {
  const payload = {
    iss: connectedAppClientId,
    sub: user.email,
    aud: 'tableau',
    jti: uuidv4(),
    scp: ['tableau:views:embed', 'tableau:metrics:embed'],
    exp: Math.floor(Date.now() / 1000) + (10 * 60), // 10 mins

    // Custom claims for RLS
    'https://tableau.com/oda': {
      tenant_id: user.tenantId,
      department: user.department
    }
  };

  return jwt.sign(payload, connectedAppSecret, {
    algorithm: 'HS256',
    header: {
      kid: connectedAppClientId,
      iss: connectedAppClientId
    }
  });
}

// Frontend: Embed with Tableau JWT
const vizContainer = document.getElementById('viz');
const vizUrl = 'https://tableau.example.com/views/Sales';
const token = await fetch('/api/tableau-jwt').then(r => r.text());

const viz = new tableau.Viz(vizContainer, vizUrl, {
  hideTabs: true,
  width: '100%',
  height: '600px',
  onFirstInteractive: () => console.log('Loaded')
});
```

---

### Power BI Embed Tokens

```javascript
// Backend: Generate Power BI Embed Token
const axios = require('axios');

async function generatePowerBIEmbedToken(user, reportId) {
  // Get Azure AD access token
  const authResponse = await axios.post(
    `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`,
    new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      scope: 'https://analysis.windows.net/powerbi/api/.default',
      grant_type: 'client_credentials'
    })
  );

  const accessToken = authResponse.data.access_token;

  // Generate embed token with RLS
  const embedTokenResponse = await axios.post(
    `https://api.powerbi.com/v1.0/myorg/reports/${reportId}/GenerateToken`,
    {
      accessLevel: 'View',
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

  return embedTokenResponse.data.token;
}

// Frontend: Embed with Power BI
const embedConfig = {
  type: 'report',
  tokenType: models.TokenType.Embed,
  accessToken: embedToken,
  embedUrl: embedUrl,
  id: reportId,
  settings: {
    filterPaneEnabled: false,
    navContentPaneEnabled: false
  }
};

const report = powerbi.embed(embedContainer, embedConfig);
```

---

### Looker SSO Embed URLs

```javascript
// Backend: Generate Looker SSO URL
const crypto = require('crypto');

function generateLookerSSOUrl(user, embedUrl, lookerSecret) {
  const json_external_user_id = user.id;
  const json_first_name = user.firstName;
  const json_last_name = user.lastName;
  const json_permissions = ['access_data', 'see_looks'];
  const json_models = ['sales'];
  const json_user_attributes = {
    tenant_id: user.tenantId,
    department: user.department
  };

  const json_nonce = uuidv4();
  const json_time = Math.floor(Date.now() / 1000);

  const url_data = {
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

  const url_data_json = JSON.stringify(url_data);
  const url_data_encoded = Buffer.from(url_data_json).toString('base64');

  const signature = crypto
    .createHmac('sha1', lookerSecret)
    .update(url_data_encoded)
    .digest('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');

  return `${embedUrl}?nonce=${json_nonce}&time=${json_time}&` +
         `signature=${signature}&external_user_id=${json_external_user_id}&` +
         `permissions=${json_permissions.join(',')}&models=${json_models.join(',')}&` +
         `user_attributes=${encodeURIComponent(JSON.stringify(json_user_attributes))}`;
}
```

---

## Token Management Best Practices

### Token Expiration Strategy

```javascript
class EmbedTokenManager {
  constructor() {
    this.token = null;
    this.expiresAt = null;
  }

  async getToken(forceRefresh = false) {
    // Check if token is valid
    if (!forceRefresh && this.token && this.expiresAt > Date.now() + 60000) {
      return this.token;
    }

    // Fetch new token
    const response = await fetch('/api/embed-token', {
      method: 'POST',
      credentials: 'include'
    });

    const data = await response.json();
    this.token = data.token;
    this.expiresAt = Date.now() + (data.expiresIn * 1000);

    return this.token;
  }

  // Proactive refresh before expiration
  scheduleRefresh() {
    const refreshTime = this.expiresAt - Date.now() - 60000; // 1 min before

    setTimeout(async () => {
      await this.getToken(true);
      this.scheduleRefresh();
    }, refreshTime);
  }
}

const tokenManager = new EmbedTokenManager();
```

---

### Token Security

```javascript
// Backend: Secure token generation
function generateSecureEmbedToken(user) {
  // Validate user session
  if (!user || !user.id) {
    throw new Error('Unauthorized');
  }

  // Rate limiting
  const tokenKey = `embed_token:${user.id}`;
  const tokenCount = redis.get(tokenKey);
  if (tokenCount > 10) {
    throw new Error('Too many token requests');
  }
  redis.incr(tokenKey);
  redis.expire(tokenKey, 60); // Reset after 1 minute

  // Generate token with minimal permissions
  const token = jwt.sign({
    sub: user.id,
    email: user.email,
    tenant_id: user.tenantId,
    // Only include necessary claims
    permissions: ['view_dashboards'], // Minimal permissions
    exp: Math.floor(Date.now() / 1000) + (30 * 60) // Short expiration
  }, process.env.JWT_SECRET);

  // Log token generation for audit
  auditLog.log({
    event: 'embed_token_generated',
    userId: user.id,
    tenantId: user.tenantId,
    timestamp: new Date()
  });

  return token;
}
```

---

## Multi-Tenant SSO Patterns

### Tenant-Specific SSO Configuration

```javascript
// Support different SSO methods per tenant
class TenantSSOProvider {
  async getEmbedToken(user, tenant) {
    const ssoConfig = await this.getTenantSSOConfig(tenant.id);

    switch (ssoConfig.method) {
      case 'saml':
        return this.initiateSAMLFlow(user, ssoConfig);

      case 'oauth':
        return this.initiateOAuthFlow(user, ssoConfig);

      case 'jwt':
        return this.generateJWTToken(user, tenant, ssoConfig.secret);

      case 'trusted':
      default:
        return this.generateTrustedToken(user, tenant);
    }
  }

  async getTenantSSOConfig(tenantId) {
    return await db.ssoConfigs.findOne({ tenantId });
  }
}
```

---

## Troubleshooting Common SSO Issues

### Issue 1: Token Expiration During Session

**Solution**:
```javascript
// Implement token refresh
embedAPI.on('tokenExpired', async () => {
  const newToken = await tokenManager.getToken(true);
  embedAPI.updateToken(newToken);
});
```

### Issue 2: CORS Errors with Session Cookies

**Solution**:
```javascript
// Backend: Set CORS headers
app.use(cors({
  origin: 'https://yourapp.example.com',
  credentials: true
}));

// Set SameSite=None for cross-site cookies
res.cookie('session', sessionId, {
  sameSite: 'none',
  secure: true,
  httpOnly: true
});
```

### Issue 3: Clock Skew in JWT Validation

**Solution**:
```javascript
// Add clock tolerance
jwt.verify(token, secret, {
  clockTolerance: 60 // 60 seconds tolerance
});
```

### Issue 4: User Attribute Sync Delays

**Solution**:
```javascript
// Force user attribute refresh on token generation
async function generateTokenWithFreshAttributes(user) {
  // Sync latest user attributes
  const latestUser = await fetchUserFromDatabase(user.id);

  return generateEmbedToken({
    ...latestUser,
    _synced_at: Date.now()
  });
}
```

---

## Performance Optimization

### Token Caching

```javascript
// Cache tokens to reduce backend calls
class CachedTokenManager {
  constructor(cacheTTL = 25 * 60 * 1000) { // 25 minutes
    this.cache = new Map();
    this.cacheTTL = cacheTTL;
  }

  getCacheKey(userId, tenantId) {
    return `${userId}:${tenantId}`;
  }

  async getToken(user) {
    const key = this.getCacheKey(user.id, user.tenantId);
    const cached = this.cache.get(key);

    if (cached && cached.expiresAt > Date.now()) {
      return cached.token;
    }

    const token = await this.fetchNewToken(user);
    this.cache.set(key, {
      token,
      expiresAt: Date.now() + this.cacheTTL
    });

    return token;
  }
}
```

---

## Security Checklist

- [ ] Use HTTPS for all SSO communication
- [ ] Implement short token expiration (15-30 minutes)
- [ ] Add rate limiting on token generation endpoints
- [ ] Validate all token claims before use
- [ ] Never expose secrets or keys to frontend
- [ ] Log all SSO events for audit trail
- [ ] Implement token revocation mechanism
- [ ] Use secure random values for nonces/state
- [ ] Validate redirect URIs to prevent open redirects
- [ ] Implement CSRF protection for OAuth flows
- [ ] Use HttpOnly, Secure, SameSite for cookies
- [ ] Regularly rotate signing keys
- [ ] Monitor for suspicious token generation patterns
- [ ] Implement user consent for data access
- [ ] Test SSO across different browsers and devices
