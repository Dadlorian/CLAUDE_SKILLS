"""Drift Analyzer - Monitors portfolio allocation drift"""
from typing import Dict


class DriftAnalyzer:
    """Analyzes portfolio drift from target allocation"""

    def calculate_drift(self, current_weights: Dict, target_weights: Dict) -> Dict:
        """Calculate allocation drift"""
        drift = {}
        max_drift = 0

        for asset, target in target_weights.items():
            current = current_weights.get(asset, 0)
            asset_drift = abs(current - target)
            drift[asset] = asset_drift
            max_drift = max(max_drift, asset_drift)

        return {
            'asset_drifts': drift,
            'max_drift': max_drift,
            'requires_rebalancing': max_drift > 0.05
        }

    def drift_analysis_report(self, current_weights: Dict,
                             target_weights: Dict) -> Dict:
        """Generate drift analysis report"""
        drift_data = self.calculate_drift(current_weights, target_weights)

        return {
            'summary': f"Portfolio drift: {drift_data['max_drift']*100:.1f}%",
            'details': drift_data['asset_drifts'],
            'recommendation': 'REBALANCE' if drift_data['requires_rebalancing'] else 'HOLD',
            'urgent': drift_data['max_drift'] > 0.10
        }
