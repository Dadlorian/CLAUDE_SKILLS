# Clinical Guidelines Reference

## Overview
Clinical practice guidelines are systematically developed statements to assist practitioner and patient decisions about appropriate healthcare for specific clinical circumstances. This reference covers guideline development, representation, and implementation in CDS systems.

## Guideline Development Frameworks

### GRADE (Grading of Recommendations Assessment, Development and Evaluation)

**Evidence Quality Levels**:
- **High (A)**: Further research very unlikely to change confidence in estimate
- **Moderate (B)**: Further research likely to have impact on confidence
- **Low (C)**: Further research very likely to have important impact
- **Very Low (D)**: Very uncertain about the estimate

**Recommendation Strength**:
- **Strong (1)**: "We recommend..."
- **Weak/Conditional (2)**: "We suggest..."

**Format**:
```
"We recommend X for Y patients (Strong recommendation, High-quality evidence)"
"1A" = Strong recommendation, High-quality evidence
"2C" = Weak recommendation, Low-quality evidence
```

**Example**:
```
Anticoagulation for Atrial Fibrillation:
"We recommend oral anticoagulation for AF patients with CHA₂DS₂-VASc ≥ 2 (1A)"
```

### Institute of Medicine (IOM) Standards

**8 Standards for Trustworthy Guidelines**:
1. Establish transparency
2. Manage conflict of interest
3. Develop multidisciplinary panel
4. Use systematic review
5. Establish evidence foundation
6. Articulate recommendations
7. Provide external review
8. Update guidelines

## Major Guideline Organizations

### Cardiovascular

#### American College of Cardiology (ACC) / American Heart Association (AHA)

**Key Guidelines**:
- **Hypertension** (2017): BP targets, treatment algorithms
- **Cholesterol** (2018/2019): ASCVD risk, statin therapy
- **Heart Failure** (2022): GDMT (guideline-directed medical therapy)
- **Atrial Fibrillation** (2023): Anticoagulation, rate/rhythm control
- **STEMI** (2013, updated 2015): Reperfusion strategies
- **Stable Ischemic Heart Disease** (2012): Medical management, revascularization

**Example Implementation**:
```javascript
// ACC/AHA Statin Guideline
function recommendStatin(patient) {
  const { age, ldl, diabetes, ascvd_risk, clinical_ascvd } = patient;

  // Group 1: Clinical ASCVD
  if (clinical_ascvd) {
    if (age < 75 || (age >= 75 && high_risk_factors)) {
      return {
        recommendation: "High-intensity statin",
        rationale: "Clinical ASCVD present",
        grade: "1A",
        options: ["Atorvastatin 40-80mg", "Rosuvastatin 20-40mg"]
      };
    }
  }

  // Group 2: LDL ≥ 190 mg/dL
  if (ldl >= 190) {
    return {
      recommendation: "High-intensity statin",
      rationale: "Severe hypercholesterolemia (LDL ≥ 190)",
      grade: "1A"
    };
  }

  // Group 3: Diabetes, age 40-75
  if (diabetes && age >= 40 && age <= 75) {
    if (ascvd_risk >= 0.075) {
      return {
        recommendation: "High-intensity statin",
        rationale: "Diabetes with 10-year ASCVD risk ≥ 7.5%",
        grade: "1A"
      };
    } else {
      return {
        recommendation: "Moderate-intensity statin",
        rationale: "Diabetes, age 40-75",
        grade: "1A"
      };
    }
  }

  // Group 4: Primary prevention, ASCVD risk ≥ 7.5%
  if (age >= 40 && age <= 75 && ldl >= 70 && ldl <= 189 && ascvd_risk >= 0.075) {
    return {
      recommendation: "Moderate-to-high intensity statin",
      rationale: "10-year ASCVD risk ≥ 7.5%",
      grade: "1A",
      note: "Discuss risk enhancers if borderline (5-7.4%)"
    };
  }

  return {
    recommendation: "No statin indicated by guideline",
    note: "Consider lifestyle modifications"
  };
}
```

### Infectious Disease

#### Infectious Diseases Society of America (IDSA)

**Key Guidelines**:
- **Community-Acquired Pneumonia** (2019)
- **Sepsis** (Surviving Sepsis Campaign, 2021)
- **Healthcare-Associated Infections** (various)
- **Antimicrobial Stewardship** (2016)

**Example: CAP Antibiotic Selection**
```javascript
function selectCAPAntibiotic(patient) {
  const { setting, severity, comorbidities, recent_antibiotics, risk_factors } = patient;

  // Outpatient
  if (setting === 'OUTPATIENT') {
    // Previously healthy, no antibiotics in 3 months
    if (!comorbidities.length && !recent_antibiotics) {
      return {
        options: [
          "Amoxicillin 1g TID",
          "Doxycycline 100mg BID",
          "Azithromycin 500mg day 1, then 250mg daily x 4"
        ],
        grade: "Strong recommendation, Moderate quality evidence"
      };
    }

    // Comorbidities or recent antibiotics
    return {
      options: [
        "Amoxicillin-clavulanate 2g BID + Macrolide",
        "Respiratory fluoroquinolone (levofloxacin, moxifloxacin)"
      ],
      grade: "Strong recommendation, Moderate quality evidence"
    };
  }

  // Inpatient non-ICU
  if (setting === 'INPATIENT' && severity !== 'SEVERE') {
    return {
      recommendation: "Beta-lactam + Macrolide OR Respiratory fluoroquinolone",
      options: [
        "Ceftriaxone 1g daily + Azithromycin 500mg daily",
        "Ampicillin-sulbactam 3g q6h + Azithromycin 500mg daily",
        "Levofloxacin 750mg daily"
      ],
      grade: "Strong recommendation, High quality evidence"
    };
  }

  // ICU
  if (setting === 'ICU' || severity === 'SEVERE') {
    let regimen = {
      base: "Beta-lactam + Macrolide OR Beta-lactam + Respiratory fluoroquinolone",
      options: [
        "Ceftriaxone 2g daily + Azithromycin 500mg daily",
        "Cefotaxime 2g q8h + Azithromycin 500mg daily"
      ]
    };

    // Add MRSA coverage if indicated
    if (risk_factors.mrsa) {
      regimen.add = "Vancomycin or Linezolid";
      regimen.indication = "MRSA risk factors: prior MRSA, IV drug use";
    }

    // Add Pseudomonas coverage if indicated
    if (risk_factors.pseudomonas) {
      regimen.base = "Antipseudomonal beta-lactam";
      regimen.options = [
        "Piperacillin-tazobactam 4.5g q6h + Azithromycin",
        "Cefepime 2g q8h + Azithromycin"
      ];
    }

    return regimen;
  }
}
```

### Diabetes

#### American Diabetes Association (ADA) Standards of Care

**Key Areas**:
- **Glycemic Targets**: A1C < 7% for most, individualized
- **Screening**: Age ≥ 35 or earlier with risk factors
- **Pharmacotherapy**: Metformin first-line, add-on based on comorbidities
- **Cardiovascular Risk**: Statin for most, SGLT2i/GLP-1 RA for CVD

**Example: Diabetes Medication Selection**
```javascript
function recommendDiabetesMedication(patient) {
  const { a1c, gfr, cvd, heart_failure, weight_goals, hypoglycemia_risk } = patient;

  let recommendations = [];

  // First-line: Metformin (unless contraindicated)
  if (gfr >= 30 && !patient.contraindications.includes('metformin')) {
    recommendations.push({
      drug_class: "Metformin",
      position: "First-line",
      rationale: "Proven efficacy, low cost, weight neutral",
      dose: "Start 500mg daily, titrate to 1000mg BID"
    });
  }

  // Established ASCVD or HF: Specific agents
  if (cvd || heart_failure) {
    if (heart_failure || gfr >= 20) {
      recommendations.push({
        drug_class: "SGLT2 inhibitor",
        position: "Add to metformin (or first-line if metformin contraindicated)",
        rationale: cvd ? "Cardiovascular benefit proven" : "Heart failure benefit",
        options: ["Empagliflozin", "Canagliflozin", "Dapagliflozin"],
        grade: "1A"
      });
    }

    if (cvd) {
      recommendations.push({
        drug_class: "GLP-1 receptor agonist",
        position: "Alternative or addition to SGLT2i",
        rationale: "Cardiovascular benefit proven",
        options: ["Dulaglutide", "Liraglutide", "Semaglutide"],
        grade: "1A"
      });
    }
  }

  // Weight loss goals
  if (weight_goals === 'IMPORTANT' && a1c > 7) {
    recommendations.push({
      drug_class: "GLP-1 receptor agonist",
      rationale: "Weight loss benefit",
      expected_weight_loss: "3-5 kg"
    });
  }

  // Hypoglycemia risk: Avoid insulin/sulfonylureas if possible
  if (hypoglycemia_risk === 'HIGH') {
    recommendations.push({
      avoid: ["Insulin", "Sulfonylureas"],
      rationale: "High hypoglycemia risk",
      prefer: ["DPP-4 inhibitors", "GLP-1 RA", "SGLT2i"]
    });
  }

  return recommendations;
}
```

### Cancer Screening

#### U.S. Preventive Services Task Force (USPSTF)

**Recommendation Grades**:
- **A**: High certainty of substantial net benefit - **Recommend**
- **B**: High certainty of moderate net benefit or moderate certainty of moderate-to-substantial benefit - **Recommend**
- **C**: Moderate certainty of small net benefit - **Selective offering**
- **D**: Moderate-to-high certainty of no net benefit or harm outweighs benefit - **Discourage**
- **I**: Insufficient evidence

**Example: Screening Recommendations**
```javascript
function screeningRecommendations(patient) {
  const { age, sex, smoking_history, family_history, risk_factors } = patient;
  let screens = [];

  // Colorectal cancer (Grade A)
  if (age >= 45 && age <= 75) {
    screens.push({
      test: "Colorectal cancer screening",
      grade: "A",
      options: [
        "Colonoscopy every 10 years",
        "FIT (fecal immunochemical test) annually",
        "Cologuard every 3 years",
        "CT colonography every 5 years"
      ]
    });
  }

  // Breast cancer (Grade B)
  if (sex === 'F' && age >= 50 && age <= 74) {
    screens.push({
      test: "Mammography",
      frequency: "Every 2 years",
      grade: "B"
    });
  }

  // Lung cancer (Grade B)
  const pack_years = smoking_history.pack_years;
  const years_since_quit = smoking_history.years_since_quit;

  if (age >= 50 && age <= 80 &&
      pack_years >= 20 &&
      (smoking_history.current || years_since_quit <= 15)) {
    screens.push({
      test: "Low-dose CT chest",
      frequency: "Annual",
      grade: "B",
      stop_when: "15 years since quit or limited life expectancy"
    });
  }

  // Cervical cancer (Grade A)
  if (sex === 'F' && age >= 21 && age <= 65) {
    if (age < 30) {
      screens.push({
        test: "Cervical cytology (Pap) alone",
        frequency: "Every 3 years",
        grade: "A"
      });
    } else {
      screens.push({
        test: "Cervical cancer screening",
        options: [
          "Cytology alone every 3 years",
          "hrHPV testing alone every 5 years",
          "Cytology + hrHPV (co-testing) every 5 years"
        ],
        grade: "A"
      });
    }
  }

  // Prostate cancer (Grade C - selective)
  if (sex === 'M' && age >= 55 && age <= 69) {
    screens.push({
      test: "PSA screening",
      grade: "C",
      recommendation: "Individual decision - discuss risks/benefits",
      note: "Small potential benefit, risk of overdiagnosis/overtreatment"
    });
  }

  return screens;
}
```

## Guideline Representation Standards

### Arden Syntax
Medical Logic Modules (MLMs) for encoding clinical knowledge

### GLIF (GuideLine Interchange Format)
Structured representation for shareable guidelines

### GEM (Guideline Elements Model)
XML-based format for guideline representation

### CQL (Clinical Quality Language)
HL7 standard for expressing clinical logic

**Example CQL**:
```cql
library HypertensionManagement version '1.0'

using FHIR version '4.0.1'

context Patient

define "Has Hypertension":
  exists([Condition: "Hypertension"] C
    where C.clinicalStatus ~ "active")

define "Most Recent BP":
  Last(
    [Observation: "Blood Pressure"] BP
    where BP.status = 'final'
    sort by effective.value desc
  )

define "BP Above Goal":
  "Most Recent BP".component.where(code ~ "Systolic BP").value > 130 'mm[Hg]'
    or "Most Recent BP".component.where(code ~ "Diastolic BP").value > 80 'mm[Hg]'

define "On ACE Inhibitor or ARB":
  exists([MedicationRequest: "ACE Inhibitors"])
    or exists([MedicationRequest: "ARBs"])

define "Needs Medication Intensification":
  "Has Hypertension"
    and "BP Above Goal"
    and not "On ACE Inhibitor or ARB"
```

## Implementing Guidelines in CDS

### Rule-Based Implementation
```javascript
class GuidelineEngine {
  constructor() {
    this.guidelines = this.loadGuidelines();
  }

  evaluatePatient(patient) {
    const recommendations = [];

    // Evaluate each guideline
    for (const guideline of this.guidelines) {
      if (this.isApplicable(guideline, patient)) {
        const recs = guideline.evaluate(patient);
        recommendations.push(...recs);
      }
    }

    // Prioritize and deduplicate
    return this.prioritize(recommendations);
  }

  isApplicable(guideline, patient) {
    // Check inclusion/exclusion criteria
    if (guideline.age_range) {
      if (patient.age < guideline.age_range.min ||
          patient.age > guideline.age_range.max) {
        return false;
      }
    }

    if (guideline.required_conditions) {
      const hasRequired = guideline.required_conditions.every(
        cond => patient.conditions.includes(cond)
      );
      if (!hasRequired) return false;
    }

    return true;
  }
}
```

### Monitoring Guideline Adherence

```javascript
class GuidelineCompliance {
  calculateCompliance(population, guideline) {
    let eligible = 0;
    let compliant = 0;

    for (const patient of population) {
      if (guideline.isEligible(patient)) {
        eligible++;

        if (guideline.isCompliant(patient)) {
          compliant++;
        }
      }
    }

    return {
      eligible_patients: eligible,
      compliant_patients: compliant,
      compliance_rate: compliant / eligible,
      gaps: this.identifyGaps(population, guideline)
    };
  }

  identifyGaps(population, guideline) {
    return population
      .filter(p => guideline.isEligible(p) && !guideline.isCompliant(p))
      .map(p => ({
        patient_id: p.id,
        gap_reason: guideline.identifyGap(p)
      }));
  }
}
```

## Guideline Update Management

### Version Control
```javascript
const guidelineVersion = {
  id: "hypertension_2017",
  title: "ACC/AHA Hypertension Guideline",
  version: "2017.1",
  published: "2017-11-13",
  effective_date: "2018-01-01",
  supersedes: "JNC-8_2014",

  major_changes: [
    "Lowered BP threshold to 130/80",
    "Removed JNC categories, using ACC/AHA categories",
    "Updated medication recommendations"
  ],

  next_review: "2024-01-01"
};
```

## Resources

### Guideline Repositories
- **National Guideline Clearinghouse** (NGC) - Archived 2018
- **ECRI Guidelines Trust**: https://guidelines.ecri.org
- **NICE** (UK): https://www.nice.org.uk
- **GRADE Working Group**: https://www.gradeworkinggroup.org

### Specialty Organizations
- ACC/AHA: https://www.acc.org/guidelines
- IDSA: https://www.idsociety.org/practice-guideline
- ADA: https://diabetesjournals.org/care/issue/46/Supplement_1
- USPSTF: https://www.uspreventiveservicestaskforce.org

### Implementation Tools
- CDS Connect: https://cds.ahrq.gov/cdsconnect
- OpenCDS: https://www.opencds.org
- CQL Testing: https://cql.hl7.org
