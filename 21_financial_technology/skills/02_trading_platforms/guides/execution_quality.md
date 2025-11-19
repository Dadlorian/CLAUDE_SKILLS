# Execution Quality Measurement Guide

## VWAP vs Arrival Price Analysis

```python
class ExecutionQualityAnalyzer:
    def analyze_execution(self, order, execution_details):
        """Measure execution quality vs benchmarks"""

        # Arrival price = price when order entered
        arrival_price = execution_details['arrival_price']

        # Calculate VWAP from execution
        vwap = sum(p * q for p, q in zip(
            execution_details['fill_prices'],
            execution_details['fill_quantities']
        )) / sum(execution_details['fill_quantities'])

        # Calculate slippage
        slippage = (vwap - arrival_price) * sum(
            execution_details['fill_quantities']
        )

        # Market impact = Change in mid-price due to execution
        market_impact = self._estimate_market_impact(
            execution_details['final_midpoint'] - arrival_price
        )

        return {
            'arrival_price': arrival_price,
            'vwap': vwap,
            'slippage_cents': slippage,
            'market_impact_cents': market_impact,
            'execution_cost_bps': (slippage + market_impact) / arrival_price / 100
        }
```

## Implementation Shortfall

```python
def calculate_implementation_shortfall(parent_order, execution):
    """Calculate total execution cost vs optimal"""

    # Total cost = (Final price - Arrival price) × Quantity
    total_cost = (execution['final_price'] - execution['arrival_price']) * execution['quantity']

    # Cost components
    explicit_costs = execution['fees'] + execution['exchange_costs']
    implicit_costs = total_cost - explicit_costs

    return {
        'total_cost': total_cost,
        'explicit_costs': explicit_costs,
        'implicit_costs': implicit_costs,
        'cost_per_share': total_cost / execution['quantity']
    }
```
