# Smart Order Routing Guide

## SOR Architecture

```python
class SmartOrderRouter:
    def __init__(self, venues, market_data):
        self.venues = venues
        self.market_data = market_data
        self.routing_history = []

    def select_optimal_venue(self, order):
        """Route order to best execution venue"""

        venue_scores = {}

        for venue in self.venues:
            # 1. Get best bid/ask from venue
            best_bid, bid_vol = self.market_data.get_best_bid(venue)
            best_ask, ask_vol = self.market_data.get_best_ask(venue)

            # 2. Estimate execution price
            if order.side == BUY:
                execution_price = best_ask
                available_qty = ask_vol
            else:
                execution_price = best_bid
                available_qty = bid_vol

            # 3. Calculate total cost
            spread_cost = self._calculate_spread_cost(
                order.side, best_bid, best_ask, order.qty)

            exchange_fee = self._get_exchange_fee(
                venue, order.side, order.qty)

            market_impact = self._estimate_market_impact(
                venue, order.qty, available_qty)

            total_cost = spread_cost + exchange_fee + market_impact

            venue_scores[venue] = {
                'execution_price': execution_price,
                'total_cost': total_cost,
                'spread': best_ask - best_bid,
                'available_qty': available_qty,
                'latency': self._get_latency(venue)
            }

        # Select venue with lowest cost
        best_venue = min(venue_scores.items(),
                        key=lambda x: x[1]['total_cost'])[0]

        self.routing_history.append({
            'order_id': order.id,
            'venue': best_venue,
            'scores': venue_scores
        })

        return best_venue

    def route_large_order(self, order):
        """Split large orders across multiple venues"""
        if order.qty <= 10000:
            # Small order: single venue
            venue = self.select_optimal_venue(order)
            return [(venue, order.qty)]

        # Large order: split across venues
        allocations = []
        remaining_qty = order.qty

        for venue in sorted(self.venues,
                          key=lambda v: self._get_liquidity(v),
                          reverse=True):
            liquidity = self._get_liquidity(venue)
            alloc_qty = min(liquidity, remaining_qty)

            if alloc_qty > 0:
                allocations.append((venue, alloc_qty))
                remaining_qty -= alloc_qty

            if remaining_qty == 0:
                break

        return allocations
```

## Venue Selection Logic

```python
# Venue configuration
VENUES = {
    'NYSE': {
        'maker_rebate': 0.001,
        'taker_fee': -0.003,
        'latency_us': 250,
        'liquidity_score': 0.95
    },
    'NASDAQ': {
        'maker_rebate': 0.0009,
        'taker_fee': -0.0032,
        'latency_us': 200,
        'liquidity_score': 0.92
    },
    'BATS': {
        'maker_rebate': 0.0008,
        'taker_fee': -0.0034,
        'latency_us': 150,
        'liquidity_score': 0.85
    },
    'CITADEL_DARK': {
        'maker_rebate': 0,
        'taker_fee': 0,
        'latency_us': 500,
        'liquidity_score': 0.3,
        'order_type': 'DARK_POOL'
    }
}
```

## Execution Quality Monitoring

```python
class ExecutionQualityTracker:
    def record_execution(self, order, execution):
        # Record for analysis
        self.executions.append({
            'symbol': order.symbol,
            'venue': execution.venue,
            'ordered_price': order.price,
            'executed_price': execution.price,
            'slippage': execution.price - order.price,
            'timestamp': execution.timestamp
        })

    def get_venue_statistics(self, venue):
        venue_executions = [e for e in self.executions
                           if e['venue'] == venue]

        slippages = [e['slippage'] for e in venue_executions]
        avg_slippage = np.mean(slippages)
        median_slippage = np.median(slippages)
        std_slippage = np.std(slippages)

        return {
            'venue': venue,
            'avg_slippage': avg_slippage,
            'median_slippage': median_slippage,
            'std_slippage': std_slippage,
            'sample_size': len(venue_executions)
        }
```

## RegSHO Compliance

```python
class RegSHOHandler:
    """Regulation SHO short sale handling"""

    def check_short_sale_eligibility(self, order, security):
        if order.side == BUY:
            return True  # Buys are always allowed

        # Short sale restrictions
        if security.is_threshold_security():
            # Shares must be located and borrowed
            if not self.locate_shares(security, order.qty):
                return False

            # Borrow shares
            if not self.borrow_shares(security, order.qty):
                return False

        return True

    def locate_shares(self, security, qty):
        """Verify shares available to short"""
        available = self.get_borrow_availability(security)
        return available >= qty

    def borrow_shares(self, security, qty):
        """Execute share borrow"""
        self.broker.borrow(security, qty)
        return True
```

## Best Practices

- Monitor execution quality by venue continuously
- Adjust routing based on real-time market conditions
- Maintain relationships with all venues
- Document routing decisions for compliance
- Test failover venues regularly
- Monitor latency to all venues
