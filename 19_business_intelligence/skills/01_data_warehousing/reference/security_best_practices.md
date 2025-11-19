# Data Warehouse Security Best Practices

Comprehensive security guidelines for protecting data in cloud data warehouses including access control, encryption, auditing, and compliance.

## Security Principles

### Defense in Depth
- Multiple layers of security controls
- Network security
- Identity and access management
- Data encryption
- Audit logging
- Data masking and privacy

### Least Privilege
- Grant minimum necessary permissions
- Regular access reviews
- Time-bound access for temporary needs
- Separation of duties

### Zero Trust
- Verify every access request
- Assume breach mentality
- Continuous monitoring and validation

## Access Control

### Role-Based Access Control (RBAC)

#### Snowflake RBAC Example
```sql
-- Create functional roles
CREATE ROLE data_analyst;
CREATE ROLE data_engineer;
CREATE ROLE data_admin;

-- Create object hierarchy
GRANT USAGE ON DATABASE analytics TO ROLE data_analyst;
GRANT USAGE ON SCHEMA analytics.reporting TO ROLE data_analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics.reporting TO ROLE data_analyst;

-- Grant roles to users
GRANT ROLE data_analyst TO USER john.doe@company.com;

-- Role hierarchy (inheritance)
GRANT ROLE data_analyst TO ROLE data_engineer;
GRANT ROLE data_engineer TO ROLE data_admin;

-- View grants
SHOW GRANTS TO ROLE data_analyst;
SHOW GRANTS TO USER john.doe@company.com;
```

#### BigQuery IAM Roles
```sql
-- Project-level roles
-- roles/bigquery.dataViewer: Read access to data
-- roles/bigquery.dataEditor: Read and write access
-- roles/bigquery.admin: Full admin access
-- roles/bigquery.jobUser: Run jobs

-- Grant dataset-level access
GRANT `roles/bigquery.dataViewer`
ON `project.dataset`
TO "user:analyst@company.com";

-- Grant table-level access
GRANT `roles/bigquery.dataViewer`
ON `project.dataset.sensitive_table`
TO "group:finance-team@company.com";

-- Create custom role
CREATE ROLE custom_analyst_role AS
    SELECT,
    CREATE TABLE,
    CREATE VIEW;
```

#### Redshift User and Group Management
```sql
-- Create users
CREATE USER analyst_user WITH PASSWORD 'SecurePassword123!';
CREATE USER etl_user WITH PASSWORD 'AnotherSecurePassword456!';

-- Create groups
CREATE GROUP analysts;
CREATE GROUP developers;

-- Add users to groups
ALTER GROUP analysts ADD USER analyst_user;
ALTER GROUP developers ADD USER etl_user;

-- Grant privileges to groups
GRANT USAGE ON SCHEMA sales TO GROUP analysts;
GRANT SELECT ON ALL TABLES IN SCHEMA sales TO GROUP analysts;

-- Prevent future table access issues
ALTER DEFAULT PRIVILEGES IN SCHEMA sales
GRANT SELECT ON TABLES TO GROUP analysts;
```

### Row-Level Security (RLS)

#### Snowflake Row Access Policies
```sql
-- Create row access policy
CREATE ROW ACCESS POLICY customer_data_policy AS (customer_region VARCHAR)
RETURNS BOOLEAN ->
    CASE
        WHEN CURRENT_ROLE() = 'ADMIN' THEN TRUE
        WHEN CURRENT_ROLE() = 'EU_ANALYST' AND customer_region = 'EU' THEN TRUE
        WHEN CURRENT_ROLE() = 'US_ANALYST' AND customer_region = 'US' THEN TRUE
        ELSE FALSE
    END;

-- Apply policy to table
ALTER TABLE customers
ADD ROW ACCESS POLICY customer_data_policy ON (region);

-- View policies
SHOW ROW ACCESS POLICIES;

-- Drop policy
ALTER TABLE customers
DROP ROW ACCESS POLICY customer_data_policy;
```

#### BigQuery Row-Level Security
```sql
-- Create row access policy
CREATE ROW ACCESS POLICY regional_filter
ON `project.dataset.customers`
GRANT TO ('user:eu-analyst@company.com')
FILTER USING (region = 'EU');

CREATE ROW ACCESS POLICY us_filter
ON `project.dataset.customers`
GRANT TO ('user:us-analyst@company.com')
FILTER USING (region = 'US');

-- Admin sees all rows (no filter)
CREATE ROW ACCESS POLICY admin_access
ON `project.dataset.customers`
GRANT TO ('group:admins@company.com')
FILTER USING (TRUE);
```

#### Azure Synapse Row-Level Security
```sql
-- Create security predicate function
CREATE FUNCTION dbo.SecurityPredicate(@Region VARCHAR(50))
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS result
WHERE @Region = USER_NAME()
   OR USER_NAME() = 'admin';

-- Create security policy
CREATE SECURITY POLICY RegionalAccessPolicy
ADD FILTER PREDICATE dbo.SecurityPredicate(Region)
ON dbo.Customers
WITH (STATE = ON);
```

### Column-Level Security

#### Snowflake Column Masking
```sql
-- Create masking policy
CREATE MASKING POLICY email_mask AS (val VARCHAR)
RETURNS VARCHAR ->
    CASE
        WHEN CURRENT_ROLE() IN ('ADMIN', 'PRIVACY_OFFICER') THEN val
        ELSE '***MASKED***'
    END;

-- Apply masking policy to column
ALTER TABLE customers
MODIFY COLUMN email SET MASKING POLICY email_mask;

-- Partial masking (show partial data)
CREATE MASKING POLICY ssn_partial_mask AS (val VARCHAR)
RETURNS VARCHAR ->
    CASE
        WHEN CURRENT_ROLE() = 'ADMIN' THEN val
        ELSE CONCAT('XXX-XX-', RIGHT(val, 4))
    END;

ALTER TABLE customers
MODIFY COLUMN ssn SET MASKING POLICY ssn_partial_mask;
```

#### BigQuery Column-Level Security
```sql
-- Create taxonomy and policy tags
-- In UI: Data Catalog → Policy Tags

-- Apply policy tag to column
ALTER TABLE `project.dataset.customers`
ALTER COLUMN email
SET OPTIONS (
    policy_tags = ('projects/project/locations/us/taxonomies/12345/policyTags/67890')
);

-- Grant access to policy tag
GRANT `roles/datacatalog.categoryFineGrainedReader`
ON policy_tag_67890
TO "user:admin@company.com";
```

#### Redshift Column-Level Grants
```sql
-- Grant column-level access
GRANT SELECT (customer_id, customer_name, country)
ON TABLE customers
TO GROUP analysts;

-- Analysts can only see specified columns
-- email, ssn columns remain hidden
```

## Data Encryption

### Encryption at Rest

#### Snowflake
```sql
-- Automatic encryption at rest (AES-256)
-- Tri-Secret Secure (customer-managed keys)

-- Enable Tri-Secret Secure (Enterprise Edition)
-- 1. Generate master key in your key management system
-- 2. Provide key to Snowflake
-- 3. Snowflake combines: Snowflake key + Customer key + Account key

-- No additional SQL configuration needed
-- Managed in account settings
```

#### BigQuery
```sql
-- Default: Google-managed encryption keys (automatic)

-- Customer-managed encryption keys (CMEK)
CREATE TABLE `project.dataset.sensitive_data` (
    id INT64,
    data STRING
)
OPTIONS(
    kms_key_name="projects/PROJECT/locations/LOCATION/keyRings/KEYRING/cryptoKeys/KEY"
);

-- Encrypt existing table with CMEK
ALTER TABLE `project.dataset.existing_table`
SET OPTIONS(
    kms_key_name="projects/PROJECT/locations/LOCATION/keyRings/KEYRING/cryptoKeys/KEY"
);
```

#### Redshift
```sql
-- Encryption at rest (must be enabled at cluster creation)
-- Options:
-- 1. AWS-managed keys (default)
-- 2. Customer-managed keys (AWS KMS)
-- 3. HSM (Hardware Security Module)

-- Check encryption status
SELECT
    schemaname,
    tablename,
    encode
FROM pg_table_def
WHERE schemaname = 'public';

-- Note: Encryption is cluster-level, not table-level
```

### Encryption in Transit

**All Platforms:**
- TLS/SSL for all connections (enforced)
- Minimum TLS 1.2
- Strong cipher suites

```sql
-- Snowflake: Enforce TLS (enabled by default)
ALTER ACCOUNT SET NETWORK_POLICY = require_tls_policy;

-- Connection string must use SSL
-- jdbc:snowflake://account.snowflakecomputing.com/?ssl=on

-- BigQuery: HTTPS enforced (automatic)

-- Redshift: SSL connections
-- Connection parameter: sslmode=require
```

## Auditing and Monitoring

### Query Auditing

#### Snowflake Account Usage
```sql
-- Track all queries
SELECT
    query_id,
    query_text,
    user_name,
    role_name,
    warehouse_name,
    execution_status,
    start_time,
    end_time
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;

-- Track failed queries (potential security issues)
SELECT
    user_name,
    query_text,
    error_message,
    start_time
FROM snowflake.account_usage.query_history
WHERE execution_status = 'FAIL'
  AND start_time >= DATEADD(day, -1, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;

-- Track access to sensitive tables
SELECT
    query_id,
    user_name,
    query_text,
    start_time
FROM snowflake.account_usage.query_history
WHERE query_text ILIKE '%sensitive_table%'
  AND start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP());
```

#### BigQuery Audit Logs
```sql
-- Enable audit logging in Cloud Logging
-- Logs: Admin activity, Data access, System events

-- Query audit logs
SELECT
    timestamp,
    protopayload_auditlog.authenticationInfo.principalEmail as user_email,
    protopayload_auditlog.methodName as action,
    protopayload_auditlog.resourceName as resource
FROM `project.dataset.cloudaudit_googleapis_com_data_access`
WHERE DATE(timestamp) = CURRENT_DATE()
ORDER BY timestamp DESC;

-- Track table access
SELECT
    timestamp,
    protopayload_auditlog.authenticationInfo.principalEmail as user,
    resource.labels.dataset_id as dataset,
    resource.labels.table_id as table,
    protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.referencedTables
FROM `project.dataset.cloudaudit_googleapis_com_data_access`
WHERE protopayload_auditlog.methodName = 'jobservice.jobcompleted'
  AND DATE(timestamp) >= CURRENT_DATE() - 7;
```

#### Redshift Audit Logging
```sql
-- Enable audit logging at cluster level
-- Logs stored in S3

-- Query system tables
SELECT
    userid,
    query,
    querytxt,
    starttime,
    endtime
FROM stl_query
WHERE userid > 1
  AND starttime >= DATEADD(day, -1, CURRENT_DATE())
ORDER BY starttime DESC;

-- Connection log
SELECT
    event,
    recordtime,
    username,
    dbname,
    remotehost
FROM stl_connection_log
WHERE recordtime >= DATEADD(day, -7, CURRENT_DATE())
ORDER BY recordtime DESC;

-- User activity log
SELECT
    userid,
    username,
    query,
    starttime
FROM svl_statementtext
WHERE starttime >= DATEADD(day, -1, CURRENT_DATE())
ORDER BY starttime DESC;
```

### Access Auditing

```sql
-- Snowflake: Track login attempts
SELECT
    user_name,
    client_ip,
    reported_client_type,
    first_authentication_factor,
    is_success,
    error_message,
    event_timestamp
FROM snowflake.account_usage.login_history
WHERE event_timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  AND is_success = 'NO'
ORDER BY event_timestamp DESC;

-- Track privilege changes
SELECT
    user_name,
    role_name,
    granted_on,
    granted_to,
    privilege,
    created_on
FROM snowflake.account_usage.grants_to_users
WHERE deleted_on IS NULL
ORDER BY created_on DESC;
```

## Network Security

### IP Whitelisting

#### Snowflake Network Policies
```sql
-- Create network policy
CREATE NETWORK POLICY office_only
ALLOWED_IP_LIST = ('203.0.113.0/24', '198.51.100.0/24')
BLOCKED_IP_LIST = ();

-- Apply to account
ALTER ACCOUNT SET NETWORK_POLICY = office_only;

-- Apply to specific user
ALTER USER analyst_user SET NETWORK_POLICY = office_only;

-- Show network policies
SHOW NETWORK POLICIES;
```

#### BigQuery VPC Service Controls
```sql
-- Implemented at GCP project/organization level
-- Define security perimeters
-- Restrict data access to specific VPCs

-- Example: Access context manager policy
{
  "accessLevels": [{
    "name": "corp_network",
    "basic": {
      "conditions": [{
        "ipSubnetworks": ["203.0.113.0/24"]
      }]
    }
  }]
}
```

#### Redshift Enhanced VPC Routing
```sql
-- Force all COPY and UNLOAD traffic through VPC
-- Enable Enhanced VPC Routing in cluster settings

-- Security group rules control access
-- Example: Allow only specific IP ranges

-- In AWS Console: VPC → Security Groups
-- Inbound rule: Custom TCP, Port 5439, Source: 203.0.113.0/24
```

### Private Connectivity

**Snowflake Private Link:**
- Direct private connection from VPC
- Traffic doesn't traverse public internet
- Available on AWS, Azure, GCP

**BigQuery Private Google Access:**
- Access BigQuery from VPC without public IPs
- Configure VPC subnet settings

**Redshift VPC:**
- Launch cluster in VPC
- Use VPC endpoints for S3 access
- PrivateLink for secure connectivity

## Compliance and Data Governance

### PII and Sensitive Data Detection

```sql
-- Automated scanning (use data catalog tools)
-- Monte Carlo, Collibra, Alation, etc.

-- Manual tagging
-- Snowflake: Object tags
CREATE TAG pii_level
ALLOWED_VALUES 'high', 'medium', 'low';

ALTER TABLE customers
SET TAG pii_level = 'high';

ALTER TABLE customers
MODIFY COLUMN ssn SET TAG pii_level = 'high';

-- Query by tag
SELECT *
FROM snowflake.account_usage.tag_references
WHERE tag_name = 'PII_LEVEL'
  AND tag_value = 'high';
```

### Data Classification

```sql
-- Define data classification levels
-- Public: Can be shared externally
-- Internal: Internal use only
-- Confidential: Restricted access
-- Highly Confidential: Extremely restricted

-- Implement as tags/labels
CREATE TAG data_classification
ALLOWED_VALUES 'public', 'internal', 'confidential', 'highly_confidential';

-- Apply to objects
ALTER DATABASE analytics
SET TAG data_classification = 'internal';

ALTER TABLE customer_pii
SET TAG data_classification = 'highly_confidential';
```

### Compliance Standards

**SOC 2:**
- Access controls and audit logs
- Encryption at rest and in transit
- Regular access reviews
- Incident response procedures

**HIPAA:**
- PHI encryption (at rest and transit)
- Audit logs for PHI access
- Business Associate Agreement (BAA) with cloud provider
- Access controls and authentication

**GDPR:**
- Right to erasure (data deletion)
- Data portability
- Consent management
- Data retention policies
- Encryption and pseudonymization

**PCI DSS:**
- Cardholder data encryption
- Access controls and logging
- Network segmentation
- Regular security assessments

### Data Retention and Deletion

```sql
-- Implement data retention policies
-- Snowflake: Time Travel and Fail-Safe
ALTER TABLE customer_data
SET DATA_RETENTION_TIME_IN_DAYS = 90;

-- BigQuery: Table expiration
ALTER TABLE `project.dataset.temp_data`
SET OPTIONS(
    expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
);

-- Hard delete for GDPR right to erasure
DELETE FROM customers
WHERE customer_id = '12345'
  AND deletion_requested = TRUE;

-- Verify deletion (Snowflake Time Travel)
SELECT * FROM customers
AT(TIMESTAMP => DATEADD(hour, -1, CURRENT_TIMESTAMP()))
WHERE customer_id = '12345';
```

## Security Checklist

### Access Control
- [ ] Implement RBAC with least privilege
- [ ] Regular access reviews (quarterly)
- [ ] Disable inactive users
- [ ] Use service accounts for applications
- [ ] Implement MFA for all users
- [ ] Row-level security for multi-tenant data
- [ ] Column-level security for PII
- [ ] Separate roles for different functions

### Encryption
- [ ] Encryption at rest enabled
- [ ] Customer-managed keys for sensitive data
- [ ] TLS 1.2+ for all connections
- [ ] Encrypted backups
- [ ] Secure key management

### Auditing
- [ ] Enable comprehensive audit logging
- [ ] Monitor failed login attempts
- [ ] Track access to sensitive tables
- [ ] Alert on unusual query patterns
- [ ] Regular log review and analysis
- [ ] Long-term log retention (1+ years)

### Network Security
- [ ] IP whitelisting for corporate network
- [ ] Private connectivity (PrivateLink, VPC)
- [ ] Network segmentation
- [ ] Firewall rules configured
- [ ] VPN for remote access

### Compliance
- [ ] Data classification implemented
- [ ] PII identified and tagged
- [ ] Data retention policies enforced
- [ ] GDPR compliance (if applicable)
- [ ] Regular compliance audits
- [ ] Incident response plan
- [ ] Security training for users

### Monitoring
- [ ] Real-time security alerts
- [ ] Anomaly detection
- [ ] Query performance monitoring
- [ ] Cost monitoring
- [ ] User activity dashboard
- [ ] Regular security assessments

## Incident Response

### Data Breach Response Plan

1. **Detection and Analysis**
   - Monitor audit logs for anomalies
   - Investigate alerts
   - Determine scope of breach

2. **Containment**
   - Revoke compromised credentials
   - Block malicious IP addresses
   - Isolate affected systems

3. **Eradication**
   - Remove unauthorized access
   - Patch vulnerabilities
   - Update security controls

4. **Recovery**
   - Restore from backups if needed
   - Verify system integrity
   - Resume normal operations

5. **Post-Incident**
   - Document incident
   - Root cause analysis
   - Update security controls
   - Notify affected parties (if required)

### Common Security Incidents

**Unauthorized Access:**
```sql
-- Immediately revoke access
REVOKE ROLE analyst_role FROM USER suspicious_user;

-- Check what was accessed
SELECT *
FROM snowflake.account_usage.query_history
WHERE user_name = 'suspicious_user'
  AND start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;
```

**Credential Compromise:**
```sql
-- Force password reset
ALTER USER compromised_user MUST_CHANGE_PASSWORD = TRUE;

-- Disable account temporarily
ALTER USER compromised_user SET DISABLED = TRUE;

-- Audit recent activity
SELECT *
FROM snowflake.account_usage.login_history
WHERE user_name = 'compromised_user'
  AND event_timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP());
```

## Security Tools and Resources

### Platform-Specific
- **Snowflake**: Trust Center, Security Overview, Account Usage views
- **BigQuery**: Security Command Center, VPC Service Controls, DLP API
- **Redshift**: AWS Security Hub, CloudTrail, GuardDuty

### Third-Party Tools
- **SIEM**: Splunk, Datadog, Sumo Logic
- **Data Catalog**: Collibra, Alation, Monte Carlo
- **Secrets Management**: HashiCorp Vault, AWS Secrets Manager
- **Access Management**: Okta, Azure AD, Google Workspace

### Best Practice Resources
- CIS Benchmarks for cloud platforms
- NIST Cybersecurity Framework
- Cloud Security Alliance (CSA) guidelines
- Platform-specific security documentation
