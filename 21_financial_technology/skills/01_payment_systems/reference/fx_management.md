# Foreign Exchange (FX) Management Reference

## Overview

FX management involves handling currency conversion, hedging currency risk, and optimizing exchange rates in international payment transactions. Critical for global merchants and fintech platforms.

## Exchange Rate Fundamentals

### Bid-Ask Spread

```
Mid-Market Rate (True Rate):
- The real market exchange rate
- What banks trade at (interbank)
- No markup or margin
- Reference only for consumers

Example:
EUR/USD mid-market: 1.10000

Bid Price (What bank pays):
- Price bank pays to buy EUR (sell USD)
- Slightly lower than mid-market
- Example: 1.09950

Ask Price (What bank charges):
- Price bank charges to sell EUR (buy USD)
- Slightly higher than mid-market
- Example: 1.10050

Spread:
- Difference between bid and ask
- 1.10050 - 1.09950 = 0.00100 (0.090%)
- Bank's profit margin
- Typical for major pairs: 0.01-0.05%
- Typical for minor pairs: 0.05-0.20%

Customer Impact:
- Mid-market 1.10000
- Bank's ask: 1.10050 (customer pays more)
- For €10,000: Pay $11,005 instead of $11,000
- Extra cost: $5 (0.045% markup)

Merchant Impact:
- Receiving EUR funds
- Bank bids: 1.09950
- Merchant receives less
- For €10,000: Receive $10,995 instead of $11,000
- Less revenue: $5 (0.045% markdown)
```

### Currency Pair Characteristics

```
Major Pairs (Highest Volume, Tightest Spreads):
- EUR/USD
- GBP/USD
- USD/JPY
- USD/CHF
- Spread: 0.01-0.03%
- Most liquid

Minor Pairs (Lower Volume, Wider Spreads):
- EUR/GBP
- EUR/JPY
- AUD/USD
- Spread: 0.05-0.10%

Exotic Pairs (Low Volume, Wide Spreads):
- EUR/ZAR (South Africa)
- USD/BRL (Brazil)
- USD/INR (India)
- Spread: 0.20-0.50%

Factors Affecting Spreads:
- Trading volume
- Volatility
- Liquidity
- Time of day (peak trading hours tightest)
- Central bank actions
- Economic data releases
```

## Conversion and Settlement

### Conversion Methods

```
Spot Rate Conversion:
- Immediate conversion at current rate
- Standard for most transactions
- Settlement: T+2 (2 business days)
- Risk: Currency can move in those 2 days

Forward Contract:
- Lock rate for future date
- Can be T+3, T+7, T+30, T+60, etc.
- Remove currency risk
- Cost: Interest rate differential

Currency Swap:
- Exchange principal at start and end
- Interest payments during holding period
- Used for longer-term hedging
- More complex than forward

Money Market Hedge:
- Borrow in one currency, lend in another
- Effective hedge at cost of borrowing
- Alternative to forwards
- Complex execution
```

### Settlement Timeline

```
Standard T+2 Settlement:
- Day 0: Contract agreed
- Day 1: Settlement date
- Day 2: Funds delivered
- Day 3: Funds available for use

Example:
- Monday morning: Agree to buy EUR100,000 at 1.10000
- Wednesday: EUR100,000 delivered to your EUR account
- EUR account credited: USD110,000 transferred

Risks During T+2:
- Exchange rate moves (not protected)
- Counterparty risk (rare for banks)
- Settlement risk (very rare, well-managed)
- Timing mismatch (one side early/late)
```

## Hedging Strategies

### Forward Contracts

```
Example: Multinational has EUR1,000,000 receivable in 30 days

Scenario 1: No Hedge
- Today spot: EUR/USD 1.10000
- Expected proceeds: $1,100,000
- Risk: Rate could drop to 1.08000
- Worst case: $1,080,000 (lose $20,000)
- Best case: Rate rises to 1.12000
- Benefit: $1,120,000 (gain $20,000)

Scenario 2: Forward Contract
- Today spot: EUR/USD 1.10000
- Forward rate (30-day): 1.09500
- Lock in: $1,095,000 (3-month interest rate differential)
- No matter what happens, get $1,095,000
- Lose opportunity if rate rises to 1.12000
- Gain protection if rate drops to 1.08000
- True cost: $5,000 (for certainty)

Decision:
- Forward if need certainty (budget planning)
- No hedge if can absorb loss (speculation acceptable)
- Partial hedge if moderate risk aversion

Cost of Forward:
- Interest rate differential
- EUR 3-month rate: 3.5%
- USD 3-month rate: 5.5%
- USD premium: 2%
- 3-month impact: 0.5%
- On EUR1M: EUR5,000 cost
- Effective: 1.10000 - 0.00500 = 1.09500
```

### Netting Strategy

```
Multi-Currency Approach:
- Match inflows/outflows by currency
- Net position only
- Reduces hedge cost

Example:
Company has:
- EUR inflows: €500,000
- EUR outflows: €300,000
- Net EUR: €200,000 (only hedge this)

Traditional:
- Hedge all: €500,000 forward
- Cost: High

Netting:
- Offset EUR inflows with EUR outflows
- Only hedge net: €200,000
- Cost: Lower (only 40% of total)

Implementation:
- Set up in-house bank with multiple currency accounts
- Consolidate all transactions
- Net each currency
- Execute hedge on net position only
```

### Layering Strategy

```
Hedge percentage gradually:
- Reduces timing risk
- Locks in average rate
- Accepts some volatility

Example: EUR1,000,000 expected in 30 days

Week 1: Hedge 25% at 1.10000
- Locks in: EUR250,000 at 1.10000 = $275,000

Week 2: Hedge 25% at 1.09500
- Locks in: EUR250,000 at 1.09500 = $273,750

Week 3: Hedge 25% at 1.09000
- Locks in: EUR250,000 at 1.09000 = $272,250

Week 4: Leave unhedged 25%
- Depends on actual rate

Outcome:
- 75% locked: Average ~1.09500
- 25% floating: Depends on week 4
- If week 4 rate: 1.10500
- Final result: $1,096,875 (weighted average of locked + floating)

Benefit vs. Full Hedge:
- If rate rises post-week 4, you benefit on 25%
- If rate falls, downside limited on 75%
- Balanced risk/reward
```

## FX API Implementation

### Real-Time Rate API

```python
import requests
from datetime import datetime
import json

class FXManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.fxprovider.com'
        self.rate_cache = {}
        self.cache_ttl = 5  # 5 seconds

    def get_current_rate(self, from_currency, to_currency):
        """Get current exchange rate"""
        pair = f"{from_currency}/{to_currency}"

        # Check cache
        if pair in self.rate_cache:
            cached_rate, timestamp = self.rate_cache[pair]
            age = (datetime.now() - timestamp).total_seconds()
            if age < self.cache_ttl:
                return cached_rate

        # Fetch from API
        try:
            response = requests.get(
                f'{self.base_url}/rates',
                params={
                    'from': from_currency,
                    'to': to_currency,
                    'type': 'live'
                },
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=5
            )

            data = response.json()
            rate = {
                'mid': data['mid_market_rate'],
                'bid': data['bid_price'],  # Bank buys at this
                'ask': data['ask_price'],  # Bank sells at this
                'spread': data['ask_price'] - data['bid_price'],
                'timestamp': datetime.now()
            }

            # Cache the rate
            self.rate_cache[pair] = (rate, datetime.now())

            return rate
        except Exception as e:
            return {'error': str(e)}

    def convert_amount(self, amount, from_currency, to_currency, direction='sell'):
        """Convert amount at current rate"""
        rate_data = self.get_current_rate(from_currency, to_currency)

        if 'error' in rate_data:
            return {'error': rate_data['error']}

        # Use bid if selling to bank, ask if buying from bank
        rate = rate_data['bid'] if direction == 'sell' else rate_data['ask']

        converted = amount * rate

        return {
            'original_amount': amount,
            'original_currency': from_currency,
            'converted_amount': converted,
            'converted_currency': to_currency,
            'rate': rate,
            'spread': rate_data['spread'],
            'markup_pct': (rate_data['spread'] / rate_data['mid']) * 100
        }

    def get_forward_rate(self, from_currency, to_currency, days=30):
        """Get forward rate for future date"""
        try:
            response = requests.get(
                f'{self.base_url}/forward',
                params={
                    'from': from_currency,
                    'to': to_currency,
                    'days': days
                },
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=5
            )

            data = response.json()
            return {
                'spot_rate': data['spot_rate'],
                'forward_rate': data['forward_rate'],
                'days': days,
                'cost_bps': (data['spot_rate'] - data['forward_rate']) / data['spot_rate'] * 10000
            }
        except Exception as e:
            return {'error': str(e)}

    def hedge_forward(self, amount, from_currency, to_currency, days=30):
        """Execute forward contract"""
        rate_data = self.get_forward_rate(from_currency, to_currency, days)

        if 'error' in rate_data:
            return {'error': rate_data['error']}

        # Lock in the forward rate
        locked_amount = amount * rate_data['forward_rate']

        # Execute contract (simplified)
        try:
            response = requests.post(
                f'{self.base_url}/contracts',
                json={
                    'type': 'forward',
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'amount': amount,
                    'rate': rate_data['forward_rate'],
                    'settlement_date': days,
                    'action': 'create'
                },
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=5
            )

            data = response.json()
            return {
                'contract_id': data['contract_id'],
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'locked_rate': rate_data['forward_rate'],
                'locked_amount': locked_amount,
                'settlement_days': days,
                'cost': rate_data['cost_bps'] / 10000 * amount,  # In from_currency
                'status': 'CONFIRMED'
            }
        except Exception as e:
            return {'error': str(e)}


# Usage Example
fx_manager = FXManager(api_key='YOUR_API_KEY')

# Get current rate
current_rate = fx_manager.get_current_rate('EUR', 'USD')
print(f"EUR/USD - Bid: {current_rate['bid']}, Ask: {current_rate['ask']}")

# Convert amount
conversion = fx_manager.convert_amount(100000, 'EUR', 'USD', direction='sell')
print(f"€{conversion['original_amount']} = ${conversion['converted_amount']:.2f}")
print(f"Markup: {conversion['markup_pct']:.3f}%")

# Hedge with forward contract
hedge = fx_manager.hedge_forward(100000, 'EUR', 'USD', days=30)
print(f"Hedged rate: {hedge['locked_rate']}")
print(f"Locked amount: ${hedge['locked_amount']:.2f}")
```

## Compliance and Reporting

### Tax Implications

```
Realized vs. Unrealized Gains/Losses:

Realized Gains/Loss:
- When conversion actually happens
- Forward contract matures
- Transaction recorded
- Reported on tax return
- Goes to P&L

Unrealized Gains/Loss:
- Forward contract not yet mature
- Mark-to-market value change
- Reported in financial statements (GAAP)
- May affect taxes (depends on accounting method)

Example:
Forward contract locked at EUR/USD 1.10000 for EUR100,000
- Initial: $110,000 locked

Week 2: Spot rate moves to 1.12000
- Forward still locked at 1.10000
- Unrealized loss: (1.12000 - 1.10000) * 100,000 = $20,000
- Reported in financial statements
- Not yet taxable

When settled:
- Receive $110,000 (locked rate)
- Could have received $112,000 (spot rate)
- Realized loss: $2,000 (after settlement)
- Taxable (can offset other gains)

ASC 815 (Derivatives Accounting):
- Hedge accounting available
- Can defer gains/losses to OCI (Other Comprehensive Income)
- Reduces P&L volatility
- Requires documentation and effectiveness testing
```

### Financial Reporting

```
Balance Sheet:
- Forward contracts: Fair value asset/liability
- Mark-to-market: Current rate vs. locked rate
- In assets if profitable, liabilities if losing
- Disclose in derivative footnote

Income Statement:
- Realized FX gains/losses
- Impact on gross margin
- Separate line item (operating or non-operating)
- Hedge gains offset transaction losses

Disclosure Requirements:
- Hedging policy and objectives
- Fair value of forward contracts
- Gains/losses recognized
- Hedge effectiveness testing
- Sensitivity to FX movements

Risk Disclosures:
- Quantify FX exposure
- Show impact of 10% FX movement
- Examples:
  - "A 10% strengthening of USD vs EUR would reduce gross margin by $500,000"
  - "Outstanding forward contracts: $5M"
  - "Effective hedging ratio: 75% of exposure"
```

### Regulatory Requirements

```
IFRS 9 (International):
- Fair value hedging allowed
- Cash flow hedging allowed
- Document hedge relationship
- Effectiveness testing required
- 80-125% effectiveness range

ASC 815 (US GAAP):
- Hedge accounting permitted
- Designate and document
- Effectiveness testing
- Quarterly assessment
- Similar 80-125% range

AML/KYC (Anti-Money Laundering):
- Forward contracts are financial instruments
- Know your counterparty
- Sanctions screening
- Beneficial ownership verification
- Documentation and reporting

Documentation:
- Master agreement with counterparty
- ISDA agreement (standard)
- Confirmation of each trade
- Valuation methodology documented
- Reconciliation procedures
```

## Cost Optimization

### Merchant FX Strategy

```
Traditional Bank:
- Markup: 2-3% on exchange rate
- On €100,000 at 1.10000:
  - Bank rate: 1.10 - 0.0275 = 1.0725 (if selling to bank)
  - Receive: $107,250
  - Bank profit: €2,750 (or $3,025)
  - Cost: 2.75%

Specialist FX Provider:
- Markup: 0.5-1.0%
- On €100,000 at 1.10000:
  - Provider rate: 1.10 - 0.006 = 1.094
  - Receive: $109,400
  - Provider profit: €600 (or $660)
  - Cost: 0.60%
  - Savings vs. bank: $2,365

Blockchain/Crypto:
- No markup if using stablecoins
- Cost: Network fees only ($10-100)
- Speed: Minutes
- Risk: Custody, volatility, regulatory

Volume Optimization:
- Higher volumes: Better rates
- $1M/month: 1% markup
- $10M/month: 0.5% markup
- $100M/month: 0.2% markup

Annual Impact:
- $1M/month EUR volume
- Traditional bank: $30,000/year cost
- Specialist: $6,000/year cost
- Savings: $24,000/year (just in FX)
- With 10% of revenue: 0.5% margin improvement
```

### Process Optimization

```
Timing Optimization:
- Execute forward contracts during liquid hours
- Better rates during peak London/NY overlap
- Avoid low-liquidity times (Asian morning)
- Saves: 0.02-0.05% on spreads

Aggregation:
- Batch multiple payments
- Single forward contract instead of individual
- Lower per-transaction costs
- Saves: Per-transaction overhead

Dynamic Routing:
- Route to lowest-cost provider
- Stripe, Wise, PayPal, bank
- Different providers for different pairs
- Saves: 0.5-1% on spreads

In-House Banking:
- Consolidate FX for entire organization
- Net inflows/outflows
- Single hedging strategy
- Saves: 2-3% with volume leverage
```
