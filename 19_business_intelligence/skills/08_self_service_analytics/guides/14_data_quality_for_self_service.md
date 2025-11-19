# Data Quality for Self-Service Analytics Guide

## Introduction

Data quality is the foundation of self-service analytics. When data is trustworthy, analysts can self-serve confidently. When it's not, self-service creates problems at scale. This guide provides a comprehensive approach to ensuring high-quality data in a self-service environment.

The challenge: Traditional data quality approaches don't scale with self-service because more users creating more analyses means more opportunities for quality issues to propagate.

## Prerequisites

Before starting, ensure you have:
- Data warehouse or data lake operational
- Data governance framework in place
- Self-service BI tool with user permissions
- Data quality tools (Great Expectations, dbt tests, etc.)
- Data stewards identified for key datasets
- Monitoring infrastructure
- 1-2 month implementation timeline

## The Self-Service Quality Paradox

### The Problem

```yaml
Traditional Analytics (Expert-Driven):
  - Few users create analyses
  - Errors caught before publishing
  - Quality gate at analysis creation
  - Limited impact of mistakes

Self-Service Analytics (User-Driven):
  - Many users create analyses
  - No review before publishing
  - Quality gate must be at data layer
  - Mistakes propagate to many stakeholders

Impact:
  1 bad metric in self-service can affect:
    - 100+ dashboards
    - 50+ users
    - Executive decisions
    - Financial impact in hours (not days)
```

### The Solution: Quality by Design

```yaml
Strategy:
  1. Move quality upstream (to the data)
  2. Make quality visible (monitor continuously)
  3. Make quality easy (simple to trust)
  4. Make quality automatic (test everything)
  5. Create accountability (clear ownership)
```

## Phase 1: Assessment (Week 1)

### Step 1: Data Quality Baseline

```yaml
Current State Assessment:

Data Accuracy:
  Questions:
    - How many reports have data discrepancies?
    - What's the error rate in key metrics?
    - How often do we catch mistakes after publishing?

  How to Measure:
    - Audit 10 high-impact reports manually
    - Compare BI metrics to source systems
    - Track data quality issues reported by users

Data Completeness:
  Questions:
    - What % of expected records are present?
    - Are there missing time periods?
    - Are all dimensions populated?

  How to Measure:
    - Count records vs baseline expectations
    - Check for NULL values
    - Verify date ranges

Data Timeliness:
  Questions:
    - How fresh is the data?
    - Are there SLAs being missed?
    - Do users know when data was last updated?

  How to Measure:
    - Track ETL execution times
    - Monitor data freshness
    - Check update notification frequency

Data Consistency:
  Questions:
    - Do different tables agree on customer count?
    - Are customer IDs consistent?
    - Are there conflicting dimension definitions?

  How to Measure:
    - Compare customer counts across tables
    - Validate referential integrity
    - Check for duplicate rows

Example Assessment Output:
  Overall Quality Score: 65/100
  Accuracy: 70 (some calculation errors)
  Completeness: 80 (few NULL values)
  Timeliness: 85 (mostly up to date)
  Consistency: 45 (significant mismatches)

  Top Issues:
  1. Customer dimension conflicts (3 definitions)
  2. Missing contract records (2% of expected)
  3. Stale product mapping (6 months old)
```

### Step 2: Identify Quality Risks

```yaml
Risk Assessment Framework:

High Risk Datasets:
  - Directly used in self-service dashboards
  - Impact executive decisions
  - Used in financial reporting
  - Widely accessed by business users

Medium Risk Datasets:
  - Frequently used but not critical
  - Some derived metrics depend on them
  - Moderate user impact

Low Risk Datasets:
  - Rarely accessed
  - Limited downstream impact
  - Experimental or archived

Quality Risk Matrix:

            High Impact    Medium Impact    Low Impact
High Error  CRITICAL      HIGH             MEDIUM
            (Fix first)   (Fix second)     (Monitor)

Medium Err  HIGH          MEDIUM           LOW
            (Fix second)  (Monitor)        (Archive/Clean)

Low Error   MEDIUM        LOW              LOW
            (Monitor)     (Ignore)         (Ignore)

Priority Action List:
1. Address CRITICAL (1-2 weeks)
2. Address HIGH (2-4 weeks)
3. Monitor MEDIUM (ongoing)
4. Ignore LOW (lower priority)
```

## Phase 2: Framework Design (Weeks 2-3)

### Step 1: Define Data Quality Dimensions

```yaml
The 6 Key Dimensions:

1. ACCURACY: Data correctly represents reality
   Measures:
     - Are customer names spelled correctly?
     - Do calculations match their definitions?
     - Do metrics match source system values?

   Targets:
     - High-risk: 99.9% accuracy
     - Medium-risk: 99% accuracy
     - Low-risk: 95% accuracy

2. COMPLETENESS: No missing data
   Measures:
     - % of expected records present
     - % non-NULL values for key fields
     - Months/days with data coverage

   Targets:
     - High-risk: 100% completeness
     - Medium-risk: 99% completeness
     - Low-risk: 95% completeness

3. TIMELINESS: Data is fresh and current
   Measures:
     - Data age (hours/days since update)
     - ETL execution time
     - SLA adherence

   Targets:
     - High-risk: Data within 4 hours
     - Medium-risk: Data within 24 hours
     - Low-risk: Data within 1 week

4. CONSISTENCY: Data aligns across systems
   Measures:
     - Referential integrity checks
     - Cross-table match rates
     - Definition alignment

   Targets:
     - High-risk: 100% consistency
     - Medium-risk: 99% consistency
     - Low-risk: 95% consistency

5. VALIDITY: Data is in valid formats
   Measures:
     - Format validation rate
     - Range validation rate
     - Type checking rate

   Targets:
     - All levels: 100% validity

6. UNIQUENESS: No unwanted duplicates
   Measures:
     - Duplicate row rate
     - Primary key violations
     - Dimension cardinality

   Targets:
     - All levels: 0% unwanted duplicates
```

### Step 2: Create Quality SLAs

```yaml
Service Level Agreements:

Core Metrics Tables:
  Data Freshness: Updated by 9 AM daily
  Accuracy: 99.9% (verified by weekly audit)
  Completeness: 100% (no missing days)
  Availability: 99.95% (no unplanned downtime)

  SLA Breach Response:
    < 1 hour issue: Acknowledge and investigate
    1-4 hour issue: Provide status update
    > 4 hour issue: Executive notification

  Escalation:
    1 breach: Investigation
    2 breaches/month: Root cause analysis
    3 breaches/month: Redesign review

Customer Dimension:
  Data Freshness: Updated within 2 hours
  Accuracy: 99% (reviewed monthly)
  Completeness: 99% (document any gaps)

  Known Issues:
    - Duplicate customers (0.1% of records)
    - Merged accounts lag 24 hours
    - International regions updated weekly

Product Catalog:
  Data Freshness: Updated within 1 day
  Accuracy: 100% (manually reviewed weekly)
  Completeness: 99% (new products may lag 1 day)

  Known Limitations:
    - Categories updated manually
    - Historical product changes documented
    - Deprecations marked but not removed

Template for Each Dataset:
  Name: [Dataset]
  Owner: [Team]
  Business Criticality: [High/Medium/Low]

  SLAs:
    Freshness: [How often updated]
    Accuracy: [%]
    Completeness: [%]
    Availability: [%]

  Known Issues: [List]
  Limitations: [List]
  Contact: [Email]
```

## Phase 3: Testing Strategy (Weeks 3-4)

### Step 1: Implement Automated Tests

```yaml
Test Pyramid for Data:

            /\
           /  \   COMPLEX
          / UX  \ Meaningful
         /       \ Tests
        /         \
       /__________\
      /            \
     / INTEGRATION  \
    / Multi-table   \
   / Cross-system   \
  /__________________\
 /                    \
/ UNIT TESTS          \
/ Single table        \
/ Focused assertions  \
/____________________\

Unit Tests (Foundation):
  Test individual columns and tables
  Easy to write, fast to run
  Should be majority of tests

  Examples:
    - No NULL values in customer_id
    - No duplicate customer_id values
    - Revenue >= 0
    - Date values in valid range
    - Email format is valid
    - Status field in ('active', 'inactive')

Integration Tests (Middle):
  Test relationships between tables
  Moderate complexity
  Catch cross-table issues

  Examples:
    - Every order has valid customer_id
    - Shipment date >= order date
    - Billing address matches customer region
    - Product revenue sums to order total
    - Customer segment classification makes sense

Complex Tests (Top):
  Test business logic and semantics
  More complex to write
  Often need domain expertise

  Examples:
    - Annual revenue ~ 12 * monthly revenue
    - Customer LTV > total customer purchases
    - Churn rate between 0 and 1
    - Gross margin = (price - cost) / price

Implementation Tools:

dbt Tests:
  models:
    customers:
      - name: customer_id
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - unique
          - not_null
          - regex_match: pattern

Great Expectations:
  expectations:
    - expect_column_values_to_not_be_null
    - expect_column_values_to_be_unique
    - expect_column_values_to_be_in_set
    - expect_column_values_to_match_regex
    - expect_compound_columns_to_be_unique

SQL Assertions:
  SELECT
    CASE
      WHEN COUNT(*) !=
           LAG(COUNT(*)) OVER (ORDER BY date)
      THEN 'FAILURE: Record count dropped'
      ELSE 'PASS'
    END as quality_check
  FROM daily_metrics
  GROUP BY date
```

### Step 2: Create Test Suite by Dataset

```yaml
Customer Dimension Tests:

Row-Level Tests:
  - customer_id is unique
  - customer_id is not null
  - email matches format
  - phone_number matches format
  - created_date <= updated_date
  - country_code in valid values
  - status in ('active', 'inactive', 'deleted')

Aggregate Tests:
  - Row count stable (alert if > 20% change)
  - No customer_id appears > 1 time
  - All countries have valid codes
  - Average revenue >= historical average

Referential Tests:
  - All orders reference valid customers
  - All subscriptions reference valid customers
  - All support tickets reference valid customers

Distribution Tests:
  - Revenue distribution stable
  - Geographic distribution stable
  - Industry distribution stable

Revenue Fact Table Tests:

Row-Level Tests:
  - revenue_amount > 0
  - currency_code is valid (USD, EUR, etc.)
  - revenue_date is valid
  - transaction_id is not null
  - customer_id references valid customer
  - product_id references valid product

Aggregate Tests:
  - Total daily revenue is stable
  - No negative revenue
  - Monthly trend is consistent with historical

Freshness Tests:
  - Data updated within 4 hours
  - Latest date is today (or expected)
  - No future-dated records

Consistency Tests:
  - Sum of fact revenue = sum of dimension revenue
  - Merchant revenue = sum of seller payments
  - Customer revenue = sum of order revenue

Completeness Tests:
  - All days in range have records
  - All customers have revenue records
  - No gaps in transaction sequences
```

## Phase 4: Monitoring and Alerting (Weeks 4+)

### Step 1: Create Monitoring Dashboard

```yaml
Executive Dashboard Metrics:

Real-Time Monitoring:
  - Data freshness (% tables updated on time)
  - Test pass rate (% of tests passing)
  - Data availability (% tables accessible)
  - SLA compliance (% within SLAs)

Trending Metrics:
  - Test pass rate over time
  - Mean time to repair issues
  - Issues by category
  - Quality score by dataset

Drill-Down Dashboards:

Dataset Health:
  - Last updated timestamp
  - Row count vs baseline
  - NULL value percentage
  - Duplicate row percentage
  - Test status (pass/fail)
  - Known issues (documented)

Test Details:
  - Test name and status
  - Failure details
  - Affected queries
  - Recommended action

Issues Tracker:
  - Open issues
  - Resolution time
  - Root cause analysis
  - Prevention measures
```

### Step 2: Set Up Alerting

```yaml
Alert Strategy:

Severity Levels:

CRITICAL (Page team immediately):
  - Data unavailable (no recent updates)
  - Core metric calculation broken
  - > 5% data quality failure
  - Data integrity violation
  Response: < 30 minutes

HIGH (Alert within hours):
  - > 2% data quality failure
  - SLA approaching breach
  - Missing data from expected source
  Response: < 4 hours

MEDIUM (Track for investigation):
  - 1-2% quality failure
  - Edge case data issues
  - Minor calculation differences
  Response: < 1 day

LOW (Track for trending):
  - < 1% quality issues
  - Informational alerts
  - Non-critical data gaps
  Response: Next business day

Alert Routing:

CRITICAL:
  - Slack #data-critical-alerts
  - Page on-call engineer
  - Notify data lead
  - Auto-escalate after 30 min

HIGH:
  - Slack #data-team
  - Email data steward
  - Auto-create ticket

MEDIUM/LOW:
  - Slack #data-insights
  - Track in dashboard

Example Alert Conditions:

```sql
-- Table freshness alert
SELECT
  table_name,
  MAX(updated_at) as last_update,
  CURRENT_TIMESTAMP - MAX(updated_at) as age
FROM table_metadata
GROUP BY table_name
HAVING age > INTERVAL '4 hours'

-- Quality score alert
SELECT
  dataset_name,
  quality_score,
  CASE
    WHEN quality_score < 0.95 THEN 'CRITICAL'
    WHEN quality_score < 0.98 THEN 'HIGH'
    ELSE 'OK'
  END as severity
FROM data_quality_scores

-- Duplicate detection
SELECT
  table_name,
  primary_key_value,
  COUNT(*) as duplicates
FROM all_tables
GROUP BY table_name, primary_key_value
HAVING COUNT(*) > 1
```

## Phase 5: Self-Service User Guidelines

### Step 1: Quality Indicators in BI Tools

```yaml
Implementing Quality Badges:

Dataset-Level Indicators:
  ✓ Certified: High-quality, production-ready
  ⚠ Approved: Good quality, use with caution
  ? Experimental: In testing, may change
  X Deprecated: No longer maintained

Metric-Level Indicators:
  Last Verified: "2025-01-15"
  Data Freshness: "Updated hourly"
  Accuracy Level: "99.9%"
  Known Issues: "See documentation"

  Example Metric Card:
  ┌─────────────────────────────────┐
  │ Annual Recurring Revenue (ARR)   │
  │ ✓ CERTIFIED                      │
  │                                  │
  │ Owner: Revenue Analytics         │
  │ Last Updated: Today, 9:00 AM    │
  │ Accuracy: 99.9%                 │
  │ Status: Production               │
  │                                  │
  │ [View Definition] [See Lineage]  │
  │ [Report Issue]   [Suggest Change]│
  └─────────────────────────────────┘

Status Meanings:
  CERTIFIED:
    - Meets high quality standards
    - Production ready
    - Safe for executive reporting
    - Use in important decisions

  APPROVED:
    - Good quality, some limitations
    - Production ready with caveats
    - Noted issues documented
    - Check documentation before use

  EXPERIMENTAL:
    - Under testing
    - May change or be removed
    - Not for critical decisions
    - Feedback welcome

  DEPRECATED:
    - No longer maintained
    - Use alternative metric instead
    - Kept for historical reference
    - No new uses
```

### Step 2: User Guidelines

```yaml
For Analysts Using Self-Service Data:

Before Creating Analyses:
  1. Check dataset certification level
  2. Read data dictionary and known issues
  3. Verify data freshness
  4. Understand any limitations
  5. Reach out if questions

When Quality Issues Arise:
  1. Note the specific problem
  2. Provide example (row IDs, values)
  3. Report in #data-quality-issues channel
  4. Include screenshot of problem
  5. Tag dataset owner
  6. Expected response: within 24 hours

For Power Users Creating Metrics:
  1. Propose metric to data team first
  2. Document business logic clearly
  3. Include test cases and examples
  4. Get peer review before publishing
  5. Update databook with definition
  6. Add to monitoring/alerting

Escalation Path for Data Issues:
  1. Check data documentation
  2. Ask in #data-team Slack channel
  3. File ticket in data-issues project
  4. Page on-call if blocking critical work
```

## Common Data Quality Issues and Solutions

```yaml
Issue: Duplicate Customer Records
  Symptoms:
    - Customer count doesn't match CRM
    - Revenue double-counted for merged customers
  Root Cause:
    - Account merge logic not applied
    - Data refresh timing issue
  Solution:
    - Add deduplication logic
    - Implement customer merge tracking
    - Test before production
  Prevention:
    - Monitor customer_id uniqueness daily
    - Alert on unexpected duplicate increase

Issue: Missing Recent Data
  Symptoms:
    - Reports end 2-3 days ago
    - ETL delayed without notification
  Root Cause:
    - ETL timeout or failure
    - Source system unavailable
    - Pipeline queue backlog
  Solution:
    - Implement retry logic
    - Increase timeout
    - Check source availability
  Prevention:
    - Monitor data freshness in real-time
    - Alert on SLA breach immediately

Issue: Metric Discrepancy
  Symptoms:
    - Different systems show different numbers
    - Calculation changes unexpectedly
  Root Cause:
    - Rounding differences
    - Timezone handling
    - Scope/filter differences
  Solution:
    - Document exact calculation
    - Add test with expected values
    - Create cross-system reconciliation
  Prevention:
    - Version metric definitions
    - Test all changes before deployment

Issue: Stale Reference Data
  Symptoms:
    - Product categories haven't updated in months
    - Customer tiers don't reflect reality
  Root Cause:
    - Manual process not maintained
    - No ownership assigned
    - Import job disabled
  Solution:
    - Restore automated import
    - Assign clear owner
    - Add monitoring/alert
  Prevention:
    - Auto-notify when data not refreshed
    - Require quarterly review
    - Track update frequency
```

## Best Practices

### Do's
- Test data quality automatically and continuously
- Make quality visible to all users
- Document all data limitations and issues
- Assign clear ownership for each dataset
- Test changes before deploying to production
- Monitor trends in quality metrics
- Communicate issues proactively
- Celebrate quality improvements

### Don'ts
- Rely on manual spot-checks
- Hide known data issues
- Deploy untested transformations
- Leave quality issues unresolved
- Change metric definitions without version control
- Ignore user-reported data issues
- Assume data quality is someone else's job
- Create quality rules without business input

## Tools and Technologies

```yaml
Data Quality Tools:

Great Expectations:
  - Open source
  - Extensive assertion library
  - Integration with dbt
  - Checkpoint validation

dbt Tests:
  - SQL-based assertions
  - Version controlled
  - Integrated with transforms
  - Runs in pipeline

Databand:
  - ETL monitoring
  - Anomaly detection
  - Impact analysis
  - Pipeline observability

dbt Cloud + Exposures:
  - Dashboard monitoring
  - Query monitoring
  - SLA management
  - Integration with BI tools

Custom Solutions:
  - SQL-based tests
  - Python quality checks
  - Business logic validation
```

## Conclusion

Data quality is not a one-time project but an ongoing practice. In self-service environments, quality must be built into the data, monitored continuously, and communicated clearly to users.

A comprehensive data quality program prevents mistakes from propagating at scale, builds user trust, and enables confident decision-making across the organization.

## Next Steps

1. Complete baseline quality assessment
2. Prioritize high-risk datasets
3. Define SLAs for critical data
4. Implement unit tests for top 5 datasets
5. Set up monitoring dashboard
6. Create user guidelines
7. Launch quality initiative
8. Iterate based on feedback
