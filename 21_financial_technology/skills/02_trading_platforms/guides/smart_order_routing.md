# Advanced Smart Order Routing Guide

## Latency-Aware Routing

```python
class LatencyAwareRouter:
    def select_venue_accounting_for_latency(self, order):
        """Route order considering latency to venue"""

        venue_options = []

        for venue in self.venues:
            # Get current best bid/ask
            best_bid, best_ask = self.market_data.get_best_prices(venue)

            # Estimate prices by the time order arrives
            latency_ms = self.get_latency(venue)
            volatility_per_ms = self.estimate_volatility_rate()

            estimated_mid = (best_bid + best_ask) / 2
            price_range = volatility_per_ms * latency_ms

            # Calculate worst-case execution
            if order.side == BUY:
                worst_case_price = estimated_mid + price_range
            else:
                worst_case_price = estimated_mid - price_range

            # Score venue
            venue_options.append({
                'venue': venue,
                'latency': latency_ms,
                'worst_case_price': worst_case_price,
                'expected_execution': (best_bid + best_ask) / 2
            })

        # Select venue minimizing worst-case price
        best = min(venue_options, 
                  key=lambda x: abs(x['worst_case_price']))
        return best['venue']
```

## Dark Pool Participation

```python
class DarkPoolRouter:
    def route_with_dark_pool_priority(self, order):
        """Try dark pools first, then lit venues"""

        # 1. Try dark pools
        dark_result = self.try_dark_pool_execution(order)
        if dark_result['success']:
            return dark_result

        # 2. Fallback to lit venues
        lit_result = self.route_to_lit_venue(order)
        return lit_result

    def try_dark_pool_execution(self, order):
        dark_pools = ['CITADEL', 'BARCLAYS_LX', 'GS_SIGMA_X']

        for dark_pool in dark_pools:
            # Send order with short timeout
            result = self.send_to_dark_pool(order, dark_pool, timeout_ms=50)

            if result.executed:
                return {
                    'success': True,
                    'venue': dark_pool,
                    'execution_price': result.price,
                    'quantity': result.quantity
                }

        return {'success': False}
```
