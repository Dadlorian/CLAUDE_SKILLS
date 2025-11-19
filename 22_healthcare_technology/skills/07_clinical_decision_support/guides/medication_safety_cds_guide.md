# Medication Safety CDS Implementation Guide

## Overview
Guide to implementing comprehensive medication safety checking including drug interactions, allergies, duplicate therapy, and renal dosing.

## Architecture

### Layered Safety Checks
1. Drug-allergy checking
2. Drug-drug interactions
3. Duplicate therapy detection
4. Contraindications
5. Renal/hepatic dosing
6. Pregnancy/lactation warnings
7. Age-specific warnings

## Implementation Steps

### 1. Database Integration

Choose medication knowledge base:
- **First DataBank** (FDB)
- **Micromedex**
- **Lexicomp**

### 2. Drug-Drug Interaction Checking

```python
class DrugInteractionChecker:
    def __init__(self, fdb_client):
        self.fdb = fdb_client
        self.severity_threshold = ["CONTRAINDICATED", "MAJOR"]
    
    async def check_interactions(self, patient_id, new_medication):
        # Get active medications
        active_meds = await self.get_active_medications(patient_id)
        
        # Extract RxNorm codes
        all_rxcuis = [med.rxcui for med in active_meds + [new_medication]]
        
        # Query FDB
        interactions = await self.fdb.check_ddi(all_rxcuis, severities=self.severity_threshold)
        
        # Filter and format
        return [self.format_interaction(i) for i in interactions]
    
    def format_interaction(self, interaction):
        return {
            'drug1': interaction['drug1'],
            'drug2': interaction['drug2'],
            'severity': interaction['severity'],
            'clinical_effect': interaction['clinical_effect'],
            'management': interaction['management'],
            'evidence': interaction['documentation_level'],
            'alternatives': self.suggest_alternatives(interaction)
        }
```

### 3. Allergy Cross-Reactivity

```python
CROSS_REACTIVITY_RULES = {
    'penicillin': {
        'cephalosporins': {'risk': 0.05, 'note': '1-5% cross-reactivity'},
        'carbapenems': {'risk': 0.01, 'note': '~1% cross-reactivity'},
        'aztreonam': {'risk': 0.0, 'note': 'No cross-reactivity'}
    },
    'sulfa_antibiotics': {
        'sulfa_nonantibiotic': {'risk': 0.0, 'note': 'Different structures, no cross-reactivity'}
    }
}

class AllergyChecker:
    def check_allergy(self, patient_allergies, new_medication):
        for allergy in patient_allergies:
            # Exact match
            if allergy.drug_rxcui == new_medication.rxcui:
                return {
                    'match_type': 'EXACT',
                    'severity': 'CRITICAL',
                    'action': 'BLOCK',
                    'message': f"Patient allergic to {allergy.drug_name}",
                    'reaction': allergy.reaction,
                    'date': allergy.onset_date
                }
            
            # Check cross-reactivity
            cross_risk = self.check_cross_reactivity(allergy, new_medication)
            if cross_risk and cross_risk['risk'] > 0.05:
                return {
                    'match_type': 'CROSS_REACTIVITY',
                    'severity': 'WARNING',
                    'action': 'WARN',
                    'risk': cross_risk['risk'],
                    'note': cross_risk['note']
                }
        
        return None
```

### 4. Renal Dosing Adjustment

```python
class RenalDosingAdjuster:
    def __init__(self):
        self.renal_adjusted_drugs = self.load_renal_database()
    
    def check_renal_dosing(self, medication, patient_gfr):
        drug_info = self.renal_adjusted_drugs.get(medication.rxcui)
        
        if not drug_info:
            return None  # No renal adjustment needed
        
        # Find appropriate dose for GFR
        for dose_tier in drug_info['tiers']:
            if dose_tier['gfr_min'] <= patient_gfr < dose_tier['gfr_max']:
                if dose_tier['dose'] != medication.dose:
                    return {
                        'current_dose': medication.dose,
                        'recommended_dose': dose_tier['dose'],
                        'frequency': dose_tier['frequency'],
                        'gfr': patient_gfr,
                        'rationale': f"Dose adjustment for GFR {patient_gfr}"
                    }
        
        return None
```

### 5. Duplicate Therapy Detection

```python
class DuplicateTherapyDetector:
    def __init__(self):
        self.drug_classes = self.load_therapeutic_classes()
    
    def check_duplicate(self, active_medications, new_medication):
        new_classes = self.get_drug_classes(new_medication)
        
        duplicates = []
        for active_med in active_medications:
            active_classes = self.get_drug_classes(active_med)
            
            # Same ingredient
            if active_med.ingredient == new_medication.ingredient:
                duplicates.append({
                    'type': 'SAME_INGREDIENT',
                    'existing': active_med,
                    'severity': 'HIGH',
                    'recommendation': 'Consider discontinuing existing medication'
                })
            
            # Same therapeutic class
            overlap = set(new_classes) & set(active_classes)
            if overlap:
                duplicates.append({
                    'type': 'THERAPEUTIC_CLASS_OVERLAP',
                    'classes': list(overlap),
                    'existing': active_med,
                    'severity': 'MODERATE'
                })
        
        return duplicates
```

## Alert Integration

### CDS Hooks Integration

```javascript
// medication-prescribe hook handler
async function handleMedicationPrescribe(request) {
    const { context, prefetch } = request;
    const cards = [];
    
    // Run all safety checks in parallel
    const [interactions, allergies, renalDosing, duplicates] = await Promise.all([
        checkDrugInteractions(context, prefetch),
        checkAllergies(context, prefetch),
        checkRenalDosing(context, prefetch),
        checkDuplicateTherapy(context, prefetch)
    ]);
    
    // Generate cards
    if (allergies.length > 0) {
        cards.push(...allergies.map(createAllergyCard));
    }
    
    if (interactions.length > 0) {
        cards.push(...interactions.map(createInteractionCard));
    }
    
    if (renalDosing) {
        cards.push(createRenalDosingCard(renalDosing));
    }
    
    return { cards };
}
```

## Testing

### Test Scenarios

```python
def test_penicillin_allergy_exact_match():
    """Should block penicillin order if documented allergy"""
    patient = create_patient(allergies=[
        Allergy('penicillin', reaction='anaphylaxis', date='2020-01-01')
    ])
    
    order = MedicationOrder(drug='amoxicillin')
    
    alert = allergy_checker.check(patient, order)
    
    assert alert['severity'] == 'CRITICAL'
    assert alert['action'] == 'BLOCK'

def test_renal_dosing_gfr_30():
    """Should recommend dose reduction for GFR 30"""
    patient = create_patient(gfr=30)
    order = MedicationOrder(drug='vancomycin', dose='1000mg', frequency='q12h')
    
    recommendation = renal_adjuster.check(patient, order)
    
    assert recommendation['recommended_dose'] == '500mg'
    assert recommendation['frequency'] == 'q24h'
```

## Performance Optimization

- Cache drug databases (refresh daily)
- Batch interaction checking
- Asynchronous processing
- Response time < 3 seconds

## Monitoring Metrics

- Alert firing rate by type
- Override rate by severity
- Time to alert acknowledgment
- Prevented adverse events

## Resources
- FDB Documentation
- ISMP High-Alert Medications
- Beers Criteria for Elderly
- KDIGO Guidelines (Renal Dosing)
