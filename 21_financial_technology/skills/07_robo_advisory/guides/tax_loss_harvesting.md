# Tax-Loss Harvesting Implementation Guide

## Tax-Loss Harvesting Overview

Tax-loss harvesting (TLH) is a strategy that systematically sells securities at a loss to offset capital gains and reduce taxable income, reinvesting in similar securities to maintain portfolio exposure.

## Core Mechanics

### Identification Algorithm

```python
def identify_harvesting_opportunities(portfolio, tax_rate=0.20):
    """
    Identify all positions with unrealized losses eligible for harvesting
    """
    opportunities = []

    for holding in portfolio.holdings:
        unrealized_loss = holding.cost_basis - holding.market_value

        if unrealized_loss > 0:
            # Verify not subject to wash sale
            wash_sale_risk = check_wash_sale_rules(holding)

            if not wash_sale_risk:
                tax_benefit = unrealized_loss * tax_rate
                opportunities.append({
                    'security': holding.symbol,
                    'loss': unrealized_loss,
                    'tax_benefit': tax_benefit,
                    'current_price': holding.market_value,
                    'cost_basis': holding.cost_basis
                })

    # Sort by tax benefit (highest first)
    opportunities.sort(key=lambda x: x['tax_benefit'], reverse=True)

    return opportunities
```

### Wash-Sale Compliance

**The 30-Day Rule**:
```
Cannot deduct losses if you acquire substantially identical security within:
- 30 days BEFORE sale
- 30 days AFTER sale
- Total: 61-day window centered on sale
```

**Implementation**:
```python
def check_wash_sale_rules(position, lookback_days=30, lookahead_days=30):
    """
    Check if position violates wash-sale rules
    """
    sale_date = datetime.now()
    start_date = sale_date - timedelta(days=lookback_days)
    end_date = sale_date + timedelta(days=lookahead_days)

    # Check for prior purchases (lookback)
    prior_purchases = portfolio.get_purchases(
        position.symbol,
        start_date,
        sale_date
    )

    # Check for planned purchases (lookahead planning)
    planned_purchases = portfolio.get_planned_purchases(
        position.symbol,
        sale_date,
        end_date
    )

    # Check for equivalent security purchases
    equivalent_purchases = check_equivalent_securities(
        position.symbol,
        start_date,
        end_date
    )

    return bool(prior_purchases or planned_purchases or equivalent_purchases)
```

## Replacement Security Selection

### Substantially Identical Concept

**Principle**: Cannot repurchase same security for 30 days

**Solution**: Use similar but not identical security

**Examples**:
```
Apple (AAPL) Loss Harvesting:
- Cannot buy: AAPL shares
- Can buy: Apple ETF (within sector)
  - QQQ (Nasdaq 100, includes AAPL)
  - VTI (Total US market, includes AAPL)
  - VOO (S&P 500, includes AAPL)
- Different but similar exposure

Vanguard Total Bond (BND) Loss Harvesting:
- Cannot buy: BND
- Can buy:
  - VBTLX (Vanguard Total Bond Admiral)
  - SCHZ (Schwab US Aggregate Bond)
  - LQD (Investment-Grade Corporate)
- Maintains fixed income exposure
```

### Replacement Strategy Algorithm

```python
def find_replacement_securities(symbol, asset_class):
    """
    Find suitable replacement securities for wash-sale compliance
    """
    replacements = []

    # Option 1: Different ETF, same index
    similar_etfs = find_competing_etfs(symbol)
    replacements.extend(similar_etfs)

    # Option 2: Broader index fund (includes position)
    broader_funds = find_broader_index_funds(asset_class)
    replacements.extend(broader_funds)

    # Option 3: Style-variant fund (same asset class, different style)
    style_variants = find_style_variants(asset_class)
    replacements.extend(style_variants)

    # Rank by suitability
    ranked = rank_replacements(replacements, symbol, asset_class)

    return ranked[:5]  # Return top 5 options
```

## Harvesting Strategy Patterns

### Pattern 1: Individual Stock Loss Harvesting

**Scenario**:
```
Position: 100 shares of Apple at $150 cost basis
Current Price: $130
Unrealized Loss: $2,000
Tax Benefit at 20% rate: $400
```

**Execution**:
```
1. Sell 100 AAPL @ $130 = $13,000 proceeds
2. Buy 100 shares VTI @ $130 = $13,000 (S&P 500, includes AAPL)
3. Result: Realized $2,000 loss (tax benefit: $400)
4. Market Exposure: Maintained (S&P 500)
5. Wash-Sale Window: 31+ days before can rebuy AAPL
```

### Pattern 2: Fund Loss Harvesting

**Scenario**:
```
Position: $10,000 Vanguard Total Bond (BND)
Cost Basis: $10,000
Current Value: $9,400
Unrealized Loss: $600
Tax Benefit at 25% rate: $150
```

**Execution**:
```
1. Sell $9,400 of BND
2. Buy $9,400 of SCHZ (alternative bond fund)
3. Realized Loss: $600 (tax benefit: $150)
4. Wash-Sale: Must avoid BND for 30 days
5. After 31 days: Can switch back to BND if desired
```

### Pattern 3: Sector Rotation Harvesting

**During downturns**:
```
Tech Sector Down 20%:
- Sell tech stocks at losses
- Rotate into tech ETF (different fund)
- Maintain sector exposure
- Harvest tax losses during downturn
```

## Advanced Harvesting Techniques

### Continuous Monitoring

**Real-Time Implementation**:
```python
def continuous_harvesting_monitor(portfolio):
    """
    Monitor all positions daily for harvesting opportunities
    Execute when conditions optimal
    """
    while True:
        # Daily check
        opportunities = identify_harvesting_opportunities(portfolio)

        for opportunity in opportunities:
            tax_benefit = opportunity['tax_benefit']

            # Harvest if:
            # 1. Loss is realized
            # 2. Replacement available
            # 3. No wash-sale violations
            # 4. Tax benefit sufficient
            if tax_benefit > MINIMUM_TAX_BENEFIT:
                replacement = select_replacement(opportunity)

                if replacement and not violates_wash_sale(opportunity):
                    harvest_loss(opportunity, replacement)

        # Sleep until next trading day
        sleep_until_next_market_open()
```

### Rolling Harvesting Strategy

**Concept**: Continuously harvest throughout year

**Schedule**:
```
Q1 (Jan-Mar): Harvest winter losses
- Post-holiday market weakness
- Winter corrections

Q2 (Apr-Jun): Harvest spring losses
- Interest rate movements
- Valuation corrections

Q3 (Jul-Sep): Harvest summer losses
- Summer weakness patterns
- Mid-year rebalancing opportunities

Q4 (Oct-Dec): Year-end tax harvesting
- Largest harvesting period
- Final loss realization
- Tax-loss carryforward planning
```

### Sector-Specific Harvesting

**During Sector Weakness**:
```
Tech Sector Down 25%:
- Identify individual tech stocks with losses
- Sell at losses (harvest $50k losses)
- Rotate into tech ETF
- Maintain tech exposure without losses

Result:
- $50,000 in realized losses
- Tax benefit: $12,500 at 25% rate
- Market exposure: Unchanged
- Can rebuy individual stocks after 30 days
```

### Multi-Account Harvesting

**Across Multiple Accounts**:
```python
def cross_account_harvesting(accounts):
    """
    Harvest losses in one account, offset gains in another
    """
    all_positions = []
    all_accounts = []

    # Aggregate positions across accounts
    for account in accounts:
        all_positions.extend(account.get_positions())
        all_accounts.append(account)

    # Identify losses and gains
    losses = [p for p in all_positions if p.unrealized_loss > 0]
    gains = [p for p in all_positions if p.unrealized_gain > 0]

    # Harvest losses where benefits most
    for loss in losses:
        # Find best account to harvest in
        best_account = select_account_for_harvesting(
            loss,
            all_accounts
        )

        harvest_in_account(loss, best_account)

    return total_tax_benefits_realized(losses)
```

## Carryforward Management

### Loss Utilization Strategy

**Annual Loss Limit**:
```
Individual taxpayer can deduct:
- All capital gains
- Plus up to $3,000 of ordinary income
- Excess losses carry forward indefinitely
```

**Carryforward Tracking**:
```python
def manage_loss_carryforward(year_loss, year_income, year_gains):
    """
    Calculate and track loss carryforward
    """
    # Current year deduction
    deductible = min(year_loss, year_gains + 3_000)

    # Calculate carryforward
    carryforward = year_loss - deductible

    # Utilization record
    record = {
        'year': current_year,
        'losses_realized': year_loss,
        'gains_recognized': year_gains,
        'ordinary_income_offset': 3_000,
        'deductible_this_year': deductible,
        'carryforward_to_next_year': carryforward
    }

    return record
```

**Strategic Utilization**:
```
High-income years: Utilize more carryforward losses
Low-income years: Preserve carryforward for future use

Example:
Year 1: Harvest $50,000 losses, only need $10,000
        Carryforward: $40,000

Year 2: High-income year, utilize $40,000 carryforward
        Tax benefit: $40,000 × 35% marginal = $14,000

Year 3: Low-income year
        Preserve remaining carryforward
```

## Tax Impact Analysis

### Calculation Example

**Scenario**:
```
Account Value: $100,000
Allocation: 50% stocks, 50% bonds
Market Down 20%: Stock losses $10,000
Bond losses: $0 (held steady)

Tax-Loss Harvesting:
- Sell stocks at $40,000 value (realize $10,000 loss)
- Rebuy in similar fund
- Tax Benefit: $10,000 × 0.25 tax rate = $2,500

Net Benefit:
- Market Exposure: Unchanged
- Tax Savings: $2,500
- Effective Return: +$2,500 or +2.5%
```

**Performance Impact**:
```
Portfolio without TLH: -$10,000 (loss)
Portfolio with TLH: -$10,000 + $2,500 (tax benefit) = -$7,500 net
Impact: +$2,500 or +25% reduction in losses
```

## Implementation Checklist

### Pre-Harvesting
- [ ] Identify unrealized losses
- [ ] Calculate tax benefit
- [ ] Check wash-sale window
- [ ] Select replacement security
- [ ] Verify no conflicts with investor intent
- [ ] Confirm adequate liquidity

### Execution
- [ ] Sell security at loss
- [ ] Confirm execution price
- [ ] Receive sale proceeds
- [ ] Immediately invest in replacement
- [ ] Confirm purchase completion
- [ ] Generate documentation

### Post-Harvesting
- [ ] Log realized loss
- [ ] Update cost basis
- [ ] Set wash-sale reminder (30+ days)
- [ ] Track carryforward
- [ ] Prepare for tax reporting
- [ ] Notify client/advisor

### Tax Reporting
- [ ] Schedule D preparation
- [ ] Form 8949 (sales of capital assets)
- [ ] Wash-sale adjustments
- [ ] Carryforward reporting
- [ ] Estimated tax implications

## Common Pitfalls

1. **Wash-Sale Violations**: Purchasing same security within 30 days
2. **Inadequate Replacement**: Not maintaining equivalent exposure
3. **Overdoing**: Too many harvests creating complexity
4. **Ignoring Carryforward**: Not tracking and utilizing losses
5. **Poor Documentation**: Insufficient records for tax filing
6. **Timing**: Waiting for perfect conditions instead of harvesting opportunities
7. **Opportunity Cost**: Excessive caution missing harvesting benefits
8. **Complexity**: Over-complicated strategies reducing effectiveness

## Automation Best Practices

1. **Continuous Monitoring**: Check daily for opportunities
2. **Systematic Execution**: Automatic harvesting when triggered
3. **Compliance Automation**: Automatic wash-sale tracking
4. **Documentation**: Automated record-keeping
5. **Reporting**: Automated tax loss reporting
6. **Communication**: Notify client of harvesting benefits
7. **Integration**: Coordinate with rebalancing
8. **Testing**: Backtest before implementation

## Expected Benefits

**Annual Tax-Loss Harvesting Impact**:
- Conservative: 0.25-0.50% annual benefit
- Moderate: 0.50-1.00% annual benefit
- Aggressive: 1.00-1.50% annual benefit

**Variables**:
- Portfolio volatility (higher = more opportunities)
- Market conditions (downturns create opportunities)
- Time horizon (longer = more opportunities)
- Tax bracket (higher bracket = larger benefit)

## Conclusion

Tax-loss harvesting is a powerful strategy that can enhance after-tax returns by 0.5-1.5% annually through systematic loss realization and reinvestment. Proper implementation requires careful attention to wash-sale rules, replacement security selection, and carryforward tracking.
