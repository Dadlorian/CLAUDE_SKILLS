# Legacy BI Modernization Playbook

## Executive Summary

This playbook provides a comprehensive framework for migrating from legacy Business Intelligence platforms (Cognos, BusinessObjects, SSRS, Crystal Reports) to modern BI solutions (Power BI, Tableau, Looker, Qlik). The approach emphasizes risk mitigation, user adoption, and business continuity through phased migration strategies.

## Table of Contents

1. [Assessment Phase](#assessment-phase)
2. [Migration Strategies](#migration-strategies)
3. [Strangler Pattern Implementation](#strangler-pattern-implementation)
4. [Parallel Run Strategies](#parallel-run-strategies)
5. [User Adoption and Training](#user-adoption-and-training)
6. [Risk Management](#risk-management)
7. [Checklists and Templates](#checklists-and-templates)

---

## Assessment Phase

### 1.1 Platform Inventory

#### Discovery Process

**Automated Discovery:**
```bash
# Sample script to inventory legacy reports
# Scan file systems for Crystal Reports
find /reports -name "*.rpt" -exec ls -lh {} \; > crystal_inventory.txt

# Query IBM Cognos metadata
cognos-cli export --format=json --output=cognos_inventory.json

# Extract BusinessObjects universe definitions
boe-cli list-universes --detailed > bobj_inventory.csv

# SSRS Report Catalog Query
sqlcmd -S ReportServer -Q "
SELECT
    c.Name,
    c.Path,
    c.Type,
    c.ModifiedDate,
    eu.UserName as LastModifiedBy,
    COUNT(DISTINCT e.TimeStart) as ExecutionCount
FROM Catalog c
LEFT JOIN ExecutionLog e ON c.ItemID = e.ReportID
LEFT JOIN Users eu ON c.ModifiedBy = eu.UserID
WHERE c.Type = 2  -- Reports only
GROUP BY c.Name, c.Path, c.Type, c.ModifiedDate, eu.UserName
ORDER BY ExecutionCount DESC
" -o ssrs_inventory.csv
```

**Manual Inventory Checklist:**

- [ ] Total number of reports by platform
- [ ] Report categorization (operational, analytical, regulatory)
- [ ] Data sources and connections
- [ ] Refresh schedules
- [ ] User groups and permissions
- [ ] Distribution lists and subscriptions
- [ ] Custom extensions or plugins
- [ ] Integration points with other systems
- [ ] Report parameters and filters
- [ ] Embedded reports in applications

#### Usage Analysis

**Key Metrics to Collect:**

1. **Execution Frequency**
   - Daily active reports
   - Weekly/Monthly reports
   - Rarely used (candidates for retirement)
   - Never used (immediate retirement candidates)

2. **User Engagement**
   - Unique users per report
   - Average view duration
   - Export frequency
   - Drill-down usage patterns

3. **Performance Metrics**
   - Average execution time
   - Peak usage times
   - Failed executions
   - Timeout occurrences

**Usage Analysis Query Template:**

```sql
-- BusinessObjects usage analysis
SELECT
    r.SI_NAME as ReportName,
    r.SI_OWNER as Owner,
    COUNT(DISTINCT a.USERID) as UniqueUsers,
    COUNT(*) as TotalExecutions,
    AVG(a.DURATION) as AvgDuration,
    MAX(a.RUN_DATE) as LastRun,
    CASE
        WHEN MAX(a.RUN_DATE) < DATEADD(month, -6, GETDATE()) THEN 'Retire'
        WHEN MAX(a.RUN_DATE) < DATEADD(month, -3, GETDATE()) THEN 'Low Priority'
        WHEN COUNT(*) > 100 THEN 'High Priority'
        ELSE 'Medium Priority'
    END as MigrationPriority
FROM CMS_InfoObjects r
LEFT JOIN CMS_Auditing a ON r.SI_ID = a.OBJECT_ID
WHERE r.SI_KIND = 'CrystalReport'
    AND a.RUN_DATE >= DATEADD(year, -1, GETDATE())
GROUP BY r.SI_NAME, r.SI_OWNER
ORDER BY TotalExecutions DESC;
```

### 1.2 Complexity Scoring

#### Complexity Assessment Framework

**Scoring Matrix (0-10 scale):**

| Factor | Low (1-3) | Medium (4-6) | High (7-10) |
|--------|-----------|--------------|-------------|
| Data Sources | Single source | 2-3 sources | 4+ sources or complex joins |
| Calculations | Basic aggregations | Calculated fields | Complex business logic, stored procedures |
| Formatting | Simple tables | Charts with formatting | Highly customized layouts, pixel-perfect |
| Parameters | None or simple | Multiple parameters | Cascading parameters, complex defaults |
| Interactivity | Static | Basic filters | Drill-through, actions, complex interactions |
| Size | < 5 pages | 5-20 pages | 20+ pages or subreports |
| Dependencies | Standalone | 2-3 dependencies | Complex dependency chains |
| Custom Code | None | Minimal scripting | Extensive custom code |

**Complexity Score Calculation:**

```python
def calculate_complexity_score(report_metadata):
    """
    Calculate migration complexity score for a legacy report
    """
    score = 0

    # Data source complexity
    num_sources = len(report_metadata['data_sources'])
    score += min(num_sources * 2, 10)

    # Calculation complexity
    if report_metadata['has_stored_procedures']:
        score += 8
    elif report_metadata['calculated_fields_count'] > 10:
        score += 6
    elif report_metadata['calculated_fields_count'] > 0:
        score += 3

    # Layout complexity
    if report_metadata['pixel_perfect_required']:
        score += 9
    elif report_metadata['custom_formatting']:
        score += 5
    else:
        score += 2

    # Parameter complexity
    param_count = report_metadata['parameter_count']
    if param_count > 5 or report_metadata['has_cascading_params']:
        score += 7
    elif param_count > 0:
        score += 4

    # Interactivity
    if report_metadata['has_drill_through']:
        score += 6
    if report_metadata['has_actions']:
        score += 4

    # Size and subreports
    if report_metadata['subreport_count'] > 3:
        score += 8
    elif report_metadata['subreport_count'] > 0:
        score += 5

    # Normalize to 0-10
    normalized_score = min(score / 6, 10)

    return {
        'score': round(normalized_score, 1),
        'category': get_complexity_category(normalized_score),
        'estimated_effort_hours': estimate_effort(normalized_score)
    }

def get_complexity_category(score):
    if score <= 3:
        return 'Simple'
    elif score <= 6:
        return 'Moderate'
    else:
        return 'Complex'

def estimate_effort(score):
    """Estimate migration effort in hours"""
    base_hours = {
        'Simple': 4,
        'Moderate': 16,
        'Complex': 40
    }
    category = get_complexity_category(score)
    return base_hours[category] * (1 + (score / 10))
```

### 1.3 Stakeholder Mapping

**Key Stakeholders:**

1. **Business Users**
   - Power users (Excel experts, report creators)
   - Information consumers
   - Executive dashboard users

2. **Technical Teams**
   - Database administrators
   - ETL developers
   - Application developers (embedded reports)
   - Network/Infrastructure teams

3. **Governance**
   - Data governance team
   - Security and compliance
   - Architecture review board

**Stakeholder Analysis Template:**

| Stakeholder Group | Influence | Interest | Strategy | Key Concerns |
|-------------------|-----------|----------|----------|--------------|
| Finance Power Users | High | High | Involve closely | Loss of Excel integration |
| Sales Leadership | High | Medium | Keep informed | Real-time data access |
| IT Operations | Medium | High | Collaborate | Support burden |
| Compliance Team | High | High | Partner | Audit trails |

---

## Migration Strategies

### 2.1 Migration Approach Selection

**Decision Framework:**

```
                    Business Criticality
                    High            Low
Report   High   │ Strangler       │ Big Bang
Complexity       │ Pattern         │ (High Risk)
                 │                 │
         Low    │ Parallel Run    │ Direct
                │ (Recommended)    │ Migration
```

### 2.2 Lift-and-Shift Strategy

**When to Use:**
- Simple reports with minimal customization
- Time-sensitive migrations
- Reports that map directly to modern BI capabilities

**Process:**

1. **Pre-Migration:**
   ```yaml
   checklist:
     - Export report definitions
     - Document data sources
     - Capture current screenshots
     - Export user access lists
     - Save sample outputs (PDF, Excel)
   ```

2. **Migration:**
   - Use automated conversion tools where available
   - Recreate in target platform
   - Match visual design closely
   - Implement equivalent functionality

3. **Validation:**
   - Side-by-side data comparison
   - User acceptance testing
   - Performance benchmarking

**Automated Conversion Tools:**

- **Cognos to Power BI:** Third-party tools like ClarityBI Migrator
- **SSRS to Power BI:** Microsoft's RDL migration tool
- **Crystal to Tableau:** Manual recreation with Tableau Desktop
- **BusinessObjects to Qlik:** Qlik Sense conversion utilities

### 2.3 Redesign Strategy

**When to Use:**
- Reports with poor UX in legacy platform
- Opportunity to consolidate multiple reports
- Leverage modern BI capabilities (AI insights, natural language)

**Design Principles:**

1. **Mobile-First Design**
   - Responsive layouts
   - Touch-optimized interactions
   - Progressive disclosure

2. **Self-Service Enablement**
   - Intuitive filtering
   - Exploratory analysis
   - Export capabilities

3. **Modern Visualizations**
   - Replace tables with charts where appropriate
   - Use modern chart types (treemaps, waterfall, sankey)
   - Implement drill-down patterns

**Redesign Workshop Template:**

```markdown
## Report Redesign Session

**Legacy Report:** [Name]
**Business Purpose:** [Description]
**Current Issues:** [Pain points]

### Discovery Questions:
1. What decision does this report support?
2. What's the most important insight?
3. How often is it viewed vs. exported?
4. What filters are most commonly used?
5. What additional data would be valuable?

### Design Goals:
- [ ] Reduce time to insight
- [ ] Improve mobile accessibility
- [ ] Enable self-service exploration
- [ ] Consolidate with related reports
- [ ] Add predictive/prescriptive analytics

### Success Metrics:
- User satisfaction score
- Time saved per report view
- Reduction in support tickets
```

---

## Strangler Pattern Implementation

### 3.1 Pattern Overview

The Strangler Pattern, based on Thoughtworks migration patterns, gradually replaces legacy systems by incrementally developing new functionality while maintaining the old system.

**Strangler Pattern Architecture:**

```
┌─────────────────────────────────────────────────┐
│           Routing Layer / Gateway               │
│  (Routes requests to Legacy or Modern BI)       │
└─────────────────┬───────────────┬───────────────┘
                  │               │
         ┌────────▼────────┐   ┌──▼──────────────┐
         │  Legacy BI      │   │  Modern BI      │
         │  (Cognos, etc)  │   │  (Power BI, etc)│
         └────────┬────────┘   └──┬──────────────┘
                  │               │
         ┌────────▼───────────────▼──────────────┐
         │      Common Data Layer                │
         │      (Shared Data Sources)            │
         └───────────────────────────────────────┘
```

### 3.2 Implementation Phases

**Phase 1: Establish Coexistence (Weeks 1-4)**

1. **Create Routing Mechanism:**
   ```javascript
   // Example: Portal-based routing
   function getReportURL(reportName, userId) {
       const migratedReports = getMigratedReportList();
       const userInPilot = isPilotUser(userId);

       if (migratedReports.includes(reportName)) {
           if (userInPilot) {
               return `/modern-bi/reports/${reportName}`;
           } else {
               // Gradual rollout percentage
               if (Math.random() < 0.1) { // 10% rollout
                   logRollout(userId, reportName);
                   return `/modern-bi/reports/${reportName}`;
               }
           }
       }

       return `/legacy-bi/reports/${reportName}`;
   }
   ```

2. **Setup Monitoring:**
   - Track report access by platform
   - Monitor error rates
   - Measure performance metrics
   - Collect user feedback

**Phase 2: Incremental Migration (Weeks 5-24)**

**Week-by-Week Migration Plan:**

| Week | Focus Area | Reports Migrated | User Rollout % |
|------|------------|------------------|----------------|
| 5-8 | High-value, low-complexity | 10-15 | 10% pilot |
| 9-12 | Departmental dashboards | 15-20 | 25% |
| 13-16 | Operational reports | 20-30 | 50% |
| 17-20 | Analytical reports | 15-25 | 75% |
| 21-24 | Complex/legacy reports | 10-15 | 100% |

**Migration Cadence:**

```yaml
sprint_duration: 2_weeks

sprint_template:
  week_1:
    monday: Sprint planning, select reports
    tuesday: Technical discovery, data source setup
    wednesday: Development begins
    thursday: Development continues
    friday: Internal testing

  week_2:
    monday: UAT with business users
    tuesday: Incorporate feedback
    wednesday: Final testing
    thursday: Deploy to production
    friday: Monitor, support, retrospective

  deliverables:
    - 3-5 migrated reports
    - User documentation
    - Training materials
    - Support runbook
```

**Phase 3: Legacy Retirement (Weeks 25-28)**

1. **Decommission Criteria:**
   - Zero active users on legacy report (30 days)
   - Successful UAT on modern version
   - Approval from business owner
   - Backup/archive of legacy report

2. **Retirement Process:**
   ```markdown
   ## Legacy Report Retirement Checklist

   ### Pre-Retirement (T-14 days)
   - [ ] Final communication to all users
   - [ ] Redirect legacy URLs to modern version
   - [ ] Archive legacy report definition
   - [ ] Document migration notes

   ### Retirement (T-0)
   - [ ] Disable legacy report
   - [ ] Update documentation
   - [ ] Remove from catalogs
   - [ ] Archive historical data

   ### Post-Retirement (T+7 days)
   - [ ] Verify no support tickets
   - [ ] Confirm user satisfaction
   - [ ] Complete migration record
   ```

### 3.3 Strangler Pattern Anti-Patterns

**Avoid These Common Mistakes:**

1. **Big Bang within Strangler:**
   - Don't migrate entire departments at once
   - Maintain small, incremental batches

2. **No Clear Migration End Date:**
   - Set deadlines for legacy retirement
   - Create urgency to prevent perpetual coexistence

3. **Neglecting the Routing Layer:**
   - Ensure seamless user experience
   - Avoid forcing users to know which platform

4. **Ignoring Data Consistency:**
   - Keep data sources synchronized
   - Validate results match between platforms

---

## Parallel Run Strategies

### 4.1 Parallel Run Framework

**Purpose:** Run legacy and modern reports simultaneously to validate accuracy and build user confidence.

**Duration:** Typically 4-12 weeks per report batch

### 4.2 Parallel Run Process

**Week 1-2: Setup and Baseline**

1. **Configure Both Environments:**
   ```yaml
   parallel_run_config:
     legacy_report:
       platform: Cognos
       schedule: Daily at 6 AM
       output_location: /legacy/outputs/
       format: PDF

     modern_report:
       platform: PowerBI
       schedule: Daily at 6 AM
       output_location: /modern/outputs/
       format: PDF, Excel

     comparison:
       automated: true
       tolerance: 0.01  # 1% variance
       alert_on_difference: true
   ```

2. **Establish Baseline:**
   - Run both versions for 5 days
   - Document expected differences
   - Calibrate comparison tools

**Week 3-8: Parallel Operation**

**Daily Reconciliation Process:**

```python
# Automated comparison script
import pandas as pd
from deepdiff import DeepDiff

def compare_report_outputs(legacy_file, modern_file, tolerance=0.01):
    """
    Compare legacy and modern report outputs
    """
    # Load outputs
    legacy_data = load_report_data(legacy_file)
    modern_data = load_report_data(modern_file)

    # Normalize data
    legacy_normalized = normalize_data(legacy_data)
    modern_normalized = normalize_data(modern_data)

    # Compare
    differences = {
        'row_count_diff': abs(len(legacy_normalized) - len(modern_normalized)),
        'column_diff': set(legacy_normalized.columns) ^ set(modern_normalized.columns),
        'value_differences': []
    }

    # Numeric comparison with tolerance
    common_cols = set(legacy_normalized.columns) & set(modern_normalized.columns)
    for col in common_cols:
        if legacy_normalized[col].dtype in ['float64', 'int64']:
            variance = calculate_variance(
                legacy_normalized[col],
                modern_normalized[col]
            )
            if variance > tolerance:
                differences['value_differences'].append({
                    'column': col,
                    'variance': variance,
                    'max_difference': max(abs(legacy_normalized[col] - modern_normalized[col]))
                })

    # Generate reconciliation report
    return generate_recon_report(differences)

def generate_recon_report(differences):
    """
    Create daily reconciliation report
    """
    status = 'PASS' if is_within_tolerance(differences) else 'FAIL'

    report = f"""
    # Daily Reconciliation Report
    Date: {datetime.now().strftime('%Y-%m-%d')}
    Status: {status}

    ## Summary
    - Row Count Difference: {differences['row_count_diff']}
    - Column Differences: {len(differences['column_diff'])}
    - Value Variances: {len(differences['value_differences'])}

    ## Details
    {format_differences(differences)}

    ## Action Required
    {get_action_items(differences, status)}
    """

    return report
```

**Week 9-10: User Validation**

1. **Distribute both versions to users:**
   - Side-by-side access
   - Feedback form
   - Feature comparison

2. **Collect feedback:**
   ```markdown
   ## Parallel Run User Feedback Form

   Report: _______________
   User: _______________
   Date: _______________

   ### Data Accuracy
   - [ ] Data matches between versions
   - [ ] Any discrepancies noted (describe):

   ### Usability
   - Modern version is: [ ] Better [ ] Same [ ] Worse
   - What improvements do you notice?
   - What features are missing?

   ### Performance
   - Legacy load time: ___ seconds
   - Modern load time: ___ seconds
   - Preferred version: [ ] Legacy [ ] Modern

   ### Readiness
   - [ ] Ready to switch to modern version
   - [ ] Need more time with modern version
   - [ ] Have concerns (describe):
   ```

**Week 11-12: Transition Decision**

**Go/No-Go Criteria:**

```yaml
transition_criteria:
  data_accuracy:
    threshold: 99.9%
    current: ___%
    status: [ ] PASS [ ] FAIL

  user_acceptance:
    threshold: 80%
    current: ___%
    status: [ ] PASS [ ] FAIL

  performance:
    requirement: <= legacy performance
    legacy_avg: ___ seconds
    modern_avg: ___ seconds
    status: [ ] PASS [ ] FAIL

  feature_parity:
    critical_features: 100%
    nice_to_have: 80%
    status: [ ] PASS [ ] FAIL

  overall_decision: [ ] GO [ ] NO-GO [ ] GO with exceptions
```

### 4.3 Parallel Run Monitoring Dashboard

**Key Metrics to Track:**

1. **Accuracy Metrics:**
   - Daily pass/fail rate
   - Variance trending
   - Root cause of differences

2. **Performance Metrics:**
   - Load time comparison
   - Refresh duration
   - Resource utilization

3. **Adoption Metrics:**
   - Views by platform
   - User preferences
   - Feature usage

**Sample Dashboard Query:**

```sql
-- Parallel run monitoring
SELECT
    pr.report_name,
    pr.run_date,
    pr.legacy_execution_time_sec,
    pr.modern_execution_time_sec,
    pr.data_match_status,
    pr.variance_percentage,
    pr.user_preference_legacy,
    pr.user_preference_modern,
    CASE
        WHEN pr.data_match_status = 'PASS'
             AND pr.modern_execution_time_sec <= pr.legacy_execution_time_sec
             AND pr.user_preference_modern > pr.user_preference_legacy
        THEN 'Ready for Cutover'
        WHEN pr.data_match_status = 'FAIL'
        THEN 'Data Issues - Not Ready'
        ELSE 'In Progress'
    END as cutover_readiness
FROM parallel_runs pr
WHERE pr.run_date >= DATEADD(day, -30, GETDATE())
ORDER BY pr.run_date DESC;
```

---

## User Adoption and Training

### 5.1 Change Management Framework

**ADKAR Model Applied to BI Migration:**

1. **Awareness** - Why change is needed
2. **Desire** - Motivation to support change
3. **Knowledge** - How to change
4. **Ability** - Skills to implement change
5. **Reinforcement** - Sustaining the change

### 5.2 Training Strategy

**Tiered Training Approach:**

**Tier 1: All Users (1-2 hours)**
- Platform navigation
- Finding and accessing reports
- Basic filtering and exporting
- Getting help and support

**Tier 2: Power Users (1 day)**
- Report customization
- Creating personal views
- Advanced filtering
- Sharing and collaboration
- Basic report creation

**Tier 3: Creators (2-3 days)**
- Data modeling
- Report design
- DAX/calculated fields
- Performance optimization
- Publishing and governance

**Training Delivery Methods:**

```markdown
## Training Plan Matrix

| Audience | Size | Method | Duration | Frequency |
|----------|------|--------|----------|-----------|
| Executives | 10-20 | Executive briefing | 30 min | Once |
| All users | 500+ | eLearning + office hours | 1-2 hrs | On-demand |
| Power users | 50-100 | Virtual instructor-led | 1 day | Monthly cohorts |
| Report creators | 10-20 | In-person workshop | 2-3 days | Quarterly |
| Super users | 5-10 | Advanced workshop | 1 week | Annually |
```

### 5.3 Communication Plan

**Migration Communication Timeline:**

**T-90 days: Announcement**
```
Subject: Modernizing Our BI Platform - What You Need to Know

Dear Team,

We're upgrading our reporting platform from [Legacy] to [Modern BI] to
provide faster, more intuitive access to data...

What this means for you:
- More powerful self-service capabilities
- Mobile access to reports
- Faster report performance
- Modern, intuitive interface

Timeline:
- Month 1-2: Pilot with select users
- Month 3-6: Phased rollout
- Month 7: Full transition

Training will be provided...
```

**T-30 days: Training Invitation**

**T-14 days: Pilot Launch**

**T-7 days: Individual Report Migration Notice**

**T-1 day: Reminder**

**T+0: Launch Confirmation**

**T+7, T+30, T+90: Follow-up and reinforcement**

### 5.4 Support Model

**Tiered Support Structure:**

```
Level 1: Self-Service
├── Knowledge base articles
├── Video tutorials
├── FAQ
└── User community forum

Level 2: Help Desk
├── Email support
├── Chat support
├── Incident logging
└── Response SLA: 4 hours

Level 3: BI Team
├── Complex technical issues
├── Report development support
├── Performance troubleshooting
└── Response SLA: 1 business day

Level 4: Vendor Support
├── Platform bugs
├── Infrastructure issues
└── Response SLA: Per contract
```

**Hypercare Period:**

During the first 30 days post-migration:
- Extended support hours (7 AM - 7 PM)
- Dedicated migration hotline
- Daily check-ins with pilot users
- War room for critical issues
- Reduced SLAs (2 hours for critical issues)

---

## Risk Management

### 6.1 Risk Register

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy | Owner |
|---------|------------------|-------------|--------|---------------------|-------|
| R001 | Data discrepancies between platforms | Medium | High | Parallel runs, automated reconciliation | Data Team |
| R002 | User resistance to change | High | Medium | Change management, training, champions | PMO |
| R003 | Performance degradation | Low | High | Performance testing, optimization | Technical Lead |
| R004 | Security/compliance issues | Low | Critical | Security review, audit trails | Security Team |
| R005 | Budget overruns | Medium | Medium | Phased approach, scope control | PM |
| R006 | Critical reports not migrated on time | Medium | High | Priority matrix, buffer time | PM |
| R007 | Loss of specialized functionality | Medium | Medium | Gap analysis, workarounds | Solution Architect |
| R008 | Vendor lock-in | Low | Medium | Platform evaluation, exit strategy | Architecture |

### 6.2 Rollback Plans

**Rollback Decision Criteria:**

Initiate rollback if:
- Critical data inaccuracy (>1% variance on financial reports)
- Performance degradation >50%
- Platform unavailability >4 hours
- Security breach or compliance violation
- User adoption <20% after 30 days

**Rollback Procedure:**

```markdown
## Emergency Rollback Procedure

### Phase 1: Immediate Actions (0-2 hours)
1. [ ] Notify incident commander
2. [ ] Alert stakeholders
3. [ ] Switch routing to legacy platform
4. [ ] Post user communication
5. [ ] Preserve modern platform state for analysis

### Phase 2: Stabilization (2-24 hours)
1. [ ] Verify legacy platform stability
2. [ ] Conduct root cause analysis
3. [ ] Document lessons learned
4. [ ] Plan remediation

### Phase 3: Recovery Planning (1-7 days)
1. [ ] Fix identified issues
2. [ ] Test solutions
3. [ ] Communicate revised timeline
4. [ ] Prepare for re-migration
```

### 6.3 Contingency Plans

**Scenario Planning:**

1. **Key Resource Unavailability:**
   - Cross-train team members
   - Document all processes
   - Engage vendor professional services

2. **Data Source Changes:**
   - Freeze data source changes during migration
   - Establish change control board
   - Build flexible data layer

3. **Budget Constraints:**
   - Prioritize high-value reports
   - Leverage free/included tools
   - Consider hybrid approach

---

## Checklists and Templates

### 7.1 Pre-Migration Checklist

```markdown
## Pre-Migration Readiness Checklist

### Discovery and Planning
- [ ] Complete platform inventory
- [ ] Conduct usage analysis
- [ ] Calculate complexity scores
- [ ] Map stakeholders
- [ ] Select migration strategy
- [ ] Establish governance model
- [ ] Define success metrics
- [ ] Secure executive sponsorship

### Technical Preparation
- [ ] Provision modern BI platform
- [ ] Configure data source connections
- [ ] Setup development, test, production environments
- [ ] Implement version control
- [ ] Configure security and permissions
- [ ] Setup monitoring and logging
- [ ] Establish backup procedures
- [ ] Complete network/firewall configuration

### Team Readiness
- [ ] Assemble migration team
- [ ] Assign roles and responsibilities
- [ ] Complete platform training
- [ ] Establish communication channels
- [ ] Setup project tracking tools
- [ ] Define escalation procedures

### Business Preparation
- [ ] Communicate migration plan
- [ ] Identify pilot users
- [ ] Schedule training sessions
- [ ] Create support documentation
- [ ] Prepare change management materials
- [ ] Establish feedback mechanisms
```

### 7.2 Report Migration Template

```markdown
## Report Migration Record

**Report ID:** _______________
**Report Name:** _______________
**Legacy Platform:** [ ] Cognos [ ] BusinessObjects [ ] SSRS [ ] Crystal
**Target Platform:** [ ] Power BI [ ] Tableau [ ] Looker [ ] Qlik

### Classification
- Business Function: _______________
- Criticality: [ ] Critical [ ] High [ ] Medium [ ] Low
- Complexity Score: ___ / 10
- Estimated Effort: ___ hours

### Technical Details
- Data Sources: _______________
- Refresh Frequency: _______________
- Parameters: _______________
- Calculations: _______________
- Custom Code: [ ] Yes [ ] No

### Migration Details
- Migration Strategy: [ ] Lift-and-Shift [ ] Redesign
- Developer: _______________
- Start Date: _______________
- Target Date: _______________
- Actual Completion: _______________

### Testing
- [ ] Data validation completed
- [ ] Performance testing passed
- [ ] UAT completed
- [ ] Security review approved

### Approval
- [ ] Business owner sign-off
- [ ] Technical lead approval
- [ ] Compliance review (if required)

### Deployment
- [ ] Deployed to production
- [ ] Legacy report archived
- [ ] Documentation updated
- [ ] Users notified
```

### 7.3 Post-Migration Review Template

```markdown
## Post-Migration Review

**Migration Batch:** _______________
**Review Date:** _______________
**Participants:** _______________

### Metrics
- Reports Migrated: ___
- On-Time Delivery: ___%
- User Adoption Rate: ___%
- Average Performance Improvement: ___%
- Support Tickets (30 days): ___

### What Went Well
1.
2.
3.

### What Didn't Go Well
1.
2.
3.

### Lessons Learned
1.
2.
3.

### Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
|        |       |          |        |

### Recommendations for Next Batch
1.
2.
3.
```

---

## Appendix: Tool-Specific Migration Notes

### A.1 Cognos to Power BI

**Key Challenges:**
- Framework Manager models → Power BI dataflows/datasets
- Cognos macros → DAX expressions
- Drill-through functionality → Page navigation
- Burst reporting → Power BI subscriptions

**Migration Accelerators:**
- Use Power BI Report Builder for paginated reports
- Leverage ClarityBI migration tools
- Cognos SDK for metadata extraction

### A.2 BusinessObjects to Tableau

**Key Challenges:**
- Universe → Published data sources
- WebI formatting → Tableau dashboards
- SAP connectivity → DirectQuery/Live connections

**Migration Tips:**
- Maintain universe structure in Tableau data source
- Use Tableau Prep for ETL logic
- Leverage SAP connector for seamless integration

### A.3 SSRS to Power BI

**Key Challenges:**
- Paginated reports → Power BI Paginated Reports
- Subscription delivery → Power BI subscriptions
- Custom code → DAX or Power Query M

**Microsoft Tools:**
- RDL Migration Tool
- Power BI Report Builder
- Paginated Reports service

### A.4 Crystal Reports to Qlik Sense

**Key Challenges:**
- Pixel-perfect layouts → Qlik visualizations
- Subreports → Master/detail in Qlik
- Formula fields → Qlik expressions

**Best Practices:**
- Redesign for modern UX
- Leverage Qlik's associative model
- Use NPrinting for formatted outputs

---

## References and Resources

### Thoughtworks Migration Patterns
- Strangler Fig Pattern: https://martinfowler.com/bliki/StranglerFigApplication.html
- Legacy Displacement: Thoughtworks Technology Radar

### Industry Best Practices
- Gartner: "Magic Quadrant for Analytics and BI Platforms"
- Forrester: "The Forrester Wave: Enterprise BI Platforms"
- TDWI: "Best Practices in BI Modernization"

### Vendor Resources
- Microsoft: Power BI Migration Framework
- Tableau: Server to Cloud Migration Guide
- Qlik: Modernization Assessment Tool
- Looker: Migration Services Documentation

### Books and Publications
- "Building a Modern BI Practice" - O'Reilly
- "Data Warehouse Toolkit" (4th Edition) - Kimball & Ross
- "Agile Data Warehouse Design" - Lawrence Corr

---

**Document Version:** 1.0
**Last Updated:** 2025-11-19
**Maintained By:** BI Modernization Center of Excellence
**Review Cycle:** Quarterly
