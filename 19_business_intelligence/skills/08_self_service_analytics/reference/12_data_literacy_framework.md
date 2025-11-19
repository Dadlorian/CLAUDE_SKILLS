# Data Literacy Framework Reference

## Overview

Data literacy is the ability to read, work with, analyze, and communicate with data. Building organizational data literacy is fundamental to self-service analytics success.

## Data Literacy Competency Model

### Level 1: Data Consumer (Foundational)

```yaml
Knowledge:
  - What is data and why it matters
  - Basic data terminology
  - How to find data
  - How to read dashboards
  - Basic chart types

Skills:
  - Navigate data catalog
  - Use dashboard filters
  - Read common visualizations
  - Export data
  - Ask data questions

Behaviors:
  - Consult data before decisions
  - Question data sources
  - Recognize when to ask for help
  - Share data-driven insights

Assessment:
  - Can find relevant dashboard
  - Can filter to answer question
  - Can interpret basic charts
  - Understands data limitations
```

### Level 2: Data Explorer (Intermediate)

```yaml
Knowledge:
  - SQL basics
  - Joins and aggregations
  - Statistical concepts
  - Data quality dimensions
  - Metric definitions

Skills:
  - Write basic SQL queries
  - Create simple dashboards
  - Join datasets
  - Calculate metrics
  - Identify data quality issues

Behaviors:
  - Self-service first
  - Validate data accuracy
  - Document analyses
  - Share findings
  - Collaborate with analysts

Assessment:
  - Can write SQL to answer questions
  - Can create dashboard
  - Can calculate KPIs
  - Understands data limitations
```

### Level 3: Data Analyst (Advanced)

```yaml
Knowledge:
  - Advanced SQL
  - Statistical methods
  - Experimental design
  - Data modeling
  - Performance optimization

Skills:
  - Complex analyses
  - A/B test design
  - Metric creation
  - Data pipeline basics
  - Storytelling with data

Behaviors:
  - Proactive analysis
  - Rigorous methodology
  - Mentor others
  - Challenge assumptions
  - Drive decisions with data

Assessment:
  - Can perform cohort analysis
  - Can design experiments
  - Can create certified metrics
  - Can mentor others
```

### Level 4: Data Specialist (Expert)

```yaml
Knowledge:
  - Advanced statistics
  - Machine learning basics
  - Data architecture
  - Tool development
  - Best practices

Skills:
  - Predictive modeling
  - Pipeline development
  - Tool customization
  - Advanced optimization
  - Thought leadership

Behaviors:
  - Innovation
  - Teaching
  - Standards development
  - Community building
  - Industry contribution

Assessment:
  - Can build ML models
  - Can architect solutions
  - Can set best practices
  - Can train others
```

## Core Competencies

### 1. Data Discovery

```yaml
Skills:
  - Use data catalog effectively
  - Understand metadata
  - Read data documentation
  - Identify relevant datasets
  - Assess data quality scores

Training Exercises:
  - Find the customer orders table
  - Identify the data owner
  - Check data freshness
  - Review quality metrics
  - Read table documentation

Assessment Questions:
  - Where would you find monthly revenue data?
  - Who owns the customer dataset?
  - How fresh is the orders data?
  - What's the quality score of users table?
```

### 2. Data Interpretation

```yaml
Skills:
  - Read charts and graphs
  - Understand axis scales
  - Identify trends
  - Spot anomalies
  - Recognize patterns

Common Chart Types:
  Line Chart:
    Use: Trends over time
    Read: Direction, rate of change, patterns
    Pitfalls: Truncated Y-axis, wrong time grain

  Bar Chart:
    Use: Compare categories
    Read: Relative sizes, rankings
    Pitfalls: 3D effects, non-zero baseline

  Pie Chart:
    Use: Part-to-whole (limited use)
    Read: Proportions
    Pitfalls: Too many slices, 3D, hard to compare

  Scatter Plot:
    Use: Relationships between variables
    Read: Correlation, clusters, outliers
    Pitfalls: Correlation ≠ causation

Training Exercise:
  Present chart, ask:
    - What does this show?
    - What's the trend?
    - Any anomalies?
    - What questions does this raise?
```

### 3. Critical Thinking

```yaml
Skills:
  - Question assumptions
  - Identify biases
  - Recognize causation vs. correlation
  - Consider alternative explanations
  - Understand limitations

Common Pitfalls:
  Selection Bias:
    Example: Survey only responds
    Impact: Non-representative sample
    Detection: Consider who's missing

  Survivorship Bias:
    Example: Only study successful companies
    Impact: Ignore failures
    Detection: Look for excluded data

  Simpson's Paradox:
    Example: Trend reverses when segmented
    Impact: Wrong conclusion
    Detection: Always segment data

  Correlation ≠ Causation:
    Example: Ice cream sales & drownings
    Impact: Wrong causal inference
    Detection: Look for confounding variables

Training Exercises:
  - Case studies of data misuse
  - "Spot the bias" exercises
  - A/B test interpretation
  - Root cause analysis
```

### 4. Statistical Reasoning

```yaml
Concepts:

Descriptive Statistics:
  - Mean, median, mode
  - Standard deviation
  - Percentiles
  - Distributions

Inferential Statistics:
  - Sampling
  - Confidence intervals
  - Statistical significance
  - P-values
  - Power analysis

Practical Application:
  "Is this change significant?"
    - Sample size adequate?
    - Variance considered?
    - Statistical test appropriate?
    - Practical significance?

  "Is this metric up or down?"
    - Compared to what?
    - Seasonal patterns?
    - Random variation?
    - Confidence interval?

Training Approach:
  - Focus on intuition, not math
  - Real-world examples
  - Common mistakes
  - When to consult expert
```

### 5. Communication

```yaml
Skills:
  - Translate data to insights
  - Create compelling visualizations
  - Tell data stories
  - Tailor to audience
  - Actionable recommendations

Storytelling Framework:
  1. Context: Why does this matter?
  2. Insight: What did we learn?
  3. Evidence: How do we know?
  4. Action: What should we do?

Visualization Principles:
  - Choose appropriate chart type
  - Clear labels and titles
  - Highlight key insights
  - Remove clutter
  - Accessible color schemes

Audience Adaptation:
  Executives:
    - Lead with bottom line
    - High-level insights
    - Clear recommendations
    - <5 slides

  Peers:
    - Show methodology
    - Detailed findings
    - Supporting analysis
    - Q&A friendly

  Technical:
    - Rigorous methods
    - Statistical details
    - Code/queries
    - Reproducible
```

## Training Curriculum

### Foundational Course (4 hours)

```yaml
Module 1: Why Data Matters (30 min)
  - Data-driven decision making
  - Types of data questions
  - Real-world examples
  - ROI of data literacy

Module 2: Finding Data (45 min)
  - Data catalog navigation
  - Understanding metadata
  - Data quality scores
  - Exercise: Find 5 datasets

Module 3: Reading Dashboards (90 min)
  - Common visualizations
  - Filters and drill-downs
  - Interpreting trends
  - Spotting anomalies
  - Exercise: Dashboard scavenger hunt

Module 4: Asking Good Questions (45 min)
  - Formulating data questions
  - When to self-serve vs. ask analyst
  - Common pitfalls
  - Exercise: Question workshop

Module 5: Assessment (30 min)
  - Quiz
  - Practical exercise
  - Certification
```

### Intermediate Course (8 hours)

```yaml
Module 1: SQL Basics (2 hours)
  - SELECT, WHERE, ORDER BY
  - Aggregations (SUM, COUNT, AVG)
  - GROUP BY
  - Hands-on exercises

Module 2: Joins & Advanced SQL (2 hours)
  - INNER JOIN, LEFT JOIN
  - Subqueries
  - CTEs
  - Hands-on exercises

Module 3: Dashboard Creation (2 hours)
  - Tool overview
  - Chart types
  - Filters and parameters
  - Best practices
  - Build your own dashboard

Module 4: Analytics Thinking (2 hours)
  - Metric definitions
  - A/B testing basics
  - Cohort analysis
  - Statistical significance
  - Case studies
```

## Assessment Methods

### Knowledge Checks

```yaml
Quiz Questions:

  Foundational:
    - What does this chart show?
    - Where would you find revenue data?
    - What's a good question to ask with data?
    - How do you know if data is trustworthy?

  Intermediate:
    - Write SQL to calculate monthly revenue
    - What's wrong with this analysis?
    - Interpret this A/B test result
    - When would you use a cohort analysis?

  Advanced:
    - Design an experiment to test hypothesis X
    - What's the best metric for goal Y?
    - How would you optimize this query?
    - Critique this analysis approach
```

### Practical Assessments

```yaml
Foundational:
  Task: Find data to answer business question
  Evaluation:
    - Correct dataset identified
    - Dashboard used effectively
    - Insight articulated clearly
    - Limitations acknowledged

Intermediate:
  Task: Build dashboard for use case
  Evaluation:
    - SQL correct
    - Visualizations appropriate
    - Insights clear
    - Design clean

Advanced:
  Task: Complete analysis project
  Evaluation:
    - Methodology sound
    - Analysis rigorous
    - Findings actionable
    - Communication excellent
```

### Certification Program

```yaml
Level 1 Certification:
  Requirements:
    - Complete foundational course
    - Pass quiz (80% score)
    - Complete practical exercise
  Benefits:
    - Digital badge
    - Dashboard access
    - Listed in directory
  Renewal: Annual

Level 2 Certification:
  Requirements:
    - Level 1 certified
    - Complete intermediate course
    - Pass advanced quiz (75% score)
    - Build demonstration dashboard
  Benefits:
    - Query access
    - Create dashboards
    - Mentor Level 1s
  Renewal: Every 2 years

Level 3 Certification:
  Requirements:
    - Level 2 certified
    - Complete advanced course
    - Comprehensive project
    - Peer review
  Benefits:
    - Create metrics
    - Advanced tools
    - Train others
  Renewal: Every 3 years
```

## Resources & Materials

### Learning Resources

```yaml
Internal:
  - Video library
  - Interactive tutorials
  - Documentation wiki
  - Office hours
  - Peer mentoring

External:
  Books:
    - "Data Literacy" by Jordan Morrow
    - "How to Lie with Statistics" by Darrell Huff
    - "Naked Statistics" by Charles Wheelan
    - "Storytelling with Data" by Cole Nussbaumer Knaflic

  Online Courses:
    - Mode Analytics SQL Tutorial
    - Khan Academy Statistics
    - DataCamp courses
    - Coursera Data Literacy

  Communities:
    - Locally Optimistic
    - Data visualization society
    - Internal Slack channels
```

### Job Aids

```yaml
Quick Reference Cards:
  - SQL cheat sheet
  - Chart selection guide
  - Common metrics glossary
  - Data catalog shortcuts
  - Best practices checklist

Templates:
  - Analysis template
  - Dashboard design guide
  - Presentation template
  - One-pager format

Tools:
  - Data quality checker
  - Sample size calculator
  - Statistical significance calculator
  - Chart type selector
```

## Success Metrics

```yaml
Organizational:
  - % of employees with Level 1+ certification
  - Average literacy score improvement
  - Self-service adoption rate
  - Training completion rate

Individual:
  - Pre/post test scores
  - Practical assessment results
  - Tool usage frequency
  - Quality of analyses
  - Peer reviews

Business Impact:
  - Faster decision making
  - More data-driven decisions
  - Reduced analyst bottleneck
  - Innovation velocity
  - Competitive advantage
```

## References

- "Data Literacy: How to Make Your Experiments Robust and Reproducible" by Jordan Morrow
- Gartner Data Literacy Framework
- Qlik Data Literacy Report
- Tableau Data Literacy Resources
