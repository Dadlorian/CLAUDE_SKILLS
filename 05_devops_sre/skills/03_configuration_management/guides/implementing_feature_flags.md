# Implementing Feature Flags - Complete Guide

## Overview

Feature flags (also called feature toggles) decouple deployment from feature releases, enabling gradual rollouts, A/B testing, and quick rollbacks. This guide covers implementing production-ready feature flag systems.

## Table of Contents

1. [Why Feature Flags?](#why-feature-flags)
2. [Types of Feature Flags](#types-of-feature-flags)
3. [Architecture Patterns](#architecture-patterns)
4. [Implementation Strategies](#implementation-strategies)
5. [Rollout Strategies](#rollout-strategies)
6. [A/B Testing](#ab-testing)
7. [Feature Flag Providers](#feature-flag-providers)
8. [Best Practices](#best-practices)
9. [Common Pitfalls](#common-pitfalls)

## Why Feature Flags?

### Benefits

1. **Decouple Deployment from Release**: Deploy code without exposing features
2. **Gradual Rollouts**: Release features to 1%, 10%, 50%, 100% of users
3. **Quick Rollbacks**: Disable problematic features without redeploying
4. **A/B Testing**: Test different implementations with real users
5. **Trunk-Based Development**: No long-lived feature branches
6. **Reduce Risk**: Test in production with controlled exposure

### Use Cases

- **New Feature Rollout**: Gradually enable new checkout flow
- **Kill Switch**: Disable expensive feature during traffic spike
- **A/B Test**: Compare two algorithm implementations
- **Canary Release**: Enable for internal users first
- **Operational Toggle**: Disable non-critical features during incident
- **Permission Toggle**: Premium features for paying users

## Types of Feature Flags

### 1. Release Toggles

Temporary flags for in-progress features:

```python
if feature_flags.is_enabled("new-checkout-flow"):
    return new_checkout_handler(request)
else:
    return legacy_checkout_handler(request)
```

**Lifecycle**: Weeks to months, should be removed after full rollout

### 2. Experiment Toggles

For A/B testing and experiments:

```python
variant = feature_flags.get_variant("search-algorithm", user)
if variant == "ml-ranking":
    results = ml_search(query)
elif variant == "relevance-ranking":
    results = relevance_search(query)
else:  # control
    results = legacy_search(query)
```

**Lifecycle**: Duration of experiment, removed after decision

### 3. Ops Toggles

Control operational aspects of system:

```python
if feature_flags.is_enabled("enable-caching"):
    result = cache.get_or_compute(key, expensive_function)
else:
    result = expensive_function()
```

**Lifecycle**: Long-lived, may be permanent

### 4. Permission Toggles

Control access based on user attributes:

```python
if feature_flags.is_enabled("premium-features", user):
    if user.plan == "premium":
        return premium_feature_handler(request)

return standard_feature_handler(request)
```

**Lifecycle**: Permanent

## Architecture Patterns

### Client-Side Evaluation

Flag rules evaluated in application:

```
┌─────────────┐
│ Application │
│   ┌─────┐   │
│   │ SDK │◄──┼────── Configuration from Server/Cache
│   └─────┘   │
│      ▼      │
│  Evaluate   │
│   Locally   │
└─────────────┘
```

**Pros**: Fast, no network latency
**Cons**: Configuration must be synced, rules visible in client

### Server-Side Evaluation

Flag evaluation happens on backend:

```
┌─────────────┐         ┌────────────────┐
│ Application ├────────►│ Feature Flag   │
│             │◄────────┤ Service        │
└─────────────┘         └────────────────┘
```

**Pros**: Centralized, secure, immediate updates
**Cons**: Network latency, additional service dependency

### Hybrid Approach

Combine both patterns:

```python
class FeatureFlagClient:
    def __init__(self):
        self.cache = {}
        self.fallback = {}

    def is_enabled(self, flag, user):
        # Try local cache first
        if flag in self.cache:
            return self.evaluate_local(flag, user)

        # Fallback to remote API
        try:
            return self.evaluate_remote(flag, user)
        except Exception:
            # Use fallback if service unavailable
            return self.fallback.get(flag, False)
```

## Implementation Strategies

### Basic Implementation

Simple boolean flag:

```python
# settings.py
FEATURE_FLAGS = {
    'new-dashboard': True,
    'beta-search': False,
    'premium-features': True
}

# views.py
if settings.FEATURE_FLAGS.get('new-dashboard'):
    return render(request, 'dashboard/new.html')
else:
    return render(request, 'dashboard/old.html')
```

### Database-Backed Flags

Store flags in database for runtime changes:

```python
# models.py
class FeatureFlag(models.Model):
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# service.py
class FeatureFlagService:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60  # seconds

    def is_enabled(self, flag_key):
        # Check cache
        if flag_key in self.cache:
            if time.time() - self.cache[flag_key]['timestamp'] < self.cache_ttl:
                return self.cache[flag_key]['value']

        # Query database
        try:
            flag = FeatureFlag.objects.get(key=flag_key)
            self.cache[flag_key] = {
                'value': flag.enabled,
                'timestamp': time.time()
            }
            return flag.enabled
        except FeatureFlag.DoesNotExist:
            return False
```

### Redis-Backed Flags

Use Redis for distributed caching:

```python
import redis
import json

class FeatureFlagClient:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)

    def is_enabled(self, flag_key, user_id):
        # Get flag configuration
        flag_data = self.redis.get(f"flag:{flag_key}")
        if not flag_data:
            return False

        flag = json.loads(flag_data)

        # Evaluate based on strategy
        if flag['strategy'] == 'all':
            return flag['enabled']

        elif flag['strategy'] == 'percentage':
            user_hash = self._hash_user(user_id, flag_key)
            return flag['enabled'] and (user_hash % 100 < flag['percentage'])

        elif flag['strategy'] == 'whitelist':
            return flag['enabled'] and user_id in flag['users']

        return False

    def set_flag(self, flag_key, config):
        self.redis.set(f"flag:{flag_key}", json.dumps(config))

    def _hash_user(self, user_id, flag_key):
        import hashlib
        hash_input = f"{user_id}:{flag_key}"
        return int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
```

## Rollout Strategies

### 1. Percentage Rollout

Enable for X% of users:

```python
def percentage_rollout(user_id, flag_key, percentage):
    """
    Enable flag for percentage of users using consistent hashing
    """
    user_hash = hash(f"{user_id}:{flag_key}") % 100
    return user_hash < percentage

# Usage
if percentage_rollout(user.id, "new-feature", 25):  # 25% of users
    return new_feature()
else:
    return old_feature()
```

### 2. User Whitelist

Enable for specific users:

```python
BETA_USERS = [
    'user@example.com',
    'admin@example.com'
]

if user.email in BETA_USERS:
    return beta_feature()
else:
    return stable_feature()
```

### 3. Gradual Rollout

Increase percentage over time:

```python
from datetime import datetime, timedelta

def gradual_rollout(user_id, flag_key, start_date, end_date, start_pct, end_pct):
    """
    Gradually increase rollout percentage from start_pct to end_pct
    """
    now = datetime.now()

    if now < start_date:
        percentage = start_pct
    elif now > end_date:
        percentage = end_pct
    else:
        # Linear interpolation
        total_duration = (end_date - start_date).total_seconds()
        elapsed = (now - start_date).total_seconds()
        progress = elapsed / total_duration
        percentage = start_pct + (end_pct - start_pct) * progress

    user_hash = hash(f"{user_id}:{flag_key}") % 100
    return user_hash < percentage

# Rollout from 0% to 100% over 7 days
start = datetime.now()
end = start + timedelta(days=7)
if gradual_rollout(user.id, "new-ui", start, end, 0, 100):
    return new_ui()
```

### 4. Ring Deployment

Enable progressively: Internal → Beta → Production

```python
class RolloutStage:
    INTERNAL = 'internal'
    BETA = 'beta'
    PRODUCTION = 'production'

def ring_deployment(user, flag_key, current_stage):
    if current_stage == RolloutStage.INTERNAL:
        return user.is_internal_user

    elif current_stage == RolloutStage.BETA:
        return user.is_internal_user or user.is_beta_user

    elif current_stage == RolloutStage.PRODUCTION:
        return True

    return False

# Usage
stage = get_flag_stage("new-feature")
if ring_deployment(user, "new-feature", stage):
    return new_feature()
```

### 5. Attribute-Based Targeting

Enable based on user attributes:

```python
def attribute_targeting(user, rules):
    """
    Enable flag based on user attributes
    rules = [
        {'attribute': 'country', 'operator': 'in', 'value': ['US', 'CA']},
        {'attribute': 'plan', 'operator': 'equals', 'value': 'premium'},
        {'attribute': 'signup_date', 'operator': 'after', 'value': '2024-01-01'}
    ]
    """
    for rule in rules:
        attr_value = getattr(user, rule['attribute'], None)

        if rule['operator'] == 'equals':
            if attr_value == rule['value']:
                return True

        elif rule['operator'] == 'in':
            if attr_value in rule['value']:
                return True

        elif rule['operator'] == 'greater_than':
            if attr_value > rule['value']:
                return True

        # Add more operators as needed

    return False

# Usage
rules = [
    {'attribute': 'country', 'operator': 'in', 'value': ['US']},
    {'attribute': 'plan', 'operator': 'equals', 'value': 'premium'}
]

if attribute_targeting(user, rules):
    return premium_feature()
```

## A/B Testing

### Multi-Variant Testing

```python
class ABTestClient:
    def get_variant(self, user_id, test_key, variants):
        """
        Assign user to variant using consistent hashing

        variants = {
            'control': {'weight': 50},
            'variant-a': {'weight': 25},
            'variant-b': {'weight': 25}
        }
        """
        user_hash = hash(f"{user_id}:{test_key}") % 100
        total_weight = sum(v['weight'] for v in variants.values())

        threshold = user_hash / 100 * total_weight
        cumulative = 0

        for variant_name, config in variants.items():
            cumulative += config['weight']
            if threshold < cumulative:
                # Track assignment
                self.track_event('variant_assigned', {
                    'test': test_key,
                    'user_id': user_id,
                    'variant': variant_name
                })
                return variant_name

        return 'control'

# Usage
ab_test = ABTestClient()

variants = {
    'control': {'weight': 50},      # 50%
    'blue-button': {'weight': 25},  # 25%
    'green-button': {'weight': 25}  # 25%
}

variant = ab_test.get_variant(user.id, "button-color-test", variants)

if variant == 'blue-button':
    button_color = 'blue'
elif variant == 'green-button':
    button_color = 'green'
else:  # control
    button_color = 'red'

# Track conversion
if user_clicked_button:
    ab_test.track_event('button_clicked', {
        'test': 'button-color-test',
        'variant': variant
    })
```

### Statistical Significance

```python
from scipy import stats

def calculate_significance(control_conversions, control_total,
                          treatment_conversions, treatment_total):
    """
    Calculate if A/B test result is statistically significant
    """
    control_rate = control_conversions / control_total
    treatment_rate = treatment_conversions / treatment_total

    # Chi-square test
    observed = [
        [control_conversions, control_total - control_conversions],
        [treatment_conversions, treatment_total - treatment_conversions]
    ]
    chi2, p_value = stats.chi2_contingency(observed)[:2]

    # Significant if p < 0.05
    is_significant = p_value < 0.05

    return {
        'control_rate': control_rate,
        'treatment_rate': treatment_rate,
        'lift': (treatment_rate - control_rate) / control_rate * 100,
        'p_value': p_value,
        'is_significant': is_significant
    }

# Example
result = calculate_significance(
    control_conversions=450,
    control_total=10000,
    treatment_conversions=520,
    treatment_total=10000
)

print(f"Control: {result['control_rate']:.2%}")
print(f"Treatment: {result['treatment_rate']:.2%}")
print(f"Lift: {result['lift']:.2f}%")
print(f"Significant: {result['is_significant']}")
```

## Feature Flag Providers

### LaunchDarkly

```python
import ldclient
from ldclient.config import Config

# Initialize
ldclient.set_config(Config("your-sdk-key"))
client = ldclient.get()

# User context
user = {
    "key": "user123",
    "email": "user@example.com",
    "custom": {
        "plan": "premium",
        "country": "US"
    }
}

# Boolean flag
if client.variation("new-feature", user, False):
    return new_feature()

# Multi-variant flag
variant = client.variation("algorithm-test", user, "control")
if variant == "ml-algorithm":
    return ml_algorithm()

# Track custom events
client.track("purchase_completed", user, None, 99.99)
```

### Unleash

```python
from UnleashClient import UnleashClient

client = UnleashClient(
    url="https://unleash.example.com/api",
    app_name="myapp",
    custom_headers={'Authorization': 'token'}
)

client.initialize_client()

# Check feature
if client.is_enabled("new-feature", {"userId": "user123"}):
    return new_feature()

# With variant
variant = client.get_variant("button-test", {"userId": "user123"})
button_color = variant.get("payload", {}).get("color", "blue")
```

### Split.io

```javascript
const SplitFactory = require('@splitsoftware/splitio').SplitFactory;

const factory = SplitFactory({
  core: {
    authorizationKey: 'your-api-key'
  }
});

const client = factory.client();

client.on(client.Event.SDK_READY, () => {
  const treatment = client.getTreatment('user123', 'new-feature');

  if (treatment === 'on') {
    // New feature
  } else {
    // Control
  }
});
```

### Custom Solution

```python
class FeatureFlagManager:
    def __init__(self, storage_backend):
        self.storage = storage_backend
        self.evaluators = {
            'percentage': self._evaluate_percentage,
            'whitelist': self._evaluate_whitelist,
            'attribute': self._evaluate_attribute
        }

    def is_enabled(self, flag_key, context):
        flag = self.storage.get_flag(flag_key)

        if not flag or not flag['enabled']:
            return False

        strategy = flag.get('strategy', 'all')
        evaluator = self.evaluators.get(strategy, lambda f, c: True)

        result = evaluator(flag, context)

        # Track evaluation
        self.storage.track_evaluation(flag_key, context, result)

        return result

    def _evaluate_percentage(self, flag, context):
        percentage = flag.get('percentage', 0)
        user_hash = hash(f"{context['user_id']}:{flag['key']}") % 100
        return user_hash < percentage

    def _evaluate_whitelist(self, flag, context):
        allowed_users = flag.get('users', [])
        return context['user_id'] in allowed_users

    def _evaluate_attribute(self, flag, context):
        rules = flag.get('rules', [])
        for rule in rules:
            if self._match_rule(rule, context):
                return True
        return False

    def _match_rule(self, rule, context):
        # Implement rule matching logic
        pass
```

## Best Practices

### 1. Short-Lived Flags

Remove feature flags after rollout:

```python
# Set expiration date when creating flag
flag = {
    'key': 'new-checkout',
    'enabled': True,
    'created_at': '2024-01-15',
    'expires_at': '2024-03-15',  # 2 months
    'status': 'temporary'
}

# Regular cleanup
def cleanup_expired_flags():
    expired = FeatureFlag.objects.filter(
        expires_at__lt=datetime.now(),
        status='temporary'
    )
    for flag in expired:
        print(f"Flag {flag.key} has expired - consider removing")
```

### 2. Default to Safe Fallback

```python
def is_enabled(flag_key, default=False):
    try:
        return feature_service.check(flag_key)
    except Exception as e:
        logger.error(f"Feature flag error: {e}")
        return default  # Safe default

# Usage - default to stable behavior
if is_enabled('experimental-feature', default=False):
    return experimental_code()
else:
    return stable_code()
```

### 3. Monitor Flag Usage

```python
def track_flag_evaluation(flag_key, user_id, enabled):
    metrics.increment(f'feature_flag.{flag_key}.evaluations')
    metrics.increment(f'feature_flag.{flag_key}.{"enabled" if enabled else "disabled"}')

    # Alert on unexpected behavior
    if flag_key in CRITICAL_FLAGS and not enabled:
        alert(f"Critical flag {flag_key} disabled for user {user_id}")
```

### 4. Document Flags

```python
# Use clear naming and documentation
flags = {
    'checkout_v2': {
        'name': 'Checkout V2',
        'description': 'New streamlined checkout flow with one-click payment',
        'owner': 'payments-team',
        'jira': 'PROJ-1234',
        'created': '2024-01-15',
        'expires': '2024-03-15',
        'rollout_plan': 'Start at 1%, increase 10% daily',
        'rollback_plan': 'Disable flag, log to Slack #payments-alerts'
    }
}
```

### 5. Test Both Paths

```python
# Unit tests for both flag states
def test_new_checkout_enabled():
    with feature_flag_override('new-checkout', True):
        response = checkout_handler(request)
        assert response.template == 'checkout/v2.html'

def test_new_checkout_disabled():
    with feature_flag_override('new-checkout', False):
        response = checkout_handler(request)
        assert response.template == 'checkout/v1.html'
```

## Common Pitfalls

### 1. Flag Sprawl

**Problem**: Too many flags, hard to manage

**Solution**:
- Regular cleanup of old flags
- Clear expiration dates
- Automated alerts for stale flags

### 2. Complex Flag Logic

**Problem**: Nested flags, hard to reason about

```python
# Bad - nested flags
if feature_flags.is_enabled('feature-a'):
    if feature_flags.is_enabled('feature-b'):
        if feature_flags.is_enabled('feature-c'):
            return complex_feature()
```

**Solution**: Simplify or combine flags

```python
# Good - single flag for feature combination
if feature_flags.is_enabled('abc-combined-feature'):
    return complex_feature()
```

### 3. Technical Debt

**Problem**: Flags left in code forever

**Solution**:
- Set expiration dates
- Regular flag audits
- Automated detection of unused flags

### 4. Inconsistent Evaluation

**Problem**: User sees different experiences on reload

**Solution**: Use consistent hashing

```python
def consistent_hash(user_id, flag_key):
    """Always returns same hash for user+flag combination"""
    import hashlib
    hash_input = f"{user_id}:{flag_key}"
    return int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
```

### 5. Performance Impact

**Problem**: Flag evaluation slows down requests

**Solution**:
- Cache flag configurations
- Async flag updates
- Fail fast with defaults

## Next Steps

1. **Choose Provider**: LaunchDarkly, Unleash, or custom
2. **Start Simple**: Boolean flags first
3. **Add Targeting**: Percentage and user-based rollouts
4. **Implement A/B Testing**: Multi-variant experiments
5. **Monitor and Clean**: Regular flag audits

## Resources

- [LaunchDarkly Documentation](https://docs.launchdarkly.com/)
- [Unleash Documentation](https://docs.getunleash.io/)
- [Feature Toggles (Martin Fowler)](https://martinfowler.com/articles/feature-toggles.html)
- [Trunk Based Development](https://trunkbaseddevelopment.com/)

---

**Last Updated**: 2025-11-19
**Version**: 1.0
