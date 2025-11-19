"""Risk calculation and assessment"""
from typing import Dict

class RiskCalculator:
    def calculate_frequency(self, risk_data: Dict) -> float:
        """Calculate claim frequency"""
        base_frequency = 0.15  # 15% chance
        
        age_factor = 1.0
        if risk_data.get('age', 0) < 25:
            age_factor = 1.5
        
        history_factor = 1.0 + (risk_data.get('prior_claims', 0) * 0.3)
        
        return base_frequency * age_factor * history_factor
    
    def calculate_severity(self, risk_data: Dict) -> float:
        """Calculate expected claim severity"""
        base_severity = 5000
        
        # Adjust for vehicle value
        vehicle_value = risk_data.get('vehicle_value', 25000)
        severity = base_severity * (vehicle_value / 25000)
        
        return round(severity, 2)
    
    def calculate_expected_loss(self, risk_data: Dict) -> float:
        """Calculate expected loss"""
        frequency = self.calculate_frequency(risk_data)
        severity = self.calculate_severity(risk_data)
        return round(frequency * severity, 2)

if __name__ == "__main__":
    calculator = RiskCalculator()
    loss = calculator.calculate_expected_loss({'age': 35, 'vehicle_value': 25000})
    print(f"Expected Loss: ${loss}")
