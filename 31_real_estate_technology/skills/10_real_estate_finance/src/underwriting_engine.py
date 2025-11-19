"""Automated Underwriting Engine"""

class UnderwritingEngine:
    def __init__(self):
        self.decision_rules = self.load_rules()
        
    def evaluate_loan(self, application):
        """Evaluate loan application"""
        findings = {
            'dti': self.calculate_dti(application),
            'ltv': self.calculate_ltv(application),
            'credit_score': application['credit_score'],
            'reserves': self.calculate_reserves(application)
        }
        
        decision = self.make_decision(findings, application['loan_type'])
        
        return {
            'decision': decision,  # approve, deny, refer
            'findings': findings,
            'conditions': self.get_conditions(findings)
        }
        
    def calculate_dti(self, app):
        """Calculate debt-to-income ratio"""
        monthly_income = app['gross_monthly_income']
        monthly_debts = app['monthly_debts']
        monthly_housing = app['proposed_payment']
        
        total_debt = monthly_debts + monthly_housing
        dti = (total_debt / monthly_income) * 100
        
        return round(dti, 2)
        
    def calculate_ltv(self, app):
        """Calculate loan-to-value"""
        loan_amount = app['loan_amount']
        appraised_value = app['appraised_value']
        
        ltv = (loan_amount / appraised_value) * 100
        return round(ltv, 2)
        
    def calculate_reserves(self, app):
        """Calculate months of reserves"""
        liquid_assets = app['liquid_assets']
        monthly_payment = app['proposed_payment']
        
        return liquid_assets / monthly_payment
        
    def make_decision(self, findings, loan_type):
        """Automated underwriting decision"""
        rules = self.decision_rules[loan_type]
        
        # Check all criteria
        if findings['credit_score'] < rules['min_credit']:
            return 'deny'
            
        if findings['dti'] > rules['max_dti']:
            return 'deny'
            
        if findings['ltv'] > rules['max_ltv']:
            return 'deny'
            
        if findings['reserves'] < rules['min_reserves']:
            return 'refer'  # Manual review
            
        return 'approve'
        
    def load_rules(self):
        """Load underwriting rules by loan type"""
        return {
            'conventional': {
                'min_credit': 620,
                'max_dti': 43,
                'max_ltv': 97,
                'min_reserves': 2
            },
            'fha': {
                'min_credit': 580,
                'max_dti': 43,
                'max_ltv': 96.5,
                'min_reserves': 0
            },
            'va': {
                'min_credit': 580,
                'max_dti': 41,
                'max_ltv': 100,
                'min_reserves': 0
            }
        }
        
    def get_conditions(self, findings):
        """Get approval conditions"""
        conditions = []
        
        if findings['reserves'] < 6:
            conditions.append('Provide additional asset documentation')
            
        if findings['credit_score'] < 680:
            conditions.append('Provide letter of explanation for recent inquiries')
            
        return conditions
