"""Renal Dosing Adjustment Calculator"""
from typing import Dict, Optional
import math

def calculate_gfr_ckd_epi(creatinine: float, age: int, sex: str, race: str = 'other') -> float:
    """Calculate eGFR using CKD-EPI equation"""
    k = 0.7 if sex == 'F' else 0.9
    a = -0.329 if sex == 'F' else -0.411
    female_factor = 1.018 if sex == 'F' else 1.0
    black_factor = 1.159 if race == 'black' else 1.0
    
    min_val = min(creatinine / k, 1)
    max_val = max(creatinine / k, 1)
    
    gfr = 141 * (min_val ** a) * (max_val ** -1.209) * (0.993 ** age) * female_factor * black_factor
    
    return round(gfr, 1)

def get_renal_dose_adjustment(drug: str, gfr: float) -> Dict:
    """Get dose adjustment based on GFR"""
    
    dosing_db = {
        'vancomycin': [
            {'gfr_min': 60, 'gfr_max': 999, 'dose': '15-20 mg/kg', 'frequency': 'q8-12h'},
            {'gfr_min': 30, 'gfr_max': 60, 'dose': '15-20 mg/kg', 'frequency': 'q24h'},
            {'gfr_min': 10, 'gfr_max': 30, 'dose': '15-20 mg/kg', 'frequency': 'q48-72h'},
            {'gfr_min': 0, 'gfr_max': 10, 'dose': 'Loading dose only', 'frequency': 'Monitor levels'}
        ],
        'ceftriaxone': [
            {'gfr_min': 10, 'gfr_max': 999, 'dose': '1-2g', 'frequency': 'q24h'},
            {'gfr_min': 0, 'gfr_max': 10, 'dose': '1-2g', 'frequency': 'q24h', 'note': 'No adjustment needed'}
        ],
        'metformin': [
            {'gfr_min': 45, 'gfr_max': 999, 'dose': 'Standard', 'frequency': 'BID', 'note': 'No adjustment'},
            {'gfr_min': 30, 'gfr_max': 45, 'dose': '500mg', 'frequency': 'BID', 'note': 'Reduce dose'},
            {'gfr_min': 0, 'gfr_max': 30, 'dose': 'CONTRAINDICATED', 'frequency': None, 'note': 'Risk of lactic acidosis'}
        ]
    }
    
    if drug not in dosing_db:
        return {'error': f'No renal dosing data for {drug}'}
    
    for tier in dosing_db[drug]:
        if tier['gfr_min'] <= gfr < tier['gfr_max']:
            return {
                'drug': drug,
                'gfr': gfr,
                'dose': tier['dose'],
                'frequency': tier['frequency'],
                'note': tier.get('note', ''),
                'contraindicated': tier['dose'] == 'CONTRAINDICATED'
            }
    
    return {'error': 'GFR out of range'}

# Example usage
if __name__ == "__main__":
    gfr = calculate_gfr_ckd_epi(creatinine=1.8, age=65, sex='M', race='white')
    print(f"eGFR: {gfr} mL/min/1.73m²")
    
    adjustment = get_renal_dose_adjustment('vancomycin', gfr)
    print(f"Vancomycin dosing: {adjustment['dose']} {adjustment['frequency']}")
