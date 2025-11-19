"""Longitudinal Patient Analysis"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class LongitudinalPatientAnalysis:
    def __init__(self, patient_id):
        self.patient_id = patient_id

    def create_patient_timeline(self, encounters, diagnoses, medications, labs):
        """Create comprehensive patient timeline"""
        timeline = []
        
        # Add encounters
        for _, enc in encounters.iterrows():
            timeline.append({
                'date': enc['encounter_date'],
                'type': 'Encounter',
                'subtype': enc['encounter_type'],
                'details': f"{enc['encounter_type']} at {enc['location']}"
            })
        
        # Add diagnoses
        for _, diag in diagnoses.iterrows():
            timeline.append({
                'date': diag['diagnosis_date'],
                'type': 'Diagnosis',
                'subtype': 'New Diagnosis',
                'details': diag['diagnosis_description']
            })
        
        # Add medications
        for _, med in medications.iterrows():
            timeline.append({
                'date': med['start_date'],
                'type': 'Medication',
                'subtype': 'Start',
                'details': med['medication_name']
            })
        
        # Add lab results
        for _, lab in labs.iterrows():
            timeline.append({
                'date': lab['result_date'],
                'type': 'Lab Result',
                'subtype': lab['test_name'],
                'details': f"{lab['test_name']}: {lab['result_value']} {lab['unit']}"
            })
        
        return pd.DataFrame(timeline).sort_values('date')

    def analyze_disease_progression(self, condition, labs_df, encounters_df):
        """Analyze disease progression over time"""
        progression = []
        
        # Group by year/quarter
        labs_df['year_quarter'] = labs_df['result_date'].dt.to_period('Q')
        
        for period in labs_df['year_quarter'].unique():
            period_labs = labs_df[labs_df['year_quarter'] == period]
            period_encounters = encounters_df[encounters_df['encounter_date'].dt.to_period('Q') == period]
            
            progression.append({
                'period': str(period),
                'avg_hba1c': period_labs[period_labs['test_code'] == '4548-4']['result_numeric'].mean() if condition == 'diabetes' else None,
                'encounter_count': len(period_encounters),
                'hospitalization_count': len(period_encounters[period_encounters['type'] == 'Inpatient'])
            })
        
        return pd.DataFrame(progression)

    def identify_care_patterns(self, encounters_df):
        """Identify patterns in care delivery"""
        patterns = {
            'visit_frequency': self.calculate_visit_frequency(encounters_df),
            'provider_continuity': self.calculate_provider_continuity(encounters_df),
            'care_setting_utilization': encounters_df['encounter_type'].value_counts().to_dict(),
            'seasonal_patterns': encounters_df.groupby(encounters_df['encounter_date'].dt.month).size().to_dict()
        }
        return patterns

    def calculate_visit_frequency(self, encounters_df):
        """Calculate average visit frequency"""
        if len(encounters_df) < 2:
            return None
        
        encounters_sorted = encounters_df.sort_values('encounter_date')
        date_diffs = encounters_sorted['encounter_date'].diff().dt.days
        return {'avg_days_between_visits': date_diffs.mean(), 'median_days_between_visits': date_diffs.median()}

    def calculate_provider_continuity(self, encounters_df):
        """Calculate continuity of care score"""
        if len(encounters_df) == 0:
            return 0
        
        primary_provider_visits = encounters_df['provider_id'].value_counts().iloc[0] if len(encounters_df) > 0 else 0
        total_visits = len(encounters_df)
        
        return primary_provider_visits / total_visits if total_visits > 0 else 0
