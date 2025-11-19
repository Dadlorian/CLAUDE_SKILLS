# Data Access Patterns for Self-Service Analytics

## Overview

Access patterns define how users interact with data based on their role, level of expertise, permissions, and analytical needs. Understanding and designing for these patterns improves user experience, security, and data governance in self-service analytics environments.

## User-Based Access Patterns

### Executive/Leadership Pattern

```yaml
Characteristics:
  - Limited technical depth
  - Preference for high-level insights
  - Time-constrained (5-15 min queries)
  - Need for context and explanations
  - Focus on strategic decisions

Data Interaction Model:
  Primary Tools:
    - Pre-built executive dashboards
    - Mobile apps for quick access
    - Email reports
    - Periodic presentations

  Data Types:
    - Aggregated metrics and KPIs
    - Trend visualizations
    - Comparative analysis (YoY, forecasts)
    - Exception alerts

  Typical Queries:
    - "What's our revenue this month vs. last?"
    - "How are we tracking to plan?"
    - "Which region is underperforming?"
    - "What's the status on key initiatives?"

Access Control:
  - All company-level metrics visible
  - Department-specific metrics filtered by role
  - No raw data access
  - No direct SQL access
  - Read-only access to reports

Time-to-Insight Expectation:
  - Instant: Cached dashboards and reports
  - Pre-scheduled: Weekly executive briefings
  - Ad-hoc: Available within 24 hours
```

### Manager/Supervisor Pattern

```yaml
Characteristics:
  - Moderate technical capability
  - Mixed strategic and tactical needs
  - Department and team focus
  - Driver of team decisions
  - Medium time investment (15-45 min)

Data Interaction Model:
  Primary Tools:
    - Department dashboards
    - Filtered report views
    - Ad-hoc query interface
    - Scheduled report distribution

  Data Types:
    - Department metrics
    - Team performance data
    - Resource utilization
    - Process metrics
    - Customer/product data within domain

  Typical Queries:
    - "How is my team performing against targets?"
    - "What's driving the variance?"
    - "Who are my top performers?"
    - "What bottlenecks do we face?"

Access Control:
  - Own department data: Full access
  - Related departments: Limited to relevant metrics
  - Other departments: Summary data only
  - No sensitive personal data
  - Read/write to department-owned reports

Advanced Capabilities:
  - Dashboard creation and editing
  - Report scheduling
  - Basic ad-hoc queries
  - Data export for analysis
  - No raw SQL unless trained
```

### Analyst/Self-Service User Pattern

```yaml
Characteristics:
  - Comfortable with data tools
  - Deep dives into specific areas
  - Can write basic SQL
  - Creative exploratory analysis
  - Longer engagement (30 min - 2 hours)

Data Interaction Model:
  Primary Tools:
    - SQL query editors
    - Advanced dashboard builders
    - Notebook environments
    - Data exploration tools
    - API access

  Data Access:
    - Own department: Full access
    - Cross-functional data: Permissioned
    - Production data: Read-only
    - Sandboxes available for experimentation

  Typical Workflows:
    - Write SQL to explore data
    - Build custom dashboards
    - Create ad-hoc reports
    - Test hypotheses
    - Develop analysis methodologies

Query Patterns:
  - Exploratory: Large result sets, many filter combinations
  - Comparative: Cross-segment, time-based, benchmark
  - Aggregative: Detailed breakdowns, hierarchical drilling
  - Integrative: Multiple table joins, complex logic

Access Control:
  - Read access to permitted data
  - Can create personal/team workspaces
  - Can share dashboards and queries
  - Subject to usage limits (query timeout, data volume)
  - Access request workflow for new data
```

### Data Engineer/Analytics Engineer Pattern

```yaml
Characteristics:
  - Advanced technical skills
  - Focus on data infrastructure
  - Pipeline and transformation work
  - Performance optimization
  - Tool configuration and customization

Data Interaction Model:
  Primary Tools:
    - dbt development environment
    - SQL editors with version control
    - Python notebooks
    - Data pipeline orchestration
    - Infrastructure as code

  Access Level:
    - Read/write to staging areas
    - Development environment: Full access
    - Production environment: Controlled via workflows
    - Direct database access with audit logging
    - Create tables/schemas with governance approval

  Responsibilities:
    - Build data models and transformations
    - Maintain data quality
    - Optimize queries and pipelines
    - Implement governance rules
    - Support self-service analytics infrastructure

Workflow:
  1. Development in feature branch
  2. Testing against staging data
  3. Code review and approval
  4. Deploy to production via CI/CD
  5. Monitor and optimize
  6. Document changes
```

## Access Pattern by Use Case

### Real-Time Dashboarding

```yaml
Pattern Characteristics:
  - Immediate data availability
  - Frequent refreshes (<30 minutes)
  - High query concurrency
  - Cache-heavy approach
  - Predictable query patterns

Architecture Considerations:
  Data Pipeline:
    - Streaming or near-real-time ingestion
    - Fast aggregation pipelines
    - Materialized views for hot metrics

  Caching Strategy:
    - Memory cache (Redis) for hot data
    - Scheduled materialization
    - Query result caching
    - Predictive pre-aggregation

  Performance Targets:
    - Dashboard load: <2 seconds
    - Metric drill-down: <5 seconds
    - Filter application: <1 second

Use Cases:
  - Operational dashboards (call center, order fulfillment)
  - Marketing campaign performance
  - Real-time KPI tracking
  - Fraud detection monitoring
  - System health dashboards

Query Optimization:
  - Pre-compute common slices
  - Index on dimension columns
  - Partition large tables
  - Use approximate algorithms when acceptable
```

### Exploratory Analysis Pattern

```yaml
Pattern Characteristics:
  - Unpredictable query patterns
  - Variable data sizes
  - Multiple queries sequentially
  - Hypothesis-driven iteration
  - May require joining multiple tables

Access Approach:
  Data Availability:
    - Access to raw and derived data
    - Multiple data sources available
    - Schema self-documentation important
    - Sample data for exploration

  Query Flexibility:
    - No pre-defined query templates
    - Custom WHERE/HAVING clauses
    - Ad-hoc joins
    - Exploratory aggregations

Tools & Environment:
  - SQL IDE with code completion
  - Query result caching
  - Data preview functionality
  - Ability to export results
  - Linked documentation

Performance Expectations:
  - Query timeout: 1-5 minutes
  - Result size limits: 1M-10M rows
  - Latency: 5 seconds to 1 minute acceptable
  - User controls complexity via interface

Example Workflow:
  1. Browse available tables and columns
  2. Preview sample data
  3. Write initial query
  4. Examine results, find patterns
  5. Refine query, add filters/groups
  6. Export results or save query
  7. Create visualization
```

### Scheduled Reporting Pattern

```yaml
Pattern Characteristics:
  - Predictable, recurring execution
  - Background processing
  - Time-insensitive
  - Can handle larger computations
  - Delivers results via email/portal

Architecture:
  Scheduling:
    - Cron-based or scheduler tool
    - Retry logic for failures
    - Dependency handling
    - Audit trail of executions

  Execution:
    - Off-peak scheduling (nights/weekends)
    - Parallel report generation
    - Resource quota management
    - Error handling and notifications

  Delivery:
    - Email with attachments
    - Portal/dashboard display
    - API webhook triggers
    - File storage systems

Query Patterns:
  - Materialization: Complex aggregations
  - Consistency: Same queries run same time
  - Optimization: Larger batch sizes
  - Aggregation: Summary statistics

Resource Management:
  - Longer query timeouts (5-30 minutes)
  - Higher data volume limits
  - Scheduled during off-peak hours
  - Dedicated compute resources
  - Priority: Lower than interactive queries

Examples:
  - Daily sales summary emails
  - Weekly performance reports
  - Monthly KPI reports
  - Automated alerts
  - Data extract files for external systems
```

### API/Application Access Pattern

```yaml
Pattern Characteristics:
  - Programmatic data access
  - High throughput, low latency critical
  - Consistent query patterns
  - Service-to-service communication
  - Monitoring and alerting required

Architecture:
  API Design:
    - RESTful endpoints or GraphQL
    - Query parameter validation
    - Rate limiting and throttling
    - Authentication/authorization
    - Caching layers

  Performance Requirements:
    - p95 latency: <100ms
    - p99 latency: <500ms
    - Cache hit rate: >90%
    - Availability: 99.9%+

  Scaling Considerations:
    - Horizontal scaling of API servers
    - Database connection pooling
    - Query result caching
    - Load balancing
    - Circuit breakers for failures

Authentication Methods:
  - API keys for applications
  - OAuth 2.0 for user-facing APIs
  - Service account tokens
  - IP whitelisting where appropriate
  - Token rotation and revocation

Example APIs:
  - Metric serving APIs
  - Data export APIs
  - Real-time data feeds
  - ML feature store endpoints
  - Mobile app data backends
```

## Permission Models

### Role-Based Access Control (RBAC)

```yaml
Role Definitions:
  Viewer:
    - Read dashboards and reports
    - View published data
    - No query writing
    - No data export

  Self-Service Analyst:
    - Write ad-hoc queries
    - Create dashboards
    - Share with specific users
    - Moderate data export

  Power User:
    - Advanced query writing
    - Dashboard creation and sharing
    - Create teams/projects
    - Perform analysis work

  Administrator:
    - System configuration
    - User and group management
    - Performance tuning
    - Security policy enforcement

  Data Steward:
    - Metadata curation
    - Access request approval
    - Data quality monitoring
    - Documentation maintenance

Limitations:
  - Doesn't account for data sensitivity
  - Role explosion in large orgs
  - Doesn't support fine-grained controls
  - Difficult to model temporary access
```

### Attribute-Based Access Control (ABAC)

```yaml
Access Rules Based On:
  User Attributes:
    - Department
    - Role/Title
    - Tenure
    - Clearance level
    - Project assignments

  Data Attributes:
    - Classification (public, internal, sensitive)
    - Department ownership
    - Data type (PII, financial, etc.)
    - Regulatory requirements
    - PII sensitivity level

  Context Attributes:
    - Location
    - Time of access
    - Device type
    - Network context
    - Purpose of access

Example Rules:
  Rule 1:
    User: role=analyst AND department=sales
    Data: department=sales AND classification!=secret
    Action: read, query, export limited

  Rule 2:
    User: role=executive
    Data: classification!=sensitive
    Action: read, view dashboards

  Rule 3:
    User: ANY
    Data: contains_pii=true
    Action: read only, no export, audit log required

Advantages:
  - Fine-grained control
  - Flexible and scalable
  - Accommodates complex scenarios
  - Better audit trails

Challenges:
  - Complexity to configure
  - Performance overhead
  - Requires attribute infrastructure
  - Harder to understand and troubleshoot
```

### Row-Level Security (RLS)

```yaml
Implementation Patterns:
  User-to-Department Mapping:
    - Users see only their department data
    - Enforced at database/BI tool level
    - Example: salesperson sees own territory

  Customer/Account Filtering:
    - Users see only assigned accounts
    - Multi-tenant isolation
    - Applied transparently to all queries

  Data Classification Levels:
    - Users see data appropriate to clearance
    - Executive data vs. detailed data
    - Sensitive fields masked for some users

Technical Implementation:
  - Database-level filters (views, policies)
  - Application-level filtering
  - BI tool row-level security settings
  - API parameter validation
  - All approaches logged for audit

Example:
  SELECT * FROM customers
  WHERE (
    user_role = 'admin'
    OR manager_id = current_user_id()
    OR region = current_user_region()
  )
```

## Data Sensitivity & Access Controls

### Data Classification Framework

```yaml
Public Data:
  - Examples: Product catalog, published pricing
  - Access: Anyone (internal or external)
  - Controls: Availability and performance

Internal Data:
  - Examples: Sales numbers, operational metrics
  - Access: Employees in relevant departments
  - Controls: Department-based RLS

Confidential Data:
  - Examples: Strategic plans, financial projections
  - Access: Leadership + relevant stakeholders
  - Controls: Role + approval required

Restricted Data:
  - Examples: Personal information, healthcare data, legal
  - Access: Specifically authorized only
  - Controls: Explicit approval, audit logging
  - Masking/redaction required for viewing

PII (Personally Identifiable Information):
  - Special handling required
  - Limited access essential
  - Anonymization/hashing recommended
  - Compliance requirements (GDPR, CCPA)
  - Audit trail mandatory
```

### PII Handling Patterns

```yaml
Access Restriction:
  - Limit to authorized personnel
  - Require explicit access requests
  - Approval from data owner
  - Expiration dates on access

Masking Techniques:
  Email: first_letter@example.com → j***@example.com
  Phone: 555-1234 → 555-****
  SSN: 123-45-6789 → ***-**-6789
  Credit Card: 4532-1234-5678-9012 → ****-****-****-9012

Anonymization:
  - Remove identifying information
  - Aggregate to prevent re-identification
  - Add noise for differential privacy
  - One-way hashing with salt

Audit Requirements:
  - Log all PII access
  - Track who accessed what, when
  - Retention policies for logs
  - Regular access review
  - Breach notification procedures
```

## Session & Connection Management

### Connection Pooling

```yaml
Purpose:
  - Reuse database connections
  - Reduce connection overhead
  - Improve query throughput
  - Limit resource consumption

Configuration:
  Min Connections: 5-10
  Max Connections: 50-200 (depends on workload)
  Connection Timeout: 30 seconds
  Idle Timeout: 5-10 minutes

  Example (PGBouncer):
    [databases]
    analytics_db = host=db.company.com port=5432 dbname=analytics

    [pgbouncer]
    pool_mode = transaction
    max_client_conn = 100
    default_pool_size = 20
    min_pool_size = 5
    reserve_pool_size = 5
```

### Query Management

```yaml
Concurrency Limits:
  Per User: 2-5 concurrent queries
  Per Department: 10-20 concurrent queries
  Total System: 50-100 concurrent queries

  Enforcement:
    - Queue additional queries
    - Reject if limit exceeded
    - Notify user of queue position
    - Priority queuing for important queries

Query Timeouts:
  Interactive Queries: 30-120 seconds
  Scheduled Jobs: 300-600 seconds (5-10 minutes)
  Batch Processes: 1-4 hours

  Handling:
    - Graceful timeout with informative message
    - Suggest query optimization
    - Offer alternative data sources
    - Log timeout events for analysis

Resource Quotas:
  CPU: Per user or department
  Memory: Per query or session
  Disk: Temporary storage for results
  Network: Bandwidth limits for data transfer

  Monitoring:
    - Track resource usage
    - Alert on approaching limits
    - Fair resource allocation
    - Ability to override for critical queries
```

## Best Practices

### 1. Principle of Least Privilege
- Grant minimum necessary access
- Regular access reviews
- Removal when no longer needed
- Default deny for new data

### 2. Separation of Concerns
- Analytics users separate from developers
- Development environment isolation
- Production access restrictions
- Controlled deployment processes

### 3. Comprehensive Auditing
- All data access logged
- Query logging with context
- Access request and approval tracking
- Regular audit reviews
- Alerting on suspicious patterns

### 4. Documentation
- Clear access policies
- Process documentation for requesting access
- Data dictionary for all assets
- Ownership and stewardship information

### 5. Continuous Monitoring
- Query pattern analysis
- Performance monitoring
- Security incident detection
- User behavior analytics
- Regular policy review and updates
