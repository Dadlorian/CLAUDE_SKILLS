"""Provider Performance Analytics"""
import pandas as pd
import numpy as np

class ProviderPerformanceAnalytics:
    def __init__(self, measurement_period):
        self.measurement_period = measurement_period

    def calculate_panel_metrics(self, provider_id, patients_df):
        """Calculate provider panel metrics"""
        panel = patients_df[patients_df['attributed_provider'] == provider_id]
        
        return {
            'provider_id': provider_id,
            'panel_size': len(panel),
            'avg_patient_age': panel['age'].mean(),
            'avg_hcc_score': panel['hcc_raf_score'].mean(),
            'high_risk_patients': len(panel[panel['risk_tier'] == 'High']),
            'chronic_condition_prevalence': {
                'diabetes': (panel['has_diabetes'] == True).sum() / len(panel) * 100,
                'hypertension': (panel['has_hypertension'] == True).sum() / len(panel) * 100,
                'chf': (panel['has_chf'] == True).sum() / len(panel) * 100
            }
        }

    def calculate_quality_metrics(self, provider_id, quality_measures_df):
        """Calculate provider quality performance"""
        provider_measures = quality_measures_df[quality_measures_df['provider_id'] == provider_id]
        
        total_measures = len(provider_measures)
        measures_meeting_target = (provider_measures['rate'] >= provider_measures['target']).sum()
        
        return {
            'provider_id': provider_id,
            'total_measures': total_measures,
            'measures_meeting_target': measures_meeting_target,
            'pct_meeting_target': measures_meeting_target / total_measures * 100 if total_measures > 0 else 0,
            'composite_quality_score': provider_measures['rate'].mean(),
            'top_performing_measures': provider_measures.nlargest(5, 'rate')[['measure_name', 'rate']].to_dict('records'),
            'opportunities': provider_measures.nsmallest(5, 'rate')[['measure_name', 'rate']].to_dict('records')
        }

    def calculate_utilization_metrics(self, provider_id, encounters_df):
        """Calculate provider utilization patterns"""
        provider_encounters = encounters_df[encounters_df['provider_id'] == provider_id]
        
        return {
            'provider_id': provider_id,
            'total_encounters': len(provider_encounters),
            'ip_admit_rate': len(provider_encounters[provider_encounters['type'] == 'Inpatient']) / len(provider_encounters) * 100,
            'ed_visit_rate': len(provider_encounters[provider_encounters['type'] == 'ED']) / len(provider_encounters) * 100,
            'avg_length_of_stay': provider_encounters[provider_encounters['type'] == 'Inpatient']['los'].mean(),
            'readmission_rate': (provider_encounters['readmitted_30d'] == True).sum() / len(provider_encounters[provider_encounters['type'] == 'Inpatient']) * 100
        }

    def generate_provider_scorecard(self, provider_id, data):
        """Generate comprehensive provider scorecard"""
        return {
            'provider_id': provider_id,
            'measurement_period': self.measurement_period,
            'panel_metrics': self.calculate_panel_metrics(provider_id, data['patients']),
            'quality_metrics': self.calculate_quality_metrics(provider_id, data['quality_measures']),
            'utilization_metrics': self.calculate_utilization_metrics(provider_id, data['encounters']),
            'generated_date': pd.Timestamp.now()
        }

    def peer_comparison(self, provider_id, all_providers_df):
        """Compare provider to peer average"""
        provider = all_providers_df[all_providers_df['provider_id'] == provider_id].iloc[0]
        peer_group = all_providers_df[all_providers_df['specialty'] == provider['specialty']]
        
        return {
            'provider_id': provider_id,
            'quality_score_percentile': (peer_group['quality_score'] < provider['quality_score']).sum() / len(peer_group) * 100,
            'peer_avg_quality_score': peer_group['quality_score'].mean(),
            'peer_avg_panel_size': peer_group['panel_size'].mean(),
            'ranking': (peer_group['quality_score'] >= provider['quality_score']).sum()
        }
