"""
Limit Monitoring System

Monitors risk limits and triggers escalations.
"""

import pandas as pd
from enum import Enum


class AlertLevel(Enum):
    GREEN = 1
    YELLOW = 2
    RED = 3


class LimitMonitor:
    """Monitor risk limits and escalate breaches."""

    def __init__(self):
        self.limits = {}
        self.current_exposure = {}
        self.alerts = []

    def set_limit(self, limit_name, limit_amount, alert_thresholds=None):
        """Set a risk limit."""
        if alert_thresholds is None:
            alert_thresholds = {'yellow': 0.80, 'red': 1.00}

        self.limits[limit_name] = {
            'Amount': limit_amount,
            'Yellow_Threshold': limit_amount * alert_thresholds['yellow'],
            'Red_Threshold': limit_amount * alert_thresholds['red'],
        }

    def update_exposure(self, limit_name, exposure):
        """Update current exposure."""
        self.current_exposure[limit_name] = exposure
        self._check_limit(limit_name)

    def _check_limit(self, limit_name):
        """Check if limit is breached and generate alert."""
        if limit_name not in self.limits:
            return

        exposure = self.current_exposure.get(limit_name, 0)
        limit = self.limits[limit_name]

        if exposure > limit['Red_Threshold']:
            self._escalate(limit_name, AlertLevel.RED, exposure)
        elif exposure > limit['Yellow_Threshold']:
            self._escalate(limit_name, AlertLevel.YELLOW, exposure)
        else:
            self._escalate(limit_name, AlertLevel.GREEN, exposure)

    def _escalate(self, limit_name, level, exposure):
        """Escalate alert based on level."""
        limit_amount = self.limits[limit_name]['Amount']
        utilization = (exposure / limit_amount * 100) if limit_amount > 0 else 0

        alert = {
            'Limit': limit_name,
            'Level': level.name,
            'Exposure': exposure,
            'Limit_Amount': limit_amount,
            'Utilization_%': utilization,
        }

        self.alerts.append(alert)

        if level == AlertLevel.RED:
            print(f"RED ALERT: {limit_name} - {utilization:.1f}% utilized")
        elif level == AlertLevel.YELLOW:
            print(f"YELLOW ALERT: {limit_name} - {utilization:.1f}% utilized")

    def get_alerts(self, level=None):
        """Get all alerts, optionally filtered by level."""
        if level:
            return [a for a in self.alerts if a['Level'] == level.name]
        return self.alerts


# Example usage
if __name__ == "__main__":
    monitor = LimitMonitor()

    # Set limits
    monitor.set_limit('Counterparty_A', 100_000_000)
    monitor.set_limit('Sector_Technology', 200_000_000)
    monitor.set_limit('Daily_VaR', 50_000_000)

    # Update exposures
    monitor.update_exposure('Counterparty_A', 95_000_000)  # Yellow
    monitor.update_exposure('Sector_Technology', 210_000_000)  # Red
    monitor.update_exposure('Daily_VaR', 45_000_000)  # Green

    # Get red alerts
    red_alerts = monitor.get_alerts(AlertLevel.RED)
    print(f"\nRed Alerts: {len(red_alerts)}")
    for alert in red_alerts:
        print(f"  {alert['Limit']}: {alert['Utilization_%']:.1f}% utilized")
