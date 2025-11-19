"""
Risk Calculator - Calculate multi-dimensional risk scores
"""

from typing import Dict
import numpy as np


class RiskCalculator:
    """Calculate combined risk scores"""

    @staticmethod
    def calculate_customer_risk(customer: Dict) -> float:
        """Calculate overall customer risk"""
        risk = 0.0

        # Account age
        if customer.get('account_age_days', 0) < 30:
            risk += 0.2

        # Chargeback rate
        chargeback_rate = customer.get('chargeback_rate', 0)
        if chargeback_rate > 0.05:
            risk += 0.3

        # Refund rate
        refund_rate = customer.get('refund_rate', 0)
        if refund_rate > 0.1:
            risk += 0.2

        return min(risk, 1.0)

    @staticmethod
    def calculate_device_risk(device: Dict) -> float:
        """Calculate device risk score"""
        risk = 0.0

        # Device age
        days_old = device.get('days_old', 30)
        if days_old < 1:
            risk += 0.3
        elif days_old < 7:
            risk += 0.2

        # Device fraud history
        fraud_count = device.get('fraud_count', 0)
        if fraud_count > 0:
            risk += 0.4

        # Device sharing
        customer_count = device.get('customer_count', 1)
        if customer_count > 5:
            risk += 0.3

        return min(risk, 1.0)
