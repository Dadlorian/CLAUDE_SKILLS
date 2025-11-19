# B2B Metrics: Definitions, Formulas, and Benchmarks

## Overview
This guide defines key B2B metrics, provides calculation formulas, and includes industry benchmarks. Use this to build your own B2B metrics dashboard and track business health.

---

## Revenue Metrics

### Annual Contract Value (ACV)

**Definition**: Average annual revenue per customer

**Formula**:
```
ACV = Total Annual Revenue / Number of Customers
```

**Example**:
```
If you have $10M in annual revenue with 500 customers:
ACV = $10,000,000 / 500 = $20,000
```

**Benchmarks**:
- **SMB SaaS**: $500 - $5,000
- **Mid-Market SaaS**: $10,000 - $100,000
- **Enterprise SaaS**: $100,000 - $1,000,000+

**Why It Matters**:
- Determines sales model (self-serve, sales-assisted, enterprise sales)
- Impacts customer acquisition cost (CAC) sustainability
- Influences pricing strategy
- Helps forecast revenue growth

**Improvement Strategies**:
- Increase price (if market allows)
- Add premium features
- Expand into larger customer segments
- Cross-sell complementary products
- Upsell to higher tiers

---

### Total Contract Value (TCV)

**Definition**: Total revenue from a customer contract over its entire term

**Formula**:
```
TCV = Annual Contract Value × Contract Duration (in years)
```

**Example**:
```
A customer signs a 3-year contract at $30,000/year:
TCV = $30,000 × 3 = $90,000
```

**Why It Matters**:
- Shows long-term value of customers
- Important for enterprise sales negotiations
- Affects accounting (revenue recognition)
- Helps understand customer lifetime value

---

### Monthly Recurring Revenue (MRR)

**Definition**: Predictable monthly revenue from all active subscriptions

**Formula**:
```
MRR = Sum of all monthly subscription values
      = Total Annual Revenue / 12
```

**Example**:
```
Annual revenue = $6,000,000
MRR = $6,000,000 / 12 = $500,000
```

**Why It Matters**:
- Key metric for SaaS companies
- Predictable revenue for operations
- Used to forecast growth
- Base metric for calculating other KPIs

---

### Annual Recurring Revenue (ARR)

**Definition**: Total predictable annual revenue from all active subscriptions

**Formula**:
```
ARR = MRR × 12
or
ARR = Sum of all annual contract values
```

**Example**:
```
If MRR = $500,000:
ARR = $500,000 × 12 = $6,000,000
```

**Benchmarks**:
- **Early stage**: $100k - $1M ARR
- **Growth stage**: $1M - $10M ARR
- **Scale stage**: $10M - $100M ARR
- **Enterprise**: $100M+ ARR

---

### Average Revenue Per Account (ARPA)

**Definition**: Average monthly or annual revenue per customer

**Formula**:
```
Monthly ARPA = MRR / Number of Customers
Annual ARPA = ARR / Number of Customers
```

**Example**:
```
MRR = $500,000 with 250 customers
Monthly ARPA = $500,000 / 250 = $2,000
Annual ARPA = $24,000
```

**Why It Matters**:
- Tracks pricing value realization
- Guides packaging strategy
- Identifies upsell opportunities
- Different from ACV if customers at different tiers

---

### Expansion Revenue

**Definition**: New revenue from existing customers (seats, tiers, features)

**Formula**:
```
Expansion Revenue = Revenue from existing customers in period X
                    - Revenue from same customers in period X-1
```

**Example**:
```
Customer A was $5k/month, now $8k/month = $3k expansion
Customer B was $10k/month, now $10k/month = $0 expansion
Expansion Revenue in that month = $3k
```

**Related Metrics**:
- **Expansion Rate**: % of customers expanding each period
- **Net Expansion Revenue**: Expansion revenue minus contraction revenue

**Benchmarks**:
- **Healthy B2B SaaS**: 5-15% monthly expansion rate
- **Top performers**: 20%+ monthly expansion rate

**Why It Matters**:
- Shows if customers find additional value
- Lower cost than acquiring new customers
- Indicates product market fit strength
- Drives NRR above 100%

---

## Growth Metrics

### Net Revenue Retention (NRR)

**Definition**: Revenue growth from existing customers, accounting for churn and expansion

**Formula**:
```
NRR = (Beginning MRR + Expansion Revenue - Churned Revenue)
      / Beginning MRR
```

**Example**:
```
Beginning MRR:      $1,000,000
Expansion Revenue:  $100,000
Churned Revenue:    $50,000
Ending MRR:         $1,050,000

NRR = $1,050,000 / $1,000,000 = 105%
```

**Interpretation**:
- **NRR < 100%**: Losing revenue from existing customers (net negative)
- **NRR = 100%**: Breakeven on existing customers
- **NRR > 100%**: Growing revenue from existing customers (healthy)
- **NRR > 120%**: Exceptional growth from existing customers

**Benchmarks**:
- **Below 100%**: Concerning - churn exceeds expansion
- **100-110%**: Average for B2B SaaS
- **110-130%**: Healthy growth
- **130%+**: Exceptional (top-tier companies)

**Industry Examples**:
- Salesforce: 165%+
- Slack: 130%+
- HubSpot: 120%+
- Average SaaS: 108-115%

**Why It Matters**:
- Shows sustainable growth without new customer acquisition
- Investors highly value NRR > 130%
- Indicates product stickiness
- Determines long-term business viability

**Improvement Strategies**:
- Increase expansion revenue (upsell, cross-sell, add seats)
- Reduce churn (improve customer success, product quality)
- Improve feature adoption
- Create expansion paths for all customer segments

---

### Gross Revenue Retention (GRR)

**Definition**: Revenue retained from existing customers (before accounting for expansion)

**Formula**:
```
GRR = (Beginning MRR - Churned Revenue) / Beginning MRR
```

**Example**:
```
Beginning MRR:  $1,000,000
Churned Revenue: $50,000
Ending MRR:      $950,000 (before expansion)

GRR = $950,000 / $1,000,000 = 95%
```

**Interpretation**:
- Shows baseline customer retention
- NRR = GRR + (Expansion Revenue / Beginning MRR)
- If GRR = 90%, then 10% of customers churned (gross)

**Benchmarks**:
- **Below 90%**: High churn - focus on retention
- **90-95%**: Acceptable baseline
- **95%+**: Strong retention
- **98%+**: Exceptional

**Why It Matters**:
- Separates retention from expansion
- Shows true churn rate for existing customers
- Important for predicting future revenue
- Easier to understand than NRR for some audiences

---

### Net New ARR

**Definition**: Net change in Annual Recurring Revenue (new customers + expansion - churn)

**Formula**:
```
Net New ARR = New Customer ARR + Expansion ARR - Churned ARR
```

**Example**:
```
New customers in quarter:  $500,000
Expansion from existing:   $150,000
Churned in quarter:        ($80,000)
Net New ARR:               $570,000
```

**Benchmarks**:
- Growth depends on company stage and market size
- **Early stage**: 50%+ quarterly growth
- **Growth stage**: 20-40% quarterly growth
- **Mature**: 10-20% quarterly growth

**Why It Matters**:
- Shows overall revenue growth
- Used for forecasting
- Key investor metric
- Easier to understand than NRR for executives

---

### Customer Growth Rate

**Definition**: Percentage growth in customer count

**Formula**:
```
Customer Growth Rate = (Ending Customers - Beginning Customers)
                       / Beginning Customers
```

**Example**:
```
Beginning customers: 500
Ending customers:    600
Growth Rate = (600 - 500) / 500 = 20%
```

**Why It Matters**:
- Shows if sales team is hitting targets
- Different from revenue growth (may add low-ACV customers)
- Impacts support and CS costs

---

## Sales Efficiency Metrics

### Sales Efficiency Ratio (Magic Number)

**Definition**: Revenue generated per dollar spent on sales and marketing

**Formula**:
```
Magic Number = (Current Quarter ARR - Previous Quarter ARR)
               / Sales & Marketing Spend in Previous Quarter
```

**Example**:
```
Q2 ARR:  $5,000,000
Q1 ARR:  $4,800,000
S&M Spend in Q1: $500,000

Magic Number = ($5,000,000 - $4,800,000) / $500,000
             = $200,000 / $500,000
             = 0.4
```

**Interpretation**:
- **< 0.5**: Inefficient - need to cut spend or improve product
- **0.5-0.75**: Below average efficiency
- **0.75-1.0**: Good efficiency
- **1.0+**: Excellent - sustainable scaling

**Benchmarks**:
- **Below 0.5**: Poor sales efficiency
- **0.5-0.75**: Average
- **0.75-1.0**: Good (healthy growth)
- **1.0+**: Exceptional (you can invest more)

**Why It Matters**:
- Shows if you can sustainably scale
- Investors look for > 0.75
- Helps determine S&M budget allocation
- Guides go-to-market efficiency

**Improvement Strategies**:
- Improve product (faster sales cycles)
- Better market fit (fewer prospects, higher close rate)
- Reduce CAC (better targeting, inbound)
- Increase ACV (upsell, larger deals)

---

### Customer Acquisition Cost (CAC)

**Definition**: Cost to acquire one new customer

**Formula**:
```
CAC = Total Sales & Marketing Spend in Period
      / Number of New Customers Acquired in Period
```

**Example**:
```
S&M spend in Q1: $500,000
New customers in Q1: 100
CAC = $500,000 / 100 = $5,000 per customer
```

**Payback Period**:
```
CAC Payback = CAC / Monthly Profit per Customer
Example: $5,000 CAC / $500 profit/month = 10 months
```

**Benchmarks**:
- **SMB SaaS**: $500 - $5,000
- **Mid-Market**: $5,000 - $50,000
- **Enterprise**: $50,000 - $500,000+

**Healthy Payback Period**:
- **SaaS average**: 9-12 months
- **High growth**: < 12 months
- **Mature products**: < 6-9 months

**Why It Matters**:
- Shows unit economics of growth
- Determines sustainability of growth
- Guides pricing strategy (price must cover CAC + profit)
- Helps budget allocation

---

### CAC Payback Period

**Definition**: Months needed to recover customer acquisition cost

**Formula**:
```
CAC Payback = CAC / (Monthly ARPA × Gross Margin %)
```

**Example**:
```
CAC: $5,000
Monthly ARPA: $1,000
Gross Margin: 80%

CAC Payback = $5,000 / ($1,000 × 0.80)
            = $5,000 / $800
            = 6.25 months
```

**Benchmarks**:
- **Below 6 months**: Exceptional
- **6-9 months**: Healthy
- **9-12 months**: Acceptable
- **12+ months**: Consider improving efficiency

---

### Lifetime Value (LTV) to CAC Ratio

**Definition**: Customer lifetime value compared to acquisition cost

**Formula**:
```
LTV = ARPA × (1 / Monthly Churn Rate) × Gross Margin
LTV:CAC Ratio = LTV / CAC
```

**Example**:
```
ARPA: $1,000/month
Monthly Churn: 2%
Gross Margin: 80%
CAC: $5,000

LTV = $1,000 × (1 / 0.02) × 0.80 = $40,000
LTV:CAC = $40,000 / $5,000 = 8:1 ratio
```

**Interpretation**:
- **< 1:1**: Don't acquire (lose money)
- **1:1 - 2:1**: Barely profitable
- **2:1 - 3:1**: Healthy
- **3:1+**: Great unit economics

**Benchmarks**:
- **Minimum viable**: 3:1
- **Healthy**: 5:1
- **Excellent**: 8:1+

**Why It Matters**:
- Shows long-term profitability of customers
- Used to justify S&M spending
- Guides product pricing
- Investors look for 3:1+ ratios

---

### CAC Efficiency Ratio

**Definition**: Revenue generated per dollar of CAC spent

**Formula**:
```
CAC Efficiency = Annual Customer Profit / CAC
                = (ARPA × 12 - Delivery Cost) / CAC
```

**Example**:
```
ARPA: $2,000
Annual revenue per customer: $24,000
Delivery cost/year: $5,000
Net annual profit: $19,000
CAC: $15,000

CAC Efficiency = $19,000 / $15,000 = 1.27
```

---

## Churn and Retention Metrics

### Customer Churn Rate

**Definition**: Percentage of customers lost in a period

**Formula**:
```
Customer Churn Rate = Customers Lost in Period
                     / Beginning Customers in Period
```

**Example**:
```
Beginning customers: 500
Churned customers: 25
Churn Rate = 25 / 500 = 5% (monthly)
```

**Annualized Churn**:
```
Annual = 1 - (1 - Monthly Churn)^12
If monthly churn = 5%:
Annual = 1 - (0.95)^12 = 46% annual churn
```

**Benchmarks**:
- **Monthly churn**:
  - **Below 2%**: Excellent
  - **2-5%**: Healthy
  - **5-10%**: Acceptable
  - **Above 10%**: Concerning
- **Annual churn**:
  - **Below 20%**: Excellent
  - **20-35%**: Healthy
  - **35-50%**: Acceptable
  - **Above 50%**: Needs improvement

**Why It Matters**:
- Directly impacts revenue growth
- Shows product-market fit
- Affects company valuation
- Easier to improve than adding new customers (usually)

**Improvement Strategies**:
- Improve onboarding
- Increase feature adoption
- Better customer success
- Product improvements
- Customer advisory boards

---

### Revenue Churn Rate

**Definition**: Revenue lost from customer cancellations

**Formula**:
```
Revenue Churn = MRR Lost from Cancellations / Beginning MRR
```

**Example**:
```
Beginning MRR: $500,000
MRR churned: $25,000
Revenue Churn = $25,000 / $500,000 = 5%
```

**Benchmarks**:
- **Below 2%**: Excellent
- **2-4%**: Healthy
- **4-7%**: Acceptable
- **Above 7%**: Needs improvement

**Why It Matters**:
- More important than customer churn (accounts for expansion)
- Shows true revenue sustainability
- If NRR < 100%, revenue churn > expansion revenue

---

### Cohort Retention

**Definition**: Retention of customers acquired in the same period

**Formula**:
```
Cohort Retention = (Customers Still Active / Cohort Size) × 100
```

**Example Cohort Analysis**:
```
Month 0 (signup):  100 customers
Month 1:  95 customers retained (95% retention)
Month 3:  85 customers retained (85% retention)
Month 6:  75 customers retained (75% retention)
Month 12: 60 customers retained (60% retention)
```

**Why It Matters**:
- Shows if product gets better/worse over time
- Different cohorts may have different retention
- Helps identify what drives retention
- Can segment by source, ACV, industry, etc.

---

### Customer Health Score

**Definition**: Predictive score of customer churn risk

**Components** (example):
- Login frequency (weight: 25%)
- Feature usage breadth (weight: 25%)
- Support ticket sentiment (weight: 20%)
- Recent expansion activity (weight: 15%)
- NPS or satisfaction score (weight: 15%)

**How to Implement**:
1. Define engagement metrics for your product
2. Weight by correlation to churn
3. Calculate monthly per customer
4. Use to trigger CS interventions
5. Refine based on actual churn

**Use Cases**:
- Identify at-risk customers for proactive outreach
- Prioritize customer success efforts
- Forecast churn for next period
- Analyze what drives retention

---

## Expansion Metrics

### Expansion Revenue Rate

**Definition**: Percentage of customers expanding in a period

**Formula**:
```
Expansion Rate = Customers with Expansion / Total Customers
```

**Example**:
```
Total customers: 500
Customers who expanded: 75
Expansion Rate = 75 / 500 = 15%
```

**Benchmarks**:
- **Below 5%**: Low expansion
- **5-10%**: Moderate
- **10-20%**: Healthy
- **20%+**: Excellent

---

### Seat Expansion

**Definition**: Increase in users/seats for existing customers

**Metrics to Track**:
- Average seats per customer (trend)
- Seats added per expanding customer
- Correlation between seat count and churn
- Department expansion (new departments using product)

**Example**:
```
Q1: Average 15 seats per customer
Q2: Average 18 seats per customer
Expansion = 3 seats, 20% growth
```

---

### Net Dollar Retention (NDR)

**Definition**: Total revenue from existing customers in period, including expansion

**Formula**:
```
NDR = (Beginning Customer Revenue + Expansion - Churn)
      / Beginning Customer Revenue
```

**Why It Matters**:
- Alternative term for NRR
- More commonly used in enterprise SaaS
- Key metric investors look at

---

### Upsell and Cross-Sell Rate

**Definition**: Percentage of customers buying additional products/features

**Formulas**:
```
Upsell Rate = Customers upgraded to higher tier / Total customers
Cross-sell Rate = Customers buying new product / Total customers
```

**Benchmarks**:
- **Healthy**: 5-15% quarterly upsell/cross-sell
- **Exceptional**: 20%+ quarterly

---

## Unit Economics

### Gross Margin

**Definition**: Percentage of revenue remaining after direct product costs

**Formula**:
```
Gross Margin = (Revenue - Cost of Goods Sold) / Revenue
```

**Example**:
```
Revenue: $1,000,000
COGS (hosting, payment fees, support): $200,000
Gross Margin = ($1,000,000 - $200,000) / $1,000,000 = 80%
```

**Benchmarks**:
- **SaaS average**: 70-90%
- **Healthy**: 75%+
- **Excellent**: 85%+

---

### Payback Period

**Definition**: How long to recover CAC from customer

**Formula**:
```
Payback Period = CAC / (Monthly ARPA × Gross Margin %)
```

**Benchmarks**:
- **Below 6 months**: Excellent
- **6-12 months**: Healthy
- **12-18 months**: Acceptable
- **18+ months**: Concerning

---

### Customer Lifetime Value (LTV)

**Definition**: Total profit from a customer over their relationship

**Formula** (simplified):
```
LTV = ARPA × (1 / Churn Rate) × Gross Margin - CAC
```

**More detailed**:
```
LTV = Sum of (Monthly Profit × Month Number × Probability of Retention in Month)
```

**Example**:
```
Monthly ARPA: $1,000
Gross Margin: 80%
Monthly Churn: 2% (average customer lifetime = 50 months)
CAC: $5,000

LTV = $1,000 × (1 / 0.02) × 0.80 - $5,000
    = $1,000 × 50 × 0.80 - $5,000
    = $40,000 - $5,000
    = $35,000
```

---

## Dashboard Template

**Monthly B2B SaaS Dashboard**:
| Metric | Current | Last Month | Target | YoY |
|--------|---------|------------|--------|-----|
| ARR | $5.2M | $5.0M | $6.0M | +25% |
| MRR | $433k | $417k | $500k | +25% |
| NRR | 112% | 110% | 115%+ | — |
| GRR | 97% | 96% | 95%+ | — |
| Customers | 520 | 510 | 600 | +15% |
| ACV | $10k | $9.8k | $10k | +2% |
| Magic Number | 0.85 | 0.72 | 0.75+ | — |
| Customer Churn | 3.5% | 3.8% | <3% | —2% |
| Revenue Churn | 2.1% | 2.3% | <2% | —1% |
| Expansion Rate | 12% | 10% | 15% | +4% |
| CAC | $8k | $8.5k | <$7.5k | —10% |
| CAC Payback | 9.2mo | 10.1mo | <9mo | — |

---

## Using These Metrics

1. **Track monthly** - Build consistent reporting
2. **Segment by** - Customer type, sales channel, cohort, geography
3. **Analyze trends** - Month-over-month, quarter-over-quarter, year-over-year
4. **Benchmark** - Compare to industry standards
5. **Act** - Use insights to drive product, sales, and CS improvements
6. **Communicate** - Share with leadership, board, and team
