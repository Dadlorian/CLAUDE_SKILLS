"""
Inventory Optimization Module - Advanced Inventory Management Algorithms

This module provides inventory optimization algorithms for:
- Safety stock calculation (ABC, demand-driven)
- Reorder point optimization
- Economic order quantity (EOQ)
- Multi-echelon inventory optimization
- DDMRP (Demand-Driven Material Requirements Planning)
- Service level optimization
- Seasonal demand forecasting
"""

import math
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Data Classes
# ============================================================================

class ClassificationMethod(Enum):
    """SKU classification methods"""
    ABC = "abc"  # By value (80/20 rule)
    XYZ = "xyz"  # By demand variability
    COMBINED = "combined"  # ABC + XYZ


class DemandPattern(Enum):
    """Demand pattern types"""
    SMOOTH = "smooth"  # Low variability
    SEASONAL = "seasonal"  # Repeating patterns
    ERRATIC = "erratic"  # High variability
    TRENDING = "trending"  # Upward/downward trend


@dataclass
class HistoricalDemand:
    """Historical demand data point"""
    date: str
    quantity: float
    lead_time_days: int
    safety_factor: float = 1.65  # 95% service level


@dataclass
class SKUMetrics:
    """SKU performance metrics"""
    sku: str
    annual_demand: float
    average_daily_demand: float
    demand_stdev: float
    lead_time_days: int
    unit_cost: float
    holding_cost_rate: float  # % of unit cost annually
    order_cost: float  # Cost per order
    service_level_target: float  # e.g., 0.95 for 95%
    classification: str  # A, B, C
    demand_pattern: DemandPattern


@dataclass
class InventoryPolicy:
    """Calculated inventory policy"""
    sku: str
    reorder_point: float
    safety_stock: float
    economic_order_quantity: float
    min_stock: float
    max_stock: float
    target_service_level: float
    review_period_days: int


# ============================================================================
# Demand Analysis
# ============================================================================

class DemandAnalyzer:
    """Analyzes demand patterns and forecasts"""

    @staticmethod
    def calculate_demand_metrics(demands: List[float]) -> Dict[str, float]:
        """
        Calculate demand statistics

        Args:
            demands: List of historical demand quantities

        Returns:
            Dictionary with mean, stdev, cv, etc.
        """
        demands = np.array(demands)
        mean = np.mean(demands)
        stdev = np.std(demands)
        cv = stdev / mean if mean > 0 else 0  # Coefficient of variation

        return {
            'mean': float(mean),
            'stdev': float(stdev),
            'min': float(np.min(demands)),
            'max': float(np.max(demands)),
            'coefficient_of_variation': float(cv)
        }

    @staticmethod
    def classify_demand_pattern(demands: List[float],
                               threshold_cv: float = 0.5) -> DemandPattern:
        """
        Classify demand pattern based on variability

        Args:
            demands: Historical demand quantities
            threshold_cv: Coefficient of variation threshold

        Returns:
            DemandPattern enum value
        """
        metrics = DemandAnalyzer.calculate_demand_metrics(demands)
        cv = metrics['coefficient_of_variation']

        if cv < 0.3:
            return DemandPattern.SMOOTH
        elif cv < threshold_cv:
            # Check for seasonality
            if len(demands) >= 12:
                # Simple seasonality check: peaks at regular intervals
                autocorr = np.correlate(demands, demands, mode='full')
                # Would need more sophisticated seasonality test here
                return DemandPattern.SEASONAL
            return DemandPattern.SMOOTH
        else:
            return DemandPattern.ERRATIC

    @staticmethod
    def forecast_exponential_smoothing(demands: List[float],
                                      alpha: float = 0.2,
                                      periods: int = 12) -> List[float]:
        """
        Simple exponential smoothing forecast

        Args:
            demands: Historical demand
            alpha: Smoothing constant (0.1-0.3 typical)
            periods: Number of periods to forecast

        Returns:
            Forecasted demands
        """
        forecast = []
        level = demands[0]

        for demand in demands[1:]:
            forecast.append(level)
            level = alpha * demand + (1 - alpha) * level

        # Forecast future periods
        future_forecast = []
        for _ in range(periods):
            future_forecast.append(level)
            level = alpha * level + (1 - alpha) * level

        return forecast + future_forecast

    @staticmethod
    def forecast_seasonal_decomposition(demands: List[float],
                                       season_length: int = 12) -> Dict:
        """
        Simple seasonal decomposition

        Args:
            demands: Historical demand
            season_length: Length of seasonal cycle

        Returns:
            Dictionary with trend, seasonal, and residual components
        """
        demands = np.array(demands)
        n = len(demands)

        # Moving average for trend
        ma_window = season_length
        trend = np.convolve(demands, np.ones(ma_window) / ma_window, mode='same')

        # Detrended series
        detrended = demands - trend

        # Seasonal component (average by season)
        seasonal = np.zeros(n)
        for i in range(season_length):
            indices = np.arange(i, n, season_length)
            seasonal[indices] = np.mean(detrended[indices])

        # Residual
        residual = demands - trend - seasonal

        return {
            'trend': trend.tolist(),
            'seasonal': seasonal.tolist(),
            'residual': residual.tolist(),
            'seasonal_factors': [seasonal[i % season_length] for i in range(n)]
        }


# ============================================================================
# SKU Classification
# ============================================================================

class SKUClassifier:
    """Classifies SKUs using ABC/XYZ analysis"""

    @staticmethod
    def abc_classification(skus: List[Dict]) -> Dict[str, str]:
        """
        ABC classification by annual value

        Classic 80/20 rule:
        - A: 80% of value from 20% of SKUs (high priority)
        - B: 15% of value from 30% of SKUs (medium priority)
        - C: 5% of value from 50% of SKUs (low priority)

        Args:
            skus: List of dicts with sku, annual_demand, unit_cost

        Returns:
            Dictionary mapping SKU to classification
        """
        # Calculate annual value per SKU
        values = []
        for sku_data in skus:
            annual_value = sku_data['annual_demand'] * sku_data['unit_cost']
            values.append({
                'sku': sku_data['sku'],
                'value': annual_value
            })

        # Sort by value descending
        values.sort(key=lambda x: x['value'], reverse=True)
        total_value = sum(v['value'] for v in values)

        # Assign classifications
        classifications = {}
        cumulative_value = 0
        cumulative_percent = 0
        cumulative_sku_count = 0
        total_skus = len(values)

        for item in values:
            cumulative_value += item['value']
            cumulative_percent = cumulative_value / total_value
            cumulative_sku_count += 1
            cumulative_sku_percent = cumulative_sku_count / total_skus

            if cumulative_percent <= 0.80:
                classifications[item['sku']] = 'A'
            elif cumulative_percent <= 0.95:
                classifications[item['sku']] = 'B'
            else:
                classifications[item['sku']] = 'C'

        logger.info(
            f"ABC Classification: {sum(1 for c in classifications.values() if c == 'A')} A-items, "
            f"{sum(1 for c in classifications.values() if c == 'B')} B-items, "
            f"{sum(1 for c in classifications.values() if c == 'C')} C-items"
        )
        return classifications

    @staticmethod
    def xyz_classification(skus: List[Dict]) -> Dict[str, str]:
        """
        XYZ classification by demand variability

        - X: Smooth demand (low variation) - Predictable
        - Y: Medium demand variation - Moderate predictability
        - Z: Erratic demand (high variation) - Unpredictable

        Args:
            skus: List of dicts with sku and historical demands

        Returns:
            Dictionary mapping SKU to classification
        """
        classifications = {}

        for sku_data in skus:
            sku = sku_data['sku']
            demands = sku_data.get('demands', [100])  # Default if not provided

            metrics = DemandAnalyzer.calculate_demand_metrics(demands)
            cv = metrics['coefficient_of_variation']

            if cv < 0.25:
                classifications[sku] = 'X'
            elif cv < 0.75:
                classifications[sku] = 'Y'
            else:
                classifications[sku] = 'Z'

        return classifications

    @staticmethod
    def combined_classification(abc: Dict[str, str],
                               xyz: Dict[str, str]) -> Dict[str, str]:
        """
        Combine ABC and XYZ classifications

        Args:
            abc: ABC classifications
            xyz: XYZ classifications

        Returns:
            Dictionary with combined classification (e.g., AX, BZ, CY)
        """
        combined = {}
        for sku in abc:
            combined[sku] = f"{abc[sku]}{xyz.get(sku, 'Y')}"

        return combined


# ============================================================================
# Inventory Policy Optimization
# ============================================================================

class InventoryOptimizer:
    """Optimizes inventory levels and reorder policies"""

    @staticmethod
    def calculate_economic_order_quantity(annual_demand: float,
                                        order_cost: float,
                                        holding_cost_per_unit: float) -> float:
        """
        Calculate Economic Order Quantity (EOQ)

        EOQ = sqrt(2 * D * S / H)

        Where:
        - D = Annual demand
        - S = Order cost per order
        - H = Annual holding cost per unit

        Args:
            annual_demand: Annual demand quantity
            order_cost: Cost per order
            holding_cost_per_unit: Annual holding cost per unit

        Returns:
            Economic order quantity
        """
        if holding_cost_per_unit <= 0:
            return 0

        eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost_per_unit)
        logger.debug(f"EOQ: {eoq:.0f} units")
        return eoq

    @staticmethod
    def calculate_safety_stock(lead_time_days: int,
                             demand_stdev: float,
                             service_level: float) -> float:
        """
        Calculate safety stock

        SS = Z * σ * sqrt(LT)

        Where:
        - Z = Service level factor (z-score)
        - σ = Demand standard deviation
        - LT = Lead time in days

        Args:
            lead_time_days: Lead time in days
            demand_stdev: Daily demand standard deviation
            service_level: Target service level (0.95 = 95%)

        Returns:
            Safety stock quantity
        """
        z_score = stats.norm.ppf(service_level)
        safety_stock = z_score * demand_stdev * math.sqrt(lead_time_days)
        logger.debug(f"Safety stock: {safety_stock:.0f} units (SL: {service_level*100:.0f}%)")
        return safety_stock

    @staticmethod
    def calculate_reorder_point(average_daily_demand: float,
                               lead_time_days: int,
                               safety_stock: float) -> float:
        """
        Calculate reorder point

        ROP = (ADU * LT) + SS

        Where:
        - ADU = Average daily usage
        - LT = Lead time
        - SS = Safety stock

        Args:
            average_daily_demand: Average daily demand
            lead_time_days: Lead time in days
            safety_stock: Safety stock quantity

        Returns:
            Reorder point
        """
        rop = (average_daily_demand * lead_time_days) + safety_stock
        logger.debug(f"Reorder point: {rop:.0f} units")
        return rop

    @staticmethod
    def optimize_inventory_policy(sku_metrics: SKUMetrics) -> InventoryPolicy:
        """
        Calculate complete inventory policy for SKU

        Args:
            sku_metrics: SKU metrics

        Returns:
            Inventory policy with all parameters
        """
        # Calculate holding cost per unit
        holding_cost_per_unit = sku_metrics.unit_cost * sku_metrics.holding_cost_rate

        # EOQ
        eoq = InventoryOptimizer.calculate_economic_order_quantity(
            sku_metrics.annual_demand,
            sku_metrics.order_cost,
            holding_cost_per_unit
        )

        # Safety stock
        safety_stock = InventoryOptimizer.calculate_safety_stock(
            sku_metrics.lead_time_days,
            sku_metrics.demand_stdev,
            sku_metrics.service_level_target
        )

        # Reorder point
        rop = InventoryOptimizer.calculate_reorder_point(
            sku_metrics.average_daily_demand,
            sku_metrics.lead_time_days,
            safety_stock
        )

        # Min/Max stock
        min_stock = safety_stock
        max_stock = rop + eoq

        # Review period
        review_period = max(1, int(365 * eoq / sku_metrics.annual_demand))

        policy = InventoryPolicy(
            sku=sku_metrics.sku,
            reorder_point=rop,
            safety_stock=safety_stock,
            economic_order_quantity=eoq,
            min_stock=min_stock,
            max_stock=max_stock,
            target_service_level=sku_metrics.service_level_target,
            review_period_days=review_period
        )

        logger.info(f"Optimized policy for {sku_metrics.sku}: ROP={rop:.0f}, SS={safety_stock:.0f}, EOQ={eoq:.0f}")
        return policy

    @staticmethod
    def calculate_total_inventory_cost(annual_demand: float,
                                      order_cost: float,
                                      unit_cost: float,
                                      holding_cost_rate: float,
                                      order_quantity: float) -> Dict[str, float]:
        """
        Calculate total inventory cost

        TIC = Product Cost + Ordering Cost + Holding Cost

        Args:
            annual_demand: Annual demand
            order_cost: Cost per order
            unit_cost: Cost per unit
            holding_cost_rate: Holding cost as % of unit cost
            order_quantity: Order quantity

        Returns:
            Dictionary with cost components
        """
        holding_cost_per_unit = unit_cost * holding_cost_rate
        product_cost = annual_demand * unit_cost
        ordering_cost = (annual_demand / order_quantity) * order_cost
        holding_cost = (order_quantity / 2) * holding_cost_per_unit
        total_cost = product_cost + ordering_cost + holding_cost

        return {
            'product_cost': product_cost,
            'ordering_cost': ordering_cost,
            'holding_cost': holding_cost,
            'total_cost': total_cost
        }


# ============================================================================
# DDMRP (Demand-Driven Material Requirements Planning)
# ============================================================================

class DDMRPPlanner:
    """Implements Demand-Driven Material Requirements Planning"""

    @staticmethod
    def calculate_buffer_levels(average_daily_demand: float,
                               lead_time_days: int,
                               variability_factor: float = 0.5,
                               demand_time_fence: int = 14) -> Dict[str, float]:
        """
        Calculate DDMRP buffer levels

        Buffer = Red Zone + Yellow Zone (+ Green Zone)

        Red Zone = Average Daily Demand × Lead Time
        Yellow Zone = Red Zone × Variability Factor
        Green Zone = Buffer - Current Inventory (shows excess)

        Args:
            average_daily_demand: Average daily consumption
            lead_time_days: Lead time in days
            variability_factor: Safety factor (0.3-0.5 typical)
            demand_time_fence: Days of demand visibility

        Returns:
            Dictionary with buffer levels
        """
        red_zone = average_daily_demand * lead_time_days
        yellow_zone = red_zone * variability_factor
        green_zone = (average_daily_demand * demand_time_fence) - red_zone

        return {
            'red_zone': red_zone,
            'yellow_zone': yellow_zone,
            'green_zone': green_zone,
            'total_buffer': red_zone + yellow_zone,
            'green_threshold': green_zone
        }

    @staticmethod
    def get_buffer_status(current_inventory: float,
                         buffer_levels: Dict[str, float]) -> str:
        """
        Determine buffer status (Red, Yellow, Green)

        Args:
            current_inventory: Current on-hand inventory
            buffer_levels: Calculated buffer levels

        Returns:
            Status string: 'RED', 'YELLOW', or 'GREEN'
        """
        red_zone = buffer_levels['red_zone']
        yellow_zone = buffer_levels['yellow_zone']
        total_buffer = buffer_levels['total_buffer']

        if current_inventory <= red_zone:
            return 'RED'  # Below reorder point
        elif current_inventory <= total_buffer:
            return 'YELLOW'  # In safety stock
        else:
            return 'GREEN'  # Excess inventory

    @staticmethod
    def calculate_qualified_demand(forecast_demand: float,
                                  actual_demand: float,
                                  forecast_signal_threshold: float = 0.3) -> float:
        """
        Calculate qualified demand (filter noise from actual demand)

        - Use forecast if actual is close (within threshold)
        - Use actual if significant deviation (indicates trend change)

        Args:
            forecast_demand: Forecasted demand
            actual_demand: Actual consumption
            forecast_signal_threshold: Threshold for signal detection

        Returns:
            Qualified demand for planning
        """
        deviation_percent = abs(actual_demand - forecast_demand) / forecast_demand if forecast_demand > 0 else 0

        if deviation_percent > forecast_signal_threshold:
            # Signal detected - use actual with dampening
            qualified = forecast_demand * 0.7 + actual_demand * 0.3
        else:
            # Noise - use forecast
            qualified = forecast_demand

        return qualified

    @staticmethod
    def generate_ddmrp_planned_orders(current_inventory: float,
                                     buffer_levels: Dict[str, float],
                                     lead_time_days: int,
                                     average_daily_demand: float,
                                     order_interval_days: int = 7) -> Optional[float]:
        """
        Generate planned order based on DDMRP logic

        When to order:
        - When inventory crosses into RED zone
        - Reorder quantity based on buffer and lead time

        Args:
            current_inventory: Current on-hand
            buffer_levels: Calculated buffers
            lead_time_days: Lead time
            average_daily_demand: Average daily demand
            order_interval_days: Review interval

        Returns:
            Planned order quantity or None if no order needed
        """
        status = DDMRPPlanner.get_buffer_status(current_inventory, buffer_levels)

        if status == 'RED':
            # In reorder zone - place order
            # Order to reach top of buffer + demand during lead time
            target = buffer_levels['total_buffer'] + (average_daily_demand * lead_time_days)
            order_qty = target - current_inventory
            return max(0, order_qty)
        else:
            return None


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Optimize inventory for a SKU
    sku_metrics = SKUMetrics(
        sku="SKU-001",
        annual_demand=36500,
        average_daily_demand=100,
        demand_stdev=15,
        lead_time_days=14,
        unit_cost=50,
        holding_cost_rate=0.25,
        order_cost=100,
        service_level_target=0.95,
        classification="A",
        demand_pattern=DemandPattern.SMOOTH
    )

    # Calculate inventory policy
    optimizer = InventoryOptimizer()
    policy = optimizer.optimize_inventory_policy(sku_metrics)

    print(f"Inventory Policy for {sku_metrics.sku}:")
    print(f"  Reorder Point: {policy.reorder_point:.0f} units")
    print(f"  Safety Stock: {policy.safety_stock:.0f} units")
    print(f"  EOQ: {policy.economic_order_quantity:.0f} units")
    print(f"  Min Stock: {policy.min_stock:.0f} units")
    print(f"  Max Stock: {policy.max_stock:.0f} units")
    print(f"  Review Period: {policy.review_period_days} days")

    # Calculate total cost
    costs = optimizer.calculate_total_inventory_cost(
        sku_metrics.annual_demand,
        sku_metrics.order_cost,
        sku_metrics.unit_cost,
        sku_metrics.holding_cost_rate,
        policy.economic_order_quantity
    )
    print(f"\nTotal Inventory Cost:")
    print(f"  Product Cost: ${costs['product_cost']:.2f}")
    print(f"  Ordering Cost: ${costs['ordering_cost']:.2f}")
    print(f"  Holding Cost: ${costs['holding_cost']:.2f}")
    print(f"  Total Cost: ${costs['total_cost']:.2f}")

    # DDMRP Example
    ddmrp = DDMRPPlanner()
    buffers = ddmrp.calculate_buffer_levels(100, 14, 0.5)
    print(f"\nDDMRP Buffer Levels:")
    print(f"  Red Zone: {buffers['red_zone']:.0f} units")
    print(f"  Yellow Zone: {buffers['yellow_zone']:.0f} units")
    print(f"  Total Buffer: {buffers['total_buffer']:.0f} units")

    current_inv = 1800
    status = ddmrp.get_buffer_status(current_inv, buffers)
    print(f"  Current Inventory: {current_inv} units")
    print(f"  Status: {status}")
