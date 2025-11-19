# BI Platform Security & Compliance Reference

## Security Framework Overview

### Defense in Depth Layers
```
1. Network Security
   ├─ Firewall rules
   ├─ VPN/Private connectivity
   ├─ DDoS protection
   └─ Network segmentation

2. Authentication
   ├─ SSO/SAML
   ├─ Multi-factor authentication
   ├─ Certificate-based auth
   └─ API key management

3. Authorization
   ├─ Role-based access control (RBAC)
   ├─ Row-level security (RLS)
   ├─ Column-level security
   └─ Object permissions

4. Data Protection
   ├─ Encryption at rest
   ├─ Encryption in transit (TLS)
   ├─ Data masking
   └─ Tokenization

5. Audit & Monitoring
   ├─ Access logging
   ├─ Change tracking
   ├─ Anomaly detection
   └─ Compliance reporting
```

## Platform Security Capabilities

| Feature | Tableau | Power BI | Looker | Qlik | Superset |
|---------|---------|----------|--------|------|----------|
| **Encryption at Rest** | ✓ Extract | ✓ Premium | ✓ DB-level | ✓ QVD | ✓ DB-level |
| **Encryption in Transit** | TLS 1.2+ | TLS 1.2+ | TLS 1.2+ | TLS 1.2+ | TLS 1.2+ |
| **SSO (SAML)** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **MFA** | Via IdP | ✓ Native | Via IdP | Via IdP | Via IdP |
| **Row-Level Security** | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ Section Access | ✓✓ SQL-based |
| **Column Masking** | ✓ | ✓ Premium | ✓ | ✓ | ✓ Custom |
| **Data Loss Prevention** | Limited | ✓ MS DLP | Custom | Limited | Custom |
| **Audit Logging** | ✓✓✓ | ✓✓ Premium | ✓✓✓ | ✓✓ | ✓ Basic |
| **Compliance Certs** | SOC2, HIPAA, FedRAMP | SOC2, HIPAA, FedRAMP | SOC2, HIPAA | SOC2, ISO27001 | Self-managed |

## Tableau Security

### Row-Level Security Implementation
```sql
-- Create entitlements table
CREATE TABLE user_entitlements (
    username VARCHAR(255),
    region VARCHAR(50),
    department VARCHAR(50),
    data_level VARCHAR(20)  -- 'Full', 'Regional', 'Departmental'
);

-- Populate
INSERT INTO user_entitlements VALUES
('john.doe@company.com', 'West', 'Sales', 'Regional'),
('jane.smith@company.com', NULL, NULL, 'Full'),
('bob.jones@company.com', 'East', 'Marketing', 'Departmental');
```

```tableau
// In Tableau (calculated field)
// Method 1: User filter
[Region] = USERNAME()

// Method 2: Data source filter (more secure)
// Right-click data source → Edit Data Source Filters → Add
// Create calculated field:
User Region Filter:
CASE [Region]
    WHEN (
        // Lookup user's region from entitlements table
        ATTR({ INCLUDE [Region] :
            LOOKUP(ATTR([User Entitlements].[Region]),
                FIRST() WHERE [User Entitlements].[Username] = USERNAME()
            )
        })
    ) THEN TRUE
    ELSE FALSE
END

// Method 3: Dynamic filter with parameters
IF [User Level] = 'Full' THEN TRUE
ELSEIF [User Level] = 'Regional' AND [Region] = [User Region] THEN TRUE
ELSEIF [User Level] = 'Departmental' AND [Department] = [User Department] THEN TRUE
ELSE FALSE
END
```

### Data Extract Encryption
```bash
# Enable extract encryption on Tableau Server
tsm configuration set -k datasourceencryption.enabled -v true
tsm configuration set -k datasourceencryption.algorithm -v "AES-256"

# Apply changes
tsm pending-changes apply

# Extract password protection (per workbook)
# In Tableau Desktop:
# Data → [Extract] → Extract Data
# Check "Encrypt extract"
# Set password
```

### Permission Model
```
Tableau Server Permissions Hierarchy:
├─ Projects
│   ├─ Default (inheritable)
│   └─ Locked (enforced)
├─ Workbooks
│   ├─ View
│   ├─ Explore
│   ├─ Publish
│   └─ Administer
├─ Data Sources
│   ├─ View
│   ├─ Connect
│   └─ Save
└─ Flows (Tableau Prep)
    ├─ View
    ├─ Run
    └─ Save

Effective Permissions =
    MAX(Direct Permissions, Group Permissions) - Explicit Denials
```

## Power BI Security

### Row-Level Security (DAX)
```dax
// Role: Regional Manager
// In "Manage Roles" → Create role

// Static role
[Region] = "West"

// Dynamic role based on user
[SalesPersonEmail] = USERPRINCIPALNAME()

// Complex multi-table RLS
VAR CurrentUserEmail = USERPRINCIPALNAME()
VAR UserRegions =
    CALCULATETABLE(
        VALUES(UserRegionMapping[Region]),
        UserRegionMapping[Email] = CurrentUserEmail
    )
RETURN
    [Region] IN UserRegions
```

### Object-Level Security (OLS)
```dax
// Hide sensitive columns for certain roles
// Create measure:
Sensitive Revenue =
IF(
    USERPRINCIPALNAME() IN {
        "finance@company.com",
        "cfo@company.com",
        "ceo@company.com"
    },
    SUM(Sales[Revenue]),
    BLANK()
)

// Use this measure instead of direct column
```

### Sensitivity Labels
```powershell
# Apply Microsoft Information Protection labels
# Requires: Azure Information Protection, Power BI Premium

# In Power BI Service:
# Dataset Settings → Sensitivity label → Apply label

# Labels propagate to:
# - Downloaded files (.pbix)
# - Exported data (Excel, PDF)
# - Embedded content

# PowerShell: Bulk apply labels
Connect-PowerBIServiceAccount

$datasets = Get-PowerBIDataset -WorkspaceId $workspaceId
foreach ($dataset in $datasets) {
    Set-PowerBIDataset -DatasetId $dataset.Id -SensitivityLabel "Confidential"
}
```

### Defender for Cloud Apps Integration
```json
// Monitor Power BI with Microsoft Defender
{
  "policies": [
    {
      "name": "Detect mass download",
      "condition": "User downloads > 100 reports in 1 hour",
      "action": "Alert and block"
    },
    {
      "name": "Anomalous access pattern",
      "condition": "Access from unusual location/time",
      "action": "Require MFA re-authentication"
    },
    {
      "name": "Sharing with external users",
      "condition": "Report shared outside organization",
      "action": "Admin approval required"
    }
  ]
}
```

## Looker Security

### Access Filters (RLS)
```lookml
# In model file
explore: orders {
  access_filter: {
    field: customer_region
    user_attribute: allowed_regions
  }

  access_filter: {
    field: customer_tier
    user_attribute: customer_access_level
  }
}

# Multiple values in user attribute (comma-separated)
# Admin UI: Users → Edit User → User Attributes
# allowed_regions: "West,East,North"

# In view
view: orders {
  dimension: customer_region {
    sql: ${TABLE}.region ;;
    # Access filter automatically applied
  }

  # Conditional visibility based on permissions
  dimension: cost {
    sql: ${TABLE}.cost ;;
    required_access_grants: [finance_only]
  }
}

# Access grant definition (in model)
access_grant: finance_only {
  user_attribute: department
  allowed_values: ["Finance", "Executive"]
}
```

### Field-Level Security
```lookml
# Hide sensitive fields from certain users
dimension: ssn {
  type: string
  sql: ${TABLE}.ssn ;;
  hidden: yes  # Not accessible via UI

  # Or conditional hiding
  sql:
    {% if _user_attributes['department'] == 'HR' %}
      ${TABLE}.ssn
    {% else %}
      'XXX-XX-' || RIGHT(${TABLE}.ssn, 4)
    {% endif %} ;;
}

# Required access grant
dimension: revenue {
  type: number
  sql: ${TABLE}.revenue ;;
  required_access_grants: [view_revenue]
}

access_grant: view_revenue {
  user_attribute: can_see_revenue
  allowed_values: ["yes"]
}
```

### Content Access Control
```ruby
# Looker API: Set folder permissions
sdk.update_folder(
  folder_id,
  {
    name: "Sales Reports",
    parent_id: parent_folder_id
  }
)

# Set access
sdk.create_folder_access(
  folder_id,
  {
    group_id: sales_group_id,
    permission_type: "view"
  }
)

# Content delivery (scheduled)
sdk.create_scheduled_plan(
  {
    name: "Weekly Sales Report",
    look_id: look_id,
    enabled: true,
    crontab: "0 9 * * 1",  # Monday 9 AM
    require_no_results: false,
    require_results: true,
    require_change: false,
    send_all_results: false,
    scheduled_plan_destination: [{
      type: "email",
      address: "sales-team@company.com",
      format: "pdf_portrait"
    }]
  }
)
```

## Qlik Sense Security

### Section Access (RLS)
```qlik
Section Access;
LOAD * INLINE [
    ACCESS, USERID, REDUCTION, OMIT
    ADMIN, DOMAIN\admin, *, *
    USER, DOMAIN\john.doe, West, Cost
    USER, DOMAIN\jane.smith, East, Margin
];

Section Application;

// Main data
Sales:
LOAD
    Region,        // Must match REDUCTION field
    Product,
    Revenue,
    Cost,
    Margin
FROM [data.qvd] (qvd);

// Qlik automatically filters:
// - john.doe sees only West region
// - john.doe doesn't see Cost column
// - jane.smith sees only East region
// - jane.smith doesn't see Margin column
```

### Dynamic Data Reduction
```qlik
// Advanced Section Access with table lookup
Section Access;
UserAccess:
LOAD
    ACCESS,
    USERID,
    REGION,
    DEPARTMENT
FROM [user_permissions.qvd] (qvd);

Section Application;

// User can see multiple regions
// by having multiple rows in UserAccess table
```

### Security Rules (Qlik Sense Enterprise)
```javascript
// Custom security rule examples
// QMC → Security Rules

// Rule 1: App access based on custom property
resource.resourcetype = "App" and
resource.stream.HasPrivilege("read") and
resource.@AppOwner = user.userId

// Rule 2: Stream access based on AD group
resource.resourcetype = "Stream" and
resource.name = "Finance" and
user.group = "DOMAIN\\FinanceTeam"

// Rule 3: Export restrictions
resource.resourcetype = "App" and
resource.App.stream.name = "Confidential" and
resource.App.HasPrivilege("export") and
user.environment = "Internal"
```

## Apache Superset Security

### Row-Level Security
```python
# superset_config.py or database

# SQL-based RLS filter
@app.before_request
def apply_rls():
    from flask import g, session
    from superset import db
    from superset.models.core import Database

    if g.user and not g.user.is_anonymous:
        # Get user's allowed tenants
        allowed_tenants = db.session.query(UserTenant)\
            .filter_by(user_id=g.user.id)\
            .all()

        tenant_ids = [t.tenant_id for t in allowed_tenants]

        # Store in session for use in SQL
        session['allowed_tenants'] = tenant_ids

# In dataset SQL
SELECT *
FROM sales
WHERE tenant_id IN (
    SELECT tenant_id FROM user_tenants
    WHERE user_id = current_user_id()
)
```

### Custom Security Manager
```python
# superset_config.py
from superset.security import SupersetSecurityManager

class CustomSecurityManager(SupersetSecurityManager):
    def get_rls_filters(self, table):
        """
        Return list of SQLAlchemy filters for row-level security
        """
        from flask import g
        from sqlalchemy import text

        filters = []

        if g.user.is_anonymous:
            return filters

        # Department-based filtering
        if hasattr(g.user, 'department'):
            filters.append(
                text(f"department = '{g.user.department}'")
            )

        # Custom role filtering
        if 'RegionalManager' in [role.name for role in g.user.roles]:
            filters.append(
                text(f"region = '{g.user.region}'")
            )

        return filters

CUSTOM_SECURITY_MANAGER = CustomSecurityManager
```

### Column-Level Security
```python
# In dataset definition or custom middleware
def filter_columns_by_role(dataset, user):
    """
    Hide sensitive columns from certain users
    """
    sensitive_columns = ['ssn', 'salary', 'credit_card']

    if not user.has_role('HR'):
        for col in dataset.columns:
            if col.column_name in sensitive_columns:
                col.is_dttm = False  # Hide from UI
                col.filterable = False
                col.groupby = False
```

## Compliance Requirements

### GDPR Compliance

**Right to Access (Article 15)**
```sql
-- Query all data for a specific user
SELECT
    dashboard_name,
    query_text,
    accessed_at
FROM audit_log
WHERE user_email = 'user@example.com'
ORDER BY accessed_at DESC;
```

**Right to Erasure (Article 17)**
```sql
-- Remove user data
DELETE FROM user_profiles WHERE email = 'user@example.com';
DELETE FROM audit_log WHERE user_email = 'user@example.com';
DELETE FROM saved_queries WHERE created_by = 'user@example.com';
```

**Data Processing Records (Article 30)**
```yaml
# Document data flows
data_processing_activities:
  - purpose: "Sales Analytics"
    legal_basis: "Legitimate Interest"
    data_subjects: "Employees, Customers"
    categories:
      - "Sales transactions"
      - "Customer demographics"
    recipients: "Sales team, Management"
    retention: "7 years"
    security:
      - "Encryption at rest (AES-256)"
      - "Encryption in transit (TLS 1.3)"
      - "Row-level security"
      - "Audit logging"
```

### HIPAA Compliance

**Technical Safeguards**
```
Required Controls:
├─ Access Control (§164.312(a)(1))
│   ├─ Unique user identification
│   ├─ Emergency access procedure
│   ├─ Automatic logoff
│   └─ Encryption and decryption
│
├─ Audit Controls (§164.312(b))
│   ├─ Hardware, software, procedures to record access
│   └─ Examination of activity
│
├─ Integrity (§164.312(c)(1))
│   ├─ Mechanisms to authenticate ePHI
│   └─ Protection from improper alteration/destruction
│
└─ Transmission Security (§164.312(e)(1))
    ├─ Integrity controls
    └─ Encryption
```

**Implementation Example**
```bash
# Tableau Server HIPAA configuration
# 1. Enable audit logging
tsm configuration set -k auditing.enabled -v true

# 2. Enable extract encryption
tsm configuration set -k datasourceencryption.enabled -v true

# 3. Configure session timeout (15 minutes)
tsm configuration set -k wgserver.session.idle_limit -v 15

# 4. Enable TLS 1.2 minimum
tsm configuration set -k ssl.protocols -v "TLSv1.2 TLSv1.3"

# 5. Restrict export capabilities
tsm configuration set -k webdataconnector.enabled -v false

# Apply all changes
tsm pending-changes apply
```

### SOC 2 Compliance

**Type II Requirements**
```
Common Criteria:
├─ CC6.1: Logical Access Controls
│   ├─ User authentication
│   ├─ Authorization
│   └─ Multi-factor authentication
│
├─ CC6.6: Logical Access Removed
│   ├─ Terminated user access removed
│   └─ Regular access reviews
│
├─ CC6.7: Audit Logging
│   ├─ All access logged
│   ├─ Logs protected from modification
│   └─ Log retention (1+ years)
│
└─ CC7.2: System Monitoring
    ├─ Anomaly detection
    ├─ Security alerts
    └─ Incident response
```

## Audit Logging

### Tableau Audit Queries
```sql
-- Most active users
SELECT
    user_name,
    COUNT(*) as view_count,
    COUNT(DISTINCT workbook_name) as unique_workbooks
FROM _http_requests
WHERE action = 'show'
  AND timestamp >= CURRENT_DATE - 30
GROUP BY user_name
ORDER BY view_count DESC
LIMIT 20;

-- Failed login attempts
SELECT
    user_name,
    timestamp,
    remote_ip
FROM _http_requests
WHERE action = 'login'
  AND http_request_uri LIKE '%failed%'
  AND timestamp >= CURRENT_DATE - 7
ORDER BY timestamp DESC;

-- Data exports (potential data exfiltration)
SELECT
    user_name,
    workbook_name,
    timestamp,
    COUNT(*) as export_count
FROM _http_requests
WHERE action IN ('export', 'download')
  AND timestamp >= CURRENT_DATE - 1
GROUP BY user_name, workbook_name, timestamp
HAVING COUNT(*) > 10  -- Suspicious: >10 exports in same minute
ORDER BY export_count DESC;
```

### Power BI Audit Log (PowerShell)
```powershell
# Connect to Power BI
Connect-PowerBIServiceAccount

# Get audit events
$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

$auditLogs = Get-PowerBIActivityEvent -StartDateTime $startDate -EndDateTime $endDate

# Filter for specific activities
$suspiciousActivities = $auditLogs | Where-Object {
    $_.Activity -in @('ShareReport', 'ExportReport', 'ExportDataflow')
}

# Export to CSV
$suspiciousActivities | Export-Csv -Path "power-bi-audit.csv" -NoTypeInformation

# Alert on external sharing
$externalShares = $auditLogs | Where-Object {
    $_.Activity -eq 'ShareReport' -and
    $_.RecipientEmail -notlike '*@company.com'
}

if ($externalShares.Count -gt 0) {
    Send-MailMessage -To "security@company.com" -Subject "Power BI External Share Detected"
}
```

### Looker System Activity
```ruby
# Looker API: Get audit logs
require 'looker-sdk'

sdk = LookerSDK::Client.new(
  client_id: ENV['LOOKER_CLIENT_ID'],
  client_secret: ENV['LOOKER_CLIENT_SECRET'],
  api_endpoint: 'https://company.looker.com:19999/api/3.1'
)

# Query logs
events = sdk.get_user_login_lockouts(
  fields: 'user_id,remote_ip,full_name',
  limit: 100
)

# Get query history
query_history = sdk.run_inline_query(
  result_format: 'json',
  body: {
    model: 'system__activity',
    view: 'history',
    fields: ['history.created_date', 'user.name', 'history.query_run_count'],
    filters: {
      'history.created_date': '30 days'
    }
  }
)
```

## Data Classification

### Sensitivity Levels
```
Public (Level 0)
├─ No restrictions
├─ Can be shared externally
└─ Example: Published reports, marketing data

Internal (Level 1)
├─ Employee access only
├─ No external sharing
└─ Example: Operational dashboards

Confidential (Level 2)
├─ Need-to-know basis
├─ RLS required
├─ Audit all access
└─ Example: Financial data, HR data

Restricted (Level 3)
├─ Explicit approval required
├─ Encryption mandatory
├─ Export disabled
├─ Watermarking enabled
└─ Example: Board reports, M&A data
```

### Implementation
```python
# Metadata tagging system
class DatasetClassification:
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3

    @staticmethod
    def get_controls(level):
        controls = {
            DatasetClassification.PUBLIC: {
                'rls': False,
                'encryption': False,
                'audit': False,
                'export': True,
                'sharing': 'anyone'
            },
            DatasetClassification.INTERNAL: {
                'rls': False,
                'encryption': True,
                'audit': True,
                'export': True,
                'sharing': 'internal_only'
            },
            DatasetClassification.CONFIDENTIAL: {
                'rls': True,
                'encryption': True,
                'audit': True,
                'export': 'manager_approval',
                'sharing': 'need_to_know'
            },
            DatasetClassification.RESTRICTED: {
                'rls': True,
                'encryption': True,
                'audit': True,
                'export': False,
                'sharing': 'explicit_grant',
                'watermark': True
            }
        }
        return controls.get(level)
```

## Security Checklist

### Pre-Deployment
- [ ] Security requirements documented
- [ ] Data classification completed
- [ ] Access control model defined
- [ ] Encryption strategy determined
- [ ] Audit logging configured
- [ ] Compliance requirements identified
- [ ] Security testing completed
- [ ] Incident response plan created

### Post-Deployment
- [ ] Regular access reviews (quarterly)
- [ ] Audit log monitoring (daily)
- [ ] Security patches applied (monthly)
- [ ] Penetration testing (annual)
- [ ] Compliance audits (annual)
- [ ] User security training (annual)
- [ ] Disaster recovery testing (semi-annual)
- [ ] Encryption key rotation (annual)

## Resources
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CIS Controls: https://www.cisecurity.org/controls
- GDPR Guidelines: https://gdpr.eu/
- HIPAA Security Rule: https://www.hhs.gov/hipaa/for-professionals/security/
