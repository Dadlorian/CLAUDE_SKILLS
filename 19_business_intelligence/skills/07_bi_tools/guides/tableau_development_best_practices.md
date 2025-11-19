# Tableau Development Best Practices

## Project Organization

### Folder Structure
```
tableau-project/
├── workbooks/
│   ├── published/           # Production-ready workbooks
│   ├── development/         # In-progress work
│   └── archived/            # Old versions
├── data-sources/
│   ├── published/           # Shared data sources
│   └── extracts/            # Extract files (.hyper)
├── prep-flows/              # Tableau Prep flows
├── documentation/
│   ├── data-dictionary.md
│   ├── calculation-library.md
│   └── style-guide.md
└── scripts/
    ├── refresh-extracts.py
    └── publish-workbooks.py
```

### Naming Conventions
```
Workbooks: [Domain]_[Purpose]_[Version]
├─ Sales_ExecutiveDashboard_v2.twbx
├─ HR_RecruitmentAnalytics_v1.twbx
└─ Finance_MonthlyP&L_v3.twbx

Data Sources: [System]_[Entity]_[RefreshFrequency]
├─ Salesforce_Opportunities_Daily.tds
├─ Snowflake_Orders_Hourly.tds
└─ Oracle_Customers_Weekly.tds

Worksheets: [ChartType]_[Metric]_[Dimension]
├─ Bar_Revenue_by_Category
├─ Line_Orders_over_Time
└─ Map_Customers_by_Region

Dashboards: [Audience]_[Topic]
├─ Executive_SalesOverview
├─ Manager_TeamPerformance
└─ Analyst_DetailedAnalysis
```

## Data Source Design

### Optimal Extract Strategy
```tableau
// When to use Extract vs Live:

Extract:
✓ Large datasets (>1M rows)
✓ Slow data source
✓ Complex calculations
✓ Offline access needed
✓ Consistent performance required

Live Connection:
✓ Real-time data required
✓ Small datasets (<100K rows)
✓ Fast database (Snowflake, BigQuery)
✓ Row-level security in database
✓ Centralized data governance

Hybrid (Data Blending):
✓ Combine different sources
✓ Different refresh schedules
✓ Quick prototyping
```

### Extract Optimization
```
1. Filter Early
   - Use data source filters
   - Filter at extraction time
   - Example: Only last 2 years of data

2. Aggregate When Possible
   - Visible dimensions only
   - Pre-aggregate measures
   - Example: Daily instead of transactional

3. Hide Unused Fields
   - Right-click → Hide
   - Reduces extract size
   - Improves performance

4. Choose Appropriate Data Types
   - String → String (not auto)
   - Integer → Number (whole)
   - Date → Date (not DateTime if no time)

5. Incremental Refresh
   - Server → Schedule → Incremental Refresh
   - Define incremental column (e.g., Created Date)
   - Full refresh: Weekly, Incremental: Daily
```

## Calculation Best Practices

### Calculation Hierarchy
```
1. Data Source Level (Best Performance)
   - Calculated in database
   - Shared across workbooks
   - Example:
     CREATE VIEW sales_metrics AS
     SELECT *, quantity * price AS line_total
     FROM orders;

2. Extract Level (Good Performance)
   - Materialized in extract
   - Edit Data Source → Create Calculated Field
   - Good for frequently used calcs

3. Workbook Level (Standard)
   - Normal calculated fields
   - Available in current workbook

4. Worksheet Level (Use Sparingly)
   - Table calculations
   - Only when absolutely needed
```

### LOD Expression Patterns
```tableau
// Pattern 1: Customer Lifetime Value
{ FIXED [Customer ID] : SUM([Revenue]) }

// Pattern 2: New vs Repeat Customers
// First purchase date
{ FIXED [Customer ID] : MIN([Order Date]) }

// Is repeat customer?
IF [Order Date] > [First Purchase Date] THEN "Repeat" ELSE "New" END

// Pattern 3: Cohort Analysis
// Cohort month
{ FIXED [Customer ID] : DATETRUNC('month', MIN([Order Date])) }

// Months since cohort
DATEDIFF('month', [Cohort Month], [Order Date])

// Pattern 4: Running Calculations
// Use table calc, not LOD for better performance
RUNNING_SUM(SUM([Sales]))

// Pattern 5: Percent of Category Total
SUM([Sales]) /
{ FIXED [Category] : SUM([Sales]) }
```

### Performance-Optimized Calculations
```tableau
// SLOW: Multiple LODs
{ FIXED [Customer] : SUM([Sales]) } /
{ FIXED : SUM([Sales]) }

// FAST: Single LOD
{ FIXED [Customer] : SUM([Sales]) } /
TOTAL(SUM([Sales]))

// SLOW: IF in aggregation
SUM(IF [Region] = "West" THEN [Sales] END)

// FAST: Set analysis (use filter)
// Or create boolean calculated field:
Is West = [Region] = "West"
// Then: SUM([Sales (West)])

// SLOW: String operations in loop
SUM([Sales]) WHERE CONTAINS([Product Name], "Premium")

// FAST: Create boolean dimension first
Is Premium Product = CONTAINS([Product Name], "Premium")
```

## Dashboard Design

### Layout Best Practices
```
1. F-Pattern Layout
   ┌─────────────────────────┐
   │ KPI 1 | KPI 2 | KPI 3  │ ← Top row: Key metrics
   ├─────────────────────────┤
   │ Main       │            │
   │ Chart      │  Supporting│ ← Middle: Primary viz
   │            │  Chart     │
   ├─────────────────────────┤
   │ Detail Table/Trends     │ ← Bottom: Details
   └─────────────────────────┘

2. 7±2 Rule
   - Max 5-9 visualizations per dashboard
   - Group related items
   - Use containers for organization

3. Progressive Disclosure
   - Overview on first view
   - Details on drill-down
   - Use dashboard actions

4. Consistent Spacing
   - Standard padding: 8px
   - Between containers: 16px
   - Align elements to grid
```

### Dashboard Actions Strategy
```
// Action Types & When to Use

Filter Action:
├─ Use: Navigate context (map → detailed view)
├─ Best for: Keeping context across worksheets
└─ Example: Click region on map filters all charts

Highlight Action:
├─ Use: Emphasize without filtering
├─ Best for: Comparing across multiple views
└─ Example: Hover product highlights across charts

URL Action:
├─ Use: External integration
├─ Best for: Drill to source system
└─ Example: Click customer → CRM profile

Set Action:
├─ Use: Dynamic grouping
├─ Best for: Creating custom segments
└─ Example: Click products → create "Favorites" set

Parameter Action:
├─ Use: Dynamic calculation changes
├─ Best for: Interactive analysis
└─ Example: Click metric → change calculation
```

## Performance Optimization

### Dashboard Performance Checklist
```
Before Publishing:
□ Run Performance Recorder (Help → Settings & Performance)
□ Analyze slow worksheets
□ Check query times (<3 seconds target)
□ Verify data source filters applied
□ Confirm extracts are optimized
□ Limit mark count (<10,000 per view)
□ Use fixed-size containers
□ Minimize use of quick filters

Common Performance Fixes:
1. Slow Query Execution
   → Add data source filters
   → Create aggregated extract
   → Add indexes to database
   → Use RAWSQLAGG for database aggregation

2. High Mark Count
   → Increase aggregation level
   → Add top N filter
   → Use sampling
   → Consider alternative chart type

3. Complex Calculations
   → Move to data source
   → Simplify LOD expressions
   → Use context filters

4. Dashboard Load Time
   → Lazy load secondary worksheets
   → Reduce number of visualizations
   → Use master filters instead of quick filters
```

### Extract Refresh Strategy
```
Daily Operational Dashboard:
├─ Full Refresh: Sunday 2 AM
├─ Incremental: Daily 6 AM, 12 PM, 6 PM
└─ Data retention: Last 90 days

Weekly Executive Report:
├─ Full Refresh: Monday 6 AM
└─ Data retention: Last 2 years

Real-time Dashboard:
├─ Live connection to database
└─ Aggregate table in database (refreshed hourly)
```

## Version Control

### Workbook Versioning
```bash
# Git repository for .twb files (XML-based)
git init
git add Sales_Dashboard_v1.twb
git commit -m "Initial sales dashboard"

# Tag releases
git tag -a v1.0 -m "Release version 1.0"

# Branch for major changes
git checkout -b feature/new-metric
# Make changes
git commit -m "Add customer lifetime value metric"
git push origin feature/new-metric

# Merge after review
git checkout main
git merge feature/new-metric
```

### Change Documentation
```markdown
# CHANGELOG.md

## [2.0.0] - 2024-11-15

### Added
- Customer lifetime value calculation
- Cohort retention analysis
- Mobile-optimized layout

### Changed
- Updated color palette for accessibility
- Improved filter performance with sets
- Optimized extracts (50% size reduction)

### Fixed
- Null handling in revenue calculations
- Date filter behavior in Q4
- Export formatting for Excel

### Deprecated
- Legacy regional grouping (use new Territory field)
```

## Testing Strategy

### Pre-Publication Checklist
```
Data Accuracy:
□ Spot-check calculations against source
□ Verify totals match reports
□ Test edge cases (null, zero, negative)
□ Confirm date filters work correctly
□ Validate LOD expressions

Functionality:
□ Test all filters
□ Verify dashboard actions
□ Check parameter controls
□ Test on different screen sizes
□ Verify mobile layout

Performance:
□ Load time < 5 seconds
□ Queries execute < 3 seconds
□ Smooth interactions
□ No timeout errors

User Experience:
□ Clear titles and labels
□ Helpful tooltips
□ Consistent formatting
□ Accessible color choices (WCAG AA)
□ Instructions for complex features
```

### User Acceptance Testing
```
Test Scenarios:
1. "As a sales manager, I want to see my team's performance"
   - Can filter to my team?
   - Can see individual rep performance?
   - Can drill into details?

2. "As an executive, I need monthly trends"
   - Date filter works correctly?
   - Can switch between metrics?
   - Can export for board presentation?

3. "As an analyst, I need to explore data"
   - Can slice by multiple dimensions?
   - Can create custom groupings?
   - Can export underlying data?
```

## Deployment Workflow

### Development → QA → Production
```
Development Environment:
├─ Individual workbooks in personal space
├─ Test with sample data
└─ Iterate quickly

QA Environment:
├─ Shared QA project
├─ Full data (or representative sample)
├─ User acceptance testing
└─ Performance testing

Production Environment:
├─ Published to appropriate project
├─ Permissions configured
├─ Extract refresh scheduled
├─ Subscriptions configured
└─ Monitoring enabled
```

### Publishing Checklist
```python
# Automated publishing script
import tableauserverclient as TSC

# Configuration
server_url = 'https://tableau.company.com'
site_id = 'production'
project_name = 'Sales'

# Connect
tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_secret, site_id)
server = TSC.Server(server_url, use_server_version=True)

with server.auth.sign_in(tableau_auth):
    # Publish workbook
    workbook_path = 'Sales_Dashboard_v2.twbx'
    workbook = TSC.WorkbookItem(project_id)

    workbook = server.workbooks.publish(
        workbook,
        workbook_path,
        mode=TSC.Server.PublishMode.Overwrite,  # Or CreateNew
        skip_connection_check=False
    )

    # Set permissions
    server.workbooks.update_permissions(
        workbook,
        [TSC.PermissionsRule(
            grantee=sales_group,
            capabilities={
                TSC.Permission.Read: TSC.Permission.Mode.Allow,
                TSC.Permission.ExportData: TSC.Permission.Mode.Deny
            }
        )]
    )

    # Schedule refresh
    schedule = server.schedules.get_by_id(daily_schedule_id)
    server.datasources.refresh(datasource_id)

    print(f"Published {workbook.name} to {project_name}")
```

## Maintenance

### Regular Tasks
```
Daily:
- Monitor extract refresh failures
- Review performance alerts
- Address user-reported issues

Weekly:
- Review usage analytics
- Check for stale content
- Update documentation

Monthly:
- Performance optimization review
- User access audit
- Retire unused content

Quarterly:
- Major version updates
- Training refreshers
- Strategic content review
```

### Monitoring Queries
```sql
-- Slow dashboards
SELECT
    dashboard_name,
    AVG(response_time_ms) as avg_response_time,
    COUNT(*) as view_count
FROM _dashboard_stats
WHERE timestamp >= CURRENT_DATE - 7
GROUP BY dashboard_name
HAVING AVG(response_time_ms) > 5000
ORDER BY avg_response_time DESC;

-- Failed refreshes
SELECT
    data_source_name,
    failed_at,
    error_message
FROM _extract_refresh_log
WHERE status = 'Failed'
  AND failed_at >= CURRENT_DATE - 1
ORDER BY failed_at DESC;

-- Unused content
SELECT
    workbook_name,
    MAX(accessed_at) as last_accessed
FROM _workbook_access_log
GROUP BY workbook_name
HAVING MAX(accessed_at) < CURRENT_DATE - 90
ORDER BY last_accessed;
```

## Common Pitfalls to Avoid

### Anti-Patterns
```
❌ Don't:
- Use many data sources in one workbook
- Create calculations on worksheets (use data source level)
- Ignore data source filters
- Mix aggregation levels without LOD
- Use live connection to slow databases
- Create overly complex dashboards (>10 sheets)
- Hardcode values (use parameters)
- Skip documentation
- Publish directly to production

✓ Do:
- Consolidate data sources when possible
- Create reusable data sources
- Always use data source filters
- Understand LOD expression scope
- Use extracts for performance
- Follow 7±2 rule for dashboards
- Parameterize for flexibility
- Document complex calculations
- Follow dev → qa → prod workflow
```

## Resources & Learning Path

### Essential Documentation
- Tableau Help: https://help.tableau.com
- Best Practices: https://help.tableau.com/current/blueprint
- Community Forums: https://community.tableau.com
- Sample Workbooks: Tableau Public Gallery

### Skill Development
```
Beginner (0-6 months):
- Master basic chart types
- Learn calculated fields
- Understand data blending
- Create simple dashboards

Intermediate (6-18 months):
- LOD expressions
- Table calculations
- Advanced dashboard actions
- Performance optimization

Advanced (18+ months):
- Complex data modeling
- Tableau Server administration
- JavaScript API
- Custom extensions
```
