# ETL Tool API Integration Guide

## Table of Contents

1. [Overview](#overview)
2. [dbt Cloud API](#dbt-cloud-api)
3. [Airbyte API](#airbyte-api)
4. [Fivetran API](#fivetran-api)
5. [Apache Airflow REST API](#apache-airflow-rest-api)
6. [Orchestration Patterns](#orchestration-patterns)
7. [Best Practices](#best-practices)

---

## Overview

Modern ETL/ELT tools provide robust APIs for programmatic orchestration, monitoring, and management. This guide covers integration patterns for the leading data pipeline tools.

**Key Integration Scenarios:**
- Automated pipeline triggering
- Job monitoring and alerting
- Connector configuration management
- Metadata extraction
- Custom workflow orchestration
- Error handling and recovery

---

## dbt Cloud API

dbt Cloud provides comprehensive APIs for managing projects, jobs, and runs.

### Administrative API

```python
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
import time

class dbtCloudAPI:
    def __init__(self, account_id: str, api_token: str, base_url: str = "https://cloud.getdbt.com/api/v2"):
        """
        Initialize dbt Cloud API client

        account_id: dbt Cloud account ID
        api_token: API token (generate from Account Settings)
        """
        self.account_id = account_id
        self.api_token = api_token
        self.base_url = base_url

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            'Authorization': f'Token {self.api_token}',
            'Content-Type': 'application/json'
        }

    def list_projects(self) -> List[Dict]:
        """List all projects in the account"""
        url = f"{self.base_url}/accounts/{self.account_id}/projects/"

        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to list projects: {str(e)}")

    def list_jobs(self, project_id: Optional[int] = None) -> List[Dict]:
        """List jobs, optionally filtered by project"""
        url = f"{self.base_url}/accounts/{self.account_id}/jobs/"

        params = {}
        if project_id:
            params['project_id'] = project_id

        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to list jobs: {str(e)}")

    def trigger_job(self, job_id: int, cause: str = "Triggered via API",
                   git_sha: Optional[str] = None, schema_override: Optional[str] = None,
                   steps_override: Optional[List[str]] = None) -> Dict:
        """
        Trigger a job run

        job_id: Job ID to trigger
        cause: Reason for triggering
        git_sha: Specific git commit to run (optional)
        schema_override: Override target schema
        steps_override: Override steps to run (e.g., ['dbt test', 'dbt run'])
        """
        url = f"{self.base_url}/accounts/{self.account_id}/jobs/{job_id}/run/"

        payload = {
            'cause': cause
        }

        if git_sha:
            payload['git_sha'] = git_sha
        if schema_override:
            payload['schema_override'] = schema_override
        if steps_override:
            payload['steps_override'] = steps_override

        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()

            data = response.json()
            return data.get('data', {})

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to trigger job: {str(e)}")

    def get_run_status(self, run_id: int) -> Dict:
        """Get status of a specific run"""
        url = f"{self.base_url}/accounts/{self.account_id}/runs/{run_id}/"

        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()

            data = response.json()
            run = data.get('data', {})

            return {
                'run_id': run.get('id'),
                'status': run.get('status'),
                'status_message': run.get('status_message'),
                'started_at': run.get('started_at'),
                'finished_at': run.get('finished_at'),
                'duration': run.get('duration'),
                'job_id': run.get('job_id'),
                'git_sha': run.get('git_sha')
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get run status: {str(e)}")

    def get_run_artifacts(self, run_id: int, artifact_type: str = 'manifest.json') -> Dict:
        """
        Get run artifacts

        artifact_type: 'manifest.json', 'catalog.json', 'run_results.json'
        """
        url = f"{self.base_url}/accounts/{self.account_id}/runs/{run_id}/artifacts/{artifact_type}"

        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get artifacts: {str(e)}")

    def cancel_run(self, run_id: int) -> bool:
        """Cancel a running job"""
        url = f"{self.base_url}/accounts/{self.account_id}/runs/{run_id}/cancel/"

        try:
            response = requests.post(url, headers=self._get_headers())
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to cancel run: {str(e)}")

    def wait_for_run_completion(self, run_id: int, timeout: int = 3600,
                                poll_interval: int = 30) -> Dict:
        """
        Wait for run to complete

        timeout: Maximum wait time in seconds
        poll_interval: Seconds between status checks
        """
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Run {run_id} did not complete within {timeout} seconds")

            status = self.get_run_status(run_id)

            # Terminal statuses: Success (10), Error (20), Cancelled (30)
            if status['status'] in [10, 20, 30]:
                return status

            print(f"Run {run_id} status: {status['status_message']}")
            time.sleep(poll_interval)

    def list_environments(self, project_id: int) -> List[Dict]:
        """List environments for a project"""
        url = f"{self.base_url}/accounts/{self.account_id}/environments/"

        params = {'project_id': project_id}

        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to list environments: {str(e)}")

# Usage example
dbt = dbtCloudAPI(
    account_id='12345',
    api_token='your-api-token'
)

# List projects
projects = dbt.list_projects()
print(f"Found {len(projects)} projects")

# Trigger job
run = dbt.trigger_job(
    job_id=67890,
    cause="Scheduled daily refresh",
    steps_override=['dbt run', 'dbt test']
)

print(f"Job triggered. Run ID: {run['id']}")

# Wait for completion
final_status = dbt.wait_for_run_completion(run['id'])

if final_status['status'] == 10:
    print("Job completed successfully!")
else:
    print(f"Job failed: {final_status['status_message']}")
```

### dbt Metadata API (GraphQL)

```python
import requests
from typing import Dict, List, Optional

class dbtMetadataAPI:
    def __init__(self, service_token: str, environment_id: int):
        """
        Initialize dbt Metadata API client (GraphQL)

        service_token: Service account token
        environment_id: Environment ID to query
        """
        self.service_token = service_token
        self.environment_id = environment_id
        self.endpoint = "https://metadata.cloud.getdbt.com/graphql"

    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL query"""
        headers = {
            'Authorization': f'Bearer {self.service_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'query': query,
            'variables': variables or {}
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()

            if 'errors' in data:
                raise Exception(f"GraphQL errors: {data['errors']}")

            return data.get('data', {})

        except requests.exceptions.RequestException as e:
            raise Exception(f"Metadata query failed: {str(e)}")

    def get_models(self, limit: int = 100) -> List[Dict]:
        """Get models and their metadata"""
        query = """
        query GetModels($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              models(first: $first) {
                edges {
                  node {
                    uniqueId
                    name
                    description
                    tags
                    meta
                    materializedType
                    database
                    schema
                    alias
                    executionInfo {
                      lastRunStatus
                      lastRunError
                      executeCompletedAt
                    }
                    stats {
                      rows {
                        value
                      }
                      bytes {
                        value
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {
            'environmentId': self.environment_id,
            'first': limit
        }

        result = self._execute_query(query, variables)

        models = []
        edges = result.get('environment', {}).get('applied', {}).get('models', {}).get('edges', [])

        for edge in edges:
            models.append(edge['node'])

        return models

    def get_model_lineage(self, unique_id: str) -> Dict:
        """Get lineage for a specific model"""
        query = """
        query GetModelLineage($environmentId: BigInt!, $uniqueId: String!) {
          environment(id: $environmentId) {
            applied {
              modelByUnique
Id(uniqueId: $uniqueId) {
                uniqueId
                name
                parentsModels {
                  uniqueId
                  name
                }
                parentsSources {
                  uniqueId
                  sourceName
                  name
                }
                childrenModels {
                  uniqueId
                  name
                }
              }
            }
          }
        }
        """

        variables = {
            'environmentId': self.environment_id,
            'uniqueId': unique_id
        }

        result = self._execute_query(query, variables)

        return result.get('environment', {}).get('applied', {}).get('modelByUniqueId', {})

    def get_test_results(self, limit: int = 100) -> List[Dict]:
        """Get recent test results"""
        query = """
        query GetTests($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              tests(first: $first) {
                edges {
                  node {
                    uniqueId
                    name
                    columnName
                    testType
                    status
                    executionInfo {
                      lastRunStatus
                      lastRunError
                      executeCompletedAt
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {
            'environmentId': self.environment_id,
            'first': limit
        }

        result = self._execute_query(query, variables)

        tests = []
        edges = result.get('environment', {}).get('applied', {}).get('tests', {}).get('edges', [])

        for edge in edges:
            tests.append(edge['node'])

        return tests

# Usage
metadata_api = dbtMetadataAPI(
    service_token='your-service-token',
    environment_id=12345
)

# Get all models
models = metadata_api.get_models(limit=200)
print(f"Found {len(models)} models")

# Get lineage for specific model
lineage = metadata_api.get_model_lineage('model.my_project.customers')
print(f"Parents: {lineage.get('parentsModels', [])}")
print(f"Children: {lineage.get('childrenModels', [])}")
```

---

## Airbyte API

Airbyte provides REST API for managing connectors and sync jobs.

```python
import requests
from typing import Dict, List, Optional, Any
import time

class AirbyteAPI:
    def __init__(self, base_url: str = "http://localhost:8001/api/v1",
                 username: str = "airbyte", password: str = "password"):
        """
        Initialize Airbyte API client

        base_url: Airbyte server URL
        username: Basic auth username
        password: Basic auth password
        """
        self.base_url = base_url
        self.auth = (username, password)

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                auth=self.auth,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()

            return response.json() if response.content else {}

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def list_workspaces(self) -> List[Dict]:
        """List all workspaces"""
        return self._request('POST', 'workspaces/list')['workspaces']

    def list_sources(self, workspace_id: str) -> List[Dict]:
        """List sources in a workspace"""
        data = {'workspaceId': workspace_id}
        return self._request('POST', 'sources/list', data)['sources']

    def list_destinations(self, workspace_id: str) -> List[Dict]:
        """List destinations in a workspace"""
        data = {'workspaceId': workspace_id}
        return self._request('POST', 'destinations/list', data)['destinations']

    def list_connections(self, workspace_id: str) -> List[Dict]:
        """List connections in a workspace"""
        data = {'workspaceId': workspace_id}
        return self._request('POST', 'connections/list', data)['connections']

    def create_source(self, workspace_id: str, source_definition_id: str,
                     name: str, connection_configuration: Dict) -> Dict:
        """Create a new source"""
        data = {
            'workspaceId': workspace_id,
            'sourceDefinitionId': source_definition_id,
            'name': name,
            'connectionConfiguration': connection_configuration
        }

        return self._request('POST', 'sources/create', data)

    def create_destination(self, workspace_id: str, destination_definition_id: str,
                          name: str, connection_configuration: Dict) -> Dict:
        """Create a new destination"""
        data = {
            'workspaceId': workspace_id,
            'destinationDefinitionId': destination_definition_id,
            'name': name,
            'connectionConfiguration': connection_configuration
        }

        return self._request('POST', 'destinations/create', data)

    def create_connection(self, source_id: str, destination_id: str,
                         sync_catalog: Dict, schedule: Optional[Dict] = None,
                         namespace_definition: str = 'source') -> Dict:
        """
        Create a connection between source and destination

        schedule: {'units': 24, 'timeUnit': 'hours'} for daily sync
        """
        data = {
            'sourceId': source_id,
            'destinationId': destination_id,
            'syncCatalog': sync_catalog,
            'namespaceDefinition': namespace_definition,
            'status': 'active'
        }

        if schedule:
            data['schedule'] = schedule

        return self._request('POST', 'connections/create', data)

    def trigger_sync(self, connection_id: str) -> Dict:
        """Manually trigger a sync"""
        data = {'connectionId': connection_id}

        result = self._request('POST', 'connections/sync', data)

        return {
            'job_id': result.get('job', {}).get('id'),
            'status': result.get('job', {}).get('status')
        }

    def get_job_status(self, job_id: int) -> Dict:
        """Get status of a sync job"""
        data = {'id': job_id}

        result = self._request('POST', 'jobs/get', data)

        job = result.get('job', {})

        return {
            'job_id': job.get('id'),
            'status': job.get('status'),
            'created_at': job.get('createdAt'),
            'updated_at': job.get('updatedAt'),
            'config_type': job.get('configType')
        }

    def wait_for_job_completion(self, job_id: int, timeout: int = 3600,
                                poll_interval: int = 30) -> Dict:
        """Wait for sync job to complete"""
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")

            status = self.get_job_status(job_id)

            # Terminal statuses
            if status['status'] in ['succeeded', 'failed', 'cancelled']:
                return status

            print(f"Job {job_id} status: {status['status']}")
            time.sleep(poll_interval)

    def get_connection_state(self, connection_id: str) -> Dict:
        """Get connection state (for incremental syncs)"""
        data = {'connectionId': connection_id}
        return self._request('POST', 'state/get', data)

    def update_connection(self, connection_id: str, sync_catalog: Optional[Dict] = None,
                         schedule: Optional[Dict] = None, status: Optional[str] = None) -> Dict:
        """Update connection configuration"""
        # First get current connection
        data = {'connectionId': connection_id}
        current = self._request('POST', 'connections/get', data)

        # Update fields
        update_data = {
            'connectionId': connection_id,
            'syncCatalog': sync_catalog or current.get('syncCatalog'),
            'schedule': schedule or current.get('schedule'),
            'status': status or current.get('status'),
            'namespaceDefinition': current.get('namespaceDefinition'),
            'prefix': current.get('prefix', '')
        }

        return self._request('POST', 'connections/update', update_data)

# Usage example
airbyte = AirbyteAPI(base_url='http://localhost:8001/api/v1')

# List workspaces
workspaces = airbyte.list_workspaces()
workspace_id = workspaces[0]['workspaceId']

# List connections
connections = airbyte.list_connections(workspace_id)
print(f"Found {len(connections)} connections")

# Trigger sync
sync_result = airbyte.trigger_sync(connections[0]['connectionId'])
print(f"Sync triggered. Job ID: {sync_result['job_id']}")

# Wait for completion
final_status = airbyte.wait_for_job_completion(sync_result['job_id'])
print(f"Sync completed with status: {final_status['status']}")
```

---

## Fivetran API

Fivetran provides REST API for connector and sync management.

```python
import requests
import base64
from typing import Dict, List, Optional
import time

class FivetranAPI:
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Fivetran API client

        api_key: Fivetran API key
        api_secret: Fivetran API secret
        """
        self.base_url = "https://api.fivetran.com/v1"
        self.auth = self._encode_credentials(api_key, api_secret)

    def _encode_credentials(self, api_key: str, api_secret: str) -> str:
        """Encode API credentials for Basic Auth"""
        credentials = f"{api_key}:{api_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"

        headers = {
            'Authorization': self.auth,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request(method=method, url=url, json=data, headers=headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Fivetran API request failed: {str(e)}")

    def list_connectors(self, group_id: Optional[str] = None) -> List[Dict]:
        """List all connectors, optionally filtered by group"""
        endpoint = f"groups/{group_id}/connectors" if group_id else "connectors"

        result = self._request('GET', endpoint)
        return result.get('data', {}).get('items', [])

    def get_connector(self, connector_id: str) -> Dict:
        """Get connector details"""
        result = self._request('GET', f"connectors/{connector_id}")
        return result.get('data', {})

    def create_connector(self, group_id: str, service: str, config: Dict) -> Dict:
        """
        Create a new connector

        service: Connector type (e.g., 'postgres', 'salesforce', 'google_sheets')
        config: Connector-specific configuration
        """
        data = {
            'service': service,
            'group_id': group_id,
            'config': config
        }

        result = self._request('POST', 'connectors', data)
        return result.get('data', {})

    def update_connector(self, connector_id: str, config: Dict) -> Dict:
        """Update connector configuration"""
        data = {'config': config}

        result = self._request('PATCH', f"connectors/{connector_id}", data)
        return result.get('data', {})

    def sync_connector(self, connector_id: str, force: bool = False) -> Dict:
        """
        Trigger connector sync

        force: Force historical resync
        """
        endpoint = f"connectors/{connector_id}/{'force' if force else 'sync'}"

        result = self._request('POST', endpoint)
        return result.get('data', {})

    def pause_connector(self, connector_id: str) -> Dict:
        """Pause a connector"""
        data = {'paused': True}

        result = self._request('PATCH', f"connectors/{connector_id}", data)
        return result.get('data', {})

    def resume_connector(self, connector_id: str) -> Dict:
        """Resume a paused connector"""
        data = {'paused': False}

        result = self._request('PATCH', f"connectors/{connector_id}", data)
        return result.get('data', {})

    def get_connector_schema(self, connector_id: str) -> Dict:
        """Get connector schema configuration"""
        result = self._request('GET', f"connectors/{connector_id}/schemas")
        return result.get('data', {})

    def update_connector_schema(self, connector_id: str, schema_config: Dict) -> Dict:
        """Update connector schema (enable/disable tables and columns)"""
        result = self._request('PATCH', f"connectors/{connector_id}/schemas", schema_config)
        return result.get('data', {})

    def test_connector(self, connector_id: str) -> Dict:
        """Test connector connection"""
        result = self._request('POST', f"connectors/{connector_id}/test")

        return {
            'succeeded': result.get('data', {}).get('succeeded'),
            'message': result.get('data', {}).get('message')
        }

    def get_connector_sync_status(self, connector_id: str) -> Dict:
        """Get current sync status"""
        connector = self.get_connector(connector_id)

        return {
            'connector_id': connector_id,
            'status': connector.get('status', {}).get('setup_state'),
            'sync_state': connector.get('status', {}).get('sync_state'),
            'update_state': connector.get('status', {}).get('update_state'),
            'is_historical_sync': connector.get('status', {}).get('is_historical_sync'),
            'succeeded_at': connector.get('succeeded_at'),
            'failed_at': connector.get('failed_at')
        }

    def list_groups(self) -> List[Dict]:
        """List all groups (destinations)"""
        result = self._request('GET', 'groups')
        return result.get('data', {}).get('items', [])

    def create_group(self, name: str) -> Dict:
        """Create a new group"""
        data = {'name': name}

        result = self._request('POST', 'groups', data)
        return result.get('data', {})

# Usage example
fivetran = FivetranAPI(
    api_key='your-api-key',
    api_secret='your-api-secret'
)

# List all connectors
connectors = fivetran.list_connectors()
print(f"Found {len(connectors)} connectors")

# Get connector details
connector = fivetran.get_connector('connector_id')
print(f"Connector: {connector.get('schema')}")

# Trigger sync
sync_result = fivetran.sync_connector('connector_id')
print(f"Sync triggered at: {sync_result.get('succeeded_at')}")

# Check sync status
status = fivetran.get_connector_sync_status('connector_id')
print(f"Sync state: {status['sync_state']}")

# Update schema to enable/disable tables
schema_config = {
    'schemas': {
        'public': {
            'enabled': True,
            'tables': {
                'users': {
                    'enabled': True,
                    'columns': {
                        'id': {'enabled': True},
                        'email': {'enabled': True},
                        'password': {'enabled': False}  # Exclude sensitive column
                    }
                }
            }
        }
    }
}

fivetran.update_connector_schema('connector_id', schema_config)
```

---

## Apache Airflow REST API

Airflow 2.0+ provides a comprehensive REST API for DAG and task management.

```python
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

class AirflowAPI:
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize Airflow API client

        base_url: Airflow webserver URL (e.g., 'http://localhost:8080')
        username: Airflow username
        password: Airflow password
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
        self.auth = (username, password)

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                params: Optional[Dict] = None) -> Dict:
        """Make API request"""
        url = f"{self.api_url}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                auth=self.auth,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()

            return response.json() if response.content else {}

        except requests.exceptions.RequestException as e:
            raise Exception(f"Airflow API request failed: {str(e)}")

    def list_dags(self, only_active: bool = True, limit: int = 100) -> List[Dict]:
        """List DAGs"""
        params = {
            'only_active': only_active,
            'limit': limit
        }

        result = self._request('GET', 'dags', params=params)
        return result.get('dags', [])

    def get_dag(self, dag_id: str) -> Dict:
        """Get DAG details"""
        return self._request('GET', f"dags/{dag_id}")

    def pause_dag(self, dag_id: str) -> Dict:
        """Pause a DAG"""
        data = {'is_paused': True}
        return self._request('PATCH', f"dags/{dag_id}", data)

    def unpause_dag(self, dag_id: str) -> Dict:
        """Unpause a DAG"""
        data = {'is_paused': False}
        return self._request('PATCH', f"dags/{dag_id}", data)

    def trigger_dag(self, dag_id: str, logical_date: Optional[str] = None,
                   conf: Optional[Dict] = None) -> Dict:
        """
        Trigger a DAG run

        logical_date: Logical date for the run (ISO format)
        conf: Configuration JSON to pass to the DAG
        """
        data = {}

        if logical_date:
            data['logical_date'] = logical_date
        if conf:
            data['conf'] = conf

        return self._request('POST', f"dags/{dag_id}/dagRuns", data)

    def get_dag_runs(self, dag_id: str, limit: int = 25,
                    state: Optional[str] = None) -> List[Dict]:
        """
        Get DAG runs

        state: Filter by state ('success', 'running', 'failed')
        """
        params = {'limit': limit}

        if state:
            params['state'] = state

        result = self._request('GET', f"dags/{dag_id}/dagRuns", params=params)
        return result.get('dag_runs', [])

    def get_dag_run(self, dag_id: str, dag_run_id: str) -> Dict:
        """Get specific DAG run details"""
        return self._request('GET', f"dags/{dag_id}/dagRuns/{dag_run_id}")

    def get_task_instances(self, dag_id: str, dag_run_id: str) -> List[Dict]:
        """Get task instances for a DAG run"""
        result = self._request('GET', f"dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances")
        return result.get('task_instances', [])

    def get_task_instance(self, dag_id: str, dag_run_id: str, task_id: str) -> Dict:
        """Get specific task instance"""
        return self._request(
            'GET',
            f"dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}"
        )

    def get_task_logs(self, dag_id: str, dag_run_id: str, task_id: str,
                     task_try_number: int = 1) -> str:
        """Get task logs"""
        result = self._request(
            'GET',
            f"dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{task_try_number}"
        )

        return result.get('content', '')

    def clear_task_instance(self, dag_id: str, dag_run_id: str, task_id: str) -> Dict:
        """Clear a task instance (marks for re-run)"""
        data = {
            'dry_run': False,
            'reset_dag_runs': False,
            'only_failed': False,
            'only_running': False
        }

        return self._request(
            'POST',
            f"dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/clear",
            data
        )

    def wait_for_dag_run_completion(self, dag_id: str, dag_run_id: str,
                                    timeout: int = 3600, poll_interval: int = 30) -> Dict:
        """Wait for DAG run to complete"""
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"DAG run did not complete within {timeout} seconds")

            dag_run = self.get_dag_run(dag_id, dag_run_id)
            state = dag_run.get('state')

            # Terminal states
            if state in ['success', 'failed']:
                return dag_run

            print(f"DAG run {dag_run_id} state: {state}")
            time.sleep(poll_interval)

    def get_variables(self) -> List[Dict]:
        """List all Airflow variables"""
        result = self._request('GET', 'variables')
        return result.get('variables', [])

    def set_variable(self, key: str, value: str) -> Dict:
        """Set an Airflow variable"""
        data = {
            'key': key,
            'value': value
        }

        return self._request('POST', 'variables', data)

    def delete_variable(self, key: str) -> bool:
        """Delete an Airflow variable"""
        try:
            self._request('DELETE', f"variables/{key}")
            return True
        except Exception:
            return False

# Usage example
airflow = AirflowAPI(
    base_url='http://localhost:8080',
    username='admin',
    password='admin'
)

# List DAGs
dags = airflow.list_dags()
print(f"Found {len(dags)} active DAGs")

# Trigger DAG with configuration
dag_run = airflow.trigger_dag(
    dag_id='my_etl_pipeline',
    conf={'source': 'api', 'date': '2024-01-01'}
)

print(f"DAG run triggered: {dag_run.get('dag_run_id')}")

# Wait for completion
final_state = airflow.wait_for_dag_run_completion(
    dag_id='my_etl_pipeline',
    dag_run_id=dag_run.get('dag_run_id')
)

if final_state['state'] == 'success':
    print("DAG run completed successfully!")
else:
    print(f"DAG run failed: {final_state.get('state')}")

    # Get failed task logs
    task_instances = airflow.get_task_instances(
        'my_etl_pipeline',
        dag_run.get('dag_run_id')
    )

    for task in task_instances:
        if task['state'] == 'failed':
            logs = airflow.get_task_logs(
                'my_etl_pipeline',
                dag_run.get('dag_run_id'),
                task['task_id']
            )
            print(f"Failed task {task['task_id']} logs:\n{logs}")
```

---

## Orchestration Patterns

### Multi-Tool Pipeline Orchestration

```python
from typing import Dict, List
import time

class DataPipelineOrchestrator:
    def __init__(self, fivetran_api, dbt_api, airflow_api):
        self.fivetran = fivetran_api
        self.dbt = dbt_api
        self.airflow = airflow_api

    def execute_full_pipeline(self, config: Dict) -> Dict:
        """
        Execute complete data pipeline:
        1. Fivetran sync (EL)
        2. dbt transformation (T)
        3. Airflow downstream tasks
        """
        results = {
            'fivetran': {},
            'dbt': {},
            'airflow': {},
            'overall_status': 'running'
        }

        try:
            # Step 1: Trigger Fivetran sync
            print("Step 1: Triggering Fivetran sync...")
            fivetran_result = self.fivetran.sync_connector(config['fivetran_connector_id'])

            # Wait for Fivetran sync
            while True:
                status = self.fivetran.get_connector_sync_status(config['fivetran_connector_id'])
                if status['sync_state'] == 'scheduled':
                    break
                time.sleep(60)

            results['fivetran'] = {'status': 'success', 'synced_at': status['succeeded_at']}
            print("Fivetran sync completed successfully")

            # Step 2: Trigger dbt job
            print("Step 2: Triggering dbt transformation...")
            dbt_run = self.dbt.trigger_job(
                job_id=config['dbt_job_id'],
                cause="Triggered after Fivetran sync"
            )

            dbt_status = self.dbt.wait_for_run_completion(dbt_run['id'])

            if dbt_status['status'] != 10:  # 10 = Success
                raise Exception(f"dbt job failed: {dbt_status['status_message']}")

            results['dbt'] = {'status': 'success', 'run_id': dbt_run['id']}
            print("dbt transformation completed successfully")

            # Step 3: Trigger Airflow DAG for downstream tasks
            print("Step 3: Triggering Airflow DAG...")
            airflow_run = self.airflow.trigger_dag(
                dag_id=config['airflow_dag_id'],
                conf={'dbt_run_id': dbt_run['id']}
            )

            airflow_status = self.airflow.wait_for_dag_run_completion(
                dag_id=config['airflow_dag_id'],
                dag_run_id=airflow_run['dag_run_id']
            )

            if airflow_status['state'] != 'success':
                raise Exception(f"Airflow DAG failed: {airflow_status['state']}")

            results['airflow'] = {
                'status': 'success',
                'dag_run_id': airflow_run['dag_run_id']
            }
            print("Airflow DAG completed successfully")

            results['overall_status'] = 'success'

        except Exception as e:
            results['overall_status'] = 'failed'
            results['error'] = str(e)
            print(f"Pipeline failed: {str(e)}")

        return results

# Usage
orchestrator = DataPipelineOrchestrator(fivetran, dbt, airflow)

pipeline_result = orchestrator.execute_full_pipeline({
    'fivetran_connector_id': 'my_connector',
    'dbt_job_id': 12345,
    'airflow_dag_id': 'downstream_processing'
})

print(f"Pipeline status: {pipeline_result['overall_status']}")
```

### Error Handling and Retry Pattern

```python
from functools import wraps
import time

def retry_on_failure(max_retries=3, backoff_factor=2, exceptions=(Exception,)):
    """Decorator for retrying failed operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise

                    wait_time = backoff_factor ** attempt
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

        return wrapper
    return decorator

class ResilientETLOrchestrator:
    def __init__(self, apis):
        self.apis = apis

    @retry_on_failure(max_retries=3, backoff_factor=2)
    def trigger_sync_with_retry(self, connector_id: str):
        """Trigger sync with automatic retry"""
        return self.apis['fivetran'].sync_connector(connector_id)

    @retry_on_failure(max_retries=3, backoff_factor=5)
    def trigger_dbt_with_retry(self, job_id: int):
        """Trigger dbt job with automatic retry"""
        return self.apis['dbt'].trigger_job(job_id)

    def execute_with_fallback(self, primary_func, fallback_func, *args, **kwargs):
        """Execute primary function with fallback on failure"""
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            print(f"Primary execution failed: {str(e)}")
            print("Attempting fallback...")
            return fallback_func(*args, **kwargs)
```

---

## Best Practices

### 1. Comprehensive Logging

```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'etl_orchestration_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LoggedETLOrchestrator:
    def __init__(self, apis):
        self.apis = apis

    def trigger_pipeline(self, config):
        logger.info(f"Starting pipeline with config: {config}")

        try:
            # Fivetran
            logger.info("Triggering Fivetran sync...")
            fivetran_result = self.apis['fivetran'].sync_connector(config['connector_id'])
            logger.info(f"Fivetran sync triggered: {fivetran_result}")

            # dbt
            logger.info("Triggering dbt job...")
            dbt_result = self.apis['dbt'].trigger_job(config['job_id'])
            logger.info(f"dbt job triggered: {dbt_result}")

            logger.info("Pipeline completed successfully")
            return {'status': 'success'}

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise
```

### 2. Webhook Integration for Event-Driven Pipelines

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/fivetran', methods=['POST'])
def fivetran_webhook():
    """Handle Fivetran sync completion webhook"""
    data = request.json

    if data.get('event') == 'sync_end' and data.get('status') == 'success':
        # Trigger dbt job
        dbt_run = dbt_api.trigger_job(
            job_id=12345,
            cause=f"Triggered by Fivetran connector {data.get('connector_id')}"
        )

        return jsonify({'status': 'dbt_triggered', 'run_id': dbt_run['id']}), 200

    return jsonify({'status': 'ignored'}), 200

@app.route('/webhook/dbt', methods=['POST'])
def dbt_webhook():
    """Handle dbt job completion webhook"""
    data = request.json

    if data.get('runStatus') == 'Success':
        # Trigger downstream processes
        airflow_api.trigger_dag('downstream_dag', conf={'dbt_run_id': data.get('runId')})

        return jsonify({'status': 'airflow_triggered'}), 200

    return jsonify({'status': 'ignored'}), 200

if __name__ == '__main__':
    app.run(port=5000)
```

### 3. Monitoring and Alerting

```python
import requests

class ETLMonitor:
    def __init__(self, slack_webhook_url):
        self.slack_webhook = slack_webhook_url

    def send_alert(self, message: str, severity: str = 'info'):
        """Send alert to Slack"""
        colors = {
            'info': '#36a64f',
            'warning': '#ff9800',
            'error': '#ff0000'
        }

        payload = {
            'attachments': [{
                'color': colors.get(severity, '#36a64f'),
                'text': message,
                'ts': time.time()
            }]
        }

        requests.post(self.slack_webhook, json=payload)

    def monitor_pipeline(self, pipeline_func, *args, **kwargs):
        """Monitor pipeline execution and send alerts"""
        try:
            start_time = time.time()
            result = pipeline_func(*args, **kwargs)
            duration = time.time() - start_time

            self.send_alert(
                f"Pipeline completed successfully in {duration:.2f}s",
                severity='info'
            )

            return result

        except Exception as e:
            self.send_alert(
                f"Pipeline failed: {str(e)}",
                severity='error'
            )
            raise

# Usage
monitor = ETLMonitor(slack_webhook_url='https://hooks.slack.com/services/XXX')
monitor.monitor_pipeline(orchestrator.execute_full_pipeline, config)
```

---

## Summary

This guide covers comprehensive API integration patterns for major ETL/ELT tools:

- **dbt Cloud**: Administrative API and GraphQL Metadata API for transformation orchestration
- **Airbyte**: REST API for open-source EL connector management
- **Fivetran**: REST API for managed EL with schema control
- **Airflow**: REST API for workflow orchestration

**Key Takeaways:**
1. Orchestrate multi-tool pipelines with proper sequencing
2. Implement retry logic and error handling for resilience
3. Use webhooks for event-driven architectures
4. Monitor pipeline execution with comprehensive logging
5. Implement alerting for failures and SLA breaches
6. Track job metadata for lineage and debugging
7. Secure API credentials using secrets management

For detailed API documentation, refer to vendor resources:
- dbt Cloud: https://docs.getdbt.com/dbt-cloud/api-v2
- Airbyte: https://docs.airbyte.com/api-documentation
- Fivetran: https://fivetran.com/docs/rest-api
- Airflow: https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html
