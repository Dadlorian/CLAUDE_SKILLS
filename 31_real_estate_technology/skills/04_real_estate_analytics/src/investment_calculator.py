"""Investment Analysis Calculator"""
import numpy as np

class InvestmentAnalyzer:
    def __init__(self, property_data):
        self.data = property_data
        
    def calculate_cap_rate(self):
        """Capitalization Rate"""
        noi = self.data['annual_rent'] - self.data['annual_expenses']
        return (noi / self.data['purchase_price']) * 100
        
    def calculate_cash_on_cash(self):
        """Cash-on-Cash Return"""
        annual_cash_flow = self.data['annual_rent'] - self.data['annual_expenses'] - self.data['annual_debt_service']
        return (annual_cash_flow / self.data['cash_invested']) * 100
        
    def calculate_irr(self, years=10):
        """Internal Rate of Return"""
        cash_flows = [-self.data['cash_invested']]  # Initial investment
        
        for year in range(years):
            annual_flow = self.data['annual_rent'] - self.data['annual_expenses'] - self.data['annual_debt_service']
            cash_flows.append(annual_flow)
            
        # Add sale proceeds in final year
        sale_price = self.data['purchase_price'] * (1.03 ** years)
        cash_flows[-1] += sale_price
        
        return np.irr(cash_flows) * 100
