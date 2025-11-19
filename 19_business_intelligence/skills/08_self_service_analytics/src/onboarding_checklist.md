# Self-Service Analytics Onboarding Checklist

## New Analyst/User Onboarding
**Version:** 2.0
**Last Updated:** November 2024
**Estimated Duration:** 2-3 hours (Day 1)

---

## Pre-Onboarding (Before Day 1)

### Manager/Sponsor Actions
- [ ] Submit analytics platform access request (template: analytics-access-form)
- [ ] Confirm user's role/level (Viewer, Analyst, Engineer, Admin)
- [ ] Identify assigned team and mentor
- [ ] Schedule onboarding session (30 minutes)
- [ ] Send welcome email with portal URL and documentation link
- [ ] Prepare example queries/dashboards for user's department

### HR/IT Actions
- [ ] Create SSO account with corporate email
- [ ] Assign to appropriate security groups
- [ ] Configure MFA (Multi-Factor Authentication)
- [ ] Provision data warehouse access
- [ ] Send credentials reset link
- [ ] Add to #analytics-onboarding Slack channel

### Analytics Team Actions
- [ ] Review user's access requirements document
- [ ] Plan datasets introduction (max 5 for day 1)
- [ ] Prepare personalized dashboard
- [ ] Schedule month-1 mentor check-ins
- [ ] Create user profile in analytics system

---

## Day 1: Platform Fundamentals (2-3 hours)

### First Hour: Getting Started

**09:00 - Welcome & Setup (15 min)**
- [ ] Welcome meeting with onboarding lead
- [ ] Confirm platform access working (can login)
- [ ] Share onboarding agenda
- [ ] Clarify team structure and contacts
- [ ] Answer initial questions

**09:15 - Portal Navigation (30 min)**
- [ ] Walk through homepage layout
  - [ ] Featured dashboards
  - [ ] Search and discovery
  - [ ] Help resources
  - [ ] User settings and preferences
- [ ] Customize sidebar and favorites
- [ ] Set timezone and language preferences
- [ ] Review user profile

**09:45 - Dashboard Basics (30 min)**
- [ ] Open 2-3 example dashboards from team
- [ ] Explain dashboard components (title, filters, charts)
- [ ] Demonstrate filtering and date range selection
- [ ] Show how to drill-down into details
- [ ] Practice: Filter dashboard and note key metrics
- [ ] Save/bookmark important dashboards

**10:15 - Break (15 min)**

### Second Hour: Core Functionality

**10:30 - Data Model Overview (25 min)**
- [ ] Explain fact vs. dimension tables
- [ ] Review team's key datasets
- [ ] Show data dictionary/schema explorer
- [ ] Discuss data refresh schedule
- [ ] Share glossary of business terms
- [ ] Point to documentation resources

**10:55 - Running Your First Query (30 min)**
- [ ] Open query editor
- [ ] Review SQL syntax basics (SELECT, WHERE, GROUP BY)
- [ ] Run pre-built query together
- [ ] Modify query (change filter/column)
- [ ] Review execution plan
- [ ] Export results (CSV/JSON)
- [ ] Save query to personal folder
- [ ] Hands-on: Write simple query independently

**11:25 - Saving & Sharing (15 min)**
- [ ] Save query to organized folder structure
- [ ] Name conventions (team_purpose_date)
- [ ] Share query with team
- [ ] Add description/documentation
- [ ] Set refresh schedule (if applicable)

**11:40 - Daily Dashboards Assignment (10 min)**
- [ ] Assign 1-2 key dashboards to monitor daily/weekly
- [ ] Explain refresh schedules
- [ ] Set up email/Slack alerts (optional)
- [ ] Add to quick-access bookmarks

---

## Day 1: Governance & Access Control (30 min)

### Data Governance

**12:00 - Data Access & Permissions**
- [ ] Review access level (read-only, query, create)
- [ ] Explain role-based access control
- [ ] Request additional access if needed (process takes 2-3 days)
- [ ] Discuss sensitive data handling
- [ ] Review data masking policies
- [ ] Understand PII (Personally Identifiable Information) protection

**12:10 - Documentation & Data Lineage**
- [ ] Show data lineage view (table dependencies)
- [ ] Explain SLAs (Service Level Agreements)
- [ ] Review certification status of metrics
- [ ] Find owners of datasets
- [ ] Understand data quality status

**12:20 - Support & Escalation**
- [ ] Share support resources
  - [ ] Help button in platform
  - [ ] Slack channel: #analytics-help
  - [ ] Email: analytics-support@company.com
  - [ ] Documentation wiki
- [ ] Provide mentor's contact info
- [ ] Schedule follow-up with mentor (tomorrow)

---

## Day 2-3: Deep Dive Training (Async or Scheduled)

### Complete by End of Week 1

**Dashboard Creation (1 hour)**
- [ ] Watch: Dashboard Builder Tutorial (video, 15 min)
- [ ] Walkthrough: Create personal dashboard (30 min)
  - [ ] Add 3 tiles (tables, charts, KPIs)
  - [ ] Add filters
  - [ ] Configure refresh schedule
- [ ] Share dashboard with mentor for feedback

**SQL Queries (1.5 hours)**
- [ ] Complete: SQL Fundamentals Tutorial
  - [ ] SELECT and WHERE clauses
  - [ ] JOINs (INNER, LEFT)
  - [ ] GROUP BY and aggregations
  - [ ] Common functions (DATE, CASE, etc.)
- [ ] Practice: 5 practice queries with solutions
- [ ] Challenge: Write custom query for your needs

**Best Practices (1 hour)**
- [ ] Read: Query Performance Guide
- [ ] Read: Dashboard Design Best Practices
- [ ] Read: Data Governance Policies
- [ ] Read: FAQ & Troubleshooting Guide

---

## Week 1: Department-Specific Training

### Schedule with Team Lead (1.5 hours)

**Team Overview**
- [ ] Department's key metrics and KPIs
- [ ] Main data sources and tables
- [ ] Common analyses and dashboards
- [ ] Reporting cadence and deadlines
- [ ] Key stakeholders and audience

**Datasets Deep-Dive**
- [ ] Walk through 3-5 team datasets
- [ ] Explain table schemas
- [ ] Review data quality known issues
- [ ] Show example queries
- [ ] Discuss refresh schedules

**Common Workflows**
- [ ] How to access weekly/monthly reports
- [ ] Who to ask for access to additional data
- [ ] Approval process for new dashboards
- [ ] How to request changes to existing dashboards
- [ ] Process for data issues/escalation

**Q&A & Next Steps**
- [ ] Answer questions
- [ ] Provide team-specific resources
- [ ] Set expectations for month 1
- [ ] Schedule month 1 check-in

---

## Week 1: Self-Study Modules (3 hours total)

Complete all (can be spread throughout week):

**Module 1: Data Basics (45 min)**
- [ ] Video: What is Business Intelligence?
- [ ] Video: Dimensions and Metrics Explained
- [ ] Interactive: Data Type Quiz (pass 80%+)
- [ ] Reading: Glossary of Terms

**Module 2: Reading Visualizations (45 min)**
- [ ] Video: Chart Types and When to Use Them
- [ ] Interactive: Dashboard Interpretation Scenarios
- [ ] Practice: Identify insights in sample charts
- [ ] Quiz: Visualization Comprehension

**Module 3: SQL for Analytics (60 min)**
- [ ] Video: SQL Fundamentals (Part 1-3)
- [ ] Interactive Labs: Practice SQL queries
- [ ] Challenge: 5 practice queries (self-assessed)
- [ ] Quiz: SQL Syntax and Logic

---

## Week 2: Hands-On Projects & Review

### Project 1: Explore Your First Dataset (1.5 hours)
- [ ] Select one key team dataset
- [ ] Understand schema and columns
- [ ] Run 3 exploratory queries
- [ ] Create simple dashboard from queries
- [ ] Document findings (1 paragraph)
- [ ] Share with mentor for feedback

### Project 2: Answer a Real Business Question (1.5 hours)
- [ ] Identify business question (with manager/team)
- [ ] Design analytical approach
- [ ] Write queries to answer question
- [ ] Create visualization of results
- [ ] Present findings to team lead
- [ ] Collect feedback and iterate

### Week 2 Check-in (30 min)
- [ ] Mentor review of projects
- [ ] Questions and clarifications
- [ ] Identify areas for deeper learning
- [ ] Set goals for month 2

---

## Month 1: Certification Track

### Choose Learning Path
- [ ] Level 1: Analytics Fundamentals (all complete by end of month 1)
- [ ] Level 2: Analytics Professional (enroll, start coursework)
- [ ] Custom: Based on role and goals

### Assignments
- [ ] Complete Level 1 modules (20 hours)
- [ ] Pass Level 1 quiz (80%+ required)
- [ ] Create personal dashboard (quality assessment)
- [ ] Attend group Q&A sessions (2)

---

## Documentation & Resources

### Key Links to Bookmark
- [ ] Analytics Portal: https://analytics.company.com
- [ ] Data Dictionary: https://docs.company.com/data-dict
- [ ] SQL Reference: https://docs.company.com/sql-reference
- [ ] Governance Policies: https://wiki.company.com/governance
- [ ] Video Tutorials: https://video.company.com/analytics
- [ ] Training Materials: https://training.company.com/analytics

### Slack Channels to Join
- [ ] #analytics-general (platform updates)
- [ ] #analytics-help (support questions)
- [ ] #analytics-announcements (new features)
- [ ] [Department]-analytics (team channel)
- [ ] #data-quality (data issues)

---

## Success Criteria (30 Days)

### By Day 1 End
- [ ] Can login to platform
- [ ] Understands basic navigation
- [ ] Can view and filter dashboards
- [ ] Can run simple queries

### By Week 1 End
- [ ] Completed all self-study modules
- [ ] Passed Level 1 quiz (80%+)
- [ ] Created personal dashboard
- [ ] Has mentor relationship established

### By Week 4 End
- [ ] Created 2+ analysis projects
- [ ] Comfortable with team datasets
- [ ] Can write intermediate queries
- [ ] Receiving positive feedback from team

---

## 90-Day Milestones

### Month 2 Goals
- [ ] Enroll in Level 2 Certification (if applicable)
- [ ] Lead 1 analytical project independently
- [ ] Present findings to stakeholders (internal)
- [ ] Improve query performance (optimization)

### Month 3 Goals
- [ ] Complete Level 1 Certification
- [ ] Mentor another new analyst
- [ ] Contribute to knowledge base/documentation
- [ ] Define areas of expertise/specialization

---

## Support & Escalation

### Immediate Help (Next 2 hours)
- Slack: #analytics-help
- Mentor: Direct message
- Colleague: Ask neighboring desk

### Standard Support (Next Business Day)
- Email: analytics-support@company.com
- Portal: Help → Submit Ticket
- Phone: IT Service Desk

### For Data Issues/Escalations
- Email: analytics-team@company.com
- Slack: @data-quality-oncall
- Severity: Blocking analysis → URGENT

---

## Onboarding Feedback

**Your feedback helps us improve!**

After completing onboarding, please complete this 2-minute survey:

[Onboarding Feedback Form](https://forms.company.com/analytics-onboarding)

**Share:**
- What was most helpful
- What could be improved
- Topics you'd like more training on
- Overall satisfaction

---

## Sign-Off

**New User:** _________________________ Date: _____

**Mentor:** __________________________ Date: _____

**Manager:** _________________________ Date: _____

---

## Next Steps

- [ ] Schedule month-1 performance review (30 min)
- [ ] Define analytical responsibilities
- [ ] Set professional development goals
- [ ] Plan advanced training path
- [ ] Request additional access if needed

**Welcome to the analytics team! We're excited to have you.**

