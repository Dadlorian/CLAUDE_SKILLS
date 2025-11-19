# DORA Research Summary: DevOps Performance Metrics

**Evidence-based research on high-performing technology organizations**

---

## Overview

The DevOps Research and Assessment (DORA) team, led by Dr. Nicole Forsgren, Jez Humble, and Gene Kim, conducted the largest and longest-running research program on DevOps practices and organizational performance. Their findings, published in the book "Accelerate" and annual State of DevOps reports, provide empirical evidence for what drives software delivery and organizational performance.

**Key Research**: 7+ years, 32,000+ responses from technical professionals worldwide

---

## Four Key Metrics

DORA identified four metrics that are predictive of software delivery performance:

### 1. Deployment Frequency

**Definition**: How often an organization successfully releases to production

**Performance Levels**:
- **Elite**: On-demand (multiple deploys per day)
- **High**: Between once per day and once per week
- **Medium**: Between once per week and once per month
- **Low**: Between once per month and once every six months

**Why it matters**:
- Enables faster feedback loops
- Reduces batch size and risk per deployment
- Allows rapid response to customer needs
- Indicates team confidence in deployment process

**Research findings**:
- Elite performers deploy 973x more frequently than low performers (2019 data)
- Deployment frequency correlates with:
  - Faster time to market
  - Higher customer satisfaction
  - Better employee retention

**How to improve**:
- Implement continuous integration and delivery
- Automate testing and deployment
- Adopt trunk-based development
- Use feature flags for progressive rollout
- Reduce deployment friction (self-service, standardized pipelines)

---

### 2. Lead Time for Changes

**Definition**: Time from code committed to code successfully running in production

**Performance Levels**:
- **Elite**: Less than one hour
- **High**: Between one day and one week
- **Medium**: Between one week and one month
- **Low**: Between one month and six months

**Why it matters**:
- Faster feedback on code changes
- Reduced context switching for developers
- Ability to respond quickly to security issues
- Indicator of process efficiency

**Research findings**:
- Elite performers have 6,570x faster lead times than low performers
- Short lead times enable:
  - Rapid experimentation (A/B testing, MVPs)
  - Quick security patches
  - Competitive advantage through faster feature delivery

**How to improve**:
- Minimize work-in-progress (WIP)
- Implement automated testing throughout the pipeline
- Reduce handoffs between teams
- Optimize code review process
- Parallelize pipeline stages
- Invest in CI/CD infrastructure

---

### 3. Change Failure Rate

**Definition**: Percentage of changes to production that result in degraded service or require remediation

**Performance Levels**:
- **Elite**: 0-15%
- **High**: 16-30%
- **Medium**: 16-30%
- **Low**: 16-30%

**Note**: Research shows that elite and low performers have similar ranges for change failure rate. The difference is in how quickly they recover (MTTR).

**Why it matters**:
- Indicates code quality and testing effectiveness
- Measures impact on user experience
- Reflects team's understanding of production environment
- Drives post-incident learning culture

**Research findings**:
- Change failure rate alone doesn't differentiate elite performers
- What matters is the combination of high deployment frequency with manageable failure rates
- Elite teams maintain quality while deploying more frequently

**How to improve**:
- Comprehensive automated testing (unit, integration, E2E)
- Test in production-like environments
- Implement progressive delivery (canary, blue-green)
- Conduct chaos engineering experiments
- Improve observability to catch issues faster
- Blameless post-mortems drive learning

---

### 4. Time to Restore Service (MTTR)

**Definition**: Time to restore service when a service incident occurs

**Performance Levels**:
- **Elite**: Less than one hour
- **High**: Less than one day
- **Medium**: Between one day and one week
- **Low**: More than one week

**Why it matters**:
- Minimizes user impact during incidents
- Indicates operational maturity
- Enables confidence to deploy more frequently
- Reflects team's understanding of systems

**Research findings**:
- Elite performers recover 2,604x faster than low performers
- Fast recovery enables:
  - Higher deployment frequency (less fear of breaking things)
  - Experimentation and innovation
  - Better customer trust

**How to improve**:
- Comprehensive observability (metrics, logs, traces)
- Automated rollback capabilities
- Clear incident response procedures
- On-call best practices and runbooks
- Chaos engineering to validate recovery procedures
- Blameless post-mortems to prevent recurrence

---

## Performance Clusters

DORA research identifies organizations into performance clusters:

### Elite Performers (2021 Data)

**Deployment Frequency**: Multiple times per day
**Lead Time**: Less than one hour
**Change Failure Rate**: 0-15%
**MTTR**: Less than one hour

**Characteristics**:
- Strong DevOps culture and practices
- Comprehensive automation
- Investment in platform engineering
- Psychological safety and learning culture

**Business outcomes**:
- 50% more likely to exceed profitability, market share, and productivity goals
- 2x more likely to recommend their organization to friends

---

### High Performers

**Deployment Frequency**: Between once per day and once per week
**Lead Time**: Between one day and one week
**Change Failure Rate**: 0-15%
**MTTR**: Less than one day

---

### Medium Performers

**Deployment Frequency**: Between once per week and once per month
**Lead Time**: Between one week and one month
**Change Failure Rate**: 16-30%
**MTTR**: Between one day and one week

---

### Low Performers

**Deployment Frequency**: Between once per month and once every six months
**Lead Time**: Between one month and six months
**Change Failure Rate**: 16-30%
**MTTR**: More than one week

---

## Technical Capabilities That Drive Performance

DORA research identified 24 technical capabilities that predict software delivery performance:

### Continuous Delivery Capabilities

1. **Version Control**: All code, configuration, scripts in version control
2. **Deployment Automation**: Automated deployment to production
3. **Continuous Integration**: Code integrated to trunk daily, automated builds and tests
4. **Trunk-Based Development**: Small batches, short-lived branches (<1 day)
5. **Test Automation**: Comprehensive automated test suite
6. **Test Data Management**: Adequate test data for testing
7. **Shift Left on Security**: Security integrated early in development
8. **Continuous Delivery (CD)**: Software can be deployed to production on-demand

**Impact**: Organizations with strong CD practices are 2x more likely to exceed organizational performance goals

---

### Architecture Capabilities

9. **Loosely Coupled Architecture**: Teams can test and deploy independently
10. **Empowered Teams**: Teams choose tools and make decisions without approval
11. **Service-Oriented Architecture**: Services can be deployed independently

**Impact**: Loosely coupled architectures enable:
- Higher deployment frequency
- Faster lead times
- Lower change failure rates
- Teams can scale independently

---

### Product and Process Capabilities

12. **Customer Feedback**: Actively and regularly seeking customer feedback
13. **Value Stream**: Teams understand and optimize their value stream
14. **Working in Small Batches**: Features decomposed into small deliverable units
15. **Team Experimentation**: Teams have authority to experiment

**Impact**: Organizations that work in small batches and gather feedback see:
- Faster time to market
- Better product-market fit
- Higher customer satisfaction

---

### Lean Management and Monitoring Capabilities

16. **Change Approval Processes**: Lightweight approval process (not CAB)
17. **Monitoring**: Comprehensive observability (metrics, logs, traces)
18. **Proactive Notifications**: Alerting detects and predicts issues
19. **WIP Limits**: Limits on work in progress
20. **Visual Management**: Team performance visible to all

**Impact**: Strong monitoring capabilities enable:
- Faster incident detection and resolution
- Proactive issue prevention
- Data-driven decision making

---

### Cultural Capabilities

21. **Westrum Organizational Culture**: Generative culture (high cooperation, messengers trained, risks shared, innovation encouraged, failures lead to inquiry)
22. **Supporting Learning**: Dedicated time and resources for learning
23. **Collaboration**: Cross-functional collaboration
24. **Job Satisfaction**: Meaningful work, supportive culture

**Impact**: Culture is the #1 predictor of software delivery and organizational performance

---

## Westrum's Organizational Culture Model

**Pathological (Power-oriented)**
- Low cooperation
- Messengers shot
- Responsibilities shirked
- Bridging discouraged
- Failure leads to scapegoating
- Novelty crushed

**Bureaucratic (Rule-oriented)**
- Modest cooperation
- Messengers neglected
- Narrow responsibilities
- Bridging tolerated
- Failure leads to justice
- Novelty leads to problems

**Generative (Performance-oriented)** ← Elite performers are here
- High cooperation
- Messengers trained
- Risks are shared
- Bridging encouraged
- Failure leads to inquiry
- Novelty implemented

**Research findings**:
- Generative culture predicts software delivery performance
- Generative culture predicts organizational performance
- Culture can be measured and improved

---

## Common Anti-Patterns (What NOT to Do)

### 1. Manual Deployments
**Problem**: Slow, error-prone, not repeatable
**Impact**: Low deployment frequency, high change failure rate
**Solution**: Automate deployment pipeline

### 2. Long-Lived Feature Branches
**Problem**: Integration hell, merge conflicts, delayed feedback
**Impact**: High lead time, integration issues
**Solution**: Trunk-based development with feature flags

### 3. Change Advisory Boards (CAB)
**Problem**: Bottleneck, bureaucracy, theater of process
**Impact**: Low deployment frequency, does not reduce change failure rate
**Solution**: Peer review, automated quality gates, progressive delivery

### 4. Hero Culture
**Problem**: Reliance on individuals, knowledge silos, burnout
**Impact**: Not scalable, high attrition, incidents when heroes unavailable
**Solution**: Documentation, automation, shared ownership, blameless culture

### 5. Big Bang Releases
**Problem**: High risk, long testing cycles, difficult rollback
**Impact**: Low deployment frequency, high change failure rate, long MTTR
**Solution**: Small batches, continuous delivery, progressive rollout

---

## How to Measure Your Performance

### Step 1: Establish Baseline
Survey your team or measure from your tools:
- What's your current deployment frequency?
- What's your average lead time?
- What percentage of deployments cause issues?
- How long does it take to recover from incidents?

### Step 2: Identify Your Cluster
Compare your metrics to DORA performance levels:
- Are you elite, high, medium, or low?
- Which metric is your biggest opportunity?

### Step 3: Choose Capabilities to Improve
From the 24 capabilities, identify:
- Which capabilities are you weak in?
- Which would have the biggest impact?
- Which are feasible to improve in the next quarter?

### Step 4: Implement and Measure
- Set improvement goals (e.g., reduce lead time by 50%)
- Implement changes incrementally
- Measure continuously
- Iterate based on results

### Step 5: Share and Learn
- Share metrics with the team
- Celebrate improvements
- Conduct retrospectives on what worked
- Share learnings across the organization

---

## Tools for Measuring DORA Metrics

### CI/CD Platforms
- **GitLab**: Built-in DORA metrics dashboard
- **GitHub Insights**: Deployment frequency, lead time
- **CircleCI Insights**: Pipeline performance metrics
- **Jenkins**: Metrics plugins (Build Monitor, Performance)

### Observability Platforms
- **Datadog**: DORA metrics dashboard
- **New Relic**: Deployment tracking, MTTR
- **Sleuth**: DORA metrics tracking and insights
- **LinearB**: Engineering metrics and analytics

### Incident Management
- **PagerDuty**: MTTR tracking, incident analytics
- **Opsgenie**: Incident response metrics
- **VictorOps**: Time to acknowledge, time to resolve

### Custom Solutions
- Extract from Git (commits, merges, tags)
- Extract from deployment logs (timestamps, outcomes)
- Extract from incident tracking (Jira, ServiceNow)
- Aggregate in dashboards (Grafana, Tableau)

---

## Case Studies

### Google
- Pioneered SRE practices that enable elite performance
- Deploys thousands of times per day across the organization
- Error budgets balance reliability and velocity
- Post-mortems drive continuous learning

### Amazon
- "You build it, you run it" - teams own full lifecycle
- Automated deployment pipelines enable continuous delivery
- Service-oriented architecture enables team autonomy
- Metrics-driven culture

### Netflix
- Deploys production code 4,000+ times per day
- Chaos engineering validates resilience continuously
- Automated canary analysis enables safe, rapid deployments
- Freedom and responsibility culture

### Etsy
- Continuous deployment since 2009
- Deploys 50+ times per day
- Feature flags enable progressive rollout
- ChatOps and observability drive collaboration

---

## Key Takeaways

1. **DORA metrics are predictive**: They correlate with business outcomes (profitability, market share, productivity)

2. **Culture matters most**: Technical practices enable performance, but culture drives adoption and sustainability

3. **There are no trade-offs**: Elite performers deploy more frequently AND have better quality (lower change failure rate)

4. **Small batches enable speed**: Working in small batches reduces risk and enables faster feedback

5. **Automation is critical**: Manual processes don't scale and introduce errors

6. **Continuous improvement**: Elite performers continuously invest in capabilities and measure results

7. **Anyone can improve**: Organizations of any size, in any industry, can achieve elite performance with focus and investment

---

## References

### Books
- **"Accelerate: The Science of Lean Software and DevOps"** (Forsgren, Humble, Kim, 2018)
  - Research methodology and findings
  - 24 technical and cultural capabilities
  - Statistical analysis of performance predictors

- **"The DevOps Handbook"** (Kim, Humble, Debois, Willis, 2016)
  - Practical implementation guidance
  - Case studies from elite performers
  - Three Ways of DevOps

### Annual Reports
- **State of DevOps Report** (DORA/Google Cloud, annual since 2014)
  - Latest research findings
  - Trend analysis over time
  - Performance benchmarks by industry and organization size
  - Available: https://cloud.google.com/devops/state-of-devops

### Academic Papers
- Forsgren, N., Humble, J., & Kim, G. (2018). "Accelerate: Building and scaling high performing technology organizations." IT Revolution Press.
- Forsgren, N., & Kersten, M. (2018). "DevOps metrics." Queue, 16(5), 39-44.
- Forsgren, N., et al. (2021). "The SPACE of Developer Productivity." Queue, 19(1), 20-48.

### Online Resources
- **DORA.dev**: Official DORA research site with tools and resources
- **DORA QuickCheck**: Free assessment tool to benchmark your team
- **Google Cloud DevOps Research**: Blog posts and whitepapers

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Based on**: 7 years of DORA research (2014-2021)
**Data Sources**: 32,000+ survey responses from technical professionals worldwide

---

**Use this research to**:
- Benchmark your team's performance
- Identify improvement opportunities
- Make evidence-based investment decisions
- Drive cultural and technical transformation
- Measure progress over time
