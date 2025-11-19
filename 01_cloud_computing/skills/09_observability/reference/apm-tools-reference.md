# APM Tools Reference

## Application Performance Monitoring (APM) Overview

APM tools provide comprehensive monitoring of application performance, user experience, and business transactions across distributed systems.

## Key APM Capabilities

### Core Features
- **Transaction Tracing**: End-to-end request tracking
- **Code-Level Visibility**: Method-level performance
- **Real User Monitoring (RUM)**: Actual user experience
- **Synthetic Monitoring**: Proactive health checks
- **Error Tracking**: Exception capture and analysis
- **Database Monitoring**: Query performance analysis
- **Infrastructure Monitoring**: Host and container metrics
- **Service Maps**: Dependency visualization

## Major APM Platforms

### Datadog

#### Overview
- **Type**: Full-stack SaaS APM
- **Deployment**: Cloud-based agent
- **Languages**: 20+ languages
- **Pricing**: Per-host + APM pricing

#### Key Features
```yaml
Capabilities:
  - APM with distributed tracing
  - Real User Monitoring (RUM)
  - Synthetic monitoring
  - Logs, metrics, traces correlation
  - Custom dashboards and alerts
  - Service dependencies mapping
  - Profiling (continuous profiler)
  - Security monitoring

Integrations:
  - 600+ integrations
  - Cloud platforms (AWS, Azure, GCP)
  - Databases, message queues
  - Container orchestration
```

#### Agent Configuration
```yaml
# datadog.yaml
api_key: YOUR_API_KEY
site: datadoghq.com

apm_config:
  enabled: true
  env: production

logs_enabled: true

process_config:
  enabled: true

tags:
  - env:production
  - service:payment-api
  - version:1.2.3
```

#### Application Instrumentation
```python
# Python
from ddtrace import tracer, patch_all

# Auto-instrument
patch_all()

# Custom span
@tracer.wrap('process_payment')
def process_payment(order_id):
    with tracer.trace('validate_order') as span:
        span.set_tag('order.id', order_id)
        # ... processing logic
```

#### Key Metrics
- `trace.requests.duration` (latency)
- `trace.requests.errors` (error count)
- `trace.servlet.request` (HTTP requests)
- Custom metrics via DogStatsD

### New Relic

#### Overview
- **Type**: Full-stack SaaS APM
- **Deployment**: Agent-based
- **Languages**: 10+ languages
- **Pricing**: User-based + data ingestion

#### Key Features
```yaml
Capabilities:
  - APM with transaction tracing
  - Browser monitoring (RUM)
  - Mobile app monitoring
  - Synthetic monitoring
  - Infrastructure monitoring
  - NRQL query language
  - AI-assisted incident analysis
  - Distributed tracing

Unique Features:
  - Applied Intelligence (AIOps)
  - Incident Intelligence
  - Proactive Detection
  - Vulnerability Management
```

#### Agent Configuration
```yaml
# newrelic.yml
common: &default_settings
  license_key: YOUR_LICENSE_KEY
  app_name: Payment API

  distributed_tracing:
    enabled: true

  transaction_tracer:
    enabled: true
    transaction_threshold: 0.5
    record_sql: obfuscated

  error_collector:
    enabled: true
    ignore_errors: ['404']

production:
  <<: *default_settings
  log_level: info
```

#### NRQL Queries
```sql
-- Average response time
SELECT average(duration) FROM Transaction
WHERE appName = 'Payment API'
TIMESERIES AUTO

-- Error rate
SELECT percentage(count(*), WHERE error IS true)
FROM Transaction
SINCE 1 hour ago

-- Slow transactions
SELECT count(*) FROM Transaction
WHERE duration > 2
FACET name
SINCE 1 day ago
```

### Dynatrace

#### Overview
- **Type**: AI-powered full-stack APM
- **Deployment**: OneAgent (auto-discovery)
- **Languages**: 30+ technologies
- **Pricing**: Host-based + licensing

#### Key Features
```yaml
Capabilities:
  - Smartscape (automatic topology)
  - Davis AI (root cause analysis)
  - Code-level visibility
  - Real User Monitoring
  - Synthetic monitoring
  - Infrastructure monitoring
  - Cloud automation
  - Business analytics

AI Features:
  - Automatic baselining
  - Anomaly detection
  - Root cause analysis
  - Problem correlation
  - Predictive alerts
```

#### OneAgent Installation
```bash
# Linux
wget -O Dynatrace-OneAgent.sh https://xxx.live.dynatrace.com/api/v1/deployment/installer/agent/unix/default/latest?Api-Token=YOUR_TOKEN
sudo /bin/sh Dynatrace-OneAgent.sh --set-app-log-content-access=true
```

#### Auto-Discovery
- Automatically detects:
  - Processes and services
  - Dependencies
  - Database calls
  - External services
  - Network connections

#### Davis AI Analysis
```
Problem Detection:
1. Baseline normal behavior
2. Detect anomalies automatically
3. Correlate related events
4. Identify root cause
5. Suggest remediation
```

### AppDynamics

#### Overview
- **Type**: Business transaction APM
- **Deployment**: Agent-based
- **Languages**: Java, .NET, Node.js, PHP, Python
- **Pricing**: License + APM units

#### Key Features
```yaml
Capabilities:
  - Business Transaction monitoring
  - Application topology
  - Database visibility
  - End User Monitoring (EUM)
  - Server visibility
  - Network visibility
  - Business iQ (analytics)
  - Runtime application self-protection

Business Focus:
  - Revenue impact analysis
  - Business transactions
  - Conversion funnels
  - User journey mapping
```

#### Agent Configuration (Java)
```xml
<!-- controller-info.xml -->
<controller-info>
  <controller-host>mycompany.saas.appdynamics.com</controller-host>
  <controller-port>443</controller-port>
  <controller-ssl-enabled>true</controller-ssl-enabled>
  <account-name>customer1</account-name>
  <account-access-key>YOUR_KEY</account-access-key>

  <application-name>Payment-API</application-name>
  <tier-name>API-Tier</tier-name>
  <node-name>api-node-1</node-name>
</controller-info>
```

#### Business Transactions
```java
// Define custom business transaction
@CustomBusinessTransaction
public void processOrder(Order order) {
    // AppDynamics automatically tracks:
    // - Transaction time
    // - Call graph
    // - Database queries
    // - External calls
}
```

### Elastic APM

#### Overview
- **Type**: Open-source APM (part of Elastic Stack)
- **Deployment**: Self-hosted or cloud
- **Languages**: 8+ languages
- **Pricing**: Free (open source) or Elastic Cloud

#### Key Features
```yaml
Capabilities:
  - Distributed tracing
  - Real User Monitoring
  - Service maps
  - Error tracking
  - Metrics correlation
  - Integration with ELK Stack
  - Machine learning anomaly detection
  - Alerting

Integration:
  - Shares infrastructure with ELK
  - Unified search (Elasticsearch)
  - Kibana visualizations
  - Log correlation
```

#### APM Server Configuration
```yaml
# apm-server.yml
apm-server:
  host: "0.0.0.0:8200"
  secret_token: "YOUR_SECRET_TOKEN"

output.elasticsearch:
  hosts: ["http://localhost:9200"]

setup.kibana:
  host: "http://localhost:5601"
```

#### Agent Configuration (Node.js)
```javascript
// Elastic APM
const apm = require('elastic-apm-node').start({
  serviceName: 'payment-api',
  serverUrl: 'http://localhost:8200',
  environment: 'production',
  secretToken: 'YOUR_SECRET_TOKEN'
});

// Custom transaction
const transaction = apm.startTransaction('process-payment');
// ... process payment ...
transaction.end();

// Custom span
const span = apm.startSpan('database-query');
// ... database query ...
span.end();
```

### Honeycomb

#### Overview
- **Type**: Observability platform focused on exploration
- **Deployment**: SaaS
- **Languages**: OpenTelemetry support
- **Pricing**: Event-based

#### Key Features
```yaml
Capabilities:
  - High-cardinality exploration
  - BubbleUp (pattern detection)
  - Heatmaps
  - Distributed tracing
  - SLO tracking
  - Derived columns
  - Triggers (alerts)

Philosophy:
  - Arbitrary query exploration
  - Unknown-unknowns
  - High-dimensional data
  - Event-based pricing
```

#### Instrumentation (OpenTelemetry)
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure Honeycomb exporter
exporter = OTLPSpanExporter(
    endpoint="api.honeycomb.io:443",
    headers=(
        ("x-honeycomb-team", "YOUR_API_KEY"),
        ("x-honeycomb-dataset", "payment-api"),
    )
)

provider = TracerProvider()
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
```

#### Queries (BubbleUp)
```
1. Find slow requests: duration > 1s
2. BubbleUp to find patterns:
   - Which user_ids are affected?
   - Which endpoints are slow?
   - What's different about slow requests?
3. Visualize with heatmaps
4. Create SLO for critical paths
```

### Lightstep

#### Overview
- **Type**: Modern APM for microservices
- **Deployment**: SaaS
- **Languages**: OpenTelemetry native
- **Pricing**: Span-based

#### Key Features
```yaml
Capabilities:
  - Change Intelligence
  - Service Diagram
  - Trace analysis
  - Correlations
  - Notebook-style queries
  - Deployment tracking
  - Incident automation

Focus:
  - OpenTelemetry first
  - CI/CD integration
  - Change analysis
  - Performance regression
```

## APM Comparison Matrix

```
Feature                 | Datadog | New Relic | Dynatrace | AppDynamics | Elastic APM | Honeycomb
------------------------|---------|-----------|-----------|-------------|-------------|----------
Distributed Tracing     | ✓       | ✓         | ✓         | ✓           | ✓           | ✓
Real User Monitoring    | ✓       | ✓         | ✓         | ✓           | ✓           | ✗
Synthetic Monitoring    | ✓       | ✓         | ✓         | ✓           | ✓           | ✗
Code-Level Profiling    | ✓       | ✓         | ✓         | ✓           | ✗           | ✗
AI/ML Insights          | ✓       | ✓         | ✓✓        | ✓           | ✓           | ✓
Open Source             | ✗       | ✗         | ✗         | ✗           | ✓           | ✗
Self-Hosted Option      | ✗       | ✗         | ✓         | ✓           | ✓           | ✗
OpenTelemetry Support   | ✓       | ✓         | ✓         | ✓           | ✓           | ✓✓
Cost Model              | Per-host| Per-user  | Per-host  | Per-APM-unit| Free/Paid   | Per-event
Best For                | All     | Startups  | Enterprise| Business TX | ELK users   | Exploration
```

## Open Source APM Alternatives

### Jaeger
```yaml
Type: Distributed tracing
Origin: Uber
Features:
  - OpenTelemetry compatible
  - Multiple storage backends
  - Service dependency graph
  - Root cause analysis

Deployment:
  - Jaeger Collector
  - Jaeger Query
  - Storage (Cassandra, Elasticsearch)
  - UI
```

### Zipkin
```yaml
Type: Distributed tracing
Origin: Twitter
Features:
  - Simple deployment
  - REST API
  - Multiple language support
  - Zipkin UI

Deployment:
  - Zipkin server
  - Storage (In-memory, MySQL, Elasticsearch, Cassandra)
```

### SkyWalking
```yaml
Type: APM and observability
Origin: Apache
Features:
  - Service mesh support
  - Topology map
  - Metrics analysis
  - Distributed tracing
  - Log analysis

Components:
  - OAP (Observability Analysis Platform)
  - Storage
  - UI
  - Agent
```

### Pinpoint
```yaml
Type: APM for Java
Origin: Naver
Features:
  - Bytecode instrumentation
  - Code-level visibility
  - Real-time monitoring
  - No code changes needed

Focus:
  - Java applications
  - Low overhead
  - Detailed code profiling
```

## Specialized APM Tools

### Sentry (Error Tracking)
```python
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_DSN",
    environment="production",
    release="payment-api@1.2.3",
    traces_sample_rate=0.1
)

# Automatic error capture
try:
    process_payment()
except Exception as e:
    sentry_sdk.capture_exception(e)

# Add context
sentry_sdk.set_user({"id": "12345", "email": "user@example.com"})
sentry_sdk.set_tag("payment_method", "credit_card")
```

### Rollbar (Error Monitoring)
```python
import rollbar

rollbar.init('YOUR_ACCESS_TOKEN', environment='production')

try:
    process_payment()
except Exception as e:
    rollbar.report_exc_info()
    # Includes:
    # - Stack trace
    # - Environment details
    # - Request data
    # - Custom context
```

## APM Best Practices

### Instrumentation
1. **Auto-instrument first**: Use agent auto-instrumentation
2. **Custom instrumentation**: Add for critical paths
3. **Business metrics**: Track business KPIs
4. **User context**: Include user IDs (not PII)
5. **Version tracking**: Tag with release versions

### Configuration
1. **Sampling**: Start with 100%, reduce if needed
2. **Thresholds**: Set appropriate transaction thresholds
3. **Filtering**: Exclude health checks, static assets
4. **Tagging**: Use consistent tags across services
5. **Error handling**: Configure error collection

### Performance
1. **Agent overhead**: Monitor agent resource usage
2. **Batch sending**: Configure batch sizes
3. **Async processing**: Use async APM calls
4. **Compression**: Enable payload compression
5. **Local caching**: Buffer data locally

### Analysis
1. **Service maps**: Understand dependencies
2. **Transaction tracing**: Identify bottlenecks
3. **Error analysis**: Group and prioritize errors
4. **Deployment tracking**: Compare before/after
5. **SLO tracking**: Monitor service objectives

## Pricing Considerations

### Cost Factors
1. **Hosts/Containers**: Per-host pricing
2. **Data Volume**: Per-GB or per-event
3. **Users**: Per-user seats
4. **Retention**: Storage duration
5. **Features**: Advanced features cost more

### Cost Optimization
```yaml
Strategies:
  - Sample non-critical services aggressively
  - Reduce retention for old data
  - Filter out noisy transactions
  - Use tiered storage (hot/cold)
  - Right-size agent deployment
  - Monitor actual usage vs plan
```

### Open Source vs Commercial
```
Open Source Pros:
  - No licensing costs
  - Full control
  - Customizable

Open Source Cons:
  - Operational overhead
  - Requires expertise
  - Self-support

Commercial Pros:
  - Easy setup
  - Managed service
  - Support included
  - Advanced features

Commercial Cons:
  - Recurring costs
  - Vendor lock-in
  - Less control
```

## Migration Strategies

### From Legacy Monitoring
```
1. Assess current coverage
2. Choose APM platform
3. Pilot with one service
4. Gradual rollout
5. Run parallel (short period)
6. Migrate dashboards/alerts
7. Decommission legacy
```

### Between APM Tools
```
1. Export existing instrumentation logic
2. Install new agent
3. Compare data quality
4. Migrate dashboards
5. Update alerts
6. Train team
7. Switch over
```

### To OpenTelemetry
```
Benefits:
  - Vendor-neutral
  - Future-proof
  - Flexibility
  - Standard

Steps:
  1. Add OpenTelemetry SDK
  2. Configure exporters
  3. Migrate custom instrumentation
  4. Test data quality
  5. Remove vendor agents
```

## Selection Criteria

### Questions to Ask
1. **Scale**: How many hosts/services?
2. **Budget**: What's the budget?
3. **Expertise**: Self-host or SaaS?
4. **Features**: What features are critical?
5. **Integration**: Existing tool stack?
6. **Compliance**: Data residency requirements?
7. **Team**: Team size and skills?

### Decision Matrix
```
Small Team, Simple App:
  → New Relic, Elastic APM (if ELK user)

Enterprise, Complex:
  → Dynatrace, AppDynamics

Cost-Conscious:
  → Elastic APM (self-hosted), Jaeger

Exploration-Focused:
  → Honeycomb, Lightstep

Future-Proof:
  → OpenTelemetry + Backend of choice
```
