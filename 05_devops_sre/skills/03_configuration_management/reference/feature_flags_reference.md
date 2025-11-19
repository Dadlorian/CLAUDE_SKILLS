# Feature Flags Reference

## Overview
Comprehensive reference for feature flag systems, covering LaunchDarkly, Unleash, and custom implementations for safe deployments and experimentation.

## Table of Contents
- [Core Concepts](#core-concepts)
- [LaunchDarkly](#launchdarkly)
- [Unleash](#unleash)
- [Custom Implementation](#custom-implementation)
- [Best Practices](#best-practices)
- [Advanced Patterns](#advanced-patterns)
- [Testing Strategies](#testing-strategies)
- [Migration Patterns](#migration-patterns)

---

## Core Concepts

### What Are Feature Flags?
Feature flags (toggles) allow you to enable/disable features without deploying code, enabling:
- **Gradual Rollouts**: Release to percentage of users
- **A/B Testing**: Compare feature variants
- **Kill Switches**: Instantly disable problematic features
- **Trunk-Based Development**: Merge incomplete code safely
- **Ops Toggles**: Control operational aspects (logging, caching)

### Flag Types
```
1. Release Flags (temporary)
   - Enable incomplete features
   - Should be removed after full rollout

2. Experiment Flags (temporary)
   - A/B testing, multivariate testing
   - Remove after experiment concludes

3. Ops Flags (permanent)
   - Circuit breakers
   - Performance tuning
   - Feature degradation

4. Permission Flags (permanent)
   - Role-based features
   - Premium features
   - Regional restrictions
```

### Architecture
```
┌─────────────────────────────────────┐
│         Application                 │
│  ┌─────────────────────────────┐   │
│  │  Feature Flag SDK           │   │
│  │  - Evaluation               │   │
│  │  - Local Cache              │   │
│  │  - Analytics               │   │
│  └──────────┬──────────────────┘   │
└─────────────┼──────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    Feature Flag Service             │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ Flag Config  │  │  Targeting  │ │
│  └──────────────┘  └─────────────┘ │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  Analytics   │  │  Audit Log  │ │
│  └──────────────┘  └─────────────┘ │
└─────────────────────────────────────┘
```

---

## LaunchDarkly

### SDK Setup

#### JavaScript/Node.js
```javascript
// server.js
const LaunchDarkly = require('@launchdarkly/node-server-sdk');

const client = LaunchDarkly.init(process.env.LAUNCHDARKLY_SDK_KEY);

// Wait for initialization
client.waitForInitialization().then(() => {
  console.log('LaunchDarkly initialized');
});

// Create user context
const user = {
  key: 'user-123',
  email: 'user@example.com',
  name: 'John Doe',
  custom: {
    groups: ['beta-users'],
    plan: 'premium',
    country: 'US'
  }
};

// Evaluate flag
const showNewFeature = await client.variation(
  'new-feature',
  user,
  false  // default value
);

if (showNewFeature) {
  // Show new feature
} else {
  // Show old feature
}

// JSON flag (for complex configurations)
const config = await client.variation(
  'app-config',
  user,
  { timeout: 30, retries: 3 }
);

// Track custom events
client.track('purchase', user, { amount: 99.99 });

// Flush events and close
await client.flush();
await client.close();
```

#### Python
```python
# app.py
import ldclient
from ldclient.config import Config

ldclient.set_config(Config(os.environ['LAUNCHDARKLY_SDK_KEY']))
client = ldclient.get()

# User context
user = {
    'key': 'user-123',
    'email': 'user@example.com',
    'custom': {
        'groups': ['beta-users'],
        'plan': 'premium'
    }
}

# Evaluate flag
show_new_feature = client.variation('new-feature', user, False)

if show_new_feature:
    # New feature logic
    pass
else:
    # Old feature logic
    pass

# Multi-variant flag
variant = client.variation('button-color', user, 'blue')

# JSON flag
config = client.variation('feature-config', user, {
    'timeout': 30,
    'max_retries': 3
})

# Close client
client.close()
```

#### Go
```go
// main.go
package main

import (
    "context"
    "time"
    ld "github.com/launchdarkly/go-server-sdk/v6"
    "github.com/launchdarkly/go-server-sdk/v6/ldcontext"
)

func main() {
    client, _ := ld.MakeClient(os.Getenv("LAUNCHDARKLY_SDK_KEY"), 5*time.Second)
    defer client.Close()

    // Create context
    context := ldcontext.NewBuilder("user-123").
        Name("John Doe").
        SetString("email", "user@example.com").
        SetString("plan", "premium").
        Build()

    // Boolean flag
    showFeature, _ := client.BoolVariation("new-feature", context, false)

    if showFeature {
        // New feature
    }

    // String flag
    variant, _ := client.StringVariation("button-color", context, "blue")

    // JSON flag
    config, _ := client.JSONVariation("app-config", context, ldvalue.Null())

    // Track event
    client.TrackEvent("purchase", context)
    client.TrackMetric("purchase", context, ldvalue.Float64(99.99))
}
```

### Targeting Rules
```json
{
  "name": "new-checkout-flow",
  "key": "new-checkout-flow",
  "variations": [
    {
      "value": false,
      "name": "Off"
    },
    {
      "value": true,
      "name": "On"
    }
  ],
  "targeting": {
    "rules": [
      {
        "clauses": [
          {
            "attribute": "email",
            "op": "endsWith",
            "values": ["@company.com"]
          }
        ],
        "variation": 1
      },
      {
        "clauses": [
          {
            "attribute": "groups",
            "op": "in",
            "values": ["beta-testers"]
          }
        ],
        "variation": 1
      },
      {
        "clauses": [
          {
            "attribute": "country",
            "op": "in",
            "values": ["US", "CA"]
          }
        ],
        "rollout": {
          "variations": [
            {"variation": 0, "weight": 90000},
            {"variation": 1, "weight": 10000}
          ]
        }
      }
    ],
    "fallthrough": {
      "variation": 0
    }
  }
}
```

### Percentage Rollouts
```javascript
// Progressive rollout strategy
// Day 1: 5%
// Day 2: 10%
// Day 3: 25%
// Day 4: 50%
// Day 5: 100%

const rolloutSchedule = {
  'new-feature': {
    rules: [
      {
        rollout: {
          variations: [
            { variation: 0, weight: 95000 }, // 95% off
            { variation: 1, weight: 5000 }   // 5% on
          ]
        }
      }
    ]
  }
};

// Targeting specific user segments
const segmentedRollout = {
  rules: [
    {
      // Premium users get 100%
      clauses: [{ attribute: 'plan', op: 'in', values: ['premium'] }],
      variation: 1
    },
    {
      // Free users get 10%
      clauses: [{ attribute: 'plan', op: 'in', values: ['free'] }],
      rollout: {
        variations: [
          { variation: 0, weight: 90000 },
          { variation: 1, weight: 10000 }
        ]
      }
    }
  ]
};
```

### Environments
```javascript
// Separate SDK keys per environment
const sdkKeys = {
  development: 'sdk-dev-key',
  staging: 'sdk-staging-key',
  production: 'sdk-prod-key'
};

const client = LaunchDarkly.init(sdkKeys[process.env.NODE_ENV]);

// Environment-specific defaults
const defaults = {
  development: {
    'debug-mode': true,
    'cache-enabled': false
  },
  production: {
    'debug-mode': false,
    'cache-enabled': true
  }
};
```

---

## Unleash

### Setup and Configuration
```javascript
// Node.js setup
const { initialize } = require('unleash-client');

const unleash = initialize({
  url: 'https://unleash.example.com/api/',
  appName: 'my-application',
  instanceId: 'instance-1',
  customHeaders: {
    Authorization: process.env.UNLEASH_API_TOKEN
  },
  strategies: {
    // Custom strategy
    customStrategy: (parameters, context) => {
      return context.userId % 10 < parameters.percentage;
    }
  }
});

unleash.on('ready', () => {
  console.log('Unleash ready');
});

unleash.on('error', (err) => {
  console.error('Unleash error:', err);
});

// Check feature
const context = {
  userId: '123',
  sessionId: 'abc',
  remoteAddress: '127.0.0.1',
  properties: {
    userPlan: 'premium',
    region: 'us-east'
  }
};

const isEnabled = unleash.isEnabled('new-feature', context);

// Get variant
const variant = unleash.getVariant('feature-variant', context);
if (variant.enabled) {
  console.log('Variant:', variant.name);
  console.log('Payload:', variant.payload);
}
```

### Strategies

#### 1. Standard Strategy
```javascript
// Default - always on/off
{
  "name": "default",
  "parameters": {}
}
```

#### 2. UserID Strategy
```javascript
// Specific users
{
  "name": "userWithId",
  "parameters": {
    "userIds": "user-1,user-2,user-3"
  }
}
```

#### 3. Gradual Rollout
```javascript
{
  "name": "flexibleRollout",
  "parameters": {
    "rollout": "50",      // 50% rollout
    "stickiness": "userId", // Consistent per user
    "groupId": "feature-a"
  }
}
```

#### 4. Custom Strategy
```javascript
// Register custom strategy
unleash.defineStrategy('premium-users', (parameters, context) => {
  return context.properties.userPlan === 'premium' &&
         context.properties.region === parameters.region;
});

// Use in toggle
{
  "name": "premium-feature",
  "strategies": [
    {
      "name": "premium-users",
      "parameters": {
        "region": "us-east"
      }
    }
  ]
}
```

### Variants
```javascript
// Configure variants
const variantConfig = {
  name: 'button-color',
  enabled: true,
  variants: [
    {
      name: 'blue',
      weight: 334,
      payload: { type: 'string', value: '#0000FF' }
    },
    {
      name: 'green',
      weight: 333,
      payload: { type: 'string', value: '#00FF00' }
    },
    {
      name: 'red',
      weight: 333,
      payload: { type: 'string', value: '#FF0000' }
    }
  ]
};

// Use variant
const variant = unleash.getVariant('button-color', context);
if (variant.enabled) {
  const color = variant.payload.value;
  // Apply color
}
```

### Feature Toggle Types
```javascript
// Release toggle
{
  "name": "new-checkout",
  "type": "release",
  "description": "New checkout flow - remove after 2024-Q1",
  "enabled": true
}

// Experiment toggle
{
  "name": "pricing-test",
  "type": "experiment",
  "description": "A/B test pricing page layouts",
  "enabled": true,
  "variants": [...]
}

// Operational toggle
{
  "name": "cache-enabled",
  "type": "operational",
  "description": "Enable Redis caching",
  "enabled": true
}

// Permission toggle
{
  "name": "admin-panel",
  "type": "permission",
  "description": "Admin panel access",
  "enabled": true
}
```

### API Integration
```bash
# Create feature toggle
curl -X POST https://unleash.example.com/api/admin/projects/default/features \
  -H "Authorization: ${UNLEASH_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new-feature",
    "type": "release",
    "description": "New feature description",
    "impressionData": true
  }'

# Add strategy
curl -X POST https://unleash.example.com/api/admin/projects/default/features/new-feature/environments/production/strategies \
  -H "Authorization: ${UNLEASH_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "flexibleRollout",
    "parameters": {
      "rollout": "25",
      "stickiness": "userId"
    }
  }'

# Get feature
curl https://unleash.example.com/api/admin/projects/default/features/new-feature \
  -H "Authorization: ${UNLEASH_API_TOKEN}"

# Archive feature
curl -X DELETE https://unleash.example.com/api/admin/projects/default/features/new-feature \
  -H "Authorization: ${UNLEASH_API_TOKEN}"
```

---

## Custom Implementation

### Simple Feature Flag Service
```python
# feature_flags.py
import redis
import json
from typing import Dict, Any

class FeatureFlags:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache = {}
        self.cache_ttl = 60  # seconds

    def is_enabled(self, flag_name: str, context: Dict[str, Any]) -> bool:
        """Check if feature is enabled for given context."""
        flag = self._get_flag(flag_name)
        if not flag:
            return False

        if not flag.get('enabled', False):
            return False

        # Check targeting rules
        for rule in flag.get('rules', []):
            if self._evaluate_rule(rule, context):
                return rule.get('enabled', True)

        # Check percentage rollout
        if 'rollout' in flag:
            return self._check_rollout(flag['rollout'], context)

        return flag.get('default', False)

    def _get_flag(self, flag_name: str) -> Dict:
        """Get flag configuration from Redis."""
        cache_key = f"flag:{flag_name}"

        # Check local cache
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Get from Redis
        data = self.redis.get(cache_key)
        if data:
            flag = json.loads(data)
            self.cache[cache_key] = flag
            return flag

        return None

    def _evaluate_rule(self, rule: Dict, context: Dict) -> bool:
        """Evaluate targeting rule."""
        conditions = rule.get('conditions', [])

        for condition in conditions:
            attribute = condition['attribute']
            operator = condition['operator']
            value = condition['value']

            context_value = context.get(attribute)

            if operator == 'equals':
                if context_value != value:
                    return False
            elif operator == 'in':
                if context_value not in value:
                    return False
            elif operator == 'contains':
                if value not in context_value:
                    return False
            elif operator == 'matches':
                import re
                if not re.match(value, str(context_value)):
                    return False

        return True

    def _check_rollout(self, rollout: Dict, context: Dict) -> bool:
        """Check percentage rollout."""
        percentage = rollout.get('percentage', 0)
        key = rollout.get('key', 'user_id')

        if key not in context:
            return False

        # Consistent hashing for sticky rollouts
        import hashlib
        hash_value = int(hashlib.md5(
            str(context[key]).encode()
        ).hexdigest(), 16)

        return (hash_value % 100) < percentage

    def get_variant(self, flag_name: str, context: Dict) -> str:
        """Get variant for multivariate flag."""
        flag = self._get_flag(flag_name)
        if not flag or not self.is_enabled(flag_name, context):
            return 'control'

        variants = flag.get('variants', [])
        if not variants:
            return 'control'

        # Weighted random selection with sticky assignment
        import hashlib
        key = context.get('user_id', '')
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)

        total_weight = sum(v['weight'] for v in variants)
        position = hash_value % total_weight

        current = 0
        for variant in variants:
            current += variant['weight']
            if position < current:
                return variant['name']

        return 'control'


# Usage
redis_client = redis.Redis(host='localhost', port=6379)
ff = FeatureFlags(redis_client)

context = {
    'user_id': '12345',
    'email': 'user@example.com',
    'plan': 'premium',
    'country': 'US'
}

if ff.is_enabled('new-checkout', context):
    # Use new checkout
    variant = ff.get_variant('checkout-layout', context)
    # Apply variant
```

### Flag Configuration Storage
```python
# store_flags.py
import redis
import json

def create_flag(redis_client, flag_config):
    """Store flag configuration in Redis."""
    flag_name = flag_config['name']
    redis_client.set(
        f"flag:{flag_name}",
        json.dumps(flag_config)
    )
    redis_client.publish('flag-updates', flag_name)

# Example flag configurations
new_checkout_flag = {
    'name': 'new-checkout',
    'enabled': True,
    'rules': [
        {
            'conditions': [
                {'attribute': 'email', 'operator': 'contains', 'value': '@company.com'}
            ],
            'enabled': True
        },
        {
            'conditions': [
                {'attribute': 'plan', 'operator': 'equals', 'value': 'premium'}
            ],
            'enabled': True
        }
    ],
    'rollout': {
        'percentage': 25,
        'key': 'user_id'
    },
    'default': False
}

variant_flag = {
    'name': 'button-color',
    'enabled': True,
    'variants': [
        {'name': 'blue', 'weight': 33},
        {'name': 'green', 'weight': 33},
        {'name': 'red', 'weight': 34}
    ],
    'default': False
}

redis_client = redis.Redis(host='localhost', port=6379)
create_flag(redis_client, new_checkout_flag)
create_flag(redis_client, variant_flag)
```

### Admin API
```python
# api.py
from flask import Flask, request, jsonify
import redis
import json

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379)

@app.route('/api/flags', methods=['GET'])
def list_flags():
    """List all feature flags."""
    keys = redis_client.keys('flag:*')
    flags = []
    for key in keys:
        data = redis_client.get(key)
        if data:
            flags.append(json.loads(data))
    return jsonify(flags)

@app.route('/api/flags/<flag_name>', methods=['GET'])
def get_flag(flag_name):
    """Get specific flag."""
    data = redis_client.get(f'flag:{flag_name}')
    if data:
        return jsonify(json.loads(data))
    return jsonify({'error': 'Flag not found'}), 404

@app.route('/api/flags', methods=['POST'])
def create_flag():
    """Create new flag."""
    flag_config = request.json
    flag_name = flag_config['name']

    redis_client.set(
        f'flag:{flag_name}',
        json.dumps(flag_config)
    )
    redis_client.publish('flag-updates', flag_name)

    return jsonify(flag_config), 201

@app.route('/api/flags/<flag_name>', methods=['PUT'])
def update_flag(flag_name):
    """Update existing flag."""
    flag_config = request.json
    flag_config['name'] = flag_name

    redis_client.set(
        f'flag:{flag_name}',
        json.dumps(flag_config)
    )
    redis_client.publish('flag-updates', flag_name)

    return jsonify(flag_config)

@app.route('/api/flags/<flag_name>', methods=['DELETE'])
def delete_flag(flag_name):
    """Delete flag."""
    redis_client.delete(f'flag:{flag_name}')
    redis_client.publish('flag-updates', f'deleted:{flag_name}')

    return '', 204

@app.route('/api/flags/<flag_name>/evaluate', methods=['POST'])
def evaluate_flag(flag_name):
    """Evaluate flag for given context."""
    context = request.json
    ff = FeatureFlags(redis_client)

    result = {
        'enabled': ff.is_enabled(flag_name, context),
        'variant': ff.get_variant(flag_name, context)
    }

    return jsonify(result)
```

---

## Best Practices

### 1. Naming Conventions
```javascript
// Good naming
const flags = {
  // Feature: what it does
  'checkout-express-shipping': true,
  'search-ai-suggestions': true,

  // Experiment: hypothesis being tested
  'exp-pricing-page-layout': 'variant-a',
  'exp-onboarding-flow': 'control',

  // Ops: operational aspect
  'ops-cache-redis-enabled': true,
  'ops-logging-debug-level': false,

  // Permission: who can access
  'perm-admin-panel': true,
  'perm-beta-features': false
};

// Bad naming
const badFlags = {
  'flag1': true,  // Not descriptive
  'new': true,    // Too vague
  'test': false   // Not specific
};
```

### 2. Flag Lifecycle Management
```javascript
// Track flag creation and expiration
const flagMetadata = {
  'new-checkout': {
    createdAt: '2024-01-01',
    createdBy: 'john@company.com',
    type: 'release',
    expiresAt: '2024-04-01',  // Remove after Q1
    jiraTicket: 'PROJ-123',
    status: 'active'
  }
};

// Automated cleanup
async function cleanupExpiredFlags() {
  const now = new Date();
  const flags = await getAllFlags();

  for (const flag of flags) {
    if (flag.expiresAt && new Date(flag.expiresAt) < now) {
      // Check if flag is at 100% rollout
      if (flag.rollout === 100 && flag.status === 'complete') {
        await archiveFlag(flag.name);
        await notifyTeam(`Flag ${flag.name} archived`);
      }
    }
  }
}
```

### 3. Testing with Flags
```javascript
// Override flags in tests
describe('Checkout', () => {
  beforeEach(() => {
    featureFlags.override({
      'new-checkout': true,
      'express-shipping': false
    });
  });

  afterEach(() => {
    featureFlags.clearOverrides();
  });

  it('shows new checkout flow', () => {
    const page = renderCheckout();
    expect(page).toHaveText('New Checkout');
  });
});

// Test both flag states
describe.each([
  ['enabled', true],
  ['disabled', false]
])('Feature when %s', (_, flagValue) => {
  it('renders correctly', () => {
    featureFlags.set('new-feature', flagValue);
    // Test both states
  });
});
```

### 4. Monitoring and Alerting
```javascript
// Track flag evaluations
function trackFlagEvaluation(flagName, enabled, context) {
  metrics.increment('feature_flag.evaluation', {
    flag: flagName,
    enabled: enabled,
    environment: process.env.NODE_ENV
  });

  // Alert on unexpected states
  if (flagName === 'critical-feature' && !enabled) {
    alerting.send({
      severity: 'warning',
      message: `Critical feature flag ${flagName} is disabled`,
      context: context
    });
  }
}

// Monitor rollout progress
function monitorRollout(flagName) {
  const stats = {
    total: 0,
    enabled: 0,
    disabled: 0,
    errors: 0
  };

  // Track over time
  setInterval(() => {
    const percentage = (stats.enabled / stats.total) * 100;
    metrics.gauge('feature_flag.rollout_percentage', percentage, {
      flag: flagName
    });
  }, 60000);
}
```

### 5. Documentation
```javascript
/**
 * Feature: New Checkout Flow
 *
 * @flag new-checkout-flow
 * @type release
 * @created 2024-01-15
 * @author john@company.com
 * @jira CHECKOUT-456
 *
 * @description
 * Simplified checkout with one-page design and auto-fill
 *
 * @rollout-plan
 * - Week 1: Internal testing (5%)
 * - Week 2: Beta users (25%)
 * - Week 3: All users (100%)
 *
 * @removal-criteria
 * - 100% rollout for 2 weeks
 * - Error rate < 0.1%
 * - Conversion rate >= baseline
 *
 * @dependencies
 * - Payment service v2.0
 * - Address validation API
 */
const useNewCheckout = featureFlags.isEnabled('new-checkout-flow', user);
```

---

## Advanced Patterns

### 1. Gradual Rollout with Metrics
```javascript
class SmartRollout {
  constructor(flagName, targetMetric) {
    this.flagName = flagName;
    this.targetMetric = targetMetric;
    this.currentPercentage = 0;
  }

  async progressRollout() {
    // Get current metrics
    const metrics = await this.getMetrics();

    // Check if metrics are healthy
    if (this.metricsHealthy(metrics)) {
      // Increase rollout
      this.currentPercentage = Math.min(
        this.currentPercentage + 10,
        100
      );

      await this.updateFlag({
        rollout: { percentage: this.currentPercentage }
      });

      console.log(`Rollout increased to ${this.currentPercentage}%`);
    } else {
      // Rollback
      await this.rollback();
      console.error('Metrics unhealthy, rolling back');
    }
  }

  metricsHealthy(metrics) {
    // Error rate check
    if (metrics.errorRate > 0.01) {
      return false;
    }

    // Performance check
    if (metrics.p95Latency > metrics.baseline.p95Latency * 1.2) {
      return false;
    }

    // Business metric check
    if (metrics[this.targetMetric] < metrics.baseline[this.targetMetric] * 0.95) {
      return false;
    }

    return true;
  }

  async rollback() {
    await this.updateFlag({
      enabled: false
    });

    await this.notifyTeam({
      severity: 'critical',
      message: `Feature ${this.flagName} rolled back due to metrics`
    });
  }
}
```

### 2. Dependency Management
```javascript
class FeatureDependencies {
  constructor(flags) {
    this.flags = flags;
    this.dependencies = {
      'new-payment-flow': ['payment-service-v2', 'fraud-detection'],
      'ai-recommendations': ['ml-service', 'feature-new-layout']
    };
  }

  isEnabled(flagName, context) {
    // Check dependencies first
    const deps = this.dependencies[flagName] || [];

    for (const dep of deps) {
      if (!this.flags.isEnabled(dep, context)) {
        console.warn(`Dependency ${dep} not enabled for ${flagName}`);
        return false;
      }
    }

    return this.flags.isEnabled(flagName, context);
  }
}
```

### 3. Circuit Breaker Pattern
```javascript
class FeatureFlagCircuitBreaker {
  constructor(flagName, threshold = 10) {
    this.flagName = flagName;
    this.threshold = threshold;
    this.failures = 0;
    this.state = 'closed';  // closed, open, half-open
    this.resetTimeout = null;
  }

  async execute(operation) {
    if (this.state === 'open') {
      throw new Error(`Circuit breaker open for ${this.flagName}`);
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failures = 0;
    if (this.state === 'half-open') {
      this.state = 'closed';
    }
  }

  onFailure() {
    this.failures++;

    if (this.failures >= this.threshold) {
      this.state = 'open';

      // Auto-disable flag
      featureFlags.disable(this.flagName);

      // Schedule reset
      this.resetTimeout = setTimeout(() => {
        this.state = 'half-open';
        this.failures = 0;
      }, 60000);
    }
  }
}
```

### 4. A/B Testing Framework
```javascript
class ABTest {
  constructor(experimentName, variants) {
    this.experimentName = experimentName;
    this.variants = variants;
    this.assignments = new Map();
  }

  getVariant(userId) {
    // Consistent assignment
    if (this.assignments.has(userId)) {
      return this.assignments.get(userId);
    }

    const variant = this.assignVariant(userId);
    this.assignments.set(userId, variant);

    // Track assignment
    analytics.track('experiment_assigned', {
      experiment: this.experimentName,
      variant: variant,
      userId: userId
    });

    return variant;
  }

  assignVariant(userId) {
    const hash = this.hashUserId(userId);
    const totalWeight = this.variants.reduce((sum, v) => sum + v.weight, 0);
    const position = hash % totalWeight;

    let current = 0;
    for (const variant of this.variants) {
      current += variant.weight;
      if (position < current) {
        return variant.name;
      }
    }

    return this.variants[0].name;
  }

  trackConversion(userId, metric, value) {
    const variant = this.getVariant(userId);

    analytics.track('experiment_conversion', {
      experiment: this.experimentName,
      variant: variant,
      userId: userId,
      metric: metric,
      value: value
    });
  }

  hashUserId(userId) {
    // Simple hash function
    let hash = 0;
    for (let i = 0; i < userId.length; i++) {
      hash = ((hash << 5) - hash) + userId.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash);
  }
}

// Usage
const pricingTest = new ABTest('pricing-page-2024-q1', [
  { name: 'control', weight: 50 },
  { name: 'variant-a', weight: 25 },
  { name: 'variant-b', weight: 25 }
]);

const variant = pricingTest.getVariant(user.id);

// Show appropriate variant
if (variant === 'variant-a') {
  renderPricingPageA();
} else if (variant === 'variant-b') {
  renderPricingPageB();
} else {
  renderPricingPageControl();
}

// Track conversion
pricingTest.trackConversion(user.id, 'purchase', 99.99);
```

---

## Testing Strategies

### Unit Testing
```javascript
// Mock feature flags
jest.mock('./featureFlags');

describe('Checkout', () => {
  it('uses new checkout when flag enabled', () => {
    featureFlags.isEnabled.mockReturnValue(true);

    const result = renderCheckout(user);

    expect(result).toContain('New Checkout');
  });

  it('uses old checkout when flag disabled', () => {
    featureFlags.isEnabled.mockReturnValue(false);

    const result = renderCheckout(user);

    expect(result).toContain('Classic Checkout');
  });
});
```

### Integration Testing
```javascript
// Test with real flag service
describe('Feature Flags Integration', () => {
  let flagService;

  beforeAll(async () => {
    flagService = await createTestFlagService();
  });

  beforeEach(async () => {
    await flagService.reset();
  });

  it('evaluates flags correctly', async () => {
    await flagService.createFlag({
      name: 'test-feature',
      enabled: true,
      rules: [
        {
          conditions: [
            { attribute: 'plan', operator: 'equals', value: 'premium' }
          ],
          enabled: true
        }
      ]
    });

    const result = await flagService.evaluate('test-feature', {
      userId: '123',
      plan: 'premium'
    });

    expect(result.enabled).toBe(true);
  });
});
```

---

## Migration Patterns

### Removing Feature Flags
```javascript
// Step 1: Ensure flag is at 100% for all users
async function prepareForRemoval(flagName) {
  const config = await getFlag(flagName);

  if (config.rollout.percentage !== 100) {
    throw new Error('Flag not at 100% rollout');
  }

  // Wait for stabilization period
  const daysAt100 = getDaysAtFullRollout(flagName);
  if (daysAt100 < 7) {
    throw new Error('Must be at 100% for at least 7 days');
  }

  return true;
}

// Step 2: Remove flag checks from code
// Before:
if (featureFlags.isEnabled('new-checkout', user)) {
  return newCheckout();
} else {
  return oldCheckout();
}

// After:
return newCheckout();
// Delete oldCheckout() function

// Step 3: Archive flag configuration
async function archiveFlag(flagName) {
  const config = await getFlag(flagName);

  await archiveStorage.save({
    flagName: flagName,
    config: config,
    archivedAt: new Date(),
    archivedBy: getCurrentUser()
  });

  await deleteFlag(flagName);
}
```

---

## Security Considerations

1. **Access Control**: Limit who can modify flags
2. **Audit Logging**: Track all flag changes
3. **Validation**: Validate targeting rules
4. **Rate Limiting**: Prevent flag evaluation abuse
5. **Encryption**: Encrypt sensitive flag data
6. **Versioning**: Track flag configuration history

```javascript
// Audit logging
function logFlagChange(flagName, oldConfig, newConfig, user) {
  auditLog.write({
    timestamp: new Date(),
    action: 'flag_updated',
    flag: flagName,
    user: user,
    changes: diff(oldConfig, newConfig),
    ip: request.ip
  });
}

// Access control
function canModifyFlag(user, flagName) {
  // Only admins can modify production flags
  if (flagName.includes('production') && !user.roles.includes('admin')) {
    return false;
  }

  return true;
}
```
