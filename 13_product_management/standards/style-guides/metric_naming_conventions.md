# Metric Naming Conventions Standard

## Table of Contents
1. [Overview](#overview)
2. [Naming Framework](#naming-framework)
3. [Core Principles](#core-principles)
4. [Category-Specific Standards](#category-specific-standards)
5. [Examples by Domain](#examples-by-domain)
6. [Calculation and Definitions](#calculation-and-definitions)
7. [Documentation Standards](#documentation-standards)
8. [Do's and Don'ts](#dos-and-donts)

## Overview

Consistent metric naming is essential for clear communication, accurate analysis, and avoiding confusion across teams. This standard defines how all product metrics should be named, defined, calculated, and documented across the organization.

**Goals**:
- Ensure metrics are understood consistently across all teams
- Enable easy identification of metric purpose and calculation
- Facilitate dashboard and reporting standardization
- Support metric governance and discovery

**Scope**: All product metrics, business metrics, and analytics measurements used in reporting, dashboards, and business decisions

## Naming Framework

### Naming Syntax Structure

```
[Timeframe]_[Object]_[Action/Attribute]_[Qualifier]
```

**Components**:
- **Timeframe** (optional): Daily (D), Weekly (W), Monthly (M), or omitted if cumulative
- **Object**: What is being measured (user, subscription, order, feature, session)
- **Action/Attribute**: What quality is being measured (retention, adoption, count, value)
- **Qualifier** (optional): Additional specificity (segment, channel, status)

### Examples of Naming Structure

```
D_Active_Users                    # Daily Active Users
M_New_Customers_Acquired         # Monthly New Customers Acquired
Subscription_Churn_Rate           # Subscription Churn Rate
NPS_Enterprise_Segment            # Net Promoter Score (Enterprise Segment)
Feature_Adoption_Free_Tier        # Feature Adoption Rate (Free Tier Users)
D_Session_Count_Mobile_App        # Daily Session Count (Mobile App)
Monthly_Recurring_Revenue         # Monthly Recurring Revenue (MRR)
Customer_Lifetime_Value_Cohort_2024 # Customer Lifetime Value (2024 Cohort)
```

## Core Principles

### 1. Clarity and Specificity
- Metric name should clearly indicate what is being measured
- Avoid ambiguous terms: "Engagement" needs qualifier (which type?)
- Use descriptive terms over abbreviations (except common ones: DAU, MAU, ARR, MRR, NPS)
- Include timeframe when measured at specific interval

**Good**: "M_New_Trial_Signups_Web_Channel"
**Bad**: "New Signups" (which channel? which product? what timeframe?)

### 2. Consistency with Dimensions
- If metrics appear in multiple dashboards, naming must be identical
- Use standard objects: user, customer, account, subscription, session, order, feature
- Use standard actions: count, rate, value, growth, adoption, retention, churn

**Standard Objects**:
- User (individual person using product)
- Customer (paying entity)
- Account (organizational entity)
- Subscription (active paid service)
- Session (user interaction period)
- Feature (product capability)
- Order (transaction)
- Cohort (user group by time or characteristic)

**Standard Actions**:
- Count/Volume: Number of occurrences
- Rate/Percentage: Ratio or percentage
- Value: Monetary or quantitative amount
- Growth: Change over time
- Adoption: Usage percentage or count
- Retention: Percentage retained over period
- Churn: Percentage lost over period
- Engagement: Interaction intensity measure

### 3. Avoid Redundancy
- Metric name shouldn't repeat dimension or filter
- Don't include "Total" if it's implied
- Don't use "Number of" if "Count" suffix indicates number

**Good**: "M_Active_Users" (in dashboard context of date range)
**Bad**: "M_Total_Number_of_Active_Users"

**Good**: "Churn_Rate_Enterprise" (dimension in name)
**Bad**: "Enterprise_Churn_Rate_Enterprise" (redundant)

### 4. Use Standard Abbreviations
Only use common, universally understood abbreviations:
- DAU = Daily Active Users
- MAU = Monthly Active Users
- WAU = Weekly Active Users
- MRR = Monthly Recurring Revenue
- ARR = Annual Recurring Revenue
- CAC = Customer Acquisition Cost
- LTV/CLV = Customer Lifetime Value
- NPS = Net Promoter Score
- ARPU = Average Revenue Per User
- Churn vs. Retention (not "turn-over" or other variants)

**Avoid**:
- Custom abbreviations known to only some teams
- Uncommon industry abbreviations without definition
- Acronyms that differ by team (always standardize)

### 5. Format and Case Conventions
- Use descriptive phrases in camelCase or snake_case
- Capitalize first letter of each significant word (Title Case for display)
- Use underscores to separate major components when naming metric in system
- When writing metric in text, use Title Case: "Daily Active Users"

**System Storage**: `d_active_users`, `monthly_recurring_revenue`
**Display/Text**: "Daily Active Users", "Monthly Recurring Revenue"
**Shorthand**: "DAU", "MRR"

## Category-Specific Standards

### User Engagement Metrics

#### Naming Template
```
[Timeframe]_[User_Type]_[Activity_Metric]_[Optional_Detail]
```

**Standard User Activity Metrics**:
- Active_Users: User took any action (configurable by product)
- Engaged_Users: User met activity threshold (must define threshold)
- New_Users: User signed up in period
- Returning_Users: User active in current period who was active in prior period
- Session_Count: Number of discrete user sessions
- Time_Spent: Aggregate or average duration in product

**Examples**:
- D_Active_Users
- M_Engaged_Users (define engagement threshold in metric definition)
- M_New_Users_Enterprise
- D_Returning_Users_Free_Tier
- D_Session_Count_Mobile
- Avg_Session_Duration_Minutes

#### Engagement Metric Do's
- Define "active" clearly (any action, or specific type)
- Define "engaged" with threshold (minimum: 5 minutes, 2 pages, or other criteria)
- Use "Returning" only for users who were active in both periods
- Distinguish between "New" and "Existing" users
- Specify platform/channel if metric differs by channel

### Retention and Churn Metrics

#### Naming Template
```
[Entity]_[Retention/Churn]_[Period]_[Qualifier]
```

**Examples**:
- User_Retention_Day_7
- User_Retention_Day_30
- Customer_Churn_Rate_Monthly
- Subscription_Churn_Rate_Annual
- Feature_Retention_Week_1
- Customer_Churn_Rate_Enterprise_Annual
- Cohort_2024_01_User_Retention_M12

#### Retention/Churn Standards
- Specify lookback period explicitly (Day_7, Week_1, Month_3, etc.)
- Distinguish retention (%) from churn rate (these are inverse)
- For cohort metrics, include cohort identifier: "Cohort_2024_01_Retention_M1"
- "Churned" = left or canceled in period
- "Retained" = remained active in period

**Example Definition**:
```
Metric Name: Customer_Churn_Rate_Monthly
Formula: (Customers_Churned_in_Month / Customers_at_Month_Start) × 100
Lookback Period: Calendar month
Entities Included: Paid customers only (exclude trials)
Calculated: On last day of month
```

### Revenue and Financial Metrics

#### Naming Template
```
[Revenue_Type]_[Optional_Timeframe]_[Optional_Qualifier]
```

**Standard Revenue Metrics**:
- ARR: Annual Recurring Revenue
- MRR: Monthly Recurring Revenue
- ACV: Annual Contract Value
- ARPU: Average Revenue Per User
- Revenue_Per_Customer: Average revenue per customer
- Bookings: Contract value signed in period
- Recognized_Revenue: Accounting basis revenue

**Examples**:
- MRR (not "Monthly_Revenue")
- ARR_Increasing_Seats (metric for metric with increasing seat licenses)
- ACV_Enterprise (average annual contract value for enterprise)
- Bookings_2024_Q1
- Recognized_Revenue_2024_Q1

#### Revenue Metric Standards
- Use MRR and ARR, not custom period calculations
- Distinguish between "Bookings" (signed) and "Recognized Revenue" (accounting basis)
- Include qualifiers for filtered metrics: "MRR_Paid_Customers" (exclude trials)
- For ACV, always specify customer segment: "ACV_Enterprise_Annual"
- Use same time period for consistency: "Fiscal Month" not "Calendar Month" (or vice versa)

### Product Feature Adoption Metrics

#### Naming Template
```
Feature_[Action]_[Optional_Qualifier]
```

**Standard Feature Metrics**:
- Feature_Adoption_Rate: % of users who have used feature
- Feature_Penetration: % of target user segment who used feature
- Feature_Usage_Count: Number of uses of feature
- Feature_Weekly_Active: Users who used feature in week
- Feature_Frequency: Average uses per user per period
- Feature_Time_Spent: Time users spend in feature

**Examples**:
- Feature_Adoption_Rate_New_Dashboard
- Feature_Penetration_Enterprise_Segment
- Feature_Usage_Count_Data_Export_Weekly
- Feature_Time_Spent_Avg_Minutes
- Dashboard_Feature_Weekly_Active_Users

#### Feature Metric Standards
- Always specify which feature in name or description
- Distinguish between "Adoption" (% who tried) and "Active" (% using in period)
- Include user segment if metric varies by segment: "Feature_Adoption_Rate_Enterprise"
- Use action verbs for clarity: "Exported", "Filtered", "Shared"

### Conversion and Funnel Metrics

#### Naming Template
```
[Funnel_Name]_Conversion_[Stage]_[Qualifier]
```

**Examples**:
- Signup_Conversion_Rate
- Trial_to_Paid_Conversion_Rate
- Feature_Adoption_Conversion_Rate
- Free_to_Paid_Conversion_Rate_30_Day
- Enterprise_Sales_Conversion_Rate_Pipeline

#### Conversion Metric Standards
- Name should indicate start and end of conversion
- Specify lookback period if relevant: "Trial_to_Paid_30_Day"
- For multi-step funnels, name the overall conversion: "Signup_to_Active_Day_7"
- Always define denominator clearly in metric definition

### Cohort-Based Metrics

#### Naming Template
```
Cohort_[Cohort_Identifier]_[Metric]_[Period_Marker]
```

**Examples**:
- Cohort_2024_01_Retention_M3 (January 2024 cohort, Month 3 retention)
- Cohort_2024_01_Users_Upgrade_M6
- Cohort_FreeTrialJan2024_ARPU_M12
- Cohort_Enterprise_OnboardingTime_Days

#### Cohort Metric Standards
- Include cohort definition date/period: "2024_01" for January 2024
- Use consistent period markers: M1 (Month 1), W4 (Week 4), D30 (Day 30)
- Specify cohort definition: "Cohort_TrialSignups_2024Q1_Retention_M3"
- Link cohort metrics to original cohort definition

### Quality and Performance Metrics

#### Naming Template
```
[System/Feature]_[Quality_Metric]_[Unit]
```

**Examples**:
- API_Latency_Milliseconds
- Page_Load_Time_Seconds
- Error_Rate_Percentage
- Feature_Uptime_Percentage
- Data_Sync_Latency_Seconds
- Support_Response_Time_Hours

#### Quality Metric Standards
- Always include unit of measurement in name
- Specify what's being measured: "API" not just "Latency"
- Use percentiles for user-facing metrics: "API_Latency_p95_Milliseconds"
- For availability: use "Uptime" not "Availability" (though either acceptable)

## Examples by Domain

### SaaS Product Domain

**Core Metrics**:
- MRR
- ARR
- Customer_Churn_Rate_Monthly
- Customer_Lifetime_Value
- Customer_Acquisition_Cost
- Trial_to_Paid_Conversion_Rate
- D_Active_Users
- Feature_Adoption_Rate_[Feature_Name]

**Specific Examples**:
```
MRR_Total
MRR_Enterprise_Segment
ARR_YoY_Growth
Customer_Churn_Rate_Monthly_Enterprise
Customer_Churn_Rate_Monthly_Freemium
CLV_Cohort_2024_Q1
DAU_Mobile_App
Feature_Adoption_Report_Export
Feature_Adoption_Rate_Collaboration
Trial_to_Paid_Conversion_7_Day
Trial_to_Paid_Conversion_30_Day
Support_NPS_Monthly
Onboarding_Time_Days_Median
```

### Marketplace Domain

**Core Metrics**:
- GMV: Gross Merchandise Value
- Seller_Count_Active
- Buyer_Count_Active
- Seller_Churn_Rate_Monthly
- Buyer_Churn_Rate_Monthly
- Average_Order_Value
- Transaction_Count_Weekly
- Seller_Listing_Count

**Specific Examples**:
```
GMV_Daily
GMV_Weekly
GMV_YoY_Growth
Seller_Count_Active_Monthly
Buyer_Count_Active_Daily
Seller_Churn_Rate_Monthly
Buyer_Churn_Rate_Monthly
Avg_Order_Value_Weekly
Avg_Order_Value_By_Category
Transaction_Count_Daily
Seller_Listing_Count_Active
Seller_Retention_Day_30
Buyer_Retention_Day_30
```

### Creator Economy Platform Domain

**Core Metrics**:
- Creator_Count_Active
- Fan_Count_Active
- Content_Published_Count
- Engagement_Rate_Content
- Creator_Earnings
- Platform_Payout_Daily

**Specific Examples**:
```
Creator_Count_Active_Monthly
Creator_Count_New_Monthly
Creator_Churn_Rate_Monthly
Fan_Count_Active_Daily
Fan_Engagement_Rate
Content_Published_Count_Daily
Content_Consumption_Hours
Creator_Earnings_Monthly
Creator_Payout_Pending
Platform_Revenue_Share_Monthly
```

## Calculation and Definitions

### Standard Definition Template

Every metric should have a clear definition document following this structure:

```markdown
## Metric Name: [Full Metric Name]

**Shorthand**: [Abbreviation if applicable]
**Category**: [Engagement / Revenue / Retention / etc.]
**Owner**: [Team or person responsible]

### Definition
[One sentence definition of what is measured]

### Formula
[Mathematical formula for calculation]
Example:
  (Users_Who_Took_Action_in_Period / Total_Users) × 100

### Components
- **Numerator**: [Clear definition of what counts]
- **Denominator**: [Clear definition of included set]
- **Time Period**: [Specific period measured]

### Calculation Details
- **Lookback Period**: [Days/weeks/months looking back]
- **Frequency**: [How often calculated: Daily / Weekly / Monthly]
- **Data Source**: [System or database where data comes from]
- **Inclusions**: [What is included in calculation]
- **Exclusions**: [What is explicitly excluded]

### Examples
[Real or realistic examples of calculation]

### Caveats and Limitations
[Known issues or limitations with metric]

### Related Metrics
[Other related metrics for context]

### History
[When metric was created, any changes to definition]
```

### Example Full Metric Definition

```markdown
## Metric Name: Trial_to_Paid_Conversion_Rate_30_Day

**Shorthand**: TTP Conv (30d)
**Category**: Revenue
**Owner**: Product Analytics Team

### Definition
Percentage of users who started a trial in a given month
and converted to a paid subscription within 30 days
of trial start.

### Formula
(Trials_Converted_Within_30_Days / Trials_Started) × 100

### Components
- **Numerator**: Users who:
  - Started trial in the month
  - Transitioned to paid plan within 30 days of trial start
  - Exclude: trials that canceled then restarted

- **Denominator**: All users who started a trial in the month
  - Exclude: trials created in error (flagged by support)
  - Include: trials from all channels (web, mobile, API)

- **Time Period**: Calendar month

### Calculation Details
- **Lookback Period**: 30 days from trial start
- **Frequency**: Calculated on last day of month (always calendar month)
- **Data Source**: Analytics warehouse, events table
- **Inclusions**: All user types, all trial lengths, all channels
- **Exclusions**: Internal staff accounts, free tier users

### Examples
- Month of January: 1,000 trials started
- Of those, 300 converted within 30 days
- Conversion rate = (300 / 1,000) × 100 = 30%

### Caveats and Limitations
- Users who convert after 30 days not captured (see "Trial_to_Paid_Conversion_60_Day")
- Does not account for user intent (accidental vs. deliberate trials)
- Free tier users might show different conversion behavior (excluded from this metric)

### Related Metrics
- Trial_to_Paid_Conversion_Rate_60_Day
- Trial_Start_Count_Monthly
- Paid_Subscription_Count_Monthly
- Trial_Churn_Rate

### History
- Created: January 2023 (initial definition)
- Modified: March 2024 (clarified internal staff exclusion)
```

## Documentation Standards

### Metric Metadata
Every metric in your system should have associated metadata:

```
Metric ID: MET_001
Metric Name: Daily_Active_Users
Display Name: Daily Active Users (DAU)
Description: Number of unique users who took any action in the product on a given day
Category: Engagement
Owner: Product Analytics
Calculation: SELECT COUNT(DISTINCT user_id) FROM events WHERE date = current_date
Data Source: Analytics Warehouse
Frequency: Daily
Created Date: 2023-01-15
Last Modified: 2024-11-01
Stakeholders: [Product, Marketing, Executive]
Dashboard: Product Overview Dashboard
Related Metrics: [Monthly_Active_Users, Weekly_Active_Users]
```

### Metric Registry
Maintain a centralized registry of all metrics:

**Format**: Spreadsheet or database with columns:
- Metric Name
- Shorthand
- Definition
- Formula
- Owner
- Data Source
- Last Updated
- Status (Active / Deprecated / In Development)
- Documentation Link

### Metric Governance
- **New Metrics**: Require definition approval by metrics owner and stakeholder
- **Changes**: Any change to formula or definition requires documentation
- **Deprecation**: Old metrics marked as deprecated, not deleted
- **Archival**: Keep history of metric definitions and calculation changes

## Do's and Don'ts

### DO's

- **DO** be specific about timeframe (Day_7, Month_1, not "Recently")
- **DO** include unit of measurement when not implied (Latency_Milliseconds)
- **DO** use standard objects and actions (User, Customer, Feature, Adoption)
- **DO** distinguish between Rate (%), Count (number), and Value ($)
- **DO** include segment or qualifier in name if metric varies meaningfully by segment
- **DO** document numerator and denominator clearly
- **DO** use Title Case for display names and snake_case for system names
- **DO** maintain consistent metric definitions across teams
- **DO** use "Retention" and "Churn" as inverse metrics (sum = 100%)
- **DO** version your metric definitions when they change
- **DO** create a central metric registry
- **DO** specify lookback period for cohort and retention metrics
- **DO** include data source in metric definition
- **DO** distinguish between "Active" (current period) and "New" (first time)
- **DO** use percentiles for performance metrics (p50, p95, p99)

### DON'Ts

- **DON'T** create ambiguous names that require explanation (e.g., "Engagement")
- **DON'T** mix metric names across teams (same metric, different names)
- **DON'T** omit timeframe when it's part of calculation
- **DON'T** use unexplained internal abbreviations
- **DON'T** name metrics with filters that might change (name instead: "Metric_Segment")
- **DON'T** hide calculation complexity in metric name (explain in definition)
- **DON'T** create metrics without clear owner
- **DON'T** change metric definitions without documentation
- **DON'T** forget to define what "counts" for derived metrics
- **DON'T** use "other" as a category name
- **DON'T** create both "New" and "Total Cumulative" without distinguishing clearly
- **DON'T** mix accounting period definitions (fiscal month vs. calendar month)
- **DON'T** name metrics without unit of measurement when ambiguous
- **DON'T** create duplicate metrics with slightly different names
- **DON'T** deprecate old metrics without maintaining historical data

### Common Naming Anti-Patterns to Avoid

**Anti-Pattern**: Vague primary object
- Wrong: "Engagement_Rate"
- Right: "Feature_Engagement_Rate_Dashboard" or "D_Session_Count"

**Anti-Pattern**: Misleading abbreviations
- Wrong: "Conv" (do they mean conversion, convolution, conference?)
- Right: "Conversion_Rate" or use standard "TTP" (Trial to Paid)

**Anti-Pattern**: Implied calculations
- Wrong: "Revenue" (is this MRR, ARR, daily, total, etc.?)
- Right: "MRR" or "ARR"

**Anti-Pattern**: Missing time period
- Wrong: "User_Churn" (churn over what period?)
- Right: "Customer_Churn_Rate_Monthly"

**Anti-Pattern**: Multiple meanings in same name
- Wrong: "Active_Users" (active today vs. active in product category?)
- Right: "D_Active_Users" or "Feature_Active_Users_Daily"

**Anti-Pattern**: Overly specific names that won't scale
- Wrong: "Conversion_Rate_Stripe_Payment_Mobile_June_2024_Campaign_A"
- Right: "Conversion_Rate_Mobile_Campaign_A" (dimensions track the specifics)

## Quick Reference: Standard Metric Naming

| Category | Pattern | Example |
|----------|---------|---------|
| User Activity | [Timeframe]_[User_Type]_[Action] | D_Active_Users |
| Retention | [Entity]_Retention_[Period] | Customer_Retention_Month_3 |
| Churn | [Entity]_Churn_Rate_[Period] | Customer_Churn_Rate_Monthly |
| Revenue | [Revenue_Type]_[Timeframe] | MRR, ARR, ACV |
| Feature | Feature_[Action]_[Feature_Name] | Feature_Adoption_Rate_Dashboard |
| Conversion | [Start]_to_[End]_[Period] | Trial_to_Paid_30_Day |
| Cohort | Cohort_[Identifier]_[Metric] | Cohort_2024_01_Retention_M3 |
| Quality | [System]_[Quality_Type]_[Unit] | API_Latency_Milliseconds |

---

**Metric Naming Audit Checklist**:
- [ ] Metric name is unambiguous without explanation
- [ ] Timeframe is clear (if not inherent)
- [ ] Metric has written definition with formula
- [ ] Numerator and denominator are clearly defined
- [ ] Data source is documented
- [ ] Metric name is consistent with company standards
- [ ] Related metrics are cross-referenced
- [ ] Owner is assigned and accountable
- [ ] Metric included in central registry
- [ ] Metric follows category-specific conventions
