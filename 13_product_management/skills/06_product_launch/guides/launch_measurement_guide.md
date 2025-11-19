# Launch Measurement & Success Guide

## Measuring and Tracking Launch Success

This guide walks you through measuring launch success, interpreting results, and using data to drive post-launch optimization. Use alongside launch_planning_guide.md and launch_plan_template.md.

---

## Setting Up for Measurement Success

### Step 1: Define Success Metrics BEFORE Launch

**Critical**: Define metrics during Week 2-3 of planning, not after launch.

**Why upfront?**
- Ensures measurement infrastructure is built
- Aligns teams on what success looks like
- Prevents measurement bias (cherry-picking favorable metrics)
- Enables data collection from day 1

### Step 2: Establish Baseline Metrics

**Pre-launch baseline** (4 weeks before launch):
- Current user growth rate (natural, without launch)
- Current feature adoption rates (for comparison)
- Current NPS/CSAT scores
- Current churn/retention rates
- Current revenue/expansion rates

**Comparison**: Compare launch cohort to pre-launch baseline to isolate launch impact.

### Step 3: Set Up Measurement Infrastructure

**Before Launch Day**:
- [ ] Analytics platform configured (Google Analytics, Amplitude, Mixpanel)
- [ ] Event tracking implemented (all key events)
- [ ] Dashboards created and tested
- [ ] Team has access to dashboards
- [ ] Data flowing correctly (verify with test events)

**After Launch**:
- [ ] Real-time monitoring during first 24 hours
- [ ] Daily metric reviews during week 1
- [ ] Weekly reviews during weeks 2-8

---

## Key Success Metrics Framework

### Tier 1: Primary Success Metrics

These are your 3-5 most important metrics that directly indicate launch success.

#### 1. Adoption Rate

**Definition**: % of eligible target audience who try/use the new feature or product

```markdown
## Adoption Metrics

### Day 1 Adoption
- # of users who activated feature on launch day
- % of active users who tried feature on day 1
- Target: 5-15% of active users (depending on visibility)

### Week 1 Adoption
- Cumulative % of users who tried feature
- Daily adoption rate trend (should be growing)
- Target: 15-40% of active users (depending on tier)

### Week 4 Adoption
- Cumulative % ever tried
- % trying for first time (new users adopting vs. existing)
- Target: 30-60% of active users (for Tier 2 feature)

### Week 8+ Adoption
- Final adoption saturation point
- Compare to goals (did we hit target?)

## Adoption Calculation
Adoption Rate = (# of users who tried feature) / (# of eligible users) × 100

## Healthy Adoption Trajectories
- Day 1: 5-10% adoption (hype and early adopters)
- Day 2-7: 20-35% adoption (word of mouth, gradual)
- Week 2-4: 35-50% adoption (peak interest period)
- Week 4-8: 45-65% adoption (long tail adoption)
- Week 8+: Flattening (saturation point)
```

#### 2. Engagement / Retention

**Definition**: % of users who continue using feature after initial trial

```markdown
## Retention Metrics

### Day 1 Retention (Next Day Retention)
- % of day 1 adopters who use feature on day 2
- Typically 20-40% for new features
- Low retention indicates usability or value issues

### Day 7 Retention
- % of day 1 adopters still using feature by day 7
- Typically 40-60% for good features
- Indicates baseline appeal of feature

### Day 30 Retention
- % of day 1 adopters using in week 4
- Typically 30-50% for well-designed features
- Indicates long-term stickiness

### Weekly Active Rate
- % of week 1 adopters active in week 2, 3, 4, etc.
- Should be gradually declining (expected) but not dropping off
- Shows if feature becomes habit-forming

## Healthy Retention Curves
- Linear decline: Steady falloff, expected pattern
- Cliff drop: Usability issue, needs investigation
- Plateau: Feature found its core audience
- Increasing: Very rare, indicates network effects or improving product

## Retention Calculation
Day N Retention = (# of users active on day N who were active on day 1) / (# of users active on day 1) × 100
```

#### 3. Awareness / Reach

**Definition**: % of target audience who became aware of the launch

```markdown
## Awareness Metrics

### Unaided Awareness (Day 1-7)
- Did customers hear about launch unprompted?
- Survey question: "What new features have you heard about recently?"
- Target: 30-50% of target audience aware within first week

### Aided Awareness (Day 1-7)
- Are customers aware of launch when prompted?
- Survey question: "Are you aware of [Feature]?"
- Target: 50-75% of target audience aware within first week

### Reach by Channel
- Blog: Total page views + unique visitors
- Email: # sent, open rate, click rate
- Social: Impressions, reach, engagement
- Press: # of articles, impressions (using media measurement tools)
- Paid ads: Impressions, clicks, reach

### Awareness Metrics for Tier 1 Launches
- Press mentions (# of articles)
- Social media impressions
- Website traffic increase
- Email reach and engagement
- Market perception (analyst reports)

## Awareness Calculation
Awareness Rate = (# of people aware) / (# of target audience) × 100

## Awareness Targets
- Tier 1: 40-60% awareness within 2 weeks
- Tier 2: 30-40% awareness within 2 weeks
- Tier 3: 15-25% awareness (internal focus)
```

#### 4. Customer Sentiment / NPS

**Definition**: Customer satisfaction and likelihood to recommend

```markdown
## Sentiment Metrics

### Net Promoter Score (NPS)
- Scale 0-10: How likely to recommend?
- 0-6: Detractors (dissatisfied)
- 7-8: Passives (satisfied but not enthusiastic)
- 9-10: Promoters (enthusiastic, likely to recommend)
- NPS = % Promoters - % Detractors

### NPS Target by Stage
- Week 1: 20-40 NPS from early adopters
- Week 2: 30-50 NPS as broader group tries
- Week 4: 40-60 NPS as feature stabilizes
- Week 8: 50+ NPS indicates healthy launch

### Other Sentiment Metrics
- **CSAT**: Customer satisfaction on 1-5 scale
  - Target: 4+ average
- **CES**: Customer effort score
  - Target: "Easy" rating for >60% of users
- **Sentiment Analysis**: Monitoring social mentions and reviews
  - Target: 70%+ positive mentions

### Qualitative Feedback
- Customer quotes and testimonials
- Themes in support tickets
- Community discussions (Reddit, forums)
- User interviews (10-15 post-launch)

## Sentiment Collection Methods
- In-app surveys (at key moments)
- Email surveys (1-2 per week)
- Post-support chat surveys
- Customer interviews
- Social listening tools
- Review sites (G2, Capterra, etc.)
```

#### 5. Business Impact

**Definition**: Impact on key business metrics

```markdown
## Business Metrics

### Revenue Impact (if applicable)
- **New Revenue**: Revenue from new customers/signups
- **Expansion Revenue**: Upsells from existing customers
- **Total Revenue Impact**: Combined new + expansion
- Target: Should align with pre-launch projections

### Retention Impact
- **Churn Reduction**: Do adopters churn less?
- **Expansion Likelihood**: Do adopters expand more?
- **LTV Impact**: Increased customer lifetime value
- Target: 5-15% churn reduction if feature aimed at retention

### Growth Impact (on North Star metric)
- **Increase in Key Metric**: Messages sent, files stored, hours spent, etc.
- **% Increase**: Typically 2-10% depending on launch importance
- **Trend**: Should see increase day 1 and sustain or grow

### Operational Impact
- **Support Costs**: Increase in support volume
- **Training Costs**: Onboarding time needed
- **Opportunity Cost**: Engineering/team effort expended
- Return on Investment = Business Impact / Total Costs

## Business Metric Calculation
Revenue Impact = (Customers acquired - Usual growth) × ACV
Retention Impact = (Churn reduction %) × (# of customers) × (LTV)
```

### Tier 2: Secondary Success Metrics

These provide deeper insight and guide iteration.

```markdown
## Secondary Metrics Framework

### Product Quality Metrics
- **Error Rate**: % of users experiencing issues/bugs
- **Performance**: Page load time, latency
- **Accessibility**: # of accessibility issues vs. WCAG standards
- **Feature Completeness**: Features working as designed (%)

### User Acquisition Metrics (Tier 1/2 launches)
- **Conversion Rate**: % of visitors → signups
  - Target: 5-15% depending on industry
- **Cost Per Acquisition (CAC)**: Total launch cost / new customers
  - Target: Should be <3x LTV (lifetime value)
- **Traffic Quality**: % of visitors from target segment

### Engagement Metrics
- **Feature Discovery**: % trying advanced features
- **Feature Depth**: Average features per user
- **Time to Value**: Time from signup to first value realization
- **Time Spent**: Average session duration

### User Experience Metrics
- **Onboarding Completion**: % completing setup/tutorial
- **Support Tickets**: Volume and types of issues
- **Feature Discoverability**: % finding key features without guidance

### Competitive Metrics (if applicable)
- **Win Rate**: % of sales deals won vs. competitor
- **Feature Comparison**: Direct comparison on key features
- **Customer Perception**: How customers perceive vs. competitors
```

---

## Measurement Timeline & Cadence

### Day 1: Launch Day Monitoring

**Real-time Monitoring** (every 30-60 minutes):
- Website uptime and performance
- Error rates and critical issues
- Adoption rate (cumulative users trying feature)
- Support tickets and sentiment

**6am, 12pm, 6pm Standups** (30 min each):
- Review key metrics from past 6 hours
- Address any critical issues
- Share momentum updates
- Prepare for next phase

**Dashboard**: Real-time dashboard showing:
- Visitors and traffic
- Signups/activations
- Key events
- Error rates
- Support volume and sentiment

### Days 2-7: Daily Monitoring

**Daily Metric Review** (9am):
- Previous day's adoption (new adopters)
- Retention of day 1 cohort
- Traffic and conversion trends
- Support issues and themes
- Customer feedback highlights

**Daily Standups** (15 min):
- Share key metrics and trends
- Address any issues
- Plan daily marketing/comms
- Monitor sentiment and reputation

**Dashboard**: Add to real-time dashboard:
- Adoption rate (cumulative)
- Adoption rate by segment
- Retention curves by day
- Top support issues
- Social sentiment

### Week 1-2: Weekly Review

**Weekly Metrics Review Meeting** (1 hour, every Monday):

**Metrics Covered**:
- Adoption rate and daily trend
- Retention (Day 1, Day 7, repeat rate)
- Awareness (reach, impressions, traffic)
- Sentiment (NPS, CSAT, social sentiment)
- Business impact (revenue, churn, retention)
- Technical health (errors, performance)
- Support volume and key issues
- Customer feedback themes

**Discussion Points**:
- Are we on track to hit goals?
- What's working well (amplify)?
- What's underperforming (investigate)?
- Changes needed for week 2 (marketing, product, support)?
- Customer wins and stories to share

**Outcome**: Action items, adjustments for week 2

### Weeks 2-4: Weekly Review

**Weekly Review** (same cadence as week 1-2, shorter duration):
- Key metrics progress
- New trends or patterns
- Customer feedback synthesis
- Product improvements made
- Customer success stories
- Plan for week ahead

**Focus Shifts**:
- Less real-time monitoring, more trend analysis
- More customer interview and research
- Product iteration based on feedback
- Expansion opportunities
- Marketing optimization

### Weeks 4-8: Monthly Review

**Month 1 Retrospective** (2 hours):
- Did we hit launch goals?
- Key metrics vs. targets
- What went well (to repeat)
- What didn't work (to avoid)
- Customer feedback summary
- Product roadmap impact
- Business impact summary
- Learnings for future launches

**Focus**:
- Medium-term trends and patterns
- Cohort analysis (launch cohort vs. historical)
- Retention and churn patterns
- Expansion and upsell opportunities
- Long-term business impact

---

## Interpreting Results & Taking Action

### Healthy Launch Indicators

**All Metrics on Target**:
```markdown
## Green Light Scenario
- Adoption: On track or exceeding (15-30% by day 7)
- Retention: Good or better (40%+ day 7 retention)
- Awareness: On track (30-50% aware)
- Sentiment: Positive (45+ NPS)
- Technical: Healthy (no critical issues)
- Support: Manageable volume

**Action**: Execute well-planned marketing acceleration, expand to new segments
```

**Most Metrics Strong, One Weak**:
```markdown
## Yellow Light Scenario: Low Adoption, Strong Retention
- Adoption: Below target (10% by day 7, target 20%)
- Retention: Strong (50%+ day 7 retention, target 40%)
- Sentiment: Positive (50+ NPS)

**Interpretation**: Feature is good, but awareness/discovery is low
**Action**:
- Increase marketing/PR investment
- Improve feature visibility (in-app promotion)
- Adjust messaging to highlight value
- Expand to new segments
- Do NOT change the product (it's working for users who try it)
```

**Adoption Strong, Retention Weak**:
```markdown
## Yellow Light Scenario: Good Adoption, Low Retention
- Adoption: Strong (30% by day 7, target 20%)
- Retention: Weak (20% day 7 retention, target 40%)
- Sentiment: Mixed (25 NPS, target 45+)

**Interpretation**: People are trying, but not sticking - possible UX or value issue
**Action**:
- Conduct user interviews to understand drop-off
- Analyze feature usage patterns (what do users try? where do they drop?)
- Check for bugs or performance issues
- Simplify onboarding or add guidance
- Iterate product based on feedback
- Do NOT increase marketing until retention improves
```

### Problematic Launch Indicators

**Red Light Scenarios**:

```markdown
## Critical Issues Requiring Immediate Action

### Technical Issues
- **Symptom**: High error rate, outages, major bugs
- **Action**:
  - Deploy hotfix immediately
  - Consider rollback if blocking use
  - Disable feature if necessary
  - Over-communicate with customers
  - Extended customer support

### Adoption Failure (Very Low Adoption)
- **Symptom**: <5% adoption after 3-5 days despite visibility
- **Action**:
  - Investigate why - user interviews
  - Check for discoverability issues
  - Verify feature works as expected
  - Possible user positioning mismatch
  - Consider extending beta for refinement

### Retention Cliff (High Drop-off)
- **Symptom**: >50% drop in engagement after day 1
- **Action**:
  - Critical usability or value issue
  - Immediate user research (5-10 interviews)
  - Analyze where users drop off
  - Possible missing critical feature
  - Major iteration needed

### Negative Sentiment
- **Symptom**: Predominantly negative comments, low NPS (<20)
- **Action**:
  - Understand specific complaints
  - Determine if isolation or systemic
  - Address concerns publicly
  - Engage customers to understand issues
  - Iterate based on feedback

### Support Overload
- **Symptom**: Support queue backs up significantly
- **Action**:
  - Add temporary support resources
  - Improve documentation/FAQs
  - Identify common issues and fix
  - Communicate known issues
  - Iterate to reduce need for support
```

---

## Cohort Analysis & Comparison

### Launch Cohort vs. Historical Comparison

```markdown
## Cohort Analysis Framework

### Retention Curve Comparison

**Historical Cohorts** (weeks before launch):
- Day 1: 100% (baseline)
- Day 7: 45% (normal week 1 retention)
- Day 30: 32% (normal month 1 retention)

**Launch Cohort** (week of launch):
- Day 1: 100% (baseline)
- Day 7: 48% (compare to 45% historical)
- Day 30: 35% (compare to 32% historical)

**Interpretation**:
- +3% day 7 retention = Feature has retention benefit
- +3% day 30 retention = Feature has long-term value
- If launch cohort > historical, feature is working
- If launch cohort < historical, feature has issues or cannibalization

### Feature Adoption by Segment

Compare adoption across:
- **New vs. Existing Customers**
  - New users: More likely to try everything
  - Existing users: Trying because feature solves their problem
- **By Company Size**
  - SMBs vs. Mid-market vs. Enterprise
  - Which segments find most value?
- **By Use Case/Industry**
  - Which use cases are driving adoption?
  - Which segments underperforming?
- **By Geography**
  - Localized launch vs. global
  - Which regions adopting fastest?

### Power User Analysis

```markdown
## Power User Engagement

### Identifying Power Users
- Top 10-20% of users by engagement
- Using feature 5+ times/week
- Using advanced features
- High satisfaction (9-10 NPS)

### Power User Behavior
- How do they use feature differently?
- What workflows do they've created?
- What advanced features do they need?
- Are they likely to be references/advocates?

### Learnings from Power Users
- What makes feature compelling (replicate)
- What use cases are most valuable (expand)
- What improvements would increase power users (iterate)
- Who should be customer references (identify advocates)
```

---

## Customer Research & Qualitative Data

### Post-Launch Customer Interviews

**Interview Recruitment** (target 10-15 interviews):
- Mix of adopters (heavy users, moderate users)
- Mix of non-adopters (tried once, haven't tried)
- Mix of segments (size, industry, use case)
- Mix of sentiment (promoters, neutrals, critics)

**Interview Structure** (30-45 minutes):

```markdown
## Post-Launch Interview Guide

### Context (5 min)
1. What's your role and primary responsibility?
2. What problems are you trying to solve with [Category]?

### Experience with Launch (15-20 min)
3. When did you first hear about [Feature]?
4. What was your first impression?
5. How did you get started?
6. What's your experience been so far?
7. What surprised you (positive or negative)?
8. What would make this more valuable for you?

### Impact & Comparison (5 min)
9. Has [Feature] changed how you work?
10. How does this compare to [Alternative you were using]?

### Recommendation (5 min)
11. Would you recommend this to a colleague?
12. What would need to change for you to definitely recommend it?
13. Who else should we talk to?

### Closing
14. Anything else I should know?
```

**Interview Analysis**:
- Transcribe or detailed notes within 24 hours
- Extract key quotes and insights
- Identify common themes across interviews
- Note unique/outlier perspectives
- Synthesize into actionable findings

### Customer Feedback Themes

**Organizing Feedback**:

```markdown
## Feedback Synthesis Template

### Theme 1: Easy to Get Started (Positive)
- Frequency: 7 of 10 users mentioned
- Quote: "I was up and running in 5 minutes"
- Action: Keep this strength, highlight in marketing

### Theme 2: Confusion About Feature X
- Frequency: 5 of 10 users struggled
- Quote: "I wasn't sure what this button did"
- Action: Add tooltip/help text, improve UX

### Theme 3: Missing Integration with Tool Y
- Frequency: 4 of 10 users requested
- Quote: "If it integrated with [Tool], it would save us hours"
- Action: Add to roadmap, prioritize integration

### Theme 4: Great Customer Support
- Frequency: 6 of 10 users mentioned
- Quote: "Support team was super helpful"
- Action: Continue excellent support, use as testimonial

### Theme 5: Pricing Concern
- Frequency: 2 of 10 users mentioned (both enterprise)
- Quote: "Price is steep for our use case"
- Action: Consider per-user vs. seat-based pricing, discuss with sales

## Prioritizing Actions
- Themes affecting majority (7-10): High priority to address
- Themes affecting some (4-6): Medium priority
- Themes affecting few (1-3): Lower priority, unless critical
```

---

## Creating Your Measurement Dashboard

### Essential Dashboard Elements

**Real-Time Metrics** (Day 1-7):
- Website traffic and conversion
- Feature adoption (daily adopters)
- Support ticket volume and sentiment
- Error rates and critical issues
- Social media mentions and sentiment

**Trend Metrics** (Weeks 1-8):
- Cumulative adoption rate
- Retention curves by day
- Weekly active rate
- NPS trend
- Customer feedback themes
- Revenue impact (if applicable)

**Comparison Metrics**:
- Launch cohort vs. historical cohorts
- Adoption by segment
- Retention by segment
- Business impact vs. goals

### Dashboard Tools

**Option 1: Google Data Studio** (free)
- Connect Google Analytics, Google Sheets
- Build visualizations and reports
- Share with stakeholders
- Good for quick dashboards

**Option 2: Tableau** (paid)
- More powerful visualizations
- Connect multiple data sources
- Real-time updates
- Better for complex data

**Option 3: Amplitude/Mixpanel** (product analytics)
- Built-in dashboards
- Event-based analysis
- Cohort analysis
- Segment analysis

**Option 4: Custom Dashboard** (Looker, Power BI)
- Ultimate flexibility
- Connect any data source
- Customized for your needs
- Requires technical setup

### Dashboard Access & Sharing

**Real-Time Dashboards**:
- Available to launch team at all times
- Updated every hour during day 1-7
- Refreshed daily during weeks 2-8

**Weekly Metrics Reports**:
- Email to leadership + launch team
- Include key metrics, trends, insights
- Include context and interpretation
- Include action items for coming week
- Keep to 1-2 pages, details available on request

**Public Dashboards** (if appropriate):
- Transparent with team on progress
- Can motivate teams, celebrate wins
- Be careful with negative stories (provide context)

---

## Post-Launch Measurement Activities

### Week 2 Iteration

**Using Data to Guide Iteration**:
- Which features are most used (double down)
- Which features are unused (investigate or remove)
- Where are drop-offs in funnel (optimize)
- What are top customer requests (prioritize)
- What are top issues/bugs (fix)

**Shipping Improvements** (should see in week 2):
- Bug fixes for top issues
- UX improvements based on usage patterns
- Onboarding improvements for low converters
- Performance optimizations
- New features based on top requests

### Weeks 2-4 Customer Success

**Proactive Outreach**:
- Contact non-adopters (why didn't you try?)
- Contact weak adopters (can we help?)
- Contact power users (would you be a reference?)

**Gathering Success Stories**:
- Identify customers with strong outcomes
- Conduct deep-dive interviews (30-45 min)
- Document quantifiable impact
- Get permission for case study and testimonial

**Customer Reference Program**:
- Identify 5-10 customers willing to speak with prospects
- Provide talking points
- Brief them before sales calls
- Thank them and provide benefits (discount, extended trial, etc.)

### Weeks 4-8 Data Analysis

**Cohort Analysis Deep Dive**:
- Compare launch cohort retention to historical baseline
- Segment by customer characteristics
- Identify which segments benefit most
- Plan segment-specific marketing

**Financial Analysis**:
- Calculate ROI of launch
- Total cost of launch (marketing, product, support)
- Revenue generated from launch
- Long-term revenue impact (based on cohort LTV)
- Cost per acquisition vs. target

**Roadmap Impact**:
- What features should we build next?
- What customer needs are unmet?
- What's the competitive opportunity?
- Create roadmap for next phase

---

## Post-Launch Retrospective (Week 8)

### Retrospective Meeting Structure

**Participants**: Launch team, leadership, cross-functional stakeholders (2 hours)

**Agenda**:

```markdown
## Launch Retrospective Agenda

### Part 1: Results & Metrics (30 min)
- Review actual metrics vs. goals
- Celebrate wins and exceeding goals
- Acknowledge underperformance areas
- Provide context for misses

### Part 2: What Went Well (25 min)
- Team accomplishments and effort
- Successful tactics and strategies
- Team dynamics and collaboration
- Processes that should be repeated
- Individual contributions

### Part 3: What Could Be Better (25 min)
- Bottlenecks and delays
- Communication gaps
- Resource constraints
- Process improvements
- Technical challenges

### Part 4: Learnings & Recommendations (25 min)
- Top 3-5 learnings for future launches
- Process improvements to document
- Resource/timeline recommendations
- Success factors to replicate
- Risks to mitigate in future

### Part 5: Celebration & Close (15 min)
- Thank the team
- Share wins internally
- Plan next steps
- Close with reflection
```

### Retrospective Outputs

**Document Learning**:
- Written summary of retrospective (2-3 pages)
- Key insights and learnings
- Recommendations for future launches
- Lessons captured in launch playbook

**Update Playbooks**:
- Launch checklist - what worked/didn't
- Timeline - realistic based on actual experience
- Resource allocation - correct over/under-allocation
- Decision-making process - what could be faster

**Share Broadly**:
- Share retrospective with broader organization
- Celebrate team and wins
- Build institutional knowledge
- Improve execution across the company

---

## Quick Reference: Success Metrics by Launch Tier

### Tier 1 Launch Success Criteria

```markdown
## Tier 1 Success Metrics

### Adoption
- 30%+ of target audience aware within 2 weeks
- 15%+ of active users adopt feature within 7 days
- 40%+ adoption within 4 weeks

### Retention
- 40%+ Day 7 retention of day 1 cohort
- 30%+ Day 30 retention of day 1 cohort

### Sentiment
- 45+ NPS from launch users
- 80%+ positive mentions (social/review)
- Less than 5% critical issues post-launch

### Business Impact
- Positive revenue impact (based on projections)
- 10%+ growth in North Star metric
- Positive ROI on launch investment

### Support
- Support team handles volume without burnout
- No more than 2% critical bug reports
```

### Tier 2 Launch Success Criteria

```markdown
## Tier 2 Success Metrics

### Adoption
- 25%+ of eligible users aware
- 20%+ adoption by day 7
- 35%+ adoption by week 4

### Retention
- 50%+ day 7 retention
- 40%+ day 30 retention

### Sentiment
- 40+ NPS
- Positive customer feedback predominant
- No critical issues

### Business Impact
- 5%+ impact on related business metrics
- Positive expansion opportunity

### Support
- Support handles volume adequately
- <2% critical bugs
```

### Tier 3 Launch Success Criteria

```markdown
## Tier 3 Success Metrics

### Adoption
- 40%+ adoption by week 2
- Available to all users by week 1

### Retention
- No significant churn from update
- Usage continues at baseline or improves

### Support
- Zero critical issues
- <1% support complaints
```

---

## Measurement Checklist

Use this checklist to ensure you're measuring your launch comprehensively:

**Pre-Launch**:
- [ ] Defined success metrics (primary and secondary)
- [ ] Established baseline metrics (pre-launch)
- [ ] Set up analytics and tracking
- [ ] Created measurement dashboard
- [ ] Assigned data analysis owner
- [ ] Briefed team on metrics and goals
- [ ] Prepared customer survey template

**Launch Day-Week 1**:
- [ ] Real-time monitoring during launch
- [ ] Daily metrics review
- [ ] Daily sentiment monitoring
- [ ] Support issue tracking
- [ ] Technical health monitoring
- [ ] Customer feedback collection
- [ ] Weekly metrics review meeting

**Weeks 2-4**:
- [ ] Weekly metrics review (ongoing)
- [ ] Conduct customer interviews (5-10)
- [ ] Cohort analysis comparing to baseline
- [ ] Product improvements based on feedback
- [ ] Customer success story documentation
- [ ] Iteration planning and execution
- [ ] Competitive monitoring

**Weeks 4-8**:
- [ ] Monthly metrics review
- [ ] Deeper cohort and segment analysis
- [ ] Financial analysis (ROI)
- [ ] Customer interviews (additional 5-10)
- [ ] Product roadmap updates
- [ ] Retrospective planning

**Retrospective**:
- [ ] Schedule retrospective meeting
- [ ] Prepare retrospective slides/document
- [ ] Conduct retrospective
- [ ] Document learnings
- [ ] Update playbooks and processes
- [ ] Share results with team and leadership
- [ ] Plan next steps

---

## Summary

Successful launch measurement requires:

1. **Upfront Planning**: Define metrics before launch
2. **Real-Time Monitoring**: Track metrics daily during launch week
3. **Rapid Analysis**: Interpret data quickly, take action
4. **Customer Feedback**: Combine quantitative and qualitative data
5. **Regular Reporting**: Weekly updates to leadership and team
6. **Actionable Insights**: Use data to guide iteration and improvement
7. **Honest Assessment**: Acknowledge what's working and what isn't
8. **Learning Capture**: Document insights for future launches

Done well, measurement drives both better launches and continuous product improvement.
