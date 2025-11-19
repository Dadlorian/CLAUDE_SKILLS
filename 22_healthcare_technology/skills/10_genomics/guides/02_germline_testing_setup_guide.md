# Germline Testing Setup & Implementation Guide

## Overview
This guide covers establishing a clinical germline genetic testing program for hereditary diseases.

## Phase 1: Pre-Test Requirements

### Step 1.1 Indication Assessment
Before testing, ensure:
1. **Appropriate Indication**:
   - Strong family history of genetic disorder
   - Or personal history consistent with genetic condition
   - Or carrier screening (population-based)
   - Or prenatal/pediatric screening

2. **Rule Out Mimics**:
   - Document why genetic cause is likely
   - Rule out acquired/environmental causes
   - Consider psychiatric etiologies if applicable
   - Note past diagnostic workup

### Step 1.2 Consent Process
1. **Informed Consent Document**:
   - Explain test purpose and scope
   - Discuss limitations and error rates
   - Describe return of results policy
   - Address incidental findings consent
   - Obtain signatures before sample collection

2. **Key Discussion Points**:
   - What will be tested (gene scope)
   - What results will/won't mean
   - Privacy and data use policies
   - Insurance/employment implications
   - Genetic counseling availability

### Step 1.3 Pre-Test Counseling
1. **Genetic Counselor Review**:
   - Confirm indication appropriateness
   - Assess understanding of inheritance
   - Discuss testing implications
   - Plan for family communication
   - Document counseling in chart

2. **Expectations Setting**:
   - Explain possible outcomes (positive, negative, VUS)
   - Discuss penetrance/expressivity
   - Prepare for negative result despite symptoms
   - Timeline for results (typically 2-4 weeks)

## Phase 2: Sample Collection & QC

### Step 2.1 Sample Types
**Acceptable Specimens**:
- Whole blood (EDTA tube, 5-10mL)
- Saliva (buccal swab kits)
- Buccal swab (if blood unavailable)
- Tissue (limited, usually research)

**Avoid**:
- Formalin-fixed tissue (DNA degradation)
- Serum only (no DNA)
- Ambient temperature shipping

### Step 2.2 Specimen Collection Protocol
1. **Proper Labeling**:
   - Patient name, DOB, Medical record number
   - Specimen ID (unique)
   - Collection date
   - Initials of collector

2. **Documentation**:
   - Note specimen type and quantity
   - Record collection time/temperature
   - Document transport method
   - Verify chain of custody

### Step 2.3 Pre-Analytical QC
1. **Upon Receipt**:
   - Verify specimen integrity
   - Check labeling accuracy
   - Assess volume adequacy
   - Note any visible contamination

2. **DNA Extraction**:
   - Extract using validated method
   - Quantify DNA (NanoDrop or Qubit)
   - Check purity (A260/A280 ratio)
   - Assess degradation (agarose gel if needed)

## Phase 3: Test Selection & Panel Design

### Step 3.1 Single-Gene Testing
**Use When**:
- Specific diagnosis highly likely
- Cost control important
- Single predominant locus in population
- Family history strongly suggests one gene

**Advantages**:
- Lower cost
- Faster turnaround
- Fewer incidental findings
- Limited interpretation complexity

**Disadvantages**:
- Genetic heterogeneity may be missed
- Higher failure-to-diagnose rate
- May need sequential testing

### Step 3.2 Multi-Gene Panels
**Use When**:
- Multiple genes cause similar phenotype
- Genetic heterogeneity high
- Diagnostic uncertainty significant
- Cost-benefit favorable

**Panel Design**:
- Include all genes known to cause phenotype
- Exclude genes with very weak evidence
- Consider population-specific founder variants
- Plan for update strategy as new genes identified

**Examples**:
- **Hereditary Cancer**: 25-75 genes (BRCA-expanded)
- **Cardiomyopathy**: 40-100 genes (early vs. late onset)
- **Deafness**: 150+ genes (nonsyndromic hearing loss)

### Step 3.3 Whole Exome/Genome
**Use When**:
- No specific phenotype diagnosis
- Ultra-rare disease suspected
- Research context
- Extensive genetic heterogeneity expected

**Considerations**:
- Generate many secondary findings
- Require structured consent for incidental findings
- Higher cost but comprehensive
- Require robust bioinformatics

## Phase 4: Analysis & Interpretation

### Step 4.1 Sequencing & Variant Calling
1. **QC Thresholds**:
   - Minimum 50x coverage for germline testing
   - Uniform coverage across target region
   - <5% bases with <20x coverage
   - <2% no-call rate

2. **Variant Calling Parameters**:
   - Include rare and common variants
   - Filter for quality (QUAL >20)
   - Include both SNVs and indels
   - Capture copy number variants if panel allows

### Step 4.2 Variant Prioritization
1. **Filter for Actionable Variants**:
   - Only report variants in tested genes
   - Exclude common benign variants (AF >1% in Europeans)
   - Focus on moderate-high impact variants
   - Consider population-specific frequencies

2. **Phenotype Matching**:
   - Does variant affect gene relevant to phenotype?
   - Is consequence consistent with phenotype severity?
   - Are there published associations?
   - Would inheritance pattern fit family?

### Step 4.3 Classification
Apply ACMG 2015/2017 criteria systematically:
1. Pathogenic
2. Likely Pathogenic
3. Variant of Uncertain Significance
4. Likely Benign
5. Benign

(See Variant Interpretation Workflow Guide for detailed approach)

## Phase 5: Reporting

### Step 5.1 Report Structure
**Essential Sections**:
1. **Header**: Patient ID, test name, ordering provider, date
2. **Methods**: Sequencing platform, genes analyzed, coverage
3. **Results**: Variants identified with HGVS nomenclature
4. **Interpretation**: Classification per ACMG, clinical significance
5. **Recommendations**: Screening, management, family implications
6. **Limitations**: Gene coverage gaps, VUS definition
7. **Signatures**: Director approval, date

### Step 5.2 Variant Reporting
For each reported variant include:
- **Gene**: Official HGNC symbol
- **Transcript**: RefSeq accession
- **HGVS**: DNA and protein notation
- **Classification**: Pathogenic/LP/VUS/LB/Benign
- **Evidence**: Brief summary of supporting evidence
- **Population Frequency**: MAF from gnomAD
- **Literature**: Key citations

### Step 5.3 Secondary Findings
**ACMG SF v3.0 Approach**:
1. **Determine Consent Status**: Did patient consent to secondary findings?
2. **Analyze Recommended Genes**: 73-gene list
3. **Report Pathogenic/LP Only**: Not VUS
4. **Separate Section**: Clearly labeled as incidental
5. **Family Implications**: Note inheritance pattern

## Phase 6: Post-Test Management

### Step 6.1 Result Delivery
1. **Communication Method**:
   - Secure notification to ordering provider
   - Provider discusses with patient
   - Provide written summary
   - Offer follow-up counseling

2. **Timing**:
   - Urgent results: Call physician immediately
   - Routine: Standard turnaround
   - Complex cases: Discuss with pathologist first

### Step 6.2 Genetic Counseling
**Post-Test Counseling (Recommended)**:
1. **Positive Results**:
   - Confirm inheritance pattern
   - Discuss penetrance/expressivity
   - Recommend surveillance/prevention
   - Plan cascade screening in family
   - Discuss reproductive options

2. **Negative Results**:
   - May not rule out genetic cause
   - Discuss residual risk
   - Suggest alternative diagnoses
   - Plan for follow-up if new gene identified

3. **VUS Results**:
   - Explain uncertainty
   - Recommend not to test family (yet)
   - Suggest monitoring for new evidence
   - Plan reclassification timeline

### Step 6.3 Cascade Screening
1. **Family Screening Planning**:
   - Identify at-risk relatives
   - Provide education materials
   - Facilitate provider contacts
   - Document cascade screening uptake

2. **Segregation Study**:
   - Test parents if proband positive
   - Confirms de novo vs. inherited
   - Aids interpretation strength
   - Important for family risk assessment

## Phase 7: Monitoring & Follow-up

### Step 7.1 Database Monitoring
1. **Variant Reclassification**:
   - Subscribe to ClinVar updates
   - Monitor literature for new evidence
   - Annual review of VUS variants
   - Plan reclassification strategy

2. **New Gene Discoveries**:
   - Monitor OMIM for new genes
   - Update panel as appropriate
   - Offer reanalysis if new gene identified
   - Maintain list of genes added and dates

### Step 7.2 Clinical Outcomes Tracking
1. **Document Outcomes**:
   - Did test help diagnosis?
   - Did management change?
   - Were family members identified?
   - What was clinical impact?

2. **Quality Metrics**:
   - Diagnostic yield (% positive by indication)
   - Time to result
   - Adequacy of reporting
   - Provider satisfaction

## Best Practices

### Technical Excellence
- Maintain >99.9% genotype accuracy
- Regular proficiency testing
- Documented validation for all new genes
- Contingency for failed samples

### Clinical Integration
- Clear communication with providers
- Timely result reporting
- Comprehensive interpretation
- Appropriate counseling resources

### Ethical Considerations
- Informed consent for testing and secondary findings
- Privacy/data security emphasis
- Non-discriminatory communication
- Respect for patient autonomy

### Continuous Improvement
- Collect feedback from providers
- Track diagnostic yields by gene
- Monitor turnaround times
- Update practices based on latest guidelines
