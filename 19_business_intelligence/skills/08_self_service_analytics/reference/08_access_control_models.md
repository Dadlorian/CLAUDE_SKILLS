# Access Control Models Reference

## Overview

Effective access control balances data democratization with security and compliance. This reference details access control patterns for self-service analytics based on industry best practices.

## Access Control Models

### 1. Role-Based Access Control (RBAC)

```yaml
Definition:
  Permissions granted based on user roles within the organization

Advantages:
  - Simple to understand and manage
  - Scales well for most organizations
  - Easy to audit
  - Standard compliance approach

Disadvantages:
  - Role explosion in complex orgs
  - Less granular than attribute-based
  - Harder to handle exceptions

Best For:
  - Most organizations
  - Clear role hierarchies
  - Standard access patterns
```

#### RBAC Implementation

```yaml
Roles:

  data_viewer:
    description: Can view pre-built dashboards
    permissions:
      - dashboard:read
      - report:read
    data_access:
      - public_datasets
      - internal_summary_tables
    restrictions:
      - no_raw_data_access
      - no_pii_access

  data_analyst:
    description: Can query and create dashboards
    permissions:
      - dashboard:read
      - dashboard:create
      - dashboard:edit_own
      - query:execute
      - export:limited
    data_access:
      - all_internal_datasets
      - most_fact_tables
      - dimension_tables
    restrictions:
      - no_production_db_access
      - no_pii_unless_justified
      - query_timeout: 300s

  senior_analyst:
    description: Advanced analytics with broader access
    permissions:
      - all data_analyst permissions
      - query:unrestricted
      - export:full
      - metric:create
      - dataset:certify
    data_access:
      - all_datasets (with RLS)
      - pii_with_masking
      - production_replicas
    restrictions:
      - audit_logging: detailed

  data_engineer:
    description: Build and maintain data pipelines
    permissions:
      - all senior_analyst permissions
      - table:create
      - table:modify
      - pipeline:manage
      - grants:limited
    data_access:
      - all_datasets
      - raw_data
      - system_tables
    restrictions:
      - cannot_modify_production_directly
      - peer_review_required

  data_admin:
    description: Full administrative access
    permissions:
      - all_permissions
      - user:manage
      - role:manage
      - grant:manage
    data_access:
      - unrestricted
    restrictions:
      - all_actions_audited
      - requires_mfa
```

### 2. Attribute-Based Access Control (ABAC)

```yaml
Definition:
  Permissions based on user attributes, resource attributes,
  and environmental conditions

Advantages:
  - Highly granular control
  - Flexible and dynamic
  - Handles complex scenarios
  - Reduces role proliferation

Disadvantages:
  - More complex to implement
  - Harder to understand
  - Performance overhead
  - Debugging challenges

Best For:
  - Complex organizations
  - Dynamic access needs
  - Multi-tenant systems
  - Advanced security requirements
```

#### ABAC Policy Examples

```yaml
Policy 1: Department-Based Access
  effect: allow
  principal:
    department: Sales
  action: query
  resource:
    data_domain: Customer
    classification: [PUBLIC, INTERNAL]
  condition:
    time: business_hours
    location: approved_countries

Policy 2: Hierarchical Access
  effect: allow
  principal:
    role: Manager
    reports_to: ANY
  action: read
  resource:
    owner_department: principal.department
  condition:
    includes_subordinate_data: true

Policy 3: Project-Based Access
  effect: allow
  principal:
    project_member: TRUE
  action: [read, write]
  resource:
    project: principal.current_project
    classification: [PUBLIC, INTERNAL, CONFIDENTIAL]
  condition:
    project_active: true
    access_expiry: < 90_days

Policy 4: Compliance-Based Restrictions
  effect: deny
  principal:
    location: [EU, California]
  action: export
  resource:
    contains_pii: true
  condition:
    consent_documented: false
    legal_basis: missing
```

### 3. Row-Level Security (RLS)

```yaml
Definition:
  Filter data rows based on user context automatically

Use Cases:
  - Multi-tenancy
  - Territorial sales data
  - Department-specific data
  - Customer-facing analytics

Implementation Approaches:
  1. Database-native RLS
  2. View-based filtering
  3. Application-level filtering
  4. Query rewriting
```

#### Database-Native RLS

```sql
-- Snowflake Row Access Policy
CREATE OR REPLACE ROW ACCESS POLICY sales_territory_policy
AS (territory_id INTEGER) RETURNS BOOLEAN ->
  CASE
    -- Admins see everything
    WHEN CURRENT_ROLE() = 'DATA_ADMIN' THEN TRUE

    -- Sales reps see their territory
    WHEN EXISTS (
      SELECT 1 FROM user_territories
      WHERE user_email = CURRENT_USER()
        AND territory_id = territory_id
    ) THEN TRUE

    -- Managers see their team's territories
    WHEN EXISTS (
      SELECT 1 FROM manager_territories
      WHERE manager_email = CURRENT_USER()
        AND territory_id = territory_id
    ) THEN TRUE

    ELSE FALSE
  END;

-- Apply policy to table
ALTER TABLE sales_data
  ADD ROW ACCESS POLICY sales_territory_policy
  ON (territory_id);
```

#### View-Based RLS

```sql
-- Create secure view with embedded filtering
CREATE OR REPLACE SECURE VIEW sales_data_filtered AS
SELECT
  s.*
FROM sales_data s
WHERE
  -- Admin role sees all
  CURRENT_ROLE() = 'DATA_ADMIN'
  OR
  -- Sales rep sees own territory
  territory_id IN (
    SELECT territory_id
    FROM user_territories
    WHERE user_email = CURRENT_USER()
  );

-- Grant access to view, not base table
GRANT SELECT ON sales_data_filtered TO ROLE data_analyst;
```

### 4. Column-Level Security

```yaml
Techniques:

Dynamic Data Masking:
  Purpose: Show masked values to unauthorized users
  Example:
    - Email: j****@example.com
    - SSN: ***-**-1234
    - Credit Card: ****-****-****-5678

Column-Level Grants:
  Purpose: Restrict access to specific columns
  Example:
    GRANT SELECT (order_id, order_date, amount)
    ON orders TO ROLE data_analyst

View-Based Column Filtering:
  Purpose: Expose subset of columns
  Example:
    CREATE VIEW orders_safe AS
    SELECT
      order_id,
      order_date,
      amount,
      product_id
      -- Excludes: customer_email, ssn, credit_card
    FROM orders
```

#### Data Masking Examples

```sql
-- Snowflake Masking Policy
CREATE OR REPLACE MASKING POLICY email_mask AS
  (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('DATA_ADMIN', 'PII_VIEWER')
      THEN val
    ELSE REGEXP_REPLACE(val, '^.(.*)@', '*****@')
  END;

-- Apply to column
ALTER TABLE customers
  MODIFY COLUMN email
  SET MASKING POLICY email_mask;

-- BigQuery Example
CREATE OR REPLACE VIEW customers_masked AS
SELECT
  customer_id,
  CASE
    WHEN IS_MEMBER_OF_GROUP('pii-viewers')
      THEN email
    ELSE CONCAT('***@', SPLIT(email, '@')[OFFSET(1)])
  END AS email,
  -- Partial SSN masking
  CASE
    WHEN IS_MEMBER_OF_GROUP('pii-viewers')
      THEN ssn
    ELSE CONCAT('XXX-XX-', SUBSTR(ssn, -4))
  END AS ssn_masked
FROM customers;
```

## Access Request Workflows

### 1. Self-Service Access Request

```yaml
Process:
  1. User discovers dataset in catalog
  2. Sees "Request Access" button
  3. Fills out request form:
     - Dataset needed
     - Business justification
     - Access duration
     - Access level needed
  4. Request routed to:
     - Data steward (for approval)
     - Security team (if sensitive)
     - Manager (if required)
  5. Approvers review and decide
  6. Access granted automatically
  7. User notified via email/Slack

SLAs:
  - PUBLIC data: Instant (auto-approved)
  - INTERNAL data: < 4 hours
  - CONFIDENTIAL data: < 24 hours
  - RESTRICTED data: < 48 hours

Automation:
  - Auto-approve based on rules
  - Auto-expire after duration
  - Auto-notify before expiration
  - Auto-revoke on role change
```

### 2. Bulk Access Provisioning

```yaml
Use Case:
  New employee onboarding, team setup

Process:
  1. HR system triggers on hire
  2. Auto-provision based on:
     - Department
     - Role
     - Manager
     - Location
  3. Grant standard access:
     - Default dashboards
     - Department data
     - Public catalog access
  4. Send welcome email with:
     - Access summary
     - Training resources
     - Support contacts

Benefits:
  - Consistent access
  - Fast onboarding
  - Reduced manual work
  - Fewer tickets
```

### 3. Access Recertification

```yaml
Frequency: Quarterly

Process:
  1. Generate access reports
  2. Send to managers/stewards
  3. Review each user's access:
     - Still needed?
     - Appropriate level?
     - Should be reduced?
  4. Submit attestation
  5. Auto-revoke unattested access
  6. Document for audit

Reporting:
  - Users with access to dataset X
  - Datasets accessed by user Y
  - Unused access (last 90 days)
  - Excessive permissions
  - Anomalous access patterns
```

## Multi-Tenancy Patterns

### Pattern 1: Schema Per Tenant

```sql
-- Tenant A schema
CREATE SCHEMA tenant_a;
CREATE TABLE tenant_a.orders (...);

-- Tenant B schema
CREATE SCHEMA tenant_b;
CREATE TABLE tenant_b.orders (...);

-- Grant access
GRANT USAGE ON SCHEMA tenant_a TO ROLE tenant_a_users;
GRANT SELECT ON ALL TABLES IN SCHEMA tenant_a TO ROLE tenant_a_users;

-- User queries their schema
SELECT * FROM tenant_a.orders;  -- User in tenant_a_users role
```

**Pros:** Clear separation, easy to manage
**Cons:** Schema proliferation, harder to query across tenants

### Pattern 2: Single Schema with Tenant ID

```sql
-- Shared table with tenant_id column
CREATE TABLE orders (
  order_id INT,
  tenant_id INT,
  order_date DATE,
  amount DECIMAL,
  ...
);

-- Row-level security policy
CREATE POLICY tenant_isolation ON orders
USING (
  tenant_id = current_setting('app.current_tenant_id')::INT
);

-- Application sets tenant context
SET app.current_tenant_id = 123;

-- User queries filter automatically
SELECT * FROM orders;  -- Only sees tenant 123 data
```

**Pros:** Simplified schema, easier cross-tenant analytics
**Cons:** Risk of data leakage, requires careful implementation

### Pattern 3: Embedded Analytics (Customer-Facing)

```yaml
Requirements:
  - Customers see only their data
  - Branding customization
  - Usage tracking per customer
  - Performance isolation

Implementation:
  1. Generate signed embed token
     - Customer ID embedded
     - Expiration time
     - Allowed resources

  2. Apply RLS based on token
     - Filter to customer's data
     - Enforce access policies

  3. Customize experience
     - Customer logo/colors
     - Custom domain
     - Whitelabeling

  4. Track usage
     - Queries per customer
     - Data volume
     - Feature usage
     - Performance metrics
```

## Access Control Best Practices

### 1. Principle of Least Privilege

```yaml
Guidelines:
  - Grant minimum necessary access
  - Default to deny
  - Require justification for elevated access
  - Time-bound access when possible
  - Regular access reviews

Implementation:
  - Start with base role
  - Add specific grants as needed
  - Use temporary elevated access
  - Expire unused permissions
  - Audit excessive access
```

### 2. Separation of Duties

```yaml
Separation Matrix:

  Data Access vs. Data Modification:
    - Analysts can read but not write
    - Engineers can write but reviewed
    - Admins can do both but audited

  Development vs. Production:
    - Engineers have dev access
    - Limited production access
    - Read-only prod replicas
    - Change management for prod

  Access Grant vs. Access Use:
    - Separate admin from user roles
    - Require approvals for grants
    - Cannot grant to self
    - Audit all permission changes
```

### 3. Defense in Depth

```yaml
Multiple Layers:

  1. Network Level:
     - VPN required
     - IP allowlisting
     - Private endpoints

  2. Authentication:
     - SSO required
     - MFA for sensitive data
     - Session timeouts

  3. Authorization:
     - Role-based access
     - Row-level security
     - Column masking

  4. Data Level:
     - Encryption at rest
     - Encryption in transit
     - Key management

  5. Audit Level:
     - Comprehensive logging
     - Anomaly detection
     - Alert on suspicious activity
```

### 4. Just-in-Time Access

```yaml
Concept:
  Grant temporary elevated access only when needed

Use Cases:
  - Incident investigation
  - One-time analysis
  - Production debugging
  - Compliance audit

Implementation:
  1. User requests elevated access
  2. Provide justification & duration
  3. Manager/admin approves
  4. Access granted for limited time
  5. Auto-revoke after expiration
  6. Comprehensive audit logging

Tools:
  - CyberArk
  - HashiCorp Boundary
  - Custom workflow systems
```

## Monitoring & Auditing

### Access Logs

```sql
-- Comprehensive access logging
CREATE TABLE access_audit_log (
  log_id BIGINT,
  timestamp TIMESTAMP,
  user_id VARCHAR,
  user_role VARCHAR,
  action VARCHAR,  -- SELECT, INSERT, UPDATE, DELETE
  object_type VARCHAR,  -- TABLE, VIEW, DASHBOARD
  object_name VARCHAR,
  query_text TEXT,
  rows_accessed BIGINT,
  data_classification VARCHAR,
  ip_address VARCHAR,
  user_agent VARCHAR,
  session_id VARCHAR,
  success BOOLEAN,
  error_message TEXT
);

-- Query patterns to monitor
-- 1. Unusual access patterns
SELECT
  user_id,
  COUNT(*) as query_count,
  COUNT(DISTINCT object_name) as tables_accessed
FROM access_audit_log
WHERE timestamp >= CURRENT_DATE
GROUP BY user_id
HAVING query_count > 1000 OR tables_accessed > 50;

-- 2. After-hours access to sensitive data
SELECT *
FROM access_audit_log
WHERE data_classification IN ('CONFIDENTIAL', 'RESTRICTED')
  AND HOUR(timestamp) NOT BETWEEN 7 AND 19
  AND DAYOFWEEK(timestamp) IN (1, 7);  -- Weekend

-- 3. Failed access attempts
SELECT
  user_id,
  object_name,
  COUNT(*) as failed_attempts
FROM access_audit_log
WHERE success = FALSE
  AND timestamp >= CURRENT_DATE - 7
GROUP BY 1, 2
HAVING failed_attempts > 5;
```

### Anomaly Detection

```yaml
Patterns to Detect:

  Volume Anomalies:
    - Sudden spike in queries
    - Large data exports
    - Unusual access times

  Behavior Anomalies:
    - Access to new systems
    - Changed access patterns
    - Geographic anomalies

  Permission Anomalies:
    - Privilege escalation
    - Unusual role assignments
    - Dormant account activity

Actions:
    - Alert security team
  - Temporary access suspension
  - Require re-authentication
  - Investigation workflow
```

## Compliance Considerations

### GDPR

```yaml
Requirements:
  - Right to access
  - Right to be forgotten
  - Data minimization
  - Purpose limitation
  - Consent management

Implementation:
  - Track data subject consents
  - Support data deletion workflows
  - Limit data retention
  - Document processing purposes
  - Access controls on PII
```

### SOX

```yaml
Requirements:
  - Segregation of duties
  - Access controls
  - Audit trails
  - Change management

Implementation:
  - Separate read/write roles
  - Approval workflows
  - Comprehensive logging
  - Version control
```

### HIPAA

```yaml
Requirements:
  - Minimum necessary access
  - Audit controls
  - Encryption
  - Access management

Implementation:
  - Role-based access to PHI
  - Detailed audit logging
  - Encryption at rest/transit
  - Regular access reviews
```

## References

- NIST RBAC Model
- OWASP Access Control Guidelines
- AWS IAM Best Practices
- Snowflake Security Best Practices
- "Zero Trust Networks" - Gilman & Barth
