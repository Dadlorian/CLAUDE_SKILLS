# Integration with Practice Management Systems: Complete Guide

## Executive Summary

Integrating document automation with practice management (PMS) software creates powerful, efficient workflows that eliminate manual data entry and reduce human error. This guide provides comprehensive strategies, architectural patterns, and implementation guidance for seamless integration across the most popular practice management platforms.

Practice management integration enables:
- Automatic client data population in templates
- Matter-based document generation
- Real-time synchronization of data between systems
- Automated document filing and organization
- Single-click document generation from case context
- Workflow automation and process efficiency gains

## Practice Management Platform Overview

### Major Platform Analysis

**Clio**
- Cloud-native platform with robust API
- Strong integration ecosystem
- REST API with OAuth 2.0 authentication
- Real-time webhooks support
- Native integration marketplace
- Ideal for: Small to medium-sized firms, highly integrated workflows

**MyCase**
- Modern cloud-based practice management
- API-first architecture
- Mobile-friendly interface
- Strong automation capabilities
- Zapier integration support
- Ideal for: Tech-forward firms, high automation requirements

**Rocket Matter**
- Comprehensive practice management
- Flexible workflow automation
- SOAP and REST API support
- Bulk import capabilities
- User-friendly interface
- Ideal for: Firms wanting balanced features and pricing

**Zola Suite**
- Built for document-centric workflows
- Strong document management integration
- RESTful API architecture
- Workflow automation engine
- Role-based access control
- Ideal for: Document-heavy practices, litigation-focused firms

**LexisNexis Practice Management**
- Enterprise-level platform
- Extensive reporting capabilities
- Integration with Lexis research tools
- Complex matter and billing management
- Ideal for: Large firms, complex billing needs

**Thomson Reuters Elite**
- Premium enterprise solution
- Sophisticated matter management
- Advanced financial tracking
- Deep integration capabilities
- Ideal for: Large firms, complex organizational structures

## Integration Architecture Patterns

### Pattern 1: Pull-Based Integration (On-Demand)

**Architecture:**
```
┌─────────────────────┐
│  Document          │
│  Automation        │
│  System            │
└────────┬────────────┘
         │ Requests data on demand
         │ (API calls)
         ▼
┌─────────────────────┐
│  Practice           │
│  Management         │
│  System             │
│  (Clio, MyCase,    │
│   Rocket Matter)   │
└─────────────────────┘
```

**Implementation Example (Clio REST API):**

```python
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class ClioIntegration:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expiry = None
        self.authenticate()

    def authenticate(self):
        """Obtain access token using OAuth 2.0"""
        token_url = "https://app.clio.com/oauth/token"

        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        response = requests.post(token_url, json=payload)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data['access_token']
        self.token_expiry = datetime.now() + \
            timedelta(seconds=token_data['expires_in'])

    def get_client(self, client_id: int) -> Dict:
        """Retrieve client information from Clio"""
        endpoint = f"https://app.clio.com/api/v4/contacts/{client_id}.json"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()

        return response.json()['data']

    def get_matter(self, matter_id: int) -> Dict:
        """Retrieve matter information from Clio"""
        endpoint = f"https://app.clio.com/api/v4/matters/{matter_id}.json"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()

        return response.json()['data']

    def extract_template_variables(self, client_id: int, matter_id: int) -> Dict:
        """Extract all template variables from Clio"""
        client = self.get_client(client_id)
        matter = self.get_matter(matter_id)

        template_variables = {
            # Client Information
            'ClientName': client.get('name', ''),
            'ClientEmail': client.get('email', ''),
            'ClientPhone': client.get('phone', ''),
            'ClientAddress': f"{client.get('address_line_1', '')}, " +
                           f"{client.get('city', '')}, " +
                           f"{client.get('state', '')} " +
                           f"{client.get('postal_code', '')}",

            # Matter Information
            'MatterName': matter.get('description', ''),
            'MatterType': matter.get('matter_type_category', {}).get('name', ''),
            'MatterStatus': matter.get('status', {}).get('name', ''),
            'MatterOpenDate': matter.get('opened_date', ''),
            'MatterAmount': matter.get('amount', 0),

            # User/Attorney Information
            'Attorney': matter.get('users', [{}])[0].get('name', '')
        }

        return template_variables

    def save_document(self, matter_id: int, document_path: str,
                     document_name: str) -> Dict:
        """Save generated document back to Clio"""
        endpoint = "https://app.clio.com/api/v4/documents.json"

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        with open(document_path, 'rb') as f:
            files = {
                'file': (document_name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }

            data = {
                'document[matter_id]': matter_id,
                'document[name]': document_name
            }

            response = requests.post(endpoint, headers=headers,
                                   files=files, data=data)
            response.raise_for_status()

        return response.json()['data']
```

**Advantages:**
- Simple to implement and understand
- No real-time synchronization overhead
- Explicit request/response flow
- Easy to debug and test

**Disadvantages:**
- Requires document automation system to initiate
- Delayed if frequent updates needed
- Possible data staleness
- Network dependent

### Pattern 2: Push-Based Integration (Event-Driven)

**Architecture:**
```
┌─────────────────────┐
│  Practice           │
│  Management         │
│  System             │
│  Event Triggers     │
└────────┬────────────┘
         │ Webhooks/Events
         │ (Real-time)
         ▼
┌─────────────────────┐
│  Document          │
│  Automation        │
│  Event Handler     │
└─────────────────────┘
```

**Webhook Implementation Example:**

```python
from flask import Flask, request, jsonify
from datetime import datetime
import hmac
import hashlib
import json

app = Flask(__name__)

class WebhookHandler:
    WEBHOOK_SECRET = "your-webhook-secret-from-clio"

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> bool:
        """Verify that webhook came from legitimate source (Clio)"""
        expected_signature = hmac.new(
            key=WebhookHandler.WEBHOOK_SECRET.encode(),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def handle_matter_created(event_data: Dict):
        """Handle matter creation event"""
        matter_id = event_data['data']['id']
        matter_name = event_data['data']['description']
        client_id = event_data['data']['contact_id']

        print(f"New matter created: {matter_name} (ID: {matter_id})")

        # Trigger document generation workflow
        # Generate engagement letter template automatically
        # Save to document automation system

    @staticmethod
    def handle_matter_updated(event_data: Dict):
        """Handle matter update event"""
        matter_id = event_data['data']['id']
        changes = event_data['data'].get('changes', {})

        print(f"Matter {matter_id} updated: {changes}")

        # Update any dependent documents if necessary

    @staticmethod
    def handle_client_updated(event_data: Dict):
        """Handle client information update"""
        client_id = event_data['data']['id']

        print(f"Client {client_id} information updated")

        # Potentially regenerate documents with updated info

@app.route('/webhooks/clio', methods=['POST'])
def clio_webhook():
    """Receive and process Clio webhooks"""

    # Verify request signature
    signature = request.headers.get('X-Clio-Signature')
    if not WebhookHandler.verify_webhook_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401

    event_data = request.get_json()
    event_type = event_data.get('event_type')

    # Route to appropriate handler
    if event_type == 'matter.created':
        WebhookHandler.handle_matter_created(event_data)
    elif event_type == 'matter.updated':
        WebhookHandler.handle_matter_updated(event_data)
    elif event_type == 'contact.updated':
        WebhookHandler.handle_client_updated(event_data)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Advantages:**
- Real-time synchronization
- Minimal system overhead on requesting system
- Responsive to events
- Better for high-frequency updates

**Disadvantages:**
- More complex implementation
- Requires webhook infrastructure
- Network reliability critical
- Debugging more difficult

### Pattern 3: Hybrid Integration (Bidirectional Sync)

```python
class HybridPMSIntegration:
    """Combines pull, push, and scheduled sync for robust integration"""

    def __init__(self, pms_api, document_automation_api):
        self.pms = pms_api
        self.da = document_automation_api
        self.sync_log = []

    def sync_on_demand(self, matter_id: int) -> Dict:
        """Pull data when user explicitly requests document generation"""
        return self.pms.get_matter(matter_id)

    def sync_scheduled(self, interval_minutes: int = 60):
        """Periodic background sync to catch missed webhooks"""
        # Run every X minutes to ensure consistency
        all_matters = self.pms.get_all_matters()
        for matter in all_matters:
            self.sync_matter_data(matter['id'])

    def sync_webhook(self, webhook_event: Dict):
        """Handle real-time events"""
        matter_id = webhook_event['data']['id']
        self.sync_matter_data(matter_id)

    def sync_matter_data(self, matter_id: int):
        """Core synchronization logic"""
        matter_data = self.pms.get_matter(matter_id)
        client_data = self.pms.get_client(matter_data['contact_id'])

        # Transform and store
        template_context = self.build_template_context(matter_data, client_data)
        self.da.cache_context(matter_id, template_context)

        self.log_sync_event(matter_id, 'success')
```

## Data Transformation and Mapping

### Creating a Data Mapper

When integrating different systems, data needs to be transformed to match template requirements:

```python
from typing import Dict, Any, Callable, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class FieldMapping:
    """Define how PMS field maps to template variable"""
    source_field: str
    target_field: str
    transformer: Callable = None
    default_value: Any = None
    required: bool = False

class DataTransformer(ABC):
    """Base class for data transformation"""

    @abstractmethod
    def transform(self, pms_data: Dict) -> Dict:
        """Transform PMS data to template format"""
        pass

class ClioToTemplateTransformer(DataTransformer):
    """Transform Clio data to template variables"""

    def __init__(self):
        self.field_mappings = [
            # Client information mappings
            FieldMapping(
                source_field='contacts[0].name',
                target_field='ClientFullName',
                required=True
            ),
            FieldMapping(
                source_field='contacts[0].email',
                target_field='ClientEmail'
            ),
            FieldMapping(
                source_field='contacts[0].phone',
                target_field='ClientPhone',
                transformer=self.format_phone_number
            ),
            FieldMapping(
                source_field='contacts[0].address_line_1',
                target_field='ClientAddress',
                transformer=self.build_full_address
            ),

            # Matter information mappings
            FieldMapping(
                source_field='description',
                target_field='MatterDescription'
            ),
            FieldMapping(
                source_field='matter_type_category.name',
                target_field='MatterType'
            ),
            FieldMapping(
                source_field='opened_date',
                target_field='MatterOpenedDate',
                transformer=self.parse_date
            ),
            FieldMapping(
                source_field='status.name',
                target_field='MatterStatus'
            ),

            # User/attorney mappings
            FieldMapping(
                source_field='users[0].name',
                target_field='AttorneyName'
            ),
        ]

    def transform(self, pms_data: Dict) -> Dict:
        """Execute transformation"""
        template_variables = {}

        for mapping in self.field_mappings:
            try:
                source_value = self.get_nested_value(pms_data, mapping.source_field)

                if source_value is None:
                    if mapping.required:
                        raise ValueError(f"Required field missing: {mapping.source_field}")
                    source_value = mapping.default_value

                # Apply transformer if provided
                if mapping.transformer and source_value is not None:
                    target_value = mapping.transformer(source_value)
                else:
                    target_value = source_value

                template_variables[mapping.target_field] = target_value

            except Exception as e:
                print(f"Error transforming {mapping.source_field}: {e}")
                if mapping.required:
                    raise

        return template_variables

    @staticmethod
    def get_nested_value(data: Dict, path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        parts = path.replace('[', '.').replace(']', '').split('.')
        current = data

        for part in parts:
            if isinstance(current, list):
                try:
                    current = current[int(part)]
                except (ValueError, IndexError):
                    return None
            elif isinstance(current, dict):
                current = current.get(part)
                if current is None:
                    return None
            else:
                return None

        return current

    @staticmethod
    def format_phone_number(phone: str) -> str:
        """Format phone number"""
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone

    @staticmethod
    def parse_date(date_str: str) -> str:
        """Parse and format date"""
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%B %d, %Y')
        except:
            return date_str

    @staticmethod
    def build_full_address(address_line_1: str) -> str:
        """Combine address components"""
        # In practice, you'd pass more context to this method
        return address_line_1
```

## Common Integration Workflows

### Workflow 1: Matter Creation to Document Generation

**Step-by-Step Flow:**

```
1. Attorney creates new matter in Clio
   ↓
2. Clio triggers webhook: matter.created
   ↓
3. Document Automation System receives webhook
   ↓
4. System extracts client and matter info from Clio
   ↓
5. System identifies required templates:
   - Engagement Letter
   - Fee Agreement
   - Conflict Check Form
   ↓
6. System generates all documents automatically
   ↓
7. Documents saved back to Clio matter
   ↓
8. Attorney notified document package ready for review
```

**Implementation:**

```python
class MatterCreationWorkflow:
    def __init__(self, pms_api, da_api):
        self.pms = pms_api
        self.da = da_api

    def execute_on_matter_created(self, matter_event: Dict):
        """Triggered by Clio webhook"""

        matter_id = matter_event['data']['id']
        matter_data = self.pms.get_matter(matter_id)
        client_data = self.pms.get_client(matter_data['contact_id'])

        # Transform data for templates
        transformer = ClioToTemplateTransformer()
        template_variables = transformer.transform(matter_data)

        # Define required templates based on practice area
        practice_area = matter_data.get('practice_area', {}).get('name', '')
        required_templates = self.get_templates_for_practice_area(practice_area)

        # Generate all documents
        generated_documents = []
        for template_name in required_templates:
            try:
                doc = self.da.generate_document(
                    template_name=template_name,
                    variables=template_variables
                )
                generated_documents.append(doc)

            except Exception as e:
                self.log_error(f"Failed to generate {template_name}: {e}")

        # Save documents back to Clio
        for doc in generated_documents:
            self.pms.save_document(
                matter_id=matter_id,
                document_path=doc['path'],
                document_name=doc['name']
            )

        # Notify attorney
        self.send_notification(
            f"Document package generated for {matter_data['description']}",
            attorney_id=matter_data['users'][0]['id']
        )

        return generated_documents

    def get_templates_for_practice_area(self, practice_area: str) -> List[str]:
        """Map practice area to required templates"""
        template_map = {
            'Litigation': [
                'Litigation Engagement Letter',
                'Client Intake Form',
                'Litigation Fee Agreement'
            ],
            'Corporate': [
                'Corporate Engagement Letter',
                'Corporate Disclosure Form',
                'Hourly Fee Agreement'
            ],
            'Real Estate': [
                'Real Estate Engagement Letter',
                'Property Details Form',
                'Flat Fee Agreement'
            ]
        }
        return template_map.get(practice_area, [
            'General Engagement Letter',
            'Fee Agreement'
        ])
```

### Workflow 2: Time Entry to Hourly Template Population

Many law firms bill by the hour. Document automation can pull time entries and populate billing templates:

```python
class BillingIntegrationWorkflow:
    def __init__(self, pms_api, da_api):
        self.pms = pms_api
        self.da = da_api

    def generate_billing_statement(self, matter_id: int,
                                   start_date: str, end_date: str):
        """Generate statement of services based on time entries"""

        # Fetch time entries from PMS
        time_entries = self.pms.get_time_entries(
            matter_id=matter_id,
            start_date=start_date,
            end_date=end_date
        )

        # Calculate totals and summaries
        total_hours = 0
        total_amount = 0
        work_summary = {}

        for entry in time_entries:
            total_hours += entry['duration_minutes'] / 60
            total_amount += entry['amount']

            # Group by work type
            work_type = entry['activity_type']
            if work_type not in work_summary:
                work_summary[work_type] = {
                    'hours': 0,
                    'amount': 0,
                    'entries': []
                }
            work_summary[work_type]['hours'] += entry['duration_minutes'] / 60
            work_summary[work_type]['amount'] += entry['amount']
            work_summary[work_type]['entries'].append({
                'date': entry['performed_on'],
                'description': entry['description'],
                'hours': entry['duration_minutes'] / 60,
                'rate': entry['rate'],
                'amount': entry['amount']
            })

        # Get client and matter info
        matter = self.pms.get_matter(matter_id)
        client = self.pms.get_client(matter['contact_id'])

        # Build template variables
        template_variables = {
            'ClientName': client['name'],
            'ClientEmail': client['email'],
            'MatterDescription': matter['description'],
            'PeriodStart': start_date,
            'PeriodEnd': end_date,
            'TotalHours': total_hours,
            'TotalAmount': total_amount,
            'WorkSummary': work_summary,
            'TimeEntries': time_entries
        }

        # Generate billing statement
        billing_doc = self.da.generate_document(
            template_name='Statement of Services',
            variables=template_variables
        )

        # Save to PMS
        self.pms.save_document(
            matter_id=matter_id,
            document_path=billing_doc['path'],
            document_name=f"Statement of Services - {start_date} to {end_date}"
        )

        return billing_doc
```

## Error Handling and Resilience

### Implementing Robust Error Handling

```python
import logging
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum

class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

class SyncLog:
    """Track all integration sync operations"""
    def __init__(self):
        self.logger = logging.getLogger('pms_integration')
        self.sync_history = []

    def log_sync_start(self, matter_id: int, operation: str):
        """Log start of sync operation"""
        log_entry = {
            'timestamp': datetime.now(),
            'matter_id': matter_id,
            'operation': operation,
            'status': SyncStatus.IN_PROGRESS,
            'errors': []
        }
        self.sync_history.append(log_entry)
        self.logger.info(f"Starting {operation} for matter {matter_id}")
        return log_entry

    def log_sync_error(self, log_entry: Dict, error: Exception,
                       recoverable: bool = False):
        """Log sync error"""
        error_record = {
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'recoverable': recoverable
        }
        log_entry['errors'].append(error_record)
        self.logger.error(f"Error in {log_entry['operation']}: {error}")

    def log_sync_complete(self, log_entry: Dict, success: bool = True):
        """Log completion of sync"""
        log_entry['status'] = SyncStatus.SUCCESS if success else SyncStatus.FAILED
        log_entry['completed_at'] = datetime.now()
        self.logger.info(f"Completed {log_entry['operation']}: {log_entry['status']}")

class ResilientPMSIntegration:
    """Integration with built-in error handling and retries"""

    def __init__(self, pms_api, da_api):
        self.pms = pms_api
        self.da = da_api
        self.sync_log = SyncLog()
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def sync_with_retry(self, matter_id: int,
                       max_attempts: Optional[int] = None) -> bool:
        """Sync with automatic retry on failure"""

        if max_attempts is None:
            max_attempts = self.max_retries

        attempt = 0
        while attempt < max_attempts:
            try:
                self.perform_sync(matter_id)
                return True

            except Exception as e:
                attempt += 1
                self.sync_log.logger.warning(
                    f"Sync failed (attempt {attempt}/{max_attempts}): {e}"
                )

                if attempt < max_attempts:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    self.sync_log.logger.error(
                        f"Sync failed after {max_attempts} attempts"
                    )
                    raise

        return False

    def perform_sync(self, matter_id: int):
        """Actual sync operation"""
        try:
            matter_data = self.pms.get_matter(matter_id)
            client_data = self.pms.get_client(matter_data['contact_id'])

            transformer = ClioToTemplateTransformer()
            template_variables = transformer.transform(matter_data)

            # Verify all required fields present
            required_fields = ['ClientFullName', 'MatterDescription']
            for field in required_fields:
                if field not in template_variables:
                    raise ValueError(f"Missing required field: {field}")

        except Exception as e:
            raise RuntimeError(f"Sync failed: {e}") from e
```

## Security and Compliance

### Authentication and Authorization

```python
class SecurePMSIntegration:
    """Integration with built-in security measures"""

    def __init__(self, pms_api_key: str, api_secret: str):
        self.api_key = pms_api_key
        self.api_secret = api_secret
        self.authorized_users = set()

    def verify_user_permission(self, user_id: str, matter_id: int) -> bool:
        """Check if user has permission to access matter"""
        # Query PMS for user's matter access
        user_matters = self.pms.get_user_accessible_matters(user_id)
        return any(m['id'] == matter_id for m in user_matters)

    def audit_log_access(self, user_id: str, matter_id: int,
                        action: str, document_id: Optional[str] = None):
        """Log all document generation and access"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'matter_id': matter_id,
            'action': action,
            'document_id': document_id,
            'ip_address': self.get_client_ip(),
            'user_agent': self.get_user_agent()
        }
        self.store_audit_log(log_entry)

    def encrypt_sensitive_data(self, data: Dict) -> str:
        """Encrypt sensitive client data"""
        from cryptography.fernet import Fernet

        # In production, store key securely (e.g., AWS Secrets Manager)
        cipher = Fernet(self.encryption_key)
        json_data = json.dumps(data)
        encrypted = cipher.encrypt(json_data.encode())
        return encrypted.decode()
```

## Monitoring and Analytics

### Integration Health Monitoring

```python
class IntegrationMonitor:
    """Monitor PMS integration health and performance"""

    def __init__(self):
        self.metrics = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'average_sync_time': 0,
            'api_error_count': 0,
            'webhook_deliveries': 0,
            'webhook_failures': 0
        }

    def track_sync_performance(self, matter_id: int, sync_time_ms: int, success: bool):
        """Track sync performance metrics"""
        self.metrics['total_syncs'] += 1
        if success:
            self.metrics['successful_syncs'] += 1
        else:
            self.metrics['failed_syncs'] += 1

        # Update average sync time
        current_avg = self.metrics['average_sync_time']
        total = self.metrics['total_syncs']
        self.metrics['average_sync_time'] = \
            ((current_avg * (total - 1)) + sync_time_ms) / total

    def get_success_rate(self) -> float:
        """Calculate sync success rate"""
        if self.metrics['total_syncs'] == 0:
            return 0
        return self.metrics['successful_syncs'] / self.metrics['total_syncs']

    def get_health_status(self) -> Dict:
        """Get overall integration health"""
        success_rate = self.get_success_rate()
        status = 'healthy' if success_rate > 0.95 else 'degraded' if success_rate > 0.8 else 'unhealthy'

        return {
            'status': status,
            'success_rate': success_rate,
            'total_syncs': self.metrics['total_syncs'],
            'average_sync_time_ms': self.metrics['average_sync_time'],
            'failed_syncs': self.metrics['failed_syncs'],
            'api_errors': self.metrics['api_error_count']
        }
```

## Conclusion

Successful PMS integration requires careful planning of architecture, robust error handling, comprehensive testing, and ongoing monitoring. By following these patterns and best practices, you can create seamless workflows that significantly improve efficiency and reduce manual data entry errors. The key to successful integration is choosing the right architecture pattern for your specific use case and maintaining clear separation of concerns between systems.
