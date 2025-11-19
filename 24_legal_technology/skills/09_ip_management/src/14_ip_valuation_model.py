"""
Advanced IP Valuation Model Example
Comprehensive valuation using financial methods and risk analysis
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import math


class IPAssetType(Enum):
    """IP asset types"""
    PATENT = "patent"
    TRADEMARK = "trademark"
    COPYRIGHT = "copyright"
    TRADE_SECRET = "trade_secret"
    DOMAIN_NAME = "domain_name"


class RiskLevel(Enum):
    """Risk levels for assets"""
    LOW = 1.0
    MODERATE = 0.9
    MEDIUM = 0.75
    HIGH = 0.6
    VERY_HIGH = 0.4


@dataclass
class IPAsset:
    """IP asset for valuation"""
    asset_id: str
    asset_type: IPAssetType
    acquisition_date: datetime
    acquisition_cost: float
    annual_maintenance_cost: float
    expected_life_years: int
    related_revenue: float  # Annual revenue attributable to asset
    jurisdiction: List[str]
    risk_level: RiskLevel


@dataclass
class ValuationScenario:
    """Valuation scenario parameters"""
    discount_rate: float  # WACC
    revenue_growth_rate: float
    inflation_rate: float
    risk_multiplier: float = 1.0


class AdvancedIPValuationModel:
    """Advanced IP valuation with multiple approaches"""

    def __init__(self, discount_rate: float = 0.12):
        self.discount_rate = discount_rate
        self.inflation_rate = 0.025
        self.results_cache = {}

    def valuate_asset(self, asset: IPAsset, scenario: ValuationScenario) -> Dict:
        """
        Perform comprehensive valuation of IP asset

        Args:
            asset: IP asset to valuate
            scenario: Valuation scenario parameters

        Returns:
            Dictionary with valuation results
        """
        results = {
            'asset_id': asset.asset_id,
            'asset_type': asset.asset_type.value,
            'valuation_date': datetime.now().isoformat(),
            'scenario': {
                'discount_rate': scenario.discount_rate,
                'revenue_growth': scenario.revenue_growth_rate,
                'risk_multiplier': scenario.risk_multiplier
            }
        }

        # Calculate valuations using different methods
        income_value = self._income_approach(asset, scenario)
        market_value = self._market_comparable_approach(asset, scenario)
        cost_value = self._cost_approach(asset, scenario)
        relief_value = self._relief_from_royalty(asset, scenario)

        # Aggregate valuations
        valuations = {
            'income_approach': income_value,
            'market_approach': market_value,
            'cost_approach': cost_value,
            'relief_from_royalty': relief_value
        }

        results['valuations'] = valuations

        # Calculate recommended value using weighted average
        weights = self._get_weights_for_asset_type(asset.asset_type)
        weighted_values = []

        for method, value in valuations.items():
            if value is not None:
                method_weight = weights.get(method, 0.25)
                weighted_values.append((value, method_weight))

        if weighted_values:
            total_weight = sum(w[1] for w in weighted_values)
            recommended_value = sum(v * (w / total_weight) for v, w in weighted_values)
        else:
            recommended_value = 0

        # Apply risk adjustment
        risk_adjusted_value = recommended_value * asset.risk_level.value * scenario.risk_multiplier

        results['recommended_value'] = recommended_value
        results['risk_adjusted_value'] = risk_adjusted_value
        results['valuation_range'] = {
            'low': risk_adjusted_value * 0.70,
            'high': risk_adjusted_value * 1.30,
            'midpoint': risk_adjusted_value
        }

        # Calculate additional metrics
        results['additional_metrics'] = self._calculate_additional_metrics(asset, scenario)

        return results

    def _income_approach(self, asset: IPAsset, scenario: ValuationScenario) -> Optional[float]:
        """
        Calculate value using income approach (DCF)

        Returns:
            NPV of projected cash flows
        """
        if asset.related_revenue <= 0:
            return None

        npv = 0
        revenue = asset.related_revenue

        for year in range(1, asset.expected_life_years + 1):
            # Project revenue with growth rate
            projected_revenue = revenue * math.pow(1 + scenario.revenue_growth_rate, year - 1)

            # Discount to present value
            discount_factor = math.pow(1 + scenario.discount_rate, year)
            pv = projected_revenue / discount_factor

            npv += pv

        return npv

    def _cost_approach(self, asset: IPAsset, scenario: ValuationScenario) -> Optional[float]:
        """
        Calculate value using cost approach

        Returns:
            Total cost to acquire and maintain
        """
        total_cost = asset.acquisition_cost

        # Add present value of maintenance costs
        annual_maintenance = asset.annual_maintenance_cost
        for year in range(1, asset.expected_life_years + 1):
            adjusted_cost = annual_maintenance * math.pow(1 + scenario.inflation_rate, year - 1)
            discount_factor = math.pow(1 + scenario.discount_rate, year)
            pv = adjusted_cost / discount_factor
            total_cost += pv

        return total_cost

    def _market_comparable_approach(self, asset: IPAsset, scenario: ValuationScenario) -> Optional[float]:
        """
        Calculate value using market comparable approach

        Returns:
            Market-based valuation
        """
        # This would typically use actual market data
        # For now, return None if no data available
        if asset.related_revenue <= 0:
            return None

        # Typical market multiples for IP (simplified)
        multiples = {
            IPAssetType.PATENT: 2.5,
            IPAssetType.TRADEMARK: 3.5,
            IPAssetType.COPYRIGHT: 2.0,
            IPAssetType.TRADE_SECRET: 2.0,
            IPAssetType.DOMAIN_NAME: 1.5
        }

        multiple = multiples.get(asset.asset_type, 2.0)
        return asset.related_revenue * multiple * scenario.risk_multiplier

    def _relief_from_royalty(self, asset: IPAsset, scenario: ValuationScenario) -> Optional[float]:
        """
        Calculate value using relief from royalty method

        Returns:
            Value based on avoided royalty payments
        """
        if asset.related_revenue <= 0:
            return None

        # Typical royalty rates (simplified)
        royalty_rates = {
            IPAssetType.PATENT: 0.04,
            IPAssetType.TRADEMARK: 0.05,
            IPAssetType.COPYRIGHT: 0.03,
            IPAssetType.TRADE_SECRET: 0.02,
            IPAssetType.DOMAIN_NAME: 0.02
        }

        royalty_rate = royalty_rates.get(asset.asset_type, 0.03)
        annual_royalty = asset.related_revenue * royalty_rate

        # Calculate PV of royalty savings
        npv = 0
        for year in range(1, asset.expected_life_years + 1):
            projected_royalty = annual_royalty * math.pow(1 + scenario.revenue_growth_rate, year - 1)
            discount_factor = math.pow(1 + scenario.discount_rate, year)
            pv = projected_royalty / discount_factor
            npv += pv

        return npv

    def _calculate_additional_metrics(self, asset: IPAsset, scenario: ValuationScenario) -> Dict:
        """
        Calculate additional valuation metrics

        Returns:
            Dictionary with additional metrics
        """
        payback_period = asset.acquisition_cost / asset.related_revenue if asset.related_revenue > 0 else float('inf')

        # ROI calculation
        total_cash_flows = asset.related_revenue * asset.expected_life_years
        total_costs = asset.acquisition_cost + (asset.annual_maintenance_cost * asset.expected_life_years)
        roi = ((total_cash_flows - total_costs) / total_costs) * 100 if total_costs > 0 else 0

        return {
            'payback_period_years': min(payback_period, asset.expected_life_years),
            'estimated_roi_percent': roi,
            'total_lifetime_cash_flows': total_cash_flows,
            'total_lifetime_costs': total_costs,
            'maintenance_cost_ratio': asset.annual_maintenance_cost / asset.related_revenue if asset.related_revenue > 0 else 0
        }

    def _get_weights_for_asset_type(self, asset_type: IPAssetType) -> Dict[str, float]:
        """Get valuation method weights based on asset type"""
        weights = {
            IPAssetType.PATENT: {
                'income_approach': 0.40,
                'market_approach': 0.30,
                'relief_from_royalty': 0.20,
                'cost_approach': 0.10
            },
            IPAssetType.TRADEMARK: {
                'income_approach': 0.35,
                'market_approach': 0.40,
                'relief_from_royalty': 0.15,
                'cost_approach': 0.10
            },
            IPAssetType.COPYRIGHT: {
                'income_approach': 0.45,
                'market_approach': 0.25,
                'relief_from_royalty': 0.20,
                'cost_approach': 0.10
            }
        }

        return weights.get(asset_type, {
            'income_approach': 0.35,
            'market_approach': 0.35,
            'relief_from_royalty': 0.20,
            'cost_approach': 0.10
        })

    def perform_sensitivity_analysis(self, asset: IPAsset, scenario: ValuationScenario,
                                     parameters: List[str]) -> Dict:
        """
        Perform sensitivity analysis on valuation

        Args:
            asset: IP asset
            scenario: Valuation scenario
            parameters: Parameters to test ('discount_rate', 'revenue_growth', etc.)

        Returns:
            Sensitivity analysis results
        """
        base_valuation = self.valuate_asset(asset, scenario)
        base_value = base_valuation['risk_adjusted_value']

        sensitivity_results = {
            'base_case': base_value,
            'sensitivities': {}
        }

        for param in parameters:
            param_sensitivity = {}

            for change in [-0.20, -0.10, 0, 0.10, 0.20]:
                test_scenario = ValuationScenario(
                    discount_rate=scenario.discount_rate if param != 'discount_rate' else scenario.discount_rate * (1 + change),
                    revenue_growth_rate=scenario.revenue_growth_rate if param != 'revenue_growth' else scenario.revenue_growth_rate * (1 + change),
                    inflation_rate=scenario.inflation_rate,
                    risk_multiplier=scenario.risk_multiplier
                )

                test_valuation = self.valuate_asset(asset, test_scenario)
                value = test_valuation['risk_adjusted_value']
                change_percent = ((value - base_value) / base_value) * 100

                param_sensitivity[f"{change:+.0%}"] = {
                    'value': value,
                    'change_percent': change_percent
                }

            sensitivity_results['sensitivities'][param] = param_sensitivity

        return sensitivity_results


# Example usage
if __name__ == "__main__":
    # Create valuation model
    model = AdvancedIPValuationModel()

    # Define asset
    patent = IPAsset(
        asset_id="US7234567",
        asset_type=IPAssetType.PATENT,
        acquisition_date=datetime(2015, 1, 1),
        acquisition_cost=150000,
        annual_maintenance_cost=5000,
        expected_life_years=10,
        related_revenue=500000,
        jurisdiction=["US", "EU", "JP"],
        risk_level=RiskLevel.MODERATE
    )

    # Define valuation scenario
    scenario = ValuationScenario(
        discount_rate=0.12,
        revenue_growth_rate=0.08,
        inflation_rate=0.025,
        risk_multiplier=1.0
    )

    # Perform valuation
    valuation = model.valuate_asset(patent, scenario)
    print("IP Asset Valuation Report")
    print(f"Asset: {valuation['asset_id']}")
    print(f"Recommended Value: ${valuation['recommended_value']:,.0f}")
    print(f"Risk Adjusted Value: ${valuation['risk_adjusted_value']:,.0f}")
    print(f"Valuation Range: ${valuation['valuation_range']['low']:,.0f} - ${valuation['valuation_range']['high']:,.0f}")
