# Clinical Risk Scores Reference

## Overview
Clinical risk scores and calculators are validated tools that quantify patient risk for various conditions, guide treatment decisions, and stratify patients for interventions.

## Cardiovascular Risk Scores

### CHADS₂-VASc (Stroke Risk in Atrial Fibrillation)

**Purpose**: Estimate stroke risk in atrial fibrillation patients

**Components**:
| Factor | Points |
|--------|--------|
| **C**HF | 1 |
| **H**ypertension | 1 |
| **A**ge ≥ 75 | 2 |
| **D**iabetes | 1 |
| **S**troke/TIA/TE history | 2 |
| **V**ascular disease (MI, PAD, aortic plaque) | 1 |
| **A**ge 65-74 | 1 |
| **Sc** Sex (Female) | 1 |

**Score Interpretation**:
| Score | Annual Stroke Risk | Recommendation |
|-------|-------------------|----------------|
| 0 (male), 1 (female) | 0-1% | Consider no anticoagulation or aspirin |
| 1 (male), 2 (female) | 1-2% | Consider anticoagulation |
| ≥ 2 | 2-15% | Anticoagulation recommended |

**Implementation**:
```javascript
function calculateCHADSVASc(patient) {
  let score = 0;

  if (patient.conditions.includes('CHF')) score += 1;
  if (patient.conditions.includes('Hypertension')) score += 1;
  if (patient.age >= 75) score += 2;
  else if (patient.age >= 65) score += 1;
  if (patient.conditions.includes('Diabetes')) score += 1;
  if (patient.conditions.includes('Stroke') ||
      patient.conditions.includes('TIA')) score += 2;
  if (patient.conditions.includes('Vascular Disease')) score += 1;
  if (patient.sex === 'F') score += 1;

  return {
    score: score,
    risk: getRiskCategory(score, patient.sex),
    recommendation: getRecommendation(score, patient.sex)
  };
}
```

### HAS-BLED (Bleeding Risk on Anticoagulation)

**Purpose**: Estimate major bleeding risk on anticoagulation

**Components**:
| Factor | Points |
|--------|--------|
| **H**ypertension (SBP > 160) | 1 |
| **A**bnormal renal/liver function (1 point each) | 1-2 |
| **S**troke history | 1 |
| **B**leeding history or predisposition | 1 |
| **L**abile INR (if on warfarin) | 1 |
| **E**lderly (age > 65) | 1 |
| **D**rugs (antiplatelet, NSAIDs) or alcohol | 1-2 |

**Score Interpretation**:
- **0-2**: Low risk (1.1% per year)
- **3-4**: Moderate risk (4.9% per year)
- **≥ 5**: High risk (8.4% per year)

**Note**: High HAS-BLED doesn't contraindicate anticoagulation; it suggests need for closer monitoring

### ASCVD Risk Calculator (10-Year Cardiovascular Risk)

**Purpose**: Estimate 10-year risk of atherosclerotic cardiovascular disease

**Input Variables**:
- Age (40-79)
- Sex
- Race (White/African American/Other)
- Total cholesterol
- HDL cholesterol
- Systolic blood pressure
- BP treatment status
- Diabetes status
- Smoking status

**Risk Categories**:
- **< 5%**: Low risk
- **5-7.4%**: Borderline risk
- **7.5-19.9%**: Intermediate risk
- **≥ 20%**: High risk

**Treatment Recommendations**:
| Risk | LDL | Recommendation |
|------|-----|----------------|
| High (≥ 20%) | Any | High-intensity statin |
| Intermediate (7.5-19.9%) | ≥ 70 | Moderate-to-high intensity statin |
| Borderline (5-7.4%) | ≥ 70 | Discuss statin, consider risk enhancers |
| Low (< 5%) | ≥ 190 | Statin therapy |

### TIMI Score (ACS Risk Stratification)

**TIMI Score for STEMI**:
| Factor | Points |
|--------|--------|
| Age 65-74 | 2 |
| Age ≥ 75 | 3 |
| Diabetes, HTN, or angina | 1 |
| SBP < 100 mmHg | 3 |
| HR > 100 | 2 |
| Killip class II-IV | 2 |
| Weight < 67 kg | 1 |
| Anterior STEMI or LBBB | 1 |
| Time to treatment > 4 hours | 1 |

**TIMI Score for NSTEMI/UA**:
| Factor | Points |
|--------|--------|
| Age ≥ 65 | 1 |
| ≥ 3 CAD risk factors | 1 |
| Known CAD (stenosis ≥ 50%) | 1 |
| Aspirin use in last 7 days | 1 |
| ≥ 2 anginal events in 24 hours | 1 |
| ST deviation ≥ 0.5 mm | 1 |
| Elevated cardiac markers | 1 |

## Thromboembolism Risk

### Wells Criteria (DVT)

**Clinical Feature** | **Points**
|---|---|
| Active cancer | 1 |
| Paralysis/recent immobilization | 1 |
| Bedridden > 3 days or major surgery < 12 weeks | 1 |
| Tenderness along deep veins | 1 |
| Entire leg swollen | 1 |
| Calf swelling > 3 cm vs other leg | 1 |
| Pitting edema (symptomatic leg) | 1 |
| Collateral superficial veins | 1 |
| Alternative diagnosis likely | -2 |

**Interpretation**:
- **≤ 0**: Low probability (5%) - D-dimer
- **1-2**: Moderate probability (17%) - D-dimer
- **≥ 3**: High probability (53%) - Ultrasound

### Wells Criteria (PE)

| Clinical Feature | Points |
|---|---|
| Clinical signs of DVT | 3.0 |
| PE most likely diagnosis | 3.0 |
| HR > 100 | 1.5 |
| Immobilization/surgery in last 4 weeks | 1.5 |
| Previous DVT/PE | 1.5 |
| Hemoptysis | 1.0 |
| Malignancy | 1.0 |

**Interpretation**:
- **< 2**: PE unlikely - D-dimer
- **2-6**: Moderate probability
- **> 6**: PE likely - CTA

### Caprini Score (VTE Risk Surgical Patients)

**Risk Factor** | **Points**
|---|---|
| Age 41-60 | 1 |
| Minor surgery | 1 |
| BMI > 25 | 1 |
| Oral contraceptives/HRT | 1 |
| Age 61-74 | 2 |
| Arthroscopic surgery | 2 |
| Major open surgery (> 45 min) | 2 |
| Laparoscopic surgery (> 45 min) | 2 |
| History of DVT/PE | 3 |
| Age ≥ 75 | 3 |
| Stroke (< 1 month) | 5 |
| Elective arthroplasty | 5 |
| Hip/pelvis/leg fracture | 5 |

**Prophylaxis**:
- **0-1**: Early ambulation
- **2**: SCDs or LMWH
- **3-4**: SCDs + LMWH
- **≥ 5**: SCDs + LMWH + extended prophylaxis

## Critical Care Scores

### APACHE II (ICU Mortality)

**Components**:
1. **Acute Physiology Score** (0-60 points): Temperature, MAP, HR, RR, A-a gradient, pH, Na, K, Cr, Hct, WBC, GCS
2. **Age Points** (0-6): Age-based scoring
3. **Chronic Health Points** (0-5): Chronic organ insufficiency

**Score Range**: 0-71
**Mortality Correlation**:
- 0-4: 4% mortality
- 5-9: 8% mortality
- 10-14: 15% mortality
- 15-19: 25% mortality
- 20-24: 40% mortality
- 25-29: 55% mortality
- 30-34: 75% mortality
- ≥ 35: 85% mortality

### SOFA Score (Sequential Organ Failure Assessment)

**Organ Systems**:
| System | 0 | 1 | 2 | 3 | 4 |
|--------|---|---|---|---|---|
| **Respiration** (PaO2/FiO2) | ≥400 | <400 | <300 | <200 | <100 |
| **Coagulation** (Platelets) | ≥150 | <150 | <100 | <50 | <20 |
| **Liver** (Bilirubin mg/dL) | <1.2 | 1.2-1.9 | 2.0-5.9 | 6.0-11.9 | ≥12.0 |
| **Cardiovascular** (MAP/pressors) | MAP≥70 | MAP<70 | Dopa≤5 | Dopa>5 | Dopa>15 |
| **CNS** (GCS) | 15 | 13-14 | 10-12 | 6-9 | <6 |
| **Renal** (Cr or UO) | <1.2 | 1.2-1.9 | 2.0-3.4 | 3.5-4.9 | >5.0 |

**Interpretation**:
- **Sepsis-3 Definition**: Increase of ≥ 2 points suggests sepsis
- **Mortality**: Each 1-point increase = 10% increase in mortality

### qSOFA (Quick SOFA)

**Components** (1 point each):
- Respiratory rate ≥ 22/min
- Altered mental status (GCS < 15)
- Systolic BP ≤ 100 mmHg

**Score ≥ 2**: Suggests sepsis, warrants further evaluation

## Renal Function Calculators

### CKD-EPI eGFR

**Formula** (most accurate for adults):
```javascript
function calculateCKD_EPI(creatinine, age, sex, race) {
  const k = (sex === 'F') ? 0.7 : 0.9;
  const a = (sex === 'F') ? -0.329 : -0.411;
  const female_factor = (sex === 'F') ? 1.018 : 1;
  const black_factor = (race === 'Black') ? 1.159 : 1;

  const min = Math.min(creatinine / k, 1);
  const max = Math.max(creatinine / k, 1);

  const eGFR = 141 * Math.pow(min, a) * Math.pow(max, -1.209) *
               Math.pow(0.993, age) * female_factor * black_factor;

  return {
    eGFR: Math.round(eGFR),
    stage: getCKDStage(eGFR)
  };
}

function getCKDStage(eGFR) {
  if (eGFR >= 90) return "G1 - Normal";
  if (eGFR >= 60) return "G2 - Mild decrease";
  if (eGFR >= 45) return "G3a - Mild-moderate decrease";
  if (eGFR >= 30) return "G3b - Moderate-severe decrease";
  if (eGFR >= 15) return "G4 - Severe decrease";
  return "G5 - Kidney failure";
}
```

### Cockcroft-Gault (Drug Dosing)

```javascript
function cockcroftGault(creatinine, age, weight, sex) {
  const female_factor = (sex === 'F') ? 0.85 : 1;

  const CrCl = ((140 - age) * weight * female_factor) / (72 * creatinine);

  return {
    creatinine_clearance: Math.round(CrCl),
    recommendation: getDrugDosingRec(CrCl)
  };
}
```

## Fracture Risk

### FRAX (10-Year Fracture Risk)

**Input Variables**:
- Age (40-90)
- Sex
- Weight, Height
- Previous fracture
- Parental hip fracture
- Current smoking
- Glucocorticoids
- Rheumatoid arthritis
- Secondary osteoporosis
- Alcohol ≥ 3 units/day
- Femoral neck BMD (optional)

**Outputs**:
- 10-year probability of major osteoporotic fracture
- 10-year probability of hip fracture

**Treatment Thresholds** (USA):
- Major osteoporotic fracture ≥ 20%: Treat
- Hip fracture ≥ 3%: Treat

## Fall Risk

### Morse Fall Scale

| Risk Factor | Score |
|-------------|-------|
| History of falling | 25 |
| Secondary diagnosis | 15 |
| Ambulatory aid: None/Bedrest | 0 |
| Ambulatory aid: Crutches/Cane | 15 |
| Ambulatory aid: Furniture | 30 |
| IV/Heparin lock | 20 |
| Gait: Normal | 0 |
| Gait: Weak | 10 |
| Gait: Impaired | 20 |
| Mental status: Oriented | 0 |
| Mental status: Overestimates ability | 15 |

**Risk Levels**:
- **0-24**: Low risk
- **25-50**: Moderate risk
- **≥ 51**: High risk

## Delirium Assessment

### CAM-ICU (Confusion Assessment Method)

**Criteria** (must have 1 AND 2, plus 3 OR 4):
1. Acute onset or fluctuating course
2. Inattention
3. Disorganized thinking
4. Altered level of consciousness

## Pregnancy Risk

### Bishop Score (Cervical Ripeness)

| Factor | 0 | 1 | 2 | 3 |
|--------|---|---|---|---|
| Dilation (cm) | 0 | 1-2 | 3-4 | ≥5 |
| Effacement (%) | 0-30 | 40-50 | 60-70 | ≥80 |
| Station | -3 | -2 | -1, 0 | +1, +2 |
| Consistency | Firm | Medium | Soft | - |
| Position | Posterior | Mid | Anterior | - |

**Score ≥ 8**: Favorable for induction

## Implementation Best Practices

### 1. Validation
```javascript
function validateInputs(inputs, calculator) {
  const errors = [];

  for (const [field, value] of Object.entries(inputs)) {
    const rules = calculator.validation[field];

    if (rules.required && !value) {
      errors.push(`${field} is required`);
    }

    if (rules.min && value < rules.min) {
      errors.push(`${field} must be >= ${rules.min}`);
    }

    if (rules.max && value > rules.max) {
      errors.push(`${field} must be <= ${rules.max}`);
    }
  }

  return errors;
}
```

### 2. Unit Handling
```javascript
function convertUnits(value, fromUnit, toUnit) {
  const conversions = {
    'mg/dL_to_mmol/L': (v) => v * 0.0555,  // Glucose
    'lb_to_kg': (v) => v * 0.453592,
    'in_to_cm': (v) => v * 2.54,
    'F_to_C': (v) => (v - 32) * 5/9
  };

  const key = `${fromUnit}_to_${toUnit}`;
  return conversions[key] ? conversions[key](value) : value;
}
```

### 3. Missing Data Handling
```javascript
function handleMissingData(calculator, inputs) {
  // Use default values
  if (!inputs.race && calculator.allowsDefaultRace) {
    inputs.race = 'Other';
  }

  // Calculate alternatives
  if (!inputs.BMD && inputs.weight && inputs.height) {
    // Use clinical risk factors only version
    return calculateWithoutBMD(inputs);
  }

  // Indicate limitations
  if (inputs.missing.length > 0) {
    return {
      score: calculateScore(inputs),
      limitations: `Missing: ${inputs.missing.join(', ')}`
    };
  }
}
```

## Resources
- MDCalc: https://www.mdcalc.com
- QxMD Calculate: https://qxmd.com/calculate
- FRAX Tool: https://www.sheffield.ac.uk/FRAX/
- ACC ASCVD Risk Calculator: http://tools.acc.org/ascvd-risk-estimator-plus/
