# Progressive Delivery Guide: Combining Canary + Feature Flags

## Overview
Progressive delivery combines the best of canary deployments, feature flags, and automated analysis to enable safe, gradual feature rollouts with fine-grained control and instant rollback capabilities.

---

## What is Progressive Delivery?

Progressive delivery is the practice of:
1. **Deploying** code to production (dark launch)
2. **Releasing** features gradually via feature flags
3. **Monitoring** real-time metrics
4. **Automating** rollout progression or rollback
5. **Controlling** blast radius of failures

### Traditional vs Progressive Delivery

```
Traditional Deployment:
Deploy → Release (all users) → Monitor → Rollback if issues

Progressive Delivery:
Deploy (dark) → Release (1% users) → Monitor → Auto-progress/rollback
                      ↓
                 Gradual increase (5% → 25% → 50% → 100%)
                      ↓
                 Per-segment rollout
                      ↓
                 Feature-level control
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Application Code (v2.0)                   │
│                  Feature Flagged (disabled)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │     Feature Flag Service      │
            │     (LaunchDarkly/Unleash)   │
            └───────────────┬───────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Internal     │    │ Canary       │    │ Production   │
│ Users (100%) │    │ Users (10%)  │    │ Users (0%)   │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │     Metrics & Monitoring      │
            │   (Prometheus, Datadog, etc)  │
            └───────────────┬───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │   Automated Analysis Engine   │
            │  (Flagger, Argo Rollouts, etc)│
            └───────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        Auto-Progress             Auto-Rollback
```

---

## Step 1: Deploy with Feature Flag (Dark Launch)

### Application Code with Feature Flag

```python
# app.py
from launchdarkly import Context
from flask import Flask, request, jsonify
import ldclient

app = Flask(__name__)

# Initialize LaunchDarkly
ldclient.set_config(ldclient.Config("sdk-key-123xyz"))
ld_client = ldclient.get()

@app.route('/api/recommendations')
def get_recommendations():
    user_id = request.headers.get('X-User-ID')

    # Create user context
    context = Context.builder(user_id).build()

    # Check feature flag
    use_new_algorithm = ld_client.variation(
        "new-recommendation-algorithm",
        context,
        False  # Default to old algorithm
    )

    if use_new_algorithm:
        # New ML-based recommendations (v2.0)
        recommendations = get_ml_recommendations(user_id)
        version = "v2.0-ml"
    else:
        # Legacy collaborative filtering (v1.0)
        recommendations = get_legacy_recommendations(user_id)
        version = "v1.0-legacy"

    # Track which version was used
    metrics.increment(
        'recommendations.served',
        tags=[f'version:{version}', f'user:{user_id}']
    )

    return jsonify({
        'recommendations': recommendations,
        'version': version
    })
```

### Kubernetes Deployment (Dark Launch)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recommendation-service
  namespace: production
spec:
  replicas: 5
  selector:
    matchLabels:
      app: recommendation-service
  template:
    metadata:
      labels:
        app: recommendation-service
        version: v2.0  # New version deployed
    spec:
      containers:
      - name: app
        image: recommendation-service:v2.0  # Contains new + old code
        env:
        - name: LAUNCHDARKLY_SDK_KEY
          valueFrom:
            secretKeyRef:
              name: feature-flags
              key: sdk-key
        - name: FEATURE_FLAG_DEFAULT
          value: "false"  # New feature disabled by default
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 1000m
            memory: 1Gi
```

```bash
# Deploy v2.0 with feature disabled (dark launch)
kubectl apply -f deployment.yaml

# Verify deployment
kubectl rollout status deployment/recommendation-service -n production

# Test that new code is deployed but feature is off
curl -H "X-User-ID: test-user" \
  http://recommendation-service/api/recommendations
# Should return v1.0-legacy
```

---

## Step 2: Enable for Internal Users

### LaunchDarkly Configuration

```json
{
  "name": "new-recommendation-algorithm",
  "key": "new-recommendation-algorithm",
  "description": "ML-based recommendation engine",
  "kind": "boolean",
  "variations": [
    { "value": false, "name": "Legacy Algorithm" },
    { "value": true, "name": "ML Algorithm" }
  ],
  "targeting": {
    "on": true,
    "rules": [
      {
        "variation": 1,
        "description": "Internal employees",
        "clauses": [
          {
            "attribute": "email",
            "op": "endsWith",
            "values": ["@company.com"]
          }
        ]
      }
    ],
    "fallthrough": {
      "variation": 0
    }
  }
}
```

### Testing Internal Rollout

```bash
# Test with internal user
curl -H "X-User-ID: employee@company.com" \
  http://recommendation-service/api/recommendations
# Should return v2.0-ml

# Test with external user
curl -H "X-User-ID: customer@external.com" \
  http://recommendation-service/api/recommendations
# Should return v1.0-legacy
```

---

## Step 3: Gradual Canary Rollout with Flagger

### Flagger Canary Configuration

```yaml
# canary.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: recommendation-service
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: recommendation-service

  service:
    port: 8080
    targetPort: 8080

  analysis:
    # Canary schedule
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    iterations: 10

    # Metrics thresholds
    metrics:
    # Success rate (overall)
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m

    # Success rate (new algorithm specifically)
    - name: ml-algorithm-success-rate
      templateRef:
        name: ml-algorithm-success-rate
      thresholdRange:
        min: 99
      interval: 1m

    # Response time
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m

    # Business metric: recommendation click-through rate
    - name: recommendation-ctr
      templateRef:
        name: recommendation-ctr
      thresholdRange:
        min: 5  # Minimum 5% CTR
      interval: 2m

    # Webhooks for progressive flag rollout
    webhooks:
    # Before rollout: enable feature for 1% of users
    - name: enable-feature-1-percent
      type: pre-rollout
      url: http://feature-flag-controller/rollout
      timeout: 30s
      metadata:
        feature: "new-recommendation-algorithm"
        percentage: "1"

    # During rollout: gradually increase percentage
    - name: progressive-flag-rollout
      type: rollout
      url: http://feature-flag-controller/rollout
      timeout: 30s
      metadata:
        feature: "new-recommendation-algorithm"
        percentage: "{{ .CanaryWeight }}"  # Match canary weight

    # After successful rollout: enable for 100%
    - name: enable-feature-100-percent
      type: post-rollout
      url: http://feature-flag-controller/rollout
      timeout: 30s
      metadata:
        feature: "new-recommendation-algorithm"
        percentage: "100"

    # On rollback: disable feature
    - name: disable-feature
      type: rollback
      url: http://feature-flag-controller/rollback
      timeout: 30s
      metadata:
        feature: "new-recommendation-algorithm"
```

### Custom Metrics for Feature Flag Usage

```yaml
# metrics.yaml
apiVersion: flagger.app/v1beta1
kind: MetricTemplate
metadata:
  name: ml-algorithm-success-rate
  namespace: production
spec:
  provider:
    type: prometheus
    address: http://prometheus:9090
  query: |
    sum(
      rate(
        recommendations_served_total{
          version="v2.0-ml",
          status="success"
        }[{{ interval }}]
      )
    )
    /
    sum(
      rate(
        recommendations_served_total{
          version="v2.0-ml"
        }[{{ interval }}]
      )
    ) * 100
---
apiVersion: flagger.app/v1beta1
kind: MetricTemplate
metadata:
  name: recommendation-ctr
  namespace: production
spec:
  provider:
    type: prometheus
    address: http://prometheus:9090
  query: |
    sum(
      rate(
        recommendation_clicks_total{
          version="v2.0-ml"
        }[{{ interval }}]
      )
    )
    /
    sum(
      rate(
        recommendations_served_total{
          version="v2.0-ml"
        }[{{ interval }}]
      )
    ) * 100
```

---

## Step 4: Feature Flag Controller Service

### Webhook Handler for Progressive Rollout

```python
# feature-flag-controller.py
from flask import Flask, request, jsonify
import ldclient
from ldclient.config import Config

app = Flask(__name__)

# Initialize LaunchDarkly
ldclient.set_config(Config("api-key-123xyz"))
ld_client = ldclient.get()

@app.route('/rollout', methods=['POST'])
def progressive_rollout():
    """Gradually increase feature flag percentage"""
    data = request.json

    feature_key = data.get('metadata', {}).get('feature')
    percentage = int(data.get('metadata', {}).get('percentage', 0))

    if not feature_key:
        return jsonify({'error': 'Missing feature key'}), 400

    try:
        # Update LaunchDarkly flag
        update_flag_percentage(feature_key, percentage)

        return jsonify({
            'approved': True,
            'message': f'Feature {feature_key} enabled for {percentage}% of users'
        })

    except Exception as e:
        return jsonify({
            'approved': False,
            'error': str(e)
        }), 500

@app.route('/rollback', methods=['POST'])
def rollback_feature():
    """Disable feature flag on rollback"""
    data = request.json
    feature_key = data.get('metadata', {}).get('feature')

    if not feature_key:
        return jsonify({'error': 'Missing feature key'}), 400

    try:
        # Disable feature
        update_flag_percentage(feature_key, 0)

        return jsonify({
            'approved': True,
            'message': f'Feature {feature_key} disabled (rollback)'
        })

    except Exception as e:
        return jsonify({
            'approved': False,
            'error': str(e)
        }), 500

def update_flag_percentage(feature_key, percentage):
    """Update LaunchDarkly flag rollout percentage"""
    import requests

    # LaunchDarkly API endpoint
    url = f"https://app.launchdarkly.com/api/v2/flags/production/{feature_key}"

    # Update targeting rules
    patch = [
        {
            "op": "replace",
            "path": "/targeting/rules/0/rollout/variations/0/weight",
            "value": 100000 - (percentage * 1000)  # Inverted for "off" variation
        },
        {
            "op": "replace",
            "path": "/targeting/rules/0/rollout/variations/1/weight",
            "value": percentage * 1000  # "on" variation
        }
    ]

    headers = {
        "Authorization": "api-key-123xyz",
        "Content-Type": "application/json"
    }

    response = requests.patch(url, json=patch, headers=headers)
    response.raise_for_status()

    print(f"Updated {feature_key} to {percentage}%")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Deploy Feature Flag Controller

```yaml
# feature-flag-controller-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: feature-flag-controller
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: feature-flag-controller
  template:
    metadata:
      labels:
        app: feature-flag-controller
    spec:
      containers:
      - name: controller
        image: feature-flag-controller:latest
        env:
        - name: LAUNCHDARKLY_API_KEY
          valueFrom:
            secretKeyRef:
              name: feature-flags
              key: api-key
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: feature-flag-controller
  namespace: production
spec:
  selector:
    app: feature-flag-controller
  ports:
  - port: 80
    targetPort: 8080
```

---

## Step 5: Monitor Progressive Rollout

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Progressive Delivery - Recommendation Service",
    "panels": [
      {
        "title": "Feature Flag Rollout %",
        "targets": [{
          "expr": "feature_flag_percentage{feature='new-recommendation-algorithm'}"
        }]
      },
      {
        "title": "Canary Traffic Weight %",
        "targets": [{
          "expr": "flagger_canary_weight{name='recommendation-service'}"
        }]
      },
      {
        "title": "Success Rate by Version",
        "targets": [
          {
            "expr": "sum(rate(recommendations_served_total{status='success'}[5m])) by (version) / sum(rate(recommendations_served_total[5m])) by (version) * 100",
            "legendFormat": "{{version}}"
          }
        ]
      },
      {
        "title": "Click-Through Rate by Version",
        "targets": [
          {
            "expr": "sum(rate(recommendation_clicks_total[5m])) by (version) / sum(rate(recommendations_served_total[5m])) by (version) * 100",
            "legendFormat": "{{version}} CTR"
          }
        ]
      },
      {
        "title": "P95 Latency by Version",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(recommendation_duration_bucket[5m])) by (le, version))",
            "legendFormat": "{{version}}"
          }
        ]
      },
      {
        "title": "Rollout Events",
        "targets": [{
          "expr": "changes(flagger_canary_weight{name='recommendation-service'}[30m])"
        }]
      }
    ]
  }
}
```

### Prometheus Alerts

```yaml
# progressive-delivery-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: progressive-delivery-alerts
  namespace: production
spec:
  groups:
  - name: progressive-delivery
    interval: 30s
    rules:
    # Alert if new feature has high error rate
    - alert: NewFeatureHighErrorRate
      expr: |
        (
          sum(rate(recommendations_served_total{version="v2.0-ml",status="error"}[5m]))
          /
          sum(rate(recommendations_served_total{version="v2.0-ml"}[5m]))
        ) > 0.05
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "New recommendation algorithm has >5% error rate"
        description: "Version v2.0-ml error rate: {{ $value }}%"

    # Alert if CTR drops significantly
    - alert: RecommendationCTRDrop
      expr: |
        (
          sum(rate(recommendation_clicks_total{version="v2.0-ml"}[10m]))
          /
          sum(rate(recommendations_served_total{version="v2.0-ml"}[10m]))
        )
        <
        (
          sum(rate(recommendation_clicks_total{version="v1.0-legacy"}[10m]))
          /
          sum(rate(recommendations_served_total{version="v1.0-legacy"}[10m]))
        ) * 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "New algorithm CTR is >10% lower than legacy"

    # Alert if rollout is stuck
    - alert: ProgressiveDeliveryStuck
      expr: |
        (
          changes(flagger_canary_weight{name="recommendation-service"}[30m]) == 0
          and
          flagger_canary_weight{name="recommendation-service"} > 0
          and
          flagger_canary_weight{name="recommendation-service"} < 100
        )
      for: 30m
      labels:
        severity: warning
      annotations:
        summary: "Progressive rollout has not progressed in 30 minutes"
```

---

## Step 6: Automated Rollout Progression

### Rollout Timeline

```
Time    Canary%  Feature%  Action
-----   -------  --------  ------
0min    0%       0%        Deploy v2.0 (dark)
                           Feature flag OFF

+5min   0%       100%      Enable for internal users
                           Validate with employees

+30min  10%      1%        Start canary rollout
                           Enable flag for 1% users

+35min  20%      5%        Increase to 5%
                           Monitor metrics

+40min  30%      10%       Increase to 10%
                           Metrics healthy

+45min  40%      25%       Increase to 25%
                           Business metrics good

+50min  50%      50%       Increase to 50%
                           Half rollout complete

+55min  0%       100%      Promote canary
                           Full traffic to new version
                           Feature flag 100%

+60min  -        -         Remove old deployment
                           Clean up canary resources
```

### Argo Rollouts with Feature Flags

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: recommendation-service
  namespace: production
spec:
  replicas: 5
  selector:
    matchLabels:
      app: recommendation-service
  template:
    metadata:
      labels:
        app: recommendation-service
    spec:
      containers:
      - name: app
        image: recommendation-service:v2.0
        env:
        - name: LAUNCHDARKLY_SDK_KEY
          valueFrom:
            secretKeyRef:
              name: feature-flags
              key: sdk-key

  strategy:
    canary:
      # Canary service
      canaryService: recommendation-service-canary
      # Stable service
      stableService: recommendation-service

      # Traffic routing
      trafficRouting:
        istio:
          virtualService:
            name: recommendation-service
            routes:
            - primary

      # Progressive steps
      steps:
      # Step 1: 10% traffic, wait for analysis
      - setWeight: 10
      - pause: {}

      # Step 2: Feature flag 5%, analyze
      - setWeight: 20
      - analysis:
          templates:
          - templateName: success-rate
          - templateName: business-metrics
          args:
          - name: service-name
            value: recommendation-service-canary
          - name: feature-percentage
            value: "5"

      # Step 3: Feature flag 10%
      - setWeight: 30
      - pause: {duration: 5m}

      # Step 4: Feature flag 25%
      - setWeight: 40
      - analysis:
          templates:
          - templateName: success-rate
          - templateName: business-metrics
          args:
          - name: feature-percentage
            value: "25"

      # Step 5: Feature flag 50%
      - setWeight: 50
      - pause: {duration: 10m}
      - analysis:
          templates:
          - templateName: comprehensive-analysis
          args:
          - name: feature-percentage
            value: "50"

      # Promotion
      - setWeight: 100
```

---

## Step 7: Rollback Scenarios

### Automatic Rollback on Metrics

```yaml
# analysis-template.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: comprehensive-analysis
  namespace: production
spec:
  args:
  - name: service-name
  - name: feature-percentage

  metrics:
  # Success rate must be >99%
  - name: success-rate
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(http_requests_total{
            service="{{args.service-name}}",
            status=~"2.."
          }[5m]))
          /
          sum(rate(http_requests_total{
            service="{{args.service-name}}"
          }[5m])) * 100
    successCondition: result >= 99
    failureLimit: 3
    interval: 1m
    count: 10

  # Business metric: CTR must be >= baseline
  - name: recommendation-ctr
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(recommendation_clicks_total{version="v2.0-ml"}[10m]))
          /
          sum(rate(recommendations_served_total{version="v2.0-ml"}[10m]))
          * 100
    successCondition: result >= 4.5
    failureLimit: 2
    interval: 2m
    count: 5

  # Response time must be <500ms
  - name: response-time
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_bucket{
              service="{{args.service-name}}"
            }[5m])) by (le)
          )
    successCondition: result < 500
    failureLimit: 3
    interval: 1m
    count: 10
```

### Manual Rollback Procedure

```bash
#!/bin/bash
# rollback-progressive-delivery.sh

NAMESPACE="production"
FEATURE_FLAG="new-recommendation-algorithm"

echo "🔄 Rolling back progressive delivery..."

# 1. Disable feature flag immediately
echo "1. Disabling feature flag..."
curl -X POST http://feature-flag-controller/rollback \
  -H "Content-Type: application/json" \
  -d "{\"metadata\": {\"feature\": \"$FEATURE_FLAG\"}}"

# 2. Abort canary rollout
echo "2. Aborting canary rollout..."
kubectl argo rollouts abort recommendation-service -n $NAMESPACE

# 3. Rollback to stable version
echo "3. Rolling back to stable version..."
kubectl argo rollouts undo recommendation-service -n $NAMESPACE

# 4. Verify rollback
echo "4. Verifying rollback..."
kubectl argo rollouts status recommendation-service -n $NAMESPACE

# 5. Check metrics
echo "5. Checking metrics..."
curl -s "http://prometheus:9090/api/v1/query?query=feature_flag_percentage{feature='$FEATURE_FLAG'}"

echo "✅ Rollback complete"
```

---

## Step 8: Multi-Environment Strategy

### Development → Staging → Production

```yaml
# dev-rollout.yaml (Fast rollout for development)
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: recommendation-service
  namespace: development
spec:
  strategy:
    canary:
      steps:
      - setWeight: 50    # Fast rollout in dev
      - pause: {duration: 2m}
      - setWeight: 100

---
# staging-rollout.yaml (Moderate rollout for staging)
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: recommendation-service
  namespace: staging
spec:
  strategy:
    canary:
      steps:
      - setWeight: 25
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100

---
# production-rollout.yaml (Conservative rollout)
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: recommendation-service
  namespace: production
spec:
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 10m}
      - setWeight: 25
      - pause: {duration: 15m}
      - setWeight: 50
      - pause: {duration: 20m}
      - setWeight: 100
```

---

## Best Practices

### 1. Decouple Deploy from Release
```
✓ Deploy code to production (dark)
✓ Release features via flags (gradual)
✓ Independent deployment and feature release
✓ Ship code anytime, release when ready
```

### 2. Comprehensive Monitoring
```python
# Track both technical and business metrics
metrics_to_monitor = [
    # Technical
    'error_rate',
    'response_time',
    'cpu_usage',
    'memory_usage',

    # Business
    'conversion_rate',
    'click_through_rate',
    'revenue_per_user',
    'user_engagement'
]
```

### 3. Gradual Rollout Sequence
```
Internal users → 1% → 5% → 10% → 25% → 50% → 100%
     ↓            ↓     ↓     ↓      ↓      ↓      ↓
  Employees    Canary Early  Growth  Half  Full  Complete
               Users  Adopters       Roll   Roll
```

### 4. Clear Rollback Criteria
```yaml
rollback_criteria:
  technical:
    - error_rate > 1%
    - p95_latency > 500ms
    - availability < 99.9%

  business:
    - conversion_rate drops > 5%
    - ctr drops > 10%
    - user_complaints > threshold

  manual:
    - critical_bug_discovered
    - security_vulnerability
    - compliance_issue
```

---

## Summary

Progressive delivery provides:
1. **Risk Mitigation**: Gradual rollout limits blast radius
2. **Fast Rollback**: Feature flags enable instant disable
3. **Data-Driven**: Metrics guide rollout decisions
4. **Automation**: Reduces human error
5. **Fine-Grained Control**: Feature-level, not just deployment
6. **Business Alignment**: Optimize for business metrics

---

## Resources

- Flagger: https://flagger.app/
- Argo Rollouts: https://argoproj.github.io/argo-rollouts/
- LaunchDarkly: https://launchdarkly.com/
- Progressive Delivery: https://www.split.io/glossary/progressive-delivery/
- Feature Flags: https://martinfowler.com/articles/feature-toggles.html
