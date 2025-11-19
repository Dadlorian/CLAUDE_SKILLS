# Training Curriculum Reference

## Overview

A comprehensive training program is essential for successful self-service analytics adoption. This curriculum framework is based on proven approaches from data-driven organizations like Airbnb's Data University and Spotify's Analytics Guild.

## Learning Paths

### Path 1: Data Consumer
**Target Audience**: All employees, business users
**Duration**: 4-6 hours
**Goal**: Find and understand data independently

#### Module 1: Data Catalog Basics (1 hour)
```yaml
Topics:
  - Navigating the data catalog
  - Searching for datasets
  - Understanding metadata
  - Reading documentation
  - Interpreting quality scores

Hands-On Exercise:
  Task: Find the customer orders table
  - Search for "customer orders"
  - Review table description
  - Check data quality score
  - Preview sample data
  - Identify the owner

Assessment:
  - 5 question quiz on catalog navigation
  - Practical task: Find 3 specific datasets
```

#### Module 2: Understanding Metrics (1.5 hours)
```yaml
Topics:
  - What are metrics vs. dimensions
  - Key business metrics (MRR, DAU, churn)
  - How metrics are calculated
  - Metric definitions and owners
  - When to use which metric

Case Studies:
  - How MRR is calculated from subscriptions
  - Understanding cohort retention metrics
  - Interpreting funnel conversion rates

Hands-On Exercise:
  - Explore metric catalog
  - Understand 5 key company metrics
  - Compare metrics across time periods
```

#### Module 3: Dashboard Usage (1.5 hours)
```yaml
Topics:
  - Navigating dashboard library
  - Filtering and drilling down
  - Exporting data
  - Scheduling reports
  - Interpreting visualizations

Interactive Labs:
  - Explore the executive dashboard
  - Filter by date range and segment
  - Drill down from summary to detail
  - Export chart data to CSV
  - Create a custom view

Assessment:
  - Navigate and answer questions from dashboards
  - Create and schedule a report
```

#### Module 4: Data Literacy Fundamentals (1 hour)
```yaml
Topics:
  - Correlation vs. causation
  - Statistical significance basics
  - Common data pitfalls
  - Asking good data questions
  - When to consult an analyst

Examples:
  - Simpson's Paradox
  - Selection bias
  - Survivorship bias
  - Cherry-picking data

Case Study:
  Real examples of misleading metrics
```

### Path 2: Data Explorer
**Target Audience**: Analysts, data-savvy business users
**Duration**: 16-20 hours
**Goal**: Perform independent analysis

#### Module 1: SQL Fundamentals (4 hours)
```yaml
Topics:
  - SELECT, WHERE, ORDER BY
  - Aggregate functions (COUNT, SUM, AVG)
  - GROUP BY and HAVING
  - Basic JOINs (INNER, LEFT)
  - Date/time functions

Hands-On Labs:
  Lab 1: Basic queries
    - Select columns
    - Filter with WHERE
    - Sort results
    - Aggregate data

  Lab 2: Joining tables
    - Join customers with orders
    - Calculate customer metrics
    - Handle NULLs appropriately

  Lab 3: Time-based analysis
    - Group by date
    - Calculate trends
    - YoY comparisons

Practice Datasets:
  - customer_data (10k rows)
  - order_history (50k rows)
  - product_catalog (1k rows)
```

#### Module 2: Advanced SQL (4 hours)
```yaml
Topics:
  - Subqueries and CTEs
  - Window functions
  - CASE statements
  - String manipulation
  - Query optimization basics

Advanced Labs:
  Lab 1: Complex transformations
    - Multi-level CTEs
    - CASE for segmentation
    - String parsing

  Lab 2: Window functions
    - Running totals
    - Ranking and percentiles
    - LAG/LEAD for comparisons

  Lab 3: Performance
    - Using EXPLAIN
    - Identifying slow queries
    - Optimization techniques

Capstone Project:
  Build a cohort retention analysis from scratch
```

#### Module 3: BI Tool Mastery (4 hours)
```yaml
Tool: [Looker/Tableau/Mode - customize per org]

Topics:
  - Creating visualizations
  - Dashboard design principles
  - Filters and parameters
  - Calculated fields
  - Sharing and collaboration

Design Workshop:
  - Chart type selection
  - Color theory basics
  - Layout best practices
  - Storytelling with data

Hands-On Project:
  Build an executive dashboard:
    - 3-5 key metrics
    - Trend visualizations
    - Comparison charts
    - Interactive filters
    - Clear insights

Peer Review:
  - Present dashboard to group
  - Receive feedback
  - Iterate on design
```

#### Module 4: Analytics Methodologies (4 hours)
```yaml
Topics:
  - Cohort analysis
  - Funnel analysis
  - Segmentation techniques
  - A/B test interpretation
  - Statistical basics

Case Studies:
  1. Retention Analysis:
     - Build cohort retention table
     - Visualize retention curves
     - Identify trends and anomalies

  2. Funnel Optimization:
     - Map conversion funnel
     - Calculate drop-off rates
     - Segment by attributes
     - Identify improvement opportunities

  3. A/B Test Review:
     - Understand experiment design
     - Calculate conversion rates
     - Interpret statistical significance
     - Make recommendations

Group Project:
  Analyze a real business problem using course techniques
```

### Path 3: Data Creator
**Target Audience**: Analytics engineers, data engineers
**Duration**: 24-32 hours
**Goal**: Build certified data products

#### Module 1: Data Modeling (8 hours)
```yaml
Topics:
  - Dimensional modeling (Kimball)
  - Fact and dimension tables
  - Slowly changing dimensions
  - Data vault basics
  - dbt fundamentals

Best Practices:
  - Naming conventions
  - Documentation standards
  - Testing requirements
  - Version control

Hands-On Project:
  Build a dimensional model:
    - Design star schema
    - Create fact table
    - Build dimension tables
    - Implement in dbt
    - Add tests and docs
```

#### Module 2: Metric Layer Development (6 hours)
```yaml
Topics:
  - Metric definition standards
  - Semantic layer architecture
  - Version control for metrics
  - Dependency management
  - Testing and validation

Tools:
  - dbt metrics / LookML / Cube.js

Workshop:
  Create certified metrics:
    - Define business logic
    - Implement in metric layer
    - Add documentation
    - Create tests
    - Submit for certification
```

#### Module 3: Data Quality Engineering (6 hours)
```yaml
Topics:
  - Quality dimensions
  - Test-driven data development
  - Monitoring and alerting
  - Incident response
  - SLA management

Tools:
  - Great Expectations
  - dbt tests
  - Monte Carlo

Hands-On Labs:
  - Write custom data tests
  - Set up quality monitors
  - Create alerting rules
  - Build quality dashboard
  - Document quality standards
```

#### Module 4: Performance & Optimization (4 hours)
```yaml
Topics:
  - Query optimization
  - Indexing strategies
  - Partitioning and clustering
  - Materialization techniques
  - Cost optimization

Database-Specific:
  Snowflake/BigQuery/Redshift optimizations

Lab Exercises:
  - Optimize slow queries
  - Implement incremental models
  - Design partitioning strategy
  - Tune warehouse sizing
  - Monitor costs
```

## Specialized Tracks

### Track A: Product Analytics
```yaml
Duration: 8 hours
Prerequisites: Data Explorer

Topics:
  - Event tracking implementation
  - User journey analysis
  - Feature adoption metrics
  - Experimentation platforms
  - Product insights frameworks

Tools:
  - Amplitude / Mixpanel
  - Feature flag systems
  - A/B testing platforms

Projects:
  - Analyze feature launch
  - Build activation funnel
  - Design experiment
```

### Track B: Marketing Analytics
```yaml
Duration: 8 hours
Prerequisites: Data Explorer

Topics:
  - Attribution modeling
  - Campaign performance
  - Customer acquisition metrics
  - Marketing mix modeling
  - ROI calculation

Tools:
  - Google Analytics
  - Ad platform APIs
  - Attribution tools

Projects:
  - Multi-touch attribution analysis
  - Campaign performance dashboard
  - LTV:CAC analysis
```

### Track C: Financial Analytics
```yaml
Duration: 8 hours
Prerequisites: Data Explorer

Topics:
  - Revenue recognition
  - Cohort-based forecasting
  - Unit economics
  - Budgeting and variance analysis
  - Financial modeling

Compliance:
  - SOX requirements
  - Audit trail maintenance
  - Control documentation

Projects:
  - Build revenue waterfall
  - Create budget vs. actual dashboard
  - Model SaaS metrics
```

## Certification Program

### Level 1: Certified Data Consumer
```yaml
Requirements:
  - Complete Data Consumer path
  - Pass 80% on final exam (20 questions)
  - Demonstrate catalog proficiency

Benefits:
  - Digital badge
  - Expanded dashboard access
  - Listed in data directory

Validity: 12 months (recertification required)
```

### Level 2: Certified Data Analyst
```yaml
Requirements:
  - Level 1 certification
  - Complete Data Explorer path
  - Pass 75% on advanced exam (40 questions)
  - Complete capstone project
  - Peer review passing score

Capstone Options:
  - Build analytical dashboard
  - Perform complex analysis
  - Create data story presentation

Benefits:
  - Advanced tool access
  - Query database privileges
  - Can mentor Level 1s
  - Priority support

Validity: 24 months
```

### Level 3: Certified Data Creator
```yaml
Requirements:
  - Level 2 certification
  - Complete Data Creator path
  - Pass 70% on expert exam (60 questions)
  - Build certified data product
  - Steward approval

Data Product Requirements:
  - Well-documented model
  - Comprehensive tests
  - Quality monitoring
  - Performance optimized
  - Production deployed

Benefits:
  - Can create certified datasets
  - Write access to data warehouse
  - Metric definition authority
  - Can train others

Validity: 36 months
```

## Delivery Methods

### Live Instructor-Led
```yaml
Format: Virtual or in-person workshops
Duration: 2-4 hour sessions
Pros:
  - Interactive Q&A
  - Hands-on guidance
  - Networking
  - Immediate feedback

Cons:
  - Scheduling challenges
  - Scalability limits
  - Higher cost

Best For:
  - Initial launches
  - Complex topics
  - Leadership training
```

### Self-Paced Online
```yaml
Format: Video modules + quizzes
Duration: Complete at own pace
Pros:
  - Flexible scheduling
  - Highly scalable
  - Reusable content
  - Consistent quality

Cons:
  - Lower engagement
  - No live interaction
  - Requires self-discipline

Best For:
  - Global teams
  - Refresher training
  - Asynchronous learning
```

### Blended Learning
```yaml
Format: Online + live sessions
Structure:
  - Pre-work: Watch videos (2 hours)
  - Workshop: Hands-on practice (4 hours)
  - Post-work: Capstone project (2 hours)

Pros:
  - Best of both worlds
  - Efficient use of time
  - Deep learning
  - Builds community

Recommended Approach
```

## Support Infrastructure

### Office Hours
```yaml
Schedule: Tuesdays and Thursdays, 2-3pm
Format: Open Zoom session
Staff: 2-3 data team members

Topics:
  - Tool usage questions
  - Query optimization help
  - Data interpretation
  - Project guidance
  - Certification support

Average Attendance: 5-15 users
```

### Slack Community
```yaml
Channels:
  #data-questions: General help
  #data-learning: Training discussions
  #data-showcase: Share insights
  #data-office-hours: Session coordination

Guidelines:
  - Search before asking
  - Provide context
  - Share solutions
  - Be respectful
  - Keep it relevant

Moderation: Data team + champions
```

### Knowledge Base
```yaml
Structure:
  /getting-started
    - Quick start guide
    - Tool access
    - First query tutorial

  /how-to-guides
    - Common tasks
    - Tool features
    - Best practices

  /reference
    - SQL syntax
    - Function library
    - Metric definitions

  /troubleshooting
    - Common errors
    - Performance issues
    - Access problems

Technology: Confluence / Notion / GitBook
Update Frequency: Weekly
```

## Measurement & Iteration

### Training Metrics
```yaml
Engagement:
  - Course enrollment
  - Completion rate
  - Time to complete
  - Video watch time
  - Exercise completion

Knowledge Retention:
  - Pre/post test scores
  - Certification pass rates
  - Practical assessment results

Application:
  - Post-training query volume
  - Dashboard creation
  - Self-service rate
  - Support ticket reduction

Satisfaction:
  - NPS score
  - Course ratings
  - Feedback themes
  - Improvement suggestions
```

### Continuous Improvement
```yaml
Quarterly Reviews:
  - Analyze metrics
  - Review feedback
  - Update content
  - Refresh examples
  - Add new modules

Annual Overhaul:
  - Tool updates
  - Curriculum refresh
  - New learning paths
  - Industry trends
  - Best practice updates
```

## Resources

### Internal Materials
- Video library (50+ recordings)
- Exercise datasets (curated and safe)
- SQL cheat sheet
- Dashboard design guide
- Data dictionary

### External Resources
- Mode Analytics SQL tutorial
- Coursera: SQL for Data Science
- DataCamp courses
- Locally Optimistic blog
- Data storytelling books

## Success Stories

### Airbnb's Data University
- 1000+ employees trained
- 80% certification rate
- 50% reduction in analyst tickets
- Increased data democratization

### Spotify's Analytics Guild
- Cross-functional community
- Regular knowledge sharing
- Self-service experimentation
- Data-driven culture

## References

- Airbnb Data University case study
- Spotify Engineering Blog
- "Building a Data-Driven Organization" by Carl Anderson
- Mode Analytics training framework
