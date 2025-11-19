# Embedded Analytics API Integration Guide

## Table of Contents

1. [Overview](#overview)
2. [Dashboard Embedding Methods](#dashboard-embedding-methods)
3. [Single Sign-On (SSO) Integration](#single-sign-on-sso-integration)
4. [Row-Level Security (RLS)](#row-level-security-rls)
5. [White-Labeling Approaches](#white-labeling-approaches)
6. [Multi-Tenant Patterns](#multi-tenant-patterns)
7. [Best Practices](#best-practices)

---

## Overview

Embedded analytics enables integrating BI dashboards and reports directly into applications. This guide covers secure embedding patterns, authentication, data security, and customization techniques.

**Key Integration Scenarios:**
- Customer-facing analytics portals
- Internal application dashboards
- Partner reporting interfaces
- White-labeled analytics products
- Multi-tenant SaaS analytics

**Security Requirements:**
- Secure authentication (SSO, JWT)
- Row-level data security
- Session management
- CORS configuration
- XSS prevention

---

## Dashboard Embedding Methods

### Method 1: iframe Embedding

The simplest approach using iframes with signed URLs.

**Tableau Trusted Ticket Embedding:**

```python
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

class TableauTrustedAuth:
    def __init__(self, server_url, username):
        """
        Initialize Tableau trusted authentication

        server_url: Tableau Server URL
        username: Tableau username for impersonation
        """
        self.server_url = server_url.rstrip('/')
        self.username = username

    def get_trusted_ticket(self, client_ip: str = None) -> str:
        """
        Get trusted ticket for embedding

        client_ip: Client IP address for additional security
        """
        url = f"{self.server_url}/trusted"

        data = {
            'username': self.username
        }

        if client_ip:
            data['client_ip'] = client_ip

        try:
            response = requests.post(url, data=data)
            ticket = response.text.strip()

            if ticket == '-1':
                raise Exception("Trusted authentication failed. Check Tableau Server config.")

            return ticket

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get trusted ticket: {str(e)}")

    def get_embed_url(self, workbook_path: str, view_name: str,
                     filters: dict = None, client_ip: str = None) -> str:
        """
        Generate embed URL with trusted ticket

        workbook_path: Path to workbook (e.g., 'site_name/workbook_name')
        view_name: Name of the view/dashboard
        filters: Dictionary of filters to apply
        """
        ticket = self.get_trusted_ticket(client_ip)

        # Construct base URL
        embed_url = f"{self.server_url}/trusted/{ticket}/views/{workbook_path}/{view_name}"

        # Add filters if provided
        if filters:
            filter_params = '&'.join([f"{k}={quote(str(v))}" for k, v in filters.items()])
            embed_url += f"?{filter_params}"

        # Add embedding parameters
        embed_params = ':embed=yes&:toolbar=no&:tabs=no'
        embed_url += f"{'&' if filters else '?'}{embed_params}"

        return embed_url

# Usage in Flask application
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = 'your-secret-key'

@app.route('/dashboard')
def embedded_dashboard():
    """Serve embedded dashboard"""
    # Get user context
    user_email = session.get('user_email')
    user_region = session.get('user_region')

    # Generate embed URL
    tableau_auth = TableauTrustedAuth(
        server_url='https://tableau.company.com',
        username=user_email
    )

    embed_url = tableau_auth.get_embed_url(
        workbook_path='Sales/RegionalDashboard',
        view_name='Overview',
        filters={'Region': user_region},
        client_ip=request.remote_addr
    )

    return render_template('dashboard.html', embed_url=embed_url)

# HTML template (dashboard.html)
"""
<!DOCTYPE html>
<html>
<head>
    <title>Analytics Dashboard</title>
    <style>
        body { margin: 0; padding: 0; }
        #dashboard-container {
            width: 100%;
            height: 100vh;
            border: none;
        }
    </style>
</head>
<body>
    <iframe
        id="dashboard-container"
        src="{{ embed_url }}"
        frameborder="0"
        allowfullscreen>
    </iframe>
</body>
</html>
"""
```

**Power BI Embed Token Method:**

```python
import requests
import msal
from datetime import datetime, timedelta

class PowerBIEmbedding:
    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def authenticate(self):
        """Authenticate and get access token"""
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        scope = ["https://analysis.windows.net/powerbi/api/.default"]

        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )

        result = app.acquire_token_for_client(scopes=scope)

        if "access_token" in result:
            self.access_token = result['access_token']
            return self.access_token
        else:
            raise Exception(f"Authentication failed: {result.get('error_description')}")

    def get_embed_token(self, workspace_id: str, report_id: str,
                       datasets: list, username: str = None,
                       roles: list = None) -> dict:
        """
        Generate embed token for a report

        workspace_id: Power BI workspace ID
        report_id: Report ID to embed
        datasets: List of dataset IDs
        username: User identity for RLS
        roles: RLS roles to apply
        """
        url = "https://api.powerbi.com/v1.0/myorg/GenerateToken"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Build request payload
        payload = {
            'datasets': [{'id': ds_id} for ds_id in datasets],
            'reports': [{'id': report_id}],
            'targetWorkspaces': [{'id': workspace_id}]
        }

        # Add RLS identity if provided
        if username and roles:
            payload['identities'] = [{
                'username': username,
                'roles': roles,
                'datasets': datasets
            }]

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()

            return {
                'token': data.get('token'),
                'token_id': data.get('tokenId'),
                'expiration': data.get('expiration')
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to generate embed token: {str(e)}")

    def get_embed_config(self, workspace_id: str, report_id: str,
                        dataset_ids: list, username: str = None,
                        roles: list = None) -> dict:
        """Get complete embed configuration"""
        # Get embed token
        embed_token = self.get_embed_token(
            workspace_id, report_id, dataset_ids, username, roles
        )

        # Get report details
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}"

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        report = response.json()

        return {
            'type': 'report',
            'id': report_id,
            'embedUrl': report.get('embedUrl'),
            'accessToken': embed_token['token'],
            'tokenExpiration': embed_token['expiration'],
            'permissions': 'All'  # or 'View'
        }

# Flask route for Power BI embedding
@app.route('/powerbi-dashboard')
def powerbi_dashboard():
    pbi = PowerBIEmbedding(
        tenant_id='your-tenant-id',
        client_id='your-client-id',
        client_secret='your-client-secret'
    )

    pbi.authenticate()

    # Get embed config with RLS
    embed_config = pbi.get_embed_config(
        workspace_id='workspace-id',
        report_id='report-id',
        dataset_ids=['dataset-id'],
        username=session.get('user_email'),
        roles=['SalesUser']  # RLS role
    )

    return render_template('powerbi_embed.html', config=embed_config)

# HTML template (powerbi_embed.html)
"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/powerbi-client@2.22.0/dist/powerbi.min.js"></script>
    <style>
        #report-container {
            height: 100vh;
            width: 100%;
        }
    </style>
</head>
<body>
    <div id="report-container"></div>

    <script>
        const embedConfig = {
            type: '{{ config.type }}',
            id: '{{ config.id }}',
            embedUrl: '{{ config.embedUrl }}',
            accessToken: '{{ config.accessToken }}',
            tokenType: models.TokenType.Embed,
            permissions: models.Permissions.All,
            settings: {
                panes: {
                    filters: { visible: false },
                    pageNavigation: { visible: true }
                },
                background: models.BackgroundType.Transparent
            }
        };

        const reportContainer = document.getElementById('report-container');
        const powerbi = new pbi.service.Service(
            pbi.factories.hpmFactory,
            pbi.factories.wpmpFactory,
            pbi.factories.routerFactory
        );

        const report = powerbi.embed(reportContainer, embedConfig);

        report.on('loaded', function() {
            console.log('Report loaded successfully');
        });

        report.on('error', function(event) {
            console.error('Report error:', event.detail);
        });
    </script>
</body>
</html>
"""
```

### Method 2: JavaScript SDK Embedding

More control and interactivity using vendor SDKs.

**Looker SDK Embedding:**

```javascript
// Node.js backend - Generate signed embed URL
const crypto = require('crypto');

class LookerEmbedding {
    constructor(embedSecret, lookerHost) {
        this.embedSecret = embedSecret;
        this.lookerHost = lookerHost;
    }

    generateEmbedUrl(dashboardId, userId, userAttributes = {}, filters = {}) {
        const embedPath = `/embed/dashboards/${dashboardId}`;

        // Build parameters
        const params = {
            nonce: this.generateNonce(),
            time: Math.floor(Date.now() / 1000),
            session_length: 3600,  // 1 hour
            external_user_id: userId,
            permissions: JSON.stringify(['access_data', 'see_lookml_dashboards']),
            models: JSON.stringify(['sales', 'marketing']),
            group_ids: JSON.stringify([1, 2]),
            external_group_id: 'external_group',
            user_attributes: JSON.stringify(userAttributes),
            access_filters: JSON.stringify(filters),
            force_logout_login: true
        };

        // Generate signature
        const paramsString = Object.keys(params)
            .sort()
            .map(key => `${key}=${encodeURIComponent(params[key])}`)
            .join('&');

        const signature = crypto
            .createHmac('sha1', this.embedSecret)
            .update(`${this.lookerHost}${embedPath}?${paramsString}`)
            .digest('base64')
            .trim();

        // Build final URL
        const embedUrl = `${this.lookerHost}${embedPath}?${paramsString}&signature=${encodeURIComponent(signature)}`;

        return embedUrl;
    }

    generateNonce() {
        return crypto.randomBytes(16).toString('hex');
    }
}

// Express.js route
const express = require('express');
const app = express();

app.get('/api/embed/looker-dashboard', (req, res) => {
    const looker = new LookerEmbedding(
        process.env.LOOKER_EMBED_SECRET,
        'https://company.looker.com'
    );

    const embedUrl = looker.generateEmbedUrl(
        dashboardId: '123',
        userId: req.user.email,
        userAttributes: {
            department: req.user.department,
            region: req.user.region
        },
        filters: {
            'sales.region': req.user.region
        }
    );

    res.json({ embedUrl });
});

// Frontend - React component
/*
import React, { useEffect, useState } from 'react';
import { LookerEmbedSDK } from '@looker/embed-sdk';

function LookerDashboard() {
    const [dashboard, setDashboard] = useState(null);

    useEffect(() => {
        // Initialize SDK
        LookerEmbedSDK.init('company.looker.com');

        // Create dashboard
        LookerEmbedSDK.createDashboardWithUrl('/api/embed/looker-dashboard')
            .appendTo('#looker-dashboard')
            .withParams({
                theme: 'custom_theme'
            })
            .on('dashboard:loaded', () => {
                console.log('Dashboard loaded');
            })
            .on('dashboard:run:start', () => {
                console.log('Query started');
            })
            .on('dashboard:run:complete', () => {
                console.log('Query completed');
            })
            .build()
            .connect()
            .then(dash => {
                setDashboard(dash);
            })
            .catch(error => {
                console.error('Embed error:', error);
            });

        return () => {
            if (dashboard) {
                dashboard.remove();
            }
        };
    }, []);

    return (
        <div id="looker-dashboard" style={{ width: '100%', height: '800px' }} />
    );
}

export default LookerDashboard;
*/
```

---

## Single Sign-On (SSO) Integration

### SAML-based SSO

**Tableau SAML Configuration:**

```python
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from flask import Flask, request, redirect, session

app = Flask(__name__)

def init_saml_auth(req):
    """Initialize SAML authentication"""
    saml_settings = {
        'sp': {
            'entityId': 'https://your-app.com/saml/metadata',
            'assertionConsumerService': {
                'url': 'https://your-app.com/saml/acs',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
            },
            'singleLogoutService': {
                'url': 'https://your-app.com/saml/sls',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
            'x509cert': '',  # Your SP certificate
            'privateKey': ''  # Your SP private key
        },
        'idp': {
            'entityId': 'https://tableau.company.com',
            'singleSignOnService': {
                'url': 'https://tableau.company.com/auth/saml/login',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'x509cert': ''  # Tableau IdP certificate
        }
    }

    auth = OneLogin_Saml2_Auth(req, saml_settings)
    return auth

@app.route('/saml/login')
def saml_login():
    """Initiate SAML SSO login"""
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)

    return redirect(auth.login())

@app.route('/saml/acs', methods=['POST'])
def saml_acs():
    """SAML Assertion Consumer Service"""
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)

    auth.process_response()

    errors = auth.get_errors()

    if not errors:
        # Successfully authenticated
        session['samlUserdata'] = auth.get_attributes()
        session['samlNameId'] = auth.get_nameid()

        # Redirect to embedded dashboard
        return redirect('/dashboard')
    else:
        return f"SAML Error: {', '.join(errors)}", 401

def prepare_flask_request(request):
    """Prepare Flask request for python-saml"""
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': request.environ.get('SERVER_PORT'),
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy()
    }
```

### JWT-based SSO

**Custom JWT Authentication for Embedding:**

```python
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

SECRET_KEY = 'your-jwt-secret-key'

def generate_embed_token(user_id: str, email: str, permissions: list,
                        attributes: dict, expires_in: int = 3600) -> str:
    """
    Generate JWT token for embedded analytics

    user_id: Unique user identifier
    email: User email
    permissions: List of permissions
    attributes: Custom user attributes for RLS
    expires_in: Token expiration in seconds
    """
    payload = {
        'sub': user_id,
        'email': email,
        'permissions': permissions,
        'attributes': attributes,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_embed_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

@app.route('/api/embed-token', methods=['POST'])
def get_embed_token():
    """Generate embed token for authenticated user"""
    # Verify user session
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user = get_user_from_session(session)

    # Generate token with user context
    token = generate_embed_token(
        user_id=user['id'],
        email=user['email'],
        permissions=['view_dashboards', 'export_data'],
        attributes={
            'department': user['department'],
            'region': user['region'],
            'role': user['role']
        },
        expires_in=3600
    )

    return jsonify({
        'token': token,
        'expiresAt': (datetime.utcnow() + timedelta(seconds=3600)).isoformat()
    })

# Middleware to verify embed token
@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Protected endpoint requiring embed token"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401

    token = auth_header.split(' ')[1]

    try:
        payload = verify_embed_token(token)

        # Use payload attributes for RLS
        region = payload['attributes']['region']
        department = payload['attributes']['department']

        # Fetch data with filters
        data = fetch_dashboard_data(region=region, department=department)

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 401
```

---

## Row-Level Security (RLS)

### Dynamic RLS with User Attributes

**Tableau User Filtering:**

```python
class TableauRLS:
    def __init__(self, tableau_api):
        self.api = tableau_api

    def apply_user_filter(self, workbook_id: str, user_email: str,
                         filter_field: str, filter_value: str):
        """
        Apply user-specific filter via custom SQL

        Creates a user filter in Tableau data source
        """
        # Custom SQL approach
        custom_sql = f"""
        SELECT *
        FROM sales_data
        WHERE {filter_field} = (
            SELECT attribute_value
            FROM user_attributes
            WHERE user_email = CURRENT_USER()
            AND attribute_name = '{filter_field}'
        )
        """

        return custom_sql

    def set_user_attribute(self, user_id: str, attribute_name: str,
                          attribute_value: str):
        """Store user attribute for RLS"""
        # Store in application database
        db.execute("""
            INSERT INTO user_attributes (user_id, attribute_name, attribute_value)
            VALUES (?, ?, ?)
            ON CONFLICT (user_id, attribute_name)
            DO UPDATE SET attribute_value = ?
        """, (user_id, attribute_name, attribute_value, attribute_value))

# Usage
rls = TableauRLS(tableau_api)
rls.set_user_attribute(
    user_id='user123',
    attribute_name='region',
    attribute_value='West'
)
```

**Power BI RLS via Embed Token:**

```python
def apply_powerbi_rls(workspace_id: str, report_id: str, dataset_id: str,
                     user_email: str, user_region: str, user_department: str):
    """
    Apply RLS through embed token generation

    Assumes RLS roles are defined in Power BI dataset
    """
    pbi = PowerBIEmbedding(tenant_id, client_id, client_secret)
    pbi.authenticate()

    # Define effective identity for RLS
    embed_config = pbi.get_embed_token(
        workspace_id=workspace_id,
        report_id=report_id,
        datasets=[dataset_id],
        username=user_email,
        roles=['RegionalManager', 'DepartmentHead']
    )

    return embed_config

# The Power BI dataset should have DAX RLS rules like:
"""
-- Region RLS rule
[Region] = USERPRINCIPALNAME()

-- Or using custom attributes
[Region] = LOOKUPVALUE(
    UserAttributes[Region],
    UserAttributes[Email],
    USERPRINCIPALNAME()
)
"""
```

### Multi-Tenant RLS Pattern

```python
class MultiTenantRLS:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_user_data_scope(self, user_id: str) -> dict:
        """Get user's data access scope"""
        query = """
        SELECT
            u.tenant_id,
            u.role,
            t.data_isolation_level,
            ua.region,
            ua.department
        FROM users u
        JOIN tenants t ON u.tenant_id = t.id
        LEFT JOIN user_attributes ua ON u.id = ua.user_id
        WHERE u.id = ?
        """

        result = self.db.execute(query, (user_id,)).fetchone()

        return {
            'tenant_id': result['tenant_id'],
            'role': result['role'],
            'isolation_level': result['data_isolation_level'],
            'region': result['region'],
            'department': result['department']
        }

    def build_data_filter(self, user_scope: dict) -> str:
        """Build SQL filter based on user scope"""
        filters = []

        # Always filter by tenant
        filters.append(f"tenant_id = '{user_scope['tenant_id']}'")

        # Add additional filters based on isolation level
        if user_scope['isolation_level'] == 'region':
            filters.append(f"region = '{user_scope['region']}'")

        if user_scope['isolation_level'] == 'department':
            filters.append(f"department = '{user_scope['department']}'")

        return ' AND '.join(filters)

    def get_filtered_embed_url(self, user_id: str, dashboard_id: str) -> str:
        """Generate embed URL with RLS filters"""
        user_scope = self.get_user_data_scope(user_id)
        data_filter = self.build_data_filter(user_scope)

        # Apply to embed URL
        embed_url = f"https://analytics.company.com/embed/{dashboard_id}"
        embed_url += f"?filter={data_filter}"

        return embed_url

# Usage
rls = MultiTenantRLS(db_connection)
embed_url = rls.get_filtered_embed_url(user_id='user123', dashboard_id='sales-dashboard')
```

---

## White-Labeling Approaches

### Custom Branding and Theming

**CSS Customization for Embedded Dashboards:**

```css
/* Custom theme for embedded analytics */
:root {
    --brand-primary: #0066cc;
    --brand-secondary: #00cc66;
    --brand-background: #f5f5f5;
    --brand-text: #333333;
    --brand-border: #e0e0e0;
}

/* Override BI tool default styles */
.tableau-viz {
    font-family: 'Your Brand Font', sans-serif !important;
}

/* Hide vendor branding */
.tableau-logo,
.powerbi-logo {
    display: none !important;
}

/* Custom toolbar */
.custom-toolbar {
    background-color: var(--brand-primary);
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.custom-toolbar .logo {
    height: 40px;
}

.custom-toolbar .actions button {
    background-color: var(--brand-secondary);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

/* Custom filters panel */
.filters-panel {
    background: white;
    border: 1px solid var(--brand-border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.filter-group {
    margin-bottom: 16px;
}

.filter-group label {
    color: var(--brand-text);
    font-weight: 600;
    display: block;
    margin-bottom: 8px;
}

.filter-group select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--brand-border);
    border-radius: 4px;
    font-size: 14px;
}
```

**White-Label Embedding Component:**

```javascript
// React component for white-labeled analytics
import React, { useEffect, useState } from 'react';
import './WhiteLabelAnalytics.css';

function WhiteLabelAnalytics({ userId, dashboardId, brandConfig }) {
    const [embedUrl, setEmbedUrl] = useState(null);
    const [filters, setFilters] = useState({});

    useEffect(() => {
        // Fetch embed URL from backend
        fetch('/api/embed-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId, dashboardId })
        })
        .then(res => res.json())
        .then(data => setEmbedUrl(data.embedUrl));
    }, [userId, dashboardId]);

    const applyFilter = (filterName, value) => {
        const updatedFilters = { ...filters, [filterName]: value };
        setFilters(updatedFilters);

        // Update embed URL with filters
        const filterParams = Object.entries(updatedFilters)
            .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
            .join('&');

        setEmbedUrl(`${embedUrl.split('?')[0]}?${filterParams}`);
    };

    return (
        <div className="white-label-analytics">
            {/* Custom branded toolbar */}
            <div className="custom-toolbar" style={{
                backgroundColor: brandConfig.primaryColor
            }}>
                <img src={brandConfig.logoUrl} alt="Logo" className="logo" />
                <div className="actions">
                    <button onClick={() => window.print()}>
                        Export PDF
                    </button>
                    <button onClick={() => downloadData()}>
                        Download Data
                    </button>
                </div>
            </div>

            {/* Custom filters */}
            <div className="filters-panel">
                <div className="filter-group">
                    <label>Date Range</label>
                    <select onChange={(e) => applyFilter('dateRange', e.target.value)}>
                        <option value="last30days">Last 30 Days</option>
                        <option value="last90days">Last 90 Days</option>
                        <option value="ytd">Year to Date</option>
                    </select>
                </div>
                <div className="filter-group">
                    <label>Region</label>
                    <select onChange={(e) => applyFilter('region', e.target.value)}>
                        <option value="">All Regions</option>
                        <option value="north">North</option>
                        <option value="south">South</option>
                        <option value="east">East</option>
                        <option value="west">West</option>
                    </select>
                </div>
            </div>

            {/* Embedded dashboard */}
            {embedUrl && (
                <iframe
                    src={embedUrl}
                    className="dashboard-iframe"
                    style={{
                        width: '100%',
                        height: 'calc(100vh - 200px)',
                        border: `1px solid ${brandConfig.borderColor}`,
                        borderRadius: '8px'
                    }}
                />
            )}
        </div>
    );
}

export default WhiteLabelAnalytics;
```

---

## Multi-Tenant Patterns

### Tenant Isolation Architecture

```python
class MultiTenantEmbedding:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_tenant_config(self, tenant_id: str) -> dict:
        """Get tenant-specific configuration"""
        query = """
        SELECT
            tenant_id,
            data_source_id,
            schema_name,
            dashboard_template_id,
            custom_domain,
            branding_config
        FROM tenant_configs
        WHERE tenant_id = ?
        """

        result = self.db.execute(query, (tenant_id,)).fetchone()

        return {
            'tenant_id': result['tenant_id'],
            'data_source_id': result['data_source_id'],
            'schema': result['schema_name'],
            'dashboard_template': result['dashboard_template_id'],
            'domain': result['custom_domain'],
            'branding': json.loads(result['branding_config'])
        }

    def provision_tenant_analytics(self, tenant_id: str, config: dict):
        """Provision analytics resources for new tenant"""
        steps = []

        # 1. Create dedicated schema in data warehouse
        schema_name = f"tenant_{tenant_id}"
        self.create_tenant_schema(schema_name)
        steps.append(f"Created schema: {schema_name}")

        # 2. Clone dashboard template
        dashboard_id = self.clone_dashboard_for_tenant(
            template_id=config['dashboard_template'],
            tenant_id=tenant_id,
            schema=schema_name
        )
        steps.append(f"Created dashboard: {dashboard_id}")

        # 3. Configure data source connection
        self.configure_tenant_datasource(
            tenant_id=tenant_id,
            schema=schema_name
        )
        steps.append("Configured data source")

        # 4. Set up RLS rules
        self.configure_tenant_rls(tenant_id, schema_name)
        steps.append("Configured RLS")

        # 5. Apply branding
        self.apply_tenant_branding(tenant_id, config.get('branding', {}))
        steps.append("Applied branding")

        return {
            'tenant_id': tenant_id,
            'dashboard_id': dashboard_id,
            'schema': schema_name,
            'steps_completed': steps
        }

    def create_tenant_schema(self, schema_name: str):
        """Create isolated schema for tenant"""
        # For Snowflake
        query = f"""
        CREATE SCHEMA IF NOT EXISTS {schema_name};
        GRANT USAGE ON SCHEMA {schema_name} TO ROLE tenant_role;
        """

        self.db.execute(query)

    def clone_dashboard_for_tenant(self, template_id: str, tenant_id: str,
                                   schema: str) -> str:
        """Clone dashboard template and update data source"""
        # Implementation depends on BI tool API
        # Example for Tableau
        tableau_api.copy_workbook(
            source_workbook_id=template_id,
            destination_project_id=f"tenant_{tenant_id}_project",
            new_name=f"Dashboard - Tenant {tenant_id}"
        )

        # Update data source connection to use tenant schema
        tableau_api.update_datasource_connection(
            workbook_id=new_workbook_id,
            schema=schema
        )

        return new_workbook_id

    def configure_tenant_rls(self, tenant_id: str, schema: str):
        """Configure row-level security for tenant"""
        # Create user attribute mapping
        query = """
        INSERT INTO user_tenant_mapping (user_id, tenant_id, schema_name)
        SELECT user_id, ?, ?
        FROM users
        WHERE tenant_id = ?
        """

        self.db.execute(query, (tenant_id, schema, tenant_id))

# Usage
multi_tenant = MultiTenantEmbedding(db_connection)

# Provision new tenant
result = multi_tenant.provision_tenant_analytics(
    tenant_id='tenant_abc123',
    config={
        'dashboard_template': 'default_template',
        'branding': {
            'primary_color': '#0066cc',
            'logo_url': 'https://cdn.example.com/tenant-logo.png'
        }
    }
)

print(f"Tenant provisioned: {result}")
```

### Tenant Data Segregation

```python
def enforce_tenant_isolation(user_id: str, query: str) -> str:
    """
    Enforce tenant isolation by modifying queries

    Automatically adds tenant filter to all queries
    """
    # Get user's tenant
    user = get_user(user_id)
    tenant_id = user['tenant_id']

    # Parse and modify query
    # Simple approach: Add WHERE clause
    if 'WHERE' in query.upper():
        modified_query = query.replace(
            'WHERE',
            f"WHERE tenant_id = '{tenant_id}' AND"
        )
    else:
        # Add WHERE clause before ORDER BY, GROUP BY, etc.
        keywords = ['ORDER BY', 'GROUP BY', 'LIMIT', 'OFFSET']
        insert_position = len(query)

        for keyword in keywords:
            pos = query.upper().find(keyword)
            if pos != -1 and pos < insert_position:
                insert_position = pos

        modified_query = (
            query[:insert_position] +
            f" WHERE tenant_id = '{tenant_id}' " +
            query[insert_position:]
        )

    return modified_query

# Database proxy middleware
class TenantIsolationProxy:
    def __init__(self, db_connection):
        self.db = db_connection

    def execute_query(self, user_id: str, query: str):
        """Execute query with automatic tenant isolation"""
        # Enforce tenant filter
        safe_query = enforce_tenant_isolation(user_id, query)

        # Log query for auditing
        self.audit_log(user_id, safe_query)

        # Execute
        return self.db.execute(safe_query)

    def audit_log(self, user_id: str, query: str):
        """Log query execution for compliance"""
        self.db.execute("""
            INSERT INTO query_audit_log (user_id, query, executed_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (user_id, query))
```

---

## Best Practices

### 1. Security Checklist

```python
class EmbeddingSecurityValidator:
    @staticmethod
    def validate_embed_request(request_data: dict) -> dict:
        """Validate embedding security requirements"""
        checks = {
            'https_only': False,
            'valid_session': False,
            'csrf_token': False,
            'rate_limit': False,
            'authorized_domain': False
        }

        # Check HTTPS
        checks['https_only'] = request_data.get('protocol') == 'https'

        # Validate session
        checks['valid_session'] = validate_session(request_data.get('session_id'))

        # CSRF protection
        checks['csrf_token'] = validate_csrf_token(
            request_data.get('csrf_token'),
            request_data.get('session_id')
        )

        # Rate limiting
        checks['rate_limit'] = check_rate_limit(request_data.get('user_id'))

        # Domain whitelist
        checks['authorized_domain'] = request_data.get('origin') in [
            'https://app.company.com',
            'https://portal.company.com'
        ]

        all_passed = all(checks.values())

        return {
            'valid': all_passed,
            'checks': checks
        }
```

### 2. Performance Optimization

```javascript
// Lazy loading for embedded dashboards
class LazyDashboardLoader {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.observer = null;
        this.loaded = false;
    }

    init(embedUrl) {
        // Use Intersection Observer for lazy loading
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.loaded) {
                    this.loadDashboard(embedUrl);
                    this.loaded = true;
                }
            });
        }, {
            rootMargin: '50px'
        });

        this.observer.observe(this.container);
    }

    loadDashboard(embedUrl) {
        const iframe = document.createElement('iframe');
        iframe.src = embedUrl;
        iframe.width = '100%';
        iframe.height = '600px';
        iframe.frameBorder = '0';

        this.container.appendChild(iframe);
    }
}

// Usage
const loader = new LazyDashboardLoader('dashboard-container');
loader.init('/api/embed-url');
```

### 3. Error Handling

```python
class EmbeddingErrorHandler:
    @staticmethod
    def handle_embed_error(error_type: str, context: dict) -> dict:
        """Centralized error handling for embedding"""
        error_responses = {
            'authentication_failed': {
                'status': 401,
                'message': 'Authentication failed. Please log in again.',
                'action': 'redirect_to_login'
            },
            'authorization_failed': {
                'status': 403,
                'message': 'You do not have permission to view this dashboard.',
                'action': 'show_error_page'
            },
            'token_expired': {
                'status': 401,
                'message': 'Your session has expired.',
                'action': 'refresh_token'
            },
            'dashboard_not_found': {
                'status': 404,
                'message': 'Dashboard not found.',
                'action': 'show_404'
            },
            'rate_limit_exceeded': {
                'status': 429,
                'message': 'Too many requests. Please try again later.',
                'action': 'show_rate_limit_error'
            }
        }

        response = error_responses.get(error_type, {
            'status': 500,
            'message': 'An unexpected error occurred.',
            'action': 'show_error_page'
        })

        # Log error
        log_error(error_type, context, response)

        return response
```

---

## Summary

This guide covers comprehensive patterns for embedded analytics:

- **Embedding Methods**: iframe vs SDK approaches for Tableau, Power BI, and Looker
- **SSO Integration**: SAML and JWT-based authentication patterns
- **Row-Level Security**: Dynamic filtering and multi-tenant data isolation
- **White-Labeling**: Custom branding and theming techniques
- **Multi-Tenancy**: Tenant provisioning and data segregation patterns

**Key Takeaways:**
1. Always use HTTPS and secure authentication (SSO, JWT)
2. Implement proper RLS to ensure data security
3. Use CSP headers and CORS configuration
4. Apply rate limiting to prevent abuse
5. Lazy load dashboards for better performance
6. Provide white-labeling for customer-facing analytics
7. Implement comprehensive error handling and logging
8. Use token expiration and refresh mechanisms
9. Audit all embedded analytics access
10. Test across browsers and devices

For platform-specific documentation:
- Tableau: https://help.tableau.com/current/api/embedding_api/en-us/
- Power BI: https://learn.microsoft.com/en-us/power-bi/developer/embedded/
- Looker: https://cloud.google.com/looker/docs/r/sdk/sso-embed
