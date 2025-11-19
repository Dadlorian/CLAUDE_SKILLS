# LOINC and RxNorm Reference Guide

## LOINC (Logical Observation Identifiers Names and Codes)

### Overview

LOINC standardizes the coding and identification of lab tests, clinical observations, and other medical measurements. Critical for laboratory and imaging results exchange.

### LOINC Structure

#### Code Format
- **6-digit numeric code** (e.g., 2345-7)
- **Unique identifier** - No duplicates
- **International standard** - Used globally

#### Components
```
ANALYTE = LOINC code 2345-7
├─ Component: Glucose
├─ Property: Mass concentration
├─ Time aspect: Point in time
├─ System: Serum or plasma
├─ Scale: Quantitative
└─ Method: Not specified
```

### LOINC Hierarchy

| Level | Type | Examples |
|-------|------|----------|
| Class | System | Chemistry, Hematology, Microbiology |
| Subclass | Analyte | Glucose, Hemoglobin, Blood culture |
| Component | Measurement | Glucose measurement |
| Property | Type | Mass concentration, Electric potential |
| Timing | Duration | Point in time, 24 hour |
| System | Specimen | Serum, Plasma, Whole blood |
| Scale | Numeric type | Quantitative, Ordinal, Nominal |
| Method | Technique | Enzymatic, Spectrophotometric |

### Common Lab LOINC Codes

| Code | Test | Type |
|------|------|------|
| 2345-7 | Glucose | Chemistry |
| 2951-2 | Sodium | Chemistry |
| 2823-3 | Potassium | Chemistry |
| 1975-2 | Albumin | Chemistry |
| 2030-8 | Hemoglobin | Hematology |
| 789-8 | WBC | Hematology |
| 718-7 | Hemoglobin A1C | Hematology |
| 8480-6 | Systolic BP | Vital Signs |
| 8462-4 | Diastolic BP | Vital Signs |
| 3141-9 | Body weight | Vital Signs |
| 3137-1 | Body height | Vital Signs |

### LOINC Implementation

#### FHIR Integration
```json
{
  "resourceType": "Observation",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "2345-7",
      "display": "Glucose [Mass/volume] in Serum or Plasma"
    }]
  },
  "valueQuantity": {
    "value": 95,
    "unit": "mg/dL",
    "system": "http://unitsofmeasure.org",
    "code": "mg/dL"
  }
}
```

#### Reference Ranges
```json
{
  "referenceRange": [{
    "low": {"value": 70, "unit": "mg/dL"},
    "high": {"value": 100, "unit": "mg/dL"},
    "text": "Normal fasting glucose"
  }]
}
```

### LOINC Data Elements

#### Panel/Battery
- Group related tests
- Multiple observations in one order
- Example: Comprehensive Metabolic Panel (CMP)

#### HL7 Order Codes
- Used for lab order placement
- Maps to electronic ordering systems
- Example: OBR segment in HL7 v2

### LOINC Challenges

1. **Large database** - Over 90,000 codes
2. **Specificity** - Multiple codes for similar tests
3. **Regular updates** - Quarterly new codes/changes
4. **Mapping complexity** - Legacy system mapping
5. **Reference range variations** - Lab-specific normal ranges

---

## RxNorm (Drug Terminology Standard)

### Overview

RxNorm provides standardized nomenclature for clinical drugs. Used for medication orders, dispensing, and clinical decision support.

### RxNorm Structure

#### Drug Components
1. **Ingredient** - Active pharmaceutical ingredient (API)
2. **Strength** - Dose amount
3. **Form** - Physical form (tablet, injection, etc.)
4. **Formulation** - Combination of above

### RxNorm Code Types

#### TTY (Term Type)

| Code | Type | Example |
|------|------|---------|
| IN | Ingredient | Metformin |
| PIN | Precise Ingredient | Metformin Hydrochloride |
| MIN | Multiple Ingredients | Metformin/Lisinopril |
| BN | Brand Name | Glucophage |
| SBDF | Semantic Branded Dose Form | Metformin HCl 500mg Oral Tablet |
| SBD | Semantic Brand Dose | Glucophage 500mg Oral Tablet |
| SCDF | Semantic Clinical Dose Form | Metformin HCl 500mg Oral Tablet |
| SCD | Semantic Clinical Dose | Metformin 500mg Oral Tablet |
| BPCK | Brand Name From Package | Glucophage 500mg Tablets |
| GPCK | Generic Package | Metformin HCl 500mg Tablets |

### RxNorm Codes

```
RxNorm CUI (Concept Unique Identifier)
├─ C0025598 = Metformin
├─ C0987409 = Metformin 500mg
├─ C1145609 = Metformin 500mg Tablet
└─ C1147195 = Glucophage (Metformin) 500mg Tablet
```

### Common RxNorm Medications

| Code | Drug | Strength |
|------|------|----------|
| 860220 | Metformin | 1000 MG |
| 314076 | Lisinopril | 10 MG |
| 200308 | Atorvastatin | 20 MG |
| 331088 | Amlodipine | 5 MG |
| 329526 | Omeprazole | 20 MG |
| 876637 | Fluticasone/Salmeterol | 100/50 MCG |

### Relationships in RxNorm

#### PAR (Parent)
- Ingredient to drug ingredient
- Simplest to most specific form

#### RB (Related By)
- Maps related concepts
- Different forms of same drug
- Generic/brand relationships

#### Example Hierarchy
```
Metformin (Ingredient)
  ├─ Metformin HCl (Precise Ingredient)
  │   ├─ Metformin HCl 500mg (Ingredient/Strength)
  │   │   ├─ Metformin HCl 500mg Tablet (Dose Form)
  │   │   │   ├─ Glucophage 500mg Tablet (Brand)
  │   │   │   └─ Metformin HCl 500mg Tablet (Generic)
```

### RxNorm Implementation

#### FHIR Integration
```json
{
  "resourceType": "MedicationRequest",
  "medicationCodeableConcept": {
    "coding": [{
      "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
      "code": "860220",
      "display": "metformin 500 MG Oral Tablet"
    }]
  },
  "dosageInstruction": [{
    "timing": {"repeat": {"frequency": 2, "period": 1, "periodUnit": "d"}},
    "doseAndRate": {
      "doseQuantity": {
        "value": 1,
        "unit": "Tablet",
        "system": "http://unitsofmeasure.org",
        "code": "{tablet}"
      }
    }
  }]
}
```

#### RxNorm APIs
```
// Look up drug information
GET /REST/rxcui?name=metformin

// Get drug properties
GET /REST/rxcui/860220/properties

// Get related concepts
GET /REST/rxcui/860220/related?tty=SBD,SCD

// Find alternatives
GET /REST/rxcui/860220/allrelatives
```

### RxNorm Challenges

1. **Complexity** - Many forms of same drug
2. **Updates** - Monthly additions/changes
3. **Mapping** - Legacy drug codes difficult to map
4. **Substitution** - Generic/brand selection logic
5. **Dosing** - Strength/form combinations

### RxNorm vs Other Standards

| Aspect | RxNorm | SNOMED | NDC |
|--------|--------|--------|-----|
| Scope | Clinical drugs | All clinical concepts | Dispensable products |
| Specificity | Dose form | Generic/detailed | Specific product |
| Usage | Orders, guidelines | General clinical | Billing/dispensing |
| Updates | Monthly | Quarterly | Real-time |

### Drug Lookup Tools

- **RxNav** - Official browser and API
- **FHIR Terminology Servers** - REST access
- **RxClass** - Drug classification
- **DailyMed** - Labeling information
- **DrugBank** - Additional drug data

### Workflow Integration

#### Medication Ordering
```
1. User enters drug name or partial name
2. System calls RxNorm lookup API
3. Returns matching concepts (multiple options)
4. User selects specific drug and strength
5. Dose form and instructions added
6. System stores RxNorm code
7. Can map to NDC for pharmacy dispensing
```

#### Drug Interactions
```
1. MedicationRequest contains RxNorm codes
2. Clinical decision support queries API
3. Gets ingredient information (RxNorm ingredients)
4. Checks against interaction database
5. Returns warnings if interactions found
6. Alerts prescriber
```

## LOINC and RxNorm Integration

### Combined Healthcare Workflow
```
Lab Order (LOINC codes)
    ↓
Lab System processes
    ↓
Lab Results (LOINC codes + values)
    ↓
EHR receives results
    ↓
Clinical Decision Support analyzes
    ↓
May suggest medication
    ↓
RxNorm code selected
    ↓
Prescription written with RxNorm
    ↓
Pharmacy fills with NDC code
```

### Key Points
- **LOINC** for observations and lab results
- **RxNorm** for medications and drugs
- **SNOMED** for conditions and procedures
- **Each serves specific purpose**
- **Integration essential for complete EHR**

### Quality Metrics
- Correct terminology usage
- Regular updates and validation
- Proper code mapping
- Audit trails for changes
- User education and training
