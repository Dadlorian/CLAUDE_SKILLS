# SSO Implementation Guide

## Option 1: JWT-Based SSO (Recommended)

### Backend: Generate JWT

```javascript
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
    exp: Math.floor(Date.now() / 1000) + (30 * 60)
  };

  return jwt.sign(payload, process.env.JWT_SECRET, {
    algorithm: 'HS256'
  });
}

app.post('/api/embed-token', (req, res) => {
  const token = generateEmbedJWT(req.user);
  res.json({ token, expiresIn: 1800 });
});
```

### Frontend: Use Token

```javascript
async function embedDashboard() {
  const { token } = await fetch('/api/embed-token', {
    method: 'POST',
    credentials: 'include'
  }).then(r => r.json());

  // Use token with BI platform
  const viz = new tableau.Viz(container, dashboardUrl, {
    token: token
  });
}
```

## Option 2: SAML SSO

### Configure SAML IdP

```xml
<!-- SAML 2.0 Configuration -->
<EntityDescriptor>
  <SPSSODescriptor>
    <AssertionConsumerService
      Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
      Location="https://bi-platform.com/auth/saml/callback"
      index="0"
    />
  </SPSSODescriptor>
</EntityDescriptor>
```

### Generate SAML Assertion

```javascript
const saml = require('samlify');

const idp = saml.IdentityProvider({
  metadata: fs.readFileSync('./idp-metadata.xml')
});

app.post('/saml/login', (req, res) => {
  const user = req.user;

  const assertion = idp.createLoginResponse({
    attributes: {
      email: user.email,
      tenant_id: user.tenantId,
      roles: user.roles.join(',')
    }
  });

  res.send(assertion);
});
```

## Option 3: OAuth 2.0

### Authorization Flow

```javascript
// Step 1: Redirect to authorization endpoint
app.get('/auth/bi-platform', (req, res) => {
  const authUrl = `https://bi-platform.com/oauth/authorize?` +
    `client_id=${clientId}&` +
    `redirect_uri=${redirectUri}&` +
    `response_type=code&` +
    `scope=embed:dashboards&` +
    `state=${generateState()}`;

  res.redirect(authUrl);
});

// Step 2: Handle callback
app.get('/auth/callback', async (req, res) => {
  const { code, state } = req.query;

  // Verify state (CSRF protection)
  if (!verifyState(state)) {
    return res.status(400).send('Invalid state');
  }

  // Exchange code for token
  const tokenResponse = await fetch('https://bi-platform.com/oauth/token', {
    method: 'POST',
    body: JSON.stringify({
      grant_type: 'authorization_code',
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri
    })
  });

  const { access_token, refresh_token } = await tokenResponse.json();

  // Store tokens in session
  req.session.accessToken = access_token;
  req.session.refreshToken = refresh_token;

  res.redirect('/dashboard');
});
```

## Security Checklist

- [ ] Use HTTPS for all SSO flows
- [ ] Implement CSRF protection (state parameter)
- [ ] Short token expiration (< 30 minutes)
- [ ] Secure token storage (HttpOnly cookies)
- [ ] Rate limiting on token endpoints
- [ ] Audit logging for all SSO events
- [ ] Token revocation capability
- [ ] Regular security audits
