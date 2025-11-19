# Data Dictionary Template

**Document Version:** 2.0
**Last Updated:** 2025-11-19
**Owner:** [Data Steward Name]
**Owner Email:** [steward@company.com]
**Owner Team:** Data Governance

---

## Table of Contents
1. [Overview](#overview)
2. [Business Context](#business-context)
3. [Technical Details](#technical-details)
4. [Column Definitions](#column-definitions)
5. [Data Quality](#data-quality)
6. [Security & Access](#security--access)
7. [Lineage](#lineage)
8. [Known Issues](#known-issues)
9. [Change Log](#change-log)

---

## Overview

### Table Name
`[schema_name].[table_name]`

### Description
[Provide a clear, comprehensive description of what this table represents. What business process does it capture? Who uses it?]

### Business Purpose
- Primary Use Cases: [List main use cases]
- Key Stakeholders: [Teams/roles that use this data]
- Business Domain: [finance/marketing/sales/operations/product]

### Table Metrics
| Metric | Value |
|--------|-------|
| **Row Count** | [Current count] |
| **Storage Size** | [GB/TB] |
| **Row Count Growth** | [Rows added per day] |
| **Update Frequency** | [daily/hourly/real-time] |
| **Last Updated** | [Timestamp] |
| **Certification Level** | [bronze/silver/gold] |

---

## Business Context

### Historical Background
[When was this table created? What problem did it solve?]

### Related Tables
| Table Name | Relationship | Join Key |
|------------|--------------|----------|
| [table1] | One-to-Many | [column] |
| [table2] | Many-to-One | [column] |
| [table3] | Equals | [column] |

### Business Rules
- [Business rule 1: Describe what data is included/excluded]
- [Business rule 2: E.g., "Only includes completed transactions from last 2 years"]
- [Business rule 3: E.g., "Excludes test accounts and cancelled orders"]

### Refresh Schedule
| Frequency | Time | SLA | Owner |
|-----------|------|-----|-------|
| Daily | 2:00 AM UTC | Completed by 9:00 AM | [Team] |

---

## Technical Details

### Source System(s)
| Source | Type | Owner | Frequency |
|--------|------|-------|-----------|
| [ERP System Name] | [Database/API/File] | [Team] | [Frequency] |

### Transformation Logic
```sql
-- Example transformation
SELECT
    customer_id,
    SUM(order_amount) as revenue,
    COUNT(*) as order_count
FROM raw_orders
WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY customer_id
```

### Schema Name
`[schema_name]` - [Description of schema purpose]

### Table Type
- [ ] Fact Table (transactional events/measurements)
- [ ] Dimension Table (descriptive attributes)
- [ ] Bridge Table (many-to-many relationships)
- [ ] Staging Table (temporary processing)
- [ ] Raw Table (source system extract)

---

## Column Definitions

### Key Columns
| Column Name | Data Type | Nullable | Primary Key | Description |
|-------------|-----------|----------|-------------|-------------|
| `customer_id` | STRING | No | Yes | Unique customer identifier from CRM system |
| `order_id` | STRING | No | Yes | Unique order identifier |

### Attribute Columns
| Column Name | Data Type | Nullable | Valid Values | Description |
|-------------|-----------|----------|--------------|-------------|
| `order_date` | DATE | No | [Any date] | Date order was placed |
| `order_amount` | DECIMAL(18,2) | No | [Positive numbers] | Total order amount in USD |
| `order_status` | STRING | No | `complete`, `pending`, `cancelled`, `refunded` | Current status of order |
| `region` | STRING | Yes | `NA`, `EMEA`, `APAC` | Geographic region |
| `payment_method` | STRING | No | `credit_card`, `paypal`, `bank_transfer`, `check` | Method of payment |

### Time Columns
| Column Name | Data Type | Grain | Timezone | Description |
|-------------|-----------|-------|----------|-------------|
| `created_at` | TIMESTAMP | Second | UTC | When record was created in source system |
| `updated_at` | TIMESTAMP | Second | UTC | Last modification timestamp |

### Sensitive Columns
| Column Name | Classification | Masking | Access Restrictions |
|-------------|-----------------|---------|-------------------|
| `email` | PII | Redact domain in non-prod | Senior analysts + approval |
| `phone` | PII | Show last 4 digits only | Senior analysts + approval |
| `home_address` | PII | Redact completely | Restricted access |

---

## Data Quality

### Quality Metrics
| Metric | Threshold | Check Frequency | Status |
|--------|-----------|-----------------|--------|
| Null Rate in Key Columns | < 5% | Daily | ✓ Pass |
| Duplicate Rate | < 0.1% | Daily | ✓ Pass |
| Freshness | < 24 hours | Hourly | ✓ Pass |
| Referential Integrity | 100% | Daily | ✓ Pass |

### Known Data Quality Issues
- **Issue 1:** [Describe known issue, impact, and workaround]
  - Impact: Medium
  - Workaround: Filter out records where [condition]
  - Target Fix Date: [Date]

- **Issue 2:** [Description]
  - Impact: Low
  - Workaround: [How to handle]

### Data Validation Rules
```sql
-- Rule 1: Order amount must be positive
SELECT COUNT(*) FROM orders WHERE order_amount <= 0;  -- Should return 0

-- Rule 2: Order date cannot be in future
SELECT COUNT(*) FROM orders WHERE order_date > CURRENT_DATE;  -- Should return 0

-- Rule 3: Customer must exist in dim_customer
SELECT COUNT(*)
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;  -- Should return 0
```

### Data Profiling Results
- **Distinct Values:** [count by column]
- **Min/Max Values:** [Range analysis]
- **Distribution:** [Skew/outliers]
- **Last Profiled:** [Date]

---

## Security & Access

### Classification
- **Level:** INTERNAL / CONFIDENTIAL / PUBLIC
- **Regulations:** GDPR, CCPA, SOX
- **Approval Required:** Yes / No

### Access Control
| Role | Permission | Requires Approval | Notes |
|------|-----------|------------------|-------|
| Data Analyst | SELECT | No | Read-only access |
| Senior Analyst | SELECT, INSERT, UPDATE | Yes | Confidential data requires approval |
| Data Steward | FULL | No | Can modify metadata and access |
| PII Handler | SELECT (PII columns) | Yes | Must have PII certification |

### Masking Rules
- Non-production environments: [Specify masking per sensitive column]
- Audit Logging: All PII access logged with user/timestamp
- Export Restrictions: Encrypted format only, requires VPN

### Compliance Requirements
- [GDPR: Right to be forgotten - customer records must be deletable]
- [SOX: Read access logs maintained for 3 years]
- [HIPAA: If applicable - encryption and access controls]

---

## Lineage

### Upstream Dependencies
```
Source System (ERP)
    ↓
Raw Layer (raw_orders)
    ↓
Staging Layer (stg_orders)
    ↓
Marts Layer (fct_orders, dim_customer)
```

### Downstream Consumers
| Consumer | Type | Frequency | Owner |
|----------|------|-----------|-------|
| Revenue Dashboard | Dashboard | Real-time | BI Team |
| CFO Weekly Report | Report | Weekly | Finance Team |
| Customer Analytics | Data Product | Daily | Analytics Team |

### Column Lineage
| Target Column | Source Table | Source Column | Transformation |
|---------------|--------------|---------------|-----------------|
| `customer_id` | raw_orders | customer_id | Direct mapping |
| `order_amount` | raw_orders | amount | Multiply by exchange rate |
| `region` | dim_customer | territory | Lookup from dimension |

---

## Known Issues

### Current Issues
1. **High Null Rate in Payment Method**
   - Severity: Medium
   - Cause: Legacy system integration incomplete
   - Workaround: Filter out NULL payment methods
   - Target Resolution: Q4 2025

2. **Data Lag During Month-End**
   - Severity: Low
   - Cause: ERP processing heavy month-end transactions
   - Workaround: Use previous day's data for month-end reports
   - Impact: Reports delayed 2-4 hours on last day of month

### Deprecated Columns
| Column | Reason | Replacement | Deprecation Date |
|--------|--------|-------------|------------------|
| `legacy_id` | System retirement | `customer_id` | 2025-06-01 |

---

## Change Log

### Recent Changes
| Date | Change | Reason | Owner |
|------|--------|--------|-------|
| 2025-11-19 | Added `payment_method` column | Support new payment options | Finance Team |
| 2025-10-15 | Increased order_amount precision to 18,2 | Support high-value transactions | Accounting |
| 2025-09-20 | Created Gold certification | Passed all DQ checks | Data Governance |

### Planned Changes
- **Q4 2025:** Add `customer_segment` column for market analysis
- **Q1 2026:** Archive orders older than 5 years
- **Q1 2026:** Implement real-time refresh (currently daily)

---

## Related Documentation

- **dbt Documentation:** [Link to dbt docs]
- **Data Lineage Diagram:** [Link to visualization]
- **Data Quality Dashboard:** [Link to monitoring]
- **Access Request Form:** [Link to process]
- **Training Materials:** [Link to resources]

---

## Contact & Support

**Primary Contact:** [Name] - [Team] - [Email]
**Secondary Contact:** [Name] - [Team] - [Email]
**Data Governance Team:** [Email]
**Report Issues:** [Jira/GitHub link]

---

*This data dictionary should be reviewed and updated quarterly or whenever schema changes occur.*
