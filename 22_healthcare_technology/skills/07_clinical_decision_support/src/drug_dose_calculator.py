"""Drug Dose Calculator with Weight/BSA-Based Dosing"""
import math

def calculate_bsa(weight_kg: float, height_cm: float, method: str = "dubois") -> float:
    """Calculate body surface area"""
    if method == "dubois":
        return 0.007184 * (weight_kg ** 0.425) * (height_cm ** 0.725)
    elif method == "mosteller":
        return math.sqrt((height_cm * weight_kg) / 3600)
    return 0.0

def calculate_weight_based_dose(drug: str, weight_kg: float, indication: str = None) -> dict:
    """Calculate weight-based medication doses"""
    
    dosing_rules = {
        'enoxaparin_treatment': {'dose_per_kg': 1.0, 'unit': 'mg', 'frequency': 'q12h'},
        'enoxaparin_prophylaxis': {'dose_per_kg': 0.5, 'unit': 'mg', 'frequency': 'daily'},
        'heparin_bolus': {'dose_per_kg': 80, 'unit': 'units', 'frequency': 'once'},
        'heparin_infusion': {'dose_per_kg': 18, 'unit': 'units/kg/hr', 'frequency': 'continuous'}
    }
    
    key = f"{drug}_{indication}" if indication else drug
    rule = dosing_rules.get(key)
    
    if not rule:
        return {'error': 'No dosing rule found'}
    
    dose = weight_kg * rule['dose_per_kg']
    
    return {
        'dose': round(dose, 1),
        'unit': rule['unit'],
        'frequency': rule['frequency'],
        'weight_kg': weight_kg
    }

def calculate_chemotherapy_dose(drug: str, bsa: float, protocol: str) -> dict:
    """Calculate chemotherapy doses based on BSA"""
    
    chemo_protocols = {
        'cisplatin': {'dose_per_m2': 75, 'unit': 'mg'},
        'doxorubicin': {'dose_per_m2': 60, 'unit': 'mg'},
        'carboplatin': {'auc': 5, 'unit': 'AUC'}
    }
    
    if drug not in chemo_protocols:
        return {'error': 'Unknown chemotherapy drug'}
    
    protocol_data = chemo_protocols[drug]
    
    if 'dose_per_m2' in protocol_data:
        dose = bsa * protocol_data['dose_per_m2']
        return {
            'dose': round(dose, 1),
            'unit': protocol_data['unit'],
            'bsa': round(bsa, 2),
            'calculation': f"{bsa} m² × {protocol_data['dose_per_m2']} {protocol_data['unit']}/m²"
        }
    
    return protocol_data
