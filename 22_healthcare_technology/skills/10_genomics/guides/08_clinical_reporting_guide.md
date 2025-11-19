# Clinical Genomics Reporting Standards Guide

## Overview
Standards and best practices for generating clinical genomic reports.

## Report Structure

### Executive Summary
- Patient identifier
- Test ordered and clinical indication
- Key findings (pathogenic/LP variants only)
- Clinical recommendations (one-line summary)

### Methods Section
- Sequencing platform and methodology
- Genes analyzed or sequencing scope
- Coverage metrics (mean depth, % bases >20x)
- Variant calling and annotation tools
- Quality control metrics

### Results Section
**For Each Reported Variant**:
1. Gene and transcript
2. HGVS nomenclature (DNA and protein)
3. Variant classification (P/LP/VUS/LB/B)
4. Key evidence summary
5. Population frequency
6. Inheritance pattern implications
7. Clinical significance

**For Whole Exome/Genome**:
- Summary statistics
- Primary findings
- Secondary findings (with separate consent section)
- Filtering criteria applied

### Interpretation Section
- Phenotype correlation
- Inheritance pattern consistency
- Functional implications
- Segregation analysis if available
- Literature support

### Recommendations Section
- Medical management suggestions
- Screening/surveillance recommendations
- Family cascade screening
- Genetic counseling referral
- Clinical trial eligibility if applicable

### Limitations Section
- Coverage gaps (genes/regions not adequately covered)
- Variants not detected (pseudogenes, structural variants)
- Interpretation boundaries (VUS vs. pathogenic)
- Methodological limitations
- Mitochondrial DNA not analyzed (if applicable)

### Signatures
- Pathologist/Medical Director
- Board certifications
- Date of report
- Laboratory accreditation information

## Variant Description Standards

### HGVS Nomenclature Requirements
- Standard format: Gene.Transcript:c.position_change:p.effect
- Use RefSeq transcripts (NM_preferred)
- Include both DNA and protein notation
- Examples:
  - BRCA1.NM_007294.4:c.68_69delAG:p.(Gly23AspfsTer10)
  - KRAS.NM_033360.4:c.35G>A:p.(Gly12Asp)

### Variant Classification Explanation
For each reported variant:
1. **Classification Rationale**:
   - Summary of ACMG criteria applied
   - Brief evidence statement (1-2 sentences)
   - Key databases/tools used
   - Any conflicting data noted

2. **Evidence Integration**:
   - Frequency data (gnomAD, COSMIC)
   - Functional predictions
   - Clinical associations
   - Segregation analysis

## Secondary Findings Reporting

### ACMG SF v3.0 Implementation
1. **Consent Verification**:
   - Document patient consent for secondary findings
   - Separate checkbox/signature if required
   - Respect patient preferences

2. **Gene Analysis**:
   - Analyze all 73 recommended genes
   - Report pathogenic/likely pathogenic only
   - Exclude VUS and benign findings
   - Separate section clearly labeled "Secondary Findings"

3. **Report Format**:
   - Conditions separately discussed
   - Management/screening recommendations
   - Family implications
   - Counseling resources

## Report Formatting & Distribution

### Content Organization
- Logical flow from specimen to conclusions
- Clear section headings
- Bulleted lists where appropriate
- Tables for variant comparisons
- Page breaks between major sections

### Visual Elements
- Patient and lab identifiers on each page
- Page numbering
- Timestamps on footer
- Laboratory logo and certification info
- Secure document marking if sensitive

### Distribution Method
- Secure electronic delivery to ordering provider
- Patient portal access (encrypted)
- Fax only if secure line confirmed
- Never standard email
- Physical copy upon request

## Quality Assurance in Reporting

### Accuracy Verification
- Two-person review of reports
- Variant nomenclature verification
- Classification accuracy check
- Numbers and statistics confirmation
- References verified

### Completeness Checklist
- All ordered genes analyzed?
- Coverage adequate for conclusions?
- Limitations clearly stated?
- Recommendations appropriate?
- Clinical significance clear?

### Patient Communication Assessment
- Are results understandable to non-specialists?
- Are limitations clear?
- Are recommendations actionable?
- Is uncertainty acknowledged appropriately?

## Report Examples & Templates

### Example: Hereditary Cancer Panel - Positive Result
[Template structure showing pathogenic BRCA1 mutation with full interpretation]

### Example: Pharmacogenomics Report
[Template showing CYP2D6 PM phenotype with specific drug recommendations]

### Example: Whole Exome - VUS Finding
[Template appropriately addressing uncertainty and follow-up plans]

---

# Hereditary Cancer Syndrome Evaluation Guide

## Overview
Comprehensive approach to evaluating patients for hereditary cancer predisposition syndromes.

## Phase 1: Risk Assessment

### Step 1.1 History Taking
**Personal History**:
- Cancer diagnosis and age of onset
- Type and stage at diagnosis
- Bilateral or multiple primary cancers
- Associated features (polyps, hamartomas, etc.)

**Family History**:
- First/second-degree relatives with cancer
- Cancer type and age of onset
- Multiple family members affected
- Consanguinity or founder ancestry

### Step 1.2 Red Flags for Genetic Testing
**Major Indicators**:
- Early-onset cancer (<50 years)
- Multiple primary cancers in one individual
- Multiple family members with same cancer type
- Uncommon cancer type (e.g., male breast cancer)
- Specific malignancy syndrome (ovarian + breast, colorectal + endometrial)

**Inherited Syndrome Features**:
- Breast cancer <45 years
- Colorectal cancer <50 years
- Endometrial cancer <50 years
- Ovarian cancer (any age)
- Male breast cancer (any age)

## Phase 2: Genetic Testing Decision

### Step 2.1 Appropriate Testing Selection
**Single-Gene Testing**:
- BRCA1 if family history suggests deleterious mutation
- DNA mismatch repair genes for Lynch syndrome
- Specific gene if pathogenic variant known in family

**Multi-Gene Panel**:
- BRCA1/2 + extended cancer panel (25-75 genes)
- Hereditary colorectal cancer panel (Lynch syndrome + others)
- Lynch Syndrome panel (MLH1, MSH2, MSH6, PMS2, EPCAM)

**Decision Factors**:
- Phenotype complexity
- Genetic heterogeneity
- Cost-benefit analysis
- Patient preferences
- Insurance coverage

### Step 2.2 Pre-Test Counseling
- Explain test methodology
- Discuss possible outcomes
- Probability of detecting mutations
- Implications of positive result
- Return of results policy
- Family implications

## Phase 3: Analysis & Interpretation

### Step 3.1 Variant Interpretation
Apply ACMG criteria with cancer-specific modifications:
- Pathogenic variants confirm hereditary syndrome
- Likely Pathogenic considered in clinical context
- VUS: Note limitations, suggest family studies
- Benign/Likely Benign: Reassuring but not exclusionary

### Step 3.2 Cancer-Specific Considerations
**BRCA1 Mutations**:
- Breast cancer: 70-80% lifetime risk
- Ovarian cancer: 40-50% lifetime risk
- Pancreatic cancer: 2-3% risk
- Prostate cancer: Moderate increased risk
- Male breast cancer: 5-10% risk

**BRCA2 Mutations**:
- Breast cancer: 60-65% lifetime risk
- Ovarian cancer: 20-25% lifetime risk
- Pancreatic, prostate, melanoma risks

**Lynch Syndrome**:
- Colorectal cancer: 70-80% lifetime risk
- Endometrial cancer: 30-60% lifetime risk
- Multiple other cancers: 25-50%
- Depends on specific gene (MLH1 > MSH2/MSH6)

## Phase 4: Risk Stratification & Management

### Step 4.1 Positive Test Result Management
1. **Confirmed Hereditary Cancer**:
   - High-penetrance mutations
   - Strong evidence-based surveillance recommendations
   - Prevention strategies (surgery, medications)
   - Family screening recommendations

2. **Surveillance Recommendations**:
   **BRCA1/2 Mutation Carriers**:
   - Breast: Annual MRI starting age 25-30
   - Mammography starting age 30-40
   - Consider risk-reducing mastectomy
   - Ovarian screening not effective; risk-reducing salpingo-oophorectomy at age 40-45
   - Pancreatic screening (emerging): Annual EUS/MRI age 40+

   **Lynch Syndrome**:
   - Colonoscopy: Every 1-2 years starting age 25-40
   - Endometrial screening: Annual ultrasound/aspiration starting age 40
   - Consider hysterectomy/BSO for women
   - Gastric screening if CDH1 mutation (hereditary diffuse gastric cancer)

### Step 4.2 Preventive Interventions
**Surgical**:
- Risk-reducing mastectomy/oophorectomy (BRCA)
- Hysterectomy ± BSO (Lynch)
- Colectomy (Lynch with early-onset CRC)

**Medical**:
- Tamoxifen for breast cancer prevention (BRCA)
- Hormone replacement therapy considerations
- Aspirin for cancer prevention (Lynch syndrome)

### Step 4.3 Therapeutic Implications
- PARP inhibitor eligibility (BRCA mutations)
- Platinum-based chemotherapy sensitivity
- Immunotherapy response (MSI-H)
- Clinical trial opportunities

## Phase 5: Family Communication & Cascade Screening

### Step 5.1 Cascade Screening Planning
1. **Identify At-Risk Relatives**:
   - First-degree relatives: 50% inheritance risk
   - Second-degree relatives: 25% risk
   - Specific cancer risk stratification

2. **Communication Strategy**:
   - Provide written summary for relatives
   - Offer to contact relatives (institutional policy)
   - Respect privacy/autonomy
   - Provide genetic counseling referral

### Step 5.2 Relative Counseling
**Testing Decision**:
- Benefits: Early detection, prevention options
- Risks: Psychological impact, discrimination concerns
- Limitations: Not all mutations detected, phenotype variability
- Reproductive implications: PGD/prenatal testing options

## Phase 6: Reporting & Documentation

### Step 6.1 Report Structure
See Clinical Reporting Standards Guide for detailed format.

**Cancer-Specific Elements**:
- Specific hereditary cancer syndrome (if positive)
- Penetrance and age-specific risks
- Surveillance recommendations (specific protocols)
- Prevention options (surgical, medical)
- Family screening implications
- Clinical trial eligibility
- Genetic counseling referral

### Step 6.2 Follow-up Documentation
- Surveillance compliance tracking
- New cancer development
- Impact on treatment decisions
- Family member testing outcomes

---

# Precision Medicine Implementation Guide

## Overview
Framework for implementing genomically-guided treatment selection and monitoring.

## Phase 1: Program Establishment

### Step 1.1 Infrastructure Planning
1. **Sequencing Capacity**:
   - Partner with qualified lab or establish in-house capability
   - Coverage requirements: 500x-1000x for somatic, 100x+ for germline
   - Turnaround time targets (2-4 weeks preferred)
   - Sample processing workflows

2. **Bioinformatics**:
   - Variant calling pipelines
   - Annotation integration
   - Database updates (CIViC, OncoKB, COSMIC)
   - Reporting system

### Step 1.2 Clinical Integration
1. **Provider Education**:
   - Genomics 101 workshops
   - Disease-specific molecular characteristics
   - Treatment implications of specific mutations
   - Quarterly updates on new approvals

2. **Multidisciplinary Team**:
   - Medical oncologist
   - Pathologist/molecular pathologist
   - Genetic counselor
   - Bioinformatician
   - Pharmacist
   - Tumor board coordinator

## Phase 2: Patient Selection & Testing

### Step 2.1 Indication-Based Testing
1. **Tumor Testing Indicators**:
   - Advanced/metastatic cancer
   - Recurrent/resistant disease
   - Specific tumor types (lung, colorectal, breast, etc.)
   - Treatment planning scenarios

2. **Germline Testing Indicators**:
   - Personal/family history of cancer
   - Young age at diagnosis
   - Multiple primary cancers
   - Specific cancer types suggesting hereditary syndrome

### Step 2.2 Sample Collection & QC
- Tissue adequacy for sequencing
- Rapid turnaround processing
- Quality control checkpoints
- Minimum cellularity verification

## Phase 3: Analysis & Report Generation

### Step 3.1 Tumor Profiling
**Standard Components**:
- Driver mutations (oncogenes, TSGs)
- Actionable variants (Tier 1A/1B)
- Biomarkers (TMB, MSI, HRD, PD-L1)
- Copy number profile
- Fusions (if RNA-seq included)

### Step 3.2 Treatment Recommendation Algorithm
1. **Tier 1A (FDA-Approved)**:
   - Approved drug for specific mutation
   - Recommend as standard therapy
   - Example: HER2+ breast cancer → Trastuzumab

2. **Tier 1B (Guideline-Recommended)**:
   - NCCN or other guideline support
   - Recommend if Tier 1A unavailable
   - Example: EGFR mutation lung → EGFR inhibitor

3. **Tier 2 (Emerging Evidence)**:
   - Clinical trials available
   - Emerging literature support
   - Consider if Tier 1 options exhausted
   - Example: Novel fusion genes

4. **Tier 3 (Research)**:
   - Pre-clinical or early-phase trials
   - Exploratory use only
   - Consider for refractory cases

### Step 3.3 Report Components
See Cancer Genomics Workflow Guide for detailed structure.

## Phase 4: Tumor Board Review & Treatment Planning

### Step 4.1 Tumor Board Process
1. **Presentation**:
   - Case overview (patient, cancer history, imaging)
   - Genomic findings (pathologist)
   - Treatment recommendations (oncologist)
   - Trial opportunities (trial coordinator)

2. **Discussion**:
   - Literature review of specific mutations
   - Treatment options and efficacy data
   - Potential resistance mechanisms
   - Consensus recommendation

3. **Documentation**:
   - Recorded recommendation
   - Rationale documented
   - Next steps defined
   - Follow-up plan established

### Step 4.2 Clinical Decision Support
- Integrate findings into EHR
- Alert oncology team to actionable mutations
- Link to clinical guidelines and trials
- Enable treatment planning

## Phase 5: Treatment Initiation & Monitoring

### Step 5.1 Targeted Therapy Selection
- Implement recommended therapy
- Educate patient on mechanism
- Baseline mutation-level profiling
- Establish response monitoring plan

### Step 5.2 Response Assessment
- Clinical response (RECIST criteria)
- ctDNA monitoring (if available)
- Biomarker changes
- Timeline: Typically 8-12 weeks initial assessment

### Step 5.3 Resistance Monitoring
- Plan re-profiling at progression
- Detect acquired resistance mutations
- Identify appropriate next-line therapy
- Serial genomic profiling strategy

## Phase 6: Continuous Improvement

### Step 6.1 Outcome Tracking
- Diagnostic yield (% positive findings)
- Actionability rate (% with available therapy)
- Treatment utilization (% recommendations followed)
- Response rates by mutation type
- Progression-free survival gains

### Step 6.2 Program Metrics
- Turnaround time to report
- Provider satisfaction
- Patient satisfaction
- Cost-benefit analysis
- Clinical trial accrual

### Step 6.3 Guideline Updates
- Monitor FDA approvals
- NCCN guideline updates
- CPIC and ACMG recommendations
- New biomarker discoveries
- Update testing and reporting accordingly

## Best Practices Summary

1. **Scientific Excellence**: Use validated, evidence-based approaches
2. **Clinical Integration**: Seamless EHR integration, provider education
3. **Patient-Centered**: Clear communication, reasonable expectations
4. **Continuous Learning**: Monitor outcomes, update practices
5. **Ethical Standards**: Informed consent, privacy protection, non-discrimination
