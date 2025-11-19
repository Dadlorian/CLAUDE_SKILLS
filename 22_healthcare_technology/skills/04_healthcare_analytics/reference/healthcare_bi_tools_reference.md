# Healthcare Business Intelligence Tools Reference

## Overview

Healthcare BI tools transform clinical and operational data into actionable insights through interactive dashboards, reports, and analytics for stakeholders across the healthcare enterprise.

## Enterprise BI Platforms

### Tableau

**Strengths:**
- Intuitive drag-and-drop interface
- Powerful data visualization capabilities
- Strong healthcare customer base
- HIPAA-compliant (Tableau Server/Cloud)
- Integration with major data warehouses

**Healthcare Use Cases:**
- Executive dashboards (quality, utilization, financial)
- Population health analytics
- Clinical quality measure tracking
- Provider performance scorecards
- Operational dashboards (ED wait times, OR utilization)

**Tableau for Healthcare Features:**
```
- Pre-built healthcare accelerators
- HEDIS measure templates
- Hospital operations dashboards
- Population health starter kits
- Patient flow visualizations
- Geographic analysis (catchment area, SDOH)
```

**Example Dashboard Structure:**
```
Executive Quality Dashboard
├── KPI Summary (Top-level metrics)
│   ├── Overall Quality Score
│   ├── Star Rating
│   ├── Quality Measure Performance (%)
│   └── Trend vs. Prior Year
├── Measure Performance Detail
│   ├── By Measure (HEDIS, eCQM)
│   ├── By Provider/Location
│   └── By Payer Type
├── Care Gap Analysis
│   ├── Open Gaps by Measure
│   ├── Patients with Multiple Gaps
│   └── Gap Closure Trends
└── Drill-Down to Patient Lists
    └── Actionable patient-level data
```

**Tableau Calculations (Healthcare-Specific):**

```
// HEDIS Diabetes HbA1c Control Rate
[Numerator: HbA1c <8%] / [Denominator: All Diabetic Patients]

// 30-Day Readmission Rate
COUNTD(IF [Days Since Discharge] <= 30 AND [Readmitted] = TRUE
    THEN [Encounter ID] END) /
COUNTD([Index Discharge ID])

// Risk-Adjusted Admits per 1000
SUM([Admits]) / (SUM([Member Months]) / 12) * 1000 *
([Avg RAF Score] / [Member RAF Score])
```

**Tableau Server Deployment:**
- Row-level security (RLS) for PHI
- User authentication (SAML, LDAP)
- Scheduled extract refreshes
- Embed in portals/EHR
- Mobile access

### Power BI

**Strengths:**
- Tight integration with Microsoft ecosystem (Azure, SQL Server)
- Cost-effective (included with M365 E5)
- Strong data modeling with DAX
- Natural language Q&A
- AI-powered insights

**Healthcare Use Cases:**
- Departmental dashboards (clinical, operational)
- Financial analytics
- Supply chain analytics
- Staff productivity tracking
- Patient satisfaction analysis

**Power BI Healthcare Capabilities:**
```
- Azure Health Data Services integration
- FHIR connector
- Direct Query to Synapse/SQL
- Real-time dashboards
- Embedded analytics in web apps
- Power BI Report Server (on-premises)
```

**DAX Measures for Healthcare:**

```dax
// Total Cost PMPM
Total Cost PMPM :=
DIVIDE(
    SUM(Claims[Allowed Amount]),
    SUM(Enrollment[Member Months]),
    0
)

// Quality Measure Rate
Quality Rate :=
DIVIDE(
    COUNTROWS(FILTER(Patients, Patients[Numerator] = TRUE)),
    COUNTROWS(FILTER(Patients, Patients[Denominator] = TRUE)),
    0
)

// IP Admits per 1000
IP Admits per 1000 :=
DIVIDE(
    COUNTROWS(Encounters),
    SUM(Enrollment[Members]),
    0
) * 1000

// Year-over-Year Change
YoY Change :=
VAR CurrentYear = [Total Cost PMPM]
VAR PriorYear = CALCULATE([Total Cost PMPM], SAMEPERIODLASTYEAR(DateTable[Date]))
RETURN
DIVIDE(CurrentYear - PriorYear, PriorYear, 0)
```

**Power BI Architecture:**
```
Data Sources (EHR, Claims, Labs)
    ↓
Power BI Dataflows (ETL in cloud)
    ↓
Power BI Datasets (Semantic models)
    ↓
Power BI Reports
    ↓
Power BI Service (sharing, collaboration)
    ↓
Consumption (Web, mobile, Teams, embedded)
```

### Qlik Sense

**Strengths:**
- Associative analytics engine (explore without pre-defined paths)
- In-memory performance
- Self-service data discovery
- Strong data integration (Qlik Replicate for CDC)
- Governed self-service

**Healthcare Use Cases:**
- Ad-hoc analysis and exploration
- Revenue cycle analytics
- Claims processing analytics
- Clinical trial analytics
- Healthcare fraud detection

**Qlik Associative Model:**
```
Green = Selected
White = Associated (related data)
Gray = Excluded (not related to selection)

Example: Select "Diabetes" diagnosis
    → Associated: Related medications, providers, labs
    → Excluded: Unrelated encounters
```

**Qlik Script for Healthcare:**

```qlik
// Load encounters with diagnosis
Encounters:
LOAD
    EncounterID,
    PatientID,
    ProviderID,
    AdmissionDate,
    DischargeDate,
    DischargeDate - AdmissionDate AS LengthOfStay,
    PrimaryDRG,
    TotalCharges
FROM [lib://EDW/Encounters.qvd] (qvd);

// Classify LOS
LEFT JOIN (Encounters)
LOAD
    EncounterID,
    IF(LengthOfStay <= 2, 'Short',
       IF(LengthOfStay <= 5, 'Medium',
          IF(LengthOfStay <= 10, 'Long', 'Extended'))) AS LOS_Category
RESIDENT Encounters;

// Calculate readmissions
Readmissions:
LOAD
    PatientID,
    EncounterID AS IndexEncounter,
    DischargeDate
RESIDENT Encounters;

LEFT JOIN (Readmissions)
LOAD
    PatientID,
    EncounterID AS ReadmitEncounter,
    AdmissionDate AS ReadmitDate
RESIDENT Encounters;

// Flag 30-day readmissions
LEFT JOIN (Encounters)
LOAD
    IndexEncounter AS EncounterID,
    IF(ReadmitDate - DischargeDate <= 30 AND ReadmitDate - DischargeDate > 0,
       1, 0) AS Readmitted30Day
RESIDENT Readmissions;
```

### Looker

**Strengths:**
- LookML (version-controlled data modeling)
- Embedded analytics capabilities
- Real-time data access (no extracts)
- Git-based development workflow
- Google Cloud integration

**Healthcare Use Cases:**
- Embedded analytics in patient portals
- Clinical analytics for research
- Operational dashboards
- Patient engagement metrics
- Value-based care analytics

**LookML for Healthcare:**

```lookml
# Define diabetes cohort
view: diabetes_patients {
  sql_table_name: edw.fact_diagnosis ;;

  dimension: patient_key {
    type: number
    primary_key: yes
    sql: ${TABLE}.patient_key ;;
  }

  dimension: has_diabetes {
    type: yesno
    sql: ${TABLE}.diagnosis_code LIKE 'E11%' ;;
  }

  measure: count_diabetic {
    type: count_distinct
    sql: ${patient_key} ;;
    filters: [has_diabetes: "yes"]
  }
}

# Define quality measure
explore: diabetes_quality {
  from: diabetes_patients

  join: lab_results {
    sql_on: ${diabetes_patients.patient_key} = ${lab_results.patient_key} ;;
    relationship: one_to_many
  }

  measure: hba1c_control_rate {
    type: number
    sql: 1.0 * ${lab_results.hba1c_controlled_count} / ${diabetes_patients.count_diabetic} ;;
    value_format_name: percent_1
  }
}
```

## Healthcare-Specific BI Tools

### Health Catalyst

**Product**: Data Operating System (DOS)

**Components:**
- Healthcare Data Warehouse (proprietary EDW)
- Analytics Applications (pre-built dashboards)
- Population Health (risk stratification, care mgmt)
- Financial & Operational Analytics

**Pre-Built Applications:**
```
Clinical:
- Sepsis Surveillance
- Readmission Reduction
- Length of Stay Optimization
- Clinical Quality Measures

Operational:
- OR Utilization
- ED Throughput
- Denials Management
- Labor Management

Financial:
- Service Line Profitability
- Payer Analytics
- Revenue Cycle

Population Health:
- Care Management
- Risk Stratification
- Care Gaps
```

**Health Catalyst Architecture:**
```
Source Systems
    ↓
Late-Binding EDW (adaptive schema)
    ↓
Healthcare-specific data marts
    ↓
Analytics Applications (dashboards)
    ↓
Population Health Tools
```

### Epic Healthy Planet

**Overview**: EHR-integrated population health and analytics platform

**Features:**
- Embedded in Epic workflows
- Real-time clinical data access
- Registries and cohort management
- Quality measure tracking
- Care gap identification
- Risk stratification

**Epic Reporting Tools:**

1. **SlicerDicer**: Self-service analytics
   - Drag-and-drop interface
   - Patient cohort building
   - Ad-hoc queries on Epic data
   - Export to Excel, Tableau

2. **Reporting Workbench**: SQL-based reporting
   - Direct queries on Clarity database
   - Scheduled reports
   - Custom metric calculations

3. **Cogito**: Predictive analytics
   - Readmission risk
   - Deterioration risk
   - No-show prediction
   - Built on Epic data

**Epic Healthy Planet Modules:**
```
Patient Registries:
- Diabetes registry
- CHF registry
- CKD registry
- Custom disease registries

Care Gaps:
- Preventive screenings due
- Quality measures due
- Immunizations due
- Medication adherence gaps

Outreach:
- Automated outreach campaigns
- Patient lists for calls
- Integration with MyChart

Analytics:
- Population health dashboards
- Provider performance
- Quality measure reporting
- HEDIS automation
```

### Arcadia Analytics

**Overview**: Cloud-based population health platform

**Core Capabilities:**
- Multi-source data aggregation (EHR, claims, HIE, labs)
- Quality measure engine (HEDIS, eCQM, MIPS)
- Risk stratification
- Care management workflows
- Analytics dashboards

**Arcadia Platform:**
```
Data Integration Layer:
- HL7 feeds
- Direct EHR connections
- Claims files
- Lab interfaces
- FHIR APIs

Analytics Layer:
- Quality measures (automated calculation)
- Risk scores
- Care gaps
- Utilization metrics

Application Layer:
- Dashboards (executive, operational, clinical)
- Care management tools
- Patient outreach
- Provider performance
```

### Philips Wellcentive

**Overview**: Population health management and analytics

**Modules:**
- Data aggregation (EHR, claims, HIE)
- Quality measure reporting
- Care coordination tools
- Patient engagement
- HEDIS automation

### Inovalon

**Overview**: Cloud-based healthcare data analytics

**Solutions:**
- Quality and risk adjustment analytics
- Provider performance management
- Network analytics
- Revenue cycle optimization
- Care management

## Dashboard Design Best Practices

### Healthcare Dashboard Principles

**1. Role-Based Design**
```
Executive Dashboard:
- High-level KPIs
- Trend indicators
- Exception alerts
- Minimal drill-down

Operational Dashboard:
- Actionable metrics
- Patient/encounter lists
- Real-time or near-real-time
- Deep drill-down

Clinical Dashboard:
- Patient-centric
- Embedded in workflow
- Clinical context
- Decision support
```

**2. Visual Hierarchy**
```
Top: KPI Summary (most important metrics)
Middle: Trend Analysis (performance over time)
Bottom: Detailed Tables (drill-down, patient lists)

Left to Right: General → Specific
```

**3. Color Coding**
```
Performance:
- Green: Meeting target
- Yellow: Below target (warning)
- Red: Significantly below (action required)

Healthcare-specific:
- Blue: Utilization metrics
- Purple: Cost metrics
- Teal: Quality metrics
```

**4. Interactivity**
```
Filters:
- Date range
- Provider / Location
- Payer type
- Patient demographics

Drill-down:
- Click KPI → View trend
- Click trend → View detail
- Click detail → Patient list
- Click patient → Patient profile
```

### Example Dashboard Layouts

#### Executive Quality Dashboard

```
┌─────────────────────────────────────────────────┐
│  Overall Quality Score: 82.5 ↑ 2.3pts YoY       │
│  Star Rating: ★★★★☆ 4.0                         │
├─────────────────────────────────────────────────┤
│  Top Metrics:                                   │
│  • Diabetes HbA1c Control: 68% ▼                │
│  • Hypertension Control: 74% ▲                  │
│  • Breast Cancer Screening: 78% →              │
│  • Colorectal Screening: 71% ▲                  │
├─────────────────────────────────────────────────┤
│  [Trend Chart: Quality Score Over Time]         │
│                                                 │
├─────────────────────────────────────────────────┤
│  Measure Details (Table)                        │
│  Measure | Rate | Target | Gap | Trend          │
│  CDC-HbA1c| 68%  | 75%   | -7% | ▼              │
│  ...                                            │
└─────────────────────────────────────────────────┘
```

#### Operational ED Dashboard

```
┌─────────────────────────────────────────────────┐
│  Current ED Volume: 38 patients                 │
│  Avg Wait Time: 45 min | Door-to-Provider: 32m  │
├─────────────────────────────────────────────────┤
│  [Wait Time Trend - Last 24 Hours]              │
│                                                 │
├─────────────────────────────────────────────────┤
│  Patients Waiting >1 Hour: 5                    │
│  [Patient List with Wait Times]                 │
│  Name | Arrival | Acuity | Wait | Status        │
│  ...                                            │
├─────────────────────────────────────────────────┤
│  [Volume by Hour of Day - Heat Map]             │
└─────────────────────────────────────────────────┘
```

### Mobile Dashboards

**Design Considerations:**
- Single-column layout
- Large touch targets
- Simplified visuals (fewer charts)
- Swipe navigation
- Critical metrics only

**Example Mobile Views:**
```
┌─────────────────┐
│  Quality Score  │
│      82.5       │
│    ▲ 2.3 pts    │
├─────────────────┤
│  Star Rating    │
│    ★★★★☆        │
├─────────────────┤
│  Top Alerts (3) │
│  • Low Diabetes │
│    Control Rate │
│  • High ED Use  │
│  • Care Gaps ↑  │
├─────────────────┤
│  [View Details] │
└─────────────────┘
```

## Data Refresh Strategies

### Batch Refresh

**Overnight ETL + Dashboard Refresh:**
```
01:00 AM - ETL starts (source → EDW)
03:00 AM - ETL completes
03:30 AM - Dashboard extract refresh begins
04:00 AM - Dashboard refresh completes
06:00 AM - Users access updated dashboards
```

**Use Cases:**
- Historical reporting
- Quality measures (monthly/quarterly)
- Financial dashboards
- Strategic analytics

### Near Real-Time

**Incremental Refresh (Every 15-60 minutes):**
```
- Pull delta records from source
- Update data warehouse incrementally
- Refresh dashboard data
- Latency: 15-60 minutes
```

**Use Cases:**
- Operational dashboards (ED, OR)
- Patient census
- Bed management
- Care gap lists

### Real-Time

**Streaming Data + Direct Query:**
```
- Event streaming (Kafka, Kinesis)
- Real-time data processing (Spark Streaming)
- In-memory caching (Redis)
- Direct query to operational systems
- Latency: Seconds to minutes
```

**Use Cases:**
- Clinical monitoring (sepsis alerts)
- Live dashboards (ED volume)
- Real-time alerting
- Command centers

## Performance Optimization

### Data Modeling

**Star Schema:**
```sql
-- Optimize for query performance
CREATE TABLE fact_encounter (
    encounter_key BIGINT PRIMARY KEY,
    patient_key BIGINT,  -- FK to dim_patient
    provider_key BIGINT, -- FK to dim_provider
    date_key INT,        -- FK to dim_date
    drg_key INT,         -- FK to dim_drg
    length_of_stay DECIMAL,
    total_charges DECIMAL
);

CREATE INDEX idx_fact_enc_patient ON fact_encounter(patient_key);
CREATE INDEX idx_fact_enc_provider ON fact_encounter(provider_key);
CREATE INDEX idx_fact_enc_date ON fact_encounter(date_key);
```

**Aggregate Tables:**
```sql
-- Pre-aggregate for common queries
CREATE TABLE agg_provider_monthly AS
SELECT
    provider_key,
    date_key,
    COUNT(DISTINCT encounter_key) AS encounter_count,
    SUM(total_charges) AS total_charges,
    AVG(length_of_stay) AS avg_los
FROM fact_encounter
GROUP BY provider_key, date_key;
```

### Tableau Extracts

**Extract Optimization:**
```
- Filter to relevant data (date range, locations)
- Aggregate to appropriate grain
- Hide unused fields
- Use extract filters
- Materialize calculations
- Incremental refresh
```

**Example Extract Filter:**
```
Include only:
- Last 2 years of data
- Active patients
- Specific facility IDs
- Completed encounters

Result: 5M rows → 500K rows (10x reduction)
```

### Power BI Optimization

**Optimize Data Model:**
```
- Use star schema
- Remove unused columns
- Avoid bidirectional relationships
- Use calculated columns sparingly (prefer measures)
- Disable auto date/time
- Use aggregations for large datasets
```

**DirectQuery vs. Import:**
```
Import (Extract):
+ Faster query performance
+ Full DAX capabilities
- Larger file size
- Scheduled refresh needed

DirectQuery:
+ Always current data
+ Smaller file size
- Slower performance
- Limited DAX functions
```

## Security & Compliance

### Row-Level Security (RLS)

**Tableau:**
```
-- User filter in data source
[Provider ID] = USERNAME()

-- Or use entitlements table
[Provider ID] IN (
    SELECT Provider_ID
    FROM user_entitlements
    WHERE user_name = USERNAME()
)
```

**Power BI:**
```dax
-- RLS role definition
[ProviderID] = USERPRINCIPALNAME()

-- Or lookup in security table
[ProviderID] IN (
    VALUES(
        FILTER(
            UserSecurity,
            UserSecurity[Email] = USERPRINCIPALNAME()
        )
    )
)
```

### HIPAA Compliance

**Requirements:**
- Encrypted data at rest and in transit
- Access controls (authentication + authorization)
- Audit logging (who accessed what, when)
- Data retention policies
- Business Associate Agreement (BAA) with vendor

**BAA Required:**
- Tableau Server/Cloud ✓
- Power BI Premium ✓
- Qlik Sense Enterprise ✓
- Looker ✓

**Platform-Specific:**
```
Tableau:
- SAML/LDAP authentication
- Row-level security
- Access logging
- Encrypted extracts

Power BI:
- Azure AD authentication
- RLS
- Audit logs in M365 compliance center
- Encryption in Premium

Qlik:
- Section access (RLS)
- SSL/TLS encryption
- Audit logs
- Custom authentication
```

## Embedded Analytics

### Tableau Embedded

```html
<!-- Embed Tableau dashboard in web app -->
<script type="text/javascript"
    src="https://tableau-server/javascripts/api/tableau-2.min.js"></script>

<div id="tableau-viz"></div>

<script>
    var containerDiv = document.getElementById("tableau-viz"),
        url = "https://tableau-server/views/QualityDashboard",
        options = {
            hideTabs: true,
            width: "100%",
            height: "800px",
            patientId: "12345"  // Pass parameter
        };

    var viz = new tableau.Viz(containerDiv, url, options);
</script>
```

### Power BI Embedded

```javascript
// Embed Power BI report in web app
const embedConfiguration = {
    type: 'report',
    tokenType: models.TokenType.Embed,
    accessToken: embedToken,
    embedUrl: embedUrl,
    id: reportId,
    filters: [
        {
            $schema: "http://powerbi.com/product/schema#basic",
            target: {
                table: "Patients",
                column: "ProviderID"
            },
            operator: "In",
            values: [currentProviderId]
        }
    ],
    settings: {
        panes: {
            filters: {
                visible: false
            }
        }
    }
};

// Embed in div
powerbi.embed(reportContainer, embedConfiguration);
```

---

*Healthcare Business Intelligence Tools Reference - Platforms and best practices for transforming healthcare data into actionable insights.*
