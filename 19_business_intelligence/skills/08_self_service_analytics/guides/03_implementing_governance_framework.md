# Implementing Governance Framework Guide

## Quick Start

**Timeline**: 6-8 weeks
**Team**: 2-3 people
**Goal**: Balanced access with appropriate controls

## Week 1-2: Define Policies

### Data Classification
```yaml
Create Classification Scheme:
  PUBLIC:
    - Non-sensitive aggregated metrics
    - Public-facing data
    - Access: All employees

  INTERNAL:
    - General business data
    - Most analytics use cases
    - Access: Employees (default)

  CONFIDENTIAL:
    - Sensitive business information
    - Financial details, strategy
    - Access: Need-to-know basis

  RESTRICTED:
    - PII, PHI, credentials
    - Regulated data
    - Access: Strictly limited

Classification Process:
  1. Data steward reviews dataset
  2. Applies classification based on:
     - PII presence
     - Regulatory requirements
     - Business sensitivity
  3. Documents in catalog
  4. Applies appropriate controls
```

### Access Control Model
```sql
-- Role-Based Access Control (RBAC) Setup

-- 1. Define roles
CREATE ROLE data_viewer;    -- View dashboards only
CREATE ROLE data_analyst;   -- Query and create dashboards
CREATE ROLE data_engineer;  -- Create tables and pipelines
CREATE ROLE data_admin;     -- Full access

-- 2. Grant permissions
-- Viewer role
GRANT USAGE ON DATABASE analytics TO ROLE data_viewer;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics.public TO ROLE data_viewer;

-- Analyst role (includes viewer)
GRANT ROLE data_viewer TO ROLE data_analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics.internal TO ROLE data_analyst;
GRANT CREATE TABLE ON SCHEMA analytics.sandbox TO ROLE data_analyst;

-- 3. Assign users to roles
GRANT ROLE data_viewer TO USER john.doe@company.com;
GRANT ROLE data_analyst TO USER jane.smith@company.com;
```

## Week 3-4: Implement Controls

### Row-Level Security
```sql
-- Example: Sales territory access
CREATE OR REPLACE ROW ACCESS POLICY sales_territory_policy
AS (territory_id VARCHAR) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() = 'DATA_ADMIN' THEN TRUE
    WHEN EXISTS (
      SELECT 1 FROM user_territories
      WHERE user_email = CURRENT_USER()
        AND territory_id = territory_id
    ) THEN TRUE
    ELSE FALSE
  END;

ALTER TABLE sales_data
  ADD ROW ACCESS POLICY sales_territory_policy
  ON (territory_id);
```

### Data Masking
```sql
-- Example: PII masking
CREATE OR REPLACE MASKING POLICY email_mask AS
  (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('DATA_ADMIN', 'PII_VIEWER')
      THEN val
    ELSE REGEXP_REPLACE(val, '^.(.*)@', '*****@')
  END;

ALTER TABLE customers
  MODIFY COLUMN email
  SET MASKING POLICY email_mask;
```

## Week 5-6: Access Request Workflow

### Self-Service Access Requests
```yaml
Setup Process:

1. Create Request Form:
   Fields:
     - Dataset needed
     - Business justification
     - Access level (read/write)
     - Duration needed
     - Manager approval

2. Approval Routing:
   - Data steward approves business need
   - Security team approves if RESTRICTED
   - Manager approves if required

3. Automation:
   # Example automation (pseudocode)
   if dataset.classification == "PUBLIC":
       auto_approve()
   elif dataset.classification == "INTERNAL":
       route_to_steward()
       if approved:
           grant_access()
   elif dataset.classification in ["CONFIDENTIAL", "RESTRICTED"]:
       route_to_steward_and_security()
       if both_approved:
           grant_access_with_expiry(90_days)

4. Audit Trail:
   - Log all requests
   - Track approvals
   - Monitor access usage
   - Alert on anomalies
```

## Week 7-8: Monitoring & Audit

### Audit Logging
```sql
-- Create audit log table
CREATE TABLE data_access_audit (
    log_id BIGINT AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    user_email VARCHAR,
    user_role VARCHAR,
    action VARCHAR,
    resource_name VARCHAR,
    query_text TEXT,
    rows_accessed BIGINT,
    data_classification VARCHAR,
    success BOOLEAN
);

-- Monitoring queries
-- 1. Access to sensitive data
SELECT
    user_email,
    resource_name,
    COUNT(*) as access_count
FROM data_access_audit
WHERE data_classification = 'RESTRICTED'
    AND timestamp >= CURRENT_DATE - 7
GROUP BY 1, 2
ORDER BY access_count DESC;

-- 2. Failed access attempts
SELECT
    user_email,
    resource_name,
    COUNT(*) as failed_attempts
FROM data_access_audit
WHERE success = FALSE
    AND timestamp >= CURRENT_DATE - 1
GROUP BY 1, 2
HAVING COUNT(*) > 5;
```

## Governance Checklist

```yaml
Policy Documents:
  □ Data classification scheme
  □ Access control policy
  □ Acceptable use policy
  □ Data retention policy
  □ Incident response plan

Technical Implementation:
  □ RBAC roles defined
  □ Row-level security policies
  □ Column masking implemented
  □ Access request workflow
  □ Audit logging enabled

Operations:
  □ Data stewards assigned
  □ Approval workflows documented
  □ Quarterly access reviews
  □ Incident response tested
  □ Compliance reporting
```

## Best Practices

```yaml
Start Light, Iterate:
  - Begin with simple RBAC
  - Add complexity as needed
  - Don't over-govern early

Balance Access & Control:
  - Default to open (within reason)
  - Add controls where necessary
  - Audit extensively
  - Trust but verify

Automate Where Possible:
  - Auto-classify data
  - Auto-approve low-risk requests
  - Auto-revoke on role change
  - Auto-alert on anomalies

Communication:
  - Clear policies published
  - Easy to understand
  - Training provided
  - Support available
```
