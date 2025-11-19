# Medication Interaction Databases Reference

## Overview
Commercial and open-source databases providing drug-drug, drug-allergy, drug-disease, and drug-food interaction information for clinical decision support systems.

## Major Commercial Databases

### First DataBank (FDB)
**Coverage**:
- Drug-drug interactions (DDI)
- Drug-allergy cross-reactivity
- Duplicate therapy
- Drug-disease contraindications
- Renal/hepatic dosing
- Pregnancy/lactation

**Severity Classifications**:
1. **Contraindicated**: Do not use together
2. **Major**: May be life-threatening or cause permanent damage
3. **Moderate**: May worsen condition or alter therapy
4. **Minor**: Limited clinical significance

**Key Features**:
- Evidence-based severity ratings
- Clinical management recommendations
- Onset and documentation levels
- Mechanism of action descriptions
- > 1 million drug-drug interaction pairs

**API Integration**:
```http
POST /ddi/v1/check
{
  "medications": [
    {"rxcui": "855332"},  // Atorvastatin
    {"rxcui": "42463"}    // Clarithromycin
  ],
  "severities": ["contraindicated", "major"]
}
```

### Micromedex (IBM Watson Health)
**Coverage**:
- Drug interactions
- Toxicology
- IV compatibility
- Drug information monographs
- Disease management

**Severity Scale**:
1. **Contraindicated**
2. **Major**: Life-threatening or permanent damage
3. **Moderate**: Deterioration, may need intervention
4. **Minor**: Minimal clinical effects

**Documentation Levels**:
- **Excellent**: Controlled studies
- **Good**: Case reports and clinical studies
- **Fair**: Limited evidence
- **Poor**: Theoretical or animal studies

**Onset**:
- Rapid: Hours
- Delayed: Days to weeks

### Lexicomp
**Coverage**:
- Drug interactions
- Clinical drug information
- Drug identification
- Pediatric & neonatal dosing
- IV compatibility

**Severity Ratings**:
- **A**: No known interaction
- **B**: No action needed
- **C**: Monitor therapy
- **D**: Consider therapy modification
- **X**: Avoid combination

**Reliability Ratings**:
1. Excellent (clinical studies)
2. Good (case reports)
3. Fair (expert opinion)
4. Poor (theoretical)

### Medi-Span (Wolters Kluwer)
**Coverage**:
- Drug interactions
- Duplicate therapy
- Allergy screening
- Clinical formularies
- Drug pricing

**Severity Levels**:
1. Contraindicated
2. Major
3. Moderate
4. Minor

## Open-Source & Public Resources

### DrugBank
**Access**: Academic license or subscription
**Content**:
- 14,000+ drug entries
- Drug targets
- Drug-drug interactions
- Pharmacology
- Chemical structures

**Data Format**: XML, JSON, CSV

### RxNorm (NLM)
**Purpose**: Drug terminology standard
**Content**:
- Clinical drug names
- Ingredient relationships
- Dose forms
- FREE from NLM

**Use Case**: Map local drug codes to standard identifiers

### RxNav APIs (NLM)
**Free APIs**:
- Find drug interactions (via DrugBank)
- RxNorm terminology browsing
- Drug relationships

**Example**:
```http
GET https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis=207106+152923
```

### PubChem (NIH)
**Content**:
- Chemical structures
- Biological activities
- Literature references
- FREE

## Interaction Types

### Drug-Drug Interactions (DDI)

#### Pharmacokinetic
**Absorption**:
- Chelation (tetracycline + calcium)
- pH changes (PPIs + ketoconazole)

**Distribution**:
- Protein binding displacement (warfarin + NSAIDs)

**Metabolism**:
- **CYP450 Inhibition**:
  - CYP3A4: Clarithromycin, grapefruit juice
  - CYP2D6: Fluoxetine, paroxetine
  - CYP2C9: Fluconazole, amiodarone
- **CYP450 Induction**:
  - Rifampin, carbamazepine, phenytoin

**Excretion**:
- Renal tubular secretion (NSAIDs + methotrexate)

#### Pharmacodynamic
**Additive/Synergistic**:
- CNS depression (opioids + benzodiazepines)
- QTc prolongation (multiple drugs)
- Bleeding risk (warfarin + aspirin)
- Serotonin syndrome (SSRIs + MAOIs)

**Antagonistic**:
- Beta-blockers + beta-agonists
- ACE inhibitors + NSAIDs (antihypertensive effect)

### Drug-Allergy Interactions

#### Cross-Reactivity Patterns

**Beta-Lactams**:
```
Penicillins ↔ Cephalosporins
  - Cross-reactivity: ~2-10%
  - Side chain similarity important
  - Anaphylaxis history: avoid

Penicillins ↔ Carbapenems
  - Cross-reactivity: ~1%
  - Generally safe if no anaphylaxis

Cephalosporins ↔ Ceftaroline
  - Same drug class
  - High cross-reactivity
```

**Sulfonamides**:
- Antibiotic sulfonamides ↔ Non-antibiotic sulfonamides
- Cross-reactivity controversial
- Evaluate individual risk

**Aspirin/NSAIDs**:
- Cross-reactivity within COX inhibitors
- Consider COX-2 selective if needed

### Drug-Disease Interactions

**Examples**:
- **NSAIDs + Chronic Kidney Disease**: Worsening renal function
- **Anticholinergics + BPH**: Urinary retention
- **Beta-blockers + Asthma**: Bronchospasm
- **Glitazones + Heart Failure**: Fluid retention
- **Metformin + Renal impairment**: Lactic acidosis risk

### Drug-Food Interactions

**Examples**:
- **Warfarin + Vitamin K-rich foods**: Decreased INR
- **MAOIs + Tyramine**: Hypertensive crisis
- **Grapefruit + CYP3A4 substrates**: Increased drug levels
- **Dairy + Tetracyclines**: Decreased absorption
- **Alcohol + Metronidazole**: Disulfiram reaction

### Drug-Lab Interactions

**Examples**:
- **Biotin supplements**: False troponin results
- **Tetracycline**: False elevated catecholamines
- **Rifampin**: False elevated bilirubin

## Duplicate Therapy Detection

### Therapeutic Class Overlap
**Examples**:
- Multiple ACE inhibitors
- Multiple statins
- Multiple PPIs
- Multiple benzodiazepines

### Ingredient Overlap
**Examples**:
- Percocet (acetaminophen + oxycodone) + acetaminophen
- Multiple cough/cold products with same ingredients
- Different brands, same active ingredient

### Cumulative Dose Concerns
**Examples**:
- Multiple acetaminophen sources > 4g/day
- Multiple sedating medications
- Multiple anticholinergic medications (anticholinergic burden)

## Implementation Patterns

### Severity Filtering
```python
def filter_interactions(interactions, patient_context):
    """Filter interactions based on clinical context"""
    filtered = []

    for interaction in interactions:
        # Always show contraindicated
        if interaction.severity == "CONTRAINDICATED":
            filtered.append(interaction)

        # Show major if not previously overridden
        elif interaction.severity == "MAJOR":
            if not is_previously_overridden(patient, interaction):
                filtered.append(interaction)

        # Show moderate only in outpatient
        elif interaction.severity == "MODERATE":
            if patient_context.setting == "OUTPATIENT":
                filtered.append(interaction)

    return filtered
```

### Dose-Dependent Interactions
```python
def check_dose_dependent_ddi(drug1, drug2):
    """Some interactions only occur at higher doses"""
    if drug1.name == "aspirin" and drug2.name == "ibuprofen":
        if drug1.dose_mg <= 81:  # Low-dose aspirin
            return {
                "severity": "MODERATE",
                "message": "Low-dose aspirin interaction with ibuprofen"
            }
        else:
            return {
                "severity": "MAJOR",
                "message": "High-dose aspirin increases bleeding risk"
            }
```

### Time-Based Interactions
```python
def check_temporal_interaction(drug1, drug2):
    """Some interactions can be mitigated by timing"""
    if drug1.name == "levothyroxine" and drug2.name == "calcium":
        return {
            "severity": "MODERATE",
            "message": "Separate administration by 4 hours",
            "recommendation": "Take levothyroxine in AM, calcium at bedtime"
        }
```

## Data Structures

### Interaction Record
```json
{
  "interaction_id": "DDI-12345",
  "drug1": {
    "rxcui": "207106",
    "name": "Warfarin",
    "ingredient": "warfarin"
  },
  "drug2": {
    "rxcui": "161",
    "name": "Aspirin",
    "ingredient": "aspirin"
  },
  "severity": "MAJOR",
  "documentation": "GOOD",
  "onset": "DELAYED",
  "mechanism": "Pharmacodynamic synergy - both antiplatelet/anticoagulant",
  "clinical_effect": "Increased bleeding risk (2-3x)",
  "management": "Consider gastroprotection with PPI. Monitor for bleeding. Check INR more frequently.",
  "evidence": [
    {
      "type": "clinical_trial",
      "citation": "PMID: 12345678",
      "summary": "Increased bleeding in warfarin + aspirin users"
    }
  ],
  "alternatives": [
    {
      "drug": "apixaban",
      "rationale": "DOAC without aspirin interaction"
    }
  ]
}
```

## Update Frequency

### Database Updates
- **First DataBank**: Monthly
- **Micromedex**: Quarterly
- **Lexicomp**: Continuous updates
- **FDA Safety Alerts**: As released

### Integration Strategy
```python
class InteractionDatabase:
    def __init__(self):
        self.version = "2023.11"
        self.last_updated = "2023-11-01"
        self.cache_ttl = 86400  # 24 hours

    def check_for_updates(self):
        """Check if database needs updating"""
        if self.is_update_available():
            self.download_update()
            self.validate_update()
            self.apply_update()
            self.notify_admin()
```

## Clinical Decision Making

### Risk-Benefit Analysis
```
High Severity + High Documentation = Hard Stop
High Severity + Low Documentation = Warning + Allow Override
Low Severity + High Documentation = Passive Alert
Low Severity + Low Documentation = Suppress
```

### Clinical Context Matters
- **ICU**: Higher tolerance for managed interactions
- **Outpatient**: Lower threshold for warnings
- **Palliative Care**: Focus on symptom control
- **Pediatrics**: Extra caution
- **Geriatrics**: Increased sensitivity

## Quality Metrics

### Interaction Checking Performance
- **Alert Firing Rate**: % of orders triggering alerts
- **Override Rate**: % of alerts overridden
- **Override Reasons**: Categorization
- **Time to Override**: Measure workflow impact
- **Clinical Outcomes**: Adverse events prevented

## Best Practices

1. **Use Multiple Sources**: Cross-reference critical interactions
2. **Severity Appropriateness**: Don't cry wolf
3. **Clinical Context**: Consider setting and patient factors
4. **Evidence-Based**: Prefer high documentation quality
5. **Actionable**: Provide clear recommendations
6. **Alternatives**: Suggest safer options
7. **Monitor Updates**: Stay current with database versions
8. **Track Outcomes**: Measure clinical impact
9. **Allow Overrides**: Support clinical judgment
10. **Document Rationale**: Capture override reasons

## Resources
- First DataBank: https://www.fdb.com
- Micromedex: https://www.micromedexsolutions.com
- Lexicomp: https://online.lexi.com
- RxNav APIs: https://rxnav.nlm.nih.gov/
- DrugBank: https://go.drugbank.com
