# Pharmacogenomics Testing & Implementation Guide

## Overview
Guide for implementing pharmacogenomics testing in clinical care for personalized medication dosing.

## Phase 1: Patient Assessment & Testing

### Step 1.1 Pre-Test Evaluation
1. **Assess Current Medications**:
   - List all drugs patient taking
   - Identify if any have PGx biomarkers
   - Note dosing history and response
   - Document adverse reactions

2. **Test Selection**:
   - **Targeted testing**: Specific gene before drug initiation
   - **Comprehensive panel**: 30-50 genes, one-time testing
   - **Population screening**: Carrier status assessment

### Step 1.2 Specimen Collection
- Whole blood (EDTA): 3-5 mL
- Saliva swab: Acceptable alternative
- Store at room temperature if needed
- Document collection date/method

## Phase 2: Genotyping & Phenotype Assignment

### Step 2.1 Variant Calling
Call common variants in PGx genes:
- **CYP2D6**: Duplications, deletions, critical mutations
- **CYP2C19**: *2, *3, *17 alleles
- **CYP2C9**: *2, *3 variants
- **TPMT**: *2, *3, *4, *5, *6 alleles
- **HLA**: HLA-B*5701, HLA-A*3101, HLA-B*1502

### Step 2.2 Phenotype Classification
**Activity Score Method**:
```
Assign activity scores per allele:
- Full-function allele: 1.0 activity
- Reduced-function: 0.5 activity
- Loss-of-function (null): 0 activity
- Duplication: 2.0+ activity

Composite score = Sum of allele scores
Phenotype = Score interpretation
```

**Phenotype Categories**:
- **Poor Metabolizer (PM)**: Minimal enzyme activity
- **Intermediate Metabolizer (IM)**: Reduced activity
- **Normal Metabolizer (NM)**: Expected activity
- **Rapid Metabolizer (RM)**: Increased activity
- **Ultra-Rapid Metabolizer (URM)**: Significantly elevated activity

## Phase 3: Drug-Gene Interaction Interpretation

### Step 3.1 Clinical Significance Assessment
For each patient medication:
1. **Identify PGx Association**:
   - Check if drug has clinically relevant PGx gene
   - Look up in PharmGKB, CPIC guidelines
   - Verify clinical action classification

2. **Assess Impact**:
   - How much does genotype affect drug levels?
   - Risk of inefficacy or toxicity?
   - Alternative drugs available?
   - Dose adjustments effective?

3. **Evidence Level**:
   - **Level A**: Strong evidence, FDA approval
   - **Level B**: Moderate evidence, guideline recommendation
   - **Level C**: Emerging evidence, clinical consideration

### Step 3.2 Phenotype-Drug Matching
**Example: CYP2D6-Codeine**
```
PM: Cannot activate codeine → Choose alternative
IM: Reduced activation → Consider alternative or higher dose
NM: Normal metabolism → Standard dosing
RM: Enhanced effect → Consider lower dose
URM: Excessive metabolism → May need higher dose
```

## Phase 4: Reporting

### Step 4.1 Report Components
1. **Gene-Phenotype Results**:
   - Gene name
   - Detected alleles (e.g., CYP2D6 *1/*4)
   - Phenotype assignment (PM/IM/NM/RM/URM)
   - Enzyme activity interpretation

2. **Drug-Response Predictions**:
   - Each patient medication assessed
   - Predicted metabolism level
   - Expected drug concentration
   - Risk of adverse effects/inefficacy

3. **Clinical Recommendations**:
   - Tier 1A: FDA-approved + guideline
   - Tier 1B: Moderate evidence (CPIC)
   - Tier 2: Emerging evidence
   - Tier 3: Potential future use

4. **Specific Actions**:
   - **Continue**: Standard dosing
   - **Adjust**: Specific dose modification
   - **Avoid**: Contraindicated combination
   - **Monitor**: Enhanced surveillance
   - **Alternative**: Different medication

## Phase 5: Integration with Clinical Care

### Step 5.1 Prescriber Communication
1. **Report Delivery**:
   - Secure electronic transmission
   - Clear actionable recommendations
   - Patient-friendly summary available
   - Pharmacist review before dispensing

2. **Medication Reconciliation**:
   - Review current medications
   - Cross-reference with PGx results
   - Make dosing adjustments as needed
   - Document recommendations followed

### Step 5.2 EHR Integration
- Store PGx results in EHR
- Link to prescribing decision support
- Alert when contraindicated drug ordered
- Enable medication reconciliation

### Step 5.3 Pharmacy Integration
- Pharmacist reviews PGx before dispensing
- Suggests dose adjustments based on genotype
- Counsels patient on medication interactions
- Documents dosing rationale

## Phase 6: Patient Education

### Step 6.1 Pharmacogenomics Counseling
1. **Genetic Basis**:
   - Explain genes tested
   - How genetics affects drug metabolism
   - Why metabolism impacts treatment

2. **Current Medications**:
   - List all drugs with known PGx
   - Recommend drug/dose changes
   - Alternative agents discussed
   - Timeline for implementation

3. **Future Implications**:
   - How results apply to future drugs
   - When to share results with new provider
   - Value of one-time testing

### Step 6.2 Patient Materials
- Wallet card with PGx phenotypes
- Medication list by metabolism category
- When to share results with providers
- Contact for questions/updates

## Phase 7: Monitoring & Follow-up

### Step 7.1 Treatment Response Monitoring
1. **Effectiveness Assessment**:
   - Is medication working as expected?
   - Symptom improvement observed?
   - Reach expected therapeutic level?

2. **Adverse Effects Monitoring**:
   - Any unexpected side effects?
   - Toxicity related to metabolism?
   - Need for dose adjustment?

### Step 7.2 Medication Changes
- When new drug prescribed: Review PGx report
- Check if existing recommendations apply
- Contact lab if new testing needed
- Update medication list

### Step 7.3 Result Sharing
- Provide copies to patient
- Share with specialists/new providers
- Update as medications change
- Recommend re-testing if indicated

## Gene-Specific Implementation

### CYP2D6 (Antidepressants, Antipsychotics, Opioids)
**Testing Challenges**:
- Complex structural variants
- Copy number variations
- Pseudogene interference

**Clinical Implementation**:
- Relevant for ~25% of medications
- High impact on dosing
- Regular testing justified

### TPMT (Thiopurine Metabolism)
**Implementation for Pediatric ALL**:
- Screen all patients before 6-MP
- PM: 85-90% dose reduction
- IM: 33-50% dose reduction
- Standard genotyping available

### CYP2C19 (Clopidogrel, Escitalopram)
**Clopidogrel Response**:
- PM/IM at risk for stent thrombosis
- Consider alternative P2Y12 inhibitor
- Standard implementation critical

### DPYD (5-Fluorouracil)
**High Priority**:
- FDA recommended pre-treatment screening
- Screen before 5-FU/capecitabine
- Homozygous loss = contraindicated
- Heterozygous = consider dose reduction

## Best Practices

### Quality Standards
- Validated genotyping methods
- Regular proficiency testing
- Accurate phenotype assignment
- CPIC guideline adherence

### Clinical Integration
- Educate prescribers on PGx
- Facilitate dose adjustments
- Monitor for compliance
- Track treatment outcomes

### Continuous Improvement
- Update with new CPIC guidelines
- Monitor new gene-drug associations
- Collect outcome data
- Assess cost-benefit of testing

## Common Scenarios & Solutions

**Scenario**: PM patient on codeine with no pain relief
**Solution**: Switch to non-opioid or use active metabolite directly

**Scenario**: IM patient on standard citalopram dose with QT prolongation
**Solution**: Reduce dose per FDA guidance based on genotype

**Scenario**: Patient starting new drug with multiple PGx genes
**Solution**: Comprehensive PGx review; coordinate metabolism across drugs

**Scenario**: Pediatric ALL on 6-MP with severe toxicity
**Solution**: TPMT testing; likely PM, reduce dose significantly
