# Energy Trading & Markets - Production Implementation Guide

## Overview

Energy Trading & Markets involve buying and selling electricity, natural gas, renewable energy credits (RECs), and ancillary services in wholesale and retail markets. This skill covers production-grade implementations of market participation, bidding strategies, risk management, and automated trading systems.

## Core Markets

### 1. Wholesale Electricity Markets
Day-ahead and real-time markets operated by ISOs/RTOs (e.g., CAISO, ERCOT, PJM, NYISO).

### 2. Ancillary Services Markets
Frequency regulation, spinning reserves, voltage support, and black start services.

### 3. Renewable Energy Credits (RECs)
Tradable certificates representing renewable energy generation.

### 4. Capacity Markets
Forward markets for generation capacity commitments.

### 5. Demand Response Programs
Compensation for load reduction during grid events.

## Market Structures (US)

### Independent System Operators (ISOs) / Regional Transmission Organizations (RTOs)
- **CAISO**: California
- **ERCOT**: Texas
- **PJM**: Mid-Atlantic and parts of Midwest
- **NYISO**: New York
- **ISO-NE**: New England
- **MISO**: Midwest
- **SPP**: Southwest Power Pool

## Production-Grade Implementation Example

```python
"""
Production-grade Energy Trading & Market Participation System

Implements:
- Day-ahead and real-time market bidding
- Locational Marginal Price (LMP) analysis
- Portfolio optimization
- Risk management
- Automated trading strategies
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketType(Enum):
    """Energy market types"""
    DAY_AHEAD = "day_ahead"
    REAL_TIME = "real_time"
    ANCILLARY_SERVICES = "ancillary_services"
    CAPACITY = "capacity"

class BidType(Enum):
    """Bid types"""
    ENERGY = "energy"
    REGULATION_UP = "regulation_up"
    REGULATION_DOWN = "regulation_down"
    SPINNING_RESERVE = "spinning_reserve"
    NON_SPINNING_RESERVE = "non_spinning_reserve"

@dataclass
class MarketPrice:
    """Market price data (Locational Marginal Price)"""
    timestamp: datetime
    node_id: str
    lmp_dollars_per_mwh: float
    energy_component: float
    congestion_component: float
    loss_component: float
    market_type: MarketType

@dataclass
class GenerationAsset:
    """Generation asset for market participation"""
    asset_id: str
    asset_name: str
    capacity_mw: float
    min_output_mw: float
    ramp_rate_mw_per_min: float
    marginal_cost_per_mwh: float  # Variable O&M + fuel
    startup_cost: float
    shutdown_cost: float
    node_id: str  # Market node/location

@dataclass
class MarketBid:
    """Market bid submission"""
    bid_id: str
    timestamp: datetime
    asset_id: str
    market_type: MarketType
    bid_type: BidType
    trading_intervals: List[datetime]  # Hours being bid
    quantities_mw: List[float]  # MW for each interval
    prices_per_mwh: List[float]  # Price for each interval
    submitted: bool = False
    accepted_quantities_mw: Optional[List[float]] = None

@dataclass
class PortfolioPosition:
    """Trading portfolio position"""
    timestamp: datetime
    market_type: MarketType
    bought_mwh: float = 0.0
    sold_mwh: float = 0.0
    net_position_mwh: float = 0.0
    average_buy_price: float = 0.0
    average_sell_price: float = 0.0
    realized_pnl: float = 0.0  # Profit and loss

class EnergyTradingSystem:
    """
    Production-grade Energy Trading System

    Features:
    - Multi-market participation (day-ahead, real-time, ancillary)
    - Optimal bidding strategies
    - Portfolio management
    - Risk management
    - P&L tracking
    - Automated execution
    """

    def __init__(self, organization_id: str, iso: str):
        self.organization_id = organization_id
        self.iso = iso  # CAISO, ERCOT, PJM, etc.
        self.generation_assets: Dict[str, GenerationAsset] = {}
        self.market_prices: List[MarketPrice] = []
        self.submitted_bids: List[MarketBid] = []
        self.portfolio_positions: List[PortfolioPosition] = []

    def register_asset(self, asset: GenerationAsset):
        """Register generation asset for market participation"""
        self.generation_assets[asset.asset_id] = asset
        logger.info(
            f"Registered asset {asset.asset_name} ({asset.capacity_mw:.1f} MW) "
            f"at node {asset.node_id}"
        )

    def forecast_day_ahead_prices(
        self,
        node_id: str,
        forecast_date: datetime
    ) -> List[MarketPrice]:
        """
        Forecast day-ahead market prices

        In production, uses:
        - Historical price data
        - Weather forecasts
        - Load forecasts
        - Machine learning models
        """

        # Simplified forecast (production would use ML models)
        forecasted_prices = []

        for hour in range(24):
            timestamp = forecast_date.replace(hour=hour, minute=0, second=0)

            # Simple pattern: higher prices during peak hours
            base_price = 30.0  # $/MWh
            peak_factor = 1.0

            if 7 <= hour <= 9 or 17 <= hour <= 20:  # Morning and evening peaks
                peak_factor = 2.0
            elif 10 <= hour <= 16:  # Mid-day (solar abundance)
                peak_factor = 0.7

            lmp = base_price * peak_factor

            price = MarketPrice(
                timestamp=timestamp,
                node_id=node_id,
                lmp_dollars_per_mwh=lmp,
                energy_component=lmp * 0.9,
                congestion_component=lmp * 0.08,
                loss_component=lmp * 0.02,
                market_type=MarketType.DAY_AHEAD
            )

            forecasted_prices.append(price)

        return forecasted_prices

    def optimize_day_ahead_bid(
        self,
        asset: GenerationAsset,
        price_forecast: List[MarketPrice],
        load_forecast_mw: Optional[List[float]] = None
    ) -> MarketBid:
        """
        Optimize day-ahead market bid for generation asset

        Strategy:
        - Bid at marginal cost for hours when price > marginal cost
        - Don't bid when price < marginal cost
        - Consider startup/shutdown costs
        - Respect ramp rate constraints

        Args:
            asset: Generation asset
            price_forecast: 24-hour price forecast
            load_forecast_mw: If bidding to serve load

        Returns:
            Optimized market bid
        """

        trading_intervals = [p.timestamp for p in price_forecast]
        quantities_mw = []
        prices_per_mwh = []

        for i, price in enumerate(price_forecast):
            # Simple strategy: bid full capacity if price > marginal cost
            if price.lmp_dollars_per_mwh > asset.marginal_cost_per_mwh:
                # Bid at capacity
                quantity = asset.capacity_mw
                bid_price = asset.marginal_cost_per_mwh  # Bid at marginal cost
            else:
                # Don't bid (economically unfavorable)
                quantity = 0.0
                bid_price = 0.0

            quantities_mw.append(quantity)
            prices_per_mwh.append(bid_price)

        bid = MarketBid(
            bid_id=f"BID-{asset.asset_id}-{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            asset_id=asset.asset_id,
            market_type=MarketType.DAY_AHEAD,
            bid_type=BidType.ENERGY,
            trading_intervals=trading_intervals,
            quantities_mw=quantities_mw,
            prices_per_mwh=prices_per_mwh,
            submitted=False
        )

        logger.info(
            f"Optimized day-ahead bid for {asset.asset_name}: "
            f"Average quantity={np.mean([q for q in quantities_mw if q > 0]):.1f} MW"
        )

        return bid

    def submit_bid(self, bid: MarketBid) -> bool:
        """
        Submit bid to ISO/RTO market

        In production, connects to market APIs:
        - CAISO OASIS
        - PJM eMKT
        - ERCOT Market Information System
        """

        # Validate bid
        if not bid.trading_intervals:
            logger.error("Bid has no trading intervals")
            return False

        if len(bid.quantities_mw) != len(bid.trading_intervals):
            logger.error("Quantities and intervals length mismatch")
            return False

        # In production, would submit via ISO API
        bid.submitted = True
        self.submitted_bids.append(bid)

        logger.info(
            f"Submitted bid {bid.bid_id} for {bid.market_type.value} market: "
            f"{len(bid.trading_intervals)} intervals"
        )

        return True

    def process_market_results(
        self,
        bid: MarketBid,
        clearing_prices: List[float],
        accepted_quantities: List[float]
    ):
        """
        Process market clearing results

        Calculate:
        - Accepted quantities
        - Revenue
        - P&L
        """

        if not bid.submitted:
            logger.error("Bid was not submitted")
            return

        bid.accepted_quantities_mw = accepted_quantities

        # Calculate revenue
        total_revenue = sum(
            qty * price
            for qty, price in zip(accepted_quantities, clearing_prices)
        )

        # Calculate cost (marginal cost × generation)
        asset = self.generation_assets[bid.asset_id]
        total_cost = sum(
            qty * asset.marginal_cost_per_mwh
            for qty in accepted_quantities
        )

        profit = total_revenue - total_cost

        logger.info(
            f"Market results for {bid.bid_id}: "
            f"Revenue=${total_revenue:.2f}, Cost=${total_cost:.2f}, "
            f"Profit=${profit:.2f}"
        )

        # Update portfolio position
        total_mwh = sum(accepted_quantities)
        avg_price = total_revenue / total_mwh if total_mwh > 0 else 0

        position = PortfolioPosition(
            timestamp=datetime.utcnow(),
            market_type=bid.market_type,
            sold_mwh=total_mwh,
            net_position_mwh=-total_mwh,  # Negative = short (sold)
            average_sell_price=avg_price,
            realized_pnl=profit
        )

        self.portfolio_positions.append(position)

    def calculate_portfolio_risk(self) -> Dict:
        """
        Calculate portfolio risk metrics

        Metrics:
        - Value at Risk (VaR)
        - Position limits
        - Price exposure
        - Volume exposure
        """

        if not self.portfolio_positions:
            return {'total_risk': 0.0}

        # Net position
        net_position_mwh = sum(p.net_position_mwh for p in self.portfolio_positions)

        # Average price
        total_bought = sum(p.bought_mwh for p in self.portfolio_positions)
        total_sold = sum(p.sold_mwh for p in self.portfolio_positions)

        # Simplified risk calculation
        price_volatility = 15.0  # $/MWh (typical)
        position_risk = abs(net_position_mwh) * price_volatility

        return {
            'net_position_mwh': net_position_mwh,
            'total_bought_mwh': total_bought,
            'total_sold_mwh': total_sold,
            'position_risk_dollars': position_risk,
            'price_volatility': price_volatility
        }

    def optimize_renewable_energy_credit_trading(
        self,
        rec_inventory: int,
        rec_price_forecast: float,
        compliance_target: int
    ) -> str:
        """
        Optimize REC trading strategy

        Decisions:
        - Buy RECs if below compliance target
        - Sell RECs if above target and price is high
        - Hold RECs if price expected to increase

        Returns:
            Trading decision: 'buy', 'sell', or 'hold'
        """

        if rec_inventory < compliance_target:
            decision = 'buy'
            quantity = compliance_target - rec_inventory
            logger.info(f"REC Decision: BUY {quantity} RECs to meet compliance")

        elif rec_inventory > compliance_target * 1.2:
            # Have excess RECs, consider selling
            decision = 'sell'
            quantity = rec_inventory - compliance_target
            logger.info(f"REC Decision: SELL {quantity} excess RECs")

        else:
            decision = 'hold'
            logger.info("REC Decision: HOLD current position")

        return decision


# Example usage
def main():
    """Example usage of Energy Trading System"""

    # Initialize trading system
    trading_system = EnergyTradingSystem(
        organization_id="TRADER-001",
        iso="CAISO"
    )

    print(f"\n=== Energy Trading System ===")
    print(f"Organization: {trading_system.organization_id}")
    print(f"ISO/RTO: {trading_system.iso}")

    # Register generation assets
    solar_farm = GenerationAsset(
        asset_id="SOLAR-001",
        asset_name="Desert Solar Farm",
        capacity_mw=50.0,
        min_output_mw=0.0,
        ramp_rate_mw_per_min=50.0,  # Solar can ramp quickly
        marginal_cost_per_mwh=0.0,  # Near-zero marginal cost
        startup_cost=0.0,
        shutdown_cost=0.0,
        node_id="CAISO-SP15"
    )

    trading_system.register_asset(solar_farm)

    # Forecast day-ahead prices
    forecast_date = datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)
    price_forecast = trading_system.forecast_day_ahead_prices(
        node_id="CAISO-SP15",
        forecast_date=forecast_date
    )

    print(f"\n=== Day-Ahead Price Forecast ===")
    print(f"Date: {forecast_date.date()}")
    print(f"Node: CAISO-SP15")

    # Show peak hours
    peak_hours = [p for p in price_forecast if p.lmp_dollars_per_mwh > 40]
    if peak_hours:
        print(f"Peak hours: {len(peak_hours)}")
        for price in peak_hours[:3]:
            print(f"  {price.timestamp.strftime('%H:00')}: ${price.lmp_dollars_per_mwh:.2f}/MWh")

    # Optimize and submit day-ahead bid
    bid = trading_system.optimize_day_ahead_bid(solar_farm, price_forecast)
    trading_system.submit_bid(bid)

    print(f"\n=== Market Bid Submitted ===")
    print(f"Bid ID: {bid.bid_id}")
    print(f"Asset: {solar_farm.asset_name}")
    print(f"Market: {bid.market_type.value}")
    print(f"Trading Intervals: {len(bid.trading_intervals)}")

    # Simulate market clearing
    clearing_prices = [p.lmp_dollars_per_mwh for p in price_forecast]
    accepted_quantities = [q * 0.9 for q in bid.quantities_mw]  # 90% acceptance

    trading_system.process_market_results(bid, clearing_prices, accepted_quantities)

    # Calculate portfolio risk
    risk_metrics = trading_system.calculate_portfolio_risk()

    print(f"\n=== Portfolio Risk Metrics ===")
    print(f"Net Position: {risk_metrics['net_position_mwh']:.1f} MWh")
    print(f"Position Risk: ${risk_metrics['position_risk_dollars']:.2f}")

    # REC trading example
    rec_decision = trading_system.optimize_renewable_energy_credit_trading(
        rec_inventory=1000,
        rec_price_forecast=45.0,
        compliance_target=1500
    )

if __name__ == "__main__":
    main()
```

## Key Concepts

### Locational Marginal Price (LMP)
Price of electricity at specific location, consisting of:
- **Energy Component**: Generation cost
- **Congestion Component**: Transmission constraints
- **Loss Component**: Transmission losses

### Ancillary Services
- **Regulation**: Fast response to frequency deviations
- **Spinning Reserve**: Online capacity ready within 10 minutes
- **Non-Spinning Reserve**: Offline capacity ready within 10-30 minutes
- **Voltage Support**: Reactive power for voltage stability

## Key Performance Indicators

### Trading Performance
- **Profit & Loss (P&L)**: Total profit from trading
- **Win Rate**: % of profitable trades
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline

### Risk Metrics
- **Value at Risk (VaR)**: Maximum loss at confidence level
- **Position Limits**: Maximum MW position
- **Price Exposure**: Sensitivity to price changes

## Industry Resources

### Market Operators
- [CAISO](http://www.caiso.com/)
- [ERCOT](http://www.ercot.com/)
- [PJM](https://www.pjm.com/)
- [NYISO](https://www.nyiso.com/)

### Trading Platforms
- **ICE**: Intercontinental Exchange
- **CME**: Chicago Mercantile Exchange
- **Nodal Exchange**: Power and gas trading

## Conclusion

Energy Trading & Markets require deep understanding of power systems, market rules, risk management, and quantitative trading strategies. Success requires real-time data processing, accurate forecasting, and automated execution systems that operate 24/7 in fast-moving markets.
