# Legal Practice Management Platform API Integration Guide

## Document Information
- **Version**: 1.0.0
- **Last Updated**: 2025-11-19
- **Authority**: Platform Vendor API Documentation, ILTA Integration Standards
- **Scope**: Integration patterns and best practices for major legal practice management platforms

## Table of Contents
1. [Introduction](#introduction)
2. [Clio API Integration](#clio-api-integration)
3. [PracticePanther API Integration](#practicepanther-api-integration)
4. [MyCase API Integration](#mycase-api-integration)
5. [Elite 3E API Integration](#elite-3e-api-integration)
6. [Common Integration Patterns](#common-integration-patterns)
7. [Security and Compliance](#security-and-compliance)
8. [Error Handling and Resilience](#error-handling-and-resilience)
9. [Testing and Validation](#testing-and-validation)
10. [Deployment and Monitoring](#deployment-and-monitoring)

---

## Introduction

### Purpose
This guide provides comprehensive integration patterns for the most widely-used legal practice management platforms, enabling law firms to build robust, compliant integrations that enhance workflow efficiency while maintaining security and ethical obligations.

### Platform Overview

#### Clio
- **Market Position**: Leading cloud-based practice management for small-medium law firms
- **User Base**: 150,000+ users globally
- **Strengths**: Comprehensive feature set, extensive integrations, strong API
- **API Technology**: RESTful API, OAuth 2.0
- **Documentation**: https://app.clio.com/api/v4/documentation

#### PracticePanther
- **Market Position**: Growing cloud platform with strong automation features
- **User Base**: 13,000+ law firms
- **Strengths**: User-friendly interface, built-in automation, competitive pricing
- **API Technology**: RESTful API, OAuth 2.0
- **Documentation**: https://api.practicepanther.com/docs

#### MyCase
- **Market Position**: Strong in small law firms, part of AffiniPay ecosystem
- **User Base**: 15,000+ firms
- **Strengths**: Client portal, integrated payments, ease of use
- **API Technology**: RESTful API, OAuth 2.0
- **Documentation**: https://www.mycase.com/api

#### Elite 3E
- **Market Position**: Enterprise solution for large law firms
- **User Base**: Major AmLaw 100/200 firms
- **Strengths**: Enterprise scalability, complex billing, global capabilities
- **API Technology**: SOAP/REST hybrid, .NET integration
- **Documentation**: Thomson Reuters Partner Portal

### Integration Use Cases

**Common Integration Scenarios:**
1. Document management system synchronization
2. Time and billing automation
3. Client relationship management (CRM) integration
4. Court calendar and deadline management
5. Accounting system integration
6. Business intelligence and reporting
7. Client portals and communication
8. Workflow automation and AI integration

---

## Clio API Integration

### Authentication and Authorization

#### OAuth 2.0 Setup

**Application Registration:**
```
1. Register application at: https://app.clio.com/api/v4/documentation
2. Obtain:
   - Client ID
   - Client Secret
   - Redirect URI (must be HTTPS in production)
3. Select required scopes
```

**Authorization Code Flow:**
```python
import requests
from urllib.parse import urlencode

class ClioAuthenticator:
    """Handle Clio OAuth 2.0 authentication"""

    BASE_URL = "https://app.clio.com"
    AUTH_URL = f"{BASE_URL}/oauth/authorize"
    TOKEN_URL = f"{BASE_URL}/oauth/token"
    API_BASE = f"{BASE_URL}/api/v4"

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, state=None):
        """Generate authorization URL for user consent"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
        }
        if state:
            params['state'] = state  # CSRF protection

        return f"{self.AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()

        token_data = response.json()
        return {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_in': token_data['expires_in'],  # seconds
            'token_type': token_data['token_type']
        }

    def refresh_access_token(self, refresh_token):
        """Refresh expired access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()

        return response.json()
```

#### Scope Selection

**Available Scopes:**
```python
CLIO_SCOPES = {
    # Core data access
    'user_details:read': 'Read user profile information',
    'contacts:read': 'Read contacts and clients',
    'contacts:write': 'Create and update contacts',
    'matters:read': 'Read matter information',
    'matters:write': 'Create and update matters',
    'documents:read': 'Read document metadata',
    'documents:write': 'Upload and manage documents',

    # Time and billing
    'activities:read': 'Read time entries',
    'activities:write': 'Create time entries',
    'bills:read': 'Read invoices and bills',
    'bills:write': 'Create and modify bills',

    # Calendar and tasks
    'calendar_entries:read': 'Read calendar events',
    'calendar_entries:write': 'Create calendar events',
    'tasks:read': 'Read tasks',
    'tasks:write': 'Create and update tasks',

    # Communications
    'communications:read': 'Read emails and messages',
    'communications:write': 'Send communications'
}

# Request minimal necessary scopes for security
required_scopes = [
    'user_details:read',
    'contacts:read',
    'matters:read',
    'matters:write',
    'documents:read',
    'documents:write'
]
```

### Core API Operations

#### Matter Management

**Retrieve Matters:**
```python
class ClioClient:
    """Clio API client for matter operations"""

    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://app.clio.com/api/v4"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })

    def get_matters(self, filters=None, page=1, per_page=50):
        """
        Retrieve matters with optional filtering

        Args:
            filters: dict of query parameters
                - query: Search term
                - client_id: Filter by client
                - status: 'Open', 'Closed', etc.
                - created_since: ISO 8601 date
            page: Page number (1-indexed)
            per_page: Results per page (max 200)

        Returns:
            dict with 'data' and 'meta' keys
        """
        params = {
            'page': page,
            'per_page': min(per_page, 200)
        }

        if filters:
            params.update(filters)

        response = self.session.get(
            f"{self.base_url}/matters.json",
            params=params
        )
        response.raise_for_status()

        return response.json()

    def get_matter(self, matter_id, include=None):
        """
        Retrieve single matter with optional associations

        Args:
            matter_id: Clio matter ID
            include: List of associations to include
                     ['client', 'practice_area', 'responsible_attorney']

        Returns:
            Matter data dict
        """
        params = {}
        if include:
            params['fields'] = ','.join(include)

        response = self.session.get(
            f"{self.base_url}/matters/{matter_id}.json",
            params=params
        )
        response.raise_for_status()

        return response.json()['data']

    def create_matter(self, matter_data):
        """
        Create new matter

        Args:
            matter_data: dict containing matter information
                Required:
                    - client: {id: client_id}
                Optional:
                    - description: Matter description
                    - status: 'Pending' or 'Open'
                    - open_date: ISO 8601 date
                    - close_date: ISO 8601 date
                    - billing_method: 'Hourly', 'Flat', etc.
                    - practice_area: {id: practice_area_id}
                    - responsible_attorney: {id: user_id}
                    - originating_attorney: {id: user_id}
                    - custom_field_values: [...]

        Returns:
            Created matter data
        """
        # Validate required fields
        if 'client' not in matter_data or 'id' not in matter_data['client']:
            raise ValueError("Client ID is required")

        payload = {'data': matter_data}

        response = self.session.post(
            f"{self.base_url}/matters.json",
            json=payload
        )
        response.raise_for_status()

        created_matter = response.json()['data']

        # Log for audit trail
        self._log_matter_creation(created_matter)

        return created_matter

    def update_matter(self, matter_id, updates):
        """Update existing matter"""
        payload = {'data': updates}

        response = self.session.patch(
            f"{self.base_url}/matters/{matter_id}.json",
            json=payload
        )
        response.raise_for_status()

        return response.json()['data']

    def _log_matter_creation(self, matter):
        """Log matter creation for compliance audit trail"""
        import logging
        logger = logging.getLogger('clio_integration')
        logger.info(
            f"Matter created in Clio: ID={matter['id']}, "
            f"Description={matter.get('description', 'N/A')}, "
            f"Client={matter['client']['id']}"
        )
```

**Example Usage:**
```python
# Initialize client
clio = ClioClient(access_token='your_access_token')

# Create new matter
new_matter = clio.create_matter({
    'client': {'id': 12345},
    'description': 'Smith v. Jones - Personal Injury',
    'status': 'Open',
    'open_date': '2025-11-19',
    'billing_method': 'Hourly',
    'practice_area': {'id': 67890},
    'responsible_attorney': {'id': 54321},
    'custom_field_values': [
        {
            'field_name': 'Matter Number',
            'value': '2025-0001-PI'
        }
    ]
})

print(f"Matter created: {new_matter['id']}")

# Retrieve matters with filters
open_matters = clio.get_matters(filters={
    'status': 'Open',
    'created_since': '2025-01-01T00:00:00Z'
})

for matter in open_matters['data']:
    print(f"{matter['id']}: {matter['description']}")
```

#### Document Management

**Upload Document to Matter:**
```python
def upload_document_to_matter(self, matter_id, file_path, document_data=None):
    """
    Upload document to Clio matter

    Args:
        matter_id: Clio matter ID
        file_path: Local path to document
        document_data: Optional metadata
            - name: Document name (defaults to filename)
            - type: Document type (brief, contract, etc.)
            - date: Document date

    Returns:
        Created document data
    """
    import os
    from pathlib import Path

    file_name = os.path.basename(file_path)

    # Step 1: Initiate document upload
    document_params = {
        'parent': {
            'type': 'Matter',
            'id': matter_id
        },
        'name': document_data.get('name', file_name) if document_data else file_name
    }

    if document_data:
        if 'type' in document_data:
            document_params['type'] = document_data['type']
        if 'date' in document_data:
            document_params['date'] = document_data['date']

    response = self.session.post(
        f"{self.base_url}/documents.json",
        json={'data': document_params}
    )
    response.raise_for_status()

    document = response.json()['data']
    upload_url = document['latest_document_version']['put_url']

    # Step 2: Upload file to S3
    with open(file_path, 'rb') as f:
        file_content = f.read()

    upload_response = requests.put(
        upload_url,
        data=file_content,
        headers={'Content-Type': 'application/octet-stream'}
    )
    upload_response.raise_for_status()

    # Log for audit trail
    self._log_document_upload(document, file_name, matter_id)

    return document

def download_document(self, document_id, version_id=None):
    """
    Download document from Clio

    Args:
        document_id: Clio document ID
        version_id: Specific version (optional, defaults to latest)

    Returns:
        tuple: (file_content, file_name, content_type)
    """
    # Get document metadata
    response = self.session.get(
        f"{self.base_url}/documents/{document_id}.json"
    )
    response.raise_for_status()

    document = response.json()['data']

    # Get appropriate version
    if version_id:
        versions = document['document_versions']
        version = next(v for v in versions if v['id'] == version_id)
    else:
        version = document['latest_document_version']

    # Download from S3 URL
    download_url = version['url']
    file_response = requests.get(download_url)
    file_response.raise_for_status()

    # Log for audit trail
    self._log_document_download(document_id, version['id'])

    return (
        file_response.content,
        document['name'],
        version['content_type']
    )
```

#### Time Entry Management

**Create Time Entry:**
```python
def create_time_entry(self, time_entry_data):
    """
    Create time entry in Clio

    Args:
        time_entry_data: dict containing:
            Required:
                - matter: {id: matter_id}
                - user: {id: user_id}
                - date: 'YYYY-MM-DD'
                - type: 'TimeEntry' or 'ExpenseEntry'
            For TimeEntry:
                - quantity_in_hours: decimal
                - price: {amount: decimal, currency: 'USD'}
                - note: description
            For ExpenseEntry:
                - total: {amount: decimal, currency: 'USD'}
                - note: description

    Returns:
        Created activity data
    """
    # Validate required fields
    required = ['matter', 'user', 'date', 'type']
    for field in required:
        if field not in time_entry_data:
            raise ValueError(f"Required field missing: {field}")

    # Validate time entry content
    if time_entry_data['type'] == 'TimeEntry':
        if 'quantity_in_hours' not in time_entry_data:
            raise ValueError("Time entry requires quantity_in_hours")
        if 'note' not in time_entry_data or len(time_entry_data['note']) < 10:
            raise ValueError(
                "Time entry requires descriptive note (min 10 characters) "
                "for compliance with billing best practices"
            )

    payload = {'data': time_entry_data}

    response = self.session.post(
        f"{self.base_url}/activities.json",
        json=payload
    )
    response.raise_for_status()

    return response.json()['data']

def get_time_entries(self, matter_id=None, user_id=None, date_range=None):
    """
    Retrieve time entries with optional filtering

    Args:
        matter_id: Filter by matter
        user_id: Filter by user
        date_range: dict with 'start_date' and 'end_date' (YYYY-MM-DD)

    Returns:
        List of time entries
    """
    params = {}

    if matter_id:
        params['matter_id'] = matter_id
    if user_id:
        params['user_id'] = user_id
    if date_range:
        params['date_from'] = date_range['start_date']
        params['date_to'] = date_range['end_date']

    response = self.session.get(
        f"{self.base_url}/activities.json",
        params=params
    )
    response.raise_for_status()

    return response.json()['data']
```

### Webhook Integration

**Setting Up Webhooks:**
```python
def register_webhook(self, webhook_config):
    """
    Register webhook for real-time notifications

    Args:
        webhook_config: dict containing:
            - url: HTTPS endpoint to receive webhooks
            - events: List of event types
                * 'matter.created', 'matter.updated', 'matter.deleted'
                * 'document.created', 'document.updated', 'document.deleted'
                * 'activity.created', 'activity.updated', 'activity.deleted'
                * 'contact.created', 'contact.updated', 'contact.deleted'
            - fields: Optional list of fields to include

    Returns:
        Webhook configuration data
    """
    # Validate HTTPS endpoint
    if not webhook_config['url'].startswith('https://'):
        raise ValueError("Webhook URL must use HTTPS for security")

    payload = {'data': webhook_config}

    response = self.session.post(
        f"{self.base_url}/webhooks.json",
        json=payload
    )
    response.raise_for_status()

    webhook = response.json()['data']

    # Save webhook secret for signature verification
    self._save_webhook_secret(webhook['id'], webhook['secret'])

    return webhook

def verify_webhook_signature(self, payload, signature, secret):
    """
    Verify webhook signature for security

    Args:
        payload: Raw request body (bytes)
        signature: X-Clio-Signature header value
        secret: Webhook secret from registration

    Returns:
        bool: True if signature valid
    """
    import hmac
    import hashlib

    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)
```

**Webhook Handler Example:**
```python
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logger = logging.getLogger('clio_webhooks')

@app.route('/webhooks/clio', methods=['POST'])
def handle_clio_webhook():
    """Handle incoming Clio webhook"""

    # Get webhook signature
    signature = request.headers.get('X-Clio-Signature')
    if not signature:
        logger.warning("Webhook received without signature")
        return jsonify({'error': 'Missing signature'}), 401

    # Get webhook ID to retrieve secret
    webhook_id = request.headers.get('X-Clio-Webhook-Id')
    secret = get_webhook_secret(webhook_id)

    # Verify signature
    if not verify_webhook_signature(request.data, signature, secret):
        logger.warning(f"Invalid webhook signature from {request.remote_addr}")
        return jsonify({'error': 'Invalid signature'}), 401

    # Process webhook payload
    payload = request.json
    event_type = payload['type']
    data = payload['data']

    logger.info(f"Received webhook: {event_type}")

    # Route to appropriate handler
    handlers = {
        'matter.created': handle_matter_created,
        'matter.updated': handle_matter_updated,
        'document.created': handle_document_created,
        'activity.created': handle_activity_created
    }

    handler = handlers.get(event_type)
    if handler:
        try:
            handler(data)
            return jsonify({'status': 'processed'}), 200
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return jsonify({'error': 'Processing failed'}), 500
    else:
        logger.warning(f"Unknown event type: {event_type}")
        return jsonify({'status': 'ignored'}), 200

def handle_matter_created(matter_data):
    """Process new matter creation"""
    logger.info(f"New matter created: {matter_data['id']}")

    # Sync to local system
    sync_matter_to_local_system(matter_data)

    # Create corresponding records in integrated systems
    create_document_management_folder(matter_data)

    # Send notifications
    notify_responsible_attorney(matter_data)
```

### Rate Limiting and Optimization

**Rate Limit Handling:**
```python
import time
from functools import wraps

class RateLimitExceeded(Exception):
    """Raised when API rate limit exceeded"""
    pass

def handle_rate_limiting(max_retries=3):
    """Decorator to handle rate limiting with exponential backoff"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0

            while retries < max_retries:
                try:
                    response = func(*args, **kwargs)

                    # Check rate limit headers
                    remaining = response.headers.get('X-RateLimit-Remaining')
                    reset_time = response.headers.get('X-RateLimit-Reset')

                    if remaining and int(remaining) < 10:
                        # Approaching rate limit, slow down
                        logger.warning(
                            f"Approaching rate limit: {remaining} requests remaining"
                        )
                        time.sleep(1)

                    return response

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:  # Too Many Requests
                        retry_after = int(e.response.headers.get('Retry-After', 60))

                        logger.warning(
                            f"Rate limit exceeded. Retrying after {retry_after}s "
                            f"(attempt {retries + 1}/{max_retries})"
                        )

                        if retries < max_retries - 1:
                            time.sleep(retry_after)
                            retries += 1
                        else:
                            raise RateLimitExceeded(
                                f"Rate limit exceeded after {max_retries} retries"
                            )
                    else:
                        raise

            raise RateLimitExceeded(f"Max retries ({max_retries}) exceeded")

        return wrapper
    return decorator

# Usage
@handle_rate_limiting(max_retries=3)
def make_api_request(self, method, endpoint, **kwargs):
    """Make API request with rate limit handling"""
    return self.session.request(method, endpoint, **kwargs)
```

**Batch Operations:**
```python
def batch_create_time_entries(self, time_entries, batch_size=50):
    """
    Create multiple time entries efficiently

    Args:
        time_entries: List of time entry data dicts
        batch_size: Number of entries per batch (max 200)

    Returns:
        List of created time entries
    """
    created_entries = []
    failed_entries = []

    for i in range(0, len(time_entries), batch_size):
        batch = time_entries[i:i + batch_size]

        try:
            # Create entries in batch
            for entry in batch:
                try:
                    created = self.create_time_entry(entry)
                    created_entries.append(created)
                except Exception as e:
                    logger.error(f"Failed to create time entry: {e}")
                    failed_entries.append((entry, str(e)))

            # Respect rate limits between batches
            if i + batch_size < len(time_entries):
                time.sleep(1)

        except RateLimitExceeded:
            logger.error(f"Rate limit exceeded at batch {i // batch_size}")
            # Add remaining to failed list
            failed_entries.extend(
                (entry, "Rate limit exceeded") for entry in batch
            )
            break

    logger.info(
        f"Batch complete: {len(created_entries)} created, "
        f"{len(failed_entries)} failed"
    )

    return {
        'created': created_entries,
        'failed': failed_entries
    }
```

---

## PracticePanther API Integration

### Authentication

**OAuth 2.0 Setup:**
```python
class PracticePantherAuthenticator:
    """Handle PracticePanther OAuth 2.0"""

    BASE_URL = "https://api.practicepanther.com"
    AUTH_URL = f"{BASE_URL}/oauth/authorize"
    TOKEN_URL = f"{BASE_URL}/oauth/token"
    API_VERSION = "v1"

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, scope='full_access'):
        """Generate authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope
        }

        return f"{self.AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code):
        """Exchange authorization code for tokens"""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()

        return response.json()
```

### Core Operations

**Matter Management:**
```python
class PracticePantherClient:
    """PracticePanther API client"""

    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.practicepanther.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })

    def get_matters(self, params=None):
        """Retrieve matters"""
        response = self.session.get(
            f"{self.base_url}/Matter",
            params=params or {}
        )
        response.raise_for_status()
        return response.json()

    def create_matter(self, matter_data):
        """Create new matter"""
        response = self.session.post(
            f"{self.base_url}/Matter",
            json=matter_data
        )
        response.raise_for_status()
        return response.json()

    def create_task(self, task_data):
        """Create task with automation support"""
        response = self.session.post(
            f"{self.base_url}/Task",
            json=task_data
        )
        response.raise_for_status()
        return response.json()

    def create_workflow(self, workflow_data):
        """Create automated workflow"""
        response = self.session.post(
            f"{self.base_url}/Workflow",
            json=workflow_data
        )
        response.raise_for_status()
        return response.json()
```

---

## MyCase API Integration

**Similar structure to Clio and PracticePanther...**

```python
class MyCaseClient:
    """MyCase API client"""

    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.mycase.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })

    # Similar methods for matters, contacts, time entries, etc.
    pass
```

---

## Elite 3E API Integration

### SOAP/REST Hybrid Approach

**Elite 3E uses .NET-based services:**

```python
from zeep import Client
from zeep.wsse.username import UsernameToken

class Elite3EClient:
    """Elite 3E SOAP API client"""

    def __init__(self, wsdl_url, username, password):
        self.wsdl_url = wsdl_url
        self.client = Client(
            wsdl_url,
            wsse=UsernameToken(username, password)
        )

    def get_matter(self, matter_number):
        """Retrieve matter data"""
        return self.client.service.GetMatter(MatterNumber=matter_number)

    def create_time_entry(self, time_card_data):
        """Create time entry"""
        return self.client.service.PostTimeCard(TimeCard=time_card_data)

    def get_invoices(self, invoice_criteria):
        """Retrieve invoices"""
        return self.client.service.GetInvoices(Criteria=invoice_criteria)
```

---

## Common Integration Patterns

### Sync Pattern

**Bidirectional Synchronization:**
```python
class PlatformSyncManager:
    """Manage bidirectional sync between systems"""

    def __init__(self, source_client, destination_client):
        self.source = source_client
        self.destination = destination_client
        self.sync_log = SyncLog()

    def sync_matters(self, since_datetime=None):
        """Sync matters from source to destination"""

        # Get updated matters from source
        matters = self.source.get_matters(filters={
            'updated_since': since_datetime or self.sync_log.last_sync_time()
        })

        for matter in matters:
            try:
                # Check if exists in destination
                existing = self.destination.find_matter_by_external_id(
                    matter['id']
                )

                if existing:
                    # Update existing
                    self.destination.update_matter(
                        existing['id'],
                        self._map_matter_data(matter)
                    )
                else:
                    # Create new
                    created = self.destination.create_matter(
                        self._map_matter_data(matter)
                    )

                    # Store mapping
                    self.sync_log.record_mapping(
                        source_id=matter['id'],
                        destination_id=created['id'],
                        entity_type='matter'
                    )

                self.sync_log.record_success(matter['id'])

            except Exception as e:
                self.sync_log.record_error(matter['id'], str(e))
                logger.error(f"Sync failed for matter {matter['id']}: {e}")

        self.sync_log.update_last_sync_time()
```

---

## Security and Compliance

### Data Protection

```python
class SecurePlatformClient:
    """Platform client with enhanced security"""

    def __init__(self, access_token, encryption_key):
        self.access_token = access_token
        self.encryption_key = encryption_key
        # ...

    def create_matter_with_compliance(self, matter_data):
        """Create matter with compliance logging"""

        # Log for audit trail
        audit_logger.info(
            f"Creating matter: {matter_data.get('description')}",
            extra={
                'user': self.current_user,
                'ip_address': self.get_client_ip(),
                'timestamp': datetime.utcnow().isoformat()
            }
        )

        # Create matter
        matter = self.create_matter(matter_data)

        # Record in compliance system
        compliance_tracker.record_matter_creation(
            matter_id=matter['id'],
            created_by=self.current_user,
            client_id=matter['client']['id']
        )

        return matter
```

---

## Error Handling and Resilience

```python
class ResilientAPIClient:
    """API client with retry logic and circuit breaker"""

    def __init__(self, base_client):
        self.client = base_client
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((RequestException, HTTPError))
    )
    def resilient_request(self, method, *args, **kwargs):
        """Make API request with retry and circuit breaker"""

        if not self.circuit_breaker.is_closed():
            raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            response = getattr(self.client, method)(*args, **kwargs)
            self.circuit_breaker.record_success()
            return response
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise
```

---

## Document Control

**Version**: 1.0.0
**Last Updated**: 2025-11-19
**Maintained By**: Legal Technology Integration Team

*This guide covers major legal practice management platforms. Refer to vendor documentation for latest API changes.*
