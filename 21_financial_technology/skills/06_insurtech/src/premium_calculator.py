"""Premium calculation with rating factors"""
from typing import Dict

class PremiumCalculator:
    def __init__(self):
        self.base_rates = {
            'auto': 1200,
            'home': 1500,
            'health': 300
        }
    
    def calculate_premium(self, product: str, risk_factors: Dict) -> float:
        """Calculate final premium"""
        base_rate = self.base_rates.get(product, 1000)
        
        # Apply rating factors
        factor = self._calculate_factor(risk_factors)
        
        # Add loading
        loading = 0.15  # 15% for expenses, profit
        
        premium = base_rate * factor * (1 + loading)
        
        # Apply discounts
        discounts = self._calculate_discounts(risk_factors)
        premium = premium * (1 - discounts)
        
        return round(premium, 2)
    
    def _calculate_factor(self, risk_factors: Dict) -> float:
        """Calculate rating factor"""
        factor = 1.0
        
        if risk_factors.get('age', 0) < 25:
            factor *= 1.5
        elif risk_factors.get('age', 0) > 65:
            factor *= 1.1
        
        factor *= (1 + 0.2 * risk_factors.get('claims', 0))
        
        return factor
    
    def _calculate_discounts(self, risk_factors: Dict) -> float:
        """Calculate total discounts"""
        discounts = 0.0
        
        if risk_factors.get('multi_policy'):
            discounts += 0.10
        if risk_factors.get('safe_driver'):
            discounts += 0.15
        if risk_factors.get('automatic_payment'):
            discounts += 0.05
        
        return min(discounts, 0.30)

if __name__ == "__main__":
    calc = PremiumCalculator()
    premium = calc.calculate_premium('auto', {'age': 35, 'safe_driver': True})
    print(f"Premium: ${premium}")
