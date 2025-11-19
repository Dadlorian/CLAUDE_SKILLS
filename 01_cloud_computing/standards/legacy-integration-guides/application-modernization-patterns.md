# Application Modernization Patterns

## Table of Contents
1. [Overview](#overview)
2. [Strangler Fig Pattern](#strangler-fig-pattern)
3. [Parallel Run Pattern](#parallel-run-pattern)
4. [Phased Migration Pattern](#phased-migration-pattern)
5. [Containerization Strategy](#containerization-strategy)
6. [Risk Mitigation](#risk-mitigation)
7. [Rollback Plans](#rollback-plans)
8. [Case Studies](#case-studies)
9. [Tool Recommendations](#tool-recommendations)

## Overview

Application modernization transforms legacy applications to leverage cloud-native architectures, modern development practices, and contemporary technology stacks. This process enables organizations to improve agility, reduce costs, and enhance scalability while preserving business logic and minimizing risk.

### Modernization Objectives

**Business Goals**:
- Accelerate time-to-market for new features
- Reduce operational costs
- Improve application scalability and reliability
- Enable digital transformation initiatives
- Enhance customer experience
- Support business growth and expansion

**Technical Goals**:
- Adopt cloud-native architectures
- Implement DevOps and CI/CD practices
- Improve application performance
- Modernize technology stack
- Enhance security and compliance
- Enable microservices architecture

### Modernization Challenges

**Technical Complexity**:
- Monolithic application architecture
- Tight coupling between components
- Legacy technology dependencies
- Limited or outdated documentation
- Technical debt accumulation
- Complex integration points

**Organizational Challenges**:
- Cultural resistance to change
- Skills gap in modern technologies
- Resource constraints
- Risk aversion for critical applications
- Coordination across teams
- Timeline and budget pressures

## Strangler Fig Pattern

### Concept and Origin

The Strangler Fig pattern, named after the strangler fig tree that grows around and eventually replaces its host tree, involves gradually replacing legacy system functionality with new services while the old system continues to operate.

**Pattern Invented By**: Martin Fowler (2004)

**Key Principle**: Incrementally migrate functionality from legacy to modern system without requiring a "big bang" rewrite.

### Architecture

```
┌──────────────────────────────────────┐
│        Routing/Facade Layer          │
│    (API Gateway, Service Mesh)       │
└──────────┬───────────────────┬───────┘
           │                   │
    ┌──────▼──────┐    ┌──────▼──────────┐
    │   Modern    │    │    Legacy       │
    │ Microservices│   │   Monolith      │
    │  (Cloud)    │    │  (On-Prem)      │
    └─────────────┘    └─────────────────┘
         │                     │
    ┌────▼─────┐         ┌────▼────┐
    │  Modern  │         │ Legacy  │
    │   Data   │         │  Data   │
    └──────────┘         └─────────┘
```

### Implementation Methodology

#### Phase 1: Establish Facade Layer

**Step 1: Deploy API Gateway**

```yaml
# Kong API Gateway Configuration Example
services:
  - name: legacy-service
    url: http://legacy-monolith.company.local:8080
    routes:
      - name: legacy-route
        paths:
          - /api/legacy

  - name: modern-service
    url: http://modern-service.cluster.local:8080
    routes:
      - name: modern-route
        paths:
          - /api/v2/users
```

**Step 2: Implement Request Routing**

```javascript
// Express.js middleware example for intelligent routing
const express = require('express');
const httpProxy = require('http-proxy');
const app = express();

const legacyProxy = httpProxy.createProxyServer({
    target: 'http://legacy-monolith:8080'
});

const modernProxy = httpProxy.createProxyServer({
    target: 'http://modern-services:8080'
});

// Feature flag-based routing
app.use('/api/users', (req, res) => {
    const userId = req.query.userId;

    // Check if user is migrated to new system
    if (isUserMigrated(userId)) {
        modernProxy.web(req, res);
    } else {
        legacyProxy.web(req, res);
    }
});

// Gradual rollout using percentage
app.use('/api/orders', (req, res) => {
    const rolloutPercentage = 20; // 20% to modern service

    if (Math.random() * 100 < rolloutPercentage) {
        modernProxy.web(req, res);
    } else {
        legacyProxy.web(req, res);
    }
});

app.listen(3000);
```

#### Phase 2: Identify and Extract Bounded Contexts

**Domain-Driven Design Approach**:

```
Legacy Monolith Analysis:
├─ User Management (High cohesion, low coupling) → Extract First
├─ Order Processing (Medium coupling)
├─ Inventory Management (Medium coupling)
├─ Payment Processing (High cohesion) → Extract Second
├─ Reporting (Read-only, low coupling) → Extract Third
└─ Core Business Logic (High coupling) → Migrate Last
```

**Extraction Priority Matrix**:

| Component | Business Value | Coupling | Complexity | Priority |
|-----------|----------------|----------|------------|----------|
| User Management | High | Low | Low | 1 |
| Payment Processing | High | Medium | Medium | 2 |
| Reporting | Medium | Low | Low | 3 |
| Inventory | Medium | High | Medium | 4 |
| Order Processing | High | High | High | 5 |
| Core Business | Critical | Very High | Very High | 6 |

#### Phase 3: Extract First Service

**Example: Extract User Service**

**Step 1: Design Service Interface**

```java
// Modern User Service API
@RestController
@RequestMapping("/api/v2/users")
public class UserController {

    @Autowired
    private UserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody CreateUserRequest request) {
        User user = userService.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }

    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(
            @PathVariable Long id,
            @RequestBody UpdateUserRequest request) {
        return userService.updateUser(id, request)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
```

**Step 2: Implement Data Synchronization**

```python
# Data synchronization strategy
class UserDataSynchronizer:
    def __init__(self, legacy_db, modern_db):
        self.legacy_db = legacy_db
        self.modern_db = modern_db

    def sync_user(self, user_id):
        # Read from legacy
        legacy_user = self.legacy_db.get_user(user_id)

        # Transform to modern schema
        modern_user = self.transform_user(legacy_user)

        # Write to modern database
        self.modern_db.save_user(modern_user)

        # Mark as migrated
        self.mark_migrated(user_id)

    def bidirectional_sync(self, user_id):
        # Dual write to both systems during transition
        legacy_user = self.legacy_db.get_user(user_id)
        modern_user = self.modern_db.get_user(user_id)

        # Conflict resolution (last-write-wins)
        if legacy_user.updated_at > modern_user.updated_at:
            self.sync_to_modern(legacy_user)
        elif modern_user.updated_at > legacy_user.updated_at:
            self.sync_to_legacy(modern_user)
```

**Step 3: Implement Routing Logic**

```javascript
// Sophisticated routing with fallback
async function routeUserRequest(req, res) {
    const userId = req.params.id;

    try {
        // Check if user exists in modern system
        const isMigrated = await checkMigrationStatus(userId);

        if (isMigrated) {
            // Route to modern service
            const response = await fetch(`http://modern-user-service/api/v2/users/${userId}`);

            if (response.ok) {
                return res.json(await response.json());
            } else {
                // Fallback to legacy if modern service fails
                console.warn('Modern service failed, falling back to legacy');
                return routeToLegacy(req, res);
            }
        } else {
            // Route to legacy system
            return routeToLegacy(req, res);
        }
    } catch (error) {
        console.error('Routing error:', error);
        // Always fallback to legacy on error
        return routeToLegacy(req, res);
    }
}
```

#### Phase 4: Gradual Migration

**Migration Strategies**:

**A. User-Based Migration**
```python
# Migrate users in cohorts
class CohortMigration:
    def __init__(self):
        self.cohorts = [
            {'name': 'internal_users', 'percentage': 100, 'week': 1},
            {'name': 'beta_customers', 'percentage': 100, 'week': 2},
            {'name': 'premium_tier', 'percentage': 50, 'week': 3},
            {'name': 'premium_tier', 'percentage': 100, 'week': 4},
            {'name': 'all_users', 'percentage': 10, 'week': 5},
            {'name': 'all_users', 'percentage': 25, 'week': 6},
            {'name': 'all_users', 'percentage': 50, 'week': 7},
            {'name': 'all_users', 'percentage': 100, 'week': 8},
        ]

    def should_migrate_user(self, user, current_week):
        cohort = self.get_cohort_for_week(current_week)

        if user.is_internal:
            return current_week >= 1
        if user.is_beta_tester:
            return current_week >= 2
        if user.tier == 'premium':
            return current_week >= 4

        # Percentage-based rollout for remaining users
        if current_week >= 5:
            hash_value = hash(user.id) % 100
            return hash_value < cohort['percentage']

        return False
```

**B. Feature-Based Migration**
```yaml
# Feature flags configuration (LaunchDarkly example)
features:
  user-service-v2:
    enabled: true
    rules:
      - variation: modern
        clauses:
          - attribute: email
            op: endsWith
            values: ["@company.com"]  # Internal users first

      - variation: modern
        clauses:
          - attribute: userTier
            op: in
            values: ["premium"]
        rollout:
          percentage: 50  # 50% of premium users

      - variation: legacy
        clauses:
          - attribute: default
            op: in
            values: [true]
```

**C. Geographic Migration**
```javascript
// Region-based migration
function getServiceEndpoint(userId, userRegion) {
    const migratedRegions = ['us-west', 'eu-west'];
    const pilotRegion = 'us-east';

    if (migratedRegions.includes(userRegion)) {
        return 'http://modern-service';
    } else if (userRegion === pilotRegion) {
        // Gradual rollout in pilot region
        if (isInRolloutPercentage(userId, 30)) {
            return 'http://modern-service';
        }
    }

    return 'http://legacy-service';
}
```

#### Phase 5: Decommission Legacy Components

**Decommissioning Checklist**:

```
Pre-Decommission Validation:
[ ] 100% of traffic routed to modern services
[ ] No errors in modern services for 2+ weeks
[ ] Data synchronization disabled
[ ] Legacy service monitoring shows zero traffic
[ ] Stakeholder approval obtained

Decommissioning Steps:
[ ] Create final backup of legacy data
[ ] Archive legacy code in version control
[ ] Document legacy business logic
[ ] Remove legacy service from load balancer
[ ] Disable legacy database connections
[ ] Archive legacy data to cold storage
[ ] Update documentation
[ ] Notify stakeholders of completion

Post-Decommission:
[ ] Monitor for any residual legacy calls
[ ] Verify cost savings realized
[ ] Update disaster recovery plans
[ ] Celebrate success! 🎉
```

### Best Practices

**1. Start Small**
- Begin with least critical, loosely coupled components
- Build expertise and confidence
- Establish patterns and practices

**2. Maintain Both Systems**
- Keep legacy system operational throughout
- Implement robust monitoring for both
- Plan for gradual traffic shifting

**3. Feature Flags**
- Enable quick rollback
- Support A/B testing
- Allow gradual rollout
- Reduce deployment risk

**4. Anti-Corruption Layer**
- Translate between legacy and modern data models
- Prevent legacy patterns from polluting new code
- Maintain clean architecture

```java
// Anti-Corruption Layer example
@Service
public class LegacyUserAdapter implements UserRepository {

    @Autowired
    private LegacySystemClient legacyClient;

    @Override
    public Optional<User> findById(Long id) {
        // Call legacy system
        LegacyUserDTO legacyUser = legacyClient.getUser(id);

        if (legacyUser == null) {
            return Optional.empty();
        }

        // Translate to modern domain model
        User modernUser = new User();
        modernUser.setId(legacyUser.getUserId());
        modernUser.setEmail(legacyUser.getEmailAddress());
        modernUser.setFullName(legacyUser.getFirstName() + " " + legacyUser.getLastName());
        modernUser.setCreatedAt(parseDate(legacyUser.getCreateDate()));

        return Optional.of(modernUser);
    }
}
```

**5. Comprehensive Testing**
- Contract testing between services
- Integration testing across systems
- Performance testing
- Chaos engineering

## Parallel Run Pattern

### Concept

Run both legacy and modern systems simultaneously, processing the same inputs and comparing outputs to validate correctness before cutover.

### Architecture

```
┌────────────────┐
│  Load Balancer │
└───────┬────────┘
        │
    ┌───▼────────────────┐
    │   Traffic Splitter  │
    └───┬──────────┬─────┘
        │          │
   ┌────▼──┐  ┌───▼────┐
   │Legacy │  │ Modern │
   │System │  │ System │
   └───┬───┘  └───┬────┘
       │          │
       └────┬─────┘
            │
    ┌───────▼────────┐
    │    Comparator   │
    │  (Results       │
    │   Validation)   │
    └────────────────┘
```

### Implementation

**Step 1: Traffic Duplication**

```python
# Flask example with request duplication
from flask import Flask, request
import requests
import threading

app = Flask(__name__)

def send_to_modern(request_data):
    try:
        response = requests.post(
            'http://modern-service/api/endpoint',
            json=request_data,
            timeout=5
        )
        return response.json()
    except Exception as e:
        print(f"Modern service error: {e}")
        return None

@app.route('/api/orders', methods=['POST'])
def create_order():
    request_data = request.get_json()

    # Primary: Call legacy system (synchronous)
    legacy_response = call_legacy_system(request_data)

    # Secondary: Call modern system (asynchronous)
    thread = threading.Thread(
        target=send_to_modern,
        args=(request_data,)
    )
    thread.start()

    # Return legacy response to user
    return legacy_response
```

**Step 2: Response Comparison**

```python
class ResponseComparator:
    def __init__(self):
        self.differences = []

    def compare_responses(self, legacy_response, modern_response):
        comparison = {
            'timestamp': datetime.now(),
            'matches': True,
            'differences': []
        }

        # Compare status codes
        if legacy_response.status != modern_response.status:
            comparison['matches'] = False
            comparison['differences'].append({
                'field': 'status_code',
                'legacy': legacy_response.status,
                'modern': modern_response.status
            })

        # Compare response bodies
        legacy_data = legacy_response.json()
        modern_data = modern_response.json()

        for key in legacy_data.keys():
            if key not in modern_data:
                comparison['matches'] = False
                comparison['differences'].append({
                    'field': key,
                    'legacy': legacy_data[key],
                    'modern': 'MISSING'
                })
            elif legacy_data[key] != modern_data[key]:
                # Allow for acceptable differences
                if not self.is_acceptable_difference(key, legacy_data[key], modern_data[key]):
                    comparison['matches'] = False
                    comparison['differences'].append({
                        'field': key,
                        'legacy': legacy_data[key],
                        'modern': modern_data[key]
                    })

        # Store for analysis
        self.store_comparison(comparison)

        return comparison

    def is_acceptable_difference(self, field, legacy_value, modern_value):
        # Define acceptable differences
        acceptable = {
            'timestamp': lambda l, m: abs(l - m) < 1000,  # 1 second tolerance
            'formatted_price': lambda l, m: float(l.replace('$', '')) == float(m.replace('$', ''))
        }

        if field in acceptable:
            return acceptable[field](legacy_value, modern_value)

        return False

    def generate_report(self):
        total = len(self.differences)
        matches = sum(1 for d in self.differences if d['matches'])

        return {
            'total_comparisons': total,
            'matches': matches,
            'match_rate': (matches / total * 100) if total > 0 else 0,
            'differences': [d for d in self.differences if not d['matches']]
        }
```

**Step 3: Monitoring and Analysis**

```python
# Metrics collection for parallel run
class ParallelRunMetrics:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')

    def record_comparison(self, matches, response_time_diff):
        # Record match/mismatch
        self.cloudwatch.put_metric_data(
            Namespace='ParallelRun',
            MetricData=[
                {
                    'MetricName': 'ResponseMatch',
                    'Value': 1 if matches else 0,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'ResponseTimeDifference',
                    'Value': response_time_diff,
                    'Unit': 'Milliseconds'
                }
            ]
        )

    def get_match_rate(self, hours=24):
        response = self.cloudwatch.get_metric_statistics(
            Namespace='ParallelRun',
            MetricName='ResponseMatch',
            StartTime=datetime.now() - timedelta(hours=hours),
            EndTime=datetime.now(),
            Period=3600,  # 1 hour
            Statistics=['Average']
        )

        if response['Datapoints']:
            return sum(d['Average'] for d in response['Datapoints']) / len(response['Datapoints']) * 100
        return 0
```

### Cutover Decision Criteria

```python
class CutoverDecision:
    def __init__(self):
        self.metrics = ParallelRunMetrics()

    def can_cutover(self):
        criteria = {
            'match_rate': self.metrics.get_match_rate() >= 99.9,  # 99.9% match rate
            'duration': self.get_parallel_run_duration() >= 14,   # 2 weeks minimum
            'error_rate': self.get_modern_error_rate() < 0.1,     # <0.1% error rate
            'performance': self.get_performance_comparison() <= 1.2, # Within 20%
            'load_test': self.load_test_passed(),
            'stakeholder_approval': self.get_stakeholder_approval()
        }

        all_passed = all(criteria.values())

        return {
            'can_cutover': all_passed,
            'criteria': criteria,
            'recommendation': self.get_recommendation(criteria)
        }

    def get_recommendation(self, criteria):
        if all(criteria.values()):
            return "Ready for cutover. All criteria met."

        failed = [k for k, v in criteria.items() if not v]
        return f"Not ready. Failed criteria: {', '.join(failed)}"
```

## Phased Migration Pattern

### Concept

Migrate application functionality in deliberate phases, with each phase representing a complete, functional subset that can be independently deployed and validated.

### Migration Phases

#### Phase 1: Read Operations

**Rationale**: Lowest risk, no data integrity concerns

```
Legacy System (Read + Write)
    ↓
Phase 1: Modern System (Read Only)
    ├─ Serve read traffic
    └─ Validate against legacy

Data Flow:
Modern Read → Modern DB (Read Replica of Legacy)
Writes → Legacy System → Replicated to Modern
```

**Implementation**:
```java
@Service
public class ProductService {

    @Autowired
    private LegacyProductClient legacyClient;

    @Autowired
    private ModernProductRepository modernRepo;

    @Value("${feature.modern-read.enabled}")
    private boolean modernReadEnabled;

    public Product getProduct(Long id) {
        if (modernReadEnabled) {
            // Use modern database for reads
            Optional<Product> product = modernRepo.findById(id);

            if (product.isPresent()) {
                // Validation: compare with legacy
                Product legacyProduct = legacyClient.getProduct(id);
                validateConsistency(product.get(), legacyProduct);

                return product.get();
            }
        }

        // Fallback to legacy
        return legacyClient.getProduct(id);
    }

    private void validateConsistency(Product modern, Product legacy) {
        if (!modern.equals(legacy)) {
            log.warn("Data inconsistency detected for product {}", modern.getId());
            metrics.recordInconsistency();
        }
    }
}
```

#### Phase 2: Write Operations

**Rationale**: After read validation, migrate writes

```
Dual Write Phase:
Application
    ├─ Write to Legacy (Primary)
    └─ Write to Modern (Secondary)

Validation:
- Compare write results
- Verify data synchronization
- Monitor for conflicts

After Validation:
Application
    ├─ Write to Modern (Primary)
    └─ Write to Legacy (Secondary, for rollback)
```

**Implementation**:
```java
@Service
public class OrderService {

    @Autowired
    private LegacyOrderClient legacyClient;

    @Autowired
    private ModernOrderRepository modernRepo;

    @Value("${migration.phase}")
    private String migrationPhase;

    @Transactional
    public Order createOrder(CreateOrderRequest request) {
        Order order;

        switch (migrationPhase) {
            case "DUAL_WRITE":
                // Write to both systems
                Order legacyOrder = legacyClient.createOrder(request);
                Order modernOrder = createModernOrder(request);

                // Validate consistency
                validateOrders(legacyOrder, modernOrder);

                // Return legacy as source of truth
                order = legacyOrder;
                break;

            case "MODERN_PRIMARY":
                // Write to modern first
                order = createModernOrder(request);

                // Async write to legacy for safety
                CompletableFuture.runAsync(() ->
                    legacyClient.createOrder(request)
                );
                break;

            case "MODERN_ONLY":
                // Modern system only
                order = createModernOrder(request);
                break;

            default:
                // Legacy only
                order = legacyClient.createOrder(request);
        }

        return order;
    }

    private Order createModernOrder(CreateOrderRequest request) {
        Order order = new Order();
        order.setCustomerId(request.getCustomerId());
        order.setItems(request.getItems());
        order.setTotal(calculateTotal(request.getItems()));
        order.setStatus(OrderStatus.PENDING);

        return modernRepo.save(order);
    }
}
```

#### Phase 3: Complex Operations

**Rationale**: Migrate complex business logic after basic operations proven

```
Complex Operations:
- Multi-step workflows
- Batch processing
- Report generation
- Integration points

Strategy:
1. Reimplement in modern system
2. Run parallel comparison
3. Gradual cutover by use case
4. Monitor and optimize
```

#### Phase 4: Decommission Legacy

**Final Phase Checklist**:
```
[ ] All operations migrated to modern system
[ ] 30+ days of successful modern operation
[ ] Zero critical incidents
[ ] Performance meeting or exceeding SLAs
[ ] Cost savings validated
[ ] Disaster recovery tested
[ ] Stakeholder approval
[ ] Decommission plan approved
[ ] Data archived
[ ] Legacy system removed
```

### Phase Management

**Phase Governance**:
```python
class MigrationPhaseManager:
    def __init__(self):
        self.phases = {
            'LEGACY_ONLY': {
                'read': 'legacy',
                'write': 'legacy',
                'complete': False
            },
            'READ_MIGRATION': {
                'read': 'modern',
                'write': 'legacy',
                'entry_criteria': self.can_start_read_migration,
                'exit_criteria': self.can_complete_read_migration
            },
            'DUAL_WRITE': {
                'read': 'modern',
                'write': 'both',
                'entry_criteria': self.can_start_dual_write,
                'exit_criteria': self.can_complete_dual_write
            },
            'MODERN_PRIMARY': {
                'read': 'modern',
                'write': 'modern_primary',
                'entry_criteria': self.can_make_modern_primary,
                'exit_criteria': self.can_complete_modern_primary
            },
            'MODERN_ONLY': {
                'read': 'modern',
                'write': 'modern',
                'entry_criteria': self.can_go_modern_only,
                'complete': True
            }
        }

    def can_start_read_migration(self):
        return (
            self.data_sync_complete() and
            self.read_replica_lag() < 1 and
            self.stakeholder_approval('read_migration')
        )

    def can_complete_read_migration(self):
        return (
            self.read_consistency_rate() >= 99.9 and
            self.duration_in_phase() >= 7  # days
        )

    def can_start_dual_write(self):
        return (
            self.read_migration_successful() and
            self.write_test_complete() and
            self.stakeholder_approval('dual_write')
        )

    # ... additional criteria methods
```

## Containerization Strategy

### Container Benefits for Legacy Applications

**Operational Benefits**:
- Consistent environments (dev, test, prod)
- Simplified deployment
- Resource efficiency
- Rapid scaling
- Infrastructure portability

**Modernization Benefits**:
- Foundation for microservices
- Cloud-native deployment
- Orchestration with Kubernetes
- DevOps enablement

### Containerization Approaches

#### Approach 1: Lift and Shift to Containers

**Process**:
```
Legacy Application
    ↓
1. Analyze dependencies
2. Create Dockerfile
3. Build container image
4. Test locally
5. Deploy to container platform
```

**Example: Java Application**

```dockerfile
# Dockerfile for legacy Java application
FROM openjdk:11-jre-slim

# Set working directory
WORKDIR /app

# Copy application JAR
COPY target/legacy-app.war /app/app.war

# Copy configuration
COPY config/ /app/config/

# Set environment variables
ENV JAVA_OPTS="-Xmx2g -Xms1g"
ENV APP_CONFIG=/app/config/application.properties

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.war"]
```

**Kubernetes Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legacy-app
  labels:
    app: legacy-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: legacy-app
  template:
    metadata:
      labels:
        app: legacy-app
    spec:
      containers:
      - name: legacy-app
        image: myregistry/legacy-app:1.0
        ports:
        - containerPort: 8080
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: db.host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: db.password
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: legacy-app-service
spec:
  selector:
    app: legacy-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

#### Approach 2: Decompose During Containerization

**Strategy**: Extract components into separate containers during containerization

```
Monolithic Application
    ↓
Analyze Components:
    ├─ Web Frontend → Container 1
    ├─ API Layer → Container 2
    ├─ Background Jobs → Container 3
    └─ Database → Managed Service (RDS, etc.)
```

**Docker Compose Example**:
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - api
    environment:
      - API_URL=http://api:8080

  api:
    build: ./api
    ports:
      - "8080:8080"
    depends_on:
      - database
      - redis
    environment:
      - DB_HOST=database
      - REDIS_HOST=redis
    secrets:
      - db_password

  worker:
    build: ./worker
    depends_on:
      - database
      - redis
    environment:
      - DB_HOST=database
      - REDIS_HOST=redis
    secrets:
      - db_password

  database:
    image: postgres:14
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  db_data:
  redis_data:

secrets:
  db_password:
    external: true
```

### Migration to Kubernetes

**Step 1: Containerize Application**
```bash
# Build Docker image
docker build -t legacy-app:1.0 .

# Test locally
docker run -p 8080:8080 legacy-app:1.0

# Push to container registry
docker tag legacy-app:1.0 myregistry.azurecr.io/legacy-app:1.0
docker push myregistry.azurecr.io/legacy-app:1.0
```

**Step 2: Create Kubernetes Manifests**
```bash
# Create namespace
kubectl create namespace legacy-app

# Create ConfigMaps and Secrets
kubectl create configmap app-config \
    --from-file=config/application.properties \
    -n legacy-app

kubectl create secret generic app-secrets \
    --from-literal=db.password=secretpassword \
    -n legacy-app

# Apply deployments
kubectl apply -f k8s/deployment.yaml -n legacy-app
kubectl apply -f k8s/service.yaml -n legacy-app
```

**Step 3: Implement Service Mesh (Optional)**
```yaml
# Istio VirtualService for canary deployment
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: legacy-app-vs
spec:
  hosts:
  - legacy-app.example.com
  http:
  - match:
    - headers:
        user-agent:
          regex: ".*mobile.*"
    route:
    - destination:
        host: legacy-app-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: legacy-app-service
        subset: v1
      weight: 90
    - destination:
        host: legacy-app-service
        subset: v2
      weight: 10
```

**Step 4: Implement CI/CD**
```yaml
# GitLab CI/CD pipeline example
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_REGISTRY: myregistry.azurecr.io
  IMAGE_NAME: legacy-app

build:
  stage: build
  script:
    - docker build -t $DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA .
    - docker push $DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA

test:
  stage: test
  script:
    - docker run $DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA ./run-tests.sh

deploy-staging:
  stage: deploy
  script:
    - kubectl set image deployment/legacy-app \
        legacy-app=$DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA \
        -n staging
    - kubectl rollout status deployment/legacy-app -n staging
  environment:
    name: staging

deploy-production:
  stage: deploy
  script:
    - kubectl set image deployment/legacy-app \
        legacy-app=$DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA \
        -n production
    - kubectl rollout status deployment/legacy-app -n production
  environment:
    name: production
  when: manual
  only:
    - main
```

## Risk Mitigation

### Risk Categories

#### 1. Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Service integration failure | High | Medium | Contract testing, integration tests, circuit breakers |
| Data inconsistency | Critical | Medium | Dual writes, validation, reconciliation |
| Performance degradation | High | Medium | Load testing, monitoring, optimization |
| Downtime during cutover | High | Low | Blue/green deployment, feature flags |
| Security vulnerabilities | Critical | Low | Security scanning, penetration testing |

**Mitigation Strategies**:

```python
# Circuit breaker pattern for service calls
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_modern_service(request):
    try:
        response = requests.post(
            'http://modern-service/api/endpoint',
            json=request,
            timeout=3
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log.error(f"Modern service call failed: {e}")
        # Circuit breaker will open after threshold
        raise

def process_request_with_fallback(request):
    try:
        return call_modern_service(request)
    except CircuitBreakerError:
        log.warn("Circuit breaker open, falling back to legacy")
        return call_legacy_service(request)
```

#### 2. Business Risks

**User Impact**:
```python
class UserImpactMinimization:
    def __init__(self):
        self.rollout_strategy = 'gradual'

    def deploy_new_version(self, version):
        if self.rollout_strategy == 'gradual':
            # Canary deployment
            self.deploy_to_subset(version, percentage=5)
            self.monitor(duration=timedelta(hours=2))

            if self.metrics_acceptable():
                self.deploy_to_subset(version, percentage=25)
                self.monitor(duration=timedelta(hours=4))

                if self.metrics_acceptable():
                    self.deploy_to_all(version)
            else:
                self.rollback()

    def metrics_acceptable(self):
        return (
            self.get_error_rate() < 0.1 and
            self.get_latency_p99() < 500 and
            self.get_user_satisfaction() > 95
        )
```

### Monitoring and Observability

**Comprehensive Monitoring Setup**:

```yaml
# Prometheus monitoring configuration
scrape_configs:
  - job_name: 'legacy-app'
    static_configs:
      - targets: ['legacy-app:8080']
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'legacy_(.*)'
        target_label: system
        replacement: 'legacy'

  - job_name: 'modern-app'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: modern-app
        action: keep
```

**Alerting Rules**:
```yaml
# Prometheus alerting rules
groups:
  - name: migration_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: ResponseTimeDegradation
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Response time degradation"
          description: "P99 latency is {{ $value }}s"

      - alert: DataInconsistency
        expr: data_comparison_mismatches_total > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Data inconsistency detected"
          description: "{{ $value }} mismatches in last 5 minutes"
```

## Rollback Plans

### Rollback Strategies by Pattern

#### Strangler Fig Rollback

**Scenario**: Modern service experiencing issues

```python
def rollback_strangler_fig():
    """
    Rollback by routing all traffic back to legacy system
    """
    steps = [
        {
            'action': 'update_routing',
            'description': 'Route 100% traffic to legacy',
            'duration_minutes': 2,
            'function': lambda: update_api_gateway_routing(legacy=100, modern=0)
        },
        {
            'action': 'disable_modern_writes',
            'description': 'Prevent data corruption in modern system',
            'duration_minutes': 1,
            'function': lambda: set_modern_system_readonly()
        },
        {
            'action': 'validate_legacy',
            'description': 'Verify legacy system handling traffic',
            'duration_minutes': 5,
            'function': lambda: validate_legacy_metrics()
        },
        {
            'action': 'pause_migration',
            'description': 'Halt further migration activities',
            'duration_minutes': 1,
            'function': lambda: pause_migration_jobs()
        },
        {
            'action': 'analyze_issue',
            'description': 'Root cause analysis',
            'duration_minutes': 30,
            'function': lambda: analyze_modern_system_logs()
        }
    ]

    for step in steps:
        print(f"Executing: {step['description']}")
        try:
            step['function']()
            print(f"✓ Completed in ~{step['duration_minutes']} minutes")
        except Exception as e:
            print(f"✗ Failed: {e}")
            raise RollbackException(f"Rollback failed at step: {step['action']}")

    print("Rollback completed successfully")
```

#### Parallel Run Rollback

**Scenario**: Need to stop modern system validation

```python
def rollback_parallel_run():
    """
    Stop sending traffic to modern system for comparison
    """
    # Simply disable the traffic duplication
    feature_flags.set('parallel_run.enabled', False)

    # Continue operating on legacy only
    # No actual rollback needed as modern wasn't serving traffic

    # Clean up comparison jobs
    stop_comparison_workers()

    # Archive comparison data for analysis
    archive_comparison_results()

    print("Parallel run stopped. Operating on legacy system only.")
```

#### Phased Migration Rollback

**Scenario**: Issues during dual-write phase

```python
def rollback_phased_migration(current_phase):
    """
    Rollback to previous migration phase
    """
    phase_rollbacks = {
        'DUAL_WRITE': rollback_to_legacy_write,
        'MODERN_PRIMARY': rollback_to_dual_write,
        'MODERN_ONLY': rollback_to_modern_primary
    }

    if current_phase in phase_rollbacks:
        rollback_function = phase_rollbacks[current_phase]
        rollback_function()
    else:
        raise ValueError(f"Unknown phase: {current_phase}")

def rollback_to_legacy_write():
    # Set configuration to write only to legacy
    update_config('migration.phase', 'READ_MIGRATION')

    # Stop writes to modern system
    disable_modern_writes()

    # Validate legacy write functionality
    validate_legacy_writes()

    # Reconcile any data written to modern during dual-write
    schedule_data_reconciliation()

def rollback_to_dual_write():
    # Revert from modern-primary to dual-write
    update_config('migration.phase', 'DUAL_WRITE')

    # Re-enable writes to legacy as primary
    enable_legacy_writes(primary=True)

    # Keep modern writes for validation
    enable_modern_writes(primary=False)
```

#### Containerization Rollback

**Scenario**: Issues with containerized application

```bash
#!/bin/bash
# Kubernetes rollback script

# Rollback to previous deployment
kubectl rollout undo deployment/legacy-app -n production

# Monitor rollback progress
kubectl rollout status deployment/legacy-app -n production

# Verify pods are healthy
kubectl get pods -n production -l app=legacy-app

# Check logs for errors
kubectl logs -n production -l app=legacy-app --tail=100

# If rollback successful
if [ $? -eq 0 ]; then
    echo "Rollback completed successfully"

    # Update incident tracking
    ./notify-team.sh "Rollback to previous version completed"

    # Schedule post-mortem
    ./schedule-postmortem.sh
else
    echo "Rollback failed! Manual intervention required"
    ./alert-oncall.sh "CRITICAL: Rollback failed"
fi
```

### Rollback Testing

**Rollback Rehearsal Checklist**:
```
Pre-Migration:
[ ] Document rollback procedures
[ ] Test rollback in staging environment
[ ] Verify backup/snapshot procedures
[ ] Define rollback decision criteria
[ ] Assign rollback decision makers
[ ] Test communication channels

During Migration:
[ ] Monitor key metrics continuously
[ ] Have rollback team on standby
[ ] Maintain go/no-go checkpoints
[ ] Document any deviations from plan

Post-Migration:
[ ] Maintain rollback capability for 30 days
[ ] Document lessons learned
[ ] Update rollback procedures
[ ] Archive migration artifacts
```

## Case Studies

### Case Study 1: E-commerce Platform - Strangler Fig Migration

**Background**:
- 15-year-old monolithic PHP application
- 2M lines of code
- 10M daily page views
- LAMP stack (Linux, Apache, MySQL, PHP)

**Modernization Goals**:
- Adopt microservices architecture
- Move to cloud (AWS)
- Improve deployment frequency
- Enable A/B testing

**Strategy**: Strangler Fig Pattern over 24 months

**Implementation Timeline**:

```
Month 1-3: Foundation
- Deployed API Gateway (AWS API Gateway)
- Established CI/CD pipeline
- Set up monitoring (DataDog)
- Created development standards

Month 4-6: First Service (Product Catalog)
- Extracted product catalog to Node.js microservice
- Deployed to ECS Fargate
- Routed 10% traffic through new service
- Parallel validation against legacy

Month 7-12: Core Services
- User service (authentication, profiles)
- Shopping cart service
- Order service
- Payment service (integrated Stripe)
Each service: 2-month development, 1-month validation

Month 13-18: Complex Features
- Recommendation engine (Python, ML)
- Search service (Elasticsearch)
- Inventory management
- Promotions engine

Month 19-24: Final Migration
- Remaining features migrated
- Legacy monolith decommissioned
- Database decomposition completed
- Full cloud-native operation
```

**Technical Details**:

```
Architecture Evolution:

Initial:
┌─────────────────┐
│ PHP Monolith    │
│ (All features)  │
└─────────────────┘
        │
    ┌───▼───┐
    │ MySQL │
    └───────┘

After 12 months:
┌──────────────┐
│ API Gateway  │
└──┬────────┬──┘
   │        │
┌──▼──┐  ┌──▼──────────┐
│Micro│  │ PHP Legacy  │
│Svc  │  │ (Remaining) │
└──┬──┘  └──────┬──────┘
   │            │
┌──▼──┐    ┌───▼────┐
│NoSQL│    │ MySQL  │
└─────┘    └────────┘

Final:
┌───────────────────┐
│   API Gateway     │
└─┬──┬──┬──┬──┬──┬──┘
  │  │  │  │  │  │
┌─▼┐┌▼┐┌▼┐┌▼┐┌▼┐┌▼┐
│S1││S2││S3││S4││S5││S6│ (Microservices)
└──┘└──┘└──┘└──┘└──┘└──┘
  │  │  │  │  │  │
┌─▼──▼──▼──▼──▼──▼─┐
│ Distributed DBs  │
└──────────────────┘
```

**Results**:
- Deployment frequency: Monthly → Multiple times daily
- Page load time: 3.2s → 1.1s (66% improvement)
- Infrastructure cost: -40% (cloud optimizations)
- Developer productivity: +200% (parallel development)
- Zero major outages during migration
- Successfully processed Black Friday (peak traffic) mid-migration

**Key Success Factors**:
- Strong executive support
- Incremental approach reduced risk
- Comprehensive monitoring enabled confidence
- Feature flags allowed gradual rollout
- Regular communication with stakeholders

### Case Study 2: Financial Services - Parallel Run Migration

**Background**:
- Core banking transaction processing
- COBOL mainframe application
- 50M transactions per day
- 99.99% uptime requirement
- Regulatory constraints

**Modernization Goals**:
- Reduce mainframe costs
- Modernize technology stack
- Enable real-time analytics
- Improve disaster recovery

**Strategy**: Parallel Run with Java Rewrite

**Implementation**:

```
Phase 1: Rewrite in Java (9 months)
- Analyzed COBOL business logic
- Designed modern Java application
- Spring Boot microservices
- Event-driven architecture (Kafka)
- Deployed to Kubernetes (on-premises initially)

Phase 2: Parallel Run (6 months)
- Duplicated transaction traffic
- Both systems processed every transaction
- Compared results transaction-by-transaction
- Monitored for discrepancies

Phase 3: Gradual Cutover (3 months)
- Started with non-critical transaction types
- Gradual increase based on confidence
- Maintained parallel run for critical transactions
- Final cutover after 99.99% match rate

Phase 4: Decommission (3 months)
- Maintained mainframe as backup
- Gradually reduced mainframe capacity
- Final decommission after 90-day success period
```

**Comparison Results**:

| Metric | Mainframe | Java System | Improvement |
|--------|-----------|-------------|-------------|
| Transaction Processing | 50M/day | 50M/day | Same |
| Response Time (P99) | 250ms | 120ms | 52% faster |
| Match Rate | N/A | 99.997% | High confidence |
| Cost | $5M/year | $2M/year | 60% reduction |
| Availability | 99.99% | 99.995% | Improved |

**Challenges Overcome**:
- Floating-point precision differences
- Time zone handling variations
- Rounding differences in calculations
- Transaction ordering in edge cases
- Performance optimization needed for peak loads

**Results**:
- Successful migration with zero customer impact
- Regulatory approval maintained
- $3M annual cost savings
- Real-time analytics enabled
- Improved disaster recovery (RTO: 24h → 1h)

### Case Study 3: SaaS Platform - Containerization First

**Background**:
- Multi-tenant SaaS platform
- .NET Framework monolith
- 500 enterprise customers
- Deployed to Windows VMs
- Manual deployment process (2-week cycle)

**Modernization Goals**:
- Adopt containers and Kubernetes
- Enable continuous deployment
- Improve resource utilization
- Multi-cloud capability

**Strategy**: Containerize first, then decompose

**Implementation**:

```
Phase 1: Containerize Monolith (2 months)
- Created Dockerfile for .NET app
- Migrated SQL Server to Azure SQL
- Deployed to Azure Kubernetes Service
- Maintained feature parity

Phase 2: Extract Read APIs (3 months)
- Created separate containers for read operations
- Implemented caching layer (Redis)
- Reduced database load
- Improved performance

Phase 3: Extract Background Jobs (2 months)
- Separated job processing into own containers
- Implemented job queue (RabbitMQ)
- Auto-scaling for job processors
- Better resource utilization

Phase 4: Decompose Core (9 months)
- Gradually extracted microservices
- Tenant management
- Billing service
- Notification service
- Remained on same Kubernetes cluster

Phase 5: Multi-Cloud (3 months)
- Deployed to both Azure and AWS
- Geographic distribution
- Improved disaster recovery
```

**Technology Stack Evolution**:

```
Before:
- Windows Server VMs
- .NET Framework 4.8
- SQL Server on VMs
- Manual deployment
- No auto-scaling

After:
- Kubernetes (AKS + EKS)
- .NET Core containers
- Azure SQL + RDS
- GitOps deployment (ArgoCD)
- Auto-scaling (HPA)
```

**Results**:
- Deployment frequency: Bi-weekly → Daily
- Deployment time: 4 hours → 15 minutes
- Infrastructure cost: -50% (better utilization)
- Incident response: Faster rollback capability
- Resource utilization: 30% → 70%
- Multi-region deployment enabled

**Lessons Learned**:
- Containerizing first provided quick wins
- Kubernetes learning curve significant
- Incremental decomposition reduced risk
- Service mesh added complexity but valuable
- Auto-scaling required careful tuning

## Tool Recommendations

### Migration Planning

**1. AWS Migration Hub**
- Purpose: Track migration progress
- Features: Application discovery, migration tracking
- Best For: AWS migrations

**2. Azure Migrate**
- Purpose: Assessment and migration platform
- Features: Dependency mapping, TCO calculation
- Best For: Azure migrations

**3. Apptio Cloudability / CloudHealth**
- Purpose: Cost optimization and tracking
- Features: Cost allocation, optimization recommendations
- Best For: Multi-cloud cost management

### Service Mesh and API Gateway

**4. Kong Gateway**
- Purpose: API Gateway for strangler fig
- Features: Routing, authentication, rate limiting
- Best For: Hybrid deployments

**5. Istio**
- Purpose: Service mesh for microservices
- Features: Traffic management, security, observability
- Best For: Kubernetes environments

**6. AWS App Mesh / Azure Service Fabric Mesh**
- Purpose: Cloud-native service mesh
- Features: Traffic routing, observability, security
- Best For: Cloud-specific deployments

### Containerization

**7. Docker**
- Purpose: Container platform
- Features: Build, ship, run containers
- Best For: Application containerization

**8. Kubernetes**
- Purpose: Container orchestration
- Features: Auto-scaling, self-healing, rolling updates
- Best For: Production container management

**9. Helm**
- Purpose: Kubernetes package manager
- Features: Templating, versioning, rollback
- Best For: Kubernetes application deployment

**10. Terraform / Pulumi**
- Purpose: Infrastructure as Code
- Features: Multi-cloud, state management
- Best For: Infrastructure provisioning

### Monitoring and Observability

**11. Datadog / New Relic**
- Purpose: APM and infrastructure monitoring
- Features: Distributed tracing, metrics, logs
- Best For: Comprehensive observability

**12. Prometheus + Grafana**
- Purpose: Metrics and visualization
- Features: Time-series database, alerting, dashboards
- Best For: Kubernetes monitoring

**13. ELK Stack (Elasticsearch, Logstash, Kibana)**
- Purpose: Log aggregation and analysis
- Features: Centralized logging, search, visualization
- Best For: Log management

### Testing

**14. Pact**
- Purpose: Contract testing
- Features: Consumer-driven contracts
- Best For: Microservices integration testing

**15. JMeter / Gatling**
- Purpose: Performance testing
- Features: Load testing, stress testing
- Best For: Performance validation

**16. Chaos Monkey / Gremlin**
- Purpose: Chaos engineering
- Features: Fault injection, resilience testing
- Best For: Reliability validation

## Conclusion

Successful application modernization requires:

**Strategic Approach**:
- Clear business objectives
- Appropriate pattern selection
- Incremental migration strategy
- Risk-based prioritization

**Technical Excellence**:
- Comprehensive testing
- Robust monitoring
- Automated deployment
- Security best practices

**Risk Management**:
- Gradual rollout strategies
- Comprehensive rollback plans
- Continuous validation
- Clear decision criteria

**Organizational Alignment**:
- Executive sponsorship
- Cross-team collaboration
- Skills development
- Change management

The patterns described—Strangler Fig, Parallel Run, Phased Migration, and Containerization—provide proven approaches to modernizing legacy applications while minimizing risk and maintaining business continuity. Success depends on selecting the appropriate pattern for your specific circumstances, executing with discipline, and maintaining focus on delivering business value throughout the journey.
