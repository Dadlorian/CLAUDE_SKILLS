# Feature Flags Reference

## Overview
Feature flags (also called feature toggles, feature switches) allow you to enable or disable functionality without deploying new code. They are essential for progressive delivery, A/B testing, and reducing deployment risk.

---

## Types of Feature Flags

### 1. Release Flags (Release Toggles)
**Purpose**: Control rollout of new features

**Characteristics**:
- Short-lived (days to weeks)
- Removed after feature is fully released
- Enable gradual rollout
- Allow quick rollback

**Example**:
```python
if feature_flags.is_enabled('new-checkout-flow', user):
    return new_checkout_process(user)
else:
    return legacy_checkout_process(user)
```

**Lifecycle**: Deploy → Test → Gradual Rollout → Full Release → Remove Flag

---

### 2. Experiment Flags (A/B Test Toggles)
**Purpose**: A/B testing and multivariate testing

**Characteristics**:
- Medium-lived (weeks to months)
- Collect metrics per variant
- Statistical analysis required
- User assignment consistency

**Example**:
```javascript
const variant = experimentService.getVariant('homepage-redesign', userId);

if (variant === 'control') {
    renderOriginalHomepage();
} else if (variant === 'variant-a') {
    renderHomepageVariantA();
} else if (variant === 'variant-b') {
    renderHomepageVariantB();
}

// Track metrics
analytics.track('homepage-viewed', { variant });
```

**Facebook's Approach**:
- Thousands of simultaneous experiments
- Sophisticated bucketing system
- Automated statistical analysis
- Experiment interaction detection

---

### 3. Ops Flags (Operational Toggles)
**Purpose**: Operational control of system behavior

**Characteristics**:
- Long-lived or permanent
- Control system behavior under load
- Circuit breaker functionality
- Performance tuning

**Example**:
```java
// Circuit breaker pattern
if (featureFlags.isEnabled("use-cache")) {
    return cacheService.get(key);
} else {
    return database.query(key);
}

// Load shedding
if (featureFlags.isEnabled("enable-rate-limiting")) {
    rateLimiter.checkLimit(request);
}
```

**Netflix's Approach**:
- Dynamic property system (Archaius)
- Real-time configuration updates
- Cascading failure prevention
- Regional traffic control

---

### 4. Permission Flags (Entitlement Toggles)
**Purpose**: Control access to premium or user-specific features

**Characteristics**:
- Long-lived or permanent
- Based on user entitlements
- Subscription tiers
- Geographic restrictions

**Example**:
```ruby
def can_access_premium_feature?(user)
  feature_flags.is_enabled('premium-analytics', user) &&
  user.subscription_tier == 'premium'
end
```

---

## Feature Flag Platforms

### LaunchDarkly

#### Overview
- Enterprise feature flag management
- Real-time updates (SSE/WebSockets)
- Sophisticated targeting rules
- Built-in A/B testing
- SDKs for 20+ languages

#### Key Features
```yaml
Feature Capabilities:
  - Real-time flag updates
  - Percentage rollouts
  - User/segment targeting
  - Multi-variate flags
  - Kill switches
  - Dependency management
  - Flag scheduling
  - Audit logs

Targeting Rules:
  - User attributes
  - Custom attributes
  - Segment membership
  - Percentage buckets
  - Geographic location
  - Device type
```

#### Example Configuration
```json
{
  "key": "new-recommendation-engine",
  "variations": [
    { "value": false, "name": "Original" },
    { "value": true, "name": "New Engine" }
  ],
  "targeting": {
    "rules": [
      {
        "clauses": [
          {
            "attribute": "country",
            "op": "in",
            "values": ["US", "CA"]
          }
        ],
        "variation": 1,
        "rollout": {
          "bucketBy": "userId",
          "variations": [
            { "variation": 0, "weight": 90000 },
            { "variation": 1, "weight": 10000 }
          ]
        }
      }
    ]
  }
}
```

#### SDK Usage Example
```python
import ldclient
from ldclient.config import Config

# Initialize
ldclient.set_config(Config("sdk-key-123xyz"))
ld_client = ldclient.get()

# User context
user = {
    "key": "user-123",
    "email": "user@example.com",
    "custom": {
        "tier": "premium",
        "country": "US"
    }
}

# Evaluate flag
show_new_feature = ld_client.variation("new-feature", user, False)

if show_new_feature:
    enable_new_feature()
else:
    use_old_feature()
```

#### Pricing Considerations
- Seats: $10-20/user/month
- MAU: Based on monthly active users
- Enterprise: Custom pricing
- Self-hosted option available

---

### Unleash

#### Overview
- Open-source feature flag platform
- Self-hosted or cloud
- Client SDKs for 15+ languages
- Admin UI included
- Free for self-hosted

#### Key Features
```yaml
Activation Strategies:
  - Standard (on/off)
  - UserIDs (whitelist)
  - Gradual Rollout (percentage)
  - IPs (IP whitelist)
  - Hostname
  - Custom strategies

Unique Features:
  - Stale flag detection
  - Flag variants (A/B/n testing)
  - API-first design
  - Metrics integration
  - Project segmentation
```

#### Example Configuration
```javascript
// unleash-config.js
const unleash = require('unleash-client');

unleash.initialize({
  url: 'https://unleash.example.com/api/',
  appName: 'my-application',
  instanceId: 'instance-1',
  customHeaders: {
    Authorization: 'API-token-xyz'
  }
});

// Usage
if (unleash.isEnabled('new-payment-flow', context)) {
  processNewPayment();
} else {
  processLegacyPayment();
}

// With variant
const variant = unleash.getVariant('homepage-test', context);
if (variant.name === 'blue') {
  renderBlueHomepage();
} else if (variant.name === 'green') {
  renderGreenHomepage();
}
```

#### Strategy Configuration
```json
{
  "name": "gradual-rollout-user-id",
  "parameters": {
    "percentage": "25",
    "groupId": "new-feature"
  }
}
```

#### Self-Hosting
```yaml
# docker-compose.yml
version: '3.8'
services:
  unleash:
    image: unleashorg/unleash-server:latest
    ports:
      - "4242:4242"
    environment:
      DATABASE_URL: postgres://unleash:password@postgres/unleash
      DATABASE_SSL: "false"
    depends_on:
      - postgres

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: unleash
      POSTGRES_USER: unleash
      POSTGRES_PASSWORD: password
```

---

### Split.io

#### Overview
- Enterprise platform with focus on experimentation
- Feature flags + A/B testing + analytics
- Real-time data pipeline
- Advanced statistical engine

#### Key Features
- Feature impact analysis
- Automated metric calculation
- Multi-armed bandit algorithms
- Advanced user segmentation
- Traffic type segregation

---

### Custom Implementation

#### Simple In-Memory Implementation
```python
# feature_flags.py
class FeatureFlagService:
    def __init__(self):
        self.flags = {
            'new-ui': {
                'enabled': True,
                'rollout_percentage': 50,
                'whitelist': ['user-123', 'user-456'],
                'blacklist': []
            },
            'beta-feature': {
                'enabled': False,
                'rollout_percentage': 0,
                'whitelist': [],
                'blacklist': []
            }
        }

    def is_enabled(self, flag_name, user_id):
        if flag_name not in self.flags:
            return False

        flag = self.flags[flag_name]

        # Check if globally disabled
        if not flag['enabled']:
            return False

        # Check blacklist
        if user_id in flag['blacklist']:
            return False

        # Check whitelist
        if user_id in flag['whitelist']:
            return True

        # Check percentage rollout
        user_hash = hash(f"{flag_name}:{user_id}") % 100
        return user_hash < flag['rollout_percentage']
```

#### Database-Backed Implementation
```sql
-- Schema
CREATE TABLE feature_flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT false,
    rollout_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE feature_flag_rules (
    id SERIAL PRIMARY KEY,
    flag_id INTEGER REFERENCES feature_flags(id),
    rule_type VARCHAR(50), -- 'user_id', 'segment', 'attribute'
    attribute_name VARCHAR(255),
    operator VARCHAR(50), -- 'equals', 'contains', 'in', etc.
    value TEXT,
    enabled BOOLEAN DEFAULT true
);

CREATE TABLE feature_flag_overrides (
    id SERIAL PRIMARY KEY,
    flag_id INTEGER REFERENCES feature_flags(id),
    user_id VARCHAR(255),
    enabled BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);
```

```python
# database_feature_flags.py
from typing import Dict, Any
import psycopg2

class DatabaseFeatureFlagService:
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)

    def is_enabled(self, flag_name: str, context: Dict[str, Any]) -> bool:
        cursor = self.conn.cursor()

        # Get flag
        cursor.execute(
            "SELECT enabled, rollout_percentage FROM feature_flags WHERE name = %s",
            (flag_name,)
        )
        result = cursor.fetchone()

        if not result or not result[0]:
            return False

        enabled, rollout_percentage = result
        user_id = context.get('user_id')

        # Check user override
        if user_id:
            cursor.execute(
                """
                SELECT enabled FROM feature_flag_overrides
                WHERE flag_id = (SELECT id FROM feature_flags WHERE name = %s)
                AND user_id = %s
                """,
                (flag_name, user_id)
            )
            override = cursor.fetchone()
            if override:
                return override[0]

        # Check rules (simplified)
        # ... rule evaluation logic ...

        # Check percentage rollout
        if user_id:
            user_hash = hash(f"{flag_name}:{user_id}") % 100
            return user_hash < rollout_percentage

        return False
```

#### Redis-Based Implementation (Fast Lookups)
```python
# redis_feature_flags.py
import redis
import json
import hashlib

class RedisFeatureFlagService:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.cache_ttl = 60  # 1 minute cache

    def is_enabled(self, flag_name: str, user_id: str) -> bool:
        # Get flag configuration from Redis
        flag_key = f"flag:{flag_name}"
        flag_data = self.redis.get(flag_key)

        if not flag_data:
            return False

        flag = json.loads(flag_data)

        if not flag.get('enabled', False):
            return False

        # Check whitelist (Redis Set)
        whitelist_key = f"flag:{flag_name}:whitelist"
        if self.redis.sismember(whitelist_key, user_id):
            return True

        # Check blacklist (Redis Set)
        blacklist_key = f"flag:{flag_name}:blacklist"
        if self.redis.sismember(blacklist_key, user_id):
            return False

        # Percentage rollout with consistent hashing
        rollout_percentage = flag.get('rollout_percentage', 0)
        user_bucket = self._get_bucket(flag_name, user_id)

        return user_bucket < rollout_percentage

    def _get_bucket(self, flag_name: str, user_id: str) -> int:
        """Consistent hashing for user bucketing (0-99)"""
        hash_input = f"{flag_name}:{user_id}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()
        return int(hash_value, 16) % 100

    def set_flag(self, flag_name: str, config: dict):
        """Update flag configuration"""
        flag_key = f"flag:{flag_name}"
        self.redis.set(flag_key, json.dumps(config))

    def add_to_whitelist(self, flag_name: str, user_id: str):
        whitelist_key = f"flag:{flag_name}:whitelist"
        self.redis.sadd(whitelist_key, user_id)
```

---

## Best Practices

### 1. Naming Conventions
```
Good Names:
- enable-new-checkout
- experiment-homepage-redesign
- kill-switch-recommendation-service
- premium-analytics-access

Bad Names:
- flag1
- test
- new_feature
- temp
```

### 2. Flag Lifecycle Management

```mermaid
graph LR
    A[Create] --> B[Test]
    B --> C[Gradual Rollout]
    C --> D[100% Enabled]
    D --> E[Remove Flag]
    E --> F[Clean Up Code]
```

**Process**:
1. **Create**: Add flag with default OFF
2. **Test**: Enable for internal users/QA
3. **Rollout**: Gradual percentage increase
4. **Stabilize**: 100% enabled, monitor
5. **Remove**: Delete flag configuration
6. **Clean**: Remove flag checks from code

### 3. Flag Debt Management

**Set Expiration Dates**:
```python
feature_flag = {
    'name': 'new-search-algorithm',
    'created_at': '2024-01-15',
    'expected_removal_date': '2024-02-15',
    'owner': 'search-team',
    'rollout_complete_date': None
}
```

**Automated Alerts**:
```python
def check_stale_flags():
    """Alert on flags older than 90 days"""
    for flag in get_all_flags():
        age_days = (datetime.now() - flag.created_at).days
        if age_days > 90 and flag.rollout_percentage == 100:
            alert(f"Flag {flag.name} is stale and should be removed")
```

### 4. Consistent User Bucketing

**DO**: Use stable user identifier
```python
# Good - consistent per user
bucket = hash(f"{flag_name}:{user.id}") % 100

# Bad - changes per request
bucket = hash(f"{flag_name}:{request.id}") % 100
```

**Bucketing Salt**: Use flag name in hash to ensure different flags have different distributions
```python
def get_bucket(flag_name: str, user_id: str) -> int:
    # Including flag_name ensures each flag has independent distribution
    hash_input = f"{flag_name}:{user_id}"
    return hash(hash_input) % 100
```

### 5. Default Values

**Always Provide Defaults**:
```javascript
// Good
const enabled = featureFlags.isEnabled('new-feature', user, false);

// Bad - can throw if flag missing
const enabled = featureFlags.isEnabled('new-feature', user);
```

### 6. Testing with Feature Flags

**Unit Tests**:
```python
def test_new_feature_enabled():
    with feature_flags_override({'new-feature': True}):
        result = process_request(user)
        assert result.used_new_feature == True

def test_new_feature_disabled():
    with feature_flags_override({'new-feature': False}):
        result = process_request(user)
        assert result.used_new_feature == False
```

**Integration Tests**:
```python
@pytest.fixture
def feature_flag_service():
    service = FeatureFlagService()
    service.set_all_flags({
        'new-payment-flow': False,
        'beta-dashboard': True
    })
    return service
```

### 7. Monitoring and Metrics

**Track Flag Evaluations**:
```python
def is_enabled(flag_name, user):
    start_time = time.time()
    result = _evaluate_flag(flag_name, user)

    # Metrics
    metrics.histogram('feature_flag.evaluation_time',
                     time.time() - start_time,
                     tags=[f'flag:{flag_name}'])

    metrics.increment('feature_flag.evaluation',
                     tags=[f'flag:{flag_name}', f'result:{result}'])

    return result
```

**Dashboard Metrics**:
- Flag evaluation latency
- Flag evaluation count per flag
- Rollout percentage over time
- Error rate per flag variant
- User distribution per variant

### 8. Security Considerations

**Sensitive Flags**:
```python
# Don't expose flag configuration to client
# Bad
response.set_cookie('feature_flags', json.dumps(all_flags))

# Good - only send evaluated results
client_flags = {
    'new_ui': feature_service.is_enabled('new_ui', user),
    'beta_access': feature_service.is_enabled('beta_access', user)
}
```

**Access Control**:
- Restrict who can modify flags
- Audit log all flag changes
- Require approvals for production flags
- Separate dev/staging/prod flag configs

---

## Advanced Patterns

### 1. Dependent Flags

```python
# Parent flag must be enabled for child flag
def is_enabled_with_dependency(flag_name, user, dependencies=[]):
    # Check all dependencies first
    for dep in dependencies:
        if not is_enabled(dep, user):
            return False

    return is_enabled(flag_name, user)

# Usage
if is_enabled_with_dependency('new-checkout-upsell', user,
                              dependencies=['new-checkout-flow']):
    show_upsell()
```

### 2. Multi-Variate Flags

```python
def get_variant(flag_name, user, variants=['control', 'variant_a', 'variant_b']):
    if not is_enabled(flag_name, user):
        return 'control'

    bucket = hash(f"{flag_name}:{user.id}") % 100
    bucket_size = 100 // len(variants)
    variant_index = bucket // bucket_size

    return variants[min(variant_index, len(variants) - 1)]

# Usage
variant = get_variant('homepage-experiment', user)
if variant == 'control':
    render_original_homepage()
elif variant == 'variant_a':
    render_homepage_a()
elif variant == 'variant_b':
    render_homepage_b()
```

### 3. Kill Switches

```python
# Emergency disable pattern
class KillSwitch:
    def __init__(self):
        self.switches = {}

    def is_killed(self, service_name):
        # Check Redis for immediate updates
        return redis.get(f"killswitch:{service_name}") == "true"

    def kill(self, service_name, reason):
        redis.set(f"killswitch:{service_name}", "true")
        log.critical(f"Kill switch activated for {service_name}: {reason}")
        alert_on_call(f"Kill switch: {service_name}")

    def revive(self, service_name):
        redis.delete(f"killswitch:{service_name}")

# Usage
if kill_switch.is_killed('recommendation-service'):
    return default_recommendations()
else:
    return ml_recommendations()
```

### 4. Flag Scheduling

```python
# Time-based flag activation
def is_enabled_with_schedule(flag_name, user):
    flag_config = get_flag_config(flag_name)

    now = datetime.now()

    # Check if within scheduled time window
    if flag_config.get('start_time') and now < flag_config['start_time']:
        return False

    if flag_config.get('end_time') and now > flag_config['end_time']:
        return False

    return is_enabled(flag_name, user)
```

---

## Facebook's Gatekeeper System

### Architecture
- Centralized configuration service
- Client libraries in all services
- Real-time updates via Thrift
- Sophisticated experimentation framework

### Key Features
```
1. Granular Control
   - Per-user flags
   - Per-request flags
   - Per-datacenter flags

2. Rollout Patterns
   - Employees first
   - 1% of users
   - 10% of users
   - Geographic rollout
   - 100% rollout

3. Integration
   - A/B testing framework
   - Metric pipelines
   - Automated analysis
   - Automated rollback
```

### Example Usage Pattern
```python
# Simplified Facebook Gatekeeper pattern
def check_gate(gate_name, user):
    # Check employee access
    if user.is_employee and gatekeeper.is_employee_enabled(gate_name):
        return True

    # Check user in specific group
    if gatekeeper.is_user_in_group(gate_name, user.id):
        return True

    # Check percentage rollout
    if gatekeeper.is_in_percentage(gate_name, user.id):
        return True

    return False
```

---

## Key Takeaways

1. **Use the Right Tool**: Choose platform based on scale, budget, and requirements
2. **Manage Flag Debt**: Actively remove old flags
3. **Consistent Bucketing**: Use stable user IDs for rollout
4. **Default to Safe**: Default values should be the safe/old behavior
5. **Monitor Everything**: Track flag performance and usage
6. **Automate Cleanup**: Set expiration dates and alerts
7. **Test Both Paths**: Test feature ON and OFF
8. **Document Flags**: Clear descriptions and owners
9. **Gradual Rollout**: Start small, increase slowly
10. **Decouple Deploy from Release**: Ship dark, release gradually

---

## Resources

- LaunchDarkly: https://launchdarkly.com/
- Unleash: https://www.getunleash.io/
- Split.io: https://www.split.io/
- Martin Fowler - Feature Toggles: https://martinfowler.com/articles/feature-toggles.html
- Feature Flags Best Practices: https://featureflags.io/
