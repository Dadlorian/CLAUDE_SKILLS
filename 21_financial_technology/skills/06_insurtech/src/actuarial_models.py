"""Actuarial modeling and analysis"""
from typing import Dict, List

class ActuarialModels:
    def calculate_pure_premium(self, frequency: float, severity: float) -> float:
        """Calculate pure premium"""
        return round(frequency * severity, 2)
    
    def calculate_loaded_premium(self, pure_premium: float, expense_ratio: float = 0.25) -> float:
        """Calculate loaded premium with expenses"""
        return round(pure_premium / (1 - expense_ratio), 2)
    
    def calculate_loss_ratio(self, incurred_losses: float, earned_premium: float) -> float:
        """Calculate loss ratio"""
        if earned_premium == 0:
            return 0
        return round(incurred_losses / earned_premium, 4)
    
    def calculate_combined_ratio(self, loss_ratio: float, expense_ratio: float) -> float:
        """Calculate combined ratio"""
        return round(loss_ratio + expense_ratio, 4)
