# Product Health Audit Checklist
## Quarterly Comprehensive Product Assessment Framework

**Version**: 1.0
**Last Updated**: 2025-11-19
**Authority**: Best practices from Amplitude, Mixpanel, Intercom, and leading product analytics organizations

---

## Overview

A quarterly product health audit is a comprehensive assessment of your product's performance, health, and trajectory. It combines quantitative metrics, qualitative feedback, and strategic analysis to identify opportunities, risks, and necessary pivots.

**Purpose**: Understand product health holistically, identify issues before they become crises, and make data-driven strategic decisions.

**Timeline**: 3-4 weeks (with ongoing data collection)
**Participation**: Product, Analytics, Engineering, Design, Sales, Customer Success
**Success Rate Target**: 90% of audit questions answered comprehensively
**Key Output**: Product health scorecard, strategic recommendations, action plan

---

## Table of Contents

1. [Preparation & Setup (Week 1)](#preparation--setup-week-1)
2. [Performance Metrics Assessment (Week 1-2)](#performance-metrics-assessment-week-1-2)
3. [Customer Health Analysis (Week 2)](#customer-health-analysis-week-2)
4. [Product Quality Assessment (Week 2-3)](#product-quality-assessment-week-2-3)
5. [User Experience & Design Review (Week 3)](#user-experience--design-review-week-3)
6. [Strategic Alignment Assessment (Week 3)](#strategic-alignment-assessment-week-3)
7. [Market & Competitive Analysis (Week 3-4)](#market--competitive-analysis-week-3-4)
8. [Risk Assessment & Opportunities (Week 4)](#risk-assessment--opportunities-week-4)
9. [Health Scorecard & Recommendations (Week 4)](#health-scorecard--recommendations-week-4)

---

## Preparation & Setup (Week 1)

**Owner**: PM Lead
**Objective**: Prepare audit framework, data sources, and team

### 1.1 Audit Planning & Framing

#### [ ] Define Audit Scope & Objectives
- **Timeline**: 1.5 hours
- **Owner**: PM Lead
- Define which product areas to audit
- Set specific audit questions
- Identify stakeholders who need to contribute
- Define success criteria for audit
- **Success Criteria**: Scope document created and shared

#### [ ] Establish Baseline Data Sources
- **Timeline**: 2 hours
- **Owner**: Analytics Lead
- Identify all data systems available
- Get access to analytics dashboards
- Verify data accuracy and completeness
- Document data collection methodology
- **Success Criteria**: All data sources accessible

#### [ ] Create Audit Dashboard
- **Timeline**: 3 hours
- **Owner**: Analytics Lead
- Build comprehensive health dashboard
- Include all key metrics
- Enable period-over-period comparisons
- Enable segment analysis
- **Success Criteria**: Dashboard built and verified

#### [ ] Schedule Audit Activities
- **Timeline**: 1 hour
- **Owner**: Product Ops
- Schedule all interviews and review sessions
- Get calendar commitments from key people
- Block time for data analysis
- Set milestone deadlines
- **Success Criteria**: All audit activities scheduled

#### [ ] Create Audit Document Template
- **Timeline**: 1 hour
- **Owner**: Product Ops
- Create audit report template
- Define sections and structure
- Set up collaboration document
- Establish review process
- **Success Criteria**: Template ready for use

### 1.2 Team Preparation & Communication

#### [ ] Kick Off Audit with Leadership
- **Timeline**: 1 hour
- **Owner**: PM Lead with VP Product
- Explain audit objectives and timeline
- Address any concerns
- Ensure executive sponsorship
- Confirm resource allocation
- **Success Criteria**: Leadership briefed and supportive

#### [ ] Brief Product & Engineering Teams
- **Timeline**: 1 hour
- **Owner**: PM Lead
- Explain audit process
- Request data and insights
- Clarify participation expectations
- Invite feedback and concerns
- **Success Criteria**: Teams understand audit process

#### [ ] Identify Key Reviewers
- **Timeline**: 30 min
- **Owner**: PM Lead
- Select reviewers for each section
- Assign responsibilities
- Set up peer review process
- Establish quality gates
- **Success Criteria**: Reviewers assigned

---

## Performance Metrics Assessment (Week 1-2)

**Owner**: Analytics Lead with PM
**Objective**: Evaluate product performance against targets and benchmarks

### 2.1 Core Product Metrics Review

#### [ ] Revenue & Business Metrics
- **Timeline**: 4 hours
- **Owner**: Analytics Lead
- **Success Criteria**: Dashboard created and analyzed

**Metrics to Analyze**:
- [ ] Total Revenue (Quarter vs. Prior quarters)
  - Quarterly revenue trend
  - Quarterly growth rate
  - Revenue vs. plan
  - Variance analysis and explanation

- [ ] Monthly Recurring Revenue (MRR) or Annual Recurring Revenue (ARR)
  - Current MRR/ARR value
  - Growth rate (MoM, QoQ, YoY)
  - Net revenue retention
  - Churn impact

- [ ] Customer Acquisition Cost (CAC)
  - CAC by channel
  - CAC payback period
  - CAC trend over time
  - Comparison to LTV

- [ ] Customer Lifetime Value (LTV)
  - Average LTV
  - LTV by cohort
  - LTV to CAC ratio (Target: 3+)
  - LTV trend

- [ ] Customer Metrics
  - Total number of customers
  - New customers acquired (quarter)
  - Customer growth rate
  - Customer concentration (% from top 10, 20)

#### [ ] Engagement & Usage Metrics
- **Timeline**: 4 hours
- **Owner**: Analytics Lead
- **Success Criteria**: Usage patterns documented

**Metrics to Analyze**:
- [ ] Daily Active Users (DAU) / Monthly Active Users (MAU)
  - DAU/MAU counts
  - DAU/MAU growth trends
  - DAU/MAU ratio (engagement indicator)
  - User trend by segment

- [ ] Activation Metrics
  - % of signups that activate
  - Time to activation
  - Activation funnel completion
  - Activation rate by cohort

- [ ] Feature Adoption
  - Top 10 features by adoption
  - Feature adoption trends
  - Net-new features adoption rate
  - Feature penetration by user segment

- [ ] Session Metrics
  - Average sessions per user per day
  - Session duration trends
  - Session frequency by cohort
  - Session quality metrics

- [ ] Retention Metrics
  - Day 1, 7, 30 retention rates
  - Retention cohort analysis
  - Cohort retention trends
  - Segment retention comparison

- [ ] Churn & Expansion
  - Gross churn rate
  - Net churn rate
  - Expansion revenue rate
  - Downsell rate

#### [ ] Quality Metrics
- **Timeline**: 3 hours
- **Owner**: Analytics Lead
- **Success Criteria**: Quality trends assessed

**Metrics to Analyze**:
- [ ] Performance Metrics
  - Page load time (median, p95)
  - Error rate (<0.1% target)
  - API response time
  - Uptime %

- [ ] Crash & Error Tracking
  - Error rate trend
  - Top errors by frequency
  - Client-side vs. server-side errors
  - Critical errors

### 2.2 Benchmark Analysis

#### [ ] Industry Benchmark Comparison
- **Timeline**: 2 hours
- **Owner**: Analytics Lead with PMM
- **Success Criteria**: Benchmark analysis completed

**Analysis to Conduct**:
- [ ] Compare to Industry Benchmarks
  - CAC benchmark for industry
  - LTV/CAC ratio benchmark
  - Churn rate benchmark
  - Retention rate benchmarks

- [ ] Compare to Competitor Metrics (if available)
  - Estimated competitor user base
  - Estimated competitor growth rate
  - Feature comparison metrics
  - Market share trajectory

- [ ] SaaS Metrics Benchmarks
  - Rule of 40 score (Growth % + Net Revenue Retention %)
  - CAC ratio
  - Time to CAC payback
  - Magic number (revenue growth / sales spend)

#### [ ] Metric Health Scoring
- **Timeline**: 2 hours
- **Owner**: PM Lead
- **Success Criteria**: Health scoring matrix completed

**Scoring System** (1-5 scale):
- 5 = Excellent (top quartile, above plan)
- 4 = Good (above average, meeting plan)
- 3 = Adequate (meets minimum targets)
- 2 = Concerning (below targets, needs attention)
- 1 = Critical (significant risk, requires action)

**Score Each**:
- Revenue metrics
- Growth metrics
- Engagement metrics
- Retention metrics
- Quality metrics
- Customer health metrics

---

## Customer Health Analysis (Week 2)

**Owner**: Customer Success Lead with PM
**Objective**: Understand customer sentiment, health, and satisfaction

### 3.1 Customer Satisfaction & Sentiment

#### [ ] NPS & Customer Satisfaction Analysis
- **Timeline**: 3 hours
- **Owner**: Customer Success Lead
- **Success Criteria**: Sentiment trends documented

**Analysis to Conduct**:
- [ ] Net Promoter Score (NPS)
  - Current NPS score
  - NPS trend (QoQ, YoY)
  - NPS by customer segment
  - NPS by product area
  - Detractor feedback themes

- [ ] Customer Satisfaction (CSAT)
  - Overall product CSAT
  - CSAT by feature
  - CSAT trend over quarter
  - Satisfaction by customer segment

- [ ] Customer Effort Score (CES)
  - Ease of use rating
  - Onboarding ease rating
  - Support experience rating
  - Feature discoverability

- [ ] Sentiment Analysis
  - Customer communication sentiment
  - Support ticket sentiment
  - Feature request sentiment
  - Feedback tone and themes

#### [ ] Customer Feedback Synthesis
- **Timeline**: 3 hours
- **Owner**: Customer Success Lead
- **Success Criteria**: Feedback summary created

**Feedback Sources to Review**:
- [ ] Customer Interviews
  - Conduct 10-15 customer interviews
  - Document pain points
  - Document feature requests
  - Document product improvement ideas
  - Identify sentiment themes

- [ ] Support Tickets
  - Analyze support ticket volume
  - Categorize issues by type
  - Identify top issues
  - Track resolution time
  - Identify product improvement opportunities

- [ ] Customer Reviews & Feedback
  - G2, Capterra ratings analysis
  - Review trends and themes
  - Negative review root causes
  - Positive review key drivers
  - Comparison to competitors

- [ ] Feature Requests & Feedback
  - Top feature requests by frequency
  - Feature request sentiment
  - Requested by segment analysis
  - Strategic alignment assessment

### 3.2 Customer Health & Retention

#### [ ] Customer Health Scoring
- **Timeline**: 3 hours
- **Owner**: Customer Success Lead
- **Success Criteria**: Customer health assessment completed

**Health Assessment**:
- [ ] At-Risk Customers
  - Identify at-risk customer accounts
  - Assess churn risk
  - Understand churn drivers
  - Create retention strategy

- [ ] High-Value Customer Assessment
  - Identify top 20% customers
  - Assess satisfaction level
  - Expansion opportunity potential
  - Engagement level

- [ ] Customer Health Metrics
  - Customer health score trend
  - Health score distribution
  - Correlation of health score to churn
  - Leading indicators of churn

- [ ] Segment Health Analysis
  - Health by customer segment
  - Enterprise customer health
  - SMB customer health
  - New vs. established customer health

#### [ ] Expansion & Upsell Assessment
- **Timeline**: 2 hours
- **Owner**: Customer Success Lead with Sales
- **Success Criteria**: Expansion opportunities identified

**Assessment to Conduct**:
- [ ] Expansion Revenue Trends
  - Net revenue retention rate
  - Expansion revenue amount
  - Expansion revenue growth rate
  - Expansion by customer segment

- [ ] Upsell Opportunities
  - Customers with expansion potential
  - Feature adoption correlation to expansion
  - Cross-sell opportunities
  - Pricing tier optimization opportunities

- [ ] Expansion Velocity
  - Time to expansion
  - Expansion rate by cohort
  - Feature adoption leading to expansion
  - Pricing impact on expansion

### 3.3 Customer Segment Analysis

#### [ ] Segment Performance Analysis
- **Timeline**: 2 hours
- **Owner**: Analytics Lead
- **Success Criteria**: Segment analysis completed

**Analyze by Key Segments**:
- [ ] Enterprise Segment
  - Customer count and concentration
  - Revenue contribution
  - Growth rate
  - Retention rate
  - Health trends

- [ ] Mid-Market Segment
  - Customer count
  - Revenue contribution and trend
  - Retention and churn rate
  - Expansion potential

- [ ] SMB/Startup Segment
  - Customer count and growth
  - LTV and profitability
  - Retention rate
  - Upsell potential

- [ ] By Industry/Vertical
  - Performance by vertical
  - Vertical-specific challenges
  - Vertical-specific opportunities
  - Vertical fit assessment

---

## Product Quality Assessment (Week 2-3)

**Owner**: QA/Engineering Lead with PM
**Objective**: Evaluate product quality, stability, and technical health

### 4.1 Quality & Stability Metrics

#### [ ] Bug & Issue Tracking
- **Timeline**: 2 hours
- **Owner**: QA Lead
- **Success Criteria**: Quality trends assessed

**Analysis to Conduct**:
- [ ] Bug Volume & Severity
  - Total bug count
  - Critical bugs (0 is target)
  - High severity bugs (minimize)
  - Bug trend over quarter
  - Open vs. closed bugs

- [ ] Bug Lifecycle
  - Average time to fix bugs
  - Critical bug resolution time
  - Bug escape rate (bugs found post-launch)
  - Regression rate (same bug twice)

- [ ] Root Cause Analysis
  - Most common bug categories
  - Root cause of critical bugs
  - Preventable issues
  - Process improvement opportunities

#### [ ] System Performance & Reliability
- **Timeline**: 2 hours
- **Owner**: DevOps/Engineering Lead
- **Success Criteria**: Performance metrics assessed

**Metrics to Analyze**:
- [ ] Uptime & Availability
  - Monthly uptime % (target: 99.9%+)
  - Planned downtime
  - Unplanned outage incidents
  - Outage impact and duration
  - MTTR (Mean Time To Recovery)

- [ ] Performance Metrics
  - Median page load time (target: <2 seconds)
  - P95 page load time (target: <5 seconds)
  - API response time
  - Database query performance
  - Performance trend over quarter

- [ ] Scalability Assessment
  - System handles expected load
  - Auto-scaling effectiveness
  - Capacity planning adequacy
  - Performance under peak load

- [ ] Infrastructure Health
  - Resource utilization metrics
  - Database performance
  - Cache effectiveness
  - CDN performance

#### [ ] Security & Compliance Assessment
- **Timeline**: 2 hours
- **Owner**: Security Lead
- **Success Criteria**: Security assessment completed

**Assessment to Conduct**:
- [ ] Security Status
  - Vulnerabilities identified in quarter
  - Vulnerabilities fixed
  - Critical vulnerabilities (0 acceptable)
  - Security incident count
  - Response time to security issues

- [ ] Compliance Status
  - SOC 2 compliance maintained
  - GDPR compliance status
  - CCPA compliance status
  - Industry-specific compliance
  - Audit results

- [ ] Data Security
  - Data encryption status
  - Access control appropriateness
  - Data breach incidents (0 target)
  - Security audit results
  - Third-party security assessments

### 4.2 Technical Debt Assessment

#### [ ] Technical Debt Evaluation
- **Timeline**: 3 hours
- **Owner**: CTO/Tech Lead
- **Success Criteria**: Technical debt prioritized

**Assessment to Conduct**:
- [ ] Technical Debt Inventory
  - Areas with high technical debt
  - Architecture limitations
  - Outdated dependencies
  - Code quality concerns
  - Test coverage gaps

- [ ] Technical Debt Impact
  - Impact on development velocity
  - Impact on product quality
  - Impact on scalability
  - Impact on team morale
  - Risk assessment

- [ ] Technical Roadmap
  - Technical debt paydown plan
  - Refactoring priorities
  - Architecture improvements needed
  - Technology upgrades needed
  - Timeline for improvements

- [ ] Test Coverage & Automation
  - Unit test coverage % (target: 80%+)
  - Integration test coverage
  - E2E test coverage
  - Test automation rate
  - Test execution time

### 4.3 Engineering Velocity & Capacity

#### [ ] Development Productivity Assessment
- **Timeline**: 2 hours
- **Owner**: Engineering Lead
- **Success Criteria**: Capacity trends documented

**Analysis to Conduct**:
- [ ] Velocity Trends
  - Story points completed per sprint
  - Velocity trend over past 3 months
  - Velocity compared to capacity plan
  - Velocity by team member

- [ ] Capacity Planning
  - Planned capacity vs. actual capacity
  - Unplanned work impact on velocity
  - Support & maintenance work allocation
  - New feature development allocation

- [ ] Development Cycle Time
  - Average time from development start to production
  - Time in code review
  - Time in QA
  - Deployment frequency
  - Lead time for changes

- [ ] Team Health
  - Unplanned absences/turnover
  - Team satisfaction
  - Skill gaps and training needs
  - Team morale and engagement

---

## User Experience & Design Review (Week 3)

**Owner**: Design Lead with PM
**Objective**: Assess user experience quality and design system health

### 5.1 Design System & UI Quality

#### [ ] Design System Health
- **Timeline**: 3 hours
- **Owner**: Design Lead
- **Success Criteria**: Design system assessment completed

**Assessment to Conduct**:
- [ ] Design System Completeness
  - % of UI components documented
  - % of components in design system
  - Consistency of implementation
  - Documentation quality

- [ ] Design System Usage
  - % of features using design system
  - Custom component usage
  - Component reuse metrics
  - Design consistency score

- [ ] Design System Performance
  - Load time of design assets
  - Design-to-development handoff efficiency
  - Design iteration speed
  - Accessibility compliance

#### [ ] Visual Design & Consistency
- **Timeline**: 2 hours
- **Owner**: Design Lead
- **Success Criteria**: Design consistency audit completed

**Audit to Conduct**:
- [ ] Visual Consistency
  - Color palette usage consistency
  - Typography consistency
  - Icon consistency and completeness
  - Spacing and layout consistency

- [ ] Interaction Patterns
  - Consistent interaction patterns
  - Predictable user flows
  - Consistent error handling
  - Consistent form patterns

- [ ] Accessibility Compliance
  - WCAG 2.1 AA compliance level
  - Color contrast verification
  - Keyboard navigation support
  - Screen reader compatibility
  - Semantic HTML usage

- [ ] Mobile & Responsive Design
  - Mobile usability
  - Touch target sizes appropriate
  - Responsive behavior correct
  - Mobile performance acceptable

### 5.2 User Experience Quality

#### [ ] Information Architecture & Navigation
- **Timeline**: 2 hours
- **Owner**: Design Lead with PM
- **Success Criteria**: Navigation assessment completed

**Assessment to Conduct**:
- [ ] Navigation Clarity
  - Primary navigation intuitive
  - Secondary navigation logical
  - Search functionality effective
  - Help/documentation easy to find

- [ ] Information Hierarchy
  - Important information prominent
  - Content well organized
  - Cognitive load appropriate
  - Discoverability of features

- [ ] User Flows
  - Key user flows documented
  - Task completion rate
  - Steps to complete tasks optimal
  - Error recovery clear

#### [ ] Usability & Functionality
- **Timeline**: 3 hours
- **Owner**: Design Lead
- **Success Criteria**: Usability assessment completed

**Assessment to Conduct**:
- [ ] Feature Discoverability
  - New features discoverable
  - Feature adoption rate
  - Feature visibility
  - Onboarding effectiveness

- [ ] User Onboarding
  - First-time user experience quality
  - Onboarding completion rate
  - Time to first value
  - Onboarding drop-off points

- [ ] Help & Documentation
  - Help documentation quality
  - Help documentation discoverability
  - FAQ effectiveness
  - Support ticket themes

- [ ] User Testing Results
  - Usability test findings
  - User confusion points
  - Accessibility issues discovered
  - Design improvement opportunities

### 5.3 Design Debt Assessment

#### [ ] Design Debt & Backlog
- **Timeline**: 2 hours
- **Owner**: Design Lead
- **Success Criteria**: Design debt prioritized

**Assessment to Conduct**:
- [ ] Design Debt Inventory
  - Outdated design patterns
  - Inconsistent component implementations
  - Accessibility gaps
  - Mobile experience gaps

- [ ] Design Impact
  - Impact on user experience quality
  - Impact on brand perception
  - Impact on accessibility
  - User satisfaction impact

- [ ] Design Roadmap
  - Design system improvements
  - Experience improvements planned
  - Accessibility improvements
  - Mobile experience improvements

---

## Strategic Alignment Assessment (Week 3)

**Owner**: PM Lead with VP Product
**Objective**: Verify product strategy execution and alignment

### 6.1 Strategy Execution Assessment

#### [ ] Quarterly Strategy Execution
- **Timeline**: 2 hours
- **Owner**: PM Lead
- **Success Criteria**: Strategy execution assessed

**Assessment to Conduct**:
- [ ] Plan vs. Actual
  - % of planned work completed
  - Initiatives shipped on schedule
  - Quality of shipped initiatives
  - Customer impact of initiatives

- [ ] Strategic Theme Progress
  - Progress on theme 1
  - Progress on theme 2
  - Progress on theme 3
  - Theme impact on business metrics

- [ ] OKR Achievement
  - OKR 1 progress
  - OKR 2 progress
  - OKR 3 progress
  - OKR impact on business

#### [ ] Roadmap Effectiveness
- **Timeline**: 2 hours
- **Owner**: PM Lead
- **Success Criteria**: Roadmap assessment completed

**Assessment to Conduct**:
- [ ] Roadmap Execution
  - % of roadmap completed on schedule
  - Scope changes and reasons
  - Deprioritized items and rationale
  - Roadmap accuracy improvements needed

- [ ] Roadmap Alignment
  - Alignment with company strategy
  - Alignment with customer needs
  - Alignment with competitive positioning
  - Stakeholder alignment

- [ ] Roadmap Clarity
  - Team clarity on priorities
  - Stakeholder clarity on direction
  - Communicated effectively
  - Regular updates provided

### 6.2 Vision & Direction Clarity

#### [ ] Product Vision Assessment
- **Timeline**: 1.5 hours
- **Owner**: VP Product with PM
- **Success Criteria**: Vision clarity assessed

**Assessment to Conduct**:
- [ ] Vision Clarity
  - Vision statement clear and compelling
  - Team can articulate vision
  - Customers understand direction
  - Vision guides decision-making

- [ ] Strategic Positioning
  - Market positioning clear and differentiated
  - Competitive advantages clear
  - Unique value proposition strong
  - Market position improving

- [ ] Long-Term Direction
  - 1-year direction clear
  - 3-year vision compelling
  - Investment areas defined
  - Growth strategy defined

---

## Market & Competitive Analysis (Week 3-4)

**Owner**: PMM with PM
**Objective**: Assess competitive positioning and market opportunity

### 7.1 Competitive Landscape Assessment

#### [ ] Competitive Position Review
- **Timeline**: 3 hours
- **Owner**: PMM
- **Success Criteria**: Competitive assessment completed

**Assessment to Conduct**:
- [ ] Competitor Feature Comparison
  - Core feature comparison with top 3 competitors
  - Feature gaps vs. competitors
  - Feature parity assessment
  - Differentiated features

- [ ] Competitor Moves
  - Competitor announcements in quarter
  - Competitive threat assessment
  - Opportunity to differentiate
  - Response required (if any)

- [ ] Market Position
  - Market share estimate
  - Competitive positioning vs. plan
  - Brand perception vs. competitors
  - Customer preference trends

#### [ ] Pricing & Packaging Assessment
- **Timeline**: 2 hours
- **Owner**: PMM with PM
- **Success Criteria**: Pricing assessment completed

**Assessment to Conduct**:
- [ ] Pricing Strategy Effectiveness
  - Pricing aligned with value delivered
  - Pricing competitiveness
  - Pricing tier utilization
  - Price optimization opportunity

- [ ] Packaging & Positioning
  - Feature packaging aligned with segments
  - Packaging vs. competitor offerings
  - Packaging changes needed
  - Tier skipping/downselling analysis

- [ ] Go-To-Market Effectiveness
  - GTM strategy effectiveness
  - Sales enablement adequacy
  - Win rate by segment
  - Win/loss ratio vs. competitors

### 7.2 Market Opportunity Assessment

#### [ ] Market & Trends Analysis
- **Timeline**: 3 hours
- **Owner**: PMM
- **Success Criteria**: Market opportunity assessed

**Assessment to Conduct**:
- [ ] Market Trends
  - Key industry trends
  - Customer expectation shifts
  - Technology shifts relevant to product
  - Emerging opportunities

- [ ] TAM/SAM/SOM Assessment
  - Total addressable market size
  - Serviceable addressable market
  - Serviceable obtainable market
  - Market size trend

- [ ] Customer Needs Evolution
  - Emerging customer needs
  - Unmet customer needs
  - Needs by customer segment
  - Needs by vertical/industry

- [ ] Expansion Opportunities
  - Adjacent market opportunities
  - Geographic expansion opportunity
  - Vertical expansion opportunity
  - Product expansion opportunity

---

## Risk Assessment & Opportunities (Week 4)

**Owner**: PM Lead with VP Product
**Objective**: Identify risks and opportunities

### 8.1 Risk Assessment

#### [ ] Product Risk Identification
- **Timeline**: 3 hours
- **Owner**: PM Lead with cross-functional team
- **Success Criteria**: Risk register created

**Risks to Assess**:
- [ ] Technical Risks
  - Scalability risk
  - Performance risk
  - Security risk
  - Infrastructure risk
  - Technical debt risk

- [ ] Product Risks
  - Feature adoption risk
  - Feature quality risk
  - User experience risk
  - Feature-market fit risk
  - Feature differentiation risk

- [ ] Market/Competitive Risks
  - Competitive threat
  - Market trend risk
  - Customer need shift risk
  - Pricing pressure risk
  - Regulatory risk

- [ ] Organizational/Execution Risks
  - Velocity/capacity risk
  - Skill gap risk
  - Resource constraint risk
  - Execution risk
  - Team turnover risk

- [ ] Business/Revenue Risks
  - Customer churn risk
  - CAC increase risk
  - Price compression risk
  - Market demand risk
  - Revenue risk

#### [ ] Risk Prioritization & Mitigation
- **Timeline**: 2 hours
- **Owner**: VP Product with PM
- **Success Criteria**: Mitigation plan created

**For Each Top Risk**:
- Impact assessment (High/Medium/Low)
- Probability assessment (High/Medium/Low)
- Mitigation strategy
- Owner assignment
- Monitoring approach

### 8.2 Opportunity Assessment

#### [ ] Product Opportunity Identification
- **Timeline**: 3 hours
- **Owner**: PM Lead with cross-functional team
- **Success Criteria**: Opportunity list created

**Opportunities to Identify**:
- [ ] Feature/Product Opportunities
  - High-impact feature opportunities
  - Customer-requested features
  - Adjacent feature opportunities
  - Integration opportunities

- [ ] Market/Customer Opportunities
  - New customer segment opportunities
  - Vertical expansion opportunities
  - Geographic expansion opportunities
  - Pricing/packaging opportunities

- [ ] Operational Opportunities
  - Velocity improvement opportunities
  - Quality improvement opportunities
  - Cost reduction opportunities
  - Experience improvement opportunities

- [ ] Strategic Opportunities
  - Partnership opportunities
  - Acquisition opportunities
  - Ecosystem opportunities
  - Platform opportunities

#### [ ] Opportunity Prioritization
- **Timeline**: 2 hours
- **Owner**: VP Product with PM
- **Success Criteria**: Opportunity prioritization completed

**For Each Top Opportunity**:
- Business impact potential
- Feasibility assessment
- Strategic alignment
- Time to value
- Resource requirements
- Priority ranking

---

## Health Scorecard & Recommendations (Week 4)

**Owner**: PM Lead with VP Product
**Objective**: Create comprehensive health assessment and recommendations

### 9.1 Create Product Health Scorecard

#### [ ] Build Health Scorecard
- **Timeline**: 3 hours
- **Owner**: PM Lead
- **Success Criteria**: Scorecard completed

**Scorecard Components**:

| Category | Key Metrics | Score (1-5) | Status | Trend |
|----------|-----------|------------|--------|-------|
| **Financial Health** | Revenue, MRR/ARR, CAC, LTV | ___ | 🔴🟡🟢 | ↑↔↓ |
| **Growth** | Revenue Growth %, Customer Growth %, DAU/MAU | ___ | 🔴🟡🟢 | ↑↔↓ |
| **Engagement** | DAU, Usage Depth, Retention | ___ | 🔴🟡🟢 | ↑↔↓ |
| **Customer Health** | NPS, CSAT, Churn Rate | ___ | 🔴🟡🟢 | ↑↔↓ |
| **Product Quality** | Uptime, Error Rate, Bug Count | ___ | 🔴🟡🟢 | ↑↔↓ |
| **User Experience** | Accessibility, Design Consistency | ___ | 🔴🟡🟢 | ↑↔↓ |
| **Technical Health** | Technical Debt, Velocity, Coverage | ___ | 🔴🟡🟢 | ↑↔↓ |
| **Market Position** | Competitive Strength, Differentiation | ___ | 🔴🟡🟢 | ↑↔↓ |

**Overall Product Health Score**: ___ / 5

#### [ ] Add Trend Analysis
- **Timeline**: 1 hour
- **Owner**: PM Lead
- Trend over past 3 quarters
- Trend interpretation
- Positive trends to build on
- Concerning trends requiring action

#### [ ] Document Key Findings
- **Timeline**: 2 hours
- **Owner**: PM Lead
- Major strengths to build on
- Critical weaknesses to address
- Key insights and patterns
- Emerging trends
- Strategic implications

### 9.2 Develop Recommendations

#### [ ] Identify Strategic Actions
- **Timeline**: 3 hours
- **Owner**: VP Product with PM
- **Success Criteria**: Action plan created

**Action Plan Should Include**:

**Immediate Actions (Next 30 days)**:
- [ ] Address critical risks (if any)
- [ ] Launch quick wins to improve key metrics
- [ ] Fix quality issues blocking progress
- [ ] Implement low-effort high-impact improvements

**Medium-Term Actions (Next 90 days)**:
- [ ] Invest in top opportunities
- [ ] Mitigate identified risks
- [ ] Improve underperforming areas
- [ ] Build on areas of strength

**Long-Term Strategic Actions (Next year)**:
- [ ] Major feature/product investments
- [ ] Market expansion opportunities
- [ ] Organizational capabilities needed
- [ ] Strategic pivots (if needed)

#### [ ] Prioritize Recommendations
- **Timeline**: 2 hours
- **Owner**: VP Product
- **Success Criteria**: Prioritized action list

**For Each Recommendation**:
- Business impact (Revenue, Growth, Retention, Brand)
- Effort/resource required
- Timeline to impact
- Owner assignment
- Success metrics
- Priority ranking (P0/P1/P2)

#### [ ] Create 90-Day Action Plan
- **Timeline**: 3 hours
- **Owner**: PM Lead
- **Success Criteria**: Action plan approved

**90-Day Plan Should Define**:
- Top 5-7 strategic initiatives
- Business case for each initiative
- Resource allocation
- Timeline and milestones
- Success metrics
- Dependencies and risks
- Owner assignments

### 9.3 Create Audit Report

#### [ ] Document Full Audit Report
- **Timeline**: 4 hours
- **Owner**: PM Lead
- **Success Criteria**: Report completed and reviewed

**Report Structure**:

1. **Executive Summary** (1 page)
   - Overall health score
   - Key findings
   - Top opportunities
   - Top risks
   - Recommended actions

2. **Detailed Assessment** (by section)
   - Metrics analysis
   - Customer health
   - Product quality
   - User experience
   - Strategic alignment
   - Market analysis

3. **Health Scorecard**
   - Score by category
   - Trend analysis
   - Strengths and weaknesses

4. **Risk Assessment**
   - Risk register
   - Mitigation plans
   - Monitoring approach

5. **Opportunity Assessment**
   - Opportunity list
   - Prioritized opportunities
   - Business case

6. **Recommendations & Action Plan**
   - Immediate actions
   - Medium-term actions
   - Long-term strategy
   - Resource plan
   - Timeline

7. **Appendices**
   - Detailed metrics tables
   - Customer feedback summary
   - Competitive analysis
   - Data sources

#### [ ] Review & Finalize
- **Timeline**: 2 hours
- **Owner**: VP Product with PM
- **Success Criteria**: Report approved

**Review Checklist**:
- [ ] All data accurate and verified
- [ ] Findings supported by evidence
- [ ] Recommendations actionable
- [ ] Tone and clarity appropriate
- [ ] Executive summary compelling
- [ ] Data visualizations clear

### 9.4 Present Audit Findings

#### [ ] Executive Briefing
- **Timeline**: 1.5 hours
- **Owner**: VP Product
- **Success Criteria**: Leadership briefed

**Briefing Structure**:
- Product health overview (10 min)
- Key findings by category (15 min)
- Strategic recommendations (10 min)
- Q&A and discussion (20 min)

**Expected Outcomes**:
- Leadership alignment on health status
- Approval of recommended actions
- Resource allocation decisions
- Q next quarter strategic direction

#### [ ] Product Team Presentation
- **Timeline**: 1 hour
- **Owner**: PM Lead
- **Success Criteria**: Team understands findings

**Presentation Coverage**:
- Overall health assessment
- Areas of strength to build on
- Areas for improvement
- Customer feedback highlights
- Strategic direction and priorities

#### [ ] Cross-Functional Briefing
- **Timeline**: 1.5 hours total
- **Owner**: Relevant leaders
- **Success Criteria**: Teams aligned

**Sessions**:
- Engineering on technical priorities
- Design on UX improvements
- Sales/CS on customer insights
- Marketing on competitive positioning

---

## Audit Success Metrics

### Audit Quality Metrics

#### Completeness (Target: 100%)
- [ ] All audit sections completed
- [ ] All data sources reviewed
- [ ] All stakeholders interviewed
- [ ] All metrics analyzed
- [ ] All recommendations developed

#### Accuracy (Target: 100%)
- [ ] All metrics verified for accuracy
- [ ] All data sources confirmed
- [ ] All analyses peer reviewed
- [ ] No conflicting conclusions
- [ ] Sources documented

#### Actionability (Target: 90%+)
- [ ] Recommendations are specific and measurable
- [ ] Recommendations have assigned owners
- [ ] Recommendations have timelines
- [ ] Recommendations have success criteria
- [ ] Recommendations are resourced

### Audit Impact Metrics (Track in Next Quarter)

#### Leadership Satisfaction
- [ ] Leadership finds audit valuable
- [ ] Leadership uses findings for decisions
- [ ] Audit recommendations inform strategy
- [ ] Board/stakeholder confidence in product

#### Decision Quality
- [ ] Actions based on audit findings
- [ ] Positive impact from recommended actions
- [ ] Metric improvements on focus areas
- [ ] Strategy adjustments made as needed

#### Team Engagement
- [ ] Team understands product health
- [ ] Team aligned on priorities
- [ ] Team motivated by findings
- [ ] Team commitment to improvements

---

## Quarterly Audit Checklist Quick Reference

| Area | Key Questions | Owner | Timeline |
|------|----------------|-------|----------|
| **Metrics** | Are key metrics on track? Growth healthy? | Analytics | Week 1-2 |
| **Customer** | Are customers satisfied? Churn acceptable? | CS | Week 2 |
| **Quality** | Product stable? Bugs under control? | QA | Week 2-3 |
| **UX** | Experience quality good? Accessible? | Design | Week 3 |
| **Strategy** | Executing on plan? Roadmap on track? | PM | Week 3 |
| **Market** | Competitive position strong? Market aware? | PMM | Week 3-4 |
| **Risks** | What could go wrong? Mitigated? | PM | Week 4 |
| **Opportunities** | What's the upside? Prioritized? | PM | Week 4 |
| **Actions** | What to do differently? Planned? | VP Product | Week 4 |

---

## Audit Scheduling & Cadence

**Recommended Schedule**:
- **Quarterly Health Audits**: End of each quarter (Week 1 of next quarter)
- **Mid-Quarter Health Check**: Week 6-7 of quarter (lightweight assessment)
- **Annual Deep Dive**: End of year (comprehensive 5-week audit)

**Notification & Calendar**:
- Schedule audit at end of prior quarter
- Announce 2 weeks in advance
- Block 4 weeks on team calendars
- Ensure leadership availability
- Plan for findings presentation

---

## Common Audit Pitfalls

| Pitfall | Impact | Prevention |
|---------|--------|-----------|
| Incomplete data collection | Biased conclusions | Follow complete checklist |
| Only looking at metrics | Miss qualitative insights | Include customer feedback |
| Confirmation bias | Miss real problems | Seek disconfirming evidence |
| Analysis paralysis | No action taken | Set tight timelines |
| Shallow assessment | Missed insights | Deep dives on key areas |
| No action plan | Findings ignored | Create specific recommendations |
| Executive disconnect | Strategy not aligned | Regular stakeholder briefings |

---

**Version History**
- 1.0 (2025-11-19): Initial comprehensive framework
