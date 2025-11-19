# Regulatory Reporting Reference

## Overview
Financial institutions must report trading activity and other metrics to regulatory authorities. Failure to comply results in significant fines.

## Trade Reporting Requirements

### FINRA Rules (US Equities)

**Rule 6730: Trade Reporting**
- Report to FINRA Trade Reporting Facilities (TRF)
- Within T+0 (same business day)
- Block trades: within 15 minutes
- Smaller trades: within 60 seconds

**Report Fields**:
- Security identifier (symbol, CUSIP)
- Trade price and volume
- Execution time (to second)
- Dealer information
- Capacity (principal, agent)
- Trade type (reported late, out of sequence, etc.)

**Example Report**:
```
Symbol: AAPL
Trade Price: $155.32
Quantity: 500
Execution Time: 10:25:47
Dealer ID: 0001234
Capacity: Principal
Timestamp: 2025-11-19 10:25:48
```

### SEC Rules (US Securities)

**Regulation FD (Fair Disclosure)**
- Material information must be disclosed simultaneously
- No selective disclosure
- Regulates insider information flow

**Regulation SHO (Short Selling)**
- Short positions must be located
- Short sale circuit breaker rules
- Threshold securities restrictions
- Close-out requirement (T+3)

### MiFID II Reporting (Europe)

**Scope**: EU and UK financial instruments trading

**Article 26 (Transaction Reporting)**
- Report all transactions in financial instruments
- Within 4 business hours of execution
- Includes OTC trades

**Data Elements**:
- Transaction reference number (TRN)
- Reporting party identifier
- Counterparty identifier
- Execution venue
- Financial instrument
- Transaction price and quantity
- Transaction date/time
- Asset class
- Settlement details

**Example EMIR Report**:
```
TRN: 2025111900001234
Reporting Party: ABC Capital
Counterparty: XYZ Bank
Execution Venue: REGULATED MARKET
Instrument: AAPL (XETRA)
Price: €152.45
Quantity: 1000
Execution Date: 2025-11-19
Time: 10:25:32.123
Asset Class: EQUITIES
Settlement: T+2
```

## Best Execution Reporting

### MiFID II Costs and Charges

**Requirement**: Firms must disclose execution costs.

**Cost Categories**:
- **Implicit Costs**:
  - Bid-ask spread: Half-spread paid
  - Market impact: Change in price due to order
  - Opportunity cost: Timing costs

- **Explicit Costs**:
  - Exchange fees
  - Broker fees
  - Regulatory fees
  - Settlement fees

**Calculation**:
```
Total Cost = Implicit Costs + Explicit Costs

VWAP Cost = (VWAP - Execution Price) * Quantity
Spread Cost = (Best Bid - Best Ask) * Quantity
```

### Quarterly Execution Quality Reports

**Required Metrics**:
- Execution venues used
- Volume by venue
- Price performance vs benchmark
- Slippage analysis
- Explicit fee costs

**Sample Report Summary**:
```
Venue: NYSE
Volume: 2.5M shares
Avg Price: $155.31
VWAP: $155.28
Slippage: 0.003/share = $7,500 total
Exchange Fees: 0.001/share = $2,500 total
Total Cost: $10,000
Cost per Share: 0.004
```

## Position and Exposure Reporting

### Large Trader Reporting

**SEC Rule 13h: Reportable Traders**
- Report trades > 2M shares (aggregate)
- Quarterly to SEC
- Beneficial ownership disclosure
- Filing within 10 days of month end

**Large Trader Identity**:
```
If aggregate trading in US equities:
- > $20M in value (end of month), or
- > 200 positions of $100K+ each
Then classified as Large Trader
```

### Beneficial Ownership

**Form 13D (Direct Ownership)**
- >5% ownership threshold
- File within 10 days of crossing
- Continuous updates for 5%+ holders

**Form 4 (Officer/Director Trades)**
- Form within 2 business days
- Officer, director, or 10% holder trades
- Insider trading tracking

## Regulatory Examinations

### Examination Readiness

**Areas Firms Must Track**:
1. **Trade Reporting Completeness**
   - No missing reports
   - No late reports
   - Accurate data elements

2. **Best Execution**
   - Execution quality documentation
   - Venue selection rationale
   - Cost analysis

3. **Risk Management**
   - Position limits
   - Margin requirements
   - Intraday monitoring

4. **Compliance**
   - Policy documentation
   - Training records
   - Exception handling

### Common Violations

**Trade Reporting**:
- Late trade reports (80% of fines)
- Inaccurate data fields
- Duplicate reports
- Missing data elements

**Execution Quality**:
- Poor venue selection
- Inadequate documentation
- No slippage analysis
- Unexplained deviations

**Example Sanction**:
```
Firm: XYZ Trading
Violation: Late trade reporting
Details: 5,000 trades reported >60 seconds late
Fine: $2.5M (avg $500/trade)
```

## Automated Compliance

### Real-Time Trade Validation

```python
def validate_trade_for_reporting(trade):
    # Checks before report submission

    # 1. Required fields present
    assert trade.security_id
    assert trade.price > 0
    assert trade.qty > 0
    assert trade.execution_time

    # 2. Time check
    time_since_execution = now - trade.execution_time
    if time_since_execution > 60_seconds:
        alert("Late trade - report ASAP")

    # 3. Duplicate detection
    if duplicate_trade_exists(trade):
        alert("Potential duplicate")

    # 4. Reasonableness check
    if not is_price_reasonable(trade):
        alert("Price anomaly")

    # 5. Settlement check
    if not is_settlement_valid(trade):
        alert("Settlement issue")

    return True
```

### Reporting Pipeline

```
Trade Execution
    ↓
Validation/Checking
    ↓
Enrichment (add regulatory fields)
    ↓
Aggregation (batch similar trades)
    ↓
Formatting (vendor-specific format)
    ↓
Submission (electronic to regulator)
    ↓
Confirmation/Reconciliation
```

## Regulatory Database Requirements

### Data Retention
- Trade reports: 6 years minimum
- Correspondence: 6 years minimum
- Compliance records: 6 years minimum
- Audit trail: Complete and tamper-proof

### Searchability
- Query by date range
- Search by symbol/issuer
- Search by account
- Search by trader/desk

### Audit Trail
- Complete action history
- Timestamps for all events
- User identification
- No retroactive modifications

## Best Practices

1. **Automate Reporting**: Reduce manual errors
2. **Real-Time Monitoring**: Catch issues immediately
3. **Data Quality**: Invest in data validation
4. **Testing**: Test reporting against regulatory specs
5. **Documentation**: Keep policies and procedures updated
6. **Training**: Ensure staff understands regulations
7. **Auditing**: Regular internal compliance audits
8. **Escalation**: Clear procedures for violations

## Key Dates & Deadlines

| Requirement | Deadline | Frequency |
|------------|----------|-----------|
| Trade Report (FINRA) | T+0 | Every trade |
| Block Trade Report | T+0 (15 min) | Large trades |
| Form 4 Filing | 2 business days | Officer trades |
| Large Trader Report | T+10 after month end | Monthly |
| Quarterly Exec Quality | 30 days after quarter | Quarterly |
| Annual Compliance Cert | 30 days after year end | Annually |
