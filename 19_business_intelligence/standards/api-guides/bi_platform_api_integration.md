# Business Intelligence Platform API Integration Guide

## Table of Contents

1. [Overview](#overview)
2. [Tableau APIs](#tableau-apis)
3. [Power BI APIs](#power-bi-apis)
4. [Looker API](#looker-api)
5. [Metabase API](#metabase-api)
6. [Authentication Patterns](#authentication-patterns)
7. [Rate Limiting and Pagination](#rate-limiting-and-pagination)
8. [Automation Use Cases](#automation-use-cases)
9. [Best Practices](#best-practices)

---

## Overview

This guide provides comprehensive patterns for integrating with major Business Intelligence platforms through their APIs. Each platform offers different capabilities, authentication methods, and use cases for automation.

**Key Integration Scenarios:**
- Automated content deployment
- User and permission management
- Data refresh orchestration
- Metadata extraction
- Custom embedding
- Monitoring and alerting

---

## Tableau APIs

Tableau provides three primary API surfaces for different integration needs.

### Tableau REST API

The REST API enables programmatic management of Tableau Server/Cloud resources.

**Core Capabilities:**
- Workbook and datasource management
- User and group administration
- Site configuration
- Extract refresh scheduling
- Permissions management

**Authentication - Personal Access Token (PAT):**

```python
import requests
import xml.etree.ElementTree as ET

class TableauAPI:
    def __init__(self, server_url, api_version='3.19'):
        self.server_url = server_url
        self.api_version = api_version
        self.base_url = f"{server_url}/api/{api_version}"
        self.auth_token = None
        self.site_id = None

    def sign_in_pat(self, token_name, token_secret, site_content_url=''):
        """Authenticate using Personal Access Token"""
        url = f"{self.base_url}/auth/signin"

        payload = f"""
        <tsRequest>
            <credentials personalAccessTokenName="{token_name}"
                        personalAccessTokenSecret="{token_secret}">
                <site contentUrl="{site_content_url}" />
            </credentials>
        </tsRequest>
        """

        try:
            response = requests.post(url, data=payload, headers={
                'Content-Type': 'application/xml',
                'Accept': 'application/xml'
            })
            response.raise_for_status()

            root = ET.fromstring(response.content)
            self.auth_token = root.find('.//t:credentials',
                                       {'t': 'http://tableau.com/api'}).get('token')
            self.site_id = root.find('.//t:site',
                                    {'t': 'http://tableau.com/api'}).get('id')

            return self.auth_token

        except requests.exceptions.RequestException as e:
            raise Exception(f"Authentication failed: {str(e)}")

    def _get_headers(self):
        """Get authenticated request headers"""
        if not self.auth_token:
            raise Exception("Not authenticated. Call sign_in_pat first.")
        return {
            'X-Tableau-Auth': self.auth_token,
            'Content-Type': 'application/xml',
            'Accept': 'application/xml'
        }

    def list_workbooks(self, page_size=100, page_number=1):
        """List workbooks with pagination"""
        url = f"{self.base_url}/sites/{self.site_id}/workbooks"
        params = {
            'pageSize': page_size,
            'pageNumber': page_number
        }

        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            workbooks = []

            for wb in root.findall('.//t:workbook', {'t': 'http://tableau.com/api'}):
                workbooks.append({
                    'id': wb.get('id'),
                    'name': wb.get('name'),
                    'contentUrl': wb.get('contentUrl'),
                    'createdAt': wb.get('createdAt'),
                    'updatedAt': wb.get('updatedAt')
                })

            pagination = root.find('.//t:pagination', {'t': 'http://tableau.com/api'})
            total_available = int(pagination.get('totalAvailable', 0))

            return {
                'workbooks': workbooks,
                'total': total_available,
                'page_size': page_size,
                'page_number': page_number
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to list workbooks: {str(e)}")

    def refresh_extract(self, datasource_id):
        """Trigger an extract refresh"""
        url = f"{self.base_url}/sites/{self.site_id}/datasources/{datasource_id}/refresh"

        payload = "<tsRequest></tsRequest>"

        try:
            response = requests.post(url, data=payload, headers=self._get_headers())
            response.raise_for_status()

            root = ET.fromstring(response.content)
            job = root.find('.//t:job', {'t': 'http://tableau.com/api'})

            return {
                'job_id': job.get('id'),
                'status': job.get('status'),
                'created_at': job.get('createdAt')
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Extract refresh failed: {str(e)}")

    def add_user_to_group(self, user_id, group_id):
        """Add a user to a group"""
        url = f"{self.base_url}/sites/{self.site_id}/groups/{group_id}/users"

        payload = f"""
        <tsRequest>
            <user id="{user_id}" />
        </tsRequest>
        """

        try:
            response = requests.post(url, data=payload, headers=self._get_headers())
            response.raise_for_status()
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                # User already in group
                return True
            raise Exception(f"Failed to add user to group: {str(e)}")

    def download_workbook(self, workbook_id, file_path):
        """Download workbook as .twbx file"""
        url = f"{self.base_url}/sites/{self.site_id}/workbooks/{workbook_id}/content"

        try:
            response = requests.get(url, headers=self._get_headers(), stream=True)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return file_path

        except requests.exceptions.RequestException as e:
            raise Exception(f"Workbook download failed: {str(e)}")

    def sign_out(self):
        """Sign out and invalidate token"""
        url = f"{self.base_url}/auth/signout"

        try:
            response = requests.post(url, headers=self._get_headers())
            response.raise_for_status()
            self.auth_token = None
            self.site_id = None

        except requests.exceptions.RequestException as e:
            print(f"Sign out warning: {str(e)}")

# Usage example
if __name__ == "__main__":
    api = TableauAPI('https://tableau.company.com')

    try:
        # Authenticate
        api.sign_in_pat('my_token_name', 'secret_token_value', 'my_site')

        # List workbooks
        result = api.list_workbooks(page_size=50)
        print(f"Found {result['total']} workbooks")

        # Refresh extract
        job = api.refresh_extract('datasource-id-here')
        print(f"Refresh job started: {job['job_id']}")

    finally:
        api.sign_out()
```

### Tableau Hyper API

The Hyper API enables creation and manipulation of Tableau extract files (.hyper).

```python
from tableauhyperapi import HyperProcess, Connection, TableDefinition, \
    SqlType, Inserter, CreateMode, TableName

def create_hyper_extract(data, output_path):
    """Create a Tableau Hyper extract from data"""

    # Define table schema
    schema = TableDefinition(
        table_name=TableName('Extract', 'Extract'),
        columns=[
            TableDefinition.Column('OrderID', SqlType.int()),
            TableDefinition.Column('OrderDate', SqlType.date()),
            TableDefinition.Column('CustomerName', SqlType.text()),
            TableDefinition.Column('Sales', SqlType.double()),
            TableDefinition.Column('Profit', SqlType.double()),
            TableDefinition.Column('Region', SqlType.text())
        ]
    )

    try:
        with HyperProcess(telemetry=HyperProcess.Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(endpoint=hyper.endpoint,
                          database=output_path,
                          create_mode=CreateMode.CREATE_AND_REPLACE) as connection:

                # Create table
                connection.catalog.create_table(schema)

                # Insert data
                with Inserter(connection, schema) as inserter:
                    for row in data:
                        inserter.add_row(row)
                    inserter.execute()

                print(f"Hyper extract created: {output_path}")
                print(f"Rows inserted: {len(data)}")

    except Exception as e:
        raise Exception(f"Hyper extract creation failed: {str(e)}")

# Usage
sample_data = [
    (1, '2024-01-15', 'Acme Corp', 1500.00, 450.00, 'West'),
    (2, '2024-01-16', 'Global Inc', 2300.00, 690.00, 'East'),
    (3, '2024-01-17', 'Tech Solutions', 1800.00, 540.00, 'Central')
]

create_hyper_extract(sample_data, 'sales_data.hyper')
```

---

## Power BI APIs

Power BI provides REST APIs and PowerShell cmdlets for programmatic access.

### Power BI REST API

**Authentication - Service Principal (OAuth 2.0):**

```python
import requests
import msal
from datetime import datetime, timedelta

class PowerBIAPI:
    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        self.access_token = None
        self.token_expiry = None

    def authenticate(self):
        """Authenticate using service principal"""
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        scope = ["https://analysis.windows.net/powerbi/api/.default"]

        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )

        try:
            result = app.acquire_token_for_client(scopes=scope)

            if "access_token" in result:
                self.access_token = result['access_token']
                # Tokens typically expire in 1 hour
                self.token_expiry = datetime.now() + timedelta(seconds=result.get('expires_in', 3600))
                return self.access_token
            else:
                raise Exception(f"Authentication failed: {result.get('error_description')}")

        except Exception as e:
            raise Exception(f"MSAL authentication error: {str(e)}")

    def _get_headers(self):
        """Get authenticated request headers with token refresh"""
        # Refresh token if expired or about to expire
        if not self.access_token or datetime.now() >= self.token_expiry - timedelta(minutes=5):
            self.authenticate()

        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def list_workspaces(self):
        """List all workspaces (groups)"""
        url = f"{self.base_url}/groups"

        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()

            data = response.json()
            return data.get('value', [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to list workspaces: {str(e)}")

    def get_datasets(self, workspace_id=None):
        """Get datasets in a workspace or personal workspace"""
        if workspace_id:
            url = f"{self.base_url}/groups/{workspace_id}/datasets"
        else:
            url = f"{self.base_url}/datasets"

        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()

            data = response.json()
            return data.get('value', [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get datasets: {str(e)}")

    def refresh_dataset(self, dataset_id, workspace_id=None):
        """Trigger a dataset refresh"""
        if workspace_id:
            url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        else:
            url = f"{self.base_url}/datasets/{dataset_id}/refreshes"

        payload = {
            "notifyOption": "MailOnFailure"
        }

        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()

            # Get request ID from response headers
            request_id = response.headers.get('RequestId')

            return {
                'status': 'started',
                'request_id': request_id
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit exceeded
                retry_after = e.response.headers.get('Retry-After', 60)
                raise Exception(f"Rate limit exceeded. Retry after {retry_after} seconds")
            raise Exception(f"Dataset refresh failed: {str(e)}")

    def get_refresh_history(self, dataset_id, workspace_id=None, top=5):
        """Get dataset refresh history"""
        if workspace_id:
            url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        else:
            url = f"{self.base_url}/datasets/{dataset_id}/refreshes"

        params = {'$top': top}

        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('value', [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get refresh history: {str(e)}")

    def add_dataset_user(self, dataset_id, user_email, role='Viewer', workspace_id=None):
        """Grant user access to a dataset"""
        if workspace_id:
            url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}/users"
        else:
            url = f"{self.base_url}/datasets/{dataset_id}/users"

        payload = {
            "emailAddress": user_email,
            "datasetUserAccessRight": role  # Viewer, Contributor, Owner
        }

        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to add dataset user: {str(e)}")

# Usage example
pbi = PowerBIAPI(
    tenant_id='your-tenant-id',
    client_id='your-client-id',
    client_secret='your-client-secret'
)

pbi.authenticate()

# List workspaces
workspaces = pbi.list_workspaces()
print(f"Found {len(workspaces)} workspaces")

# Refresh dataset
result = pbi.refresh_dataset('dataset-id', workspace_id='workspace-id')
print(f"Refresh started: {result['request_id']}")
```

### Power BI PowerShell Cmdlets

```powershell
# Install Power BI cmdlets
Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser

# Connect using service principal
$credential = New-Object System.Management.Automation.PSCredential(
    $clientId,
    (ConvertTo-SecureString $clientSecret -AsPlainText -Force)
)

Connect-PowerBIServiceAccount -ServicePrincipal -Credential $credential -TenantId $tenantId

# Get all workspaces
$workspaces = Get-PowerBIWorkspace -Scope Organization

# Get datasets in a workspace
$datasets = Get-PowerBIDataset -WorkspaceId $workspaceId

# Trigger dataset refresh
Invoke-PowerBIRestMethod -Url "datasets/$datasetId/refreshes" -Method Post -Body '{}'

# Export report
Export-PowerBIReport -WorkspaceId $workspaceId -ReportId $reportId -OutFile "report.pbix"
```

---

## Looker API

Looker API 4.0 provides comprehensive access to Looker functionality.

```python
import looker_sdk
from looker_sdk import models40 as models
from typing import List, Optional

class LookerAPI:
    def __init__(self, base_url, client_id, client_secret):
        """Initialize Looker SDK"""
        self.sdk = looker_sdk.init40(
            config_settings={
                'base_url': base_url,
                'client_id': client_id,
                'client_secret': client_secret,
                'verify_ssl': True
            }
        )

    def list_dashboards(self, folder_id: Optional[str] = None) -> List[dict]:
        """List all dashboards or dashboards in a folder"""
        try:
            if folder_id:
                dashboards = self.sdk.folder_dashboards(folder_id)
            else:
                dashboards = self.sdk.all_dashboards()

            return [
                {
                    'id': d.id,
                    'title': d.title,
                    'folder_id': d.folder.id if d.folder else None,
                    'user_id': d.user_id,
                    'view_count': d.view_count
                }
                for d in dashboards
            ]

        except looker_sdk.error.SDKError as e:
            raise Exception(f"Failed to list dashboards: {str(e)}")

    def run_query(self, query_id: int, result_format: str = 'json') -> dict:
        """Run a query and return results"""
        try:
            result = self.sdk.run_query(
                query_id=query_id,
                result_format=result_format
            )

            if result_format == 'json':
                import json
                return json.loads(result)

            return result

        except looker_sdk.error.SDKError as e:
            raise Exception(f"Query execution failed: {str(e)}")

    def create_scheduled_plan(self, dashboard_id: str, user_id: int,
                             email: str, cron_schedule: str) -> dict:
        """Create a scheduled dashboard delivery"""
        try:
            # Create schedule
            schedule = self.sdk.create_scheduled_plan(
                body=models.WriteScheduledPlan(
                    name=f"Scheduled delivery for dashboard {dashboard_id}",
                    dashboard_id=dashboard_id,
                    user_id=user_id,
                    enabled=True,
                    crontab=cron_schedule,  # e.g., "0 9 * * 1" for Mondays at 9am
                    scheduled_plan_destination=[
                        models.ScheduledPlanDestination(
                            format='pdf',
                            type='email',
                            address=email
                        )
                    ]
                )
            )

            return {
                'id': schedule.id,
                'name': schedule.name,
                'enabled': schedule.enabled,
                'crontab': schedule.crontab
            }

        except looker_sdk.error.SDKError as e:
            raise Exception(f"Failed to create scheduled plan: {str(e)}")

    def create_user(self, email: str, first_name: str, last_name: str,
                   role_ids: List[int]) -> dict:
        """Create a new user"""
        try:
            user = self.sdk.create_user(
                body=models.WriteUser(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role_ids=role_ids
                )
            )

            return {
                'id': user.id,
                'email': user.email,
                'display_name': user.display_name
            }

        except looker_sdk.error.SDKError as e:
            raise Exception(f"User creation failed: {str(e)}")

    def add_user_to_group(self, group_id: int, user_id: int) -> bool:
        """Add a user to a group"""
        try:
            self.sdk.add_group_user(
                group_id=group_id,
                body=models.GroupIdForGroupUserInclusion(user_id=user_id)
            )
            return True

        except looker_sdk.error.SDKError as e:
            raise Exception(f"Failed to add user to group: {str(e)}")

    def get_look(self, look_id: int) -> dict:
        """Get a Look and its metadata"""
        try:
            look = self.sdk.look(look_id)

            return {
                'id': look.id,
                'title': look.title,
                'query_id': look.query_id,
                'folder_id': look.folder.id if look.folder else None,
                'view_count': look.view_count,
                'last_viewed_at': look.last_viewed_at
            }

        except looker_sdk.error.SDKError as e:
            raise Exception(f"Failed to get Look: {str(e)}")

# Usage
looker = LookerAPI(
    base_url='https://company.looker.com:19999',
    client_id='your_client_id',
    client_secret='your_client_secret'
)

# List dashboards
dashboards = looker.list_dashboards()

# Schedule dashboard delivery
schedule = looker.create_scheduled_plan(
    dashboard_id='123',
    user_id=456,
    email='team@company.com',
    cron_schedule='0 9 * * 1'  # Mondays at 9am
)
```

---

## Metabase API

Metabase provides a straightforward REST API for programmatic access.

```javascript
const axios = require('axios');

class MetabaseAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.sessionToken = null;
    }

    async authenticate(username, password) {
        try {
            const response = await axios.post(`${this.baseUrl}/api/session`, {
                username: username,
                password: password
            });

            this.sessionToken = response.data.id;
            return this.sessionToken;

        } catch (error) {
            throw new Error(`Authentication failed: ${error.message}`);
        }
    }

    getHeaders() {
        if (!this.sessionToken) {
            throw new Error('Not authenticated. Call authenticate() first.');
        }

        return {
            'X-Metabase-Session': this.sessionToken,
            'Content-Type': 'application/json'
        };
    }

    async listDashboards() {
        try {
            const response = await axios.get(
                `${this.baseUrl}/api/dashboard`,
                { headers: this.getHeaders() }
            );

            return response.data;

        } catch (error) {
            throw new Error(`Failed to list dashboards: ${error.message}`);
        }
    }

    async getDashboard(dashboardId) {
        try {
            const response = await axios.get(
                `${this.baseUrl}/api/dashboard/${dashboardId}`,
                { headers: this.getHeaders() }
            );

            return response.data;

        } catch (error) {
            throw new Error(`Failed to get dashboard: ${error.message}`);
        }
    }

    async executeQuery(query) {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/dataset`,
                {
                    database: query.databaseId,
                    type: 'query',
                    query: {
                        'source-table': query.tableId,
                        filter: query.filter || [],
                        aggregation: query.aggregation || [],
                        breakout: query.breakout || []
                    }
                },
                { headers: this.getHeaders() }
            );

            return response.data;

        } catch (error) {
            throw new Error(`Query execution failed: ${error.message}`);
        }
    }

    async createCard(card) {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/card`,
                {
                    name: card.name,
                    display: card.display || 'table',
                    visualization_settings: card.visualizationSettings || {},
                    dataset_query: card.datasetQuery,
                    collection_id: card.collectionId
                },
                { headers: this.getHeaders() }
            );

            return response.data;

        } catch (error) {
            throw new Error(`Card creation failed: ${error.message}`);
        }
    }

    async createUser(user) {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/user`,
                {
                    first_name: user.firstName,
                    last_name: user.lastName,
                    email: user.email,
                    password: user.password,
                    group_ids: user.groupIds || []
                },
                { headers: this.getHeaders() }
            );

            return response.data;

        } catch (error) {
            throw new Error(`User creation failed: ${error.message}`);
        }
    }
}

// Usage example
async function main() {
    const metabase = new MetabaseAPI('https://metabase.company.com');

    try {
        // Authenticate
        await metabase.authenticate('admin@company.com', 'password');

        // List dashboards
        const dashboards = await metabase.listDashboards();
        console.log(`Found ${dashboards.length} dashboards`);

        // Execute query
        const results = await metabase.executeQuery({
            databaseId: 1,
            tableId: 10,
            aggregation: [['count']],
            breakout: [['field', 5, null]]
        });

        console.log('Query results:', results);

    } catch (error) {
        console.error('Error:', error.message);
    }
}
```

---

## Authentication Patterns

### OAuth 2.0 Flow

Most enterprise BI platforms support OAuth 2.0 for secure delegated access.

**Authorization Code Flow (for web apps):**

```python
from flask import Flask, request, redirect, session
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Configuration
OAUTH_CONFIG = {
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'authorization_url': 'https://platform.com/oauth/authorize',
    'token_url': 'https://platform.com/oauth/token',
    'redirect_uri': 'http://localhost:5000/callback'
}

@app.route('/login')
def login():
    """Redirect user to OAuth provider"""
    params = {
        'client_id': OAUTH_CONFIG['client_id'],
        'redirect_uri': OAUTH_CONFIG['redirect_uri'],
        'response_type': 'code',
        'scope': 'read write'
    }

    auth_url = f"{OAUTH_CONFIG['authorization_url']}?" + \
               '&'.join([f"{k}={v}" for k, v in params.items()])

    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle OAuth callback"""
    code = request.args.get('code')

    if not code:
        return "Error: No authorization code received", 400

    # Exchange code for token
    token_data = {
        'client_id': OAUTH_CONFIG['client_id'],
        'client_secret': OAUTH_CONFIG['client_secret'],
        'code': code,
        'redirect_uri': OAUTH_CONFIG['redirect_uri'],
        'grant_type': 'authorization_code'
    }

    response = requests.post(OAUTH_CONFIG['token_url'], data=token_data)

    if response.status_code == 200:
        tokens = response.json()
        session['access_token'] = tokens['access_token']
        session['refresh_token'] = tokens.get('refresh_token')

        return redirect('/dashboard')
    else:
        return f"Token exchange failed: {response.text}", 400
```

### API Key Management

Best practices for API key security:

```python
import os
from cryptography.fernet import Fernet
import keyring

class SecureAPIKeyManager:
    def __init__(self, service_name='bi_platform'):
        self.service_name = service_name
        self.cipher_suite = None
        self._initialize_encryption()

    def _initialize_encryption(self):
        """Initialize encryption key"""
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            # Generate new key if not exists
            key = Fernet.generate_key()
            print(f"Store this key securely: {key.decode()}")
        else:
            key = key.encode()

        self.cipher_suite = Fernet(key)

    def store_api_key(self, key_name, api_key):
        """Store API key securely in system keyring"""
        encrypted = self.cipher_suite.encrypt(api_key.encode())
        keyring.set_password(self.service_name, key_name, encrypted.decode())

    def retrieve_api_key(self, key_name):
        """Retrieve and decrypt API key"""
        encrypted = keyring.get_password(self.service_name, key_name)
        if encrypted:
            return self.cipher_suite.decrypt(encrypted.encode()).decode()
        return None

    def delete_api_key(self, key_name):
        """Delete stored API key"""
        keyring.delete_password(self.service_name, key_name)

# Usage
manager = SecureAPIKeyManager()
manager.store_api_key('tableau_token', 'secret-token-value')
api_key = manager.retrieve_api_key('tableau_token')
```

---

## Rate Limiting and Pagination

### Implementing Rate Limit Handling

```python
import time
from functools import wraps

class RateLimiter:
    def __init__(self, max_calls, period):
        """
        max_calls: Maximum number of calls allowed
        period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # Remove calls outside the period
            self.calls = [call for call in self.calls if call > now - self.period]

            if len(self.calls) >= self.max_calls:
                # Wait until oldest call expires
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    print(f"Rate limit reached. Waiting {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                    self.calls = []

            self.calls.append(time.time())
            return func(*args, **kwargs)

        return wrapper

# Usage: 100 calls per minute
@RateLimiter(max_calls=100, period=60)
def api_call():
    # Make API request
    pass
```

### Pagination Patterns

```python
def fetch_all_pages(api_client, resource_type, page_size=100):
    """Generic pagination handler"""
    all_items = []
    page_number = 1
    has_more = True

    while has_more:
        try:
            response = api_client.get_page(
                resource_type,
                page_size=page_size,
                page_number=page_number
            )

            items = response.get('items', [])
            all_items.extend(items)

            # Check if more pages exist
            total_items = response.get('total', 0)
            has_more = len(all_items) < total_items
            page_number += 1

            print(f"Fetched {len(all_items)}/{total_items} items")

            # Respect rate limits
            time.sleep(0.1)

        except Exception as e:
            print(f"Error fetching page {page_number}: {str(e)}")
            break

    return all_items
```

---

## Automation Use Cases

### Automated Data Refresh Orchestration

```python
import schedule
import time
from datetime import datetime

class RefreshOrchestrator:
    def __init__(self, tableau_api, powerbi_api):
        self.tableau_api = tableau_api
        self.powerbi_api = powerbi_api
        self.refresh_log = []

    def refresh_tableau_extracts(self, datasource_ids):
        """Refresh multiple Tableau extracts"""
        print(f"[{datetime.now()}] Starting Tableau extract refreshes")

        for ds_id in datasource_ids:
            try:
                job = self.tableau_api.refresh_extract(ds_id)
                self.refresh_log.append({
                    'platform': 'Tableau',
                    'datasource_id': ds_id,
                    'job_id': job['job_id'],
                    'status': 'started',
                    'timestamp': datetime.now()
                })
                print(f"  Refresh started for {ds_id}: {job['job_id']}")

            except Exception as e:
                print(f"  Error refreshing {ds_id}: {str(e)}")
                self.refresh_log.append({
                    'platform': 'Tableau',
                    'datasource_id': ds_id,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now()
                })

    def refresh_powerbi_datasets(self, datasets):
        """Refresh multiple Power BI datasets"""
        print(f"[{datetime.now()}] Starting Power BI dataset refreshes")

        for dataset in datasets:
            try:
                result = self.powerbi_api.refresh_dataset(
                    dataset['id'],
                    workspace_id=dataset.get('workspace_id')
                )
                self.refresh_log.append({
                    'platform': 'PowerBI',
                    'dataset_id': dataset['id'],
                    'request_id': result['request_id'],
                    'status': 'started',
                    'timestamp': datetime.now()
                })
                print(f"  Refresh started for {dataset['id']}")

            except Exception as e:
                print(f"  Error refreshing {dataset['id']}: {str(e)}")

    def schedule_refreshes(self):
        """Set up refresh schedules"""
        # Daily at 6 AM
        schedule.every().day.at("06:00").do(
            self.refresh_tableau_extracts,
            datasource_ids=['ds1', 'ds2', 'ds3']
        )

        # Every 4 hours
        schedule.every(4).hours.do(
            self.refresh_powerbi_datasets,
            datasets=[
                {'id': 'dataset1', 'workspace_id': 'ws1'},
                {'id': 'dataset2', 'workspace_id': 'ws1'}
            ]
        )

        print("Refresh schedules configured")

        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)
```

### User Provisioning Automation

```python
class UserProvisioningService:
    def __init__(self, tableau_api, powerbi_api, looker_api):
        self.tableau_api = tableau_api
        self.powerbi_api = powerbi_api
        self.looker_api = looker_api

    def provision_user(self, user_data):
        """Provision user across all platforms"""
        results = {}

        # Tableau
        try:
            tableau_user = self.tableau_api.create_user(
                user_data['email'],
                user_data['site_role']
            )
            self.tableau_api.add_user_to_group(
                tableau_user['id'],
                user_data['tableau_group_id']
            )
            results['tableau'] = 'success'
        except Exception as e:
            results['tableau'] = f'failed: {str(e)}'

        # Power BI
        try:
            self.powerbi_api.add_workspace_user(
                user_data['powerbi_workspace_id'],
                user_data['email'],
                role='Viewer'
            )
            results['powerbi'] = 'success'
        except Exception as e:
            results['powerbi'] = f'failed: {str(e)}'

        # Looker
        try:
            looker_user = self.looker_api.create_user(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role_ids=user_data['looker_role_ids']
            )
            results['looker'] = 'success'
        except Exception as e:
            results['looker'] = f'failed: {str(e)}'

        return results
```

---

## Best Practices

### 1. Error Handling and Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise

                    wait_time = backoff_factor ** retries
                    print(f"Retry {retries}/{max_retries} after {wait_time}s: {str(e)}")
                    time.sleep(wait_time)

        return wrapper
    return decorator

@retry_on_failure(max_retries=3, backoff_factor=2)
def critical_api_call():
    # Make API request
    pass
```

### 2. Logging and Monitoring

```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bi_api_integration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_api_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"API call started: {func.__name__}")
        start_time = datetime.now()

        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"API call succeeded: {func.__name__} ({duration:.2f}s)")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"API call failed: {func.__name__} ({duration:.2f}s) - {str(e)}")
            raise

    return wrapper
```

### 3. Connection Pooling

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

def create_session_with_retries():
    """Create requests session with connection pooling and retries"""
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session
```

### 4. Secrets Management

```python
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name='us-east-1'):
    """Retrieve secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise Exception(f"Failed to retrieve secret: {str(e)}")

# Usage
import json

secrets = json.loads(get_secret('bi-platform-credentials'))
api_key = secrets['tableau_api_key']
```

---

## Summary

This guide covers the major BI platform APIs and integration patterns:

- **Tableau**: REST API, Server API, and Hyper API for comprehensive automation
- **Power BI**: REST API and PowerShell cmdlets with Azure AD authentication
- **Looker**: API 4.0 with SDK support for programmatic access
- **Metabase**: Simple REST API for open-source BI automation

**Key Takeaways:**
1. Always use secure authentication (OAuth, PAT, service principals)
2. Implement proper error handling and retry logic
3. Respect rate limits and use pagination effectively
4. Store credentials securely using secrets management
5. Log API calls for monitoring and debugging
6. Use connection pooling for better performance
7. Automate common tasks like refreshes and user provisioning

For detailed API documentation, refer to vendor-specific resources:
- Tableau: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm
- Power BI: https://learn.microsoft.com/en-us/rest/api/power-bi/
- Looker: https://developers.looker.com/api/overview
- Metabase: https://www.metabase.com/docs/latest/api-documentation
