#!/usr/bin/env python3
"""
Conditional validation logic for document automation
Validate form data based on conditional requirements
"""

from typing import Dict, List, Tuple

class ConditionalValidator:
    def __init__(self):
        self.errors = []
    
    def validate_engagement_letter(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate engagement letter intake data."""
        self.errors = []
        
        # Required fields
        required_fields = ['client_name', 'matter_description', 'engagement_date', 'jurisdiction']
        for field in required_fields:
            if not data.get(field):
                self.errors.append(f"Missing required field: {field}")
        
        # Client type validation
        client_type = data.get('client_type')
        if client_type == 'business':
            if not data.get('business_name'):
                self.errors.append("Business name required for business clients")
            if not data.get('state_of_incorporation'):
                self.errors.append("State of incorporation required for business clients")
        
        elif client_type == 'individual':
            if not data.get('client_dob'):
                self.errors.append("Date of birth required for individual clients")
        
        # Fee arrangement validation
        is_contingency = data.get('is_contingency')
        
        if is_contingency:
            # Contingency-specific validations
            if not data.get('contingency_percentage'):
                self.errors.append("Contingency percentage required")
            elif not (10 <= float(data.get('contingency_percentage', 0)) <= 50):
                self.errors.append("Contingency percentage must be between 10-50%")
            
            if data.get('hourly_rate'):
                self.errors.append("Hourly rate should not be specified for contingency matters")
        
        else:
            # Hourly arrangement validations
            if not data.get('hourly_rate'):
                self.errors.append("Hourly rate required for non-contingency matters")
            elif not (50 <= float(data.get('hourly_rate', 0)) <= 1000):
                self.errors.append("Hourly rate must be between $50-$1000")
            
            if not data.get('retainer_amount'):
                self.errors.append("Retainer amount required for hourly matters")
            elif float(data.get('retainer_amount', 0)) < 500:
                self.errors.append("Retainer must be at least $500")
        
        # Cross-field validation
        if data.get('estimated_hours') and data.get('hourly_rate') and data.get('retainer_amount'):
            estimated_cost = (
                float(data.get('estimated_hours', 0)) * 
                float(data.get('hourly_rate', 0))
            )
            retainer = float(data.get('retainer_amount', 0))
            
            if retainer > estimated_cost:
                self.errors.append(
                    f"Retainer (${retainer}) should not exceed estimated cost (${estimated_cost})"
                )
        
        return len(self.errors) == 0, self.errors
    
    def validate_court_filing(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate court filing form data."""
        self.errors = []
        
        # Required fields
        required = ['case_number', 'court_name', 'filing_date', 'party_name', 'party_role']
        for field in required:
            if not data.get(field):
                self.errors.append(f"Missing required field: {field}")
        
        # Case number format validation
        import re
        case_num = data.get('case_number', '')
        if not re.match(r'^\d{2}-[CV|CR]+-\d{5}$', case_num):
            self.errors.append("Case number must be in format: YY-CV-XXXXX or YY-CR-XXXXX")
        
        # Jurisdiction-specific validations
        jurisdiction = data.get('jurisdiction', '')
        
        if jurisdiction == 'federal':
            if not data.get('federal_district'):
                self.errors.append("Federal district required for federal filings")
            if not data.get('judge_name'):
                self.errors.append("Judge name required for federal filings")
        
        elif jurisdiction == 'state':
            if not data.get('state_court'):
                self.errors.append("State court required for state filings")
            if not data.get('county'):
                self.errors.append("County required for state filings")
        
        # Local rule compliance
        if data.get('court_name'):
            local_rules = self._get_local_rules(data.get('court_name'))
            if local_rules:
                self._validate_local_rules(local_rules, data)
        
        return len(self.errors) == 0, self.errors
    
    def validate_contract_review(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate contract review intake data."""
        self.errors = []
        
        # Required fields
        if not data.get('contract_type'):
            self.errors.append("Contract type is required")
        
        if not data.get('contract_value') or float(data.get('contract_value', 0)) < 0:
            self.errors.append("Contract value must be a positive number")
        
        # Conditional date validation
        execution_date = data.get('execution_date')
        expiration_date = data.get('expiration_date')
        
        if execution_date and expiration_date:
            if expiration_date <= execution_date:
                self.errors.append("Expiration date must be after execution date")
        
        # Contract type specific validation
        contract_type = data.get('contract_type')
        
        if contract_type == 'NDA':
            if not data.get('confidentiality_duration'):
                self.errors.append("Confidentiality duration required for NDAs")
        
        elif contract_type == 'Employment':
            if not data.get('position_title'):
                self.errors.append("Position title required for employment contracts")
            if not data.get('start_date'):
                self.errors.append("Start date required for employment contracts")
        
        elif contract_type == 'Lease':
            if not data.get('property_address'):
                self.errors.append("Property address required for leases")
            if not data.get('monthly_rent'):
                self.errors.append("Monthly rent amount required for leases")
        
        return len(self.errors) == 0, self.errors
    
    def _get_local_rules(self, court_name: str) -> Dict:
        """Get local rules for specific court."""
        # This would be a database lookup in real implementation
        local_rules_db = {
            'U.S. District Court, N.D. Cal.': {
                'max_page_limit': 15,
                'font_requirement': '12pt Times New Roman',
                'margin_requirement': '1 inch',
                'electronic_filing': True
            },
            'California Superior Court': {
                'max_page_limit': 10,
                'font_requirement': '12pt',
                'margin_requirement': '1 inch',
                'local_forms': True
            }
        }
        return local_rules_db.get(court_name, {})
    
    def _validate_local_rules(self, rules: Dict, data: Dict):
        """Validate compliance with local court rules."""
        if rules.get('max_page_limit') and data.get('document_pages'):
            if int(data.get('document_pages', 0)) > rules.get('max_page_limit'):
                self.errors.append(
                    f"Document exceeds maximum page limit of {rules.get('max_page_limit')} pages"
                )
        
        if rules.get('electronic_filing') and data.get('filing_method') == 'paper':
            self.errors.append("Court requires electronic filing")


# Example usage
if __name__ == '__main__':
    validator = ConditionalValidator()
    
    # Example engagement letter data
    engagement_data = {
        'client_name': 'John Smith',
        'client_type': 'individual',
        'client_dob': '1980-05-15',
        'matter_description': 'Contract review and negotiation',
        'engagement_date': '2024-01-15',
        'is_contingency': False,
        'hourly_rate': 350,
        'retainer_amount': 5000,
        'estimated_hours': 20,
        'jurisdiction': 'California'
    }
    
    is_valid, errors = validator.validate_engagement_letter(engagement_data)
    print(f"Engagement Letter Valid: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Example contingency matter
    contingency_data = {
        'client_name': 'Jane Doe',
        'client_type': 'individual',
        'matter_description': 'Personal injury claim',
        'engagement_date': '2024-01-20',
        'is_contingency': True,
        'contingency_percentage': 33,
        'jurisdiction': 'Texas'
    }
    
    is_valid, errors = validator.validate_engagement_letter(contingency_data)
    print(f"\nContingency Matter Valid: {is_valid}")
