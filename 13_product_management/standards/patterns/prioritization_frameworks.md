# Product Prioritization Frameworks
## Elite Decision-Making for Product Managers

**Version**: 1.0
**Last Updated**: 2025-11-19
**Authority**: Frameworks from Intercom (RICE), Airbnb, Google, Amazon, and leading product organizations

---

## Overview

Product prioritization is the art and science of deciding **what to build next** given constrained resources. Great prioritization balances:
- **Customer value**: What users need most
- **Business impact**: What moves key metrics
- **Strategic alignment**: What advances company vision
- **Feasibility**: What's technically possible within constraints
- **Opportunity cost**: What we're NOT doing

This guide covers battle-tested frameworks used by world-class product teams.

---

## Table of Contents

1. [RICE Scoring](#rice-scoring) ⭐ Most Popular
2. [Value vs Effort Matrix](#value-vs-effort-matrix)
3. [Kano Model](#kano-model)
4. [Weighted Scoring](#weighted-scoring)
5. [Cost of Delay](#cost-of-delay)
6. [MoSCoW Method](#moscow-method)
7. [Story Mapping](#story-mapping)
8. [OKR Alignment](#okr-alignment)
9. [ICE Scoring](#ice-scoring)
10. [Buy a Feature](#buy-a-feature)
11. [Opportunity Scoring](#opportunity-scoring)
12. [Framework Selection Guide](#framework-selection-guide)

---

## RICE Scoring

**Created by**: Intercom
**Best for**: Quantitative prioritization across diverse initiatives
**Time to implement**: 30-60 minutes per scoring session

### Formula

```
RICE Score = (Reach × Impact × Confidence) / Effort
```

### Components

#### Reach
**Definition**: How many people will this affect in a given time period?

**How to estimate**:
- Users per month (if monthly release cycle)
- Users per quarter (if quarterly planning)
- Customers affected (for B2B features)

**Examples**:
- "500 users per month will see this feature"
- "All 10,000 enterprise customers will benefit"
- "20% of our user base (2,000 users) will use this monthly"

**Tips**:
- Be specific about time period (per month, per quarter)
- Use actual data from analytics when possible
- For new features, estimate based on similar features
- For workflow improvements, count how many times workflow happens

---

#### Impact
**Definition**: How much will this impact each person who encounters it?

**Scale**:
- **3 = Massive Impact**: Transformative change, solves major pain point
- **2 = High Impact**: Significant improvement, removes friction
- **1 = Medium Impact**: Moderate improvement, nice to have
- **0.5 = Low Impact**: Small improvement, marginal value
- **0.25 = Minimal Impact**: Tiny improvement, barely noticeable

**How to estimate**:
- Consider: Does this solve a high-frequency, high-severity problem?
- Use customer research: How many users cited this as a pain point?
- Reference satisfaction surveys: How important is this capability?

**Examples**:
- **Massive (3)**: SSO for enterprise customers (security requirement, blocks deals)
- **High (2)**: Bulk actions (saves 30 minutes per week for 40% of users)
- **Medium (1)**: Dark mode (nice to have, improves experience)
- **Low (0.5)**: Subtle UI polish (minor aesthetic improvement)
- **Minimal (0.25)**: Tooltip text update (tiny clarity improvement)

**Common Mistake**: Don't conflate Reach and Impact
- High reach, low impact: Tooltip shown to everyone
- Low reach, high impact: Enterprise admin panel (few users, critical for them)

---

#### Confidence
**Definition**: How confident are you in your Reach and Impact estimates?

**Scale**:
- **100% = High Confidence**: Strong data, validated with customers
- **80% = Medium Confidence**: Some data, reasonable assumptions
- **50% = Low Confidence**: Mostly hypothetical, needs validation

**How to estimate**:
- Have you talked to customers about this? (Higher confidence)
- Do you have usage data supporting estimates? (Higher confidence)
- Is this a new feature with uncertainty? (Lower confidence)
- Have you tested a prototype? (Higher confidence)

**Examples**:
- **100%**: Customer research with 20 interviews, all mentioned this problem
- **80%**: Analytics show 35% of users attempt this workflow and fail
- **50%**: Hypothesis based on competitor features, not validated with our users

**Pro Tip**: Confidence prevents inflated scores on unvalidated ideas

---

#### Effort
**Definition**: How much total time will this require from all team members?

**Units**: Person-months (one person working for one month)

**Include**:
- Product management time (research, specs, launch)
- Design time (exploration, high-fidelity, iteration)
- Engineering time (backend, frontend, testing, deployment)
- QA time
- DevOps/infrastructure setup

**How to estimate**:
- Get estimates from engineering and design leads
- Add 20-30% buffer for unknowns
- Round to half-person-months (0.5, 1, 1.5, 2, etc.)

**Examples**:
- **0.5 person-months**: Simple UI change, backend already exists
- **1 person-month**: New feature with frontend + backend work
- **3 person-months**: Complex feature with integrations, new data models
- **6+ person-months**: Major initiative, consider breaking down

**Common Mistake**: Forgetting non-engineering effort (PM, design, QA adds 30-50%)

---

### Calculating RICE Score

**Example Calculation**:

**Feature**: Bulk CSV import for team members

- **Reach**: 200 team admins per month
- **Impact**: 2 (high - saves significant time)
- **Confidence**: 80% (0.8) - validated in customer interviews
- **Effort**: 2 person-months

```
RICE Score = (200 × 2 × 0.8) / 2
           = 320 / 2
           = 160
```

**Feature**: Dark mode theme

- **Reach**: 5,000 users per month (all users)
- **Impact**: 1 (medium - nice to have)
- **Confidence**: 50% (0.5) - assumption, not validated
- **Effort**: 1.5 person-months

```
RICE Score = (5,000 × 1 × 0.5) / 1.5
           = 2,500 / 1.5
           = 1,667
```

**Result**: Dark mode scores higher (1,667 > 160) despite lower impact, due to much higher reach

---

### RICE Prioritization Workflow

**Step 1: Gather Ideas**
- Collect feature requests from customers, sales, support, team
- Include strategic initiatives from roadmap
- Typical backlog: 20-50 items

**Step 2: Score Collaboratively**
- Schedule 90-minute session with product trio (PM, Design, Eng)
- Use spreadsheet or tool (ProductBoard, Airfocus)
- Score each item:
  1. PM proposes Reach, Impact, Confidence
  2. Engineering proposes Effort
  3. Discuss and agree
  4. Calculate RICE score

**Step 3: Review & Adjust**
- Sort by RICE score (high to low)
- Sanity check: Does this feel right?
- Consider dependencies and sequencing
- Adjust for strategic importance if needed

**Step 4: Communicate**
- Share prioritized list with stakeholders
- Explain methodology and scores
- Be transparent about trade-offs

**Step 5: Revisit**
- Re-score quarterly as new data emerges
- Update Reach/Impact based on learnings
- Adjust Confidence as you validate assumptions

---

### RICE Templates

**Spreadsheet Template**:

| Feature | Reach | Impact | Confidence | Effort | RICE Score | Priority |
|---------|-------|--------|------------|--------|------------|----------|
| Bulk CSV import | 200 | 2 | 80% | 2 | 160 | 3 |
| Dark mode | 5000 | 1 | 50% | 1.5 | 1,667 | 1 |
| SSO integration | 50 | 3 | 100% | 3 | 50 | 5 |
| Mobile app | 3000 | 2 | 70% | 6 | 700 | 2 |

---

### RICE Pros & Cons

**Pros** ✅:
- Quantitative, reduces bias
- Confidence factor prevents inflating unvalidated ideas
- Easy to explain to stakeholders
- Well-known framework, new PMs recognize it
- Compares diverse initiatives on same scale

**Cons** ❌:
- Can feel overly prescriptive
- Debates about exact scores ("Is this a 2 or a 3?")
- Doesn't account for strategic importance explicitly
- Math can give false sense of precision
- Effort estimation is notoriously hard

**When to use**:
- You have many diverse ideas to compare
- You want a systematic, defendable process
- You need to align stakeholders on priorities
- You're starting out with prioritization frameworks

**When NOT to use**:
- Strategic initiatives that must be done regardless of score
- Very early-stage products (too much uncertainty)
- Extremely time-sensitive opportunities (market windows)

---

## Value vs Effort Matrix

**Best for**: Visual prioritization, stakeholder workshops
**Time to implement**: 15-30 minutes

### Framework

Plot initiatives on 2x2 matrix:

```
High Value |  Fill-Ins  |  Quick Wins  |
           |            |              |
           |____________|______________|
           |            |              |
Low Value  | Time Sinks |   Big Bets   |
           |            |              |
           |____________|______________|
           Low Effort     High Effort
```

**Definitions**:

- **Quick Wins** (High Value, Low Effort): Do these first, maximum ROI
- **Big Bets** (High Value, High Effort): Strategic priorities, plan carefully
- **Fill-Ins** (Low Value, Low Effort): Nice to haves, fill gaps in sprint
- **Time Sinks** (Low Value, High Effort): Avoid unless required

---

### How to Use

**Step 1: Define "Value"**
Choose what "value" means for your context:
- Business value (revenue impact)
- Customer value (satisfaction improvement)
- Strategic value (alignment with vision)
- Or composite of multiple dimensions

**Step 2: Define "Effort"**
- Engineering time
- Total team time (eng + design + PM)
- Calendar time to ship

**Step 3: Plot Items**
- Gather team (product trio + stakeholders)
- Use whiteboard or Miro
- Discuss and place each item on matrix
- Relative positioning matters more than exact placement

**Step 4: Prioritize**
1. **Immediate**: Quick Wins
2. **Strategic Planning**: Big Bets (sequence thoughtfully)
3. **Fill Extra Capacity**: Fill-Ins
4. **Avoid/Defer**: Time Sinks

---

### Value vs Effort Workshop Script

**Duration**: 60-90 minutes
**Participants**: Product trio, key stakeholders (5-8 people)

**Agenda**:
1. **Setup (5 min)**: Explain framework, define value and effort
2. **Individual Plotting (10 min)**: Each person plots items on their own matrix
3. **Group Discussion (40 min)**: Discuss each item, find consensus placement
4. **Prioritization (15 min)**: Agree on next steps for each quadrant
5. **Action Planning (10 min)**: Define immediate next actions

**Facilitation Tips**:
- Keep debates time-boxed (5 min max per item)
- Use voting if consensus is hard ("Where should this go? Vote now")
- Capture dissenting opinions ("Noted: Sales team sees this as higher value")
- Focus on relative position, not precise coordinates

---

### Value vs Effort Scoring Variation

Add numerical scores for more precision:

**Value Score (1-10)**:
- 9-10: Critical, transformative
- 7-8: High value, significant impact
- 5-6: Moderate value, nice improvement
- 3-4: Low value, marginal benefit
- 1-2: Minimal value, almost no impact

**Effort Score (1-10)**:
- 9-10: Massive project (6+ person-months)
- 7-8: Large project (3-6 person-months)
- 5-6: Medium project (1-3 person-months)
- 3-4: Small project (0.5-1 person-months)
- 1-2: Tiny change (<0.5 person-months)

**ROI Calculation**:
```
ROI = Value / Effort
```

Sort by ROI to prioritize.

---

### Pros & Cons

**Pros** ✅:
- Simple, visual, intuitive
- Great for workshops (collaborative)
- Easy for non-PMs to understand
- Fast (can prioritize 20 items in 30 min)
- Flexible definitions of value and effort

**Cons** ❌:
- Less rigorous than RICE
- Value can be subjective
- No confidence factor
- Can oversimplify complex trade-offs
- Hard to compare very similar items

**When to use**:
- Stakeholder alignment workshops
- Quick prioritization sessions
- Early-stage product (less data available)
- Visual communication needed

---

## Kano Model

**Created by**: Noriaki Kano (1984)
**Best for**: Understanding which features delight vs satisfy vs are expected
**Time to implement**: 1-2 weeks (includes customer surveys)

### Framework

Kano categorizes features into 5 types based on customer satisfaction response:

```
Satisfaction
     ↑
     |    Delighters (Exciters)
     |         ↗
     | _______________
     |/Performance
     |
_____|______________ Implementation →
     |\___
     |    \
     |     Basic Needs (Must-haves)
     |
```

---

### Feature Categories

#### 1. Basic Needs (Must-Haves)
**Definition**: Expected features. Absence causes dissatisfaction, presence does not increase satisfaction.

**Characteristics**:
- Customers assume you have these
- Missing them makes product unusable or uncompetitive
- Having them is "table stakes"
- No competitive advantage from these

**Examples**:
- **Email app**: Send and receive email
- **E-commerce**: Checkout process
- **SaaS**: Basic security (HTTPS, password protection)
- **Enterprise**: SSO, basic permissions

**Product Strategy**:
- Must have these, but don't over-invest
- Meet baseline expectations efficiently
- Focus engineering excellence on performance, not features

---

#### 2. Performance Needs (Satisfiers)
**Definition**: Linear relationship - more is better. Better implementation increases satisfaction proportionally.

**Characteristics**:
- Customers explicitly request these
- Satisfaction increases with better implementation
- Competitive differentiation possible
- Diminishing returns at some point

**Examples**:
- **Loading speed**: Faster is always better (up to a point)
- **Storage space**: More storage increases satisfaction
- **Search relevance**: Better results = happier users
- **Price**: Lower price (for same value) = higher satisfaction

**Product Strategy**:
- Invest to differentiate from competitors
- Continuously improve (faster, more accurate, more capacity)
- Use as competitive messaging ("10x faster than competitor")
- Measure performance, optimize systematically

---

#### 3. Delighters (Exciters)
**Definition**: Unexpected features that wow users. Absence doesn't cause dissatisfaction, presence creates delight.

**Characteristics**:
- Customers don't expect these
- Create strong positive emotional response
- Powerful differentiators when new
- Become expected over time (→ Performance or Basic)

**Examples**:
- **Gmail (2004)**: 1GB storage when competitors offered 2MB (delighter → became basic need)
- **Uber**: Real-time driver tracking (delighter → now expected)
- **Spotify**: Discover Weekly personalized playlist
- **Notion**: Seamless docs + database hybrid

**Product Strategy**:
- Source of competitive advantage
- Invest in innovation and discovery
- Don't wait for customers to request (they won't - they don't know it's possible)
- Requires continuous innovation (today's delighter = tomorrow's basic need)

**Innovation Approach**:
1. Identify unmet needs customers can't articulate
2. Explore emerging technologies
3. Test bold hypotheses
4. Launch as beta/experiment
5. Measure emotional response (NPS, qualitative feedback)

---

#### 4. Indifferent
**Definition**: Features users don't care about. Presence or absence has no impact on satisfaction.

**Characteristics**:
- Users don't notice or value
- No competitive advantage
- Waste of resources

**Examples**:
- Features built based on one loud customer (not representative)
- Over-designed UI flourishes nobody uses
- Complex features with 1% adoption

**Product Strategy**:
- Avoid building these in the first place
- Validate demand before building (talk to customers!)
- Remove if already built (reduce complexity)
- Learn from these mistakes (how did this get built?)

---

#### 5. Reverse
**Definition**: Features that actually decrease satisfaction for some users.

**Characteristics**:
- Some users actively dislike
- Can increase complexity or noise
- Often "helpful" features that feel intrusive

**Examples**:
- Automatic notifications users can't disable
- Clippy (Microsoft's assistant)
- Auto-play videos with sound
- Over-aggressive onboarding

**Product Strategy**:
- Offer as optional, not default
- Allow users to disable
- Test carefully before widespread rollout
- Listen to negative feedback

---

### Conducting Kano Analysis

#### Step 1: Design Kano Survey

For each feature, ask two questions:

**Functional Question** (feature present):
"How would you feel if [feature] was available?"
- I like it
- I expect it
- I'm neutral
- I can tolerate it
- I dislike it

**Dysfunctional Question** (feature absent):
"How would you feel if [feature] was NOT available?"
- I like it
- I expect it
- I'm neutral
- I can tolerate it
- I dislike it

---

#### Step 2: Classify Responses

Use Kano evaluation table:

|  | Dysfunctional → | Like | Expect | Neutral | Tolerate | Dislike |
|--|----------------|------|--------|---------|----------|---------|
| **Functional ↓** | | | | | | |
| **Like** | | Q | E | E | E | P |
| **Expect** | | R | I | I | I | M |
| **Neutral** | | R | I | I | I | M |
| **Tolerate** | | R | I | I | I | M |
| **Dislike** | | R | R | R | R | Q |

**Key**:
- **M** = Must-have (Basic Need)
- **P** = Performance (Satisfier)
- **E** = Exciter (Delighter)
- **I** = Indifferent
- **R** = Reverse
- **Q** = Questionable (inconsistent response)

---

#### Step 3: Analyze Results

Calculate percentage in each category:
- 40% Must-have
- 30% Performance
- 20% Delighter
- 10% Indifferent

**Categorization**:
- Highest percentage wins
- If tie, use hierarchy: M > P > E > I

**Sample Size**: 50-100 responses for statistical significance

---

#### Step 4: Prioritize

**Priority 1**: Must-haves (missing these causes dissatisfaction)
**Priority 2**: Performance + Delighters
- **Performance**: If you need competitive parity
- **Delighters**: If you need differentiation

**Priority 3**: Indifferent (consider cutting)

---

### Kano Survey Example

**Feature**: Dark mode theme

**Functional**: "How would you feel if our app had a dark mode theme?"
- I like it: 40%
- I expect it: 25%
- I'm neutral: 25%
- I can tolerate it: 5%
- I dislike it: 5%

**Dysfunctional**: "How would you feel if our app did NOT have a dark mode theme?"
- I like it: 2%
- I expect it: 5%
- I'm neutral: 40%
- I can tolerate it: 35%
- I dislike it: 18%

**Analysis**:
Most common pairing: "Like" (functional) + "Neutral/Tolerate" (dysfunctional) = **Performance/Delighter**

**Interpretation**: Dark mode is a Performance feature - some users care a lot, absence is tolerable but presence increases satisfaction.

---

### Kano Over Time

**Important**: Kano categories shift over time

```
Delighter → Performance → Basic Need → Indifferent (if commoditized)
```

**Examples**:
- **2004**: Gmail 1GB storage (Delighter)
- **2010**: Large storage (Performance - more is better)
- **2020**: Large storage (Basic Need - expected)

**Product Implication**:
- Continuous innovation needed
- Yesterday's delighters become today's basics
- Must keep adding new delighters to stay competitive

---

### Kano Pros & Cons

**Pros** ✅:
- Customer-centric (based on surveys, not opinion)
- Identifies features that truly delight
- Prevents wasting time on indifferent features
- Helps distinguish must-haves from nice-to-haves

**Cons** ❌:
- Time-intensive (survey design, distribution, analysis)
- Requires statistically significant sample size
- Users can't always predict future satisfaction accurately
- Survey fatigue if you ask about too many features

**When to use**:
- Deciding between many potential features
- Understanding which features are differentiators
- Planning major product releases
- Validating assumptions about "must-have" features

---

## Weighted Scoring

**Best for**: Custom prioritization with multiple criteria
**Time to implement**: 1-2 hours for framework design, 30 min per scoring session

### Framework

Create custom scoring model based on your specific business priorities.

**Step 1: Define Criteria**

Example criteria:
- Strategic alignment
- Customer value
- Revenue impact
- Technical feasibility
- Time to market
- Competitive advantage
- Risk level

**Step 2: Assign Weights**

Weights should sum to 100%

Example:
| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| Strategic Alignment | 25% | Must advance company vision |
| Customer Value | 25% | Customer-centric company |
| Revenue Impact | 20% | Need to grow ARR |
| Technical Feasibility | 15% | Limited eng resources |
| Time to Market | 10% | Speed matters in our market |
| Competitive Advantage | 5% | Less differentiated market |

**Step 3: Score Each Feature**

Score 1-10 on each criterion, multiply by weight.

**Step 4: Calculate Total Score**

Sum of all weighted scores.

---

### Weighted Scoring Template

| Feature | Strategic (25%) | Customer Value (25%) | Revenue (20%) | Feasibility (15%) | Time (10%) | Competitive (5%) | **Total Score** |
|---------|-----------------|---------------------|---------------|-------------------|-----------|------------------|----------------|
| | Score × 0.25 | Score × 0.25 | Score × 0.20 | Score × 0.15 | Score × 0.10 | Score × 0.05 | |
| SSO Integration | 10 × 0.25 = 2.5 | 8 × 0.25 = 2.0 | 9 × 0.20 = 1.8 | 7 × 0.15 = 1.05 | 6 × 0.10 = 0.6 | 7 × 0.05 = 0.35 | **8.3** |
| Mobile App | 9 × 0.25 = 2.25 | 9 × 0.25 = 2.25 | 7 × 0.20 = 1.4 | 5 × 0.15 = 0.75 | 3 × 0.10 = 0.3 | 8 × 0.05 = 0.4 | **7.35** |
| Dark Mode | 4 × 0.25 = 1.0 | 6 × 0.25 = 1.5 | 3 × 0.20 = 0.6 | 9 × 0.15 = 1.35 | 8 × 0.10 = 0.8 | 5 × 0.05 = 0.25 | **5.5** |

**Result**: SSO Integration (8.3) > Mobile App (7.35) > Dark Mode (5.5)

---

### Scoring Guidelines

**Define clear scoring rubrics** for each criterion:

**Example: Customer Value (1-10)**
- **9-10**: Solves critical problem for majority of users, high frequency/severity
- **7-8**: Solves important problem for significant segment
- **5-6**: Moderate improvement, benefits some users
- **3-4**: Small improvement, benefits few users
- **1-2**: Marginal benefit, unclear value

**Example: Technical Feasibility (1-10)**
- **9-10**: Very easy, low risk, well-understood tech
- **7-8**: Moderate complexity, some unknowns
- **5-6**: Complex, multiple dependencies
- **3-4**: Very complex, significant technical risk
- **1-2**: Extremely difficult, may not be possible

---

### Weighted Scoring Workflow

**1. Design Framework (One-Time)**
- Define 5-8 criteria relevant to your business
- Assign weights through stakeholder discussion
- Create scoring rubrics (1-10 scale definitions)
- Document and share framework

**2. Score Features (Regular)**
- Gather product trio + relevant stakeholders
- For each feature:
  - Discuss each criterion
  - Assign score (use rubric)
  - Calculate weighted score
- Sum to get total score

**3. Prioritize**
- Sort by total score
- Review for sanity ("Does this ranking make sense?")
- Adjust if needed (framework is guide, not rule)

**4. Iterate**
- Revisit weights quarterly
- Adjust criteria as business priorities change
- Refine scoring rubrics based on experience

---

### Weighted Scoring Pros & Cons

**Pros** ✅:
- Highly customizable to your business
- Incorporates multiple important factors
- Transparent and defendable
- Aligns with company priorities
- Works for diverse types of initiatives

**Cons** ❌:
- Time-intensive to set up
- Can feel bureaucratic
- Risk of "gaming" scores
- Debates about weights and scores
- False precision

**When to use**:
- Your business has unique priorities not captured by standard frameworks
- Multiple stakeholder groups with different priorities
- Need highly transparent, audit-able prioritization
- Complex B2B with many considerations

---

## Framework Selection Guide

### Quick Reference

| Framework | Best For | Time Required | Complexity | Output Type |
|-----------|----------|---------------|------------|-------------|
| **RICE** | Quantitative comparison of diverse ideas | 1-2 hours | Medium | Ranked list with scores |
| **Value/Effort** | Visual prioritization, workshops | 30-60 min | Low | 2x2 matrix |
| **Kano** | Understanding customer satisfaction drivers | 1-2 weeks | High | Feature categorization |
| **Weighted Scoring** | Custom multi-criteria prioritization | 2-3 hours | High | Ranked list with scores |
| **Cost of Delay** | Time-sensitive decisions | 1-2 hours | Medium | Ranked by urgency |
| **MoSCoW** | Scope management, release planning | 30 min | Low | Categorized list |
| **OKR Alignment** | Linking features to goals | 1 hour | Medium | Alignment scores |
| **ICE** | Quick prioritization | 15-30 min | Low | Ranked list |

---

### Decision Tree

**Start here**: What's your primary goal?

**Goal: Compare many diverse ideas systematically**
→ Use **RICE Scoring**

**Goal: Quick prioritization for workshop/stakeholder meeting**
→ Use **Value vs Effort Matrix**

**Goal: Understand which features delight vs are expected**
→ Use **Kano Model**

**Goal: Prioritize with unique business criteria**
→ Use **Weighted Scoring**

**Goal: Decide what's in/out of scope for release**
→ Use **MoSCoW**

**Goal: Align features to company OKRs**
→ Use **OKR Alignment Scoring**

**Goal: Make time-sensitive decisions**
→ Use **Cost of Delay / Weighted Shortest Job First**

---

## Best Practices Across All Frameworks

### 1. Collaborate, Don't Dictate
- Involve product trio (PM, Design, Eng) in scoring
- Get stakeholder input where appropriate
- Build consensus through discussion
- Document disagreements and reasoning

### 2. Use Data, Not Opinions
- Base scores on customer research
- Use analytics to validate assumptions
- Reference market data and competitive intel
- Cite sources for estimates

### 3. Be Transparent
- Share methodology with stakeholders
- Explain why each framework was chosen
- Communicate trade-offs openly
- Make scores and rankings visible

### 4. Treat as Guide, Not Gospel
- Frameworks inform decisions, don't make them
- Use judgment to override when needed (with justification)
- Consider strategic exceptions
- Balance quantitative and qualitative inputs

### 5. Revisit Regularly
- Re-score quarterly as you learn
- Update estimates based on new data
- Adjust priorities based on market changes
- Archive old prioritizations for learning

### 6. Define "Done"
- Set clear prioritization cadence (e.g., quarterly)
- Establish decision-making authority (who has final say?)
- Document decisions in decision log
- Communicate outcomes widely

### 7. Keep It Simple
- Don't over-engineer prioritization
- Start with simpler frameworks (Value/Effort, ICE)
- Add rigor as team matures
- Avoid analysis paralysis

---

## Common Mistakes to Avoid

❌ **Mistake 1**: Using framework mechanically without judgment
**Solution**: Framework provides input, PM makes final decision

❌ **Mistake 2**: Scoring in isolation
**Solution**: Score collaboratively with cross-functional team

❌ **Mistake 3**: Never revisiting priorities
**Solution**: Re-score quarterly, update based on learning

❌ **Mistake 4**: Letting loudest voice dominate
**Solution**: Use data and framework to depersonalize debates

❌ **Mistake 5**: Prioritizing only by highest score
**Solution**: Consider dependencies, sequencing, strategic timing

❌ **Mistake 6**: Forgetting opportunity cost
**Solution**: Every "yes" is a "no" to something else - make it explicit

❌ **Mistake 7**: Over-complicating the process
**Solution**: Start simple, add complexity only if needed

---

## Tools & Templates

**Spreadsheet Templates**:
- [Download RICE Template](#)
- [Download Weighted Scoring Template](#)
- [Download Value/Effort Template](#)

**Software Tools**:
- **ProductBoard**: Built-in prioritization frameworks (RICE, custom scoring)
- **Airfocus**: Priority scoring with custom criteria
- **Aha!**: Weighted scoring, value vs effort
- **Jira Product Discovery**: Ideas prioritization
- **Miro/Mural**: Visual prioritization workshops

**Free Resources**:
- Intercom's RICE Prioritization Guide
- ProductPlan's Prioritization Framework Guide
- Mind the Product: Prioritization Best Practices

---

## Summary

**For most teams, we recommend**:
1. **Start with**: Value vs Effort Matrix (simple, fast, collaborative)
2. **Mature to**: RICE Scoring (more rigorous, quantitative)
3. **Add complexity if needed**: Weighted Scoring (custom criteria)
4. **Validate assumptions**: Kano Model (customer satisfaction drivers)

**Remember**:
- The best prioritization framework is the one your team actually uses
- Data beats opinions
- Frameworks guide, judgment decides
- Transparency builds trust
- Iterate and improve your process over time

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Next Review**: 2025-02-19

**Further Reading**:
- "Intercom on Product Management" - RICE framework deep dive
- "Escaping the Build Trap" by Melissa Perri - Outcome-driven prioritization
- "The Lean Product Playbook" by Dan Olsen - Prioritization best practices
