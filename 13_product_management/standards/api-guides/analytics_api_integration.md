# Analytics API Integration Guide for Product Managers

## Overview

Analytics APIs are critical infrastructure for modern product management. This guide covers integration patterns with leading analytics platforms: Amplitude, Mixpanel, and Segment. Understanding these integrations enables PMs to make data-driven decisions, track user behaviors, and measure product performance.

### Why Analytics Integration Matters for PMs

Product Managers rely on analytics to:
- Track feature adoption and user engagement
- Monitor product health metrics and KPIs
- Understand user journey and conversion funnels
- Validate hypotheses through A/B testing
- Create data-driven product roadmaps
- Generate insights for stakeholder presentations

---

## Amplitude API Integration

### Authentication & Setup

Amplitude uses API keys for authentication. There are two types of keys:
- **API Key**: For sending events from client or server
- **Secret Key**: For server-to-server communication with Amplitude APIs

#### Environment Configuration

```bash
# .env file setup
AMPLITUDE_API_KEY=your_amplitude_api_key
AMPLITUDE_SECRET_KEY=your_amplitude_secret_key
AMPLITUDE_REGION=US  # or EU
```

#### SDK Installation

```bash
# Using npm/yarn
npm install @amplitude/analytics-browser
npm install @amplitude/analytics-node

# Using pip for Python
pip install amplitude
```

### Event Tracking Implementation

#### Browser-Based Event Tracking

```javascript
// Initialize Amplitude SDK
import * as amplitude from '@amplitude/analytics-browser';

amplitude.init(process.env.REACT_APP_AMPLITUDE_API_KEY, {
  userId: 'user123',
  sessionId: 'session456',
  defaultTracking: {
    pageViews: true,
    sessions: true,
    formInteractions: true,
    fileDownloads: true,
  },
});

// Track custom events
amplitude.track('Feature Viewed', {
  featureName: 'product_dashboard',
  section: 'analytics',
  timestamp: new Date().toISOString(),
});

// Track with user properties
amplitude.setUserId('user_456');
amplitude.setUserProperties({
  plan: 'enterprise',
  organizationId: 'org_789',
  signupDate: '2024-01-15',
});
```

#### Server-Side Event Tracking

```python
from amplitude import Amplitude
from datetime import datetime

# Initialize client
client = Amplitude(api_key=os.getenv('AMPLITUDE_API_KEY'))

# Track event
event = {
    'user_id': 'user_123',
    'event_type': 'feature_purchased',
    'event_properties': {
        'feature_name': 'advanced_analytics',
        'price': 99.99,
        'currency': 'USD',
        'plan_type': 'annual'
    },
    'user_properties': {
        'company_size': 'enterprise',
        'industry': 'saas'
    },
    'timestamp': int(datetime.now().timestamp() * 1000)
}

client.track(event)
```

### Amplitude REST API Usage

#### Query User Events

```bash
curl -X GET \
  "https://api.amplitude.com/api/2/userevents?user_id=user_123&limit=100" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Response example
{
  "user": {
    "user_id": "user_123",
    "properties": {
      "plan": "enterprise",
      "region": "EMEA"
    }
  },
  "events": [
    {
      "event_type": "feature_viewed",
      "event_properties": {
        "feature_name": "dashboard"
      },
      "timestamp": 1642598400000
    }
  ]
}
```

#### Export User Cohorts

```python
import requests
from typing import List

class AmplitudeExport:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.amplitude.com"

    def export_cohort(self, cohort_id: str) -> List[str]:
        """Export users from a specific cohort"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(
            f"{self.base_url}/api/3/cohorts/{cohort_id}/members",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()['members']
        else:
            raise Exception(f"Failed to export cohort: {response.text}")

    def get_retention_data(self, event: str, period: str = "daily"):
        """Get retention metrics for a specific event"""
        payload = {
            "e": {
                "filters": [{
                    "type": "event",
                    "value": event
                }]
            },
            "m": "retention",
            "p": period
        }

        response = requests.post(
            f"{self.base_url}/api/2/events/segmentation",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

        return response.json()
```

### Common PM Use Cases

```javascript
// Track feature adoption
function trackFeatureAdoption(featureName, userId) {
  amplitude.track('Feature Adopted', {
    feature_name: featureName,
    adoption_date: new Date().toISOString(),
    user_segment: getUserSegment(userId),
  });
}

// Track conversion funnel
function trackFunnelStep(stepName, metadata) {
  amplitude.track('Funnel Step', {
    step_name: stepName,
    step_number: getStepNumber(stepName),
    ...metadata,
  });
}

// Track product health metrics
function trackHealthMetric(metricName, value) {
  amplitude.track('Health Metric', {
    metric_name: metricName,
    metric_value: value,
    timestamp: new Date().toISOString(),
  });
}
```

---

## Mixpanel API Integration

### Authentication & Setup

Mixpanel uses project tokens and API credentials for different API endpoints.

```bash
# .env configuration
MIXPANEL_TOKEN=your_project_token
MIXPANEL_API_SECRET=your_api_secret
MIXPANEL_API_KEY=your_api_key
```

#### SDK Installation

```bash
npm install mixpanel-browser
pip install mixpanel
```

### Event Tracking with Mixpanel

#### Browser Client Implementation

```javascript
import mixpanel from 'mixpanel-browser';

// Initialize
mixpanel.init(process.env.REACT_APP_MIXPANEL_TOKEN, {
  track_pageview: false,
  persistence: 'localStorage',
  cross_subdomain_cookie: false,
});

// Identify user
mixpanel.identify('user_123');

// Set user properties
mixpanel.people.set({
  'Plan': 'Enterprise',
  'Company': 'TechCorp',
  'Sign-up Date': new Date(),
});

// Track events
mixpanel.track('Dashboard Viewed', {
  'dashboard_type': 'executive',
  'num_widgets': 8,
  'load_time_ms': 1250,
});
```

#### Server-Side Implementation

```python
from mixpanel import Mixpanel
import json
from datetime import datetime

class MixpanelProductAnalytics:
    def __init__(self, token: str, api_secret: str):
        self.mp = Mixpanel(token)
        self.api_secret = api_secret
        self.base_url = "https://api.mixpanel.com"

    def track_event(self, distinct_id: str, event_name: str, properties: dict):
        """Track an event in Mixpanel"""
        self.mp.track(distinct_id, event_name, properties)

    def set_user_properties(self, distinct_id: str, properties: dict):
        """Set user properties in Mixpanel"""
        self.mp.people_set(distinct_id, properties)

    def query_retention(self, event: str, interval: int = 7):
        """Query retention using Mixpanel API"""
        import requests

        params = {
            'token': self.token,
            'event': event,
            'unit': 'day',
            'interval': interval,
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
        }

        response = requests.get(
            f"{self.base_url}/api/2/retention",
            params=params
        )

        return response.json()

    def get_funnel_analysis(self, funnel_name: str, events: list):
        """Analyze funnel conversion"""
        import requests

        params = {
            'token': self.token,
            'funnel_id': funnel_name,
        }

        response = requests.get(
            f"{self.base_url}/api/2/funnels",
            params=params
        )

        return response.json()
```

### Mixpanel Data Export API

```bash
# Export raw data for custom analysis
curl -X GET \
  "https://data.mixpanel.com/api/2.0/export" \
  -u YOUR_API_SECRET: \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-01-31",
    "event": ["Purchase", "SignUp"]
  }'

# Export user profiles
curl -X POST \
  "https://data.mixpanel.com/api/2.0/engage" \
  -u YOUR_API_SECRET: \
  -d '{
    "where": {"properties": {"Plan": {"$eq": "Enterprise"}}}
  }'
```

---

## Segment API Integration

### Architecture Overview

Segment acts as a data collection hub, routing events to multiple analytics platforms.

```
Your Application
    ↓
Segment API
    ├→ Amplitude
    ├→ Mixpanel
    ├→ Google Analytics
    ├→ Data Warehouse (BigQuery, Redshift)
    └→ 200+ Integrations
```

### Setup & Authentication

```javascript
// Initialize Segment
import Analytics from '@segment/analytics-next';

const analytics = Analytics.load({
  writeKey: process.env.REACT_APP_SEGMENT_WRITE_KEY,
  cdnURL: 'https://cdn.segment.com',
});

// Identify user
analytics.identify('user_123', {
  email: 'user@example.com',
  plan: 'enterprise',
  signupDate: '2024-01-15',
  organizationId: 'org_456',
});

// Track events
analytics.track('Feature Purchased', {
  featureName: 'advanced_dashboard',
  price: 99.99,
  currency: 'USD',
  timestamp: new Date().toISOString(),
});
```

### Server-Side Segment Integration

```python
import analytics
import os
from datetime import datetime

# Configure Segment
analytics.write_key = os.getenv('SEGMENT_WRITE_KEY')

class SegmentProductEvents:
    @staticmethod
    def track_event(user_id: str, event_name: str, properties: dict):
        """Track event via Segment"""
        analytics.track(
            user_id=user_id,
            event=event_name,
            properties=properties,
            timestamp=datetime.utcnow()
        )

    @staticmethod
    def identify_user(user_id: str, traits: dict):
        """Identify user with traits"""
        analytics.identify(
            user_id=user_id,
            traits=traits
        )

    @staticmethod
    def create_group(user_id: str, group_id: str, group_traits: dict):
        """Create/update a group (organization)"""
        analytics.group(
            user_id=user_id,
            group_id=group_id,
            traits=group_traits
        )

# Flush events before shutdown
analytics.flush()
```

### Event Naming Conventions

```javascript
// Segment recommends object-action naming convention
// object: the thing being acted upon
// action: what's being done

// Good examples:
analytics.track('Feature Viewed', {...});
analytics.track('Feature Created', {...});
analytics.track('Feature Deleted', {...});
analytics.track('Plan Upgraded', {...});
analytics.track('Settings Updated', {...});

// Always include context
analytics.track('Button Clicked', {
  buttonName: 'pricing_cta',
  pageTitle: 'landing_page',
  buttonPosition: 'hero_section',
});
```

---

## Authentication Best Practices

### Secure Credential Management

```javascript
// ❌ DON'T - Never hardcode credentials
const apiKey = 'live_abc123xyz';

// ✅ DO - Use environment variables
const apiKey = process.env.ANALYTICS_API_KEY;

// ✅ DO - Use secrets management service
import AWS from 'aws-sdk';

async function getAnalyticsCredentials() {
  const secretsManager = new AWS.SecretsManager();
  const secret = await secretsManager
    .getSecretValue({ SecretId: 'analytics-api-key' })
    .promise();

  return JSON.parse(secret.SecretString);
}
```

### Rate Limiting & Error Handling

```python
import time
from functools import wraps
from typing import Callable

def rate_limit(max_requests: int = 100, time_window: int = 60):
    """Decorator to rate limit API calls"""
    def decorator(func: Callable):
        calls = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls = [call for call in calls if call > now - time_window]

            if len(calls) >= max_requests:
                wait_time = calls[0] + time_window - now
                time.sleep(wait_time)

            calls.append(now)
            return func(*args, **kwargs)

        return wrapper
    return decorator

@rate_limit(max_requests=100, time_window=60)
def call_analytics_api(endpoint: str, params: dict):
    """Make rate-limited API call"""
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Implement exponential backoff
        retry_after = int(response.headers.get('Retry-After', 5))
        time.sleep(retry_after)
        raise Exception(f"API Error: {str(e)}")
```

---

## Integration Testing & Validation

### Testing Event Tracking

```javascript
// Jest test example
describe('Analytics Tracking', () => {
  let amplitudeTrackSpy;

  beforeEach(() => {
    amplitudeTrackSpy = jest.spyOn(amplitude, 'track');
  });

  afterEach(() => {
    amplitudeTrackSpy.mockRestore();
  });

  test('tracks feature adoption event', () => {
    trackFeatureAdoption('new_dashboard', 'user_123');

    expect(amplitudeTrackSpy).toHaveBeenCalledWith(
      'Feature Adopted',
      expect.objectContaining({
        feature_name: 'new_dashboard',
      })
    );
  });

  test('includes required event properties', () => {
    trackEvent('Purchase', {
      productId: '456',
      price: 99.99,
    });

    expect(amplitudeTrackSpy).toHaveBeenCalledWith(
      'Purchase',
      expect.objectContaining({
        timestamp: expect.any(String),
        user_id: expect.any(String),
      })
    );
  });
});
```

### Data Quality Validation

```python
class AnalyticsValidator:
    @staticmethod
    def validate_event_schema(event: dict, required_fields: list) -> bool:
        """Validate event has required properties"""
        return all(field in event for field in required_fields)

    @staticmethod
    def validate_user_properties(properties: dict) -> bool:
        """Ensure user properties meet data standards"""
        required_props = ['email', 'plan', 'signup_date']

        # Check required properties exist
        if not all(prop in properties for prop in required_props):
            return False

        # Validate property types
        if not isinstance(properties.get('email'), str):
            return False

        if properties.get('plan') not in ['free', 'pro', 'enterprise']:
            return False

        return True

# Usage
event = {
    'user_id': 'user_123',
    'event_type': 'purchase',
    'properties': {'product_id': '456', 'price': 99.99}
}

if AnalyticsValidator.validate_event_schema(event, ['user_id', 'event_type']):
    send_to_amplitude(event)
```

---

## Common Patterns & PM Workflows

### Feature Launch Analytics

```javascript
function launchFeatureAnalytics(featureName, launchDate, targetAudience) {
  // Pre-launch tracking setup
  amplitude.setUserProperties({
    feature_launch_audience: targetAudience,
    feature_version: 'v1.0',
  });

  // Track when feature becomes available
  amplitude.track('Feature Launch', {
    feature_name: featureName,
    launch_date: launchDate,
    target_audience: targetAudience,
    rollout_percentage: 100,
  });

  // Track early adoption
  setTimeout(() => {
    amplitude.track('Feature Adoption Tracking Started', {
      feature_name: featureName,
      tracking_started_at: new Date().toISOString(),
    });
  }, 5000);
}
```

### Retention & Churn Analysis

```python
class RetentionAnalytics:
    def __init__(self, analytics_client):
        self.client = analytics_client

    def calculate_retention_cohort(self, signup_date_start, signup_date_end):
        """Calculate retention by signup cohort"""
        return self.client.query_retention(
            event='active_session',
            cohort_property='signup_date',
            cohort_start=signup_date_start,
            cohort_end=signup_date_end,
            retention_period=30  # days
        )

    def identify_churn_risk_users(self, threshold_days=7):
        """Identify users at risk of churning"""
        return self.client.query_events(
            query={
                'event': 'last_active_session',
                'last_seen_before': f'{threshold_days} days ago'
            }
        )

# Usage
retention = RetentionAnalytics(amplitude_client)
cohort_data = retention.calculate_retention_cohort(
    signup_date_start='2024-01-01',
    signup_date_end='2024-03-31'
)
```

---

## API Documentation Best Practices

### Documentation Structure

1. **Authentication Section**: Clear credential setup
2. **API Reference**: Endpoints with request/response examples
3. **Code Examples**: Multiple languages (JavaScript, Python, etc.)
4. **Error Handling**: Common error codes and troubleshooting
5. **Rate Limits**: API quotas and throttling strategies
6. **Best Practices**: Do's and don'ts
7. **Troubleshooting**: Common issues and solutions

### Maintaining Documentation

- Keep examples updated with current SDK versions
- Include changelog for API updates
- Link to official vendor documentation
- Provide runnable example code
- Document custom analytics schema used internally

---

## Conclusion

Analytics API integration is fundamental to data-driven product management. By implementing Amplitude, Mixpanel, and Segment integrations with proper authentication, event tracking, and error handling, PMs can access comprehensive product insights needed for informed decision-making.

Key takeaways:
- Use environment variables for all credentials
- Implement consistent event naming conventions
- Validate data quality before sending to analytics platforms
- Monitor API rate limits and implement backoff strategies
- Test analytics implementations with proper unit tests
- Document your analytics schema for team alignment
