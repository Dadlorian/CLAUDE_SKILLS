# Clinical Data Warehouse Design Guide

## Planning Phase

### Requirements Gathering

**Stakeholder Interviews:**
- Executive leadership: Strategic KPIs, regulatory reporting
- Clinical leaders: Quality measures, clinical outcomes
- IT: Technical constraints, security, compliance
- Analytics team: Data access, tools, refresh frequency
- End users: Reports, dashboards, self-service needs

**Use Case Prioritization:**
```
High Priority (Phase 1):
- Quality measure reporting (HEDIS, eCQM)
- Population health dashboards
- Utilization analytics

Medium Priority (Phase 2):
- Predictive analytics (readmission, no-show)
- Provider performance
- Financial analytics

Low Priority (Phase 3):
- Advanced ML models
- Research datasets
- Patient-level dashboards
```

### Source System Assessment

**Inventory:**
- EHR (Epic, Cerner, etc.)
- Practice management
- Laboratory systems
- Pharmacy systems
- Claims/billing
- ADT feed
- FHIR APIs

**Data Quality Assessment:**
```python
# Assess data quality of source systems
source_assessment = {
    'Epic EHR': {
        'completeness': 0.95,
        'timeliness': '15min lag',
        'accuracy': 'High',
        'consistency': 'High',
        'extract_method': 'Clarity views',
        'refresh_frequency': 'Nightly'
    },
    'Lab System': {
        'completeness': 0.98,
        'timeliness': '30min lag',
        'accuracy': 'Very High',
        'consistency': 'High',
        'extract_method': 'HL7 feeds',
        'refresh_frequency': 'Real-time'
    }
}
```

## Architecture Design

### Reference Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Source Systems                       │
│  EHR | Labs | Pharmacy | Claims | ADT | FHIR APIs   │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│              Integration Layer                       │
│  HL7 Processing | File Ingestion | API Connectors   │
│           CDC | Event Streaming                      │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│              Staging Layer (Raw)                     │
│         Bronze: Immutable source copies              │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│         Transform & Cleanse Layer                    │
│  Silver: Validated, conformed, de-duplicated data    │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│       Enterprise Data Warehouse (EDW)                │
│  Gold: Curated dimensions and facts                  │
│  • dim_patient | dim_provider | dim_location         │
│  • fact_encounter | fact_diagnosis | fact_lab        │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│              Data Marts                              │
│  Clinical | Financial | Operational | Research       │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│          Analytics & BI Layer                        │
│  Tableau | Power BI | OMOP | ML Platform             │
└─────────────────────────────────────────────────────┘
```

### Technology Stack Selection

**Cloud vs. On-Premises:**
```
Cloud (Recommended for most):
+ Scalability
+ Managed services
+ Pay-as-you-go
+ Built-in HA/DR
- Data egress costs
- Compliance complexity

On-Premises:
+ Full control
+ No data egress
+ Existing infrastructure
- Capital expense
- Maintenance overhead
```

**Platform Options:**
```
Snowflake:
- Best for: Multi-cloud, separation of compute/storage
- Pros: Easy scaling, time travel, data sharing
- Cons: Cost at scale

Google BigQuery:
- Best for: Google Cloud ecosystem, serverless
- Pros: No infrastructure, ML integration
- Cons: Vendor lock-in

AWS Redshift:
- Best for: AWS ecosystem, tight integration
- Pros: Mature, Spectrum for S3 data
- Cons: Cluster management

Azure Synapse:
- Best for: Microsoft ecosystem
- Pros: Unified analytics, serverless option
- Cons: Complexity
```

## Data Modeling

### Dimensional Model Design (Kimball)

**Star Schema Example: Encounters**
```sql
-- Fact Table
CREATE TABLE fact_encounter (
    encounter_key BIGINT PRIMARY KEY,
    patient_key BIGINT,          -- FK
    provider_key BIGINT,         -- FK
    location_key BIGINT,         -- FK
    admission_date_key INT,      -- FK
    discharge_date_key INT,      -- FK
    drg_key INT,                 -- FK
    payer_key BIGINT,            -- FK

    -- Degenerate dimensions
    encounter_id VARCHAR(50),

    -- Measures
    length_of_stay DECIMAL(10,2),
    total_charges DECIMAL(15,2),
    total_payments DECIMAL(15,2),

    -- Flags
    readmission_flag BOOLEAN,
    readmission_30d_flag BOOLEAN,

    -- Audit
    source_system VARCHAR(50),
    etl_insert_date TIMESTAMP,
    etl_update_date TIMESTAMP
);

-- Dimension: Patient (SCD Type 2)
CREATE TABLE dim_patient (
    patient_key BIGINT PRIMARY KEY,
    mrn VARCHAR(50),
    enterprise_mrn VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    date_of_death DATE,
    gender_code VARCHAR(10),
    race_code VARCHAR(50),
    ethnicity_code VARCHAR(50),

    -- SCD Type 2
    effective_start_date DATE,
    effective_end_date DATE,
    current_flag BOOLEAN,
    version INT,

    -- Audit
    source_system VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP
);
```

**Slowly Changing Dimensions:**
```
Type 0: No change (retain original)
  Example: Date of birth

Type 1: Overwrite (no history)
  Example: Phone number (if history not needed)

Type 2: Add new row (full history)
  Example: Address, PCP assignment
  Columns: effective_start_date, effective_end_date, current_flag

Type 3: Add new column (limited history)
  Example: current_address, prior_address

Type 4: Add history table
  Example: Separate patient_history table
```

### Conformed Dimensions

**Master Data Management:**
```sql
-- Shared across all fact tables
-- Single source of truth

CREATE TABLE dim_patient_conformed AS (
    -- Enterprise-wide patient dimension
    -- Used by clinical, financial, operational marts
);

CREATE TABLE dim_provider_conformed AS (
    -- Validated against NPI registry
    -- Shared across all analytics
);

CREATE TABLE dim_date AS (
    -- Date dimension with attributes
    -- Fiscal calendar, holidays, business days
);
```

## ETL Development

### ETL Framework

```python
class ETLPipeline:
    def __init__(self, source, target, transformation_logic):
        self.source = source
        self.target = target
        self.transformation_logic = transformation_logic
        self.error_log = []

    def extract(self):
        """Extract data from source"""
        try:
            if self.source['type'] == 'database':
                data = self.extract_from_database()
            elif self.source['type'] == 'file':
                data = self.extract_from_file()
            elif self.source['type'] == 'api':
                data = self.extract_from_api()

            log_extraction(source=self.source, row_count=len(data))
            return data

        except Exception as e:
            self.error_log.append({
                'step': 'extract',
                'error': str(e),
                'timestamp': datetime.now()
            })
            raise

    def transform(self, data):
        """Apply business rules and transformations"""
        # Data quality checks
        data = self.validate_data_quality(data)

        # Apply business rules
        for rule in self.transformation_logic:
            data = rule(data)

        # Lookups (FK resolution)
        data = self.resolve_foreign_keys(data)

        # Derived columns
        data = self.calculate_derived_fields(data)

        return data

    def load(self, data):
        """Load to target"""
        if self.target['load_type'] == 'full':
            self.truncate_and_load(data)
        elif self.target['load_type'] == 'incremental':
            self.upsert(data)
        elif self.target['load_type'] == 'scd2':
            self.scd2_load(data)

        log_load(target=self.target, row_count=len(data))

    def validate_data_quality(self, data):
        """DQ checks"""
        # Null checks
        critical_fields = self.target.get('required_fields', [])
        for field in critical_fields:
            null_count = data[field].isna().sum()
            if null_count > 0:
                log_dq_issue(
                    field=field,
                    issue='null_values',
                    count=null_count
                )

        # Range checks
        # Format checks
        # Business rule checks

        return data

    def run(self):
        """Execute ETL pipeline"""
        try:
            data = self.extract()
            data = self.transform(data)
            self.load(data)

            log_success(pipeline=self.source['name'])

        except Exception as e:
            log_failure(pipeline=self.source['name'], error=str(e))
            send_alert(pipeline=self.source['name'], error=str(e))
            raise
```

### Incremental Load Strategy

```sql
-- Track last processed record
CREATE TABLE etl_watermark (
    source_table VARCHAR(100) PRIMARY KEY,
    last_processed_timestamp TIMESTAMP,
    last_processed_id BIGINT,
    last_run_date TIMESTAMP
);

-- Extract delta
SELECT *
FROM source_system.encounters
WHERE last_modified_date > (
    SELECT last_processed_timestamp
    FROM etl_watermark
    WHERE source_table = 'encounters'
);

-- Update watermark after successful load
UPDATE etl_watermark
SET last_processed_timestamp = :max_timestamp,
    last_run_date = CURRENT_TIMESTAMP
WHERE source_table = 'encounters';
```

## Data Quality Management

### DQ Framework

```python
class DataQualityValidator:
    def __init__(self, dataset, rules):
        self.dataset = dataset
        self.rules = rules
        self.issues = []

    def check_completeness(self):
        """Required fields populated"""
        for field in self.rules['required_fields']:
            null_pct = (self.dataset[field].isna().sum() /
                        len(self.dataset) * 100)

            if null_pct > self.rules['max_null_pct']:
                self.issues.append({
                    'field': field,
                    'check': 'completeness',
                    'null_pct': null_pct,
                    'threshold': self.rules['max_null_pct']
                })

    def check_validity(self):
        """Values in expected range/format"""
        for field, spec in self.rules['validity_rules'].items():
            if spec['type'] == 'range':
                out_of_range = (
                    (self.dataset[field] < spec['min']) |
                    (self.dataset[field] > spec['max'])
                ).sum()

                if out_of_range > 0:
                    self.issues.append({
                        'field': field,
                        'check': 'validity',
                        'issue': 'out_of_range',
                        'count': out_of_range
                    })

    def check_consistency(self):
        """Logical consistency"""
        # Discharge >= admission
        invalid_dates = (
            self.dataset['discharge_date'] <
            self.dataset['admission_date']
        ).sum()

        if invalid_dates > 0:
            self.issues.append({
                'check': 'consistency',
                'issue': 'discharge_before_admission',
                'count': invalid_dates
            })

    def check_accuracy(self):
        """Compare to known values"""
        # Example: Validate NPI checksum
        # Compare to reference data

    def generate_report(self):
        """DQ scorecard"""
        return {
            'dataset': self.dataset.name,
            'row_count': len(self.dataset),
            'issues': self.issues,
            'quality_score': self.calculate_quality_score()
        }
```

## Performance Optimization

### Indexing Strategy

```sql
-- Fact table indexes
CREATE INDEX idx_fact_enc_patient
    ON fact_encounter(patient_key);

CREATE INDEX idx_fact_enc_date
    ON fact_encounter(admission_date_key);

CREATE INDEX idx_fact_enc_provider
    ON fact_encounter(provider_key);

-- Covering index for common query
CREATE INDEX idx_fact_enc_coverage
    ON fact_encounter(patient_key, admission_date_key)
    INCLUDE (encounter_type, drg_code, length_of_stay, total_charges);

-- Filtered index
CREATE INDEX idx_fact_enc_recent
    ON fact_encounter(admission_date_key)
    WHERE admission_date_key >= 20200101;
```

### Partitioning

```sql
-- Partition by date
CREATE TABLE fact_encounter_partitioned (
    -- columns
) PARTITION BY RANGE (admission_date_key) (
    PARTITION p_2020 VALUES LESS THAN (20210101),
    PARTITION p_2021 VALUES LESS THAN (20220101),
    PARTITION p_2022 VALUES LESS THAN (20230101),
    PARTITION p_2023 VALUES LESS THAN (20240101),
    PARTITION p_2024 VALUES LESS THAN (20250101)
);

-- Partition pruning enables faster queries
SELECT * FROM fact_encounter_partitioned
WHERE admission_date_key BETWEEN 20230101 AND 20231231;
-- Only scans p_2023 partition
```

### Aggregate Tables

```sql
-- Pre-aggregated monthly summaries
CREATE TABLE agg_patient_monthly_summary AS
SELECT
    patient_key,
    DATE_TRUNC('month', encounter_date) AS month,
    COUNT(DISTINCT encounter_key) AS encounter_count,
    SUM(total_charges) AS total_charges,
    AVG(length_of_stay) AS avg_los
FROM fact_encounter
GROUP BY patient_key, DATE_TRUNC('month', encounter_date);

-- Refreshed monthly
```

## Security & Compliance

### HIPAA Compliance

```
Technical Safeguards:
- Encrypt data at rest (AES-256)
- Encrypt data in transit (TLS 1.2+)
- Access controls (RBAC)
- Audit logging
- Automatic logoff

Administrative Safeguards:
- BAA with vendors
- Workforce training
- Risk assessments
- Policies & procedures

Physical Safeguards:
- Data center security
- Workstation security
- Device controls
```

### Row-Level Security

```sql
-- Create security view
CREATE VIEW vw_encounter_secure AS
SELECT e.*
FROM fact_encounter e
WHERE e.provider_key IN (
    SELECT provider_key
    FROM user_provider_access
    WHERE user_id = CURRENT_USER
);

-- Grant access to view only
GRANT SELECT ON vw_encounter_secure TO analyst_role;
```

## Deployment & Operations

### Deployment Checklist

```
Pre-Deployment:
□ Code review completed
□ Unit tests passed
□ Integration tests passed
□ Data quality validation
□ Performance testing
□ Security review
□ Documentation updated

Deployment:
□ Backup current version
□ Deploy to staging
□ Smoke tests in staging
□ Deploy to production
□ Validation queries
□ Monitor for errors

Post-Deployment:
□ Performance monitoring
□ User acceptance testing
□ Document lessons learned
```

### Monitoring

```python
# ETL monitoring dashboard
monitoring_metrics = {
    'etl_success_rate': 'Successful runs / Total runs',
    'data_freshness': 'Hours since last update',
    'row_count_variance': 'Deviation from expected volume',
    'dq_score': 'Composite data quality score',
    'query_performance': 'Average query execution time',
    'storage_utilization': 'GB used / GB allocated'
}

# Alerts
if etl_success_rate < 0.98:
    send_alert('ETL Success Rate Below Threshold')

if data_freshness > 24:  # hours
    send_alert('Data Staleness Alert')
```

---

*Clinical Data Warehouse Design Guide - Comprehensive guide to designing and implementing healthcare data warehouses.*
