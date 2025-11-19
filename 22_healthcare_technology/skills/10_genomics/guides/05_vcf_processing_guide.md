# VCF Processing & Annotation Guide

## Overview
Standardized approach to VCF file processing from variant calling through annotation.

## Phase 1: VCF Quality Assessment

### Step 1.1 VCF Structure Validation
1. **Header Validation**:
   - Correct fileformat declaration (VCFv4.2)
   - All INFO fields properly defined
   - FORMAT fields documented
   - contig information present

2. **Data Line Checks**:
   - Verify required columns present (#CHROM through FORMAT/samples)
   - Check for valid chromosome names
   - Ensure POS is integer, REF/ALT are valid bases
   - Verify QUAL values

### Step 1.2 Variant Count & QC
1. **Summary Statistics**:
   - Total variants called
   - Transition/transversion ratio (2.0-2.1 expected)
   - Heterozygous/homozygous ratio (1.5-2.0 expected)
   - Variant type distribution (SNVs vs. indels)

2. **Quality Filtering**:
   - % variants with QUAL >20
   - % variants with QUAL >30
   - % variants with PASS filter
   - Distribution of GQ scores

### Step 1.3 Comparison to References
- GIAB concordance if available
- Known SNP presence verification
- Batch effect assessment
- Population allele frequency consistency

## Phase 2: Variant Normalization

### Step 2.1 Decomposition
- Split multi-allelic sites to biallelic
- Normalize indels (left-align to earliest position)
- Remove reference duplicates
- Standardize nomenclature

### Step 2.2 Coordinate System Standardization
- Convert between 0-based and 1-based if needed
- Map GRCh37 to GRCh38 if necessary
- Document reference assembly version
- Verify position accuracy post-conversion

### Step 2.3 Variant Normalization Tools
- **bcftools**: `bcftools norm -f ref.fa variants.vcf`
- **vt**: `vt decompose -s variants.vcf`
- **GATK**: LeftAlignAndTrimVariants

## Phase 3: Annotation Pipeline

### Step 3.1 Gene-Level Annotation
1. **VEP (Variant Effect Predictor)**:
   ```
   vep --input_file variants.vcf \
       --assembly GRCh38 \
       --cache --offline \
       --tab --output_file annotated.txt
   ```

2. **Key Outputs**:
   - Gene name (HGNC symbol)
   - Transcript ID
   - Consequence prediction
   - Protein position
   - SIFT/PolyPhen predictions

### Step 3.2 Frequency Annotation
- gnomAD allele frequency (all populations + ancestry-specific)
- 1000 Genomes frequency
- ESP frequency (if applicable)
- COSMIC frequency (cancer variants)

### Step 3.3 Functional Annotation
- Conservation scores (GERP, phyloP)
- CADD score
- AlphaMissense prediction
- FATHMM-MKL score
- dbNSFP integration

### Step 3.4 Clinical Database Integration
- ClinVar assertions
- COSMIC somatic variants
- HGMD professional
- UniProt/SwissProt

## Phase 4: Filtering & Prioritization

### Step 4.1 Hard Filtering
```
Apply to all variants:
- Remove intronic variants (unless splice-affecting)
- Remove synonymous variants (unless predicted splicing impact)
- Filter by frequency: MAF < 0.01 for rare disease
- Remove common benign variants: MAF > 1% in gnomAD
```

### Step 4.2 Impact-Based Filtering
```
Prioritize:
- HIGH impact: frameshift, stop-gain/loss, splice
- MODERATE impact: missense, in-frame indel
- LOW impact: synonymous with splicing prediction
- MODIFIER impact: intronic, intergenic
```

### Step 4.3 Clinical Relevance Filtering
- Known pathogenic in ClinVar?
- In gene relevant to phenotype?
- Consistent with inheritance pattern?
- Population-specific frequency?

## Phase 5: Quality Control & Validation

### Step 5.1 Internal Validation
- Re-sequence variant locus
- Sanger sequencing confirmation (orthogonal method)
- ddPCR for somatic/low VAF variants

### Step 5.2 Comparison Checks
- SNP concordance with array genotypes
- Pedigree consistency (Mendelian errors)
- Duplicate sample concordance
- Batch effect assessment

## Phase 6: Output & Archival

### Step 6.1 Final VCF Output
- Annotated VCF with all fields
- Compressed and indexed (bgzip + tabix)
- Metadata documenting analysis version
- Quality metrics included

### Step 6.2 Data Archival
- Store raw VCF
- Store annotated VCF
- Document pipeline version
- Backup on secure storage

---

# Bioinformatics Best Practices Guide

## Workflow Standards

### Step 1: Alignment Best Practices
1. **Reference Alignment**:
   - Use GRCh38 with decoys for human
   - Remove duplicate reads with Picard MarkDuplicates
   - Recalibrate base quality with GATK BaseRecalibrator

2. **Quality Metrics**:
   - Minimum 50x for germline, 100x+ for cancer
   - >95% alignment rate expected
   - >90% properly paired reads
   - Monitor MAPQ distribution

### Step 2: Variant Calling Standards
1. **Primary Callers**:
   - GATK HaplotypeCaller (germline WES/WGS)
   - DeepVariant (high-accuracy alternative)
   - Strelka (somatic + indel)
   - MuTect2 (somatic germline comparison)

2. **Filtering Approach**:
   - GATK VQSR for quality filtering
   - Conditional filters if small sample size
   - Document filtering decisions

### Step 3: Annotation Protocol
1. **Primary Annotation**:
   - VEP or SnpEff (consistent tool choice)
   - gnomAD frequency annotation
   - Conservation score integration
   - Functional prediction tools

2. **Custom Annotations**:
   - Add lab-specific databases
   - Include in-house disease associations
   - Document custom field definitions

## Quality Assurance Standards

### Proficiency Testing
- Participate in CAP or external PT program
- Quarterly or biannual samples
- Monitor pass/fail rates
- Document corrective actions

### Internal QC
- Positive/negative controls per run
- Reproducibility testing (repeat samples)
- Batch effect monitoring
- Genotype concordance >99.9%

### Data Validation
- Sanger sequencing for reported variants
- Array comparison for SNP concordance
- Pedigree analysis for Mendelian errors
- Cross-platform comparison

## Bioinformatics Infrastructure

### Compute Environment
- Secure server with access controls
- Regular backups (daily minimum)
- Disaster recovery planning
- Hardware redundancy for critical components

### Software Management
- Document all tools and versions
- Implement version control for scripts
- Validate new software before clinical use
- Archive obsolete but historical tools

### Data Security
- Encrypt data at rest and in transit
- Limit access to authorized personnel
- Audit log access and modifications
- Regular security assessments

## Troubleshooting Common Issues

### Low Coverage Regions
- **Problem**: Inadequate coverage in specific regions
- **Causes**: GC content, sequence complexity, repeats
- **Solutions**: Increase target coverage, use long-read sequencing, design better baits

### Copy Number Calling Challenges
- **Problem**: Inconsistent CNV detection
- **Causes**: Low coverage, segmental duplications, ploidy
- **Solutions**: Higher coverage, long-read support, manual inspection

### Variant Calling Discordance
- **Problem**: Different callers give different results
- **Causes**: Different algorithms, quality filtering, callers
- **Solutions**: Use ensemble calling, orthogonal validation, review discordant calls

---

# EHR Integration & Genomic Data Exchange Guide

## Overview
Integration of genomic findings with electronic health record systems for clinical decision support.

## Phase 1: EHR Preparation

### Step 1.1 System Capabilities Assessment
1. **Current Functionality**:
   - Can system receive structured genomic data?
   - Support for FHIR or proprietary formats?
   - Clinical decision support capabilities?
   - Patient portal access?

2. **Integration Requirements**:
   - HL7v2 vs. FHIR vs. custom interfaces?
   - Authentication/security standards?
   - Data formatting specifications?
   - Real-time vs. batch processing?

### Step 1.2 Workflow Planning
1. **Test Ordering**:
   - How genomic tests ordered?
   - Indication documentation required?
   - Consent management integrated?

2. **Result Return**:
   - How results delivered to providers?
   - Patient notification process?
   - Follow-up care triggers?

## Phase 2: Data Standard Mapping

### Step 2.1 FHIR Genomics Mapping
- Map local variant data to FHIR Observation resources
- Create MolecularSequence references
- Link to Patient, Specimen, DiagnosticReport
- Include interpretation codes (ACMG, CIViC)

### Step 2.2 Clinical Decision Support
1. **Rule Engine Configuration**:
   - Identify actionable mutations in EHR
   - Create alerts for Tier 1A/1B findings
   - Link to relevant clinical guidelines
   - Provider education materials

2. **Examples**:
   - HER2+ breast cancer → Alert for trastuzumab
   - EGFR mutation lung cancer → Alert for EGFR inhibitor
   - MSI-H colorectal → Alert for pembrolizumab

## Phase 3: Implementation

### Step 3.1 Data Exchange Interface
1. **Technical Setup**:
   - Configure HL7/FHIR interface
   - Test data transmission
   - Verify security encryption
   - Establish error handling

2. **Testing Protocol**:
   - Send test results
   - Verify EHR receipt
   - Confirm display formatting
   - Test alert triggering

### Step 3.2 Provider Portal
- Display genomic results clearly
- Actionable recommendations prominent
- Links to clinical guidelines
- Contact information for questions

### Step 3.3 Patient Portal
- Secure access to results
- Layman-friendly explanations
- Visual representations if helpful
- Contact genetic counselor option

## Phase 4: Workflow Integration

### Step 4.1 Oncology Workflow Example
1. **Test Order**:
   - Oncologist orders tumor genomics panel
   - Tumor site and clinical stage documented
   - Consent for secondary findings

2. **Sample Collection**:
   - Tissue sent to genomics lab
   - Lab confirms adequacy
   - Sequencing initiates

3. **Result Reporting**:
   - Lab sends annotated report
   - Report displays in EHR
   - Alert triggered for actionable findings
   - Tumor board notification

4. **Treatment Planning**:
   - Oncologist reviews findings
   - Treatment recommendation made
   - Alternative options discussed
   - Clinical trial options presented

5. **Follow-up Monitoring**:
   - Treatment plan documented
   - Response assessment scheduled
   - Resistance monitoring if appropriate

### Step 4.2 Pharmacy Integration
1. **Pharmacogenomics Example**:
   - Patient starts antidepressant
   - CYP2D6 genotype available in EHR
   - Alert if dose adjustment needed
   - Pharmacist reviews before dispensing
   - Patient educated on metabolism

## Phase 5: Data Quality & Governance

### Step 5.1 Data Accuracy
- Verify patient identifiers match
- Confirm test date accuracy
- Validate result entry
- Monitor for transcription errors

### Step 5.2 Access Control
- Role-based access (lab, oncology, genetics)
- Patient consent for each use
- Audit log of all accesses
- Annual review of access rights

### Step 5.3 Data Retention
- Follow regulatory requirements (7-10 years minimum)
- Backup critical data
- Secure deletion after retention period
- Disaster recovery tested regularly

## Best Practices

### Provider Education
- Workshops on genomics interpretation
- Quarterly updates on new findings
- Case-based learning
- Genetic counselor collaboration

### Patient Communication
- Explain test purpose clearly
- Discuss limitations and uncertainty
- Offer counseling support
- Provide educational materials

### Continuous Improvement
- Collect provider feedback
- Monitor alert fatigue
- Track treatment decision impact
- Update based on latest guidelines
