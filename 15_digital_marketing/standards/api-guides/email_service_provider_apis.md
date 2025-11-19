# Email Service Provider APIs Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [SendGrid API](#sendgrid-api)
3. [Mailchimp API](#mailchimp-api)
4. [Klaviyo API](#klaviyo-api)
5. [Customer.io API](#customerio-api)
6. [Email Authentication](#email-authentication)
7. [Deliverability Best Practices](#deliverability-best-practices)
8. [Tracking & Analytics](#tracking--analytics)
9. [Webhooks](#webhooks)
10. [Error Handling](#error-handling)
11. [Testing Strategies](#testing-strategies)

---

## Overview

Email Service Providers (ESPs) offer robust APIs for managing transactional and marketing emails at scale. This guide covers the four major ESPs used in modern marketing stacks.

### Use Cases by Provider

**SendGrid:**
- High-volume transactional emails
- Marketing campaigns
- SMTP relay for applications
- Email validation and deliverability tools

**Mailchimp:**
- Marketing automation campaigns
- Audience segmentation and management
- E-commerce integrations
- Landing pages and forms

**Klaviyo:**
- E-commerce email marketing
- Advanced segmentation and personalization
- Revenue attribution
- SMS marketing integration

**Customer.io:**
- Behavior-based messaging
- Multi-channel campaigns (email, push, SMS)
- Event-triggered automation
- Customer journey orchestration

### Comparison Matrix

| Feature | SendGrid | Mailchimp | Klaviyo | Customer.io |
|---------|----------|-----------|---------|-------------|
| Transactional | Excellent | Good | Good | Excellent |
| Marketing | Good | Excellent | Excellent | Excellent |
| E-commerce | Good | Good | Excellent | Good |
| Automation | Good | Excellent | Excellent | Excellent |
| SMS Support | Yes | Limited | Yes | Yes |
| Push Notifications | No | No | Limited | Yes |

---

## SendGrid API

### Overview

SendGrid provides a powerful REST API for sending emails, managing contacts, and analyzing email performance.

- **API Version**: v3
- **Base URL**: `https://api.sendgrid.com/v3`
- **Authentication**: API Key (Bearer token)
- **Rate Limits**: Varies by plan (typically 600 requests/minute)

### Authentication

```python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

class SendGridManager:
    """SendGrid API client"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        self.client = SendGridAPIClient(self.api_key)
        self.base_url = 'https://api.sendgrid.com/v3'

    def get_headers(self):
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
```

### Sending Transactional Emails

```python
class SendGridTransactional:
    """SendGrid transactional email operations"""

    def __init__(self, api_key):
        self.client = SendGridAPIClient(api_key)

    def send_simple_email(self, to_email, subject, html_content, from_email='noreply@example.com'):
        """Send simple transactional email"""
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        try:
            response = self.client.send(message)
            return {
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id'),
                'success': True
            }
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return {'success': False, 'error': str(e)}

    def send_template_email(self, to_email, template_id, dynamic_data, from_email='noreply@example.com'):
        """Send email using dynamic template"""
        message = Mail(from_email=from_email, to_emails=to_email)
        message.template_id = template_id
        message.dynamic_template_data = dynamic_data

        try:
            response = self.client.send(message)
            return {
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id'),
                'success': True
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def send_bulk_emails(self, recipients, subject, html_content, from_email='noreply@example.com'):
        """Send bulk personalized emails"""
        from sendgrid.helpers.mail import Personalization

        message = Mail()
        message.from_email = Email(from_email)
        message.subject = subject
        message.content = Content("text/html", html_content)

        for recipient in recipients:
            personalization = Personalization()
            personalization.add_to(Email(recipient['email']))

            # Add dynamic substitutions
            for key, value in recipient.get('substitutions', {}).items():
                personalization.add_substitution(key, value)

            message.add_personalization(personalization)

        try:
            response = self.client.send(message)
            return {
                'status_code': response.status_code,
                'success': True,
                'sent_count': len(recipients)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def send_with_attachments(self, to_email, subject, html_content, attachments, from_email='noreply@example.com'):
        """Send email with attachments"""
        from sendgrid.helpers.mail import Attachment, FileContent, FileName, FileType, Disposition
        import base64

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        for attachment_data in attachments:
            with open(attachment_data['file_path'], 'rb') as f:
                file_data = f.read()

            encoded = base64.b64encode(file_data).decode()

            attachment = Attachment(
                FileContent(encoded),
                FileName(attachment_data['filename']),
                FileType(attachment_data['file_type']),
                Disposition('attachment')
            )

            message.add_attachment(attachment)

        try:
            response = self.client.send(message)
            return {'status_code': response.status_code, 'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Usage Examples
sg = SendGridTransactional(api_key='YOUR_API_KEY')

# Send simple email
result = sg.send_simple_email(
    to_email='customer@example.com',
    subject='Welcome to Our Platform',
    html_content='<h1>Welcome!</h1><p>Thanks for signing up.</p>',
    from_email='welcome@example.com'
)

# Send template email
result = sg.send_template_email(
    to_email='customer@example.com',
    template_id='d-1234567890abcdef',
    dynamic_data={
        'first_name': 'John',
        'order_number': 'ORD-12345',
        'total_amount': '$99.99',
        'order_items': [
            {'name': 'Product 1', 'price': '$49.99'},
            {'name': 'Product 2', 'price': '$50.00'}
        ]
    }
)

# Send bulk emails
recipients = [
    {
        'email': 'user1@example.com',
        'substitutions': {'{{name}}': 'John', '{{custom_field}}': 'Value1'}
    },
    {
        'email': 'user2@example.com',
        'substitutions': {'{{name}}': 'Jane', '{{custom_field}}': 'Value2'}
    }
]

result = sg.send_bulk_emails(
    recipients=recipients,
    subject='Personalized Message for {{name}}',
    html_content='<p>Hello {{name}}, here is your {{custom_field}}</p>'
)
```

### Marketing Campaigns

```python
class SendGridMarketing:
    """SendGrid marketing campaign operations"""

    def __init__(self, api_key):
        self.client = SendGridAPIClient(api_key)

    def create_contact(self, email, first_name, last_name, custom_fields=None):
        """Add or update contact"""
        import json

        data = {
            "contacts": [
                {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "custom_fields": custom_fields or {}
                }
            ]
        }

        try:
            response = self.client.client.marketing.contacts.put(
                request_body=data
            )
            return response
        except Exception as e:
            print(f"Error creating contact: {str(e)}")
            return None

    def create_list(self, list_name):
        """Create contact list"""
        data = {"name": list_name}

        try:
            response = self.client.client.marketing.lists.post(
                request_body=data
            )
            return response.to_dict
        except Exception as e:
            print(f"Error creating list: {str(e)}")
            return None

    def add_contacts_to_list(self, list_id, contact_ids):
        """Add contacts to a list"""
        data = {"contact_ids": contact_ids}

        try:
            response = self.client.client.marketing.lists._(list_id).contacts.put(
                request_body=data
            )
            return response
        except Exception as e:
            print(f"Error adding contacts to list: {str(e)}")
            return None

    def create_segment(self, name, query_dsl):
        """Create dynamic segment"""
        data = {
            "name": name,
            "query_dsl": query_dsl
        }

        try:
            response = self.client.client.marketing.segments.post(
                request_body=data
            )
            return response
        except Exception as e:
            print(f"Error creating segment: {str(e)}")
            return None

# Usage
marketing = SendGridMarketing(api_key='YOUR_API_KEY')

# Create contact
marketing.create_contact(
    email='subscriber@example.com',
    first_name='John',
    last_name='Doe',
    custom_fields={
        'e1_T': 'Premium',  # Custom field ID
        'e2_T': 'New York'
    }
)

# Create segment with filters
segment = marketing.create_segment(
    name='Active Premium Users',
    query_dsl={
        "and": [
            {
                "field": "custom_field:subscription_tier",
                "value": "Premium",
                "operator": "eq"
            },
            {
                "field": "last_clicked",
                "value": "30",
                "operator": "gt"
            }
        ]
    }
)
```

### Email Statistics & Analytics

```python
class SendGridAnalytics:
    """SendGrid analytics and statistics"""

    def __init__(self, api_key):
        self.client = SendGridAPIClient(api_key)

    def get_stats(self, start_date, end_date, aggregated_by='day'):
        """Get email statistics"""
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'aggregated_by': aggregated_by
        }

        try:
            response = self.client.client.stats.get(query_params=params)
            return response.to_dict
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return None

    def get_category_stats(self, categories, start_date, end_date):
        """Get statistics by category"""
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'categories': categories
        }

        try:
            response = self.client.client.categories.stats.get(query_params=params)
            return response.to_dict
        except Exception as e:
            print(f"Error getting category stats: {str(e)}")
            return None

    def get_email_activity(self, query_params):
        """Get email activity feed"""
        try:
            response = self.client.client.messages.get(query_params=query_params)
            return response.to_dict
        except Exception as e:
            print(f"Error getting email activity: {str(e)}")
            return None

# Usage
analytics = SendGridAnalytics(api_key='YOUR_API_KEY')

# Get stats for date range
stats = analytics.get_stats(
    start_date='2024-01-01',
    end_date='2024-01-31',
    aggregated_by='day'
)

# Get email activity
activity = analytics.get_email_activity({
    'limit': 100,
    'query': 'status="delivered" AND subject="Welcome Email"'
})
```

---

## Mailchimp API

### Overview

Mailchimp's Marketing API provides comprehensive access to audience management, campaigns, and automation.

- **API Version**: v3.0
- **Base URL**: `https://{dc}.api.mailchimp.com/3.0`
- **Authentication**: API Key
- **Rate Limits**: 10 requests/second per account

### Authentication

```python
import requests
import hashlib

class MailchimpManager:
    """Mailchimp API client"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.dc = api_key.split('-')[-1]  # Extract datacenter
        self.base_url = f'https://{self.dc}.api.mailchimp.com/3.0'

    def get_headers(self):
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method, endpoint, data=None, params=None):
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"

        response = requests.request(
            method=method,
            url=url,
            headers=self.get_headers(),
            json=data,
            params=params
        )

        response.raise_for_status()
        return response.json() if response.content else None
```

### Audience Management

```python
class MailchimpAudience:
    """Mailchimp audience (list) management"""

    def __init__(self, api_client):
        self.client = api_client

    def create_list(self, list_config):
        """Create a new audience list"""
        data = {
            'name': list_config['name'],
            'contact': {
                'company': list_config['company'],
                'address1': list_config['address1'],
                'city': list_config['city'],
                'state': list_config['state'],
                'zip': list_config['zip'],
                'country': list_config['country']
            },
            'permission_reminder': list_config['permission_reminder'],
            'campaign_defaults': {
                'from_name': list_config['from_name'],
                'from_email': list_config['from_email'],
                'subject': list_config['subject'],
                'language': list_config.get('language', 'en')
            },
            'email_type_option': True
        }

        return self.client._make_request('POST', 'lists', data=data)

    def add_member(self, list_id, email, merge_fields=None, status='subscribed'):
        """Add member to list"""
        data = {
            'email_address': email,
            'status': status,
            'merge_fields': merge_fields or {}
        }

        return self.client._make_request(
            'POST',
            f'lists/{list_id}/members',
            data=data
        )

    def update_member(self, list_id, email, merge_fields=None, status=None):
        """Update list member"""
        subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()

        data = {}
        if merge_fields:
            data['merge_fields'] = merge_fields
        if status:
            data['status'] = status

        return self.client._make_request(
            'PATCH',
            f'lists/{list_id}/members/{subscriber_hash}',
            data=data
        )

    def add_or_update_member(self, list_id, email, merge_fields=None, status='subscribed'):
        """Add or update member (upsert)"""
        subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()

        data = {
            'email_address': email,
            'status_if_new': status,
            'merge_fields': merge_fields or {}
        }

        if status:
            data['status'] = status

        return self.client._make_request(
            'PUT',
            f'lists/{list_id}/members/{subscriber_hash}',
            data=data
        )

    def batch_subscribe(self, list_id, members):
        """Batch add/update members"""
        data = {
            'members': members,
            'update_existing': True
        }

        return self.client._make_request(
            'POST',
            f'lists/{list_id}',
            data=data
        )

    def create_segment(self, list_id, segment_config):
        """Create segment"""
        data = {
            'name': segment_config['name'],
            'static_segment': segment_config.get('static_segment', []),
            'options': {
                'match': segment_config.get('match', 'any'),
                'conditions': segment_config.get('conditions', [])
            }
        }

        return self.client._make_request(
            'POST',
            f'lists/{list_id}/segments',
            data=data
        )

    def add_tag(self, list_id, email, tag):
        """Add tag to member"""
        subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()

        data = {
            'tags': [{'name': tag, 'status': 'active'}]
        }

        return self.client._make_request(
            'POST',
            f'lists/{list_id}/members/{subscriber_hash}/tags',
            data=data
        )

# Usage
mc_client = MailchimpManager(api_key='YOUR_API_KEY')
audience = MailchimpAudience(mc_client)

# Add member to list
member = audience.add_member(
    list_id='abc123',
    email='subscriber@example.com',
    merge_fields={
        'FNAME': 'John',
        'LNAME': 'Doe',
        'PHONE': '+1234567890'
    },
    status='subscribed'
)

# Create segment
segment = audience.create_segment(
    list_id='abc123',
    segment_config={
        'name': 'High Engagement Users',
        'match': 'all',
        'conditions': [
            {
                'condition_type': 'Campaigns',
                'field': 'campaign_id',
                'op': 'open',
                'value': 'campaign_123'
            },
            {
                'condition_type': 'DateMerge',
                'field': 'OPTIN_TIME',
                'op': 'greater',
                'value': '2024-01-01'
            }
        ]
    }
)

# Batch subscribe
members = [
    {
        'email_address': 'user1@example.com',
        'status': 'subscribed',
        'merge_fields': {'FNAME': 'John', 'LNAME': 'Doe'}
    },
    {
        'email_address': 'user2@example.com',
        'status': 'subscribed',
        'merge_fields': {'FNAME': 'Jane', 'LNAME': 'Smith'}
    }
]

audience.batch_subscribe(list_id='abc123', members=members)
```

### Campaign Management

```python
class MailchimpCampaigns:
    """Mailchimp campaign management"""

    def __init__(self, api_client):
        self.client = api_client

    def create_campaign(self, campaign_config):
        """Create email campaign"""
        data = {
            'type': campaign_config.get('type', 'regular'),
            'recipients': {
                'list_id': campaign_config['list_id'],
                'segment_opts': campaign_config.get('segment_opts')
            },
            'settings': {
                'subject_line': campaign_config['subject'],
                'preview_text': campaign_config.get('preview_text', ''),
                'title': campaign_config['title'],
                'from_name': campaign_config['from_name'],
                'reply_to': campaign_config['reply_to'],
                'authenticate': True,
                'auto_footer': False,
                'inline_css': True
            }
        }

        return self.client._make_request('POST', 'campaigns', data=data)

    def set_campaign_content(self, campaign_id, html_content):
        """Set campaign HTML content"""
        data = {
            'html': html_content
        }

        return self.client._make_request(
            'PUT',
            f'campaigns/{campaign_id}/content',
            data=data
        )

    def set_campaign_template(self, campaign_id, template_id, template_sections):
        """Set campaign template"""
        data = {
            'template': {
                'id': template_id,
                'sections': template_sections
            }
        }

        return self.client._make_request(
            'PUT',
            f'campaigns/{campaign_id}/content',
            data=data
        )

    def send_test_email(self, campaign_id, test_emails):
        """Send test campaign"""
        data = {
            'test_emails': test_emails,
            'send_type': 'html'
        }

        return self.client._make_request(
            'POST',
            f'campaigns/{campaign_id}/actions/test',
            data=data
        )

    def schedule_campaign(self, campaign_id, schedule_time):
        """Schedule campaign"""
        data = {
            'schedule_time': schedule_time,
            'timewarp': False
        }

        return self.client._make_request(
            'POST',
            f'campaigns/{campaign_id}/actions/schedule',
            data=data
        )

    def send_campaign(self, campaign_id):
        """Send campaign immediately"""
        return self.client._make_request(
            'POST',
            f'campaigns/{campaign_id}/actions/send'
        )

    def get_campaign_reports(self, campaign_id):
        """Get campaign performance report"""
        return self.client._make_request(
            'GET',
            f'reports/{campaign_id}'
        )

# Usage
campaigns = MailchimpCampaigns(mc_client)

# Create campaign
campaign = campaigns.create_campaign({
    'type': 'regular',
    'list_id': 'abc123',
    'subject': 'Monthly Newsletter - January 2024',
    'preview_text': 'Your monthly marketing insights',
    'title': 'Newsletter Jan 2024',
    'from_name': 'Marketing Team',
    'reply_to': 'marketing@example.com'
})

# Set content
campaigns.set_campaign_content(
    campaign_id=campaign['id'],
    html_content='<html><body><h1>Newsletter</h1></body></html>'
)

# Send test
campaigns.send_test_email(
    campaign_id=campaign['id'],
    test_emails=['test@example.com']
)

# Schedule campaign
campaigns.schedule_campaign(
    campaign_id=campaign['id'],
    schedule_time='2024-01-15T10:00:00+00:00'
)
```

### Automation

```python
class MailchimpAutomation:
    """Mailchimp marketing automation"""

    def __init__(self, api_client):
        self.client = api_client

    def create_automation(self, automation_config):
        """Create automation workflow"""
        data = {
            'recipients': {
                'list_id': automation_config['list_id'],
                'segment_opts': automation_config.get('segment_opts')
            },
            'settings': {
                'title': automation_config['title'],
                'from_name': automation_config['from_name'],
                'reply_to': automation_config['reply_to']
            },
            'trigger_settings': automation_config['trigger_settings']
        }

        return self.client._make_request(
            'POST',
            'automations',
            data=data
        )

    def add_automation_email(self, workflow_id, email_config):
        """Add email to automation workflow"""
        data = {
            'settings': {
                'subject_line': email_config['subject'],
                'preview_text': email_config.get('preview_text', ''),
                'title': email_config['title'],
                'from_name': email_config['from_name'],
                'reply_to': email_config['reply_to']
            },
            'delay': {
                'amount': email_config.get('delay_amount', 0),
                'type': email_config.get('delay_type', 'now'),
                'direction': email_config.get('delay_direction', 'after')
            }
        }

        return self.client._make_request(
            'POST',
            f'automations/{workflow_id}/emails',
            data=data
        )

# Usage
automation = MailchimpAutomation(mc_client)

# Create welcome series
welcome_flow = automation.create_automation({
    'list_id': 'abc123',
    'title': 'Welcome Series',
    'from_name': 'Welcome Team',
    'reply_to': 'welcome@example.com',
    'trigger_settings': {
        'workflow_type': 'emailFollowup',
        'workflow_emails_count': 3,
        'runtime': {
            'days': ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
            'hours': {'type': 'send_asap'}
        }
    }
})

# Add first email
automation.add_automation_email(
    workflow_id=welcome_flow['id'],
    email_config={
        'subject': 'Welcome to Our Community!',
        'title': 'Welcome Email 1',
        'from_name': 'Welcome Team',
        'reply_to': 'welcome@example.com',
        'delay_amount': 0,
        'delay_type': 'now'
    }
)
```

---

## Klaviyo API

### Overview

Klaviyo specializes in e-commerce email marketing with advanced segmentation and revenue attribution.

- **API Version**: v2023-10-15 (latest revision)
- **Base URL**: `https://a.klaviyo.com/api`
- **Authentication**: Private API Key
- **Rate Limits**: Variable by endpoint (typically 10-100 requests/second)

### Authentication & Setup

```python
import requests
import json

class KlaviyoManager:
    """Klaviyo API client"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://a.klaviyo.com/api'
        self.revision = '2023-10-15'

    def get_headers(self):
        """Get authorization headers"""
        return {
            'Authorization': f'Klaviyo-API-Key {self.api_key}',
            'Content-Type': 'application/json',
            'revision': self.revision
        }

    def _make_request(self, method, endpoint, data=None, params=None):
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"

        response = requests.request(
            method=method,
            url=url,
            headers=self.get_headers(),
            json=data,
            params=params
        )

        response.raise_for_status()
        return response.json() if response.content else None
```

### Profile & Event Tracking

```python
class KlaviyoProfiles:
    """Klaviyo profile management"""

    def __init__(self, api_client):
        self.client = api_client

    def create_or_update_profile(self, profile_data):
        """Create or update customer profile"""
        data = {
            'data': {
                'type': 'profile',
                'attributes': {
                    'email': profile_data['email'],
                    'phone_number': profile_data.get('phone_number'),
                    'external_id': profile_data.get('external_id'),
                    'first_name': profile_data.get('first_name'),
                    'last_name': profile_data.get('last_name'),
                    'properties': profile_data.get('properties', {})
                }
            }
        }

        return self.client._make_request('POST', 'profiles', data=data)

    def get_profile(self, profile_id):
        """Get profile by ID"""
        return self.client._make_request('GET', f'profiles/{profile_id}')

    def subscribe_to_list(self, list_id, profiles):
        """Subscribe profiles to a list"""
        data = {
            'data': {
                'type': 'profile-subscription-bulk-create-job',
                'attributes': {
                    'profiles': {
                        'data': [
                            {
                                'type': 'profile',
                                'attributes': {
                                    'email': profile['email'],
                                    'phone_number': profile.get('phone_number'),
                                    'subscriptions': {
                                        'email': {
                                            'marketing': {
                                                'consent': 'SUBSCRIBED'
                                            }
                                        }
                                    }
                                }
                            }
                            for profile in profiles
                        ]
                    }
                },
                'relationships': {
                    'list': {
                        'data': {
                            'type': 'list',
                            'id': list_id
                        }
                    }
                }
            }
        }

        return self.client._make_request(
            'POST',
            'profile-subscription-bulk-create-jobs',
            data=data
        )

class KlaviyoEvents:
    """Klaviyo event tracking"""

    def __init__(self, api_client):
        self.client = api_client

    def track_event(self, event_data):
        """Track custom event"""
        data = {
            'data': {
                'type': 'event',
                'attributes': {
                    'properties': event_data['properties'],
                    'metric': {
                        'data': {
                            'type': 'metric',
                            'attributes': {
                                'name': event_data['event_name']
                            }
                        }
                    },
                    'profile': {
                        'data': {
                            'type': 'profile',
                            'attributes': {
                                'email': event_data['email']
                            }
                        }
                    }
                }
            }
        }

        return self.client._make_request('POST', 'events', data=data)

    def track_ecommerce_event(self, event_type, profile_email, event_data):
        """Track e-commerce specific events"""
        data = {
            'data': {
                'type': 'event',
                'attributes': {
                    'properties': event_data,
                    'time': event_data.get('time'),
                    'value': event_data.get('value'),
                    'metric': {
                        'data': {
                            'type': 'metric',
                            'attributes': {
                                'name': event_type  # e.g., "Placed Order", "Viewed Product"
                            }
                        }
                    },
                    'profile': {
                        'data': {
                            'type': 'profile',
                            'attributes': {
                                'email': profile_email
                            }
                        }
                    }
                }
            }
        }

        return self.client._make_request('POST', 'events', data=data)

# Usage
klaviyo = KlaviyoManager(api_key='YOUR_PRIVATE_KEY')
profiles = KlaviyoProfiles(klaviyo)
events = KlaviyoEvents(klaviyo)

# Create/update profile
profile = profiles.create_or_update_profile({
    'email': 'customer@example.com',
    'first_name': 'John',
    'last_name': 'Doe',
    'phone_number': '+1234567890',
    'external_id': 'user_12345',
    'properties': {
        'customer_tier': 'Gold',
        'lifetime_value': 5000,
        'favorite_category': 'Electronics'
    }
})

# Track custom event
events.track_event({
    'event_name': 'Product Viewed',
    'email': 'customer@example.com',
    'properties': {
        'product_id': 'PROD-123',
        'product_name': 'Wireless Headphones',
        'price': 99.99,
        'category': 'Electronics'
    }
})

# Track order placed
events.track_ecommerce_event(
    event_type='Placed Order',
    profile_email='customer@example.com',
    event_data={
        'order_id': 'ORD-12345',
        'value': 299.99,
        'items': [
            {
                'product_id': 'PROD-123',
                'product_name': 'Wireless Headphones',
                'quantity': 2,
                'price': 99.99
            },
            {
                'product_id': 'PROD-456',
                'product_name': 'Phone Case',
                'quantity': 1,
                'price': 19.99
            }
        ]
    }
)
```

### Segmentation & Campaigns

```python
class KlaviyoCampaigns:
    """Klaviyo campaign management"""

    def __init__(self, api_client):
        self.client = api_client

    def create_campaign(self, campaign_data):
        """Create email campaign"""
        data = {
            'data': {
                'type': 'campaign',
                'attributes': {
                    'name': campaign_data['name'],
                    'audiences': {
                        'included': campaign_data['included_segments'],
                        'excluded': campaign_data.get('excluded_segments', [])
                    },
                    'send_strategy': {
                        'method': campaign_data.get('send_method', 'static'),
                        'options_static': {
                            'datetime': campaign_data.get('send_time')
                        }
                    }
                }
            }
        }

        return self.client._make_request('POST', 'campaigns', data=data)

    def create_segment(self, segment_data):
        """Create dynamic segment"""
        data = {
            'data': {
                'type': 'segment',
                'attributes': {
                    'name': segment_data['name'],
                    'definition': segment_data['definition']
                }
            }
        }

        return self.client._make_request('POST', 'segments', data=data)

# Usage
campaigns = KlaviyoCampaigns(klaviyo)

# Create segment for high-value customers
segment = campaigns.create_segment({
    'name': 'High Value Customers',
    'definition': {
        'type': 'and',
        'children': [
            {
                'type': 'profile_property',
                'dimension': 'lifetime_value',
                'operator': 'greater_than',
                'value': 1000
            },
            {
                'type': 'profile_metric',
                'dimension': 'Placed Order',
                'operator': 'at_least_once',
                'timeframe': 90
            }
        ]
    }
})
```

---

## Customer.io API

### Overview

Customer.io provides behavioral messaging across email, push, SMS, and in-app channels.

- **API Version**: v1
- **Track API**: `https://track.customer.io/api/v1`
- **App API**: `https://api.customer.io/v1`
- **Beta API**: `https://beta-api.customer.io/v1`
- **Authentication**: Site ID + API Key (Track) or App API Key

### Authentication

```python
import requests
import base64
from datetime import datetime

class CustomerIOManager:
    """Customer.io API client"""

    def __init__(self, site_id, api_key, app_api_key=None):
        self.site_id = site_id
        self.api_key = api_key
        self.app_api_key = app_api_key
        self.track_url = 'https://track.customer.io/api/v1'
        self.app_url = 'https://api.customer.io/v1'
        self.beta_url = 'https://beta-api.customer.io/v1'

    def get_track_headers(self):
        """Get headers for Track API"""
        credentials = f"{self.site_id}:{self.api_key}"
        encoded = base64.b64encode(credentials.encode()).decode()

        return {
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/json'
        }

    def get_app_headers(self):
        """Get headers for App/Beta API"""
        return {
            'Authorization': f'Bearer {self.app_api_key}',
            'Content-Type': 'application/json'
        }
```

### Customer & Event Tracking

```python
class CustomerIOTracking:
    """Customer.io tracking operations"""

    def __init__(self, manager):
        self.manager = manager

    def identify_customer(self, customer_id, attributes):
        """Create or update customer"""
        url = f"{self.manager.track_url}/customers/{customer_id}"

        data = attributes

        response = requests.put(
            url,
            headers=self.manager.get_track_headers(),
            json=data
        )

        response.raise_for_status()
        return response.status_code == 200

    def delete_customer(self, customer_id):
        """Delete customer"""
        url = f"{self.manager.track_url}/customers/{customer_id}"

        response = requests.delete(
            url,
            headers=self.manager.get_track_headers()
        )

        response.raise_for_status()
        return response.status_code == 200

    def track_event(self, customer_id, event_name, event_data=None):
        """Track custom event"""
        url = f"{self.manager.track_url}/customers/{customer_id}/events"

        data = {
            'name': event_name,
            'data': event_data or {},
            'timestamp': int(datetime.utcnow().timestamp())
        }

        response = requests.post(
            url,
            headers=self.manager.get_track_headers(),
            json=data
        )

        response.raise_for_status()
        return response.status_code == 200

    def track_anonymous_event(self, anonymous_id, event_name, event_data=None):
        """Track event for anonymous user"""
        url = f"{self.manager.track_url}/events"

        data = {
            'name': event_name,
            'anonymous_id': anonymous_id,
            'data': event_data or {},
            'timestamp': int(datetime.utcnow().timestamp())
        }

        response = requests.post(
            url,
            headers=self.manager.get_track_headers(),
            json=data
        )

        response.raise_for_status()
        return response.status_code == 200

    def add_device(self, customer_id, device_id, platform):
        """Add device for push notifications"""
        url = f"{self.manager.track_url}/customers/{customer_id}/devices"

        data = {
            'device': {
                'id': device_id,
                'platform': platform,  # 'ios' or 'android'
                'last_used': int(datetime.utcnow().timestamp())
            }
        }

        response = requests.put(
            url,
            headers=self.manager.get_track_headers(),
            json=data
        )

        response.raise_for_status()
        return response.status_code == 200

# Usage
cio_manager = CustomerIOManager(
    site_id='YOUR_SITE_ID',
    api_key='YOUR_API_KEY',
    app_api_key='YOUR_APP_API_KEY'
)

tracking = CustomerIOTracking(cio_manager)

# Identify customer
tracking.identify_customer(
    customer_id='user_12345',
    attributes={
        'email': 'customer@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'created_at': int(datetime.utcnow().timestamp()),
        'plan': 'premium',
        'custom_field': 'value'
    }
)

# Track event
tracking.track_event(
    customer_id='user_12345',
    event_name='product_viewed',
    event_data={
        'product_id': 'PROD-123',
        'product_name': 'Wireless Headphones',
        'price': 99.99,
        'category': 'Electronics'
    }
)

# Add device for push
tracking.add_device(
    customer_id='user_12345',
    device_id='device_token_abc123',
    platform='ios'
)
```

### Transactional Messaging

```python
class CustomerIOTransactional:
    """Customer.io transactional messaging"""

    def __init__(self, manager):
        self.manager = manager

    def send_transactional_email(self, transactional_message_id, recipient, message_data):
        """Send transactional email"""
        url = f"{self.manager.beta_url}/send/email"

        data = {
            'transactional_message_id': transactional_message_id,
            'to': recipient,
            'message_data': message_data,
            'identifiers': {
                'id': recipient.get('id'),
                'email': recipient.get('email')
            }
        }

        response = requests.post(
            url,
            headers=self.manager.get_app_headers(),
            json=data
        )

        response.raise_for_status()
        return response.json()

# Usage
transactional = CustomerIOTransactional(cio_manager)

# Send transactional email
transactional.send_transactional_email(
    transactional_message_id='1',
    recipient={
        'id': 'user_12345',
        'email': 'customer@example.com'
    },
    message_data={
        'order_number': 'ORD-12345',
        'total': '$299.99',
        'items': [
            {'name': 'Product 1', 'price': '$149.99'},
            {'name': 'Product 2', 'price': '$150.00'}
        ]
    }
)
```

---

## Email Authentication

### SPF, DKIM, and DMARC Setup

```yaml
# SPF Record (TXT)
v=spf1 include:sendgrid.net include:spf.mailchimp.com include:spf.klaviyo.com include:cust-spf.exacttarget.com ~all

# DKIM Record (TXT) - Provider specific
# SendGrid example
s1._domainkey.yourdomain.com TXT "k=rsa; p=YOUR_PUBLIC_KEY"

# DMARC Record (TXT)
_dmarc.yourdomain.com TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; ruf=mailto:forensic@yourdomain.com; fo=1"
```

---

## Deliverability Best Practices

```python
class EmailDeliverability:
    """Email deliverability best practices"""

    @staticmethod
    def validate_email(email):
        """Basic email validation"""
        import re

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def check_spam_score(html_content, subject):
        """Check potential spam indicators"""
        spam_indicators = {
            'excessive_caps': sum(1 for c in subject if c.isupper()) / len(subject) > 0.5 if subject else False,
            'spam_words': any(word in subject.lower() for word in ['free', 'click here', 'act now', 'limited time']),
            'excessive_exclamation': subject.count('!') > 2,
            'no_unsubscribe': 'unsubscribe' not in html_content.lower()
        }

        return spam_indicators

# Best practices checklist
DELIVERABILITY_CHECKLIST = {
    'authentication': {
        'spf_configured': True,
        'dkim_configured': True,
        'dmarc_configured': True,
        'custom_domain': True
    },
    'content': {
        'personalization': True,
        'mobile_responsive': True,
        'clear_unsubscribe': True,
        'text_version': True,
        'spam_score_low': True
    },
    'sending': {
        'list_hygiene': True,
        'engagement_based_sending': True,
        'sunset_policy': True,
        'double_opt_in': True
    },
    'monitoring': {
        'bounce_tracking': True,
        'complaint_tracking': True,
        'deliverability_monitoring': True
    }
}
```

---

## Tracking & Analytics

### Universal Email Tracking

```python
class EmailTracking:
    """Universal email tracking implementation"""

    def add_tracking_parameters(self, url, campaign_params):
        """Add UTM parameters to links"""
        from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # Add UTM parameters
        params.update({
            'utm_source': [campaign_params.get('source', 'email')],
            'utm_medium': [campaign_params.get('medium', 'email')],
            'utm_campaign': [campaign_params.get('campaign')],
            'utm_content': [campaign_params.get('content', '')],
            'utm_term': [campaign_params.get('term', '')]
        })

        # Remove None values
        params = {k: v for k, v in params.items() if v[0]}

        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

# Usage
tracker = EmailTracking()

tracked_url = tracker.add_tracking_parameters(
    url='https://example.com/product',
    campaign_params={
        'source': 'newsletter',
        'medium': 'email',
        'campaign': 'january_2024',
        'content': 'cta_button'
    }
)
# Result: https://example.com/product?utm_source=newsletter&utm_medium=email&utm_campaign=january_2024&utm_content=cta_button
```

---

## Webhooks

### Universal Webhook Handler

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/sendgrid', methods=['POST'])
def sendgrid_webhook():
    """Handle SendGrid event webhook"""
    events = request.json

    for event in events:
        event_type = event.get('event')
        email = event.get('email')
        timestamp = event.get('timestamp')

        if event_type == 'bounce':
            handle_bounce(email, event)
        elif event_type == 'open':
            handle_open(email, event)
        elif event_type == 'click':
            handle_click(email, event)

    return 'OK', 200

@app.route('/webhooks/mailchimp', methods=['POST'])
def mailchimp_webhook():
    """Handle Mailchimp webhook"""
    data = request.form

    event_type = data.get('type')
    email = data.get('data[email]')

    if event_type == 'subscribe':
        handle_subscribe(email, data)
    elif event_type == 'unsubscribe':
        handle_unsubscribe(email, data)

    return 'OK', 200

def handle_bounce(email, event):
    """Handle bounce event"""
    print(f"Email bounced: {email}")
    # Update customer record, remove from lists, etc.

def handle_open(email, event):
    """Handle email open"""
    print(f"Email opened: {email}")
    # Track engagement, update lead score, etc.

def handle_click(email, event):
    """Handle link click"""
    url = event.get('url')
    print(f"Link clicked: {url} by {email}")
    # Track conversion, trigger follow-up, etc.
```

---

## Error Handling

```python
class ESPErrorHandler:
    """Universal ESP error handling"""

    @staticmethod
    def handle_rate_limit(response, provider):
        """Handle rate limit errors"""
        import time

        if provider == 'sendgrid':
            retry_after = int(response.headers.get('X-RateLimit-Reset', 60))
        elif provider == 'mailchimp':
            retry_after = 60
        else:
            retry_after = 60

        print(f"Rate limited. Retrying after {retry_after} seconds")
        time.sleep(retry_after)

    @staticmethod
    def handle_invalid_email(email):
        """Handle invalid email address"""
        print(f"Invalid email: {email}")
        # Log error, notify admin, etc.

    @staticmethod
    def handle_unsubscribed(email):
        """Handle unsubscribed recipient"""
        print(f"User unsubscribed: {email}")
        # Update database, suppress future sends, etc.
```

---

## Testing Strategies

```python
import unittest

class TestEmailIntegrations(unittest.TestCase):
    """Test email service provider integrations"""

    def test_sendgrid_send(self):
        """Test SendGrid email sending"""
        # Use test mode or sandbox
        pass

    def test_mailchimp_subscribe(self):
        """Test Mailchimp subscription"""
        # Use test list
        pass

    def test_klaviyo_event_tracking(self):
        """Test Klaviyo event tracking"""
        # Use test profile
        pass

if __name__ == '__main__':
    unittest.main()
```

---

## Conclusion

This guide provides comprehensive coverage of major Email Service Provider APIs. For production implementations:

1. Implement proper authentication and credential management
2. Use batch operations for efficiency
3. Respect rate limits and implement queuing
4. Set up proper email authentication (SPF, DKIM, DMARC)
5. Monitor deliverability metrics
6. Implement webhook listeners for real-time events
7. Maintain list hygiene and sunset policies
8. Test thoroughly before production deployment

For official documentation:
- [SendGrid API Docs](https://docs.sendgrid.com/api-reference)
- [Mailchimp API Docs](https://mailchimp.com/developer/)
- [Klaviyo API Docs](https://developers.klaviyo.com/en/reference/api_overview)
- [Customer.io API Docs](https://customer.io/docs/api/)
