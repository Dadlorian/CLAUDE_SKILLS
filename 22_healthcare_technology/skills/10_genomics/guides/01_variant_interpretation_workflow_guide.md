# Variant Interpretation Workflow Guide

## Overview
This guide provides a step-by-step systematic approach to interpret genetic variants clinically, following ACMG 2015 standards with 2017 updates.

## Phase 1: Data Quality Assessment

### Step 1.1 Examine Sequencing Metrics
1. **Review Raw Data Quality**:
   - Check sequencing quality scores (Phred scores)
   - Verify GC content distribution (40-50% for human)
   - Assess adapter contamination (<2%)
   - Review duplication rate (<10% for WGS)

2. **Review Alignment Quality**:
   - Overall alignment rate: >95%
   - Properly paired reads: >90%
   - Mapping quality distribution (MAPQ)
   - Check for potential contamination

### Step 1.2 Assess Variant-Level Quality
1. **Examine VCF FILTER Field**:
   - Look for PASS vs. specific filter assignments
   - Understand filter definitions applied
   - Review any low-quality calls

2. **Evaluate Quality Metrics**:
   ```
   QUAL ≥ 20: Acceptable quality
   GQ ≥ 20: Confident genotype
   DP ≥ 10x: Minimum coverage (adjust for test)
   AF/VAF: Check allele frequency is reasonable
   AD: Allele depth counts consistent with genotype
   ```

3. **Check Strand Bias**:
   - Review FS (Fisher Strand) score
   - SOR (Strand Odds Ratio) < 3.0 preferred
   - Variants with significant bias: Flag for review

### Step 1.3 Validate Variant Call
1. **Confirm Genotype**:
   - Manual inspection of BAM file at variant location
   - Verify reads support called allele
   - Check for technical artifacts

2. **Assess Coverage**:
   - Adequate coverage at locus
   - Uniform depth in region
   - Flag if coverage <10x

## Phase 2: Variant Annotation & Functional Assessment

### Step 2.1 Annotate Variant
1. **Nomenclature Standardization**:
   - Convert to HGVS format: `Gene.Transcript:c.position:p.consequence`
   - Use RefSeq (NM_) transcripts preferred
   - Include both DNA and protein notation
   - Verify nomenclature with HGVS checker

2. **Determine Consequence**:
   - Run VEP or SnpEff annotation
   - Identify predicted consequence:
     - Frameshift, stop-gain/loss, splice site: HIGH impact
     - Missense, in-frame indel: MODERATE impact
     - Synonymous, intronic: LOW impact
   - Select canonical/most severe consequence

### Step 2.2 Assess Functional Impact
1. **Check Gene Function**:
   - Review Gene Cards or OMIM for gene function
   - Understand how variant affects protein
   - Consider protein structure/domains affected
   - Assess if mutation in critical region

2. **Computational Predictions**:
   - Run multiple prediction tools:
     - SIFT: Tolerated vs. Deleterious
     - PolyPhen-2: Benign, Possibly damaging, Probably damaging
     - CADD: Score interpretation
     - AlphaMissense: Pathogenic probability
   - Look for consensus across tools (not all predictions equal)
   - Note that predictions are probabilistic

3. **Conservation Assessment**:
   - Check phyloP/GERP conservation scores
   - Higher conservation = more likely important
   - Focus on nucleotides highly conserved across species

## Phase 3: Population Frequency Assessment

### Step 3.1 Query Frequency Databases
1. **Check gnomAD**:
   - Filter "PASS" variants
   - Note exact allele frequency
   - **Critical**: Use correct ancestry group
   - Compare across ancestry groups (frequency variation)
   - If AF ≥5%: Likely benign (BA1 criterion met)

2. **Secondary Frequency Checks**:
   - ClinVar for reported frequencies
   - 1000 Genomes (if gnomAD not available)
   - dbSNP for historical frequency data
   - COSMIC for cancer-specific frequencies (somatic)

### Step 3.2 Evaluate Rarity
1. **Categorize Frequency**:
   - **Common** (AF ≥1%): Usually benign
   - **Low frequency** (0.01% ≤ AF <1%): Uncertain
   - **Rare** (AF <0.01%): More likely pathogenic
   - **Singleton**: Only seen once, newmutation possible

2. **Population-Specific Assessment**:
   - Check ancestry of patient vs. database population
   - Use matching ancestry frequency when available
   - Document which population frequency used
   - Be cautious with admixed individuals

## Phase 4: Clinical & Segregation Evidence

### Step 4.1 Assess Phenotype Match
1. **Review Patient Phenotype**:
   - Collect comprehensive clinical information
   - Document all symptoms/signs/findings
   - Review family history
   - Note age of onset, severity, progression

2. **Match to Gene Function**:
   - Does gene function match patient phenotype?
   - Is phenotype consistent with gene-disease association?
   - Are there overlapping features?
   - Note discrepancies (may suggest misdiagnosis)

3. **Literature Review**:
   - Search PubMed for variant + disease
   - Search gene + patient phenotype
   - Look for case reports with same mutation
   - Note if variant previously reported as pathogenic

### Step 4.2 Evaluate Family Studies
1. **De Novo Assessment** (if parents available):
   - Confirm BOTH parents tested at locus
   - If variant present in one parent: Not truly de novo
   - De novo in unaffected parent: Consider low penetrance
   - Document parental status in report

2. **Segregation Analysis** (if family available):
   - Does variant segregate with disease?
   - Present in all affected family members?
   - Absent in unaffected relatives?
   - Large families provide stronger evidence
   - Calculate LOD score if possible

## Phase 5: ACMG Criteria Application

### Step 5.1 Evaluate Pathogenic Criteria (P/LP)

**Check PVS1** (Very Strong):
- Is gene loss-of-function intolerant? (Check pLI/LOEUF)
- Is variant a clear null? (Frameshift, stop-gain, splice consensus)
- Apply exceptions (pseudogenes, isoforms, 3'UTR)
- Result: PVS1 applicable OR not applicable

**Check PS1-PS4** (Strong):
- PS1: Exact same aa change as known pathogenic (different codon)?
- PS2: De novo confirmed (both parents tested, unaffected)?
- PS3: Functional studies available showing loss-of-function?
- PS4: Prevalence significantly higher in affected than unaffected?

**Check PM1-PM6** (Moderate):
- PM1: In documented mutational hot spot?
- PM2: Absent from large population databases? (<0.005% or absent)
- PM3: In trans with pathogenic variant (compound het in recessive)?
- PM4: Protein-altering indels in loss-of-function genes?
- PM5: Different nucleotide at same aa where pathogenic mutation found?
- PM6: De novo (assumed parental origin unknown)?

**Check PP1-PP5** (Supporting):
- PP1: Co-segregates with disease in family?
- PP2: Missense in low-rate-of-benign-missense gene?
- PP3: Computational evidence supports damaging effect?
- PP4: Phenotype/family/lab findings specific for gene?
- PP5: Reputable source recently reports as pathogenic?

**Aggregate Pathogenic Evidence**:
```
Pathogenic: 1×PVS1 + ≥1×PS OR ≥2×PS OR 1×PS + ≥2×PM OR ≥3×PM
Likely Pathogenic: 1×PVS1 + 1×PM OR 1×PS + ≥1×PM OR ≥3×PM
```

### Step 5.2 Evaluate Benign Criteria (B/LB)

**Check BA1** (Standalone):
- Minor allele frequency ≥5% in general population?
- YES → Benign (standalone)

**Check BS1-BS4** (Strong):
- BS1: MAF higher than expected for disease? (>1% for dominant, etc.)
- BS2: Observed homozygous in unaffected individual (recessive)?
- BS3: Well-established functional studies show no loss-of-function?
- BS4: Lack of segregation in affected family members?

**Check BP1-BP7** (Supporting):
- BP1: Missense in gene with low rate of benign missense?
- BP2: In cis with pathogenic variant (same chromosome)?
- BP3: In-frame indel in repetitive region?
- BP4: Computational evidence suggests no impact?
- BP5: Found in case report but no convincing phenotype match?
- BP6: Absent from affected individuals in case-control study?
- BP7: Synonymous with no predicted splice impact?

**Aggregate Benign Evidence**:
```
Benign: ≥1×BA1 OR ≥2×BS
Likely Benign: 1×BS + ≥1×BP OR ≥2×BP
```

## Phase 6: Final Classification

### Step 6.1 Reconcile Evidence
1. **Tally Evidence**:
   - List all applicable ACMG criteria
   - Note strength of each
   - Identify any conflicting evidence

2. **Weight Evidence**:
   - Not all criteria are equal weight
   - Functional evidence (PS3/BS3) highly valuable
   - Frequency evidence (BA1/BS1) can override others
   - Consider interdependencies between criteria

3. **Apply Inheritance Pattern**:
   - Dominant vs. recessive context affects interpretation
   - Compound heterozygosity strengthens recessive pathogenicity
   - De novo strengthens dominant pathogenicity

### Step 6.2 Assign Classification
1. **Determine Tier**:
   ```
   Pathogenic: P ← Strong evidence, clinically significant
   Likely Pathogenic: LP ← Good evidence, likely causes disease
   Uncertain Significance: VUS ← Insufficient evidence
   Likely Benign: LB ← Some evidence suggests benign
   Benign: B ← Strong evidence, not pathogenic
   ```

2. **Document Reasoning**:
   - Write brief summary of key evidence
   - Justify classification with specific criteria
   - Note any limitations
   - Suggest future studies if applicable

## Phase 7: Monitoring & Reassessment

### Step 7.1 VUS Monitoring
For variants classified as VUS:
1. **Set up alert system**: Monitor ClinVar, PubMed
2. **Track new evidence**: Functional studies, clinical outcomes
3. **Annual review**: Check if new data warrants reclassification
4. **Communicate updates**: Notify original requesters if reclassified

### Step 7.2 Documentation
1. **Maintain audit trail**:
   - Record classification date
   - Document all evidence reviewed
   - Note databases/tools used
   - Record personnel performing interpretation

2. **Prepare for reclassification**:
   - Monitor for contradicting evidence
   - Track literature updates
   - Be ready to revise if warranted
   - Communicate reclassifications appropriately

## Practical Workflow Template

### Quick Reference Checklist

```
□ Step 1: Quality Assessment
  □ VCF quality metrics acceptable?
  □ Variant-level quality adequate?
  □ Strand bias assessment done?

□ Step 2: Annotation
  □ HGVS nomenclature standardized?
  □ Functional consequence determined?
  □ Computational predictions obtained?

□ Step 3: Frequency Assessment
  □ gnomAD frequency checked?
  □ Ancestry-specific frequency reviewed?
  □ Rarity categorized?

□ Step 4: Clinical Evidence
  □ Phenotype match assessed?
  □ Family studies reviewed?
  □ Literature searched?

□ Step 5: ACMG Criteria
  □ Pathogenic criteria evaluated?
  □ Benign criteria evaluated?
  □ Evidence aggregated?

□ Step 6: Classification
  □ Final tier assigned?
  □ Reasoning documented?
  □ Confidence level noted?

□ Step 7: Monitoring
  □ Follow-up plan for VUS?
  □ Audit trail complete?
  □ Reclassification plan established?
```

## Common Interpretation Pitfalls

### Pitfall 1: Over-relying on Frequency
**Problem**: Assuming rare = pathogenic
**Solution**: Integrate with functional evidence; many benign variants are rare

### Pitfall 2: Ignoring Population Specificity
**Problem**: Using European frequency for African patient
**Solution**: Always use ancestry-specific frequency

### Pitfall 3: Misapplying Criteria
**Problem**: Applying ACMG criteria incorrectly or inconsistently
**Solution**: Review ACMG paper carefully; use standardized interpretation

### Pitfall 4: Neglecting Gene Function
**Problem**: Interpreting variant without understanding gene biology
**Solution**: Research gene thoroughly before classification

### Pitfall 5: Insufficient Segregation Data
**Problem**: Making strong conclusions with limited family data
**Solution**: Note limitations; consider as supporting, not definitive

## Escalation for Complex Cases

### When to Seek Expert Review
- Conflicting computational predictions
- Variants in genes with controversial disease associations
- Cases with unusual phenotypes
- Variants of major clinical significance
- Complex segregation patterns

### Consultation Resources
- Pathologist specialized in genetics
- Genetic counselor
- Literature experts in specific gene/disease
- ClinGen experts for contested genes
- Institutional medical genetics committee
