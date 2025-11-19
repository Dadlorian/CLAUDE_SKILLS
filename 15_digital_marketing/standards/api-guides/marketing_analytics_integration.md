# Marketing Analytics Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [Google Analytics 4 (GA4)](#google-analytics-4-ga4)
3. [Mixpanel](#mixpanel)
4. [Amplitude](#amplitude)
5. [Segment](#segment)
6. [Event Tracking Standards](#event-tracking-standards)
7. [Custom Dimensions & Properties](#custom-dimensions--properties)
8. [Data Export & Warehousing](#data-export--warehousing)
9. [Attribution Modeling](#attribution-modeling)
10. [Privacy & Compliance](#privacy--compliance)
11. [Testing & Validation](#testing--validation)
12. [Integration Patterns](#integration-patterns)

---

## Overview

Marketing analytics platforms provide crucial insights into user behavior, campaign performance, and business metrics. This guide covers integration with four major analytics platforms, each serving different use cases.

### Platform Comparison

| Feature | GA4 | Mixpanel | Amplitude | Segment |
|---------|-----|----------|-----------|---------|
| Primary Focus | Web Analytics | Product Analytics | Behavioral Analytics | Data Infrastructure |
| Real-time Data | Yes | Yes | Yes | Yes |
| Event Tracking | Yes | Yes | Yes | CDP (passes to others) |
| Funnel Analysis | Basic | Advanced | Advanced | Via Destinations |
| Cohort Analysis | Basic | Advanced | Advanced | Via Destinations |
| Attribution | Multi-touch | Limited | Limited | Via Destinations |
| Data Warehouse Export | BigQuery | Yes | Yes | Yes |
| Price Model | Free + 360 | Usage-based | Usage-based | Usage-based |
| Best For | Marketing Attribution | Product Teams | Growth Teams | Data Infrastructure |

### Use Cases by Platform

**Google Analytics 4:**
- Website and app traffic analysis
- Marketing campaign attribution
- E-commerce conversion tracking
- SEO and content performance
- Cross-platform user journeys

**Mixpanel:**
- Feature adoption tracking
- User engagement analysis
- Retention and churn analysis
- A/B test analytics
- Product funnel optimization

**Amplitude:**
- User behavior analysis
- Cohort-based insights
- Predictive analytics
- Cross-platform analytics
- Revenue analytics

**Segment:**
- Customer data platform (CDP)
- Single source of truth for customer data
- Multi-tool integration hub
- Data governance and quality
- Real-time data streaming

---

## Google Analytics 4 (GA4)

### Overview

GA4 is Google's next-generation analytics platform with event-based tracking and cross-platform capabilities.

- **API**: Google Analytics Data API v1
- **Authentication**: OAuth 2.0 or Service Account
- **Rate Limits**: 10 concurrent requests per property
- **Measurement Protocol**: v2 (for server-side tracking)

### Client-Side Implementation

```javascript
// gtag.js implementation
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-XXXXXXXXXX');

// Event tracking
gtag('event', 'purchase', {
  transaction_id: 'T_12345',
  value: 299.99,
  currency: 'USD',
  tax: 24.00,
  shipping: 15.00,
  items: [
    {
      item_id: 'SKU_12345',
      item_name: 'Wireless Headphones',
      item_category: 'Electronics',
      item_variant: 'Black',
      price: 149.99,
      quantity: 2
    }
  ]
});

// Custom event
gtag('event', 'generate_lead', {
  lead_source: 'website_form',
  lead_type: 'contact_sales',
  value: 0
});

// User properties
gtag('set', 'user_properties', {
  crm_id: 'user_12345',
  customer_tier: 'premium',
  lifetime_value: 5000
});
```

### Server-Side Tracking (Measurement Protocol)

```python
import requests
import json
import uuid
from datetime import datetime

class GA4ServerTracking:
    """GA4 Measurement Protocol v2 implementation"""

    def __init__(self, measurement_id, api_secret):
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.endpoint = 'https://www.google-analytics.com/mp/collect'
        self.debug_endpoint = 'https://www.google-analytics.com/debug/mp/collect'

    def send_event(self, client_id, events, user_properties=None, debug=False):
        """Send events to GA4"""
        url = self.debug_endpoint if debug else self.endpoint

        params = {
            'measurement_id': self.measurement_id,
            'api_secret': self.api_secret
        }

        payload = {
            'client_id': client_id,
            'events': events,
            'timestamp_micros': int(datetime.utcnow().timestamp() * 1000000)
        }

        if user_properties:
            payload['user_properties'] = user_properties

        response = requests.post(url, params=params, json=payload)
        response.raise_for_status()

        if debug:
            return response.json()

        return response.status_code == 204

    def track_purchase(self, client_id, transaction_data):
        """Track e-commerce purchase"""
        events = [{
            'name': 'purchase',
            'params': {
                'transaction_id': transaction_data['transaction_id'],
                'value': transaction_data['value'],
                'currency': transaction_data.get('currency', 'USD'),
                'tax': transaction_data.get('tax', 0),
                'shipping': transaction_data.get('shipping', 0),
                'items': transaction_data['items']
            }
        }]

        return self.send_event(client_id, events)

    def track_lead_generation(self, client_id, lead_data):
        """Track lead generation event"""
        events = [{
            'name': 'generate_lead',
            'params': {
                'lead_source': lead_data.get('source'),
                'lead_type': lead_data.get('type'),
                'value': lead_data.get('value', 0),
                'currency': lead_data.get('currency', 'USD')
            }
        }]

        return self.send_event(client_id, events)

    def track_custom_event(self, client_id, event_name, parameters):
        """Track custom event"""
        events = [{
            'name': event_name,
            'params': parameters
        }]

        return self.send_event(client_id, events)

# Usage
ga4_tracker = GA4ServerTracking(
    measurement_id='G-XXXXXXXXXX',
    api_secret='YOUR_API_SECRET'
)

# Track purchase
ga4_tracker.track_purchase(
    client_id='user_12345',
    transaction_data={
        'transaction_id': 'T_12345',
        'value': 299.99,
        'currency': 'USD',
        'tax': 24.00,
        'shipping': 15.00,
        'items': [
            {
                'item_id': 'SKU_12345',
                'item_name': 'Wireless Headphones',
                'item_category': 'Electronics',
                'price': 149.99,
                'quantity': 2
            }
        ]
    }
)

# Track lead
ga4_tracker.track_lead_generation(
    client_id='visitor_67890',
    lead_data={
        'source': 'website_form',
        'type': 'contact_sales',
        'value': 0
    }
)
```

### GA4 Reporting API

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    Filter,
    FilterExpression,
    FilterExpressionList
)

class GA4Reporting:
    """GA4 Data API for reporting"""

    def __init__(self, property_id):
        self.property_id = property_id
        self.client = BetaAnalyticsDataClient()

    def run_report(self, dimensions, metrics, start_date, end_date, filters=None):
        """Run custom GA4 report"""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name=d) for d in dimensions],
            metrics=[Metric(name=m) for m in metrics],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
        )

        if filters:
            request.dimension_filter = filters

        response = self.client.run_report(request)

        results = []
        for row in response.rows:
            result = {}

            for i, dim_value in enumerate(row.dimension_values):
                result[dimensions[i]] = dim_value.value

            for i, metric_value in enumerate(row.metric_values):
                result[metrics[i]] = metric_value.value

            results.append(result)

        return results

    def get_conversion_funnel(self, start_date, end_date):
        """Get conversion funnel data"""
        dimensions = ['eventName', 'sessionSource', 'sessionMedium']
        metrics = ['eventCount', 'conversions', 'totalRevenue']

        return self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date
        )

    def get_user_acquisition(self, start_date, end_date):
        """Get user acquisition report"""
        dimensions = [
            'sessionDefaultChannelGroup',
            'sessionSource',
            'sessionMedium',
            'sessionCampaignName'
        ]

        metrics = [
            'activeUsers',
            'newUsers',
            'sessions',
            'conversions',
            'totalRevenue'
        ]

        return self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date
        )

    def get_ecommerce_performance(self, start_date, end_date):
        """Get e-commerce performance metrics"""
        dimensions = ['itemName', 'itemCategory']
        metrics = [
            'itemsPurchased',
            'itemRevenue',
            'itemsViewed',
            'cartToViewRate',
            'purchaseToViewRate'
        ]

        return self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date
        )

# Usage
reporting = GA4Reporting(property_id='123456789')

# Get conversion funnel
funnel = reporting.get_conversion_funnel(
    start_date='30daysAgo',
    end_date='today'
)

# Get user acquisition
acquisition = reporting.get_user_acquisition(
    start_date='2024-01-01',
    end_date='2024-01-31'
)
```

---

## Mixpanel

### Overview

Mixpanel specializes in product analytics with powerful cohort analysis and funnel tracking.

- **API**: Project API, Query API, Data Export API
- **Authentication**: Project Token (client), Service Account (server)
- **Rate Limits**: Varies by endpoint (typically 60 requests/hour for export)

### Client-Side Implementation

```javascript
// Initialize Mixpanel
mixpanel.init('YOUR_PROJECT_TOKEN', {
  debug: true,
  track_pageview: true,
  persistence: 'localStorage'
});

// Identify user
mixpanel.identify('user_12345');

// Set user properties
mixpanel.people.set({
  '$email': 'user@example.com',
  '$name': 'John Doe',
  '$created': '2024-01-15',
  'plan': 'premium',
  'company': 'Acme Corp',
  'role': 'Marketing Manager'
});

// Track event
mixpanel.track('Product Viewed', {
  'product_id': 'PROD-123',
  'product_name': 'Wireless Headphones',
  'category': 'Electronics',
  'price': 99.99,
  'currency': 'USD'
});

// Track purchase
mixpanel.track('Purchase Completed', {
  'transaction_id': 'T_12345',
  'revenue': 299.99,
  'items': [
    {
      'product_id': 'PROD-123',
      'quantity': 2,
      'price': 149.99
    }
  ]
});

// Increment user property
mixpanel.people.increment('purchases', 1);
mixpanel.people.increment('total_revenue', 299.99);

// Track revenue
mixpanel.people.track_charge(299.99, {
  'transaction_id': 'T_12345',
  'time': new Date().toISOString()
});
```

### Server-Side Implementation

```python
import requests
import json
import base64
from datetime import datetime

class MixpanelTracking:
    """Mixpanel server-side tracking"""

    def __init__(self, project_token):
        self.project_token = project_token
        self.track_url = 'https://api.mixpanel.com/track'
        self.engage_url = 'https://api.mixpanel.com/engage'

    def track_event(self, distinct_id, event_name, properties=None):
        """Track event"""
        event_data = {
            'event': event_name,
            'properties': {
                'token': self.project_token,
                'distinct_id': distinct_id,
                'time': int(datetime.utcnow().timestamp()),
                **(properties or {})
            }
        }

        data = base64.b64encode(json.dumps(event_data).encode()).decode()

        response = requests.post(
            self.track_url,
            params={'data': data, 'verbose': 1}
        )

        return response.json()

    def set_user_properties(self, distinct_id, properties):
        """Set user profile properties"""
        update_data = {
            '$token': self.project_token,
            '$distinct_id': distinct_id,
            '$set': properties
        }

        data = base64.b64encode(json.dumps(update_data).encode()).decode()

        response = requests.post(
            self.engage_url,
            params={'data': data, 'verbose': 1}
        )

        return response.json()

    def increment_user_property(self, distinct_id, property_name, value):
        """Increment numeric user property"""
        update_data = {
            '$token': self.project_token,
            '$distinct_id': distinct_id,
            '$add': {property_name: value}
        }

        data = base64.b64encode(json.dumps(update_data).encode()).decode()

        response = requests.post(
            self.engage_url,
            params={'data': data, 'verbose': 1}
        )

        return response.json()

    def track_revenue(self, distinct_id, amount, properties=None):
        """Track revenue"""
        charge_data = {
            '$token': self.project_token,
            '$distinct_id': distinct_id,
            '$append': {
                '$transactions': {
                    '$amount': amount,
                    '$time': datetime.utcnow().isoformat(),
                    **(properties or {})
                }
            }
        }

        data = base64.b64encode(json.dumps(charge_data).encode()).decode()

        response = requests.post(
            self.engage_url,
            params={'data': data, 'verbose': 1}
        )

        return response.json()

# Usage
mixpanel = MixpanelTracking(project_token='YOUR_PROJECT_TOKEN')

# Track event
mixpanel.track_event(
    distinct_id='user_12345',
    event_name='Purchase Completed',
    properties={
        'transaction_id': 'T_12345',
        'revenue': 299.99,
        'product_category': 'Electronics'
    }
)

# Set user properties
mixpanel.set_user_properties(
    distinct_id='user_12345',
    properties={
        'email': 'user@example.com',
        'name': 'John Doe',
        'plan': 'premium',
        'signup_date': '2024-01-15'
    }
)

# Track revenue
mixpanel.track_revenue(
    distinct_id='user_12345',
    amount=299.99,
    properties={
        'transaction_id': 'T_12345',
        'product_id': 'PROD-123'
    }
)
```

### Mixpanel Query API

```python
import hashlib
import time

class MixpanelQuery:
    """Mixpanel Query API for analytics"""

    def __init__(self, api_secret):
        self.api_secret = api_secret
        self.base_url = 'https://mixpanel.com/api/2.0'

    def _generate_signature(self, params):
        """Generate API signature"""
        sorted_params = sorted(params.items())
        param_string = ''.join(f'{k}={v}' for k, v in sorted_params)
        signature_string = param_string + self.api_secret

        return hashlib.md5(signature_string.encode()).hexdigest()

    def query(self, endpoint, params):
        """Make query API request"""
        params['expire'] = int(time.time()) + 600
        params['sig'] = self._generate_signature(params)

        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()

    def get_events(self, event_names, from_date, to_date, unit='day'):
        """Get event data"""
        params = {
            'event': json.dumps(event_names),
            'unit': unit,
            'from_date': from_date,
            'to_date': to_date,
            'type': 'general'
        }

        return self.query('events', params)

    def get_funnel(self, funnel_id, from_date, to_date):
        """Get funnel analysis"""
        params = {
            'funnel_id': funnel_id,
            'from_date': from_date,
            'to_date': to_date,
            'unit': 'day'
        }

        return self.query('funnels', params)

    def get_retention(self, from_date, to_date, retention_type='birth'):
        """Get retention data"""
        params = {
            'from_date': from_date,
            'to_date': to_date,
            'retention_type': retention_type,
            'unit': 'day'
        }

        return self.query('retention', params)

# Usage
query = MixpanelQuery(api_secret='YOUR_API_SECRET')

# Get event data
events = query.get_events(
    event_names=['Purchase Completed', 'Product Viewed'],
    from_date='2024-01-01',
    to_date='2024-01-31',
    unit='day'
)

# Get funnel data
funnel = query.get_funnel(
    funnel_id='12345',
    from_date='2024-01-01',
    to_date='2024-01-31'
)
```

---

## Amplitude

### Overview

Amplitude provides behavioral analytics with advanced cohort analysis and predictive insights.

- **API**: HTTP API v2, Analytics API, Cohort API
- **Authentication**: API Key
- **Rate Limits**: 1,000 events/second per project

### Client-Side Implementation

```javascript
// Initialize Amplitude
amplitude.getInstance().init('YOUR_API_KEY', 'user_12345', {
  includeReferrer: true,
  includeUtm: true,
  saveEvents: true,
  trackingOptions: {
    city: true,
    country: true,
    ip_address: true
  }
});

// Set user properties
amplitude.getInstance().setUserId('user_12345');
amplitude.getInstance().setUserProperties({
  'email': 'user@example.com',
  'name': 'John Doe',
  'plan': 'premium',
  'signup_date': '2024-01-15'
});

// Track event
amplitude.getInstance().logEvent('Product Viewed', {
  'product_id': 'PROD-123',
  'product_name': 'Wireless Headphones',
  'category': 'Electronics',
  'price': 99.99
});

// Track revenue
var revenue = new amplitude.Revenue()
  .setProductId('PROD-123')
  .setPrice(99.99)
  .setQuantity(2)
  .setRevenueType('purchase');

amplitude.getInstance().logRevenueV2(revenue);

// Set user property operations
var identify = new amplitude.Identify()
  .set('plan', 'premium')
  .add('purchases', 1)
  .setOnce('first_purchase_date', '2024-01-15')
  .append('favorite_categories', 'Electronics');

amplitude.getInstance().identify(identify);
```

### Server-Side Implementation

```python
import requests
import json
from datetime import datetime

class AmplitudeTracking:
    """Amplitude HTTP API v2 implementation"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = 'https://api2.amplitude.com/2/httpapi'
        self.batch_endpoint = 'https://api2.amplitude.com/batch'

    def track_event(self, user_id, event_type, event_properties=None, user_properties=None):
        """Track single event"""
        event_data = {
            'user_id': user_id,
            'event_type': event_type,
            'time': int(datetime.utcnow().timestamp() * 1000),
            'event_properties': event_properties or {},
            'user_properties': user_properties or {}
        }

        payload = {
            'api_key': self.api_key,
            'events': [event_data]
        }

        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()

        return response.json()

    def track_batch_events(self, events):
        """Track multiple events in batch"""
        payload = {
            'api_key': self.api_key,
            'events': events
        }

        response = requests.post(self.batch_endpoint, json=payload)
        response.raise_for_status()

        return response.json()

    def track_revenue(self, user_id, product_id, price, quantity=1, revenue_type='purchase'):
        """Track revenue event"""
        event_data = {
            'user_id': user_id,
            'event_type': 'revenue',
            'time': int(datetime.utcnow().timestamp() * 1000),
            'event_properties': {
                'productId': product_id,
                'quantity': quantity,
                'price': price,
                'revenueType': revenue_type,
                'revenue': price * quantity
            }
        }

        payload = {
            'api_key': self.api_key,
            'events': [event_data]
        }

        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()

        return response.json()

    def identify_user(self, user_id, user_properties):
        """Set user properties"""
        event_data = {
            'user_id': user_id,
            'event_type': '$identify',
            'time': int(datetime.utcnow().timestamp() * 1000),
            'user_properties': {
                '$set': user_properties
            }
        }

        payload = {
            'api_key': self.api_key,
            'events': [event_data]
        }

        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()

        return response.json()

    def increment_user_property(self, user_id, property_name, value):
        """Increment user property"""
        event_data = {
            'user_id': user_id,
            'event_type': '$identify',
            'time': int(datetime.utcnow().timestamp() * 1000),
            'user_properties': {
                '$add': {property_name: value}
            }
        }

        payload = {
            'api_key': self.api_key,
            'events': [event_data]
        }

        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()

        return response.json()

# Usage
amplitude = AmplitudeTracking(api_key='YOUR_API_KEY')

# Track event
amplitude.track_event(
    user_id='user_12345',
    event_type='Purchase Completed',
    event_properties={
        'transaction_id': 'T_12345',
        'product_id': 'PROD-123',
        'amount': 299.99,
        'category': 'Electronics'
    },
    user_properties={
        '$set': {
            'last_purchase_date': datetime.utcnow().isoformat()
        }
    }
)

# Track revenue
amplitude.track_revenue(
    user_id='user_12345',
    product_id='PROD-123',
    price=149.99,
    quantity=2,
    revenue_type='purchase'
)

# Identify user
amplitude.identify_user(
    user_id='user_12345',
    user_properties={
        'email': 'user@example.com',
        'name': 'John Doe',
        'plan': 'premium'
    }
)

# Increment property
amplitude.increment_user_property(
    user_id='user_12345',
    property_name='total_purchases',
    value=1
)
```

### Amplitude Analytics API

```python
class AmplitudeAnalytics:
    """Amplitude Analytics API for querying data"""

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = 'https://amplitude.com/api/2'

    def get_active_users(self, start_date, end_date, interval='day'):
        """Get active users"""
        params = {
            'start': start_date,
            'end': end_date,
            'm': 'active',
            'i': interval
        }

        response = requests.get(
            f"{self.base_url}/users",
            params=params,
            auth=(self.api_key, self.secret_key)
        )

        response.raise_for_status()
        return response.json()

    def get_event_segmentation(self, event_type, start_date, end_date, segment_by=None):
        """Get event segmentation"""
        params = {
            'e': json.dumps({'event_type': event_type}),
            'start': start_date,
            'end': end_date
        }

        if segment_by:
            params['s'] = json.dumps([{'prop': segment_by}])

        response = requests.get(
            f"{self.base_url}/events/segmentation",
            params=params,
            auth=(self.api_key, self.secret_key)
        )

        response.raise_for_status()
        return response.json()

    def get_funnel_analysis(self, events, start_date, end_date):
        """Get funnel analysis"""
        params = {
            'e': json.dumps(events),
            'start': start_date,
            'end': end_date
        }

        response = requests.get(
            f"{self.base_url}/funnels",
            params=params,
            auth=(self.api_key, self.secret_key)
        )

        response.raise_for_status()
        return response.json()

# Usage
analytics = AmplitudeAnalytics(
    api_key='YOUR_API_KEY',
    secret_key='YOUR_SECRET_KEY'
)

# Get active users
active_users = analytics.get_active_users(
    start_date='20240101',
    end_date='20240131',
    interval='day'
)

# Get event segmentation
segmentation = analytics.get_event_segmentation(
    event_type='Purchase Completed',
    start_date='20240101',
    end_date='20240131',
    segment_by='product_category'
)
```

---

## Segment

### Overview

Segment is a Customer Data Platform (CDP) that collects data once and sends it to multiple destinations.

- **API**: HTTP Tracking API, Config API, Public API
- **Authentication**: Write Key (tracking), Access Token (config)
- **Rate Limits**: 500 requests/second per source

### Client-Side Implementation

```javascript
// Initialize Segment
analytics.load('YOUR_WRITE_KEY');

// Identify user
analytics.identify('user_12345', {
  email: 'user@example.com',
  name: 'John Doe',
  plan: 'premium',
  company: {
    id: 'company_123',
    name: 'Acme Corp',
    industry: 'Technology'
  }
});

// Track event
analytics.track('Product Viewed', {
  product_id: 'PROD-123',
  product_name: 'Wireless Headphones',
  category: 'Electronics',
  price: 99.99,
  currency: 'USD'
});

// Track page view
analytics.page('Product Detail', {
  product_id: 'PROD-123',
  category: 'Electronics',
  path: '/products/wireless-headphones'
});

// Group (for B2B)
analytics.group('company_123', {
  name: 'Acme Corp',
  industry: 'Technology',
  employees: 500,
  plan: 'enterprise'
});

// Alias (merge identities)
analytics.alias('user_12345', 'anonymous_id_abc123');
```

### Server-Side Implementation

```python
import requests
import json
import base64
from datetime import datetime
import uuid

class SegmentTracking:
    """Segment HTTP Tracking API implementation"""

    def __init__(self, write_key):
        self.write_key = write_key
        self.endpoint = 'https://api.segment.io/v1'

    def _get_auth_header(self):
        """Get Basic Auth header"""
        credentials = f"{self.write_key}:"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _make_request(self, method_type, data):
        """Make API request"""
        url = f"{self.endpoint}/{method_type}"

        headers = {
            'Authorization': self._get_auth_header(),
            'Content-Type': 'application/json'
        }

        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat() + 'Z'

        if 'messageId' not in data:
            data['messageId'] = str(uuid.uuid4())

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()

    def identify(self, user_id, traits=None, context=None):
        """Identify user"""
        data = {
            'type': 'identify',
            'userId': user_id,
            'traits': traits or {},
            'context': context or {}
        }

        return self._make_request('identify', data)

    def track(self, user_id, event, properties=None, context=None, anonymous_id=None):
        """Track event"""
        data = {
            'type': 'track',
            'event': event,
            'properties': properties or {},
            'context': context or {}
        }

        if user_id:
            data['userId'] = user_id
        if anonymous_id:
            data['anonymousId'] = anonymous_id

        return self._make_request('track', data)

    def page(self, user_id, name, properties=None, context=None):
        """Track page view"""
        data = {
            'type': 'page',
            'userId': user_id,
            'name': name,
            'properties': properties or {},
            'context': context or {}
        }

        return self._make_request('page', data)

    def screen(self, user_id, name, properties=None, context=None):
        """Track screen view (mobile)"""
        data = {
            'type': 'screen',
            'userId': user_id,
            'name': name,
            'properties': properties or {},
            'context': context or {}
        }

        return self._make_request('screen', data)

    def group(self, user_id, group_id, traits=None, context=None):
        """Associate user with group"""
        data = {
            'type': 'group',
            'userId': user_id,
            'groupId': group_id,
            'traits': traits or {},
            'context': context or {}
        }

        return self._make_request('group', data)

    def alias(self, user_id, previous_id):
        """Merge user identities"""
        data = {
            'type': 'alias',
            'userId': user_id,
            'previousId': previous_id
        }

        return self._make_request('alias', data)

    def batch(self, events):
        """Send batch of events"""
        data = {
            'batch': events
        }

        url = f"{self.endpoint}/batch"

        headers = {
            'Authorization': self._get_auth_header(),
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()

# Usage
segment = SegmentTracking(write_key='YOUR_WRITE_KEY')

# Identify user
segment.identify(
    user_id='user_12345',
    traits={
        'email': 'user@example.com',
        'name': 'John Doe',
        'plan': 'premium',
        'company': {
            'id': 'company_123',
            'name': 'Acme Corp'
        }
    },
    context={
        'ip': '192.168.1.1',
        'userAgent': 'Mozilla/5.0...'
    }
)

# Track event
segment.track(
    user_id='user_12345',
    event='Purchase Completed',
    properties={
        'transaction_id': 'T_12345',
        'revenue': 299.99,
        'currency': 'USD',
        'products': [
            {
                'product_id': 'PROD-123',
                'name': 'Wireless Headphones',
                'price': 149.99,
                'quantity': 2
            }
        ]
    }
)

# Track page
segment.page(
    user_id='user_12345',
    name='Product Detail',
    properties={
        'product_id': 'PROD-123',
        'category': 'Electronics',
        'url': 'https://example.com/products/wireless-headphones'
    }
)

# Group user
segment.group(
    user_id='user_12345',
    group_id='company_123',
    traits={
        'name': 'Acme Corp',
        'industry': 'Technology',
        'employees': 500,
        'plan': 'enterprise'
    }
)

# Batch tracking
events = [
    {
        'type': 'track',
        'userId': 'user_12345',
        'event': 'Product Viewed',
        'properties': {'product_id': 'PROD-123'}
    },
    {
        'type': 'track',
        'userId': 'user_12345',
        'event': 'Added to Cart',
        'properties': {'product_id': 'PROD-123', 'quantity': 2}
    }
]

segment.batch(events)
```

---

## Event Tracking Standards

### Standard E-commerce Events

```python
# Event taxonomy for consistent tracking across platforms
ECOMMERCE_EVENTS = {
    'product_viewed': {
        'required_properties': ['product_id', 'product_name', 'price'],
        'optional_properties': ['category', 'brand', 'variant', 'image_url']
    },
    'product_list_viewed': {
        'required_properties': ['list_id', 'category'],
        'optional_properties': ['products']
    },
    'product_added_to_cart': {
        'required_properties': ['product_id', 'product_name', 'price', 'quantity'],
        'optional_properties': ['category', 'variant']
    },
    'cart_viewed': {
        'required_properties': ['cart_id', 'total'],
        'optional_properties': ['products', 'item_count']
    },
    'checkout_started': {
        'required_properties': ['order_id', 'total', 'currency'],
        'optional_properties': ['products', 'shipping', 'tax']
    },
    'checkout_step_completed': {
        'required_properties': ['order_id', 'step'],
        'optional_properties': ['shipping_method', 'payment_method']
    },
    'order_completed': {
        'required_properties': ['order_id', 'total', 'revenue', 'currency'],
        'optional_properties': ['products', 'shipping', 'tax', 'discount']
    }
}

# Marketing events
MARKETING_EVENTS = {
    'email_opened': {
        'required_properties': ['campaign_id', 'email_id'],
        'optional_properties': ['subject', 'variant']
    },
    'email_clicked': {
        'required_properties': ['campaign_id', 'email_id', 'link_url'],
        'optional_properties': ['link_name']
    },
    'ad_clicked': {
        'required_properties': ['campaign_id', 'ad_id', 'platform'],
        'optional_properties': ['creative_id', 'placement']
    },
    'lead_generated': {
        'required_properties': ['lead_source', 'form_id'],
        'optional_properties': ['campaign_id', 'offer']
    }
}
```

### Universal Event Tracker

```python
class UniversalEventTracker:
    """Track events across multiple analytics platforms"""

    def __init__(self, ga4_tracker, mixpanel_tracker, amplitude_tracker, segment_tracker):
        self.ga4 = ga4_tracker
        self.mixpanel = mixpanel_tracker
        self.amplitude = amplitude_tracker
        self.segment = segment_tracker

    def track_purchase(self, user_id, transaction_data):
        """Track purchase across all platforms"""
        # GA4
        self.ga4.track_purchase(user_id, transaction_data)

        # Mixpanel
        self.mixpanel.track_event(
            distinct_id=user_id,
            event_name='Purchase Completed',
            properties={
                'transaction_id': transaction_data['transaction_id'],
                'revenue': transaction_data['value'],
                'product_category': transaction_data.get('category')
            }
        )
        self.mixpanel.track_revenue(
            distinct_id=user_id,
            amount=transaction_data['value']
        )

        # Amplitude
        self.amplitude.track_event(
            user_id=user_id,
            event_type='Purchase Completed',
            event_properties={
                'transaction_id': transaction_data['transaction_id'],
                'amount': transaction_data['value']
            }
        )
        self.amplitude.track_revenue(
            user_id=user_id,
            product_id=transaction_data['items'][0]['item_id'],
            price=transaction_data['value'],
            quantity=1
        )

        # Segment (will fan out to destinations)
        self.segment.track(
            user_id=user_id,
            event='Order Completed',
            properties={
                'order_id': transaction_data['transaction_id'],
                'total': transaction_data['value'],
                'revenue': transaction_data['value'],
                'currency': transaction_data.get('currency', 'USD'),
                'products': transaction_data['items']
            }
        )

    def identify_user(self, user_id, user_properties):
        """Identify user across all platforms"""
        # GA4
        # (User properties set per event)

        # Mixpanel
        self.mixpanel.set_user_properties(
            distinct_id=user_id,
            properties=user_properties
        )

        # Amplitude
        self.amplitude.identify_user(
            user_id=user_id,
            user_properties=user_properties
        )

        # Segment
        self.segment.identify(
            user_id=user_id,
            traits=user_properties
        )
```

---

## Custom Dimensions & Properties

### GA4 Custom Dimensions

```python
# Configure custom dimensions in GA4 interface
CUSTOM_DIMENSIONS = {
    'user_scoped': [
        'customer_tier',
        'signup_method',
        'lifetime_value_bucket',
        'preferred_category'
    ],
    'event_scoped': [
        'ab_test_variant',
        'promo_code',
        'referral_source',
        'content_type'
    ]
}

# Track with custom dimensions
ga4_tracker.track_custom_event(
    client_id='user_12345',
    event_name='page_view',
    parameters={
        'page_location': 'https://example.com/products',
        'ab_test_variant': 'variant_a',  # Custom dimension
        'content_type': 'product_listing'  # Custom dimension
    }
)
```

### Mixpanel Super Properties

```javascript
// Set super properties (sent with every event)
mixpanel.register({
  'Plan': 'Premium',
  'Environment': 'Production',
  'App Version': '2.1.0'
});

// Set super properties once
mixpanel.register_once({
  'First Touch Source': 'google_ads',
  'Signup Date': '2024-01-15'
});
```

---

## Data Export & Warehousing

### GA4 BigQuery Export

```python
from google.cloud import bigquery

class GA4BigQueryExport:
    """Query GA4 data from BigQuery"""

    def __init__(self, project_id, dataset_id):
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = dataset_id

    def query_events(self, start_date, end_date, event_name=None):
        """Query events from GA4 BigQuery export"""
        query = f"""
        SELECT
            event_date,
            event_timestamp,
            event_name,
            user_pseudo_id,
            (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location') as page_location,
            (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'engagement_time_msec') as engagement_time
        FROM
            `{self.dataset_id}.events_*`
        WHERE
            _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'
        """

        if event_name:
            query += f" AND event_name = '{event_name}'"

        results = self.client.query(query)
        return [dict(row) for row in results]

    def query_ecommerce_revenue(self, start_date, end_date):
        """Query e-commerce revenue"""
        query = f"""
        SELECT
            event_date,
            COUNT(DISTINCT user_pseudo_id) as unique_purchasers,
            COUNT(DISTINCT (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'transaction_id')) as transactions,
            SUM((SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'value') / 1000000) as revenue
        FROM
            `{self.dataset_id}.events_*`
        WHERE
            _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'
            AND event_name = 'purchase'
        GROUP BY
            event_date
        ORDER BY
            event_date
        """

        results = self.client.query(query)
        return [dict(row) for row in results]
```

---

## Attribution Modeling

### Multi-Touch Attribution

```python
class AttributionModel:
    """Multi-touch attribution modeling"""

    def __init__(self, touchpoints):
        self.touchpoints = touchpoints

    def linear_attribution(self):
        """Equal credit to all touchpoints"""
        credit_per_touchpoint = 1.0 / len(self.touchpoints)

        return [
            {
                'touchpoint': tp,
                'credit': credit_per_touchpoint
            }
            for tp in self.touchpoints
        ]

    def time_decay_attribution(self, half_life_days=7):
        """More credit to recent touchpoints"""
        import math
        from datetime import datetime

        if not self.touchpoints:
            return []

        # Calculate time-based weights
        last_touchpoint_time = self.touchpoints[-1]['timestamp']
        weights = []

        for tp in self.touchpoints:
            days_before_conversion = (last_touchpoint_time - tp['timestamp']).days
            weight = math.exp(-days_before_conversion / half_life_days)
            weights.append(weight)

        total_weight = sum(weights)

        return [
            {
                'touchpoint': tp,
                'credit': weight / total_weight
            }
            for tp, weight in zip(self.touchpoints, weights)
        ]

    def position_based_attribution(self, first_touch_credit=0.4, last_touch_credit=0.4):
        """40-20-40 model (first, middle, last)"""
        if len(self.touchpoints) == 1:
            return [{'touchpoint': self.touchpoints[0], 'credit': 1.0}]

        middle_credit = 1.0 - first_touch_credit - last_touch_credit
        middle_touchpoints = len(self.touchpoints) - 2

        if middle_touchpoints > 0:
            middle_credit_each = middle_credit / middle_touchpoints
        else:
            middle_credit_each = 0

        attribution = []

        for i, tp in enumerate(self.touchpoints):
            if i == 0:
                credit = first_touch_credit
            elif i == len(self.touchpoints) - 1:
                credit = last_touch_credit
            else:
                credit = middle_credit_each

            attribution.append({
                'touchpoint': tp,
                'credit': credit
            })

        return attribution

# Usage
touchpoints = [
    {'channel': 'organic_search', 'timestamp': datetime(2024, 1, 1)},
    {'channel': 'email', 'timestamp': datetime(2024, 1, 5)},
    {'channel': 'paid_social', 'timestamp': datetime(2024, 1, 10)},
    {'channel': 'direct', 'timestamp': datetime(2024, 1, 15)}
]

attribution = AttributionModel(touchpoints)

# Linear attribution
linear = attribution.linear_attribution()
# Each touchpoint gets 25% credit

# Time decay
time_decay = attribution.time_decay_attribution()
# More recent touchpoints get more credit

# Position based
position_based = attribution.position_based_attribution()
# First: 40%, Middle: 10% each, Last: 40%
```

---

## Privacy & Compliance

### GDPR/CCPA Compliance

```python
class PrivacyCompliance:
    """Handle privacy and consent management"""

    def __init__(self, analytics_clients):
        self.clients = analytics_clients

    def check_consent(self, user_id):
        """Check user consent status"""
        # Query consent management platform
        consent_status = self.get_consent_from_cmp(user_id)

        return {
            'analytics': consent_status.get('analytics', False),
            'marketing': consent_status.get('marketing', False),
            'personalization': consent_status.get('personalization', False)
        }

    def anonymize_user_data(self, user_id):
        """Anonymize user data across platforms"""
        # Mixpanel
        self.clients['mixpanel'].track_event(
            distinct_id=user_id,
            event_name='$delete',
            properties={}
        )

        # Amplitude - use Privacy API
        # Segment - use GDPR Delete API

        return True

    def export_user_data(self, user_id):
        """Export all user data (GDPR right to access)"""
        user_data = {
            'user_id': user_id,
            'platforms': {}
        }

        # Export from each platform
        # Implementation specific to each platform's export API

        return user_data
```

---

## Testing & Validation

### Event Validation

```python
class EventValidator:
    """Validate analytics events"""

    def __init__(self, event_schema):
        self.schema = event_schema

    def validate_event(self, event_name, properties):
        """Validate event against schema"""
        if event_name not in self.schema:
            return {
                'valid': False,
                'errors': [f'Unknown event: {event_name}']
            }

        schema = self.schema[event_name]
        errors = []

        # Check required properties
        for required_prop in schema.get('required_properties', []):
            if required_prop not in properties:
                errors.append(f'Missing required property: {required_prop}')

        # Validate property types
        for prop, value in properties.items():
            if prop in schema.get('property_types', {}):
                expected_type = schema['property_types'][prop]
                if not isinstance(value, expected_type):
                    errors.append(
                        f'Invalid type for {prop}: expected {expected_type.__name__}, '
                        f'got {type(value).__name__}'
                    )

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

# Usage
validator = EventValidator(ECOMMERCE_EVENTS)

result = validator.validate_event(
    'product_viewed',
    {'product_id': 'PROD-123', 'product_name': 'Headphones', 'price': 99.99}
)

if not result['valid']:
    print(f"Validation errors: {result['errors']}")
```

---

## Integration Patterns

### Unified Analytics Layer

```python
class UnifiedAnalytics:
    """Unified analytics layer for all platforms"""

    def __init__(self):
        self.ga4 = GA4ServerTracking('G-XXXXX', 'secret')
        self.mixpanel = MixpanelTracking('token')
        self.amplitude = AmplitudeTracking('api_key')
        self.segment = SegmentTracking('write_key')

    def track(self, event_name, properties, user_id=None, anonymous_id=None):
        """Track event across all platforms"""
        # Use Segment as the primary integration point
        self.segment.track(
            user_id=user_id,
            event=event_name,
            properties=properties,
            anonymous_id=anonymous_id
        )

        # Direct integrations for platforms not in Segment
        # or for redundancy

    def identify(self, user_id, traits):
        """Identify user across all platforms"""
        self.segment.identify(user_id=user_id, traits=traits)

# Usage
analytics = UnifiedAnalytics()

analytics.track(
    event_name='Purchase Completed',
    properties={
        'order_id': 'T_12345',
        'revenue': 299.99,
        'products': [...]
    },
    user_id='user_12345'
)
```

---

## Conclusion

This guide provides comprehensive coverage of marketing analytics integration across major platforms. For production implementations:

1. Implement consistent event taxonomies
2. Use Segment or similar CDP for centralized tracking
3. Validate events before sending
4. Implement proper consent management
5. Set up data exports to warehouses
6. Monitor data quality and completeness
7. Test thoroughly in development
8. Document all custom events and properties

For official documentation:
- [GA4 Documentation](https://developers.google.com/analytics/devguides/collection/ga4)
- [Mixpanel Documentation](https://developer.mixpanel.com/docs)
- [Amplitude Documentation](https://www.docs.developers.amplitude.com/)
- [Segment Documentation](https://segment.com/docs/)
