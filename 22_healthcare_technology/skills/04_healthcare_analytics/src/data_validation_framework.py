"""Healthcare Data Validation Framework"""
import pandas as pd
from datetime import datetime

class HealthcareDataValidator:
    def __init__(self):
        self.validation_rules = {}
        self.issues = []

    def add_rule(self, rule_name, rule_func, severity='error'):
        """Add a validation rule"""
        self.validation_rules[rule_name] = {
            'function': rule_func,
            'severity': severity
        }

    def validate_patient_data(self, patient_df):
        """Validate patient demographic data"""
        issues = []
        
        # Date of birth validation
        invalid_dob = patient_df[
            (patient_df['date_of_birth'] > datetime.now().date()) |
            (patient_df['date_of_birth'] < datetime(1900, 1, 1).date())
        ]
        if len(invalid_dob) > 0:
            issues.append({
                'rule': 'valid_date_of_birth',
                'severity': 'error',
                'count': len(invalid_dob),
                'message': f'{len(invalid_dob)} patients with invalid date of birth'
            })
        
        # Death date validation
        invalid_death = patient_df[
            patient_df['date_of_death'].notna() &
            (patient_df['date_of_death'] < patient_df['date_of_birth'])
        ]
        if len(invalid_death) > 0:
            issues.append({
                'rule': 'death_after_birth',
                'severity': 'error',
                'count': len(invalid_death),
                'message': 'Death date before birth date'
            })
        
        # Gender code validation
        valid_gender_codes = ['M', 'F', 'U', 'O']
        invalid_gender = patient_df[~patient_df['gender'].isin(valid_gender_codes)]
        if len(invalid_gender) > 0:
            issues.append({
                'rule': 'valid_gender_code',
                'severity': 'error',
                'count': len(invalid_gender),
                'message': f'Invalid gender codes: {invalid_gender["gender"].unique()}'
            })
        
        return issues

    def validate_encounter_data(self, encounter_df):
        """Validate encounter data"""
        issues = []
        
        # Discharge before admission
        invalid_dates = encounter_df[
            encounter_df['discharge_date'] < encounter_df['admission_date']
        ]
        if len(invalid_dates) > 0:
            issues.append({
                'rule': 'discharge_after_admission',
                'severity': 'error',
                'count': len(invalid_dates),
                'message': 'Discharge date before admission date'
            })
        
        # Negative length of stay
        invalid_los = encounter_df[encounter_df['length_of_stay'] < 0]
        if len(invalid_los) > 0:
            issues.append({
                'rule': 'non_negative_los',
                'severity': 'error',
                'count': len(invalid_los),
                'message': 'Negative length of stay'
            })
        
        # Implausible length of stay (>365 days)
        implausible_los = encounter_df[encounter_df['length_of_stay'] > 365]
        if len(implausible_los) > 0:
            issues.append({
                'rule': 'plausible_los',
                'severity': 'warning',
                'count': len(implausible_los),
                'message': f'{len(implausible_los)} encounters with LOS > 365 days'
            })
        
        return issues

    def validate_lab_data(self, lab_df):
        """Validate laboratory data"""
        issues = []
        
        # Result date after collection date
        invalid_dates = lab_df[
            lab_df['result_date'] < lab_df['collection_date']
        ]
        if len(invalid_dates) > 0:
            issues.append({
                'rule': 'result_after_collection',
                'severity': 'error',
                'count': len(invalid_dates),
                'message': 'Result date before collection date'
            })
        
        # Implausible lab values
        implausible_hba1c = lab_df[
            (lab_df['test_code'] == '4548-4') &
            ((lab_df['result_numeric'] < 3) | (lab_df['result_numeric'] > 20))
        ]
        if len(implausible_hba1c) > 0:
            issues.append({
                'rule': 'plausible_hba1c',
                'severity': 'warning',
                'count': len(implausible_hba1c),
                'message': 'Implausible HbA1c values (<3 or >20)'
            })
        
        return issues

    def generate_validation_report(self, data):
        """Generate comprehensive validation report"""
        all_issues = []
        
        if 'patients' in data:
            all_issues.extend(self.validate_patient_data(data['patients']))
        if 'encounters' in data:
            all_issues.extend(self.validate_encounter_data(data['encounters']))
        if 'labs' in data:
            all_issues.extend(self.validate_lab_data(data['labs']))
        
        error_count = sum(1 for i in all_issues if i['severity'] == 'error')
        warning_count = sum(1 for i in all_issues if i['severity'] == 'warning')
        
        return {
            'validation_date': datetime.now(),
            'total_issues': len(all_issues),
            'errors': error_count,
            'warnings': warning_count,
            'issues': all_issues,
            'passed': error_count == 0
        }
