# Clinical Laboratory Validation & Testing Reference

## Laboratory Standards & Accreditation

### CLIA (Clinical Laboratory Improvement Amendments)
**Regulation Purpose**: Ensures quality and accuracy of laboratory testing.

**Laboratory Categories**:
1. **Waived Tests**: Minimal complexity, FDA approval with waiver
2. **Moderate Complexity**: Most genetic tests fall here
3. **High Complexity**: Advanced genomic testing (most NGS-based)

**CLIA Requirements**:
- Laboratory director qualification
- Quality control procedures
- Proficiency testing participation
- Personnel training and competency
- Standard operating procedures
- Quality assurance program

### CAP (College of American Pathologists)
**Accreditation**: Voluntary, higher standard than CLIA.

**Benefits**:
- Peer-review inspection
- Enhanced quality standards
- Proficiency testing oversight
- Continuous improvement focus

**Genetic Testing Standards**:
- Sample handling protocols
- DNA extraction validation
- Instrument calibration
- Data analysis verification
- Report generation standards

### State Licensing
**Variable Requirements**: Some states (e.g., New York, Florida) have additional licensing requirements.

**CLIA Certification Number**: Required for all clinical laboratories.

## Test Development & Validation

### Pre-Analytical Phase

**Sample Collection**:
- **Specimen Type**: Blood (EDTA tube, 5-10mL typically), saliva, tissue
- **Stability**: Temperature requirements, shelf-life
- **Labeling**: Patient identification, unique specimen ID
- **Transportation**: Courier requirements, temperature control
- **Documentation**: Chain of custody maintenance

**DNA Extraction**:
- **Method Validation**: Bench-top evaluation of yield and purity
- **Quality Metrics**: A260/A280 ratio (1.7-1.9 ideal), DNA concentration
- **Degradation Assessment**: Fragment analysis, agarose gel
- **Contamination Screening**: No bacteria, no PCR inhibitors

**Library Preparation**:
- **Input Amount**: Validated DNA quantity (typically 100-500ng)
- **Fragment Size**: Target insert size (e.g., 300bp for Illumina)
- **Adapter Ligation**: Efficiency validation
- **QC Metrics**: Fragment analyzer confirmation

### Analytical Validation

**Analytical Sensitivity (Detection Limit)**:
```
Sensitivity = # true positives / (# true positives + # false negatives)
```

**Definition**: Minimum variant allele frequency (VAF) reliably detected.

**Determination**:
1. Create samples with known variants at decreasing VAF
2. Sequence at target coverage
3. Calculate detection frequency at each VAF level
4. Report minimum detectable VAF (typically ≥90% detection)

**Documentation**:
- Minimum detectable VAF: e.g., 20% for heterozygous, 10% for somatic
- Sensitivity at clinically relevant VAF levels
- Coverage requirements to achieve sensitivity

**Analytical Specificity (False Positive Rate)**:
```
Specificity = # true negatives / (# true negatives + # false positives)
```

**Definition**: Proportion of tested variants correctly identified as absent.

**Determination**:
1. Sequence known reference samples (e.g., HapMap genotypes)
2. Compare called variants to known truth set
3. Calculate false positive rate
4. Report specificity at clinical VAF cutoff

**Documentation**:
- Specificity: e.g., >99.9%
- False positive rate per megabase
- Comparison to reference materials

### Clinical Validation

**Positive Predictive Value (PPV)**:
```
PPV = # true positive calls / # positive calls
```

**Determination**:
1. Test clinical samples with known variants
2. Validate called variants via Sanger sequencing
3. Calculate proportion confirmed
4. Report PPV: e.g., >98% at VAF cutoff

**Negative Predictive Value (NPV)**:
```
NPV = # true negative calls / # negative calls
```

**Determination**:
1. Test clinical samples known to lack variants
2. Confirm called negatives (optional validation)
3. Calculate proportion confirmed absent
4. Report NPV: >99.9% typical

**Clinical Sensitivity/Specificity**:
- Test known positive samples (affected individuals)
- Test known negative samples (unaffected or alternative disease)
- Calculate diagnostic sensitivity and specificity
- May differ from analytical metrics due to:
  - Incomplete penetrance
  - Genetic heterogeneity
  - Pathogenic variant overlap with benign variants

## Proficiency Testing & QC

### External Proficiency Testing (PT)

**Purpose**: Assess laboratory accuracy in comparison to peer labs.

**Programs**:
- **CAP Survey**: Comprehensive programs (if CAP accredited)
- **AABB**: Blood banking genetics
- **CLIA**: Required participation (minimum 2 samples/analyte/year)
- **G2L**: Genetics 2 Lab proficiency testing

**Sample Distribution**:
- Multiple unknown samples annually
- Scored pass/fail or graded on accuracy
- Results compared to peer performance
- Failures trigger corrective action

**Documentation**:
- PT reports filed and available for inspection
- Corrective actions for failures
- Personnel awareness of results
- Method improvements based on PT findings

### Internal Quality Control

**Positive & Negative Controls**:
- **Positive Control**: Known variant present, run with each batch
- **Negative Control**: Known variant absent, no contamination
- **Water/Blank**: No template control
- **Acceptance Criteria**: Control must pass before reporting results

**Replicate Testing**:
- **Reproducibility**: Repeat samples on separate run
- **Concordance**: ≥99.9% genotype concordance
- **Frequency**: Every run or batch testing

**Run Metrics**:
- **Cluster Analysis**: Verify expected clustering pattern
- **Coverage Statistics**: Mean depth, coverage distribution
- **GC Bias**: Assess uniformity across GC content
- **Error Rates**: Monitor contamination/quality trends

### Benchtop Validation Studies

**Concordance Studies**:
1. **Method Comparison**: Compare new method to established gold standard
   - Test 30-50 samples with both methods
   - Calculate concordance rate (target >99.5%)
   - Investigate discordances

2. **Platform Concordance**: Different instruments/labs
   - Same DNA sample on multiple platforms
   - Assess systematic differences
   - Establish equivalence

**Sensitivity Studies**:
1. **Dilution Series**: Create samples with decreasing variant VAF
   - Down to 50%, 25%, 10%, 5%, 1% VAF
   - Run at target coverage
   - Determine minimum detectable VAF

2. **Coverage Studies**:
   - Downsample data computationally
   - Test at 50x, 100x, 200x, 500x
   - Establish minimum coverage requirements

## Variant Confirmation & Validation

### Orthogonal Validation Methods

**Sanger Sequencing**:
- **Purpose**: Gold standard for variant confirmation
- **Method**: Chain-termination sequencing
- **Sensitivity**: Detects variants at ~5-10% VAF
- **Timeline**: 24-48 hours
- **Use**: Confirms pathogenic/clinical findings

**Digital PCR (ddPCR)**:
- **Purpose**: Highly sensitive variant detection
- **Method**: Partitioning into droplets, absolute quantification
- **Sensitivity**: Can detect variants at <0.1% VAF
- **Advantage**: VAF quantification without standard curve
- **Use**: Confirming rare somatic variants, MRD monitoring

**Quantitative PCR (qPCR)**:
- **Purpose**: Copy number variation confirmation
- **Method**: Real-time fluorescence monitoring
- **Application**: Validates large deletions/duplications
- **Use**: CNV confirmation from array/NGS

**MLPA (Multiplex Ligation-Dependent Probe Amplification)**:
- **Purpose**: Copy number assessment (targeted)
- **Application**: 40+ target regions, 12-50 probes
- **Use**: Exon/gene-level CNV confirmation
- **Advantage**: Cost-effective for targeted assessment

**Array CGH (Comparative Genomic Hybridization)**:
- **Purpose**: Genome-wide CNV assessment
- **Resolution**: 10kb-100kb depending on platform
- **Application**: Copy number discovery and confirmation
- **Use**: Comprehensive CNV characterization

### Bioinformatics Validation

**Variant Calling Accuracy**:
1. **Benchmark Datasets**: Test on gold-standard callsets
   - GIAB (Genome in a Bottle) references
   - NIST standards for high-confidence variants
   - Measure sensitivity/specificity

2. **Pipeline Validation**:
   - Compare variant calling algorithms
   - Assess filter settings impact
   - Optimize parameters for clinical use

**Annotation Accuracy**:
1. **Consequence Prediction**: Validate VEP/SnpEff accuracy
   - Compare to manually curated annotations
   - Assess missed/incorrect predictions
   - Update annotation parameters as needed

2. **Classification Accuracy**: Validate ACMG interpretation
   - Test on known pathogenic/benign variants
   - Assess correct classification rates
   - Compare to expert interpretation

## Analytical Performance Standards

### Recommended Thresholds

| Metric | Standard | Target |
|--------|----------|--------|
| Analytical Sensitivity | ≥90% detection | 95%+ |
| Analytical Specificity | >99.5% | 99.9%+ |
| Positive Predictive Value | >95% | 99%+ |
| Negative Predictive Value | >99% | 99.9%+ |
| Variant Concordance | >99% | 99.5%+ |
| Copy Number Accuracy | ±0.5 copies | ±0.25 copies |
| Genotype Accuracy | >99% | 99.9%+ |

### Minimum Coverage Requirements

| Test Type | Min Coverage | Recommended | Notes |
|-----------|--------------|-------------|--------|
| Whole Genome | 30x | 50-100x | Average across genome |
| Whole Exome | 100x | 150-200x | Average over targeted region |
| Gene Panel (broad) | 100x | 200-500x | Depends on disease penetrance |
| Gene Panel (targeted) | 500x | 1000x+ | Cancer/somatic variants |
| Mitochondrial | 1000x+ | 10,000x+ | Heteroplasmy detection |

## Data Management & Security

### HIPAA Compliance

**Safeguards Required**:
1. **Administrative**:
   - Privacy officer designation
   - Workforce security training
   - Incident response procedures
   - Audit controls logging

2. **Physical**:
   - Facility access controls
   - Workstation use/security policies
   - Device and media controls
   - Physical access audit trails

3. **Technical**:
   - Encryption at rest and in transit
   - Unique user authentication
   - Automatic logoff procedures
   - Transmission security

### Data Retention
**Standard Policies**:
- **Raw Data**: 2-7 years (varies by accreditation)
- **Processed Data**: 7-10 years
- **Reports**: Permanent (electronic archive)
- **Backup**: Regular backups with disaster recovery

**Genomic Data Considerations**:
- **Sensitivity**: Genomic data predicts future health
- **Return of Results**: Explicit consent needed
- **Incidental Findings**: Separate consent for secondary findings
- **Withdrawal**: Patient can withdraw future research use

## Variant Reporting Standards

### Report Components

**Required Elements**:
1. **Patient Identification**: Name, DOB, MRN
2. **Specimen Information**: Sample type, collection date, receipt date
3. **Test Ordered**: Specific test name and clinical indication
4. **Methods**: Technique, coverage, genes analyzed
5. **Results**: Findings with HGVS nomenclature
6. **Interpretation**: ACMG classification if Mendelian
7. **Clinical Significance**: Evidence supporting interpretation
8. **Laboratory Director**: Signature/initials, date
9. **Limitations**: Coverage gaps, methodologic limits, caveats

**Optional Elements**:
- Family history correlation
- Segregation analysis results
- Literature references
- Recommendations for family screening
- Genetic counseling referral

### Reporting Formats

**Structured Reporting**:
- Standardized templates
- Checkboxes for findings categories
- Integrated with EHR
- Machine-readable format

**Narrative Reporting**:
- Free-text interpretation
- Case-specific nuance
- Complex findings explanation
- Family/phenotype context

**Hybrid Approach**:
- Structured data fields + narrative interpretation
- Balance standardization with flexibility
- Machine-readable + human-readable

## Continuous Quality Improvement

### Performance Monitoring

**Metrics Tracked**:
- **Turn-around time**: Days from receipt to report
- **Analytical success rate**: % samples with valid results
- **Error rate**: Incorrect genotypes or interpretations
- **Customer satisfaction**: Provider feedback
- **Referral patterns**: Which tests ordered

### Corrective Actions

**When Issues Arise**:
1. **Investigation**: Root cause analysis
2. **Containment**: Prevent recurrence
3. **Notification**: Affected patients/providers
4. **Correction**: Corrected report issued
5. **Prevention**: Process improvement implemented
6. **Documentation**: Filed with PT/CAP records

### Staff Competency

**Initial Training**:
- Standard operating procedures (SOPs)
- Quality standards
- Interpretation guidelines (ACMG, disease-specific)
- Data security and HIPAA

**Ongoing Education**:
- Annual continuing education
- Updates on new guidelines
- Proficiency testing results review
- Quality improvement discussions
- Genetic counselor/physician collaboration

## Regulatory Change Management

### Monitoring Guideline Updates

**Key Sources**:
- ACMG standards updates (periodic major revisions)
- CPIC guidelines (quarterly new drugs/genes)
- ClinVar assertions (continuous updates)
- Gene-disease evidence changes (literature monitoring)
- FDA biomarker updates

### Implementation of Changes

**Systematic Approach**:
1. **Awareness**: Subscribe to updates
2. **Assessment**: Evaluate impact on current practice
3. **Planning**: Determine implementation timeline
4. **Training**: Staff education on changes
5. **Validation**: Test implementation before clinical use
6. **Deployment**: Roll-out to clinical practice
7. **Monitoring**: Track compliance with new standards

**Documentation**:
- Change control log
- Effective dates
- Staff sign-off on training
- Validation results
