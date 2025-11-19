# Cancer Genomics Analysis Workflow Guide

## Overview
Comprehensive guide for analyzing tumor samples and generating actionable genomic reports for precision medicine.

## Phase 1: Pre-Analytical Processing

### Step 1.1 Specimen Requirements
- **Tumor Content**: Minimum 20% neoplastic cellularity
- **Sample Type**: Fresh tumor, FFPE tissue, or circulating tumor DNA
- **Size**: Minimum tissue dimensions documented
- **Processing**: Rapid fixation (<1 hour) for optimal DNA/RNA

### Step 1.2 Quality Assessment
1. **Histopathologic Review**:
   - Confirm diagnosis
   - Estimate tumor cellularity
   - Note any necrosis/inflammation
   - Document tumor heterogeneity

2. **Specimen Macrodissection**:
   - Enrich tumor area if <20% cellularity
   - Remove uninvolved tissue to improve signal
   - Confirm representative sampling
   - Document macrodissection location

## Phase 2: Sequencing & Initial Analysis

### Step 2.1 Test Selection
- **Targeted Panel**: 300-500 genes for specific cancer types
- **Tumor-Only**: No matched normal tissue
- **Tumor-Normal**: Paired normal improves specificity
- **RNA-seq**: Assess gene fusions and expression

### Step 2.2 Sequencing QC
- **Tumor Coverage**: Minimum 500x-1000x for somatic SNVs
- **Variant Calling**: Both SNVs and indels included
- **Copy Number**: Assess amplifications/deletions
- **Contamination**: Assess if normal tissue contamination significant

### Step 2.3 Somatic Variant Filtering
1. **Frequency Filtering**:
   - Exclude variants in gnomAD >1% (common benign)
   - Note population-specific frequencies
   - Cancer-specific variant databases (COSMIC)

2. **Functional Impact**:
   - Focus on HIGH/MODERATE consequence variants
   - Prioritize known cancer-associated variants
   - Flag novel variants in cancer-related genes

3. **VAF Thresholds**:
   - Single-hit: VAF >5% typically reportable
   - Clonal variants: VAF >20% preferred
   - Subclonal: Document if below threshold

## Phase 3: Driver vs. Passenger Assessment

### Step 3.1 Identify Drivers
**Oncogenes** (activating mutations):
- Known hotspot mutations (KRAS G12C, BRAF V600E)
- Gene amplifications (HER2, MYC)
- Fusion genes (ABL-BCR, ALK rearrangements)

**Tumor Suppressors** (loss-of-function):
- TP53, RB1, PTEN, BRCA1/2
- Deep deletions (complete gene loss)
- Biallelic inactivation pattern

### Step 3.2 Prioritize Findings
1. **Tier 1A (Highest Confidence)**:
   - FDA-approved therapeutic
   - Approved companion diagnostic
   - Clear clinical actionability

2. **Tier 1B (Strong Evidence)**:
   - NCCN guideline recommendation
   - Peer-reviewed clinical trials
   - Substantial clinical benefit

3. **Tier 2 (Emerging)**:
   - Clinical trials ongoing
   - Emerging literature evidence
   - Potential therapeutic option

4. **Tier 3 (Research)**:
   - Pre-clinical evidence
   - Functional significance known
   - Investigational agents

## Phase 4: Biomarker Assessment

### Step 4.1 Tumor Mutational Burden (TMB)
```
TMB = Total nonsynonymous mutations / Sequenced megabases
Threshold: ≥10 mut/Mb = high TMB (potential immunotherapy candidate)
```

### Step 4.2 Microsatellite Instability (MSI)
- **Testing Methods**: IHC (MLH1/MSH2/MSH6/PMS2), PCR, NGS
- **Results**:
  - MSI-H/dMMR → Checkpoint inhibitor eligible
  - MSI-L/pMMR → Standard therapy

### Step 4.3 Homologous Recombination Deficiency (HRD)
- **Assessment**: Genomic scarring analysis
- **BRCA1/2 Status**: Somatic or germline mutation
- **PARP Inhibitor Eligibility**: Based on HRD status
- **Platinum Sensitivity**: Predict treatment response

## Phase 5: Treatment Recommendations

### Step 5.1 Actionable Findings Report
**Format for Each Finding**:
1. Gene and variant
2. Tumor type frequency
3. FDA approval status
4. Clinical trial options
5. Dosing/administration
6. Expected response rates
7. Resistance mechanisms
8. Literature references

### Step 5.2 Drug-Variant Matching
- Use OncoKB, CIViC, NCCN guidelines
- Document FDA approval date
- Note any restrictions/contraindications
- Flag available clinical trials

### Step 5.3 Multidisciplinary Review
- Tumor board presentation
- Oncologist interpretation
- Treatment selection discussion
- Documented clinical action

## Phase 6: Resistance Monitoring

### Step 6.1 Baseline Characterization
Document all driver mutations at baseline for:
- Treatment response monitoring
- Resistance detection
- Treatment adaptation

### Step 6.2 Serial Monitoring
- **Baseline**: Comprehensive profiling at diagnosis
- **On-Treatment**: 8-12 weeks if clinically indicated
- **Progression**: Re-biopsy/ctDNA to detect resistance mutations
- **Next Line**: Re-profiling before next therapy

### Step 6.3 Resistance Pattern Analysis
**Common Mechanisms**:
- EGFR TKI: T790M secondary mutation
- ALK Inhibitor: G1269A or kinase domain mutations
- PARP Inhibitor: BRCA1/2 reversion mutations
- Immunotherapy: PD-L1 downregulation, TMB loss

## Phase 7: Reporting & Communication

### Step 7.1 Report Structure
1. **Executive Summary**: Key findings and recommendations
2. **Specimen Quality**: Cellularity, DNA quality metrics
3. **Somatic Variants**: All detected pathogenic/actionable variants
4. **Tumor Characteristics**:
   - TMB score
   - MSI status
   - Copy number profile
   - Gene fusions

5. **Actionable Findings**:
   - Tier 1A: FDA-approved therapies
   - Tier 1B: NCCN recommendations
   - Tier 2: Clinical trial opportunities
   - Tier 3: Research options

6. **Clinical Interpretation**: Integrative narrative
7. **Limitations**: Coverage gaps, VAF cutoffs
8. **References**: Key citations and databases

### Step 7.2 EHR Integration
- Result delivery to oncology team
- Flag urgent/critical findings
- Link to treatment planning tools
- Track treatment decisions made

### Step 7.3 Patient Communication
- Secure portal access to results
- Educational materials about mutations
- Family implications if germline
- Contact for questions/concerns

## Best Practices

### Quality Assurance
- Verify biopsies histologically confirmed
- Confirm tumor cellularity adequate
- Validate all tier 1A/1B findings
- Regular proficiency testing

### Clinical Integration
- Educate providers on genomic findings
- Facilitate tumor board presentations
- Support clinical trial identification
- Document treatment decisions

### Continuous Improvement
- Track diagnostic yield by cancer type
- Monitor treatment response by mutation
- Collect outcome data
- Update panels with emerging genes

## Common Challenges & Solutions

**Challenge**: Low tumor cellularity
**Solution**: Microdissect enriched tumor area, consider re-biopsy

**Challenge**: Conflicting variant significance
**Solution**: Refer to ClinGen/CIViC; discuss in tumor board

**Challenge**: Finding with no approved therapy
**Solution**: Comprehensive trial search; discuss emerging options

**Challenge**: Acquired resistance pattern
**Solution**: Recommend combination therapy or alternative agent; consider clinical trials
