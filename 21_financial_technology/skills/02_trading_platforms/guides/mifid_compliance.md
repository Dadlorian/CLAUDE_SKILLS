# MiFID II Compliance Guide

## Transaction Reporting

```python
class MiFIDReportingEngine:
    def report_transaction(self, trade):
        """Generate MiFID II transaction report"""

        report = {
            # Reference
            'transaction_reference': self.generate_trn(),
            'execution_venue': trade.venue,
            'execution_timestamp': trade.timestamp,

            # Parties
            'reporting_entity': 'ABC Trading Ltd',
            'counterparty': trade.counterparty,

            # Instrument
            'isin': trade.security.isin,
            'financial_instrument_id': trade.security.id,

            # Transaction Details
            'transaction_price': trade.price,
            'transaction_quantity': trade.quantity,
            'transaction_currency': 'USD',

            # Settlement
            'settlement_date': trade.settlement_date,
            'trading_date': trade.execution_date,

            # Costs and Charges
            'explicit_costs': trade.exchange_fee + trade.broker_fee,
            'implicit_costs': self.calculate_implicit_costs(trade),
            'total_cost': trade.exchange_fee + trade.broker_fee +
                         self.calculate_implicit_costs(trade)
        }

        self.submit_to_authority(report)  # Send to NCA
        return report

    def calculate_implicit_costs(self, trade):
        """Calculate spread and market impact costs"""
        midpoint = (trade.bid + trade.ask) / 2
        spread_cost = abs(trade.price - midpoint)
        market_impact = self._estimate_market_impact(trade)
        return spread_cost + market_impact
```

## Cost and Charges Disclosure

```
MiFID II Costs Report Format:

Instrument: AAPL
Period: Q3 2025

Execution Venues Used:
- NYSE: 60% of volume
- NASDAQ: 30% of volume  
- DARK POOL: 10% of volume

Average Execution Quality:
- VWAP Comparison: -0.25bps (favorable)
- Slippage: 0.15bps
- Spread Cost: 0.50bps
- Market Impact: 0.10bps

Total Implicit Costs: 0.75bps
Explicit Fees: 0.30bps

Net Cost: 1.05bps per share
```
