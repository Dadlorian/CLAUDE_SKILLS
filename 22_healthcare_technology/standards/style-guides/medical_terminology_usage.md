# Medical Terminology Usage Standards

## Executive Summary

This document establishes comprehensive standards for medical terminology implementation in healthcare technology systems, ensuring interoperability, clinical accuracy, and regulatory compliance through SNOMED CT, LOINC, RxNorm, and related coding systems.

---

## 1. SNOMED CT (Systematized Nomenclature of Medicine Clinical Terms)

### 1.1 Overview and Compliance

**SNOMED CT** is the international clinical terminology standard for electronic health records, supporting:
- Comprehensive clinical documentation
- Clinical research and analytics
- Interoperability between healthcare systems
- Quality measurement and reporting

**License Status**: Implementations must use licensed SNOMED CT distribution

### 1.2 SNOMED CT Concept Structure

```
Concept ID: 73211009
Preferred Term: Diabetes mellitus
Semantic Tag: (disorder)
FSN: "Diabetes mellitus (disorder)"
Descriptions:
  - "Type 1 diabetes mellitus"
  - "Insulin-dependent diabetes"
  - "Juvenile diabetes"
```

#### Key Hierarchies

| Hierarchy | Root Concept | Usage |
|-----------|--------------|-------|
| Clinical Finding | 404684003 | Signs, symptoms, diagnoses |
| Procedure | 71388002 | Medical procedures |
| Medication | 373873005 | Pharmaceutical substances |
| Body Structure | 123037004 | Anatomical locations |
| Organism | 410607006 | Pathogens, bacteria |
| Substance | 105590001 | Chemical compounds |

### 1.3 Implementation Requirements

#### Concept Selection Protocol
```
Step 1: Identify clinical concept (e.g., "elevated glucose")
Step 2: Search SNOMED CT preferred terms
Step 3: Select most specific concept
Step 4: Verify semantic tag matches clinical meaning
Step 5: Map to local system codes (ICD-10, ICD-9-CM)
Step 6: Document rationale in change log
```

#### Common Diagnosis Mappings

| Clinical Presentation | SNOMED CT Concept | ICD-10 | Rationale |
|----------------------|-------------------|--------|-----------|
| Type 2 Diabetes | 44054006 | E11.9 | Endocrine disorder |
| Hypertension | 59621000 | I10 | Chronic condition |
| Acute MI (STEMI) | 57054005 | I21.0 | Acute coronary event |
| Pneumonia (bacterial) | 53084003 | J15.9 | Infectious disease |
| Heart failure (systolic) | 48694002 | I50.20 | Cardiac dysfunction |

### 1.4 Clinical Document Architecture (CDA) Integration

```xml
<!-- CDA Coded Problem Entry -->
<entry typeCode="DRIV">
  <act classCode="ACT" moodCode="EVN">
    <templateId root="2.16.840.1.113883.10.20.22.4.4"/>
    <code code="PROBLEM"
          codeSystem="2.16.840.1.113883.6.96"/>
    <entryRelationship typeCode="SUBJ">
      <observation classCode="OBS" moodCode="EVN">
        <code code="64572001"
              codeSystem="2.16.840.1.113883.6.96"
              codeSystemName="SNOMED CT"
              displayName="Disease (disorder)"/>
        <value xsi:type="CD"
               code="44054006"
               codeSystem="2.16.840.1.113883.6.96"
               displayName="Type 2 diabetes mellitus"/>
        <statusCode code="completed"/>
        <effectiveTime>
          <low value="20230115"/>
        </effectiveTime>
      </observation>
    </entryRelationship>
  </act>
</entry>
```

### 1.5 SNOMED CT Versioning and Updates

**Release Cycle**: January and July (International)

```
Version Format: YYYYMMDD
Example: 20250131 (January 31, 2025 release)

Implementation Requirements:
- Document SNOMED CT version in all exports
- Map legacy codes when upgrading versions
- Maintain version-specific search indices
- Test compatibility with downstream systems
```

---

## 2. LOINC (Logical Observation Identifiers Names and Codes)

### 2.1 LOINC Overview

**LOINC** is the standard for laboratory and clinical observations:
- 100,000+ unique observations
- Supports both clinical and research laboratory tests
- Required for laboratory results exchange (HL7 v2.5+)
- Regulatory requirement for meaningful use

### 2.2 LOINC Code Structure

```
LOINC Code: 2345-7
Analyte: Glucose [Mass/volume] in Serum or Plasma
System: Serum or Plasma
Method: Direct measurement
Time aspect: Point in time (not 24-hour)
Class: Chemistry

Full Format:
[COMPONENT]-[PROPERTY]-[TIME ASPECT]-[SYSTEM]-[SCALE]-[METHOD]-[RELATED OBSERVATIONS]
```

#### Essential Components

| Component | Example | Notes |
|-----------|---------|-------|
| Component | Glucose | What is being measured |
| Property | Mass concentration | Type of property (mass, volume, etc.) |
| Time Aspect | Pt (point) | Moment or interval |
| System | Ser/Plas | Specimen type |
| Scale | Qn (quantitative) | Numeric or categorical |
| Method | Direct | Measurement technique |

### 2.3 Common Laboratory Tests LOINC Mapping

```
CHEMISTRY:
  Glucose, fasting       → 2345-7      (mg/dL)
  Creatinine, serum      → 2160-0      (mg/dL)
  Sodium, serum          → 2951-2      (mmol/L)
  Potassium, serum       → 2823-3      (mmol/L)
  BUN (Urea N, serum)    → 3094-0      (mg/dL)

HEMATOLOGY:
  WBC, automated         → 6690-2      (K/uL)
  RBC, automated         → 789-8       (M/uL)
  Hemoglobin, blood      → 718-7       (g/dL)
  Hematocrit, blood      → 4544-3      (%)
  Platelets, blood       → 777-3       (K/uL)

MICROBIOLOGY:
  Culture, bacterial     → 625-4       (growth)
  Gram stain result      → 10358-4     (narrative)

CARDIOLOGY:
  Troponin T, serum      → 6597-9      (pg/mL)
  BNP (B-type natriuretic peptide) → 42637-9
```

### 2.4 LOINC Implementation in EHR Systems

#### Lab Order Entry Example
```sql
-- LOINC Registry Query
SELECT
  loinc_code,
  component,
  specimen_type,
  reference_range_low,
  reference_range_high,
  unit_of_measure
FROM loinc_catalog
WHERE component LIKE '%Glucose%'
  AND specimen_type = 'Serum'
  AND status = 'ACTIVE'
ORDER BY display_priority;

Result:
2345-7 | Glucose [Mass/volume] in Serum or Plasma | 70-100 | mg/dL
```

#### Results Transmission (HL7 v2.5)
```
OBX|1|NM|2345-7^Glucose^LN||95|mg/dL|70-100|N|||F
OBX|2|NM|2160-0^Creatinine^LN||1.2|mg/dL|0.7-1.3|N|||F
OBX|3|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.0|N|||F
```

### 2.5 Reference Ranges and Units

**Critical Requirement**: All lab values must include reference range and units

```
Standard Units (SI vs. Conventional):

Glucose:
  SI Units: mmol/L (multiply conventional by 0.0555)
  Conventional: mg/dL

Hemoglobin:
  SI Units: g/L (multiply conventional by 10)
  Conventional: g/dL

Creatinine:
  SI Units: micromol/L (multiply conventional by 88.4)
  Conventional: mg/dL

Implementation Note: Systems must support both; patient-specific
unit preferences must be configurable.
```

---

## 3. RxNorm (FDA Medication Terminology Standard)

### 3.1 RxNorm Overview

**RxNorm** is the FDA standard for medication terminology:
- 40,000+ clinical drug names
- Links to other drug vocabularies (NDC, SNOMED CT)
- Required for medication ordering and dispensing
- Supports dose form, strength, and route standardization

### 3.2 RxNorm Concept Hierarchy

```
RxNorm Identifier (RXCUI): 205923
Preferred Name: Metformin
Names at Different Levels:
  - Clinical Drug Component: Metformin
  - Clinical Drug: Metformin 500 MG Oral Tablet
  - Branded Product: Glucophage 500 MG Oral Tablet
  - Semantic Clinical Drug (SCD): Metformin 500 MG
  - Semantic Branded Drug (SBD): Glucophage 500 MG
```

#### Term Types in RxNorm

| Term Type | Example | Clinical Use |
|-----------|---------|--------------|
| SCD (Semantic Clinical Drug) | Metformin 500 mg | Preferred for ordering |
| SBD (Semantic Branded Drug) | Glucophage 500 mg | Brand identification |
| GPCK (Generic Drug Pack) | Metformin 500mg + Lisinopril 10mg | Combination therapy |
| BPCK (Branded Drug Pack) | Glucophage + Prinivil | Brand combinations |

### 3.3 Medication Ordering Standards

#### Preferred RxNorm Format

```
STRUCTURE: [Generic Name] [Strength] [Dose Form]

CORRECT FORMATS:
✓ Metformin 500 mg oral tablet
✓ Lisinopril 10 mg oral tablet
✓ Amoxicillin 500 mg oral capsule
✓ Insulin glargine 100 units/mL subcutaneous injection

AVOID:
✗ Glucophage (use generic name)
✗ 500 mg metformin (put strength after name)
✗ Metformin tabs (use "tablets" or abbreviate formally)
✗ Amox (use full name)
```

#### Example Medication Order Entry

```json
{
  "order_id": "MED-2025-001234",
  "patient_id": "PT-9876543",
  "medication": {
    "rxcui": 205923,
    "name": "Metformin",
    "strength": "500 mg",
    "dose_form": "Oral Tablet",
    "route": "Oral",
    "frequency": "Twice daily",
    "sig": "Take 1 tablet by mouth twice daily with meals",
    "quantity": 60,
    "days_supply": 30,
    "refills": 3,
    "ndc": "00378-0179-93"
  },
  "indication": {
    "snomed_code": "44054006",
    "snomed_display": "Type 2 diabetes mellitus"
  },
  "pharmacy_processing": {
    "timestamp": "2025-01-15T10:30:00Z",
    "pharmacist_id": "PH-5678",
    "verification_status": "VERIFIED"
  }
}
```

### 3.4 Drug Interaction and Allergy Checking

#### RxNorm-Based Interaction Matrix

```python
def check_drug_interactions(patient_medications: List[RXCUI]):
    """
    Check medication interactions using RxNorm database

    Args:
        patient_medications: List of RxNorm CUIs

    Returns:
        interaction_report: {
            "severity": "SEVERE|MODERATE|MILD|NONE",
            "interactions": [
                {
                    "drug_pair": ["Metformin 500mg", "Contrast Media"],
                    "interaction": "May impair renal function",
                    "recommendation": "Monitor renal function; consider temporary discontinuation",
                    "reference": "DrugBank, FDA MedWatch"
                }
            ]
        }
    """

    # Pseudocode for interaction checking
    interaction_matrix = load_fda_interaction_database()
    alerts = []

    for i, drug1 in enumerate(patient_medications):
        for drug2 in patient_medications[i+1:]:
            severity = interaction_matrix.get((drug1, drug2))
            if severity in ["SEVERE", "MODERATE"]:
                alerts.append({
                    "drug_pair": [drug1, drug2],
                    "severity": severity,
                    "alert": True
                })

    return alerts
```

### 3.5 Controlled Substance and DEA Scheduling

**DEA Schedules Integration with RxNorm:**

```
Schedule I:   No medical use (excluded from RxNorm)
Schedule II:  High abuse potential (e.g., morphine, oxycodone)
              - Require triplicate prescription
              - No automatic refills
Schedule III: Moderate abuse potential (e.g., codeine)
              - Up to 5 refills
              - 6-month validity
Schedule IV:  Low abuse potential (e.g., alprazolam, lorazepam)
              - Up to 11 refills
              - 1-year validity
Schedule V:   Over-the-counter with restrictions

RxNorm Field: dea_schedule_category
```

---

## 4. ICD-10-CM (Diagnosis Coding)

### 4.1 ICD-10-CM Code Structure

```
ICD-10-CM Code Structure: X XX . XX X
                          │ ││ │ ││ │
                          │ ││ │ ││ └─ 5th digit: Laterality/type
                          │ ││ │ │└─ 4th digit: Specificity
                          │ ││ │ └── Decimal point
                          │ ││ └─ 3rd digit: Anatomical site
                          │ └┴─ 2nd & 3rd: Etiology
                          └─ 1st letter/number: Chapter

Examples:
E11.9   - Type 2 diabetes mellitus without complications
I10     - Essential (primary) hypertension
J15.9   - Unspecified bacterial pneumonia
I21.01  - STEMI of left anterior descending coronary artery
R73.09  - Elevated fasting glucose
```

### 4.2 ICD-10-CM to SNOMED CT Mapping

```
ICD-10-CM → SNOMED CT (Gold Standard Mapping)

E11.9 (Type 2 diabetes, no complications)
  → 44054006 (Type 2 diabetes mellitus)

I10 (Essential hypertension)
  → 59621000 (Essential hypertension)

J15.9 (Bacterial pneumonia, unspecified)
  → 53084003 (Acute bacterial pneumonia)

I21.01 (STEMI - Left Anterior Descending)
  → 57054005 (Acute myocardial infarction)
  → 284347008 (Anterior wall STEMI)
```

---

## 5. Clinical Documentation Standards

### 5.1 Problem List Standards

**Required Format:**

```
PROBLEM: Diabetes mellitus, type 2
DATE ONSET: 01/15/2015
SNOMED CT CODE: 44054006
ICD-10-CM CODE: E11.9
ACTIVE: Yes

STATUS: Controlled on current therapy
LAST REVIEWED: 01/10/2025
REVIEWED BY: Dr. Sarah Johnson, MD

MEDICATIONS:
- Metformin 500 mg BID (RXCUI: 205923)
- Lisinopril 10 mg QD (RXCUI: 199800)

LATEST LABS:
- Hemoglobin A1C: 6.8% (LOINC: 4549-7)
  Reference range: <5.7%
  Date: 01/10/2025
- Fasting glucose: 115 mg/dL (LOINC: 2345-7)
  Reference range: 70-100 mg/dL
```

### 5.2 Assessment and Plan Standards

```
ASSESSMENT:
[SNOMED Concept]: [ICD-10 Code] - [Clinical Status]

Example:
Type 2 diabetes mellitus (44054006): E11.9 - Adequately controlled

PLAN:
1. Continue current medications
2. Repeat A1C in 3 months
3. Annual diabetic eye exam (due 12/2025)
4. Referral to endocrinology if A1C >7.5%

MEDICATIONS:
- Continue Metformin 500 mg BID (RXCUI: 205923)
- Continue Lisinopril 10 mg QD (RXCUI: 199800)
- Add Aspirin 81 mg QD for cardiac protection (RXCUI: 243670)
  REASON: Primary prevention in Type 2 DM with hypertension
```

---

## 6. Terminology Interoperability

### 6.1 Multi-Code Mapping Standards

```
Clinical Concept: Patient has Type 2 Diabetes

SNOMED CT:        44054006
ICD-10-CM:        E11.9
ICD-9-CM:         250.00
RxNorm Relevant:  205923 (Metformin), 199800 (Lisinopril)
CPT Codes:        99214 (Office visit - established patient)
                  80053 (Comprehensive metabolic panel)

FHIR Coding:
{
  "coding": [
    {
      "system": "http://snomed.info/sct",
      "code": "44054006",
      "display": "Type 2 diabetes mellitus"
    },
    {
      "system": "http://hl7.org/fhir/sid/icd-10-cm",
      "code": "E11.9",
      "display": "Type 2 diabetes mellitus without complications"
    },
    {
      "system": "http://terminology.hl7.org/CodeSystem/icd9cm",
      "code": "250.00",
      "display": "Diabetes mellitus without mention of complication"
    }
  ]
}
```

### 6.2 HL7 FHIR Terminology Binding

```xml
<!-- FHIR Condition Resource with Multiple Code Systems -->
<Condition>
  <id value="diabetes-2025"/>
  <code>
    <coding>
      <system value="http://snomed.info/sct"/>
      <code value="44054006"/>
      <display value="Type 2 diabetes mellitus"/>
    </coding>
    <coding>
      <system value="http://hl7.org/fhir/sid/icd-10-cm"/>
      <code value="E11.9"/>
      <display value="Type 2 diabetes mellitus without complications"/>
    </coding>
    <text value="Type 2 Diabetes"/>
  </code>
  <subject>
    <reference value="Patient/pt-12345"/>
  </subject>
  <onsetDateTime value="2015-01-15"/>
  <recordedDate value="2025-01-15"/>
</Condition>
```

---

## 7. Quality Assurance and Validation

### 7.1 Code Validation Protocol

```python
def validate_medical_coding(concept_map: Dict) -> ValidationReport:
    """
    Validate medical codes across multiple systems

    Requirements:
    1. SNOMED CT concept exists and is active
    2. ICD-10-CM code is valid and current
    3. RxNorm medication codes match dose/form
    4. LOINC codes match specimen type and unit
    5. Code mapping is clinically appropriate
    """

    validation_errors = []

    # Check SNOMED CT
    if not snomed_ct.is_active(concept_map['snomed_code']):
        validation_errors.append({
            "type": "SNOMED_INACTIVE",
            "code": concept_map['snomed_code'],
            "severity": "ERROR"
        })

    # Check ICD-10-CM validity
    if not icd10cm.code_exists(concept_map['icd10_code']):
        validation_errors.append({
            "type": "ICD10_INVALID",
            "code": concept_map['icd10_code'],
            "severity": "ERROR"
        })

    # Check cross-system consistency
    if not validate_mapping_consistency(concept_map):
        validation_errors.append({
            "type": "MAPPING_INCONSISTENCY",
            "details": "Codes don't map to same clinical concept",
            "severity": "WARNING"
        })

    return ValidationReport(
        valid=(len(validation_errors) == 0),
        errors=validation_errors
    )
```

### 7.2 Terminology Update Management

**Annual Requirements:**
- [ ] Update SNOMED CT to latest release
- [ ] Update ICD-10-CM codes
- [ ] Update RxNorm medication database
- [ ] Update LOINC laboratory codes
- [ ] Test legacy code mappings
- [ ] Validate all interface vocabularies
- [ ] Update documentation and references

---

## 8. Compliance Checklist

### Federal Requirements
- [ ] SNOMED CT licensed and current
- [ ] RxNorm integrated for all medication orders
- [ ] LOINC codes for all laboratory results
- [ ] ICD-10-CM codes for all diagnoses
- [ ] FDA 21 CFR Part 11 compliance
- [ ] HL7 v2.5 or FHIR STU3+ for data exchange

### Clinical Standards
- [ ] Problem list using SNOMED CT
- [ ] Medication orders using RxNorm
- [ ] Laboratory results with LOINC and reference ranges
- [ ] Allergy/intolerance documented
- [ ] Drug interaction checking implemented
- [ ] Code mappings documented and validated

### Documentation
- [ ] Terminology maintenance procedures documented
- [ ] Code mapping rationale recorded
- [ ] Version tracking for all code systems
- [ ] Training materials for clinical staff
- [ ] Audit logs for terminology changes

---

## 9. References and Resources

### Official Code System Resources
- **SNOMED CT**: https://www.snomed.org/
- **LOINC**: https://loinc.org/
- **RxNorm**: https://www.nlm.nih.gov/research/umls/rxnorm/
- **ICD-10-CM**: https://www.cdc.gov/nchs/icd/icd-10-cm.htm

### Standards Organizations
- **HL7 International**: https://www.hl7.org/
- **FHIR Standard**: https://www.hl7.org/fhir/
- **FDA**: https://www.fda.gov/

### Clinical References
- **Meaningful Use**: 42 CFR §495.4
- **Quality Reporting System (QRUR)**: CMS requirement
- **Phenomapping Standards**: OHDSI network

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Compliance Level**: FDA ONC Certification, HL7 FHIR STU3+
