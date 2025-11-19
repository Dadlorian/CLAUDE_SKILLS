# Market Analysis Guide: How to Conduct Market Analysis for Strategy

## Overview

Market analysis is the **foundation** of product strategy. It tells you:
- What's the opportunity size?
- Who's competing and how?
- What are market trends?
- Where can you win?

This guide provides a **step-by-step process** to conduct comprehensive market analysis.

---

## Part 1: Market Sizing

### What is Market Sizing?

Market sizing estimates the **total addressable opportunity** for your product. It typically breaks into:

```
TAM (Total Addressable Market)
 │
 ├─ All potential customers globally
 │
 ├─ SAM (Serviceable Addressable Market)
 │  │
 │  └─ Market you can realistically reach (geography, language, sales channel)
 │
 └─ SOM (Serviceable Obtainable Market)
    │
    └─ Market share you can achieve in 5 years
```

### Market Sizing Approach 1: Top-Down

**Method:** Start with industry data and work backward

**Steps:**

1. **Find total addressable market from research firms**
   ```
   Research sources:
   - Gartner reports
   - IDC market research
   - Forrester
   - CB Insights
   - Industry-specific analyst firms
   - Company annual reports

   Example: "Project Management Software market projected at $12B globally in 2025"
   ```

2. **Calculate your addressable market**
   ```
   Start: $12B market
   Filter by:
   - Geography (if US-focused): $5B (40% of global)
   - Customer size (if SMB-focused): $2B (40% of US)
   - Use case (if product-team focused): $600M (30% of SMB)

   Your SAM: ~$600M
   ```

3. **Estimate market share (SOM)**
   ```
   Realistic 5-year share: 5-10%
   SOM: $30-60M revenue opportunity
   ```

**Pros:**
- Quick (1-2 days)
- Uses professional data
- Shows upside to investors

**Cons:**
- Analyst estimates often inflated
- Doesn't validate if you can actually penetrate market
- Assumes you can reach entire market

**Best for:** Initial investor pitch, high-level planning

---

### Market Sizing Approach 2: Bottom-Up

**Method:** Build from actual unit economics

**Steps:**

1. **Define target customer**
   ```
   Example: Mid-market SaaS companies (50-500 people)
   ```

2. **Estimate addressable customers**
   ```
   Total mid-market SaaS companies: 50,000 globally
   That use project management: 40,000
   That would switch for your solution: 20,000 (50% willing to switch)

   Market size estimate: 20,000 potential customers
   ```

3. **Estimate average revenue per customer**
   ```
   Based on customer interviews + research:
   - Small accounts (50 people): $500/month
   - Mid accounts (200 people): $2,000/month
   - Large accounts (500 people): $5,000/month

   Average: $2,000/month = $24,000 annual
   ```

4. **Calculate total opportunity**
   ```
   20,000 customers × $24,000 = $480M TAM
   Realistic penetration (5 years): 5% = $24M SOM
   ```

**Pros:**
- Based on actual customer economics
- More defensible for investors
- Realistic about what you can achieve

**Cons:**
- Time-consuming (requires research)
- Limited by available customer data
- May miss new use cases/customers

**Best for:** Detailed business planning, justifying resource investment

---

### Market Sizing Approach 3: Value-Based

**Method:** Estimate based on value you create

**Steps:**

1. **Estimate customer's current cost**
   ```
   Problem: Time spent on manual coordination
   - Hours per month: 40 hours
   - Hourly cost (loaded): $150
   - Monthly cost: 40 × $150 = $6,000
   ```

2. **Estimate value your solution creates**
   ```
   Time saved: 30%
   Value created: $6,000 × 30% = $1,800/month

   Could you price at: 30-50% of value = $540-900/month
   ```

3. **Estimate max customers willing to pay this price**
   ```
   From research: 20% of mid-market SaaS willing to adopt
   = 8,000 customers potential
   ```

4. **Calculate opportunity**
   ```
   8,000 × $720/month × 12 = $69M opportunity
   ```

**Pros:**
- Grounded in value creation
- Informs pricing
- Strong for sales conversations

**Cons:**
- Requires detailed customer value research
- Hard to predict adoption
- May overestimate willingness to pay

**Best for:** Pricing strategy, detailed business cases

---

### Market Sizing Template

**For your business:**

```
MARKET SIZING TEMPLATE

Approach 1: Top-Down
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total addressable market (TAM):
- Starting market: $[X]B (source: [analyst firm])
- Geographic filter: [X%] = $[X]B
- Vertical filter: [X%] = $[X]B
- Company size filter: [X%] = $[X]M

Serviceable addressable market (SAM): $[X]M

Serviceable obtainable market (SOM):
- 5-year market share: [X%]
- 5-year revenue opportunity: $[X]M

Approach 2: Bottom-Up
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Target customers:
- Global addressable: [X] companies
- Willing to switch: [X]% = [X] companies
- Realistic penetration (5 years): [X]% = [X] customers

Average revenue per customer:
- Small: $[X]/year
- Mid: $[X]/year
- Enterprise: $[X]/year
- Weighted average: $[X]/year

Market opportunity:
- [X] customers × $[X]/year = $[X]M

Approach 3: Value-Based
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Customer's current problem cost: $[X]/year
Your solution's value: [X]% improvement = $[X]

Willingness to pay: $[X]/month = $[X]/year
Max customers at this price: [X]

Market opportunity: $[X]M

FINAL ESTIMATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conservative: $[X]M (bottom-up -20%)
Realistic: $[X]M (average of approaches)
Optimistic: $[X]M (top-down -20%)
```

---

## Part 2: Competitive Analysis

### Step 1: Identify Your Competitive Set

**Categorize competitors:**

```
1. DIRECT COMPETITORS
   Products solving the same problem in the same way
   Example for Slack: Hipchat, Rocket.Chat, Mattermost

2. INDIRECT COMPETITORS
   Products solving the same customer need differently
   Example for Slack: Email, Microsoft Teams, Discord

3. SUBSTITUTES
   Non-product solutions
   Example for Slack: Face-to-face meetings, phone calls

4. ADJACENT COMPETITORS
   Companies that could enter your market
   Example for Slack: Microsoft (via Teams), Google (could launch)

5. NON-CONSUMERS
   Customers solving problem by doing nothing
   Example for Slack: Small companies continuing with email
```

**Create competitive set:**

```
Direct (threat level: HIGH)
- Competitor A: [description]
- Competitor B: [description]

Indirect (threat level: MEDIUM)
- Competitor A: [description]

Substitutes (threat level: LOW-MEDIUM)
- Email
- Meetings

Should monitor:
- Microsoft Teams (could focus on SMB market)
- Discord (gaming could move to work)
```

---

### Step 2: Map Competitive Dimensions

**What dimensions do customers care about?**

```
For Communication Platform:

Feature Dimensions:
- Search capability
- Integration ecosystem
- Mobile experience
- Threading/organization
- Customization
- Security/compliance

Business Dimensions:
- Price
- Implementation time
- Support quality
- Vertical specialization

Company Dimensions:
- Market position
- Financial stability
- Vision/roadmap
- Company culture fit
```

---

### Step 3: Create Competitive Matrix

**Score each competitor on key dimensions**

```
COMPETITIVE MATRIX

Dimension         Weight   Slack   Teams   Hipchat   Us (Launch)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search            20%      9       5       7         8
Integrations      15%      10      8       6         7
Mobile            15%      8       9       7         9
Price             20%      4       8       9         8
Ease of use       15%      8       7       7         9
Support           15%      7       8       6         9

Weighted Score            8.0     7.4     7.1       8.4
```

**Insights:**
- You're strongest in: Ease of use, Support, Price
- Slack strongest: Integrations, Mobile, Brand
- Differentiation: Make ease of use and support your advantages

---

### Step 4: Competitive Positioning Statement

**For each major competitor, define:**

```
COMPETITIVE POSITIONING

SLACK
Position: The market leader in team communication
Strengths: Integrations, network effects, brand, mobile
Weaknesses: Expensive, cluttered UX, limited organization
Strategy: Maintain leadership through integrations + culture fit
Threat: If they improve UI, hard to compete

MICROSOFT TEAMS
Position: The bundled alternative (Office 365 bundle)
Strengths: Existing Office install base, enterprise relationships
Weaknesses: Poor UX compared to Slack, weak ecosystem
Strategy: Win companies that don't want Slack tax
Threat: Improving rapidly, unlimited resources

OUR STRATEGY
Differentiation: Superior UX for SMB, with built-in knowledge management
Positioning: "Slack's simplicity with Teams' knowledge management"
Win Against: Both - focus on ease of use + knowledge capture
Avoid: Enterprise-only play (too strong), price war (can't win)
```

---

## Part 3: Market Trends & Dynamics

### Research Market Trends

**Sources:**
```
1. Analyst reports (Gartner, Forrester, IDC)
2. Industry publications (VentureBeat, TechCrunch, industry-specific)
3. Customer surveys (Gartner Magic Quadrant shows trends)
4. Patent filings (shows company R&D direction)
5. Product launches (what are leaders building?)
6. Job postings (what skills are companies hiring?)
7. Conference trends (what are people talking about?)
```

### Analyze Macro Trends Affecting Your Market

**Template:**

```
MACRO TRENDS

Trend: Shift to remote work
Impact: Increased need for communication/collaboration tools
Opportunity: Products that enhance distributed team experience
Timeline: Already happening, accelerating

Trend: Consolidation of work tools (platforms vs best-of-breed)
Impact: Integrated solutions gaining share vs point solutions
Opportunity: Build integration/ecosystem strategy
Threat: Slack could bundle knowledge management
Timeline: 2-3 years

Trend: AI/ML becoming table stakes
Impact: Features without AI losing perceived value
Opportunity: Add AI copilot to differentiate
Threat: Everyone adding AI, becomes commodity
Timeline: Already happening

Trend: Data privacy/security concerns
Impact: Customers demanding self-hosted/encrypted options
Opportunity: Offer on-prem option, emphasize security
Threat: Regulatory changes could require capabilities we don't have
Timeline: Accelerating, regulations may arrive in 2-3 years
```

### Create Market Opportunity Map

**Assess: TAM Growth + Competitive Intensity**

```
                High TAM Growth
                      ↑
                      |
        EMERGING      |      GROWTH
        (Invest)      |      (Compete)
                      |
        ──────────────┼───────────── → Low
     High Intensity   |      High Intensity
        (Avoid)       |      (Crowded)
                      |
                      | MATURE
                      | (Optimize)
                      ↓
                Low TAM Growth
```

**Plot your market:**
```
Our market (SMB communication):
- TAM growth: +20% annually (growth phase)
- Competitive intensity: Medium-high (Slack, Teams, niche players)
- Assessment: Growth market with strong competitor. Win through differentiation.

Adjacent market (enterprise knowledge management):
- TAM growth: +15% annually
- Competitive intensity: Very high (Confluence, Notion, Monday.com)
- Assessment: Crowded market, no strong position unless unique angle
```

---

## Part 4: Customer & Market Segmentation

### Define Market Segments

**Segment by:**

```
1. COMPANY SIZE
   - Startup (1-20 people)
   - SMB (20-500 people)
   - Mid-market (500-5,000 people)
   - Enterprise (5,000+ people)

2. INDUSTRY VERTICAL
   - Software/Tech
   - Financial Services
   - Healthcare
   - Manufacturing
   - Etc.

3. GEOGRAPHIC MARKET
   - US
   - Europe
   - APAC
   - Emerging markets

4. CUSTOMER MATURITY
   - Early adopters (want cutting edge)
   - Mainstream (want proven)
   - Late adopters (want simplicity)

5. USE CASE/JOB
   - Product team coordination
   - Remote work
   - Client collaboration
   - Knowledge management
```

### Assess Each Segment

```
SEGMENT ASSESSMENT

SMB Product Teams
├─ Size: 40,000 addressable companies
├─ Growth: +15% annually
├─ Competitive intensity: HIGH (Slack, Monday.com, Asana)
├─ Willingness to pay: $50-150/month
├─ Switching cost: LOW (try easy to adopt)
├─ Our strength: Ease of use, great support
├─ Our weakness: Limited enterprise features
└─ Strategy: WIN THIS - strong match

Enterprise Product Teams
├─ Size: 5,000 addressable companies
├─ Growth: +8% annually
├─ Competitive intensity: VERY HIGH
├─ Willingness to pay: $1,000+/month
├─ Switching cost: VERY HIGH (hard to move)
├─ Our strength: Technical foundation for scale
├─ Our weakness: No enterprise relationships
└─ Strategy: AVOID INITIALLY - too hard to crack

Distributed Teams (non-product)
├─ Size: 100,000+ addressable
├─ Growth: +25% annually (work-from-home boom)
├─ Competitive intensity: MEDIUM (Slack, Teams, Discord, Gather)
├─ Willingness to pay: $30-100/month (more price sensitive)
├─ Switching cost: LOW
├─ Our strength: Great UX, mobile-first
├─ Our weakness: Limited vertical context
└─ Strategy: EXPLORE - secondary market after SMB
```

---

## Part 5: Strategic Recommendations

### Market Opportunity Summary

**Template:**

```
MARKET ANALYSIS SUMMARY

Market Overview:
- TAM: $[X]M (conservative), $[X]M (realistic)
- Growth rate: [X]% annually
- Stage: Mature / Growth / Emerging

Primary Opportunity:
- Segment: SMB software teams
- Size: $[X]M addressable
- Growth: [X]% annually
- Competitive intensity: [Low/Medium/High]
- Why we can win: [specific competitive advantages]

Secondary Opportunity:
- Segment: [...]
- Size: $[X]M addressable
- When to enter: [timeline]

Competitive Landscape:
- Leader: [Company] with [X]% market share
- Challengers: [List 2-3]
- Niche players: [List opportunities]
- Most credible threat: [Company] because [reason]

Key Market Trends:
1. [Trend]: Impact is [positive/negative]. We should [action].
2. [Trend]: Impact is [positive/negative]. We should [action].
3. [Trend]: Impact is [positive/negative]. We should [action].

Strategic Recommendations:
1. Focus on [segment] because [clear reasons]
2. Differentiate on [dimensions] where we're strong
3. Avoid competing with [competitor] on [dimensions]
4. Monitor [trend/competitor] closely because [risk/opportunity]
5. Plan to enter [adjacent market] in [timeline]
```

---

## Market Analysis Tools

### Research Platforms

1. **Analyst Reports:**
   - Gartner (comprehensive, expensive)
   - Forrester (strategy focused)
   - IDC (market sizing)

2. **Competitive Intelligence:**
   - CB Insights (funding, company data)
   - Crunchbase (company data, funding)
   - PitchBook (investment data)
   - G2/Capterra (customer reviews)
   - ProductHunt (product launches)

3. **Market Data:**
   - US Census Bureau (demographic data)
   - Bureau of Labor Statistics (employment data)
   - Company earnings reports (market data)
   - LinkedIn (hiring trends, company growth)

4. **Customer Research:**
   - Surveys (SurveySparrow, Typeform)
   - Interview panels (UserTesting, Respondent)
   - Focus groups (local or remote)

---

## Common Pitfalls in Market Analysis

### Pitfall 1: Inflated TAM

**Problem:** Using analyst firm's total market, not your addressable market

```
Bad:
- "Project management is a $50B market" (everything globally)
- Therefore: We'll capture 2% = $1B

Reality:
- You can only reach SMB market = $2B
- Realistically can get 5% = $100M
```

**Solution:** Be conservative. Show TAM, SAM, and SOM separately.

---

### Pitfall 2: Ignoring Competitive Response

**Problem:** Assuming your analysis of opportunity stays true when competitors respond

```
Bad analysis:
- "Market growing 30% annually"
- "No one else focused on this segment"
- "We'll grow 40% and capture 5% of market"

Reality:
- 2 large competitors notice growth
- Enter segment with better resources
- Market growth continues but your share drops to 2%
```

**Solution:** Plan for competitive response. How will leader react? How will you respond?

---

### Pitfall 3: Assuming Perfect Execution

**Problem:** Market analysis assumes you execute perfectly

```
Bad:
- "We can reach $10M revenue in 3 years"
- (Assumes: perfect sales, product always works, marketing works, team is perfect)

Reality:
- Execution is messy
- Sales takes longer than expected
- Product bugs hurt adoption
```

**Solution:** Add risk factors. Conservative estimate: -30% from base case.

---

### Pitfall 4: Missing Non-Consumption

**Problem:** Only analyzing existing customers of competitors, not problems people solve by doing nothing

```
Bad:
- "Project management market is $10B"
- "These 50,000 companies are our addressable market"

Missing:
- 100,000 companies using email and spreadsheets instead
- Have same problem but don't think they can solve it
- Might be larger addressable market than existing tool users
```

**Solution:** Interview people NOT using your category. Why? What would convert them?

---

## Checklist: Is Your Market Analysis Complete?

```
□ Market sizing done (TAM, SAM, SOM)
□ Competitive set identified (direct, indirect, substitutes)
□ Competitors analyzed on key dimensions
□ Competitive positioning clear (where you win/lose)
□ Market trends identified (3-5 key trends)
□ Macro forces analyzed (regulatory, economic, social)
□ Customer segments defined (at least 3)
□ Primary segment identified
□ Growth rate verified
□ Competitive intensity assessed
□ Differentiation justified
□ Risks identified
□ Market analysis shared and challenged internally
□ Updated annually (market moves fast)
```

---

## Market Analysis Timeline

**For new market:** 4-6 weeks
**For existing market refresh:** 2 weeks
**Quick assessment:** 3-4 days

---

## Next Steps

Once market analysis is complete, use insights to:
1. Refine product vision (adjusted for market realities)
2. Set strategic goals (based on SAM/SOM)
3. Create roadmap (priorities based on trends)
4. Set OKRs (goals aligned to market opportunity)

---

*Market analysis is not a one-time exercise. Revisit quarterly to catch market shifts early.*
