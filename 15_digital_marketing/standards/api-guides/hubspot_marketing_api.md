# HubSpot Marketing Hub API Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Contacts API](#contacts-api)
4. [Companies API](#companies-api)
5. [Deals API](#deals-api)
6. [Email Marketing API](#email-marketing-api)
7. [Workflows API](#workflows-api)
8. [Analytics API](#analytics-api)
9. [Forms API](#forms-api)
10. [Lists & Segmentation](#lists--segmentation)
11. [Rate Limits & Quotas](#rate-limits--quotas)
12. [Error Handling](#error-handling)
13. [Best Practices](#best-practices)
14. [Testing Strategies](#testing-strategies)

---

## Overview

HubSpot's Marketing Hub API provides comprehensive programmatic access to CRM data, marketing automation, email marketing, analytics, and workflow management. The API enables seamless integration with your marketing technology stack.

### Use Cases

**Marketing Automation:**
- Automated lead nurturing workflows
- Behavioral email triggers
- Lead scoring and qualification
- Multi-channel campaign orchestration

**CRM Integration:**
- Bi-directional contact synchronization
- Company and deal management
- Custom property management
- Activity tracking and attribution

**Email Marketing:**
- Programmatic email campaign creation
- List management and segmentation
- A/B testing automation
- Performance analytics and reporting

**Analytics & Reporting:**
- Custom dashboard creation
- Marketing attribution reporting
- ROI and conversion tracking
- Multi-touch attribution analysis

### API Architecture

- **REST API**: Standard HTTP methods (GET, POST, PATCH, DELETE)
- **API Version**: v3 (current stable)
- **Base URL**: `https://api.hubapi.com`
- **Data Format**: JSON
- **Authentication**: OAuth 2.0 and API Keys

---

## Authentication & Authorization

### Authentication Methods

HubSpot supports two primary authentication methods:

1. **OAuth 2.0** (Recommended for integrations)
2. **API Keys** (Deprecated for new integrations)

### OAuth 2.0 Implementation

#### Step 1: Create HubSpot App

```yaml
1. Navigate to: https://developers.hubspot.com/
2. Create new app in Developer Account
3. Configure app settings:
   - App name: Your Integration Name
   - Description: Integration description
   - Redirect URLs: https://yourdomain.com/oauth/callback
```

#### Step 2: Configure Scopes

```yaml
Required OAuth Scopes:
  CRM:
    - crm.objects.contacts.read
    - crm.objects.contacts.write
    - crm.objects.companies.read
    - crm.objects.companies.write
    - crm.objects.deals.read
    - crm.objects.deals.write

  Marketing:
    - content
    - forms
    - automation
    - transactional-email

  Analytics:
    - analytics.read
```

### Python Authentication Implementation

```python
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode

class HubSpotAuth:
    """Handle HubSpot OAuth 2.0 authentication"""

    AUTHORIZATION_URL = 'https://app.hubspot.com/oauth/authorize'
    TOKEN_URL = 'https://api.hubapi.com/oauth/v1/token'
    BASE_URL = 'https://api.hubapi.com'

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None

    def get_authorization_url(self, scopes):
        """Generate OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes)
        }

        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    def exchange_code_for_tokens(self, code):
        """Exchange authorization code for access and refresh tokens"""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()

        token_data = response.json()
        self._update_tokens(token_data)

        return token_data

    def refresh_access_token(self):
        """Refresh access token using refresh token"""
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()

        token_data = response.json()
        self._update_tokens(token_data)

        return token_data

    def _update_tokens(self, token_data):
        """Update stored tokens"""
        self.access_token = token_data['access_token']
        self.refresh_token = token_data['refresh_token']

        expires_in = token_data.get('expires_in', 21600)  # Default 6 hours
        self.expires_at = datetime.now() + timedelta(seconds=expires_in)

    def get_valid_token(self):
        """Get valid access token, refreshing if necessary"""
        if not self.access_token or datetime.now() >= self.expires_at:
            if self.refresh_token:
                self.refresh_access_token()
            else:
                raise Exception("No valid tokens available. Please re-authenticate.")

        return self.access_token

    def get_headers(self):
        """Get authorization headers for API requests"""
        return {
            'Authorization': f'Bearer {self.get_valid_token()}',
            'Content-Type': 'application/json'
        }

# Usage
auth = HubSpotAuth(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    redirect_uri='https://yourdomain.com/oauth/callback'
)

# Generate authorization URL
scopes = [
    'crm.objects.contacts.read',
    'crm.objects.contacts.write',
    'automation'
]
auth_url = auth.get_authorization_url(scopes)
print(f"Authorize at: {auth_url}")

# After user authorization, exchange code for tokens
code = 'authorization_code_from_callback'
tokens = auth.exchange_code_for_tokens(code)
```

### JavaScript Authentication Implementation

```javascript
const axios = require('axios');

class HubSpotAuth {
  constructor(clientId, clientSecret, redirectUri) {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.redirectUri = redirectUri;
    this.authorizationUrl = 'https://app.hubspot.com/oauth/authorize';
    this.tokenUrl = 'https://api.hubapi.com/oauth/v1/token';
    this.accessToken = null;
    this.refreshToken = null;
    this.expiresAt = null;
  }

  getAuthorizationUrl(scopes) {
    const params = new URLSearchParams({
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      scope: scopes.join(' '),
    });

    return `${this.authorizationUrl}?${params.toString()}`;
  }

  async exchangeCodeForTokens(code) {
    const data = {
      grant_type: 'authorization_code',
      client_id: this.clientId,
      client_secret: this.clientSecret,
      redirect_uri: this.redirectUri,
      code: code,
    };

    const response = await axios.post(this.tokenUrl, data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    this.updateTokens(response.data);
    return response.data;
  }

  async refreshAccessToken() {
    const data = {
      grant_type: 'refresh_token',
      client_id: this.clientId,
      client_secret: this.clientSecret,
      refresh_token: this.refreshToken,
    };

    const response = await axios.post(this.tokenUrl, data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    this.updateTokens(response.data);
    return response.data;
  }

  updateTokens(tokenData) {
    this.accessToken = tokenData.access_token;
    this.refreshToken = tokenData.refresh_token;

    const expiresIn = tokenData.expires_in || 21600;
    this.expiresAt = new Date(Date.now() + expiresIn * 1000);
  }

  async getValidToken() {
    if (!this.accessToken || new Date() >= this.expiresAt) {
      if (this.refreshToken) {
        await this.refreshAccessToken();
      } else {
        throw new Error('No valid tokens available. Please re-authenticate.');
      }
    }

    return this.accessToken;
  }

  async getHeaders() {
    const token = await this.getValidToken();
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }
}

module.exports = HubSpotAuth;
```

---

## Contacts API

### Managing Contacts

```python
class HubSpotContacts:
    """HubSpot Contacts API client"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.hubapi.com/crm/v3/objects/contacts'

    def create_contact(self, properties):
        """Create a new contact"""
        url = self.base_url

        data = {
            'properties': properties
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def get_contact(self, contact_id, properties=None):
        """Get contact by ID"""
        url = f"{self.base_url}/{contact_id}"

        params = {}
        if properties:
            params['properties'] = ','.join(properties)

        response = requests.get(
            url,
            headers=self.auth.get_headers(),
            params=params
        )
        response.raise_for_status()

        return response.json()

    def get_contact_by_email(self, email):
        """Get contact by email address"""
        url = f"{self.base_url}/{email}"
        params = {'idProperty': 'email'}

        response = requests.get(
            url,
            headers=self.auth.get_headers(),
            params=params
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    def update_contact(self, contact_id, properties):
        """Update contact properties"""
        url = f"{self.base_url}/{contact_id}"

        data = {
            'properties': properties
        }

        response = requests.patch(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def search_contacts(self, filters, properties=None, limit=100):
        """Search contacts with filters"""
        url = f"{self.base_url}/search"

        data = {
            'filterGroups': filters,
            'properties': properties or [],
            'limit': limit
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def batch_create_contacts(self, contacts):
        """Create multiple contacts in batch"""
        url = f"{self.base_url}/batch/create"

        data = {
            'inputs': [
                {'properties': contact} for contact in contacts
            ]
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def batch_update_contacts(self, updates):
        """Update multiple contacts in batch"""
        url = f"{self.base_url}/batch/update"

        data = {
            'inputs': updates
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def associate_contact(self, contact_id, to_object_type, to_object_id, association_type):
        """Create association between contact and another object"""
        url = f"{self.base_url}/{contact_id}/associations/{to_object_type}/{to_object_id}/{association_type}"

        response = requests.put(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.json()

# Usage Examples
contacts_api = HubSpotContacts(auth)

# Create contact
new_contact = contacts_api.create_contact({
    'email': 'john.doe@example.com',
    'firstname': 'John',
    'lastname': 'Doe',
    'phone': '+1234567890',
    'company': 'Example Corp',
    'website': 'https://example.com',
    'lifecyclestage': 'lead'
})

print(f"Created contact: {new_contact['id']}")

# Search contacts
search_results = contacts_api.search_contacts(
    filters=[
        {
            'filters': [
                {
                    'propertyName': 'lifecyclestage',
                    'operator': 'EQ',
                    'value': 'lead'
                },
                {
                    'propertyName': 'createdate',
                    'operator': 'GT',
                    'value': '2024-01-01'
                }
            ]
        }
    ],
    properties=['email', 'firstname', 'lastname', 'lifecyclestage']
)

print(f"Found {len(search_results['results'])} contacts")

# Batch update
batch_updates = [
    {
        'id': '123',
        'properties': {'lifecyclestage': 'marketingqualifiedlead'}
    },
    {
        'id': '456',
        'properties': {'lifecyclestage': 'salesqualifiedlead'}
    }
]

contacts_api.batch_update_contacts(batch_updates)
```

### Contact Properties Reference

```python
# Standard HubSpot Contact Properties
CONTACT_PROPERTIES = {
    'identification': [
        'email',
        'firstname',
        'lastname',
        'phone',
        'mobilephone',
        'address',
        'city',
        'state',
        'zip',
        'country'
    ],

    'business': [
        'company',
        'website',
        'jobtitle',
        'industry',
        'annualrevenue',
        'numberofemployees'
    ],

    'lifecycle': [
        'lifecyclestage',  # subscriber, lead, marketingqualifiedlead, etc.
        'hs_lead_status',
        'lead_source',
        'hs_analytics_source',
        'hs_analytics_first_touch_converting_campaign'
    ],

    'engagement': [
        'hs_email_optout',
        'hs_email_bounce',
        'hs_email_last_email_name',
        'hs_email_last_send_date',
        'hs_email_last_open_date',
        'hs_email_last_click_date',
        'num_notes',
        'num_contacted_notes',
        'num_conversion_events'
    ],

    'sales': [
        'hs_sales_email_last_replied',
        'closedate',
        'hs_analytics_revenue',
        'total_revenue'
    ]
}
```

---

## Companies API

### Managing Companies

```python
class HubSpotCompanies:
    """HubSpot Companies API client"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.hubapi.com/crm/v3/objects/companies'

    def create_company(self, properties):
        """Create a new company"""
        url = self.base_url

        data = {
            'properties': properties
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def get_company(self, company_id, properties=None):
        """Get company by ID"""
        url = f"{self.base_url}/{company_id}"

        params = {}
        if properties:
            params['properties'] = ','.join(properties)

        response = requests.get(
            url,
            headers=self.auth.get_headers(),
            params=params
        )
        response.raise_for_status()

        return response.json()

    def search_companies(self, filters, properties=None, limit=100):
        """Search companies with filters"""
        url = f"{self.base_url}/search"

        data = {
            'filterGroups': filters,
            'properties': properties or [],
            'limit': limit
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def get_company_contacts(self, company_id):
        """Get all contacts associated with a company"""
        url = f"{self.base_url}/{company_id}/associations/contacts"

        response = requests.get(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.json()

# Usage
companies_api = HubSpotCompanies(auth)

# Create company
new_company = companies_api.create_company({
    'name': 'Example Corporation',
    'domain': 'example.com',
    'industry': 'Technology',
    'numberofemployees': 500,
    'annualrevenue': 10000000,
    'city': 'San Francisco',
    'state': 'California',
    'country': 'United States'
})

# Search companies by domain
search_results = companies_api.search_companies(
    filters=[
        {
            'filters': [
                {
                    'propertyName': 'domain',
                    'operator': 'EQ',
                    'value': 'example.com'
                }
            ]
        }
    ],
    properties=['name', 'domain', 'industry']
)
```

---

## Deals API

### Managing Deals

```python
class HubSpotDeals:
    """HubSpot Deals API client"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.hubapi.com/crm/v3/objects/deals'
        self.pipelines_url = 'https://api.hubapi.com/crm/v3/pipelines/deals'

    def create_deal(self, properties, associations=None):
        """Create a new deal"""
        url = self.base_url

        data = {
            'properties': properties
        }

        if associations:
            data['associations'] = associations

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def get_deal(self, deal_id, properties=None):
        """Get deal by ID"""
        url = f"{self.base_url}/{deal_id}"

        params = {}
        if properties:
            params['properties'] = ','.join(properties)

        response = requests.get(
            url,
            headers=self.auth.get_headers(),
            params=params
        )
        response.raise_for_status()

        return response.json()

    def update_deal_stage(self, deal_id, stage_id):
        """Move deal to a different stage"""
        url = f"{self.base_url}/{deal_id}"

        data = {
            'properties': {
                'dealstage': stage_id
            }
        }

        response = requests.patch(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def get_pipelines(self):
        """Get all deal pipelines"""
        url = self.pipelines_url

        response = requests.get(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.json()

    def search_deals(self, filters, properties=None, sorts=None, limit=100):
        """Search deals with filters"""
        url = f"{self.base_url}/search"

        data = {
            'filterGroups': filters,
            'properties': properties or [],
            'limit': limit
        }

        if sorts:
            data['sorts'] = sorts

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

# Usage
deals_api = HubSpotDeals(auth)

# Create deal with associations
new_deal = deals_api.create_deal(
    properties={
        'dealname': 'Q1 Enterprise Deal',
        'amount': 50000,
        'closedate': '2024-03-31',
        'pipeline': 'default',
        'dealstage': 'qualifiedtobuy'
    },
    associations=[
        {
            'to': {'id': '123'},
            'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 3}]
        }
    ]
)

# Search open deals
open_deals = deals_api.search_deals(
    filters=[
        {
            'filters': [
                {
                    'propertyName': 'dealstage',
                    'operator': 'NEQ',
                    'value': 'closedwon'
                },
                {
                    'propertyName': 'dealstage',
                    'operator': 'NEQ',
                    'value': 'closedlost'
                }
            ]
        }
    ],
    properties=['dealname', 'amount', 'dealstage', 'closedate'],
    sorts=[{'propertyName': 'amount', 'direction': 'DESCENDING'}]
)

print(f"Found {len(open_deals['results'])} open deals")
```

---

## Email Marketing API

### Campaign Management

```python
class HubSpotEmail:
    """HubSpot Email Marketing API client"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.hubapi.com'

    def create_marketing_email(self, email_config):
        """Create marketing email"""
        url = f"{self.base_url}/marketing/v3/emails"

        data = {
            'name': email_config['name'],
            'subject': email_config['subject'],
            'htmlBody': email_config['html_body'],
            'fromName': email_config['from_name'],
            'replyTo': email_config['reply_to'],
            'campaignName': email_config.get('campaign_name')
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def send_transactional_email(self, email_data):
        """Send single transactional email"""
        url = f"{self.base_url}/marketing/v3/transactional/single-email/send"

        data = {
            'emailId': email_data['email_id'],
            'message': {
                'to': email_data['to'],
                'from': email_data.get('from'),
                'cc': email_data.get('cc', []),
                'bcc': email_data.get('bcc', [])
            },
            'contactProperties': email_data.get('contact_properties', {}),
            'customProperties': email_data.get('custom_properties', {})
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def get_email_statistics(self, email_id):
        """Get email campaign statistics"""
        url = f"{self.base_url}/marketing/v3/emails/{email_id}/statistics"

        response = requests.get(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.json()

    def create_ab_test(self, test_config):
        """Create A/B test for email"""
        url = f"{self.base_url}/marketing/v3/emails/ab-test"

        data = {
            'name': test_config['name'],
            'emailIds': test_config['email_ids'],
            'testPercentage': test_config['test_percentage'],
            'winnerCriteria': test_config['winner_criteria'],
            'duration': test_config.get('duration', 4)  # hours
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

# Usage
email_api = HubSpotEmail(auth)

# Create marketing email
email = email_api.create_marketing_email({
    'name': 'Monthly Newsletter - January 2024',
    'subject': 'Your Monthly Marketing Update',
    'html_body': '<html><body><h1>Hello!</h1></body></html>',
    'from_name': 'Marketing Team',
    'reply_to': 'marketing@example.com',
    'campaign_name': 'Monthly Newsletter'
})

# Send transactional email
email_api.send_transactional_email({
    'email_id': email['id'],
    'to': 'customer@example.com',
    'contact_properties': {
        'firstname': 'John',
        'lastname': 'Doe'
    },
    'custom_properties': {
        'order_number': 'ORD-12345',
        'total_amount': '$99.99'
    }
})

# Get email statistics
stats = email_api.get_email_statistics(email['id'])
print(f"Open rate: {stats['openRate']}%")
print(f"Click rate: {stats['clickRate']}%")
```

---

## Workflows API

### Automation Workflows

```python
class HubSpotWorkflows:
    """HubSpot Workflows API client"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.hubapi.com/automation/v3/workflows'

    def list_workflows(self):
        """List all workflows"""
        url = self.base_url

        response = requests.get(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.json()

    def get_workflow(self, workflow_id):
        """Get workflow by ID"""
        url = f"{self.base_url}/{workflow_id}"

        response = requests.get(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.json()

    def enroll_contact(self, workflow_id, contact_email):
        """Enroll a contact in a workflow"""
        url = f"{self.base_url}/{workflow_id}/enrollments"

        data = {
            'email': contact_email
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def unenroll_contact(self, workflow_id, contact_email):
        """Unenroll a contact from a workflow"""
        url = f"{self.base_url}/{workflow_id}/enrollments/{contact_email}"

        response = requests.delete(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.status_code == 204

# Usage
workflows_api = HubSpotWorkflows(auth)

# List all workflows
workflows = workflows_api.list_workflows()
print(f"Found {len(workflows['workflows'])} workflows")

# Enroll contact in nurture workflow
workflows_api.enroll_contact(
    workflow_id='12345',
    contact_email='lead@example.com'
)
```

---

## Analytics API

### Marketing Analytics

```python
class HubSpotAnalytics:
    """HubSpot Analytics API client"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.hubapi.com'

    def get_analytics_views(self, object_type, start_date, end_date):
        """Get page views analytics"""
        url = f"{self.base_url}/analytics/v2/reports/{object_type}"

        params = {
            'start': start_date,
            'end': end_date
        }

        response = requests.get(
            url,
            headers=self.auth.get_headers(),
            params=params
        )
        response.raise_for_status()

        return response.json()

    def get_traffic_analytics(self, start_date, end_date, time_period='total'):
        """Get traffic analytics"""
        url = f"{self.base_url}/analytics/v2/reports/traffic-sources"

        params = {
            'start': start_date,
            'end': end_date,
            'time_period': time_period
        }

        response = requests.get(
            url,
            headers=self.auth.get_headers(),
            params=params
        )
        response.raise_for_status()

        return response.json()

    def get_campaign_analytics(self, campaign_guid):
        """Get campaign performance analytics"""
        url = f"{self.base_url}/email/public/v1/campaigns/{campaign_guid}"

        response = requests.get(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.json()

    def get_attribution_report(self, start_date, end_date):
        """Get multi-touch attribution report"""
        url = f"{self.base_url}/analytics/v2/reports/attribution"

        params = {
            'start': start_date,
            'end': end_date
        }

        response = requests.get(
            url,
            headers=self.auth.get_headers(),
            params=params
        )
        response.raise_for_status()

        return response.json()

# Usage
analytics_api = HubSpotAnalytics(auth)

# Get traffic analytics
traffic = analytics_api.get_traffic_analytics(
    start_date='2024-01-01',
    end_date='2024-01-31',
    time_period='daily'
)

# Get page views
views = analytics_api.get_analytics_views(
    object_type='landing-pages',
    start_date='2024-01-01',
    end_date='2024-01-31'
)
```

---

## Forms API

### Form Management

```python
class HubSpotForms:
    """HubSpot Forms API client"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.hubapi.com'

    def list_forms(self):
        """List all forms"""
        url = f"{self.base_url}/marketing/v3/forms"

        response = requests.get(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.json()

    def get_form(self, form_id):
        """Get form by ID"""
        url = f"{self.base_url}/marketing/v3/forms/{form_id}"

        response = requests.get(
            url,
            headers=self.auth.get_headers()
        )
        response.raise_for_status()

        return response.json()

    def submit_form(self, portal_id, form_guid, data):
        """Submit data to a form"""
        url = f"https://api.hsforms.com/submissions/v3/integration/submit/{portal_id}/{form_guid}"

        payload = {
            'fields': [
                {'name': key, 'value': value}
                for key, value in data.items()
            ],
            'context': {
                'pageUri': data.get('pageUri', ''),
                'pageName': data.get('pageName', '')
            }
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        return response.json()

# Usage
forms_api = HubSpotForms(auth)

# Submit form data
forms_api.submit_form(
    portal_id='123456',
    form_guid='abc-def-ghi',
    data={
        'email': 'user@example.com',
        'firstname': 'John',
        'lastname': 'Doe',
        'company': 'Example Corp',
        'pageUri': 'https://example.com/landing-page',
        'pageName': 'Product Demo Request'
    }
)
```

---

## Lists & Segmentation

### List Management

```python
class HubSpotLists:
    """HubSpot Lists API client"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.hubapi.com/contacts/v1/lists'

    def create_list(self, list_config):
        """Create a new contact list"""
        url = self.base_url

        data = {
            'name': list_config['name'],
            'dynamic': list_config.get('dynamic', False),
            'filters': list_config.get('filters', [])
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def add_contacts_to_list(self, list_id, contact_ids):
        """Add contacts to a static list"""
        url = f"{self.base_url}/{list_id}/add"

        data = {
            'vids': contact_ids
        }

        response = requests.post(
            url,
            headers=self.auth.get_headers(),
            json=data
        )
        response.raise_for_status()

        return response.json()

    def get_list_contacts(self, list_id, count=100):
        """Get all contacts in a list"""
        url = f"{self.base_url}/{list_id}/contacts/all"

        params = {
            'count': count
        }

        response = requests.get(
            url,
            headers=self.auth.get_headers(),
            params=params
        )
        response.raise_for_status()

        return response.json()

# Usage
lists_api = HubSpotLists(auth)

# Create dynamic list
lead_list = lists_api.create_list({
    'name': 'High Value Leads',
    'dynamic': True,
    'filters': [
        [
            {
                'operator': 'EQ',
                'property': 'lifecyclestage',
                'value': 'lead'
            },
            {
                'operator': 'GT',
                'property': 'hs_analytics_num_page_views',
                'value': '10'
            }
        ]
    ]
})
```

---

## Rate Limits & Quotas

### API Rate Limits

```python
# HubSpot API Rate Limits
RATE_LIMITS = {
    'default': {
        'per_second': 10,
        'daily': 500000
    },
    'batch': {
        'per_second': 4,
        'batch_size': 100
    },
    'search': {
        'per_second': 4,
        'per_minute': 120
    }
}

class HubSpotRateLimiter:
    """Rate limiter for HubSpot API"""

    def __init__(self, calls_per_second=10):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0

    def wait_if_needed(self):
        """Wait if necessary to respect rate limits"""
        import time

        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        self.last_call = time.time()
```

---

## Error Handling

```python
class HubSpotError(Exception):
    """Base exception for HubSpot API errors"""
    pass

class HubSpotErrorHandler:
    """Centralized error handling"""

    ERROR_CODES = {
        400: 'Bad request - Invalid parameters',
        401: 'Unauthorized - Invalid API key or token',
        403: 'Forbidden - Insufficient permissions',
        404: 'Not found - Resource does not exist',
        429: 'Rate limit exceeded',
        500: 'Internal server error',
        503: 'Service unavailable'
    }

    @staticmethod
    def handle_error(response):
        """Handle API error responses"""
        if response.status_code == 200:
            return response.json()

        error_message = HubSpotErrorHandler.ERROR_CODES.get(
            response.status_code,
            f'HTTP {response.status_code} error'
        )

        if response.status_code == 429:
            # Rate limit - check retry-after header
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                print(f"Rate limited. Retry after {retry_after} seconds")

        raise HubSpotError(f"{error_message}: {response.text}")
```

---

## Best Practices

### 1. Efficient Data Synchronization

```python
class HubSpotSync:
    """Efficient bidirectional sync"""

    def __init__(self, contacts_api):
        self.contacts_api = contacts_api

    def sync_contacts(self, external_contacts):
        """Sync contacts efficiently"""
        # Get existing contacts by email
        emails = [c['email'] for c in external_contacts]

        existing = {}
        for email in emails:
            contact = self.contacts_api.get_contact_by_email(email)
            if contact:
                existing[email] = contact

        # Separate creates and updates
        to_create = []
        to_update = []

        for contact in external_contacts:
            if contact['email'] in existing:
                to_update.append({
                    'id': existing[contact['email']]['id'],
                    'properties': contact
                })
            else:
                to_create.append(contact)

        # Batch operations
        if to_create:
            self.contacts_api.batch_create_contacts(to_create)

        if to_update:
            self.contacts_api.batch_update_contacts(to_update)

        return {
            'created': len(to_create),
            'updated': len(to_update)
        }
```

### 2. Webhook Integration

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/hubspot/webhook', methods=['POST'])
def hubspot_webhook():
    """Handle HubSpot webhooks"""
    # Verify signature
    signature = request.headers.get('X-HubSpot-Signature')
    if not verify_signature(request.get_data(), signature):
        return 'Invalid signature', 403

    # Process webhook
    data = request.json

    for event in data:
        object_type = event.get('subscriptionType')
        event_type = event.get('eventType')

        if object_type == 'contact.creation':
            handle_contact_created(event)
        elif object_type == 'contact.propertyChange':
            handle_contact_updated(event)

    return 'OK', 200

def verify_signature(payload, signature):
    """Verify webhook signature"""
    app_secret = 'YOUR_APP_SECRET'
    expected = hmac.new(
        app_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

---

## Testing Strategies

```python
import unittest
from unittest.mock import Mock, patch
import responses

class TestHubSpotAPI(unittest.TestCase):
    """Test HubSpot API integration"""

    def setUp(self):
        self.auth = Mock()
        self.auth.get_headers.return_value = {
            'Authorization': 'Bearer test_token',
            'Content-Type': 'application/json'
        }
        self.contacts_api = HubSpotContacts(self.auth)

    @responses.activate
    def test_create_contact(self):
        """Test contact creation"""
        responses.add(
            responses.POST,
            'https://api.hubapi.com/crm/v3/objects/contacts',
            json={'id': '123', 'properties': {'email': 'test@example.com'}},
            status=200
        )

        contact = self.contacts_api.create_contact({
            'email': 'test@example.com',
            'firstname': 'Test',
            'lastname': 'User'
        })

        self.assertEqual(contact['id'], '123')

    @responses.activate
    def test_search_contacts(self):
        """Test contact search"""
        responses.add(
            responses.POST,
            'https://api.hubapi.com/crm/v3/objects/contacts/search',
            json={'results': [{'id': '123', 'properties': {}}]},
            status=200
        )

        results = self.contacts_api.search_contacts(
            filters=[{
                'filters': [{
                    'propertyName': 'email',
                    'operator': 'EQ',
                    'value': 'test@example.com'
                }]
            }]
        )

        self.assertEqual(len(results['results']), 1)

if __name__ == '__main__':
    unittest.main()
```

---

## Real-World Integration Patterns

### Pattern 1: Lead Scoring System

```python
class LeadScoringSystem:
    """Automated lead scoring"""

    def __init__(self, contacts_api):
        self.contacts_api = contacts_api
        self.scoring_rules = {
            'email_opens': 5,
            'email_clicks': 10,
            'page_views': 2,
            'form_submissions': 20,
            'demo_requests': 50
        }

    def calculate_score(self, contact_id):
        """Calculate lead score"""
        contact = self.contacts_api.get_contact(
            contact_id,
            properties=[
                'hs_email_open',
                'hs_email_click',
                'num_pageviews',
                'num_conversion_events'
            ]
        )

        score = 0
        props = contact['properties']

        score += int(props.get('hs_email_open', 0)) * self.scoring_rules['email_opens']
        score += int(props.get('hs_email_click', 0)) * self.scoring_rules['email_clicks']
        score += int(props.get('num_pageviews', 0)) * self.scoring_rules['page_views']

        # Update contact with score
        self.contacts_api.update_contact(
            contact_id,
            {'hs_lead_score': score}
        )

        return score
```

### Pattern 2: Marketing Attribution

```python
class MarketingAttribution:
    """Multi-touch attribution"""

    def __init__(self, analytics_api, contacts_api):
        self.analytics_api = analytics_api
        self.contacts_api = contacts_api

    def get_contact_journey(self, contact_id):
        """Get complete customer journey"""
        contact = self.contacts_api.get_contact(
            contact_id,
            properties=[
                'hs_analytics_first_touch_converting_campaign',
                'hs_analytics_last_touch_converting_campaign',
                'hs_analytics_source',
                'hs_analytics_source_data_1',
                'hs_analytics_source_data_2'
            ]
        )

        journey = {
            'first_touch': contact['properties'].get('hs_analytics_first_touch_converting_campaign'),
            'last_touch': contact['properties'].get('hs_analytics_last_touch_converting_campaign'),
            'source': contact['properties'].get('hs_analytics_source'),
            'touchpoints': []
        }

        return journey
```

---

## Conclusion

This guide provides comprehensive coverage of the HubSpot Marketing Hub API. For production implementations:

1. Use OAuth 2.0 for authentication
2. Implement proper token refresh mechanisms
3. Use batch operations for efficiency
4. Respect rate limits
5. Implement webhook listeners for real-time updates
6. Use custom properties for business-specific data
7. Leverage workflows for automation
8. Monitor API usage and errors

For the latest documentation:
- [HubSpot API Documentation](https://developers.hubspot.com/docs/api/overview)
- [HubSpot API Client Libraries](https://github.com/HubSpot)
- [HubSpot Community](https://community.hubspot.com/t5/APIs-Integrations/ct-p/APIs_and_Integrations)
