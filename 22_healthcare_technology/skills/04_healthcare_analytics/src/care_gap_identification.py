"""Care Gap Identification System"""
import pandas as pd
from datetime import datetime, timedelta

class CareGapIdentifier:
    def __init__(self, measurement_date=None):
        self.measurement_date = measurement_date or datetime.now().date()
        self.gaps = []

    def identify_diabetes_gaps(self, patient):
        """Identify diabetes-related care gaps"""
        gaps = []
        if not patient.get('hba1c_last_date') or \
           (self.measurement_date - patient['hba1c_last_date']).days > 180:
            gaps.append({
                'gap_type': 'HbA1c Test Due',
                'priority': 'High' if patient.get('last_hba1c_value', 0) > 9 else 'Medium',
                'due_date': self.measurement_date,
                'measure': 'HEDIS CDC'
            })

        if not patient.get('eye_exam_last_date') or \
           (self.measurement_date - patient['eye_exam_last_date']).days > 365:
            gaps.append({
                'gap_type': 'Diabetic Eye Exam Due',
                'priority': 'Medium',
                'due_date': self.measurement_date,
                'measure': 'HEDIS CDC'
            })

        if not patient.get('on_statin') and patient.get('age', 0) >= 40:
            gaps.append({
                'gap_type': 'Statin Therapy Recommended',
                'priority': 'High',
                'due_date': self.measurement_date,
                'measure': 'HEDIS SPC'
            })

        return gaps

    def identify_preventive_gaps(self, patient):
        """Identify preventive care gaps"""
        gaps = []
        
        # Mammogram (Women 50-74)
        if patient['gender'] == 'F' and 50 <= patient['age'] <= 74:
            if not patient.get('mammogram_last_date') or \
               (self.measurement_date - patient['mammogram_last_date']).days > 730:  # 2 years
                gaps.append({
                    'gap_type': 'Mammogram Due',
                    'priority': 'High',
                    'due_date': self.measurement_date,
                    'measure': 'HEDIS BCS'
                })

        # Colonoscopy (50-75)
        if 50 <= patient['age'] <= 75:
            if not patient.get('colonoscopy_last_date') or \
               (self.measurement_date - patient['colonoscopy_last_date']).days > 3650:  # 10 years
                gaps.append({
                    'gap_type': 'Colorectal Cancer Screening Due',
                    'priority': 'High',
                    'due_date': self.measurement_date,
                    'measure': 'HEDIS COL'
                })

        return gaps

    def prioritize_gaps(self, all_gaps):
        """Prioritize care gaps for outreach"""
        # Sort by: High priority first, then by measure weight, then by due date
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        return sorted(all_gaps, key=lambda x: (priority_order[x['priority']], x['due_date']))

    def generate_outreach_list(self, patients_df):
        """Generate prioritized outreach list with care gaps"""
        outreach_list = []
        
        for _, patient in patients_df.iterrows():
            patient_gaps = []
            
            if patient.get('has_diabetes'):
                patient_gaps.extend(self.identify_diabetes_gaps(patient))
            
            patient_gaps.extend(self.identify_preventive_gaps(patient))
            
            if patient_gaps:
                outreach_list.append({
                    'patient_id': patient['patient_id'],
                    'patient_name': patient['name'],
                    'phone': patient['phone'],
                    'total_gaps': len(patient_gaps),
                    'gaps': self.prioritize_gaps(patient_gaps),
                    'priority_score': sum(1 if g['priority'] == 'High' else 0.5 for g in patient_gaps)
                })
        
        return sorted(outreach_list, key=lambda x: x['priority_score'], reverse=True)
