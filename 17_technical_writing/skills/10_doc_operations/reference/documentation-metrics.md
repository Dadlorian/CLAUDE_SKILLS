# Documentation Metrics & KPIs

## Overview
Documentation metrics provide quantifiable measures of effectiveness, usage, and business impact. This guide outlines essential KPIs, calculation methods, and industry benchmarks for technical documentation.

---

## 1. Usage Metrics

### 1.1 Page Views & Traffic
**Definition:** Total visits to documentation pages per period.

**Formula:**
```
Monthly Page Views = Σ (Unique Visits to Doc Pages)
Page View Trend = (Current Month Views - Previous Month Views) / Previous Month Views × 100%
```

**Benchmarks:**
- Healthy growth: 10-20% month-over-month
- Mature docs: 50,000+ monthly views
- Early stage: 1,000-5,000 monthly views

**Tools:** Google Analytics, Amplitude, ReadMe Analytics

---

### 1.2 Unique Visitors
**Definition:** Number of distinct users accessing documentation.

**Formula:**
```
Monthly Unique Visitors = Count(Distinct User IDs)
Return Visitor Rate = Returning Visitors / Total Visitors × 100%
```

**Benchmarks:**
- Return visitor rate: 40-60% (healthy engagement)
- New visitor rate: 40-60%
- Typical ratio: 1 returning visitor per 1 new visitor

---

### 1.3 Session Duration
**Definition:** Average time users spend on documentation pages.

**Formula:**
```
Average Session Duration = Total Time on Site / Number of Sessions
Bounce Rate = Single-Page Sessions / Total Sessions × 100%
Page Time = Total Session Duration / Pages Viewed
```

**Benchmarks:**
- Good session duration: 3-5 minutes
- Poor: < 1 minute (indicates unclear content)
- Excellent: > 10 minutes (indicates thorough engagement)
- Acceptable bounce rate: < 50%

---

### 1.4 Documentation Search Usage
**Definition:** Frequency of internal documentation searches.

**Formula:**
```
Search Volume = Total Searches / Month
Average Searches per User = Total Searches / Unique Users
Search to Page View Ratio = Searches / Page Views × 100%
```

**Benchmarks:**
- Search volume: 20-40% of total page views
- Search success rate: 65-75% (users find relevant results)
- Common queries indicate content gaps

---

## 2. Quality Metrics

### 2.1 Documentation Completeness
**Definition:** Percentage of documented features/APIs relative to total available.

**Formula:**
```
Completeness Score = (Documented Features / Total Features) × 100%
Coverage Gap = 100% - Completeness Score
```

**Benchmarks:**
- Minimum: 80% of public APIs documented
- Target: 90-95%
- Excellent: > 95%

**Tracking Method:**
- Maintain feature inventory spreadsheet
- Update quarterly with new features
- Review against product roadmap

---

### 2.2 Content Freshness
**Definition:** Percentage of documentation updated within target periods.

**Formula:**
```
Freshness Score = (Recently Updated Pages / Total Pages) × 100%
Days Since Last Update (per page) = (Today - Last Update Date)
Average Documentation Age = Σ (Days Since Update) / Number of Pages
```

**Benchmarks:**
- Pages updated within 6 months: > 80%
- Core documentation: Updated every 3 months
- API docs: Updated every release
- Tutorials: Updated annually

---

### 2.3 Documentation Accuracy
**Definition:** Percentage of documentation verified against current product.

**Formula:**
```
Accuracy Score = (Verified Correct Pages / Audited Pages) × 100%
Error Density = Number of Errors / Total Pages
```

**Benchmarks:**
- Acceptable accuracy: > 95%
- Target accuracy: > 98%
- Error density: < 0.5 errors per page

**Verification Methods:**
- Quarterly audit cycles
- Developer reviews on changes
- User feedback mechanisms
- Automated testing of code examples

---

### 2.4 Readability Metrics
**Definition:** Content complexity and accessibility measures.

**Formula:**
```
Flesch-Kincaid Grade = 0.39(words/sentences) + 11.8(syllables/words) - 15.59
Average Sentence Length = Total Words / Number of Sentences
Technical Jargon Ratio = Technical Terms / Total Words × 100%
```

**Benchmarks:**
- Grade level: 8-10 (high school level)
- Sentence length: 15-20 words average
- Technical terms explained: 90%+
- Paragraph length: 3-5 sentences

**Tools:**
- Hemingway Editor
- Readability Score
- Grammarly

---

## 3. Engagement Metrics

### 3.1 Click-Through Rate (CTR)
**Definition:** Percentage of users clicking documentation links from external sources.

**Formula:**
```
CTR = (Clicks on Doc Link / Impressions) × 100%
Internal CTR = (Internal Link Clicks / Total Link Impressions) × 100%
```

**Benchmarks:**
- Email newsletter to docs: 5-15%
- In-app help prompts: 10-25%
- Search results: 2-8%

---

### 3.2 Content Useful Rating
**Definition:** User satisfaction with individual pages.

**Formula:**
```
Helpful Rating = (Helpful Ratings / Total Ratings) × 100%
Usefulness Score = (Helpful - Not Helpful) / Total Ratings × 100%
```

**Benchmarks:**
- Healthy content: > 70% marked helpful
- High-quality content: > 80% marked helpful
- Low performers: < 50% marked helpful (candidates for revision)

---

### 3.3 Search Query Success Rate
**Definition:** Percentage of searches yielding relevant results.

**Formula:**
```
Success Rate = (Successful Searches / Total Searches) × 100%
Successful Search = User views result and doesn't return to search
Click Depth = Average page clicks after search
```

**Benchmarks:**
- Success rate: 60-75%
- Click depth: 1.5-2 clicks to answer
- Failed searches: < 25%

---

## 4. Business Impact Metrics

### 4.1 Support Ticket Reduction
**Definition:** Decrease in support tickets attributable to documentation.

**Formula:**
```
Ticket Reduction = (Baseline Tickets - Current Tickets) / Baseline × 100%
Self-Service Rate = Self-Answered Tickets / Total Tickets × 100%
Documentation ROI = (Support Cost Saved - Doc Costs) / Doc Costs × 100%
```

**Benchmarks:**
- Good documentation: 20-30% reduction in support tickets
- Excellent documentation: 30-50% reduction
- Self-service rate: 40-60%
- Support cost per ticket: $50-150 (varies by industry)

**Calculation Example:**
```
Monthly Support Cost: $10,000
Doc Team Cost: $8,000
Ticket Reduction: 25%
Support Savings: $10,000 × 25% = $2,500/month
ROI = ($2,500 - $8,000) / $8,000 = -68.75% (first month)
ROI (year 2): ($30,000 - $96,000) / $96,000 = -68.75% (needs better metrics)
```

---

### 4.2 Time-to-Productivity
**Definition:** Duration for new users to become productive with documentation help.

**Formula:**
```
Average TTP = Σ (Time from Signup to First Action) / Number of Users
Reduction in TTP = (Baseline TTP - Current TTP) / Baseline TTP × 100%
```

**Benchmarks:**
- Without documentation: 2-4 weeks
- With documentation: 3-5 days
- Improvement: 60-75% reduction
- Target: < 1 week for core workflows

---

### 4.3 Product Adoption Rate
**Definition:** Percentage of users adopting documented features.

**Formula:**
```
Feature Adoption = (Users Using Feature / Total Users) × 100%
Adoption Increase = (Current - Baseline) / Baseline × 100%
Documentation Impact = Users Adopting After Doc Release
```

**Benchmarks:**
- Well-documented features: 40-70% adoption
- Undocumented features: 10-20% adoption
- Post-launch improvement: 25-40% increase
- Time to adoption: 2-4 weeks after docs published

---

### 4.4 Customer Satisfaction (CSAT)
**Definition:** User satisfaction with documentation quality.

**Formula:**
```
CSAT Score = (Satisfied Ratings / Total Ratings) × 100%
Satisfied = Ratings 4-5 on 5-point scale
Net Satisfaction = (Promoters - Detractors) / Total × 100%
```

**Benchmarks:**
- Acceptable CSAT: 70-75%
- Good CSAT: 75-85%
- Excellent CSAT: 85-95%
- Enterprise SaaS average: 78%

---

## 5. Efficiency Metrics

### 5.1 Documentation Maintenance Cost
**Definition:** Total resources spent maintaining documentation.

**Formula:**
```
Annual Maintenance Cost = (Salaries + Tools + Infrastructure)
Cost per Page = Annual Cost / Total Pages
Cost per User = Annual Cost / Monthly Active Users
```

**Benchmarks:**
- Cost per page: $200-500/year
- Cost per active user: $0.50-2.00/month
- Typical doc team: 1 writer per 3-5 engineers

---

### 5.2 Documentation Update Frequency
**Definition:** How often documentation is updated.

**Formula:**
```
Update Frequency = Total Updates / Time Period
Pages Updated = Updated Pages / Total Pages × 100%
Update Velocity = Pages Updated per Writer per Month
```

**Benchmarks:**
- High-frequency updates: 2+ times weekly
- Regular cadence: Weekly
- Standard: Bi-weekly
- Update velocity: 5-15 pages per writer monthly

---

### 5.3 Time-to-Publish
**Definition:** Duration from content creation to live documentation.

**Formula:**
```
Average TTP = Σ (Publish Date - Creation Date) / Number of Articles
Median TTP = Middle value of TTP distribution
```

**Benchmarks:**
- Quick turnaround: 1-2 days
- Standard: 3-5 days
- Slow: > 1 week
- Target for bug fixes: < 24 hours

---

## 6. Technical Metrics

### 6.1 Documentation Build/Deploy Time
**Definition:** Time to build and deploy documentation changes.

**Formula:**
```
Build Time = Seconds to compile documentation
Deploy Time = Seconds to push to production
Total Pipeline Time = Build + Deploy + QA
```

**Benchmarks:**
- Build time: < 60 seconds
- Deploy time: < 30 seconds
- Total pipeline: < 2 minutes
- Deployment frequency: Multiple per day

---

### 6.2 Broken Links & 404 Errors
**Definition:** Count of non-functional links and missing pages.

**Formula:**
```
Broken Link Rate = (Broken Links / Total Links) × 100%
404 Error Rate = (404 Page Views / Total Page Views) × 100%
Link Health Score = 100% - Broken Link Rate
```

**Benchmarks:**
- Acceptable: < 1% broken links
- Good: < 0.5% broken links
- Excellent: < 0.1% broken links
- 404 rate: < 1% of traffic

**Tools:**
- Link checker services
- Automated CI/CD checks
- Google Search Console

---

### 6.3 Accessibility Metrics
**Definition:** Documentation compliance with accessibility standards.

**Formula:**
```
WCAG Compliance Score = (Passed Checks / Total Checks) × 100%
Mobile Usability Score = (Mobile-Friendly Pages / Total Pages) × 100%
Loading Performance = Page Load Time (seconds)
```

**Benchmarks:**
- WCAG 2.1 AA compliance: 95%+ pages
- Mobile usability: 95%+ pages
- Page load time: < 2 seconds (90th percentile)
- Core Web Vitals: Good for 90%+ pages

---

## 7. Attribution & Correlation

### 7.1 Documentation Impact on Revenue
**Definition:** Correlation between documentation quality and revenue metrics.

**Formula:**
```
Revenue per User = Total Revenue / Active Users
Documentation Quality Score = Composite of multiple metrics
Correlation Coefficient = Statistical measure of relationship
```

**Methods:**
- Cohort analysis: Compare users before/after doc updates
- A/B testing: Version A (old docs) vs Version B (new docs)
- Regression analysis: Control for other variables
- Time series: Track revenue and doc quality over time

---

### 7.2 Documentation Engagement vs Churn
**Definition:** Relationship between doc usage and customer retention.

**Formula:**
```
Churn Rate = (Customers Lost / Starting Customers) × 100%
Heavy Doc Users Churn = Churn rate for high-usage segment
Light Doc Users Churn = Churn rate for low-usage segment
Churn Reduction = (Light - Heavy) / Light × 100%
```

**Benchmarks:**
- Heavy doc users: 5-15% churn
- Light doc users: 25-40% churn
- Documentation impact: 15-25% churn reduction

---

## 8. Dashboard & Reporting

### 8.1 Recommended KPI Dashboard
Essential metrics for leadership:
1. Monthly unique visitors
2. Average session duration
3. Helpful page rating
4. Support ticket reduction
5. Feature adoption rate
6. CSAT score
7. Content freshness (% updated within 6 months)
8. Documentation completeness

### 8.2 Reporting Frequency
- **Daily:** Uptime, 404 errors, deployment status
- **Weekly:** Traffic, new content, engagement
- **Monthly:** All KPIs, trend analysis, insights
- **Quarterly:** Strategic review, gap analysis, roadmap adjustments

---

## 9. Industry Benchmarks Summary

| Metric | Beginner | Intermediate | Advanced | World-Class |
|--------|----------|--------------|----------|-------------|
| Monthly Views | <10K | 10-50K | 50-200K | >200K |
| Return Visitor Rate | 20-30% | 30-45% | 45-60% | >60% |
| Content Freshness | 40-50% | 60-70% | 80-90% | >95% |
| CSAT Score | 60-70% | 70-80% | 80-90% | >90% |
| Support Reduction | 5-10% | 10-20% | 20-30% | >30% |
| Page Helpful Rating | 50-60% | 60-75% | 75-85% | >85% |

---

## 10. Implementation Guide

**Phase 1 (Month 1-2):** Establish baseline metrics
- Identify current tools and data sources
- Create measurement framework
- Set initial targets

**Phase 2 (Month 3-4):** Automated tracking
- Implement analytics in all pages
- Set up dashboards
- Begin weekly reporting

**Phase 3 (Month 5-6):** Optimization
- Identify improvement opportunities
- A/B test high-impact changes
- Document learnings

**Phase 4 (Ongoing):** Continuous improvement
- Monthly review cycles
- Quarterly strategic analysis
- Annual benchmark updates

---

## References
- Google Analytics Documentation
- Industry reports on technical documentation
- Case studies on doc ROI
- Analytics tools documentation (ReadMe, Amplitude)
