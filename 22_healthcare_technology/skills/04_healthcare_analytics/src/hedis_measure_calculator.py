"""HEDIS Quality Measure Calculator"""
import pandas as pd
from datetime import datetime, timedelta

class HEDISCalculator:
    def __init__(self, measurement_year):
        self.measurement_year = measurement_year
        self.year_start = f'{measurement_year}-01-01'
        self.year_end = f'{measurement_year}-12-31'

    def calculate_cdc_hba1c_testing(self, patients_df, labs_df):
        """Comprehensive Diabetes Care - HbA1c Testing"""
        # Denominator: Diabetic patients age 18-75
        denominator = patients_df[
            (patients_df['age'].between(18, 75)) &
            (patients_df['has_diabetes'] == True) &
            (patients_df['continuous_enrollment'] == True)
        ]
        # Numerator: At least one HbA1c test during measurement year
        hba1c_tests = labs_df[
            (labs_df['test_code'] == '4548-4') &  # LOINC for HbA1c
            (labs_df['result_date'].between(self.year_start, self.year_end))
        ]
        numerator = denominator[denominator['patient_id'].isin(hba1c_tests['patient_id'])]
        return {
            'measure': 'CDC - HbA1c Testing',
            'denominator': len(denominator),
            'numerator': len(numerator),
            'rate': len(numerator) / len(denominator) * 100 if len(denominator) > 0 else 0
        }

    def calculate_cbp(self, patients_df, vitals_df):
        """Controlling High Blood Pressure"""
        # Denominator: Hypertensive patients age 18-85
        denominator = patients_df[
            (patients_df['age'].between(18, 85)) &
            (patients_df['has_hypertension'] == True) &
            (patients_df['continuous_enrollment'] == True)
        ]
        # Numerator: Most recent BP <140/90
        latest_bp = vitals_df.sort_values('measurement_date').groupby('patient_id').last()
        controlled_bp = latest_bp[(latest_bp['systolic_bp'] < 140) & (latest_bp['diastolic_bp'] < 90)]
        numerator = denominator[denominator['patient_id'].isin(controlled_bp.index)]
        return {
            'measure': 'Controlling High Blood Pressure',
            'denominator': len(denominator),
            'numerator': len(numerator),
            'rate': len(numerator) / len(denominator) * 100 if len(denominator) > 0 else 0
        }

    def calculate_bcs(self, patients_df, procedures_df):
        """Breast Cancer Screening"""
        # Denominator: Women age 50-74
        denominator = patients_df[
            (patients_df['gender'] == 'F') &
            (patients_df['age'].between(50, 74)) &
            (patients_df['continuous_enrollment'] == True)
        ]
        # Numerator: Mammogram in measurement year or prior year
        mammogram_codes = ['77065', '77066', '77067']  # CPT codes
        lookback_date = f'{self.measurement_year - 1}-01-01'
        mammograms = procedures_df[
            (procedures_df['procedure_code'].isin(mammogram_codes)) &
            (procedures_df['procedure_date'].between(lookback_date, self.year_end))
        ]
        numerator = denominator[denominator['patient_id'].isin(mammograms['patient_id'])]
        return {
            'measure': 'Breast Cancer Screening',
            'denominator': len(denominator),
            'numerator': len(numerator),
            'rate': len(numerator) / len(denominator) * 100 if len(denominator) > 0 else 0
        }
