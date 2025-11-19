# Data Catalog Implementation Guide

## Overview

A data catalog is the foundation of self-service analytics. This guide walks through implementing a production-ready data catalog from scratch.

## Implementation Roadmap

### Phase 1: Planning (Weeks 1-2)

#### Step 1: Define Scope and Goals

```yaml
Objectives:
  Primary:
    - Enable data discovery
    - Reduce time to find data
    - Increase data trust

  Metrics:
    - Time to find data: From 2 hours → 5 minutes
    - Catalog coverage: 80% of frequently used datasets
    - User adoption: 70% weekly active users

Scope Decision:
  Start Narrow:
    ✓ Focus on top 100 most-used tables
    ✓ One data warehouse
    ✓ Core business domains
    ✓ MVP features only

  Don't Boil the Ocean:
    ✗ All databases simultaneously
    ✗ Advanced features first
    ✗ Perfect metadata day 1
    ✗ Every table ever created
```

#### Step 2: Choose Technology

```yaml
Tool Selection Checklist:

Open Source Options:
  Amundsen (Lyft):
    Pros: Mature, proven at scale, free
    Cons: Complex setup, requires hosting
    Best For: Tech-savvy teams, budget-conscious

  DataHub (LinkedIn):
    Pros: Modern, real-time, GraphQL API
    Cons: Newer, smaller community
    Best For: Modern data stack, API-first

Commercial Options:
  Alation:
    Pros: Enterprise features, great support
    Cons: Expensive ($100k+/year)
    Best For: Large enterprises

  Atlan:
    Pros: Modern UI, dbt native, quick setup
    Cons: Newer vendor
    Best For: Modern stack, dbt users

Decision Framework:
  Budget Available: <$50k → Open source
  Technical Resources: Limited → Commercial
  Speed to Value: Fast needed → Commercial
  Customization Needed: High → Open source
```

### Phase 2: Setup (Weeks 3-4)

#### Step 3: Install and Configure

```yaml
# Example: Amundsen Setup (Docker)

1. Prerequisites:
   - Docker and Docker Compose
   - Python 3.7+
   - Access to data warehouse

2. Clone and Setup:
   git clone https://github.com/amundsen-io/amundsen.git
   cd amundsen
   docker-compose -f docker-amundsen.yml up

3. Configure Data Sources:
   # databuilder/example/scripts/sample_snowflake_loader.py
   from pyhocon import ConfigFactory
   from databuilder.extractor.snowflake_metadata_extractor import SnowflakeMetadataExtractor

   job_config = ConfigFactory.from_dict({
       'extractor.snowflake.account': 'your-account.snowflakecomputing.com',
       'extractor.snowflake.user': 'service_account',
       'extractor.snowflake.password': 'password',
       'extractor.snowflake.warehouse': 'ANALYTICS_WH',
       'extractor.snowflake.database': 'PROD',
       'extractor.snowflake.cluster_key': 'snowflake',
   })

4. Run Initial Metadata Extract:
   python sample_snowflake_loader.py

5. Verify:
   - Open http://localhost:5000
   - Search for a table
   - Verify metadata appears
```

#### Step 4: Integrate Data Sources

```yaml
Priority Order:
  1. Production data warehouse (80% of use)
  2. Key BI tool (dashboards, reports)
  3. dbt (transformation lineage)
  4. Other databases (as needed)

Integration Steps Per Source:

Snowflake/BigQuery/Redshift:
  - Create service account
  - Grant read-only metadata access
  - Configure connection
  - Test extraction
  - Schedule regular updates (hourly/daily)

dbt:
  - Install dbt extractor
  - Point to manifest.json
  - Extract model documentation
  - Link to warehouse tables
  - Schedule post-dbt-run

BI Tools (Looker/Tableau):
  - API access setup
  - Extract dashboard metadata
  - Link to underlying tables
  - Show lineage to dashboards
  - Schedule daily refresh
```

### Phase 3: Content (Weeks 5-6)

#### Step 5: Curate Initial Content

```yaml
Top 100 Tables Curation:

1. Identify Priority Tables:
   # Query to find most-used tables
   SELECT
     table_name,
     COUNT(DISTINCT user_name) as unique_users,
     COUNT(*) as query_count
   FROM query_history
   WHERE query_date >= CURRENT_DATE - 90
   GROUP BY table_name
   ORDER BY query_count DESC
   LIMIT 100;

2. Enrich Each Table:
   Required Fields:
     - Description (1-2 sentences)
     - Owner (person or team)
     - Update frequency
     - Data classification

   Nice-to-Have:
     - Column descriptions
     - Usage examples
     - Known issues
     - Related tables

3. Curation Template:
   Table: dim_customers
   Description: Core customer dimension table with one row per customer.
                Contains demographic info, signup data, and current status.
   Owner: customer-analytics-team@company.com
   Update Frequency: Hourly (15 minutes past the hour)
   Freshness SLA: Data should be <2 hours old
   Classification: INTERNAL (contains PII in masked form)
   Quality Score: 94/100

   Key Columns:
     - customer_id: Unique customer identifier (PK)
     - email: Customer email (masked to first char)
     - signup_date: Date customer signed up
     - current_plan: Current subscription plan
     - lifetime_value: Total revenue from customer

   Common Uses:
     - Joining orders to customer attributes
     - Customer segmentation
     - Cohort analysis

   Known Issues:
     - Some legacy customers missing signup_date (pre-2020)
     - Email occasionally null for deactivated accounts

   Example Query:
     SELECT customer_id, email, signup_date, current_plan
     FROM dim_customers
     WHERE current_plan = 'enterprise'
       AND signup_date >= '2025-01-01';
```

#### Step 6: Implement Data Quality Integration

```yaml
Integrate Quality Scores:

1. Setup Quality Tests:
   # dbt tests example
   version: 2
   models:
     - name: dim_customers
       description: Customer dimension
       columns:
         - name: customer_id
           tests:
             - unique
             - not_null
         - name: email
           tests:
             - not_null
         - name: signup_date
           tests:
             - not_null
             - dbt_utils.accepted_range:
                 min_value: "2020-01-01"

2. Display Quality Metrics:
   In Catalog:
     Quality Score: 94/100
     ✓ Completeness: 99% (1% null emails)
     ✓ Freshness: Updated 15 min ago (within SLA)
     ✓ Accuracy: 99.8% referential integrity
     ⚠ Consistency: Known issue with legacy data

3. Link to Quality Dashboard:
   [View detailed quality metrics →]
   - Historical quality trends
   - Failed test details
   - Issue tracking
   - SLA compliance
```

### Phase 4: Adoption (Weeks 7-8)

#### Step 7: Launch and Train

```yaml
Soft Launch (Week 7):
  Audience: Data team + Champions (20-30 people)

  Activities:
    - Demo session (30 min)
    - Hands-on workshop (1 hour)
    - Feedback collection
    - Fix critical issues
    - Refine documentation

  Feedback Focus:
    - Ease of finding data
    - Quality of descriptions
    - Missing features
    - Performance issues
    - UI/UX improvements

General Launch (Week 8):
  Announcement:
    Subject: 📊 Introducing the Data Catalog!

    Finding data just got easier. Our new data catalog helps you:
    ✓ Search and discover datasets
    ✓ Understand what data means
    ✓ See who owns and uses data
    ✓ Check data quality

    🔗 Access: https://catalog.company.com
    📚 Docs: https://docs.company.com/catalog
    💬 Support: #data-catalog Slack channel

    Get started: 5-minute intro video
    Training: Office hours Tue/Thu 2-3pm

  Training Materials:
    - 5-min introduction video
    - Quick start guide
    - Search tips cheat sheet
    - FAQ document
    - Office hours schedule
```

#### Step 8: Drive Engagement

```yaml
Week 1-2 Tactics:
  Daily Tips in Slack:
    Day 1: "Pro tip: Use quotes for exact match searches"
    Day 2: "Discover datasets by domain in the Browse tab"
    Day 3: "Check the quality score before using data"
    Day 4: "See who else is using a dataset under Usage tab"
    Day 5: "Can't find data? Request it via the catalog"

  Gamification:
    - "Search scavenger hunt" challenge
    - Prizes for finding 10 datasets
    - "Catalog explorer" badge

  Showcase Examples:
    - Feature "Dataset of the Week"
    - Highlight excellent documentation
    - Share user success stories

Week 3-4:
  Metrics Sharing:
    - X searches performed
    - Y users discovered data
    - Z minutes saved
    - Top searched tables

  Continuous Improvement:
    - Address feedback
    - Add requested features
    - Improve documentation
    - Optimize performance
```

### Phase 5: Scale (Weeks 9-12)

#### Step 9: Expand Coverage

```yaml
Beyond Top 100:

1. Automate Documentation:
   # Auto-generate descriptions using AI (GPT-4)
   def generate_description(table_name, column_names):
       prompt = f"""
       Generate a clear 1-2 sentence description for this database table:
       Table: {table_name}
       Columns: {', '.join(column_names)}
       """
       return openai.ChatCompletion.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )

2. Crowdsource Enrichment:
   Enable Users to:
     - Add/edit descriptions
     - Tag datasets
     - Add usage examples
     - Report issues
     - Thumbs up/down

   Moderation:
     - Require approval for edits
     - Data stewards review
     - Version control changes
     - Audit trail

3. Expand Integrations:
   Add:
     - Additional databases
     - More BI tools
     - Jupyter notebooks
     - API documentation
     - Data pipelines (Airflow)

   Lineage Graph:
     Source DB → dbt model → Table → Dashboard
     Show full data flow
```

#### Step 10: Measure and Optimize

```yaml
Success Metrics:

Adoption:
  - Weekly active users: Target 70%
  - Searches per user: Target 5+
  - Coverage: Target 80% of tables

Efficiency:
  - Time to find data: Target <5 min
  - % finding data successfully: Target >90%
  - Documentation completeness: Target >80%

Quality:
  - User satisfaction (NPS): Target >40
  - Search relevance: Target >85%
  - Metadata freshness: Target <24 hours

Dashboard Example:
  # Catalog Usage Dashboard
  - Daily/Weekly/Monthly active users (trend)
  - Search volume (trend)
  - Top searches
  - Most viewed tables
  - Documentation coverage %
  - User satisfaction score
  - Support ticket volume

Optimization Cycle:
  Monthly:
    - Review metrics
    - Analyze user feedback
    - Prioritize improvements
    - Release updates

  Quarterly:
    - Major feature releases
    - Coverage expansion
    - Integration additions
    - Training refreshes
```

## Best Practices

```yaml
Metadata Quality:
  ✓ Clear, jargon-free descriptions
  ✓ Always include owner
  ✓ Keep column descriptions updated
  ✓ Add usage examples
  ✓ Document known issues

Governance:
  ✓ Define metadata standards
  ✓ Assign data stewards
  ✓ Review process for changes
  ✓ Audit trail for edits
  ✓ Regular quality audits

Performance:
  ✓ Fast search (<1 second)
  ✓ Quick page loads
  ✓ Efficient metadata extraction
  ✓ Incremental updates
  ✓ Caching strategy

User Experience:
  ✓ Intuitive navigation
  ✓ Relevant search results
  ✓ Mobile-friendly
  ✓ Clear documentation
  ✓ Responsive support
```

## Common Pitfalls

```yaml
1. Trying to Catalog Everything Day 1:
   Problem: Overwhelmed, low quality
   Solution: Start with top 100 tables

2. Auto-Generated Descriptions Only:
   Problem: Generic, not helpful
   Solution: Human curation for key tables

3. No Ownership Model:
   Problem: Stale metadata, no accountability
   Solution: Assign data stewards per domain

4. Building It and Hoping They Come:
   Problem: Low adoption
   Solution: Active promotion and training

5. Ignoring Data Quality:
   Problem: Users don't trust catalog
   Solution: Integrate quality scores prominently
```

## Checklist

```yaml
Planning:
  □ Goals and metrics defined
  □ Scope identified (start narrow)
  □ Tool selected
  □ Budget approved
  □ Team assigned

Setup:
  □ Tool installed and configured
  □ Data sources connected
  □ Metadata extraction working
  □ Search functional
  □ Authentication integrated

Content:
  □ Top 100 tables documented
  □ Owners assigned
  □ Quality scores integrated
  □ Examples added
  □ Known issues documented

Launch:
  □ Soft launch completed
  □ Feedback incorporated
  □ Training materials created
  □ Communication sent
  □ Support channels ready

Scale:
  □ Adoption metrics tracked
  □ Continuous improvement process
  □ Coverage expanding
  □ User feedback addressed
  □ Integration roadmap
```

## Resources

- Amundsen Documentation: https://www.amundsen.io/amundsen/
- DataHub Quickstart: https://datahubproject.io/docs/quickstart
- "Building a Data Catalog" webinar series
- Data catalog comparison matrix
