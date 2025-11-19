# Risk Profiling and Investor Suitability

## Risk Profiling Importance

Risk profiling is foundational to robo-advisory platforms, determining appropriate allocations, client suitability, and regulatory compliance. Poor profiling leads to unsuitable allocations and dissatisfied clients.

## Risk Tolerance Components

### 1. Financial Risk Capacity

**Definition**: Objective ability to take on risk based on financial circumstances.

**Key Metrics**:
- **Time Horizon**: How long until funds needed
  - Long (10+ years): Can tolerate volatility
  - Medium (5-10 years): Moderate tolerance
  - Short (<5 years): Limited tolerance

- **Income Stability**: Job security and income predictability
  - Stable income: Can tolerate volatility
  - Variable income: Limited tolerance

- **Liquidity Needs**: Expected cash withdrawals
  - Minimal withdrawals: Higher risk capacity
  - Significant withdrawals: Need stability

- **Financial Obligations**: Debts and expenses
  - Low obligations: Higher risk capacity
  - High obligations: Limited capacity

**Calculation Example**:
```
Financial Risk Capacity Score:
Time Horizon (10 years): 30 points
Stable Income: 25 points
Minimal Withdrawals: 25 points
Low Debt: 20 points
Total Capacity: 100 points (high)
```

### 2. Risk Tolerance (Psychological)

**Definition**: Investor's psychological comfort with volatility and losses.

**Components**:
- **Loss Aversion**: How much discomfort investor feels from losses
- **Volatility Tolerance**: Comfort with price fluctuations
- **Control Preference**: Desire to actively manage portfolio
- **Knowledge Level**: Understanding of investments and markets

**Assessment Methods**:
- Questionnaires asking about hypothetical losses
- Historical loss scenario testing
- Decision-making under uncertainty
- Comfort with volatility magnitude

**Risk Tolerance Categories**:

| Category | Loss Tolerance | Expected Volatility | Typical Allocation |
|----------|----------------|---------------------|-------------------|
| Very Conservative | ≤2% annual | ≤5% annual | 20% stocks, 80% bonds |
| Conservative | 2-5% annual | 5-10% annual | 30-40% stocks |
| Moderate | 5-10% annual | 10-15% annual | 50-60% stocks |
| Moderately Aggressive | 10-15% annual | 15-20% annual | 70-80% stocks |
| Aggressive | >15% annual | >20% annual | 90%+ stocks |

### 3. Risk Perception

**Definition**: Investor's belief about risk vs actual risk.

**Challenges**:
- **Overconfidence**: Underestimating personal risk
- **Recency Bias**: Overweighting recent events
- **Loss Aversion**: Fear of losses exceeds appetite for gains
- **Hindsight Bias**: Believing past events were predictable

**Mitigation**:
- Educate about market history and volatility
- Show historical loss scenarios
- Discuss sequence of returns risk
- Establish realistic expectations

## Questionnaire Design

### Risk Tolerance Questionnaire Framework

**Question 1: Time Horizon**
```
How soon do you need the money from this investment?
a) Less than 3 years (0 points)
b) 3-5 years (1 point)
c) 5-10 years (2 points)
d) 10-15 years (3 points)
e) More than 15 years (4 points)
```

**Question 2: Income Stability**
```
How stable is your employment/income?
a) Unstable/variable (0 points)
b) Somewhat stable (1 point)
c) Stable (2 points)
d) Very stable (3 points)
```

**Question 3: Financial Obligations**
```
What percentage of assets are needed for upcoming expenses?
a) More than 30% (0 points)
b) 20-30% (1 point)
c) 10-20% (2 points)
d) Less than 10% (3 points)
```

**Question 4: Loss Tolerance Scenario**
```
If your $100,000 investment dropped to $80,000 in a market downturn, you would:
a) Sell immediately to prevent further loss (0 points)
b) Consider selling if losses continue (1 point)
c) Stay invested and rebalance (2 points)
d) Buy more at the lower price (3 points)
```

**Question 5: Volatility Comfort**
```
How much annual price fluctuation would concern you?
a) Any decline is concerning (0 points)
b) Up to 10% decline (1 point)
c) Up to 20% decline (2 points)
d) Up to 30% decline or more (3 points)
```

**Question 6: Knowledge Level**
```
How would you rate your investment knowledge?
a) Minimal (0 points)
b) Basic (1 point)
c) Intermediate (2 points)
d) Advanced (3 points)
```

**Question 7: Past Experience**
```
Have you invested in stocks before?
a) No, never (0 points)
b) Yes, but experienced significant losses (1 point)
c) Yes, with mixed results (2 points)
d) Yes, and stayed through downturns (3 points)
```

**Question 8: Goal Priority**
```
Which is more important?
a) Preserving capital/steady income (0 points)
b) Steady growth with some risk (1-2 points)
c) Maximum growth accepting volatility (3 points)
```

### Scoring and Interpretation

**Total Score Calculation**:
```
Sum all question points
Divide by maximum possible points
Multiply by 100 for percentage
```

**Risk Profile Categories**:
- 0-20: Very Conservative (Conservative Investor)
- 20-40: Conservative
- 40-60: Moderate
- 60-80: Moderately Aggressive
- 80-100: Aggressive

## Model Portfolios by Risk Profile

### Conservative Portfolio (Risk Score: 20-30)

**Asset Allocation**:
- 25% US Equities
  - 15% Large-Cap (VTI)
  - 10% Dividend stocks (SCHD)
- 20% International Equities (VEA)
- 50% Fixed Income
  - 30% Investment-grade bonds (BND)
  - 15% Short-term bonds (SHV)
  - 5% TIPS (VTIP)
- 5% Cash/Money Market

**Expected Metrics**:
- Average Annual Return: 4-5%
- Annual Volatility: 5-7%
- Maximum Expected Drawdown: 8-12%
- Suitable For: Retirees, near-retirees

### Moderate Portfolio (Risk Score: 40-60)

**Asset Allocation**:
- 55% Equities
  - 35% US stocks (VTI)
  - 20% International (VEA)
- 35% Fixed Income
  - 20% Investment-grade bonds (BND)
  - 10% TIPS
  - 5% High-yield bonds (HYG)
- 5% Real Estate (VNQ)
- 5% Cash

**Expected Metrics**:
- Average Annual Return: 6-7%
- Annual Volatility: 10-12%
- Maximum Expected Drawdown: 15-20%
- Suitable For: Mid-career professionals

### Aggressive Portfolio (Risk Score: 70-90)

**Asset Allocation**:
- 80% Equities
  - 45% US stocks (VTI)
  - 20% International (VXUS)
  - 10% Value factor (VTV)
  - 5% Growth factor (VUG)
- 10% Fixed Income (BND)
- 5% Real Estate (VNQ)
- 5% Commodities (DBC)

**Expected Metrics**:
- Average Annual Return: 8-9%
- Annual Volatility: 15-18%
- Maximum Expected Drawdown: 30-40%
- Suitable For: Young investors, long time horizon

## Behavioral Factors in Risk Assessment

### Overconfidence Bias
- Investors overestimate return potential
- Underestimate risk and volatility
- **Mitigation**: Show historical returns and volatility
- **Strategy**: Use conservative return assumptions

### Loss Aversion
- Fear of losses exceeds desire for equivalent gains
- May cause overly conservative allocation
- **Mitigation**: Explain portfolio diversification benefits
- **Strategy**: Show historical recovery patterns

### Recency Bias
- Recent market performance influences expectations
- Overweight current conditions
- **Mitigation**: Show long-term historical averages
- **Strategy**: Education on market cycles

### Status Quo Bias
- Reluctance to change allocation
- Stickiness to current portfolio
- **Mitigation**: Show rebalancing benefits
- **Strategy**: Regular review and education

## Ongoing Risk Assessment

### Rebalancing and Risk Drift

**Risk Drift Calculation**:
```
Current Portfolio Risk = √(σp² of current allocation)
Target Portfolio Risk = √(σp² of target allocation)
Risk Drift = |Current - Target| / Target
Rebalance if: Risk Drift > 20%
```

**Example**:
- Target: 60% stocks, 40% bonds (risk = 12%)
- Current: 75% stocks, 25% bonds (risk = 15%)
- Risk Drift: |15-12|/12 = 25% > 20%
- Action: Rebalance back to target

### Life Event Adjustments

**Triggers for Risk Profile Review**:
- Major income change
- Job loss or change
- Inheritance or significant windfall
- Approaching retirement
- Health changes affecting work capacity
- Family situation changes
- Market crashes affecting psychology

### Annual Review Process

1. **Reassess Time Horizon**: Have circumstances changed?
2. **Review Financial Capacity**: Income and obligations updated?
3. **Evaluate Psychological Comfort**: Is allocation still suitable?
4. **Discuss Market Outlook**: Inform but don't change allocation
5. **Rebalance if Necessary**: Back to target allocation
6. **Document Changes**: Record any allocation modifications

## Regulatory Compliance

### Suitability Standard
- Investment recommendations must be suitable for investor
- Documentation of understanding and authorization
- Consideration of financial situation and objectives
- Regular suitability reviews

### Fiduciary Standard (if applicable)
- Act in client's best interest
- Disclose conflicts of interest
- Seek best execution
- Document investment advice rationale

### Best Execution
- Minimize transaction costs
- Use quality custodians
- Competitive pricing on products
- Fair fee structures

## Risk Profiling Technology

### Questionnaire Platforms
- Online questionnaires with branching logic
- Mobile-friendly interfaces
- Real-time scoring
- Client dashboard visualization

### Machine Learning Applications
- Predict optimal risk profile based on behavioral patterns
- Identify at-risk portfolios (drawdown risk)
- Anomaly detection for sudden risk changes
- Personalized product recommendations

### Data Analysis
- Correlation with actual portfolio behavior
- Outcomes analysis (client satisfaction, retention)
- Stress test on historical downturns
- Ongoing calibration and improvement

## Common Risk Profiling Mistakes

1. **Over-reliance on Single Metric**: Use multiple assessment methods
2. **Ignoring Life Circumstances**: Beyond time horizon and income
3. **Static Profiles**: Review and update periodically
4. **Marketing-Driven Profiles**: Ensure truly suitable allocations
5. **Underestimating Sequence Risk**: Particularly important for retirees
6. **Ignoring Behavioral Factors**: Psychology matters significantly
7. **Poor Communication**: Educate clients before and during downturns
