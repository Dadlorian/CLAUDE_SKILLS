# CRM Integration Patterns for Product Managers

## Overview

CRM systems like Salesforce and HubSpot are critical for managing customer relationships, tracking deals, and coordinating between product, sales, and customer success teams. This guide covers integration patterns, authentication strategies, and workflow automation for product teams using CRM APIs.

### Why CRM Integration Matters for PMs

Product Managers benefit from CRM integration to:
- Access customer feedback and support tickets
- Track feature requests from key accounts
- Monitor product adoption across customers
- Align product roadmap with customer opportunities
- Automate customer segmentation and messaging
- Generate customer insights for product decisions
- Coordinate with sales and customer success teams

---

## Salesforce API Integration

### Authentication Methods

Salesforce offers multiple authentication approaches depending on use case.

#### OAuth 2.0 Flow (Recommended for Apps)

```bash
# Environment setup
SALESFORCE_CLIENT_ID=your_connected_app_client_id
SALESFORCE_CLIENT_SECRET=your_connected_app_client_secret
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
SALESFORCE_USERNAME=pm-integration@company.com
SALESFORCE_PASSWORD=your_password
```

#### OAuth 2.0 Implementation

```python
import requests
import json
from typing import Optional

class SalesforceAuth:
    def __init__(self, client_id: str, client_secret: str, instance_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.instance_url = instance_url
        self.access_token = None
        self.token_type = None

    def authenticate(self, username: str, password: str, security_token: str = "") -> dict:
        """Authenticate using username/password flow"""
        auth_url = f"{self.instance_url}/services/oauth2/token"

        payload = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': username,
            'password': password + security_token
        }

        response = requests.post(auth_url, data=payload)

        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.token_type = data['token_type']
            return data
        else:
            raise Exception(f"Authentication failed: {response.text}")

    def get_headers(self) -> dict:
        """Get authorization headers for API requests"""
        return {
            'Authorization': f'{self.token_type} {self.access_token}',
            'Content-Type': 'application/json',
        }

    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        auth_url = f"{self.instance_url}/services/oauth2/token"

        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token
        }

        response = requests.post(auth_url, data=payload)
        return response.json()
```

### SOQL Query Language

Salesforce Object Query Language (SOQL) allows querying objects and relationships.

```python
class SalesforceClient:
    def __init__(self, auth: SalesforceAuth):
        self.auth = auth
        self.instance_url = auth.instance_url

    def query(self, soql: str) -> dict:
        """Execute SOQL query"""
        query_url = f"{self.instance_url}/services/data/v57.0/query"

        params = {'q': soql}
        response = requests.get(
            query_url,
            params=params,
            headers=self.auth.get_headers()
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Query failed: {response.text}")

# Example SOQL queries for PMs
class ProductManagerQueries:
    @staticmethod
    def get_accounts_with_feature_requests(feature_name: str) -> str:
        """Get all accounts interested in a specific feature"""
        return f"""
            SELECT Id, Name, Industry, Revenue, Phone
            FROM Account
            WHERE Id IN (
                SELECT AccountId FROM Opportunity
                WHERE Description LIKE '%{feature_name}%'
                AND IsClosed = false
            )
        """

    @staticmethod
    def get_product_adoption_by_account() -> str:
        """Get product adoption metrics by account"""
        return """
            SELECT
                Account.Name,
                COUNT(AccountId) as Feature_Count,
                MAX(LastActivityDate) as Last_Activity
            FROM Opportunity
            WHERE StageName = 'Closed Won'
            GROUP BY AccountId
            ORDER BY Feature_Count DESC
        """

    @staticmethod
    def get_feature_requests() -> str:
        """Get all feature requests from opportunities"""
        return """
            SELECT Id, Name, AccountId, Description, CreatedDate
            FROM Opportunity
            WHERE Description != null
            AND StageName NOT IN ('Closed Lost', 'Closed Won')
            ORDER BY CreatedDate DESC
        """

    @staticmethod
    def get_customer_health_score() -> str:
        """Get customers with health indicators"""
        return """
            SELECT
                Account.Name,
                Account.Industry,
                COUNT(Task.Id) as Task_Count,
                MAX(Activity_Date__c) as Last_Activity
            FROM Account
            LEFT JOIN Task ON Account.Id = Task.WhoId
            GROUP BY Account.Id, Account.Name, Account.Industry
        """
```

### Creating and Updating Records

```python
class SalesforceRecordManager:
    def __init__(self, client: SalesforceClient):
        self.client = client

    def create_record(self, sobject_type: str, fields: dict) -> str:
        """Create a new Salesforce record"""
        create_url = f"{self.client.instance_url}/services/data/v57.0/sobjects/{sobject_type}"

        response = requests.post(
            create_url,
            json=fields,
            headers=self.client.auth.get_headers()
        )

        if response.status_code == 201:
            return response.json()['id']
        else:
            raise Exception(f"Record creation failed: {response.text}")

    def update_record(self, sobject_type: str, record_id: str, fields: dict):
        """Update an existing Salesforce record"""
        update_url = f"{self.client.instance_url}/services/data/v57.0/sobjects/{sobject_type}/{record_id}"

        response = requests.patch(
            update_url,
            json=fields,
            headers=self.client.auth.get_headers()
        )

        return response.status_code == 204

    def create_feature_request(self, account_id: str, feature_name: str,
                               description: str, priority: str = "Medium") -> str:
        """Create a feature request opportunity"""
        fields = {
            'AccountId': account_id,
            'Name': f"Feature Request: {feature_name}",
            'StageName': 'Prospecting',
            'Description': description,
            'Priority__c': priority,
            'CloseDate': '2024-12-31',
            'RecordTypeId': 'FEATURE_REQUEST_RT'  # Custom record type
        }

        return self.create_record('Opportunity', fields)

    def create_account_product_feedback(self, account_id: str, feedback: dict):
        """Create product feedback for an account"""
        feedback_fields = {
            'AccountId__c': account_id,
            'Feedback_Type__c': feedback.get('type', 'General'),
            'Feedback_Content__c': feedback.get('content'),
            'Sentiment__c': feedback.get('sentiment', 'Neutral'),
            'Source__c': feedback.get('source', 'Manual'),
            'CreatedDate': feedback.get('date')
        }

        return self.create_record('Product_Feedback__c', feedback_fields)
```

---

## HubSpot API Integration

### Authentication & Setup

HubSpot uses API keys or OAuth for authentication.

```bash
# Using API key (simpler for internal tools)
HUBSPOT_API_KEY=your_private_app_key

# Or OAuth
HUBSPOT_CLIENT_ID=your_client_id
HUBSPOT_CLIENT_SECRET=your_client_secret
HUBSPOT_REDIRECT_URI=https://your-app.com/callback
```

#### HubSpot API Client Implementation

```python
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class HubSpotClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> dict:
        """Make GET request to HubSpot API"""
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: dict) -> dict:
        """Make POST request to HubSpot API"""
        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def _patch(self, endpoint: str, data: dict) -> dict:
        """Make PATCH request to HubSpot API"""
        response = requests.patch(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def get_companies(self, limit: int = 100, properties: List[str] = None) -> List[dict]:
        """Retrieve companies from HubSpot"""
        properties = properties or [
            'name',
            'industry',
            'revenue',
            'numberofemployees',
            'lifecyclestage'
        ]

        payload = {
            'limit': limit,
            'properties': properties,
        }

        response = self._post('/crm/v3/objects/companies/search', payload)
        return response.get('results', [])

    def get_deals(self, filter_property: Optional[str] = None,
                  filter_value: Optional[str] = None) -> List[dict]:
        """Retrieve deals with optional filtering"""
        properties = [
            'dealname',
            'dealstage',
            'closedate',
            'amount',
            'hubspot_owner_id'
        ]

        payload = {
            'limit': 100,
            'properties': properties,
        }

        if filter_property and filter_value:
            payload['filterGroups'] = [{
                'filters': [{
                    'propertyName': filter_property,
                    'operator': 'EQ',
                    'value': filter_value
                }]
            }]

        response = self._post('/crm/v3/objects/deals/search', payload)
        return response.get('results', [])

    def get_contacts(self, email: Optional[str] = None) -> List[dict]:
        """Get contacts with optional email filter"""
        properties = [
            'firstname',
            'lastname',
            'email',
            'phone',
            'lifecyclestage',
            'hs_lead_status'
        ]

        payload = {
            'limit': 100,
            'properties': properties,
        }

        if email:
            payload['filterGroups'] = [{
                'filters': [{
                    'propertyName': 'email',
                    'operator': 'EQ',
                    'value': email
                }]
            }]

        response = self._post('/crm/v3/objects/contacts/search', payload)
        return response.get('results', [])

    def create_contact(self, email: str, first_name: str, last_name: str) -> str:
        """Create a new contact in HubSpot"""
        payload = {
            'properties': {
                'email': email,
                'firstname': first_name,
                'lastname': last_name,
            }
        }

        response = self._post('/crm/v3/objects/contacts', payload)
        return response['id']

    def update_contact(self, contact_id: str, properties: dict) -> bool:
        """Update contact properties"""
        payload = {
            'properties': properties
        }

        self._patch(f'/crm/v3/objects/contacts/{contact_id}', payload)
        return True

    def create_custom_object(self, object_type: str, properties: dict) -> str:
        """Create custom object (e.g., Feature Request)"""
        payload = {
            'properties': properties
        }

        response = self._post(f'/crm/v3/objects/{object_type}', payload)
        return response['id']

    def associate_objects(self, object_type1: str, object_id1: str,
                         object_type2: str, object_id2: str,
                         association_type: str) -> bool:
        """Create association between two objects"""
        endpoint = (f'/crm/v3/objects/{object_type1}/{object_id1}/'
                   f'associations/{object_type2}/{object_id2}/{association_type}')

        self._put(endpoint, {})
        return True
```

### PM-Focused HubSpot Workflows

```python
class ProductManagerWorkflows:
    def __init__(self, hubspot_client: HubSpotClient):
        self.client = hubspot_client

    def track_feature_adoption(self, company_id: str, feature_name: str,
                               adoption_percentage: float):
        """Log feature adoption for a company"""
        properties = {
            'feature_name': feature_name,
            'adoption_percentage': adoption_percentage,
            'adoption_date': datetime.now().isoformat()
        }

        self.client.update_contact(company_id, properties)

    def create_feature_request_from_feedback(self, contact_email: str,
                                             feature_request: dict):
        """Create feature request custom object from customer feedback"""
        contacts = self.client.get_contacts(email=contact_email)

        if not contacts:
            raise ValueError(f"Contact not found: {contact_email}")

        contact_id = contacts[0]['id']
        contact_name = contacts[0]['properties'].get('firstname', 'Unknown')

        # Create feature request custom object
        request_properties = {
            'feature_title': feature_request.get('title'),
            'description': feature_request.get('description'),
            'priority': feature_request.get('priority', 'Medium'),
            'requested_by_email': contact_email,
            'status': 'New',
            'created_date': datetime.now().isoformat()
        }

        request_id = self.client.create_custom_object('feature_requests', request_properties)

        # Associate with contact
        self.client.associate_objects('contacts', contact_id,
                                    'feature_requests', request_id,
                                    'contact_to_request')

        return request_id

    def get_customer_engagement_report(self) -> dict:
        """Generate customer engagement report for product review"""
        companies = self.client.get_companies()

        engagement_report = {
            'total_companies': len(companies),
            'by_industry': {},
            'by_revenue': {
                'enterprise': 0,
                'mid_market': 0,
                'smb': 0
            },
            'by_lifecycle_stage': {}
        }

        for company in companies:
            properties = company.get('properties', {})
            industry = properties.get('industry', 'Unknown')
            revenue = properties.get('revenue', 0)
            lifecycle = properties.get('lifecyclestage', 'Unknown')

            # Group by industry
            if industry not in engagement_report['by_industry']:
                engagement_report['by_industry'][industry] = 0
            engagement_report['by_industry'][industry] += 1

            # Group by revenue
            if revenue > 50000000:
                engagement_report['by_revenue']['enterprise'] += 1
            elif revenue > 10000000:
                engagement_report['by_revenue']['mid_market'] += 1
            else:
                engagement_report['by_revenue']['smb'] += 1

            # Group by lifecycle
            if lifecycle not in engagement_report['by_lifecycle_stage']:
                engagement_report['by_lifecycle_stage'][lifecycle] = 0
            engagement_report['by_lifecycle_stage'][lifecycle] += 1

        return engagement_report

    def identify_product_champions(self) -> List[dict]:
        """Identify potential product champions from engaged contacts"""
        contacts = self.client.get_contacts()

        champions = []
        for contact in contacts:
            properties = contact.get('properties', {})
            engagement_score = self._calculate_engagement_score(properties)

            if engagement_score > 7:
                champions.append({
                    'id': contact['id'],
                    'email': properties.get('email'),
                    'name': f"{properties.get('firstname', '')} {properties.get('lastname', '')}",
                    'engagement_score': engagement_score,
                    'lifecycle_stage': properties.get('lifecyclestage')
                })

        return sorted(champions, key=lambda x: x['engagement_score'], reverse=True)

    @staticmethod
    def _calculate_engagement_score(properties: dict) -> float:
        """Calculate engagement score based on properties"""
        score = 0

        # Score based on lifecycle stage
        lifecycle = properties.get('lifecyclestage', '')
        lifecycle_scores = {
            'customer': 10,
            'evangelist': 9,
            'sales qualified lead': 7,
            'opportunity': 6,
            'subscriber': 3,
            'lead': 1
        }
        score += lifecycle_scores.get(lifecycle.lower(), 0)

        # Score based on lead status
        lead_status = properties.get('hs_lead_status', '')
        if lead_status in ['Open', 'In Progress', 'Attempted to Contact']:
            score += 3

        return min(score, 10)  # Cap at 10
```

---

## Sync Patterns & Data Synchronization

### Real-time Webhook Synchronization

```python
from flask import Flask, request
import hmac
import hashlib
import json

app = Flask(__name__)

class HubSpotWebhookHandler:
    def __init__(self, client_secret: str):
        self.client_secret = client_secret

    def verify_webhook_signature(self, request_body: str, x_hubspot_signature: str) -> bool:
        """Verify HubSpot webhook signature"""
        expected_signature = hmac.new(
            self.client_secret.encode(),
            request_body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, x_hubspot_signature)

    def handle_deal_update(self, deal_data: dict):
        """Handle deal update webhook"""
        deal_id = deal_data['objectId']
        changes = deal_data.get('changeSource', 'INTEGRATION')

        # Update internal systems
        if deal_data.get('eventType') == 'property_change':
            property_name = deal_data['propertyName']
            new_value = deal_data['propertyValue']

            # Sync to product management system
            self._sync_to_product_db(deal_id, property_name, new_value)

    def handle_company_update(self, company_data: dict):
        """Handle company update webhook"""
        company_id = company_data['objectId']

        # Trigger product adoption analysis
        self._trigger_adoption_analysis(company_id)

    @staticmethod
    def _sync_to_product_db(deal_id: str, property_name: str, value: str):
        """Sync CRM data to product database"""
        # Implementation depends on your database
        pass

    @staticmethod
    def _trigger_adoption_analysis(company_id: str):
        """Trigger analysis of product adoption for company"""
        pass

@app.route('/webhooks/hubspot', methods=['POST'])
def hubspot_webhook():
    webhook_handler = HubSpotWebhookHandler(os.getenv('HUBSPOT_CLIENT_SECRET'))

    # Verify signature
    if not webhook_handler.verify_webhook_signature(
        request.get_data(as_text=True),
        request.headers.get('X-HubSpot-Request-Signature')
    ):
        return {'error': 'Invalid signature'}, 401

    # Process events
    events = request.json
    for event in events:
        if event['objectType'] == 'deal':
            webhook_handler.handle_deal_update(event)
        elif event['objectType'] == 'company':
            webhook_handler.handle_company_update(event)

    return {'status': 'ok'}, 200
```

### Batch Sync with Polling

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json

class CRMSyncScheduler:
    def __init__(self, salesforce_client, hubspot_client):
        self.salesforce = salesforce_client
        self.hubspot = hubspot_client
        self.scheduler = BackgroundScheduler()

    def start_sync(self):
        """Start scheduled CRM synchronization"""
        # Sync every 6 hours
        self.scheduler.add_job(
            self.sync_accounts,
            'interval',
            hours=6,
            id='sync_accounts'
        )

        # Sync feature requests every 2 hours
        self.scheduler.add_job(
            self.sync_feature_requests,
            'interval',
            hours=2,
            id='sync_feature_requests'
        )

        self.scheduler.start()

    def sync_accounts(self):
        """Sync accounts from Salesforce to HubSpot"""
        # Query Salesforce for recent accounts
        soql = "SELECT Id, Name, Industry FROM Account WHERE LastModifiedDate = LAST_N_DAYS:1"
        sf_accounts = self.salesforce.query(soql)

        for sf_account in sf_accounts.get('records', []):
            # Find matching HubSpot company
            hs_companies = self.hubspot.get_companies(
                properties=['name', 'industry', 'salesforce_id']
            )

            matching_company = next(
                (c for c in hs_companies
                 if c['properties'].get('salesforce_id') == sf_account['Id']),
                None
            )

            if matching_company:
                # Update HubSpot company
                self.hubspot.update_contact(
                    matching_company['id'],
                    {
                        'industry': sf_account.get('Industry'),
                        'hs_sync_timestamp': datetime.now().isoformat()
                    }
                )

    def sync_feature_requests(self):
        """Sync feature requests from Salesforce to internal system"""
        soql = """
            SELECT Id, Name, AccountId, Description, CreatedDate
            FROM Opportunity
            WHERE RecordTypeId = 'FEATURE_REQUEST_RT'
            AND CreatedDate = LAST_N_DAYS:1
        """

        requests = self.salesforce.query(soql)

        for request in requests.get('records', []):
            # Process and store feature request
            self._store_feature_request({
                'crm_id': request['Id'],
                'title': request['Name'],
                'account_id': request['AccountId'],
                'description': request['Description'],
                'created_at': request['CreatedDate']
            })

    @staticmethod
    def _store_feature_request(feature_data: dict):
        """Store feature request in internal database"""
        # Implementation depends on your database
        pass
```

---

## Error Handling & Rate Limiting

### Retry Logic with Exponential Backoff

```python
import time
from functools import wraps
from typing import Callable

def retry_with_backoff(max_retries: int = 3, base_wait: float = 1.0):
    """Decorator for API calls with exponential backoff"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            retries = 0
            wait_time = base_wait

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    retries += 1

                    if retries >= max_retries:
                        raise

                    # Check for rate limit headers
                    if hasattr(e, 'response') and e.response:
                        retry_after = e.response.headers.get('Retry-After')
                        if retry_after:
                            wait_time = float(retry_after)

                    print(f"Retry {retries}/{max_retries} after {wait_time}s")
                    time.sleep(wait_time)
                    wait_time *= 2  # Exponential backoff

        return wrapper
    return decorator
```

### Rate Limit Management

```python
class RateLimitManager:
    def __init__(self, max_requests_per_minute: int = 600):
        self.max_requests = max_requests_per_minute
        self.request_times = []

    def wait_if_needed(self):
        """Wait if approaching rate limit"""
        now = time.time()

        # Remove old requests outside the window
        self.request_times = [
            req_time for req_time in self.request_times
            if now - req_time < 60
        ]

        if len(self.request_times) >= self.max_requests:
            # Calculate wait time
            oldest_request = self.request_times[0]
            wait_time = 60 - (now - oldest_request)
            print(f"Rate limit approaching, waiting {wait_time}s")
            time.sleep(wait_time + 0.1)

        self.request_times.append(now)
```

---

## Testing CRM Integrations

### Mock CRM Responses

```python
import pytest
from unittest.mock import Mock, patch

class TestCRMIntegration:
    @pytest.fixture
    def mock_hubspot_client(self):
        client = Mock()
        client.get_companies.return_value = [
            {
                'id': 'company_123',
                'properties': {
                    'name': 'Acme Corp',
                    'industry': 'Technology',
                    'revenue': 50000000
                }
            }
        ]
        return client

    def test_create_feature_request(self, mock_hubspot_client):
        workflow = ProductManagerWorkflows(mock_hubspot_client)

        request_id = workflow.create_feature_request_from_feedback(
            'user@acme.com',
            {'title': 'Export to CSV', 'description': 'Export reports as CSV'}
        )

        assert request_id is not None

    def test_get_customer_engagement_report(self, mock_hubspot_client):
        workflow = ProductManagerWorkflows(mock_hubspot_client)
        report = workflow.get_customer_engagement_report()

        assert report['total_companies'] == 1
        assert report['by_revenue']['enterprise'] == 1
```

---

## Conclusion

CRM integration is essential for product managers to stay connected with customers and align product development with business objectives. By implementing robust Salesforce and HubSpot integrations with proper authentication, error handling, and data synchronization patterns, PMs can leverage customer data to inform product decisions.

Key takeaways:
- Use OAuth 2.0 for secure authentication
- Implement SOQL/HubSpot Search API for flexible querying
- Create custom objects for product-specific data (feature requests, adoption metrics)
- Use webhooks for real-time synchronization where appropriate
- Implement retry logic with exponential backoff for reliability
- Monitor rate limits and implement backoff strategies
- Test integrations thoroughly with mock data
- Document your CRM schema and field mappings
