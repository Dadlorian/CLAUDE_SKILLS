# Governance Frameworks Reference

## Overview

Effective governance enables self-service analytics by providing guardrails that ensure data quality, security, and compliance without hindering accessibility. This reference outlines comprehensive governance frameworks for self-service environments.

## Core Governance Dimensions

### 1. Data Classification

#### Classification Levels
```yaml
PUBLIC:
  Description: Non-sensitive data safe for broad access
  Examples: Marketing content, public metrics, documentation
  Access: All employees
  Controls: Basic audit logging

INTERNAL:
  Description: General business data
  Examples: Aggregate metrics, operational reports
  Access: Employees (default)
  Controls: Role-based access, audit logging

CONFIDENTIAL:
  Description: Sensitive business information
  Examples: Revenue details, strategic plans, customer data
  Access: Need-to-know basis
  Controls: Approval required, enhanced auditing, encryption

RESTRICTED:
  Description: Highly sensitive regulated data
  Examples: PII, PHI, financial records, credentials
  Access: Strictly limited
  Controls: Multi-factor auth, encryption, compliance monitoring
```

#### Classification Criteria
```
Sensitivity Assessment:
  1. Contains PII/PHI?
  2. Subject to regulations? (GDPR, CCPA, HIPAA)
  3. Competitive advantage if leaked?
  4. Financial impact of breach?
  5. Reputational risk?

Scoring:
  High Risk (3+ Yes) → RESTRICTED
  Medium Risk (2 Yes) → CONFIDENTIAL
  Low Risk (1 Yes) → INTERNAL
  No Risk (0 Yes) → PUBLIC
```

### 2. Access Control Models

#### Role-Based Access Control (RBAC)
```yaml
Roles:
  data_consumer:
    permissions:
      - read: [public, internal]
      - query: [approved_datasets]

  data_analyst:
    permissions:
      - read: [public, internal, confidential]
      - query: [all_datasets]
      - create: [derived_tables]

  data_engineer:
    permissions:
      - read: [all]
      - write: [all]
      - admin: [data_pipelines]

  domain_steward:
    permissions:
      - read: [domain_data]
      - write: [domain_data]
      - approve: [access_requests]
      - certify: [datasets]
```

#### Attribute-Based Access Control (ABAC)
```python
# Policy example
access_policy = {
    "effect": "allow",
    "principal": {
        "department": ["Sales", "Marketing"],
        "role": "Manager"
    },
    "action": "read",
    "resource": {
        "data_domain": "Customer",
        "classification": ["PUBLIC", "INTERNAL"]
    },
    "condition": {
        "time": "business_hours",
        "location": "approved_countries"
    }
}
```

#### Row-Level Security (RLS)
```sql
-- Sales rep sees only their territory
CREATE POLICY sales_territory ON sales_data
FOR SELECT
USING (
  territory_id IN (
    SELECT territory_id
    FROM user_territories
    WHERE user_email = current_user()
  )
);

-- Manager sees entire team
CREATE POLICY manager_team ON sales_data
FOR SELECT
USING (
  territory_id IN (
    SELECT territory_id
    FROM territories
    WHERE manager_email = current_user()
  )
);
```

### 3. Data Stewardship

#### Stewardship Model
```yaml
Executive Sponsor:
  Role: Strategic oversight and funding
  Responsibilities:
    - Approve governance framework
    - Allocate resources
    - Resolve escalations
    - Champion data culture

Chief Data Officer:
  Role: Overall governance leadership
  Responsibilities:
    - Define policies and standards
    - Monitor compliance
    - Drive data strategy
    - Report to leadership

Domain Stewards:
  Role: Subject area ownership
  Responsibilities:
    - Define business logic
    - Approve access requests
    - Certify data quality
    - Document domain data
    - Resolve data issues

Data Engineers:
  Role: Technical implementation
  Responsibilities:
    - Implement governance controls
    - Build data pipelines
    - Ensure data quality
    - Optimize performance
    - Support users

Data Analysts:
  Role: Subject matter experts
  Responsibilities:
    - Create certified metrics
    - Validate data accuracy
    - Document use cases
    - Train end users
```

### 4. Approval Workflows

#### Access Request Process
```
User Request → Auto-Approval OR Manual Review → Grant Access

Auto-Approval Criteria:
  - Classification: PUBLIC or INTERNAL
  - User role has default access
  - Data domain matches user's department

Manual Review Required:
  - CONFIDENTIAL or RESTRICTED data
  - Cross-department access
  - Bulk data export
  - API access requests

Approval SLA:
  - PUBLIC: Instant
  - INTERNAL: < 1 hour
  - CONFIDENTIAL: < 24 hours
  - RESTRICTED: < 48 hours
```

#### Certification Workflow
```yaml
Dataset Certification Process:
  1. Data Creator:
      - Build dataset
      - Add documentation
      - Run quality tests
      - Submit for review

  2. Domain Steward:
      - Verify business logic
      - Validate calculations
      - Check completeness
      - Approve or request changes

  3. Data Quality Team:
      - Run automated tests
      - Review quality metrics
      - Check SLA compliance
      - Certify or flag issues

  4. Security Team:
      - Verify classification
      - Validate access controls
      - Check compliance
      - Approve or escalate

  Result: CERTIFIED badge or PENDING status
```

### 5. Compliance Management

#### Regulatory Frameworks
```yaml
GDPR (EU):
  Requirements:
    - Data subject consent
    - Right to be forgotten
    - Data portability
    - Privacy by design
    - Breach notification
  Implementation:
    - User consent tracking
    - Deletion workflows
    - Export capabilities
    - Audit logging
    - Incident response

CCPA (California):
  Requirements:
    - Opt-out of data sale
    - Access to personal data
    - Deletion rights
    - Non-discrimination
  Implementation:
    - Opt-out mechanisms
    - Data inventory
    - Deletion processes
    - Rights management

HIPAA (Healthcare):
  Requirements:
    - PHI protection
    - Access controls
    - Audit trails
    - Breach notification
    - Business associate agreements
  Implementation:
    - Encryption at rest/transit
    - RBAC enforcement
    - Comprehensive logging
    - Incident procedures
    - Vendor management

SOX (Financial):
  Requirements:
    - Financial data accuracy
    - Internal controls
    - Audit trails
    - Change management
  Implementation:
    - Data validation
    - Segregation of duties
    - Immutable logs
    - Version control
```

### 6. Quality Standards

#### Data Quality Dimensions
```yaml
Completeness:
  Definition: Extent to which data is complete
  Metrics:
    - Null percentage < 5%
    - Required fields populated
    - Record count expectations met
  Tests:
    - NOT NULL constraints
    - Row count thresholds
    - Completeness scoring

Accuracy:
  Definition: Correctness of data values
  Metrics:
    - Error rate < 1%
    - Values within expected ranges
    - Referential integrity maintained
  Tests:
    - Range validation
    - Foreign key checks
    - Cross-system reconciliation

Consistency:
  Definition: Data uniformity across systems
  Metrics:
    - Same values in related systems
    - Standard formats applied
    - Naming conventions followed
  Tests:
    - Cross-table comparisons
    - Format validation
    - Duplicate detection

Timeliness:
  Definition: Data is up-to-date
  Metrics:
    - Freshness < defined SLA
    - Update frequency met
    - Lag time minimized
  Tests:
    - Freshness checks
    - Update timestamp validation
    - SLA monitoring

Validity:
  Definition: Data conforms to business rules
  Metrics:
    - Valid values only
    - Proper data types
    - Business logic satisfied
  Tests:
    - Enum validation
    - Type checking
    - Business rule assertions
```

### 7. Audit & Monitoring

#### Audit Log Requirements
```sql
-- Comprehensive audit logging
CREATE TABLE data_access_logs (
    log_id BIGINT PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    user_role VARCHAR(100),
    action VARCHAR(50), -- SELECT, INSERT, UPDATE, DELETE
    resource_type VARCHAR(50), -- table, dashboard, report
    resource_name VARCHAR(255),
    query_text TEXT,
    rows_affected INT,
    execution_time_ms INT,
    ip_address VARCHAR(45),
    client_application VARCHAR(100),
    success BOOLEAN,
    error_message TEXT
);

-- Indices for efficient querying
CREATE INDEX idx_timestamp ON data_access_logs(timestamp);
CREATE INDEX idx_user ON data_access_logs(user_email);
CREATE INDEX idx_resource ON data_access_logs(resource_name);
```

#### Monitoring Dashboards
```yaml
Governance Metrics Dashboard:

  Access Monitoring:
    - Access requests by classification
    - Approval turnaround time
    - Denied access attempts
    - Unusual access patterns

  Data Quality:
    - Quality score trends
    - Failed test counts
    - SLA compliance rates
    - Issue resolution time

  Usage Analytics:
    - Active users by role
    - Query volume trends
    - Popular datasets
    - Performance metrics

  Compliance:
    - Certification coverage
    - Policy violations
    - Audit findings
    - Remediation status
```

## Policy Templates

### Data Retention Policy
```yaml
Policy: Data Retention and Deletion
Version: 2.0
Effective Date: 2025-01-01

Retention Periods:
  Transactional Data:
    Active: 7 years
    Archive: 10 years
    Justification: Legal and tax requirements

  Analytical Data:
    Aggregate Metrics: Indefinite
    Raw Event Logs: 2 years
    User Behavior: 13 months (GDPR)
    Justification: Business value vs privacy

  PII Data:
    Active Users: Duration of relationship + 30 days
    Inactive Users: 90 days after last activity
    Justification: GDPR right to be forgotten

Deletion Process:
  1. Automated daily cleanup jobs
  2. Soft delete with 30-day recovery window
  3. Hard delete after retention period
  4. Verification and audit logging
```

### Acceptable Use Policy
```yaml
Policy: Self-Service Analytics Acceptable Use
Version: 1.0

Permitted Uses:
  - Business decision support
  - Product and operational analytics
  - Data exploration and hypothesis testing
  - Dashboard and report creation
  - Model development and testing

Prohibited Uses:
  - Personal use or benefit
  - Competitor intelligence gathering
  - Unauthorized data exports
  - Sharing credentials
  - Circumventing access controls
  - Reverse engineering customer identities
  - High-frequency automated queries without approval

Consequences:
  First Violation: Warning and training
  Second Violation: Access suspension (7 days)
  Third Violation: Access revocation
  Severe Violation: Immediate revocation + HR action
```

## Governance Operating Model

### Decision Rights
```yaml
Strategic Decisions:
  Owner: Chief Data Officer
  Examples: Tool selection, architecture choices
  Process: Quarterly steering committee

Policy Decisions:
  Owner: Data Governance Council
  Examples: Classification rules, retention policies
  Process: Monthly review and approval

Operational Decisions:
  Owner: Domain Stewards
  Examples: Access approvals, data certifications
  Process: Daily/weekly as needed

Technical Decisions:
  Owner: Data Engineering Team
  Examples: Implementation approaches, optimizations
  Process: Continuous with architectural review
```

### Governance Cadence
```yaml
Daily:
  - Access request processing
  - Incident response
  - Quality monitoring

Weekly:
  - Steward office hours
  - Issue triage
  - Metrics review

Monthly:
  - Governance council meeting
  - Policy updates
  - Compliance reporting

Quarterly:
  - Steering committee review
  - Strategy refinement
  - Budget planning

Annual:
  - Comprehensive audit
  - Policy overhaul
  - Goal setting
```

## Success Criteria

### Leading Indicators
- Policy acknowledgment rate
- Training completion rate
- Access request volume
- Certification coverage

### Lagging Indicators
- Security incidents
- Compliance violations
- Data quality scores
- User satisfaction

### Business Outcomes
- Reduced risk exposure
- Faster time to insight
- Increased data trust
- Regulatory compliance

## References

- GDPR Official Text: https://gdpr.eu/
- CCPA Compliance Guide
- NIST Data Governance Framework
- DAMA-DMBOK Data Management Body of Knowledge
- Airbnb Data Governance Case Study
