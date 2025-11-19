# BI Platform API Integration Reference

## Tableau REST API

### Authentication
```python
import requests
import xml.etree.ElementTree as ET

# Sign in to get auth token
def tableau_sign_in(server_url, username, password, site_id=''):
    url = f"{server_url}/api/3.19/auth/signin"

    payload = f"""
    <tsRequest>
        <credentials name="{username}" password="{password}">
            <site contentUrl="{site_id}" />
        </credentials>
    </tsRequest>
    """

    headers = {'Content-Type': 'application/xml'}
    response = requests.post(url, data=payload, headers=headers)

    # Parse response
    tree = ET.fromstring(response.content)
    token = tree.find('.//t:credentials', {'t': 'http://tableau.com/api'}).get('token')
    site_id = tree.find('.//t:site', {'t': 'http://tableau.com/api'}).get('id')

    return token, site_id
```

### Common Operations
```python
class TableauAPI:
    def __init__(self, server_url, token, site_id, api_version='3.19'):
        self.server_url = server_url
        self.token = token
        self.site_id = site_id
        self.api_version = api_version
        self.base_url = f"{server_url}/api/{api_version}"
        self.headers = {'X-Tableau-Auth': token}

    def get_workbooks(self):
        """Get all workbooks in site"""
        url = f"{self.base_url}/sites/{self.site_id}/workbooks"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def publish_workbook(self, workbook_path, project_id, name):
        """Publish workbook to Tableau Server"""
        url = f"{self.base_url}/sites/{self.site_id}/workbooks"

        # Prepare multipart request
        with open(workbook_path, 'rb') as f:
            files = {'tableau_workbook': (name, f, 'application/octet-stream')}

            payload = f"""
            <tsRequest>
                <workbook name="{name}">
                    <project id="{project_id}" />
                </workbook>
            </tsRequest>
            """

            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data={'request_payload': payload}
            )

        return response.json()

    def refresh_extract(self, workbook_id):
        """Trigger extract refresh"""
        url = f"{self.base_url}/sites/{self.site_id}/workbooks/{workbook_id}/refresh"
        response = requests.post(url, headers=self.headers)
        return response.json()

    def download_workbook(self, workbook_id, filepath):
        """Download workbook file"""
        url = f"{self.base_url}/sites/{self.site_id}/workbooks/{workbook_id}/content"
        response = requests.get(url, headers=self.headers)

        with open(filepath, 'wb') as f:
            f.write(response.content)

    def create_user(self, username, site_role='Viewer'):
        """Add user to site"""
        url = f"{self.base_url}/sites/{self.site_id}/users"

        payload = f"""
        <tsRequest>
            <user name="{username}" siteRole="{site_role}" />
        </tsRequest>
        """

        response = requests.post(
            url,
            headers=self.headers,
            data=payload,
            headers={**self.headers, 'Content-Type': 'application/xml'}
        )
        return response.json()

    def update_permissions(self, workbook_id, user_id, permissions):
        """Update workbook permissions"""
        url = f"{self.base_url}/sites/{self.site_id}/workbooks/{workbook_id}/permissions"

        capabilities = '\n'.join([
            f'<capability name="{cap}" mode="{mode}" />'
            for cap, mode in permissions.items()
        ])

        payload = f"""
        <tsRequest>
            <permissions>
                <granteeCapabilities>
                    <user id="{user_id}" />
                    <capabilities>
                        {capabilities}
                    </capabilities>
                </granteeCapabilities>
            </permissions>
        </tsRequest>
        """

        response = requests.put(
            url,
            data=payload,
            headers={**self.headers, 'Content-Type': 'application/xml'}
        )
        return response.json()
```

### Tableau Hyper API
```python
from tableauhyperapi import HyperProcess, Telemetry, Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, Inserter, escape_name

def create_hyper_file(data, output_path):
    """Create Tableau Hyper file from pandas DataFrame"""

    # Define table schema
    table_def = TableDefinition(
        table_name='Extract',
        columns=[
            TableDefinition.Column('OrderID', SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('OrderDate', SqlType.date(), NULLABLE),
            TableDefinition.Column('Customer', SqlType.text(), NULLABLE),
            TableDefinition.Column('Amount', SqlType.double(), NULLABLE),
        ]
    )

    with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(
            endpoint=hyper.endpoint,
            database=output_path,
            create_mode=CreateMode.CREATE_AND_REPLACE
        ) as connection:

            # Create table
            connection.catalog.create_table(table_def)

            # Insert data
            with Inserter(connection, table_def) as inserter:
                for _, row in data.iterrows():
                    inserter.add_row([
                        row['OrderID'],
                        row['OrderDate'],
                        row['Customer'],
                        row['Amount']
                    ])
                inserter.execute()

    print(f"Hyper file created: {output_path}")
```

## Power BI REST API

### Authentication with MSAL
```python
from msal import ConfidentialClientApplication, PublicClientApplication
import requests

class PowerBIAPI:
    def __init__(self, client_id, client_secret=None, tenant_id='common'):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.base_url = 'https://api.powerbi.com/v1.0/myorg'

        # Authority URL
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"

        # Scopes for Power BI Service
        self.scopes = ["https://analysis.windows.net/powerbi/api/.default"]

        if client_secret:
            # Service Principal (app-only)
            self.app = ConfidentialClientApplication(
                client_id,
                authority=self.authority,
                client_credential=client_secret
            )
        else:
            # User authentication (device code flow)
            self.app = PublicClientApplication(
                client_id,
                authority=self.authority
            )

    def get_token_service_principal(self):
        """Get token using client credentials"""
        result = self.app.acquire_token_for_client(scopes=self.scopes)
        if "access_token" in result:
            return result['access_token']
        else:
            raise Exception(f"Failed to get token: {result.get('error_description')}")

    def get_token_device_code(self):
        """Get token using device code flow (user auth)"""
        flow = self.app.initiate_device_flow(scopes=self.scopes)
        print(flow['message'])

        result = self.app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            return result['access_token']
        else:
            raise Exception(f"Failed to get token: {result.get('error_description')}")

    def _get_headers(self, token):
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def get_workspaces(self, token):
        """Get all workspaces"""
        url = f"{self.base_url}/groups"
        response = requests.get(url, headers=self._get_headers(token))
        return response.json()

    def get_datasets(self, token, workspace_id):
        """Get datasets in workspace"""
        url = f"{self.base_url}/groups/{workspace_id}/datasets"
        response = requests.get(url, headers=self._get_headers(token))
        return response.json()

    def refresh_dataset(self, token, workspace_id, dataset_id):
        """Trigger dataset refresh"""
        url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        response = requests.post(url, headers=self._get_headers(token))
        return response.status_code == 202

    def get_reports(self, token, workspace_id):
        """Get reports in workspace"""
        url = f"{self.base_url}/groups/{workspace_id}/reports"
        response = requests.get(url, headers=self._get_headers(token))
        return response.json()

    def export_report(self, token, workspace_id, report_id, format='PDF'):
        """Export report to file"""
        url = f"{self.base_url}/groups/{workspace_id}/reports/{report_id}/Export"
        payload = {'format': format}

        response = requests.post(
            url,
            json=payload,
            headers=self._get_headers(token)
        )

        export_id = response.json()['id']

        # Poll for completion
        status_url = f"{url}/{export_id}"
        while True:
            status = requests.get(status_url, headers=self._get_headers(token))
            if status.json()['status'] == 'Succeeded':
                # Download file
                file_url = f"{status_url}/file"
                file_response = requests.get(file_url, headers=self._get_headers(token))
                return file_response.content
            elif status.json()['status'] == 'Failed':
                raise Exception("Export failed")

            time.sleep(2)

    def create_dataset(self, token, workspace_id, dataset_definition):
        """Create new dataset"""
        url = f"{self.base_url}/groups/{workspace_id}/datasets"
        response = requests.post(
            url,
            json=dataset_definition,
            headers=self._get_headers(token)
        )
        return response.json()

    def push_data(self, token, workspace_id, dataset_id, table_name, rows):
        """Push data to dataset"""
        url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}/tables/{table_name}/rows"
        payload = {'rows': rows}

        response = requests.post(
            url,
            json=payload,
            headers=self._get_headers(token)
        )
        return response.status_code == 200
```

### Embed Token Generation
```python
def generate_embed_token(token, workspace_id, report_id, datasets):
    """Generate embed token for report"""
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/GenerateToken"

    payload = {
        "accessLevel": "View",
        "datasetId": datasets[0],  # Can include multiple
        "allowSaveAs": False
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()['token']
```

## Looker API (SDK)

### Python SDK
```python
import looker_sdk
from looker_sdk import models40 as models

# Initialize SDK (reads from looker.ini or environment)
sdk = looker_sdk.init40()

class LookerAPI:
    def __init__(self, sdk):
        self.sdk = sdk

    def get_user_info(self):
        """Get current user information"""
        return self.sdk.me()

    def get_all_dashboards(self, folder_id=None):
        """Get all dashboards"""
        if folder_id:
            return self.sdk.folder_dashboards(folder_id)
        return self.sdk.all_dashboards()

    def get_dashboard(self, dashboard_id):
        """Get specific dashboard"""
        return self.sdk.dashboard(dashboard_id)

    def create_dashboard(self, title, folder_id, description=''):
        """Create new dashboard"""
        dashboard = models.WriteDashboard(
            title=title,
            folder_id=folder_id,
            description=description
        )
        return self.sdk.create_dashboard(dashboard)

    def run_look(self, look_id, result_format='json'):
        """Run a Look and get results"""
        return self.sdk.run_look(look_id, result_format)

    def run_inline_query(self, model, view, fields, filters=None):
        """Run ad-hoc query"""
        query = models.WriteQuery(
            model=model,
            view=view,
            fields=fields,
            filters=filters or {}
        )
        query_result = self.sdk.create_query(query)
        return self.sdk.run_query(query_result.id, 'json')

    def create_scheduled_plan(self, dashboard_id, email, cron):
        """Create scheduled dashboard delivery"""
        schedule = models.WriteScheduledPlan(
            name=f"Scheduled {dashboard_id}",
            dashboard_id=dashboard_id,
            crontab=cron,
            timezone='America/Los_Angeles',
            scheduled_plan_destination=[
                models.ScheduledPlanDestination(
                    type='email',
                    address=email,
                    format='pdf_landscape'
                )
            ]
        )
        return self.sdk.create_scheduled_plan(schedule)

    def create_sso_embed_url(self, target_url, external_user_id,
                            first_name, last_name, permissions, models,
                            session_length=3600):
        """Create SSO embed URL"""
        embed_params = {
            'target_url': target_url,
            'external_user_id': external_user_id,
            'first_name': first_name,
            'last_name': last_name,
            'permissions': permissions,
            'models': models,
            'session_length': session_length
        }

        sso_url = self.sdk.create_sso_embed_url(
            models.EmbedSsoParams(**embed_params)
        )
        return sso_url.url

    def update_lookml(self, project_id, file_path, content):
        """Update LookML file"""
        return self.sdk.create_project_file(
            project_id=project_id,
            file_id=file_path,
            body=content
        )

    def git_deploy(self, project_id, branch='master'):
        """Deploy LookML project from Git"""
        return self.sdk.deploy_to_production(project_id)
```

## Qlik Sense API

### Engine API (WebSocket)
```javascript
// Qlik Engine API with enigma.js
const enigma = require('enigma.js');
const WebSocket = require('ws');
const schema = require('enigma.js/schemas/12.612.0.json');

// Configuration
const config = {
  schema,
  url: 'wss://qlik.company.com/app/appId',
  createSocket: url => new WebSocket(url, {
    headers: {
      'Authorization': `Bearer ${jwtToken}`
    }
  })
};

// Connect and interact
async function qlikEngineExample() {
  const session = enigma.create(config);
  const global = await session.open();
  const doc = await global.openDoc('app-id');

  // Create object
  const obj = await doc.createObject({
    qInfo: {
      qType: 'my-object'
    },
    qHyperCubeDef: {
      qDimensions: [{
        qDef: {
          qFieldDefs: ['Product']
        }
      }],
      qMeasures: [{
        qDef: {
          qDef: 'Sum(Sales)'
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
  const layout = await obj.getLayout();
  console.log(layout.qHyperCube.qDataPages);

  // Make selection
  const field = await doc.getField('Region');
  await field.select('East');

  // Clear selection
  await field.clear();

  await session.close();
}
```

### Repository API (REST)
```python
import requests

class QlikRepositoryAPI:
    def __init__(self, server, certificate, verify_ssl=True):
        self.base_url = f"https://{server}/qrs"
        self.cert = certificate  # (cert_file, key_file)
        self.verify = verify_ssl
        self.headers = {
            'X-Qlik-Xrfkey': '0123456789abcdef',
            'Content-Type': 'application/json'
        }

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint}?xrfkey=0123456789abcdef"
        return requests.request(
            method,
            url,
            cert=self.cert,
            verify=self.verify,
            headers=self.headers,
            **kwargs
        )

    def get_apps(self):
        """Get all apps"""
        return self._request('GET', 'app/full').json()

    def publish_app(self, app_id, stream_id, name):
        """Publish app to stream"""
        payload = {
            'stream': {'id': stream_id},
            'name': name
        }
        return self._request('PUT', f'app/{app_id}/publish', json=payload)

    def reload_app(self, app_id):
        """Trigger app reload"""
        task = {
            'task': {
                'app': {'id': app_id},
                'isManuallyTriggered': True
            }
        }
        return self._request('POST', 'app/reload', json=task)

    def export_app(self, app_id, filename):
        """Export app"""
        response = self._request('POST', f'app/{app_id}/export/{filename}')
        download_path = response.json()['downloadPath']

        # Download file
        file_response = self._request('GET', f'download/{download_path}')
        return file_response.content
```

## Apache Superset API

### Authentication and Basic Operations
```python
import requests

class SupersetAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.login(username, password)

    def login(self, username, password):
        """Authenticate and get tokens"""
        url = f"{self.base_url}/api/v1/security/login"
        payload = {
            "username": username,
            "password": password,
            "provider": "db",
            "refresh": True
        }
        response = requests.post(url, json=payload)
        tokens = response.json()
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_dashboards(self):
        """Get all dashboards"""
        url = f"{self.base_url}/api/v1/dashboard/"
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def get_charts(self, dashboard_id=None):
        """Get charts, optionally filtered by dashboard"""
        url = f"{self.base_url}/api/v1/chart/"
        if dashboard_id:
            url += f"?q=(filters:!((col:dashboards,opr:rel_m_m,value:{dashboard_id})))"
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def execute_sql(self, database_id, sql):
        """Execute SQL query"""
        url = f"{self.base_url}/api/v1/sqllab/execute/"
        payload = {
            "database_id": database_id,
            "sql": sql,
            "runAsync": False,
            "schema": "public"
        }
        response = requests.post(url, json=payload, headers=self._get_headers())
        return response.json()

    def export_dashboard(self, dashboard_ids):
        """Export dashboards"""
        url = f"{self.base_url}/api/v1/dashboard/export/"
        params = {'q': f'!({",".join(map(str, dashboard_ids))})'}
        response = requests.get(url, params=params, headers=self._get_headers())
        return response.content  # ZIP file

    def import_dashboard(self, zip_file_path):
        """Import dashboard from ZIP"""
        url = f"{self.base_url}/api/v1/dashboard/import/"
        with open(zip_file_path, 'rb') as f:
            files = {'formData': ('dashboard.zip', f, 'application/zip')}
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.post(url, files=files, headers=headers)
        return response.json()

    def create_chart(self, viz_type, datasource_id, metrics, groupby):
        """Create new chart"""
        url = f"{self.base_url}/api/v1/chart/"
        payload = {
            "slice_name": "New Chart",
            "viz_type": viz_type,
            "datasource_id": datasource_id,
            "datasource_type": "table",
            "params": {
                "metrics": metrics,
                "groupby": groupby
            }
        }
        response = requests.post(url, json=payload, headers=self._get_headers())
        return response.json()
```

## Webhook Integrations

### Tableau Webhook Handler
```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = 'your-secret-key'

@app.route('/tableau-webhook', methods=['POST'])
def tableau_webhook():
    """Handle Tableau webhook events"""

    # Verify signature
    signature = request.headers.get('X-Tableau-Signature')
    body = request.get_data()

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if signature != expected_signature:
        return 'Invalid signature', 401

    # Process event
    event = request.json
    event_type = event['event_type']

    if event_type == 'DatasourceRefreshStarted':
        print(f"Refresh started for {event['resource_name']}")
    elif event_type == 'DatasourceRefreshSucceeded':
        print(f"Refresh completed for {event['resource_name']}")
        # Trigger downstream processes
    elif event_type == 'DatasourceRefreshFailed':
        print(f"Refresh failed for {event['resource_name']}")
        # Send alert

    return 'OK', 200
```

## API Rate Limiting Best Practices

```python
import time
from functools import wraps

def rate_limit(calls=10, period=60):
    """Rate limiting decorator"""
    min_interval = period / calls
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret

        return wrapper
    return decorator

# Usage
@rate_limit(calls=100, period=60)
def api_call():
    # Your API call here
    pass
```

## Resources
- Tableau REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm
- Power BI REST API: https://docs.microsoft.com/en-us/rest/api/power-bi/
- Looker API: https://developers.looker.com/api/explorer/4.0/
- Qlik Sense APIs: https://help.qlik.com/en-US/sense-developer/
- Superset API: https://superset.apache.org/docs/api
