"""Multidimensional Risk Stratification Algorithm"""
import pandas as pd
import numpy as np

class RiskStratification:
    def __init__(self):
        self.weights = {'clinical': 0.35, 'utilization': 0.30, 'cost': 0.20, 'psychosocial': 0.15}

    def calculate_clinical_risk(self, patient):
        """Clinical complexity risk score"""
        score = 0
        score += min(patient['chronic_condition_count'] / 10, 1.0) * 0.25
        score += min(patient['hcc_raf_score'] / 3.0, 1.0) * 0.30
        score += min(patient['charlson_score'] / 10, 1.0) * 0.20
        score += min(patient['medication_count'] / 15, 1.0) * 0.15
        score += min(patient['high_risk_meds'] / 5, 1.0) * 0.10
        return score

    def calculate_utilization_risk(self, patient):
        """Healthcare utilization risk score"""
        score = 0
        score += min(patient['ed_visits_12mo'] / 6, 1.0) * 0.30
        score += min(patient['ip_admits_12mo'] / 3, 1.0) * 0.35
        score += min(patient['readmissions_12mo'] / 2, 1.0) * 0.20
        score += (1.0 - min(patient['pcp_visits_12mo'] / 4, 1.0)) * 0.10
        score += patient['noshow_rate'] * 0.05
        return score

    def calculate_cost_risk(self, patient):
        """Cost-based risk score"""
        predicted_cost = patient.get('predicted_cost_annual', 0)
        return min(predicted_cost / 50000, 1.0)

    def calculate_psychosocial_risk(self, patient):
        """Social determinants and behavioral health risk"""
        score = 0
        if patient.get('lives_alone') and patient.get('age', 0) > 75: score += 0.15
        if patient.get('transportation_barriers'): score += 0.15
        if patient.get('food_insecure'): score += 0.20
        if patient.get('housing_unstable'): score += 0.20
        if patient.get('has_depression'): score += 0.10
        if patient.get('substance_abuse'): score += 0.15
        if patient.get('area_deprivation_index', 0) > 80: score += 0.10
        return min(score, 1.0)

    def stratify_patient(self, patient):
        """Calculate composite risk score and assign tier"""
        clinical = self.calculate_clinical_risk(patient)
        utilization = self.calculate_utilization_risk(patient)
        cost = self.calculate_cost_risk(patient)
        psychosocial = self.calculate_psychosocial_risk(patient)
        
        composite = (clinical * self.weights['clinical'] +
                    utilization * self.weights['utilization'] +
                    cost * self.weights['cost'] +
                    psychosocial * self.weights['psychosocial'])
        
        if composite >= 0.70: tier, intervention = 'High', 'Intensive Care Management'
        elif composite >= 0.40: tier, intervention = 'Medium', 'Care Coordination'
        elif composite >= 0.20: tier, intervention = 'Low', 'Self-Management Support'
        else: tier, intervention = 'Healthy', 'Prevention & Wellness'
        
        return {'patient_id': patient['patient_id'], 'composite_score': composite,
                'risk_tier': tier, 'recommended_intervention': intervention,
                'component_scores': {'clinical': clinical, 'utilization': utilization,
                                   'cost': cost, 'psychosocial': psychosocial}}
