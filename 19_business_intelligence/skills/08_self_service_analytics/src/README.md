# Self-Service Analytics - Source Implementations

This directory contains production-ready source code and configurations for the Self-Service Analytics platform. These implementations support the strategy and architecture described in the parent skill documentation.

## Overview

These files provide the technical foundation for deploying self-service analytics capabilities at scale:

- **APIs & Services**: REST APIs for metrics management, data discovery, and platform operations
- **Data Integration**: Catalog synchronization across multiple data sources and platforms
- **Monitoring & Governance**: SQL views for comprehensive dashboards and compliance tracking
- **Configuration**: Alert rules, thresholds, and escalation policies

## File Descriptions

### 1. `08_metrics_api.py` - Production Metrics Management API

**Purpose**: RESTful API for metric definitions, validation, and lifecycle management

**Key Components**:
- `MetricDefinition`: Database model for versioned metric storage
- `MetricValidator`: Syntax and compatibility checking
- `FastAPI Application`: Production-grade REST endpoints
- `MetricAuditLog`: Complete audit trail for compliance

**Endpoints**:
- `POST /api/v1/metrics` - Create new metric definition
- `GET /api/v1/metrics` - List metrics with filtering/pagination
- `GET /api/v1/metrics/{metric_name}` - Retrieve specific metric version
- `POST /api/v1/metrics/{metric_name}/validate` - Pre-publication validation
- `GET /api/v1/metrics/{metric_name}/usage` - Usage statistics
- `POST /api/v1/metrics/{metric_name}/deprecate` - Mark metric as deprecated
- `GET /api/v1/metrics/search` - Full-text search

**Features**:
- Metric versioning and content hashing
- SQL injection prevention and expression validation
- Dependency tracking and lineage
- Usage analytics and performance metrics
- Complete audit trail for regulatory compliance

**Database Requirements**:
- SQLAlchemy ORM with PostgreSQL/MySQL/Snowflake
- Tables: `metric_definitions`, `metric_usage`, `metric_audit_log`

**Dependencies**:
```
fastapi>=0.95.0
pydantic>=1.10.0
sqlalchemy>=2.0.0
structlog>=22.3.0
redis>=4.5.0
```

**Example Usage**:
```python
# Create a metric
curl -X POST http://localhost:8000/api/v1/metrics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token" \
  -d '{
    "metric_name": "monthly_active_users",
    "label": "Monthly Active Users",
    "description": "Count of unique users with activity in the month",
    "model": "ref(fct_user_events)",
    "calculation_method": "count_distinct",
    "expression": "user_id",
    "timestamp": "event_timestamp",
    "owner": "product_analytics_team"
  }'

# Search metrics
curl http://localhost:8000/api/v1/metrics/search?q=revenue&limit=10

# Get usage statistics
curl http://localhost:8000/api/v1/metrics/monthly_recurring_revenue/usage?days=30
```

---

### 2. `09_data_catalog_sync.py` - Multi-Catalog Metadata Synchronization

**Purpose**: Synchronize metadata across data sources and catalog platforms

**Key Components**:
- `DataAsset`: Universal representation of data assets
- `DataSourceAdapter`: Pluggable adapters for different data sources
- `SQLDatabaseAdapter`: Implementation for SQL databases
- `CatalogAdapter`: Interface for catalog platforms
- `AmundsenAdapter`: Implementation for Amundsen catalog
- `CatalogSyncEngine`: Main orchestration engine

**Supported Data Sources**:
- PostgreSQL, MySQL, Snowflake, BigQuery, Redshift, Hive, Spark, Kafka

**Supported Catalogs**:
- Amundsen (with pluggable support for DataHub, Alation, Collibra)

**Features**:
- Automatic schema discovery and reflection
- Column-level metadata extraction
- Usage pattern estimation
- Full and incremental sync modes
- Multi-catalog support with conflict resolution
- Comprehensive error handling and retry logic
- Audit logging for all operations

**Sync Job Tracking**:
- Job status monitoring (pending, in_progress, completed, failed, partial)
- Detailed metrics: created, updated, deleted asset counts
- Error collection and reporting
- Historical tracking

**Example Usage**:
```python
from data_catalog_sync import (
    CatalogSyncEngine,
    SQLDatabaseAdapter,
    AmundsenAdapter,
    DataSourceType
)

# Initialize engine
engine = CatalogSyncEngine(config)

# Register PostgreSQL as data source
pg_config = {
    "type": "postgres",
    "host": "analytics.company.com",
    "port": 5432,
    "user": "catalog_user",
    "password": "***",
    "database": "analytics_prod"
}
pg_adapter = SQLDatabaseAdapter(pg_config)
engine.register_data_source(DataSourceType.POSTGRES, pg_adapter)

# Register Amundsen as target catalog
amundsen_adapter = AmundsenAdapter("https://amundsen.company.com")
engine.register_catalog("amundsen", amundsen_adapter)

# Execute sync
job = engine.sync(
    source_types=[DataSourceType.POSTGRES],
    target_catalogs=["amundsen"]
)

print(f"Sync Status: {job.status.value}")
print(f"Processed: {job.processed_assets}/{job.total_assets}")
print(f"Errors: {job.errors}")
```

**Database Requirements**:
- Connection pooling configured for source databases
- Read-only credentials recommended for source access

**Dependencies**:
```
sqlalchemy>=2.0.0
requests>=2.28.0
tenacity>=8.2.0
structlog>=22.3.0
asyncio
```

---

### 3. `10_governance_dashboard.sql` - Governance Monitoring Views

**Purpose**: Production SQL views for comprehensive governance dashboard

**Key Views**:

#### `governance.access_control_audit`
Real-time access control audit with role status tracking
- User access grants by role and dataset
- Access expiration monitoring
- Role status classification (active, expiring_soon, expired)

#### `governance.data_classification_compliance`
Data classification and compliance status
- PII, PHI, PCI indicators
- Classification coverage metrics
- Compliance status assessment

#### `governance.user_activity_monitoring`
User activity patterns and risk detection
- Daily query volumes
- Export and sharing patterns
- Anomaly detection (unusual volumes, large result sets)
- Activity-based risk scoring

#### `governance.policy_violations`
Automated policy violation detection
- Excessive permission accumulation
- Expired role access
- Sensitive dataset access violations

#### `governance.data_lineage_impact`
Data lineage tracking with impact analysis
- Upstream and downstream dependencies
- Affected dataset counts
- User access through lineage paths

#### `governance.metrics_summary`
Aggregate compliance metrics
- Active users count
- Classification coverage
- Policy violations
- Activity trends

**Usage Examples**:
```sql
-- Check user access expiration
SELECT *
FROM governance.access_control_audit
WHERE role_status = 'expiring_soon'
ORDER BY expires_at;

-- Find policy violations
SELECT *
FROM governance.policy_violations
WHERE violation_status = 'OPEN'
ORDER BY detected_at DESC;

-- Analyze department access patterns
SELECT *
FROM governance.department_access_patterns
ORDER BY accessible_datasets DESC;

-- Get governance summary
SELECT * FROM governance.metrics_summary;
```

**Database Requirements**:
- Schema: `governance`, `iam`, `analytics`, `audit`
- Tables: `user_roles`, `users`, `roles`, `dataset_access_grants`, `datasets`,
  `dataset_classifications`, `columns`, `user_activity`, `data_lineage`, `audit_log`

**Index Recommendations**:
```sql
CREATE INDEX idx_user_roles_user_id ON iam.user_roles(user_id);
CREATE INDEX idx_user_roles_expires_at ON iam.user_roles(expires_at);
CREATE INDEX idx_dataset_access_dataset_id ON governance.dataset_access_grants(dataset_id);
CREATE INDEX idx_user_activity_user_id ON audit.user_activity(user_id);
CREATE INDEX idx_user_activity_timestamp ON audit.user_activity(activity_timestamp);
CREATE INDEX idx_data_lineage_source ON governance.data_lineage(source_dataset_id);
```

---

### 4. `11_self_service_metrics.sql` - Platform Adoption & Engagement Tracking

**Purpose**: Comprehensive SQL views for measuring self-service analytics success

**Key Views**:

#### `analytics.adoption_metrics`
User adoption cohorts and progression
- Activation status and days to first activity
- Adoption category (quick, steady, slow adopter)
- User tenure classification

#### `analytics.query_performance_metrics`
Query execution performance and efficiency
- Average, max, p95 execution times
- Cache hit rates
- Success/failure rates
- Performance grading

#### `analytics.dataset_utilization`
Dataset popularity and usage patterns
- Unique user counts
- Query volumes and trends
- Data extraction volumes
- Usage tier classification (critical, high_value, moderate, low_usage)

#### `analytics.engagement_funnel`
User engagement progression (exploration → creation → sharing)
- Exploration (queries, dashboard views)
- Creation (dashboards, saved queries)
- Sharing (shared artifacts)
- User segments (champion, creator, explorer, browser, inactive)
- Engagement scores

#### `analytics.business_impact_metrics`
Self-service vs analyst request trends
- Self-service user and query counts
- Analyst request volumes
- Self-service rate percentage
- Analyst time savings potential

#### `analytics.training_metrics`
Training program effectiveness
- Enrollment and completion rates
- Score trends
- Completion rates by training type
- Recent completions tracking

#### `analytics.support_metrics`
Support ticket resolution and satisfaction
- Ticket creation and resolution rates
- Average resolution time
- User satisfaction scores
- Resolution rate trending

#### `analytics.cohort_retention`
User retention by onboarding cohort
- Cohort sizes and month-over-month retention
- Retention curves for multiple cohorts
- Churn analysis

**Usage Examples**:
```sql
-- Monitor adoption by department
SELECT
  department,
  COUNT(*) as user_count,
  SUM(CASE WHEN adoption_category = 'QUICK_ADOPTER' THEN 1 ELSE 0 END) as quick_adopters,
  ROUND(SUM(CASE WHEN adoption_category = 'QUICK_ADOPTER' THEN 1 ELSE 0 END) * 100.0 /
        COUNT(*), 1) as quick_adoption_rate
FROM analytics.adoption_metrics
WHERE onboarding_date >= DATEADD(month, -3, CURRENT_DATE)
GROUP BY department
ORDER BY quick_adoption_rate DESC;

-- Track self-service impact
SELECT
  report_week,
  self_service_users,
  analyst_requests,
  ROUND(self_service_users * 100.0 /
        (self_service_users + analyst_requests), 1) as self_service_rate_pct
FROM analytics.business_impact_metrics
WHERE report_week >= DATEADD(month, -3, CURRENT_DATE)
ORDER BY report_week DESC;

-- Identify power users
SELECT
  user_id,
  email,
  department,
  lifetime_queries,
  user_segment,
  engagement_score
FROM analytics.engagement_funnel
WHERE engagement_score > 50
ORDER BY engagement_score DESC
LIMIT 20;

-- Analyze query performance
SELECT
  query_date,
  COUNT(DISTINCT user_id) as daily_users,
  SUM(daily_queries) as total_queries,
  AVG(avg_exec_time_ms) as avg_query_time_ms,
  COUNT(CASE WHEN performance_grade = 'GOOD' THEN 1 END) as good_performing_days
FROM analytics.query_performance_metrics
WHERE query_date >= DATEADD(day, -30, CURRENT_DATE)
GROUP BY query_date
ORDER BY query_date DESC;
```

**Database Requirements**:
- Schema: `analytics`, `iam`, `audit`, `training`, `support`
- Tables: `users`, `user_activity`, `datasets`, `analyst_requests`, `trainings`,
  `enrollments`, `tickets`

**Index Recommendations**:
```sql
CREATE INDEX idx_users_created_at ON iam.users(created_at);
CREATE INDEX idx_users_department ON iam.users(department);
CREATE INDEX idx_user_activity_user_id_timestamp ON audit.user_activity(user_id, activity_timestamp);
CREATE INDEX idx_user_activity_type ON audit.user_activity(activity_type);
CREATE INDEX idx_enrollments_user_id ON training.enrollments(user_id, completion_status);
CREATE INDEX idx_tickets_created_at ON support.tickets(created_at);
```

---

### 5. `12_alert_rules.yaml` - Monitoring & Alert Configuration

**Purpose**: Comprehensive production alert rules for platform health and governance

**Alert Categories**:

#### Performance & Health
- `query_performance_degradation` - Query execution time > baseline
- `query_failure_rate_high` - Query failure rate > threshold
- `dataset_sync_failure` - Data catalog synchronization failures
- `database_connection_pool_exhausted` - Connection pool utilization critical

#### Governance & Security
- `excessive_data_export` - Unusual data export volumes
- `unauthorized_access_attempt` - Repeated access denials
- `policy_violation_detected` - Governance policy violations
- `expired_access_rights` - Users with expired roles

#### Adoption & Engagement
- `low_user_adoption_rate` - Adoption below target by department
- `user_inactivity_risk` - Power user inactivity
- `analyst_request_backlog_growing` - Backlog accumulation

#### Data Quality
- `data_freshness_sla_breach` - Data not refreshed per SLA
- `data_quality_score_degradation` - Quality metrics declining
- `missing_column_metadata` - Low metadata coverage

#### Cost & Resources
- `compute_cost_spike` - Query costs elevated
- `storage_capacity_warning` - Storage nearing capacity

**Alert Structure**:
```yaml
alert_id: unique_identifier
name: human_readable_name
description: what_the_alert_detects
severity: critical|high|medium|low
enabled: true|false

condition:
  metric: metric_name
  operator: '>|<|=|!='
  threshold: numeric_value
  lookback_window: time_period
  comparison: optional_baseline_comparison

evaluation_rule: SQL query or metric calculation

notification_template: message_template_with_variables

remediation_steps:
  - step_1
  - step_2

runbook: url_to_documentation
```

**Severity Escalation**:
- **Critical** (5m): Email, Slack, PagerDuty
- **High** (15m): Email, Slack
- **Medium** (1h): Slack, Email
- **Low**: Slack only

**Alert Correlation**:
Groups related alerts into incidents (e.g., "Database Issues" groups query performance,
failure rate, and connection pool alerts within 15-minute window)

**Usage**:
```bash
# Deploy alerts to monitoring system
python deploy_alerts.py --config 12_alert_rules.yaml --env production

# Test alert configuration
python validate_alerts.py --config 12_alert_rules.yaml

# View active alerts
curl http://monitoring.company.com/api/v1/alerts?severity=critical

# Acknowledge alert
curl -X POST http://monitoring.company.com/api/v1/alerts/query_failure_rate_high/acknowledge
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│          Self-Service Analytics Platform                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │  Metrics API     │  │  Data Catalog Sync Service   │ │
│  │  (08_metrics_api │  │  (09_data_catalog_sync)     │ │
│  │  .py)            │  │                              │ │
│  └────────┬─────────┘  └──────────────┬────────────────┘ │
│           │                           │                   │
│  ┌────────▼───────────────────────────▼──────────────┐  │
│  │        Metrics Registry & Data Catalog             │  │
│  │   (PostgreSQL/Snowflake/MySQL)                    │  │
│  └────────────────────────────────────────────────────┘  │
│           │                           │                   │
│  ┌────────▼───────────────────────────▼──────────────┐  │
│  │      Governance & Monitoring Layer                 │  │
│  │  • governance_dashboard.sql (10)                  │  │
│  │  • self_service_metrics.sql (11)                 │  │
│  │  • alert_rules.yaml (12)                         │  │
│  └────────────────────────────────────────────────────┘  │
│                       │                                    │
│           ┌───────────┼───────────┐                       │
│           │           │           │                       │
│      ┌────▼─┐    ┌───▼──┐   ┌───▼──┐                    │
│      │Grafana│    │Slack │   │Email │                    │
│      └───────┘    │Alerts│   │Alerts│                    │
│                   └──────┘   └──────┘                    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Deployment Steps

### 1. Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up database connections
export DB_HOST=analytics.company.com
export DB_USER=analytics_user
export DB_PASSWORD=***
```

### 2. Deploy Metrics API
```bash
# Run migrations
alembic upgrade head

# Start API service
uvicorn 08_metrics_api:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Deploy Catalog Sync
```bash
# Run initial discovery
python 09_data_catalog_sync.py --mode discover --output catalog_manifest.json

# Execute first sync
python 09_data_catalog_sync.py --mode sync --config config.yaml
```

### 4. Deploy Governance Views
```bash
# Create SQL views in data warehouse
psql -h $DB_HOST -U $DB_USER -d analytics < 10_governance_dashboard.sql
psql -h $DB_HOST -U $DB_USER -d analytics < 11_self_service_metrics.sql
```

### 5. Configure Alerts
```bash
# Deploy alert rules to monitoring system
python deploy_alerts.py \
  --config 12_alert_rules.yaml \
  --monitoring-backend prometheus \
  --env production
```

## Performance Tuning

### Query Optimization
```sql
-- Example: Optimize adoption metrics query
-- Add bitmap indexes for boolean columns
CREATE INDEX idx_user_activity_cached
  ON audit.user_activity USING BRIN (query_cached);

-- Partition user_activity by date for faster range queries
ALTER TABLE audit.user_activity
  PARTITION BY RANGE (DATEDIFF(month, activity_timestamp, '2000-01-01'));
```

### Caching Strategy
- Metrics API: Redis caching with 5-minute TTL
- Query results: Database-level query result caching
- Catalog sync: 24-hour sync frequency with incremental updates

## Monitoring

### Key Metrics to Track
- API response times (target: <200ms p95)
- Query success rate (target: >99%)
- Catalog sync success rate (target: 100%)
- Alert response time (critical: <10min, high: <30min)

### Health Checks
```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Check catalog sync status
curl http://localhost:8001/health

# Check alert system
curl http://monitoring.company.com/health
```

## Troubleshooting

### Common Issues

**Query Performance Degradation**
1. Check database connection pool utilization
2. Review slow query logs
3. Run EXPLAIN on problematic queries
4. Check for table lock contention

**Catalog Sync Failures**
1. Verify data source connectivity
2. Check catalog API availability
3. Review sync logs for error details
4. Validate adapter configurations

**Low Adoption**
1. Review user training completion rates
2. Analyze adoption blockers (usability, documentation)
3. Identify high-value use cases for champions
4. Provide targeted personalized onboarding

## Contributing

Guidelines for extending these implementations:

1. **Adding New Metrics**: Follow pattern in 08_metrics_api.py
2. **New Data Sources**: Extend DataSourceAdapter in 09_data_catalog_sync.py
3. **New Views**: Add to appropriate SQL file with documentation
4. **New Alerts**: Follow structure in 12_alert_rules.yaml

## References

- **dbt Metrics**: https://docs.getdbt.com/docs/build/metrics
- **Amundsen**: https://www.amundsendata.io/
- **Metrics Layer Patterns**: https://www.locallyoptimistic.com/
- **Data Governance Best Practices**: https://gdpr-info.eu/

## Support

For questions or issues:
- Documentation: https://wiki.company.com/analytics/self-service
- Slack: #analytics-platform
- Email: analytics-platform@company.com
