# Authentication and SSO Reference for BI Platforms

## Overview of Authentication Methods

### Supported Authentication Types by Platform

| Method | Tableau | Power BI | Looker | Qlik | Superset |
|--------|---------|----------|--------|------|----------|
| **Username/Password** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **SAML 2.0** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **OAuth 2.0** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **OpenID Connect** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **LDAP/AD** | ✓ | ✓ AAD | ✓ | ✓ | ✓ |
| **Kerberos** | ✓ | ✓ | Limited | ✓ | Limited |
| **Multi-Factor Auth** | Via IdP | ✓ Native | Via IdP | Via IdP | Via IdP |
| **Certificate-based** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **API Keys** | ✓ PAT | ✓ Service Principal | ✓ API Keys | ✓ | ✓ |

## Tableau Authentication

### SAML Configuration
```xml
<!-- Tableau Server SAML Configuration -->
<Metadata xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <SPSSODescriptor
    AuthnRequestsSigned="true"
    protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">

    <KeyDescriptor use="signing">
      <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
        <ds:X509Data>
          <ds:X509Certificate>
            <!-- Certificate -->
          </ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </KeyDescriptor>

    <NameIDFormat>
      urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress
    </NameIDFormat>

    <AssertionConsumerService
      Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
      Location="https://tableau.company.com/saml/acs"
      index="0"
      isDefault="true"/>
  </SPSSODescriptor>
</Metadata>
```

### Tableau Server CLI Commands
```bash
# Enable SAML
tsm authentication saml configure \
  --idp-entity-id "https://idp.company.com" \
  --idp-metadata-file "/path/to/idp-metadata.xml" \
  --idp-return-url "https://tableau.company.com"

# Apply pending changes
tsm pending-changes apply

# Import certificate
tsm authentication saml import-certificate \
  --cert-file "/path/to/certificate.pem"

# Map SAML attributes
tsm authentication saml map-assertions \
  --user-name "email" \
  --display-name "displayName"
```

### Personal Access Tokens (PAT)
```python
# Create PAT via Tableau REST API
import requests

# Step 1: Sign in to get auth token
auth_url = f"{server_url}/api/3.19/auth/signin"
auth_payload = {
    "credentials": {
        "name": username,
        "password": password,
        "site": {"contentUrl": site_id}
    }
}
auth_response = requests.post(auth_url, json=auth_payload)
auth_token = auth_response.json()['credentials']['token']

# Step 2: Create PAT
pat_url = f"{server_url}/api/3.19/sites/{site_id}/users/{user_id}/personalAccessTokens"
headers = {'X-Tableau-Auth': auth_token}
pat_payload = {
    "personalAccessToken": {
        "name": "API_Access_Token"
    }
}
pat_response = requests.post(pat_url, json=pat_payload, headers=headers)
print(pat_response.json())
```

### Embedded Authentication
```javascript
// Tableau Embedding API v3 with Connected Apps
const tableau = window.tableau;

// JWT authentication for embedded dashboards
const viz = new tableau.Viz({
  container: document.getElementById('vizContainer'),
  url: 'https://tableau.company.com/views/Dashboard',
  token: jwtToken, // Generated server-side
  height: 800,
  width: 1200
});
```

## Power BI Authentication

### Azure AD Configuration
```powershell
# Register Power BI app in Azure AD
az ad app create \
  --display-name "PowerBI-App" \
  --identifier-uris "https://company.com/powerbi" \
  --reply-urls "https://app.powerbi.com/redirect"

# Grant admin consent for Power BI Service API
az ad app permission add \
  --id <app-id> \
  --api 00000009-0000-0000-c000-000000000000 \
  --api-permissions <permission-id>=Scope

az ad app permission admin-consent --id <app-id>
```

### Service Principal Authentication
```python
# Power BI REST API with Service Principal
from msal import ConfidentialClientApplication
import requests

# MSAL authentication
authority = f"https://login.microsoftonline.com/{tenant_id}"
app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret
)

# Get access token
scopes = ["https://analysis.windows.net/powerbi/api/.default"]
result = app.acquire_token_for_client(scopes=scopes)
access_token = result['access_token']

# Use token for API calls
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Example: Get datasets
response = requests.get(
    f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets',
    headers=headers
)
```

### Embedded Analytics Authentication
```javascript
// Power BI Embedded with AAD token
const models = window['powerbi-client'].models;

// Get embed token from backend
fetch('/api/getEmbedToken')
  .then(response => response.json())
  .then(data => {
    const config = {
      type: 'report',
      id: data.reportId,
      embedUrl: data.embedUrl,
      accessToken: data.embedToken,
      tokenType: models.TokenType.Embed,
      settings: {
        filterPaneEnabled: false,
        navContentPaneEnabled: false
      }
    };

    const reportContainer = document.getElementById('reportContainer');
    powerbi.embed(reportContainer, config);
  });
```

### Row-Level Security (RLS)
```dax
// DAX-based RLS
[Email] = USERPRINCIPALNAME()

// Or with dynamic assignment
VAR UserEmail = USERPRINCIPALNAME()
VAR UserRegion =
    LOOKUPVALUE(
        UserSecurity[Region],
        UserSecurity[Email], UserEmail
    )
RETURN
    Sales[Region] = UserRegion
```

## Looker Authentication

### SAML Setup
```ruby
# config/looker.yml (simplified)
auth:
  saml:
    enabled: true
    idp_issuer: "https://idp.company.com"
    idp_url: "https://idp.company.com/saml/sso"
    idp_cert: |
      -----BEGIN CERTIFICATE-----
      MIIDXTCCAkWg...
      -----END CERTIFICATE-----
    user_attribute_map_email: "email"
    user_attribute_map_first_name: "firstName"
    user_attribute_map_last_name: "lastName"
    default_new_user_role_ids: [3]
```

### OAuth for Embedded Analytics
```python
# Server-side embed URL generation with SSO
import time
import binascii
import hashlib
import json
import urllib
from base64 import b64encode

# Looker embed secret
embed_secret = "your_embed_secret"

# Build embed URL
def create_embed_url(
    host,
    dashboard_id,
    user_id,
    first_name,
    last_name,
    permissions,
    models,
    group_ids=None,
    external_user_id=None,
    user_attributes=None
):
    # Create embed path
    path = f"/embed/dashboards/{dashboard_id}"

    # Build JSON with user info
    embed_user = {
        "external_user_id": external_user_id or user_id,
        "first_name": first_name,
        "last_name": last_name,
        "permissions": permissions,
        "models": models,
        "access_filters": user_attributes or {}
    }

    if group_ids:
        embed_user["group_ids"] = group_ids

    # Create signature
    json_data = json.dumps(embed_user)
    nonce = binascii.hexlify(os.urandom(16)).decode()
    timestamp = int(time.time())

    string_to_sign = f"{host}\n{nonce}\n{timestamp}\n{json_data}\n{path}"
    signature = b64encode(
        hmac.new(
            embed_secret.encode(),
            string_to_sign.encode(),
            hashlib.sha1
        ).digest()
    ).decode()

    # Build final URL
    params = {
        'nonce': nonce,
        'time': timestamp,
        'signature': signature,
        'external_user_id': embed_user['external_user_id'],
        'first_name': first_name,
        'last_name': last_name,
        'permissions': json.dumps(permissions),
        'models': json.dumps(models)
    }

    if user_attributes:
        for key, value in user_attributes.items():
            params[f'user_attributes[{key}]'] = value

    query_string = urllib.parse.urlencode(params)
    return f"https://{host}{path}?{query_string}"
```

### API Authentication
```python
# Looker API SDK
import looker_sdk

# Initialize SDK with credentials
sdk = looker_sdk.init40()  # reads from looker.ini

# Or programmatic init
from looker_sdk import methods40, models

sdk = methods40.LookerSDK(
    base_url="https://company.looker.com:19999",
    client_id="your_client_id",
    client_secret="your_client_secret",
    api_version="4.0"
)

# Use SDK
user = sdk.me()
dashboards = sdk.all_dashboards()
```

### User Attributes for RLS
```lookml
# In LookML model
explore: orders {
  access_filter: {
    field: region
    user_attribute: allowed_regions
  }

  access_filter: {
    field: customer_segment
    user_attribute: customer_tier
  }
}

# In view
dimension: revenue {
  sql:
    CASE
      WHEN {% user_attribute 'department' %} = 'Finance'
      THEN ${TABLE}.revenue
      ELSE NULL
    END ;;
}
```

## Qlik Sense Authentication

### JWT Authentication
```javascript
// Qlik Sense Enterprise with JWT
const qlikAuth = require('qlik-auth');

const config = {
  host: 'qlik.company.com',
  port: 443,
  appId: 'app-id',
  userId: 'DOMAIN\\username',
  userDirectory: 'DOMAIN',
  certificates: {
    cert: fs.readFileSync('client.pem'),
    key: fs.readFileSync('client_key.pem'),
    ca: fs.readFileSync('root.pem')
  }
};

// Create JWT token
const jwt = qlikAuth.generateJWT({
  userId: config.userId,
  userDirectory: config.userDirectory
}, privateKey);
```

### Section Access (RLS)
```qlik
// In load script
Section Access;
LOAD * INLINE [
    ACCESS, USERID, REGION
    USER, DOMAIN\john.doe, East
    USER, DOMAIN\jane.smith, West
    ADMIN, DOMAIN\admin, *
];

Section Application;
// Regular data load
LOAD
    Region,
    Sales,
    Customer
FROM [data.qvd] (qvd);
```

### Qlik Cloud OAuth
```python
# Qlik Cloud API with OAuth
import requests

# Get OAuth token
token_url = "https://oauth.platform.qlik.com/oauth/token"
token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret
}
token_response = requests.post(token_url, data=token_data)
access_token = token_response.json()['access_token']

# Use token for API calls
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Example: Get apps
apps_url = f"https://{tenant}.{region}.qlikcloud.com/api/v1/apps"
apps_response = requests.get(apps_url, headers=headers)
```

## Apache Superset Authentication

### Flask-AppBuilder Auth
```python
# superset_config.py

# Database authentication (default)
from flask_appbuilder.security.manager import AUTH_DB
AUTH_TYPE = AUTH_DB

# OAuth configuration
from flask_appbuilder.security.manager import AUTH_OAUTH
AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [{
    'name': 'google',
    'icon': 'fa-google',
    'token_key': 'access_token',
    'remote_app': {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
        'client_kwargs': {
            'scope': 'email profile'
        },
        'request_token_url': None,
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth'
    }
}]

# LDAP configuration
from flask_appbuilder.security.manager import AUTH_LDAP
AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = "ldap://ldap.company.com"
AUTH_LDAP_BIND_USER = "cn=admin,dc=company,dc=com"
AUTH_LDAP_BIND_PASSWORD = "password"
AUTH_LDAP_SEARCH = "ou=users,dc=company,dc=com"
AUTH_LDAP_UID_FIELD = "uid"
AUTH_LDAP_FIRSTNAME_FIELD = "givenName"
AUTH_LDAP_LASTNAME_FIELD = "sn"
AUTH_LDAP_EMAIL_FIELD = "mail"
```

### Row-Level Security
```python
# Custom RLS function
def my_rls_filter(view_name):
    """
    Return SQLAlchemy filter for RLS
    """
    from flask import g
    from superset import db
    from sqlalchemy import text

    user = g.user
    if user.is_anonymous:
        return None

    # Get user's allowed regions from custom user attribute
    allowed_regions = db.session.query(UserAttribute)\
        .filter_by(user_id=user.id, attribute_name='region')\
        .all()

    regions = [attr.attribute_value for attr in allowed_regions]

    if view_name == 'sales':
        return text(f"region IN ({','.join(repr(r) for r in regions)})")

    return None

# Register RLS filter
from superset.security import SupersetSecurityManager

class CustomSecurityManager(SupersetSecurityManager):
    def get_rls_filters(self, table):
        return [my_rls_filter(table.table_name)]

CUSTOM_SECURITY_MANAGER = CustomSecurityManager
```

### API Authentication
```python
# Login and get access token
import requests

login_url = "http://superset.company.com/api/v1/security/login"
login_data = {
    "username": "admin",
    "password": "password",
    "provider": "db",
    "refresh": True
}

response = requests.post(login_url, json=login_data)
tokens = response.json()
access_token = tokens['access_token']
refresh_token = tokens['refresh_token']

# Use access token
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Get dashboards
dashboards_url = "http://superset.company.com/api/v1/dashboard/"
dashboards = requests.get(dashboards_url, headers=headers)
```

## Best Practices

### General Security Principles
1. **Always use HTTPS** in production
2. **Implement MFA** via identity provider
3. **Rotate secrets** regularly (API keys, certificates)
4. **Principle of least privilege** for user permissions
5. **Audit logging** for authentication events
6. **Session timeout** configuration
7. **IP whitelisting** for sensitive environments

### Token Management
```python
# Example: Secure token storage and refresh
import jwt
from datetime import datetime, timedelta
import redis

# Token storage in Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def store_token(user_id, access_token, refresh_token, expires_in):
    """Store tokens securely"""
    redis_client.setex(
        f"access_token:{user_id}",
        expires_in,
        access_token
    )
    redis_client.setex(
        f"refresh_token:{user_id}",
        expires_in * 2,  # Refresh token lives longer
        refresh_token
    )

def get_token(user_id):
    """Retrieve valid token or refresh"""
    access_token = redis_client.get(f"access_token:{user_id}")

    if access_token:
        return access_token.decode()

    # Token expired, try to refresh
    refresh_token = redis_client.get(f"refresh_token:{user_id}")
    if refresh_token:
        new_tokens = refresh_access_token(refresh_token.decode())
        store_token(user_id, **new_tokens)
        return new_tokens['access_token']

    # Need to re-authenticate
    return None
```

### Certificate Management
```bash
# Generate self-signed cert for testing (DO NOT use in production)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout private.key -out certificate.crt

# Generate CSR for production CA
openssl req -new -newkey rsa:2048 -nodes \
  -keyout private.key -out request.csr

# Verify certificate
openssl x509 -in certificate.crt -text -noout

# Check certificate expiration
openssl x509 -enddate -noout -in certificate.crt
```

### Monitoring Authentication
```python
# Example: Authentication monitoring
import logging
from datetime import datetime

logger = logging.getLogger('auth_monitor')

def log_auth_event(event_type, user_id, success, ip_address, details=None):
    """Log authentication events for monitoring"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,  # login, logout, token_refresh, etc.
        'user_id': user_id,
        'success': success,
        'ip_address': ip_address,
        'details': details or {}
    }

    if success:
        logger.info(f"Auth success: {log_entry}")
    else:
        logger.warning(f"Auth failure: {log_entry}")

    # Send to SIEM or monitoring system
    send_to_siem(log_entry)

# Usage
log_auth_event('login', 'user@company.com', True, '192.168.1.100')
```

## Compliance Considerations

### SAML Assertion Requirements
- NameID format (email recommended)
- Required attributes: email, first name, last name
- Optional: groups, custom attributes
- Assertion encryption (recommended for sensitive data)
- Assertion signing (required)

### GDPR/Privacy
- Token expiration policies
- User consent for embedded analytics
- Data retention for auth logs
- Right to be forgotten (token revocation)

### SOC 2 / ISO 27001
- Regular access reviews
- Privileged access monitoring
- Failed authentication alerting
- Session management policies

## Troubleshooting

### Common SAML Issues
```bash
# Verify SAML response
echo "<SAML_RESPONSE>" | base64 -d | xmllint --format -

# Common errors:
# 1. Clock skew - sync NTP
# 2. Certificate mismatch - verify thumbprint
# 3. Missing attributes - check attribute mapping
# 4. Audience mismatch - verify entity ID
```

### OAuth Debugging
```python
# Enable detailed OAuth logging
import logging
logging.basicConfig(level=logging.DEBUG)

oauth_logger = logging.getLogger('oauthlib')
oauth_logger.setLevel(logging.DEBUG)
oauth_logger.addHandler(logging.StreamHandler())
```

## Resources
- OAuth 2.0 RFC: https://tools.ietf.org/html/rfc6749
- SAML 2.0 Spec: http://docs.oasis-open.org/security/saml/v2.0/
- OpenID Connect: https://openid.net/connect/
