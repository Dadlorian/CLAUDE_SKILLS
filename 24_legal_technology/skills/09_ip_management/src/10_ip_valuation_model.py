"""
IP Valuation Model Example
Calculates IP asset value using multiple approaches
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import math

class ValuationMethod(Enum):
    """IP valuation methods"""
    COST_APPROACH = "cost"
    MARKET_APPROACH = "market"
    INCOME_APPROACH = "income"
    RELIEF_FROM_ROYALTY = "royalty"

@dataclass
class ValuationInput:
    """Input data for valuation"""
    asset_id: str
    asset_type: str  # patent, trademark, copyright
    acquisition_cost: Optional[float] = None
    prosecution_costs: Optional[float] = None
    maintenance_costs_annual: Optional[float] = None
    years_remaining: Optional[int] = None
    estimated_annual_revenue: Optional[float] = None
    projected_revenue_growth: Optional[float] = None  # percentage per year
    royalty_rate: Optional[float] = None  # as decimal, e.g., 0.03 for 3%
    discount_rate: Optional[float] = None  # WACC or required return
    comparable_sale_price: Optional[float] = None

@dataclass
class ValuationResult:
    """Results of valuation analysis"""
    asset_id: str
    cost_approach_value: Optional[float]
    market_approach_value: Optional[float]
    income_approach_value: Optional[float]
    relief_from_royalty_value: Optional[float]
    recommended_value: float
    valuation_range_low: float
    valuation_range_high: float
    confidence_level: str  # Low, Medium, High

class IPValuationModel:
    """Calculate IP asset valuations"""

    def __init__(self):
        self.discount_rate = 0.15  # 15% default WACC
        self.inflation_rate = 0.03  # 3% default inflation

    def calculate_valuation(self, inputs: ValuationInput) -> ValuationResult:
        """
        Calculate IP valuation using multiple approaches

        Args:
            inputs: ValuationInput with asset and financial data

        Returns:
            ValuationResult with multiple valuations
        """
        cost_value = self._cost_approach(inputs)
        market_value = self._market_approach(inputs)
        income_value = self._income_approach(inputs)
        royalty_value = self._relief_from_royalty(inputs)

        # Calculate weighted average of available methods
        values = [v for v in [cost_value, market_value, income_value, royalty_value] if v is not None]

        if not values:
            recommended_value = 0.0
            confidence = "Low"
        else:
            # Weight by method reliability (income approach weighted higher)
            weights = []
            if royalty_value is not None:
                weights.append((royalty_value, 0.35))  # Most reliable
            if income_value is not None:
                weights.append((income_value, 0.30))
            if market_value is not None:
                weights.append((market_value, 0.20))
            if cost_value is not None:
                weights.append((cost_value, 0.15))

            total_weight = sum(w[1] for w in weights)
            recommended_value = sum(v * (w / total_weight) for v, w in weights)

            # Determine confidence level
            if len(values) >= 3:
                confidence = "High"
            elif len(values) >= 2:
                confidence = "Medium"
            else:
                confidence = "Low"

        # Calculate range
        low_range = recommended_value * 0.70
        high_range = recommended_value * 1.30

        return ValuationResult(
            asset_id=inputs.asset_id,
            cost_approach_value=cost_value,
            market_approach_value=market_value,
            income_approach_value=income_value,
            relief_from_royalty_value=royalty_value,
            recommended_value=recommended_value,
            valuation_range_low=low_range,
            valuation_range_high=high_range,
            confidence_level=confidence
        )

    def _cost_approach(self, inputs: ValuationInput) -> Optional[float]:
        """
        Cost approach: sum of all costs to develop the asset
        """
        if not inputs.acquisition_cost:
            return None

        total_cost = inputs.acquisition_cost

        if inputs.prosecution_costs:
            total_cost += inputs.prosecution_costs

        # Add maintenance costs (present value)
        if inputs.maintenance_costs_annual and inputs.years_remaining:
            pv_maintenance = self._calculate_present_value_annuity(
                inputs.maintenance_costs_annual,
                inputs.years_remaining,
                self.discount_rate
            )
            total_cost += pv_maintenance

        return total_cost

    def _market_approach(self, inputs: ValuationInput) -> Optional[float]:
        """
        Market approach: based on comparable transactions
        """
        if not inputs.comparable_sale_price:
            return None

        # Could adjust for age, technology relevance, etc.
        return inputs.comparable_sale_price

    def _income_approach(self, inputs: ValuationInput) -> Optional[float]:
        """
        Income approach: NPV of projected cash flows from the asset
        """
        if not inputs.estimated_annual_revenue or not inputs.years_remaining:
            return None

        cash_flows = []
        revenue = inputs.estimated_annual_revenue
        growth_rate = inputs.projected_revenue_growth or self.inflation_rate

        # Project cash flows
        for year in range(1, inputs.years_remaining + 1):
            # Apply growth rate
            year_revenue = revenue * math.pow(1 + growth_rate, year - 1)

            # Discount to present value
            pv = year_revenue / math.pow(1 + self.discount_rate, year)
            cash_flows.append(pv)

        return sum(cash_flows)

    def _relief_from_royalty(self, inputs: ValuationInput) -> Optional[float]:
        """
        Relief from royalty: value of avoiding royalty payments
        """
        if not inputs.estimated_annual_revenue or not inputs.royalty_rate or not inputs.years_remaining:
            return None

        # Calculate royalty savings
        annual_royalty = inputs.estimated_annual_revenue * inputs.royalty_rate
        growth_rate = inputs.projected_revenue_growth or self.inflation_rate

        cash_flows = []
        for year in range(1, inputs.years_remaining + 1):
            year_royalty = annual_royalty * math.pow(1 + growth_rate, year - 1)
            pv = year_royalty / math.pow(1 + self.discount_rate, year)
            cash_flows.append(pv)

        return sum(cash_flows)

    def _calculate_present_value_annuity(self, annual_amount: float,
                                        years: int, discount_rate: float) -> float:
        """Calculate present value of an annuity"""
        if discount_rate == 0:
            return annual_amount * years

        factor = (1 - math.pow(1 + discount_rate, -years)) / discount_rate
        return annual_amount * factor

    def sensitivity_analysis(self, base_inputs: ValuationInput,
                           variable_name: str,
                           variation_range: float = 0.25) -> Dict:
        """
        Perform sensitivity analysis on a variable
        Shows how valuation changes with variable changes

        Args:
            base_inputs: Base case inputs
            variable_name: Variable to test (e.g., 'royalty_rate')
            variation_range: Range of variation (e.g., 0.25 for +/- 25%)

        Returns:
            Dictionary of sensitivity results
        """
        results = {}

        # Get base value
        base_result = self.calculate_valuation(base_inputs)
        results['base_case'] = base_result.recommended_value

        # Test variations
        for variation in [-variation_range, -variation_range/2, 0, variation_range/2, variation_range]:
            test_inputs = ValuationInput(**vars(base_inputs))

            # Apply variation to specified variable
            if hasattr(test_inputs, variable_name):
                current_value = getattr(test_inputs, variable_name)
                if current_value is not None:
                    adjusted_value = current_value * (1 + variation)
                    setattr(test_inputs, variable_name, adjusted_value)

                    test_result = self.calculate_valuation(test_inputs)
                    key = f"{variable_name}_{variation:+.1%}"
                    results[key] = test_result.recommended_value

        return results


# Example usage
if __name__ == "__main__":
    valuator = IPValuationModel()

    # Patent valuation example
    patent_inputs = ValuationInput(
        asset_id="US7123456",
        asset_type="patent",
        acquisition_cost=50000,
        prosecution_costs=30000,
        maintenance_costs_annual=2000,
        years_remaining=10,
        estimated_annual_revenue=1000000,
        projected_revenue_growth=0.05,
        royalty_rate=0.03,
        discount_rate=0.15
    )

    valuation = valuator.calculate_valuation(patent_inputs)
    print(f"Patent Valuation: ${valuation.recommended_value:,.0f}")
    print(f"Range: ${valuation.valuation_range_low:,.0f} - ${valuation.valuation_range_high:,.0f}")
    print(f"Confidence: {valuation.confidence_level}")

    # Sensitivity analysis
    sensitivity = valuator.sensitivity_analysis(patent_inputs, 'royalty_rate', 0.25)
    print("\nSensitivity Analysis (Royalty Rate):")
    for scenario, value in sensitivity.items():
        print(f"  {scenario}: ${value:,.0f}")
