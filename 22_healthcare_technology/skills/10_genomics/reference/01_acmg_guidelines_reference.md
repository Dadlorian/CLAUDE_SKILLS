# ACMG Standards for Genomic Sequence Interpretation Reference

## Overview
The American College of Medical Genetics (ACMG) 2015 standards provide a unified approach to variant classification applicable to most genetic conditions. Updated in 2017 with additional guidance.

## Five-Tier Classification System

### Tier 1: Pathogenic (P)
**Definition**: Strong evidence that variant causes disease. Appropriate to report as causative finding.
**Criteria Combinations**:
- 1 PVS1 AND ≥1 PS criterion
- ≥2 PS criteria
- 1 PS AND ≥2 PM criteria
- 1 PS AND 1 PM AND ≥1 PP criterion
- ≥2 PM AND ≥2 PP criteria

### Tier 2: Likely Pathogenic (LP)
**Definition**: Likely causes disease but insufficient for clinical certainty.
**Criteria Combinations**:
- 1 PVS1 AND 1 PM criterion
- 1 PS AND ≥1 PM criterion
- ≥3 PM criteria
- 2 PM AND ≥2 PP criteria
- 1 PM AND ≥2 PP AND ≥1 BP criterion (if BP is supporting)

### Tier 3: Variant of Uncertain Significance (VUS)
**Definition**: Insufficient evidence for pathogenicity classification. Continue monitoring literature.
**Criteria**: Does not meet criteria for other tiers.

### Tier 4: Likely Benign (LB)
**Definition**: Likely does not cause disease but not enough for clinical certainty.
**Criteria Combinations**:
- ≥1 BS AND ≥1 BP
- ≥2 BP without BS criteria

### Tier 5: Benign (B)
**Definition**: Strong evidence variant does not cause disease.
**Criteria Combinations**:
- ≥1 BA criterion
- ≥2 BS criteria

## Pathogenic Criteria (P/LP)

### PVS1 (Very Strong)
**Null Variant**: Frameshift, stop-gain, or splice site disruption in gene where loss-of-function (LoF) is mechanism of disease.
**Exceptions to Apply**:
- Genes with redundancy or isoforms
- Missense-tolerant genes
- 3' UTR variants
- Synonymous variants
- Deep intronic variants outside splice consensus

### PS1-PS4 Strength

| Criterion | Description | Application |
|-----------|-------------|-------------|
| PS1 | Same amino acid change as pathogenic variant (different nucleotide) | Strong evidence of recurrent mutation |
| PS2 | De novo mutation (confirmed parental origin) in dominant disease | Establishes new mutation causality |
| PS3 | Well-established functional studies show loss/gain of function | Laboratory functional assays |
| PS4 | Prevalence in affected vs. unaffected varies significantly | Segregation pattern analysis |

### PM1-PM6 Strength

| Criterion | Description | Application |
|-----------|-------------|-------------|
| PM1 | Mutational hot spot and/or region of special interest | ACMG specified domains |
| PM2 | Absent from large population databases | Allele frequency cutoff 0.005% |
| PM3 | For recessive disorders: found in trans with pathogenic variant | Compound heterozygous pattern |
| PM4 | Protein length changes due to indels/stop loss | In genes sensitive to loss of function |
| PM5 | Novel missense change at amino acid with pathogenic substitution | Functional domain specificity |
| PM6 | De novo (assumed parental origin unknown/unconfirmed) | Lower specificity than PS2 |

### PP1-PP5 Strength

| Criterion | Description | Application |
|-----------|-------------|-------------|
| PP1 | Co-segregates with disease in multiple affected family members | Supportive evidence only |
| PP2 | Missense variant in gene with low rate of benign missense variation | Gene-specific analysis |
| PP3 | Multiple lines of computational evidence support damaging effect | Prediction tools consensus |
| PP4 | Patient phenotype/family history/laboratory findings specific for gene | Phenotype matching |
| PP5 | Reputable source recently reports variant as pathogenic | Limited use, recent publications |

## Benign Criteria (BP/LB)

### BA1 (Standalone)
**High Minor Allele Frequency**: ≥5% in general population (gnomAD, 1000G, ESP) in same ancestry group.

### BS1-BS4 Strength

| Criterion | Description | Threshold |
|-----------|-------------|-----------|
| BS1 | Minor allele frequency higher than expected for disorder | MAF >1% for dominant disease |
| BS2 | Observed in healthy adult homozygous state in recessive disease | Rules out homozygous causality |
| BS3 | Well-established functional studies show no deleterious effect | Functional assays negative |
| BS4 | Lack of segregation with disease in affected family members | Multiple family analysis |

### BP1-BP7 Strength

| Criterion | Description | Application |
|-----------|-------------|-------------|
| BP1 | Missense variant in gene with low rate of pathogenic missense | Benign-enriched domains |
| BP2 | Observed in cis with pathogenic variant on same chromosome | Cis/trans configuration |
| BP3 | In-frame indels in repetitive regions without known function | Repetitive sequence tolerance |
| BP4 | Computational evidence suggests no impact | Conflicting predictions |
| BP5 | Variant found in case report but no convincing phenotype match | Incidental findings |
| BP6 | Absent from affected individuals in large case-control study | Negative case studies |
| BP7 | Synonymous variant with no predicted impact on splicing | Silent nucleotide change |

## Special Considerations

### ACMG SF v3.0 Secondary Findings
**73 Recommended Genes** for reporting incidental findings:

**Cancer Predisposition** (51 genes):
- BRCA1, BRCA2, PTEN, TP53, CHEK2, PALB2, etc.

**Cardiac Conditions** (14 genes):
- MYBPC3, MYH7, TNNT2, etc.

**Pharmacogenomics** (8 genes):
- TPMT, SLCO1B1, CYP3A5, etc.

### Age-Appropriate Reporting
- **Pediatric Patients**: Exclude adult-onset conditions (e.g., hereditary cancer syndromes onset age 40+)
- **Adult Patients**: Include all genes regardless of age of onset
- **Updated Recommendations**: Added dilated cardiomyopathy genes (2021)

### Modifier Guidance for Missense Variants

**Consider Lower Pathogenicity**:
- Located in C-terminal region of proteins
- Multiple benign missense in locus
- Predicted benign by algorithms
- Located in low-constraint regions

**Consider Higher Pathogenicity**:
- At functional domain boundaries
- At ATP/substrate binding sites
- In zinc finger regions
- Conservation highly preserved

## Incidental Findings Management

### Workflow
1. **Detection**: Variant identified during analysis
2. **Classification**: Apply ACMG criteria
3. **Confirmation**: Verify genotype accuracy
4. **Consent Check**: Return of results discussion
5. **Reporting**: Structured variant report
6. **Notification**: Secure communication to referring provider
7. **Documentation**: Audit trail and counseling notes

### Consent Implications
- **Prospective Consent**: Patient agrees in advance to receive secondary findings
- **Retrospective Consent**: Patient given opportunity to opt-out after discovery
- **Institutional Policy**: Varies by laboratory and IRB guidance

## Classification Reassessment

### Triggers for Reclassification
- New literature published with conflicting evidence
- Frequency changes in population databases
- Functional assay results become available
- Clinical outcomes in affected families
- Updates to gene classification (LoF-tolerant status)

### Best Practices
- Monitor ClinVar submissions quarterly
- Subscribe to disease-specific clinical updates
- Maintain classification audit trail
- Communicate reclassifications to original requesters
- Track outcomes for VUS variants

## Interaction with Penetrance & Expressivity

### Reduced Penetrance Considerations
- Lower confidence in segregation studies
- Clinical findings may not appear in all mutation carriers
- Age-dependent manifestation considerations
- Environmental factors influencing expression

### Variable Expressivity Implications
- Severity varies among affected individuals
- Phenotype expansion over time
- Requires careful family phenotyping
- May affect clinical utility of finding
