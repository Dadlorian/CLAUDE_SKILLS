# Pharmacogenomics (PGx) Reference

## Overview
Pharmacogenomics studies how genetic variations influence drug metabolism, efficacy, and toxicity. Clinical implementation involves genotyping relevant genes and translating genotypes to actionable medication guidance.

## Key Pharmacogenes

### Cytochrome P450 (CYP) System

**CYP2D6** - Major Drug Metabolizer
- **Substrates**: ~25% of drugs (antidepressants, antipsychotics, beta-blockers, opioids)
- **Common Variants**:
  - *1: Normal function
  - *2: Reduced function
  - *3,*4,*5: Loss of function (null variants)
  - *10, *41: Decreased function
  - Gene duplications/multiplications: Ultra-rapid metabolism

- **Phenotype Assignment**:
  - Ultra-Rapid Metabolizer (URM): ≥2.5 activity score (gene duplication)
  - Rapid Metabolizer (RM): 1.5-2.24 activity score
  - Normal Metabolizer (NM): 1.0-1.24 activity score
  - Intermediate Metabolizer (IM): 0.5-0.99 activity score
  - Poor Metabolizer (PM): <0.5 activity score

**Clinical Recommendations**:
- **Antidepressants**: Dose adjustments based on phenotype
- **Codeine**: PM/IM cannot activate prodrug (no analgesia)
- **Tamoxifen**: PM associated with reduced breast cancer benefit
- **Aripiprazole/Risperidone**: Increased toxicity in IM/PM

**Genotyping Challenges**:
- Structural variants (duplications, deletions)
- Pseudogene interference
- Copy number variations
- Requires specialized assays

**CYP2C19** - Clopidogrel/Escitalopram Metabolism
- **Key Variants**: *2,*3 (loss-of-function), *17 (increased function)
- **Phenotypes**: PM, IM, NM, RM
- **Clinical Uses**:
  - **Clopidogrel**: PM/IM at risk for thrombotic events (FDA warning)
  - **Escitalopram/Citalopram**: Dose reduction in IM/PM for QT prolongation
  - **Pantoprazole**: May reduce clopidogrel effectiveness

**CYP2C9** - Warfarin/NSAID Metabolism
- **Key Variants**: *2, *3 (reduced function)
- **Clinical Application**: Warfarin dosing algorithms
- **Effect**: IM/PM require lower maintenance doses
- **NSAIDs**: Reduced metabolism increases GI toxicity risk

**CYP3A4/5** - Largest CYP Subfamily
- **Substrates**: ~50% of drugs (immunosuppressants, statins, many cancers drugs)
- **CYP3A5*1 vs *3**: Major polymorphism affecting expressers vs. non-expressers
- **Clinical Significance**: Guides tacrolimus, sirolimus, everolimus dosing
- **Note**: Weak CYP2C8 inhibitor/inducer interactions common

**Other CYPs**:
- **CYP1A2**: Caffeine, warfarin (minor), theophylline metabolism
- **CYP2B6**: Efavirenz, cyclophosphamide metabolism
- **CYP2C8**: Repaglinide, cerivastatin metabolism

### Phase II Metabolism Genes

**TPMT (Thiopurine S-Methyltransferase)**
- **Substrates**: 6-Mercaptopurine, azathioprine, thioguanine
- **Variants**: *2, *3, *4, *5, *6 (null variants)
- **Phenotypes**: PM (0.3%), IM (10%), NM (90%)
- **Clinical Significance**: PM at extreme risk of bone marrow toxicity
- **Recommendations**:
  - PM: Reduce 6-MP dose by 85-90%
  - IM: Reduce dose by 33-50%
  - NM: Normal dosing

**NUDT15 (Nudix Hydrolase 15)**
- **Substrates**: Thiopurines (6-MP, azathioprine)
- **Variants**: Especially significant in Asian populations
- **Gene-Gene Interaction**: Works with TPMT for 6-MP toxicity prediction
- **Clinical Use**: Asian pediatric ALL treatment dosing

**COMT (Catechol-O-Methyltransferase)**
- **Val158Met Polymorphism**: Common functional SNP
- **Effect**: Dopamine/epinephrine metabolism
- **Variable Evidence**: Less clinically actionable currently

**NAT2 (N-Acetyltransferase 2)**
- **Substrates**: Isoniazid, sulfamethoxazole, carcinogenic amines
- **Phenotypes**: Slow acetylator (50%), fast acetylator (50%)
- **Clinical Significance**: Isoniazid-induced hepatotoxicity in slow acetylators

### Transporters

**SLCO1B1 (Solute Carrier Organic Anion)**
- **Substrates**: Statins (especially simvastatin, atorvastatin)
- **Variants**: c.521T>C, c.388A>G
- **Effect**: SLCO1B1 loss-of-function increases statin myopathy risk
- **FDA Guidance**: Consider alternative statins in T521T carriers

**MDR1/ABCB1 (P-glycoprotein)**
- **Substrates**: Many drugs (digoxin, fexofenadine, others)
- **Variants**: C3435T (common, variable effect)
- **Clinical Significance**: Modest effect on drug levels

### DNA Repair & Metabolism

**DPYD (Dihydropyrimidine Dehydrogenase)**
- **Substrate**: 5-Fluorouracil (5-FU), capecitabine, other fluoropyrimidines
- **Severe Deficiency**: Rare but life-threatening 5-FU toxicity
- **Common Variants**:
  - IVS14+1G>A (splicing variant)
  - c.496A>G (p.Asp166Gly)
  - c.1679T>G (p.Ile560Ser)
- **FDA Guidance**: Screen before 5-FU therapy
- **Recommendations**: PM at extreme risk (avoid 5-FU or use alternative)

## HLA Associations

### HLA-B*5701 (Abacavir)
- **Association**: Abacavir hypersensitivity reaction (2-9% of exposed)
- **Consequence**: Severe, life-threatening reaction
- **Screening**: Mandatory before abacavir initiation
- **Recommendation**: Avoid abacavir if HLA-B*5701 positive

### HLA-A*3101 (Carbamazepine)
- **Association**: Carbamazepine severe cutaneous adverse reactions (SCARes)
- **Populations**: Especially relevant in Han Chinese, Thai populations
- **Effect**: Severe, non-recoverable reactions
- **Screening**: FDA recommended pre-prescription testing in at-risk populations

### HLA-B*1502 (Carbamazepine)
- **Association**: Severe cutaneous reactions (SJS/TEN)
- **Populations**: Asian descent, especially Han Chinese
- **Screening**: FDA required testing before carbamazepine
- **Recommendation**: Avoid carbamazepine if HLA-B*1502 positive

### HLA-DRB1*15:01, HLA-DQA1*05:01 (Flucloxacillin)
- **Association**: Flucloxacillin-induced liver injury
- **Mechanism**: T cell activation
- **Testing**: Limited availability, case-by-case basis
- **Clinical Impact**: Variable penetrance

## Testing Strategies

### Targeted Gene Panels
**Pre-Medication Testing**:
- CYP2C9, CYP2C19, CYP2D6: For multiple cardiovascular, psychiatric drugs
- TPMT: Before thiopurine therapy
- DPYD: Before 5-FU/capecitabine
- HLA alleles: For specific drugs with known associations

**Comprehensive PGx Panels**:
- 30-50+ genes covering >500 drugs
- One-time testing for potential lifetime value
- Cost-benefit analysis ongoing

### Testing Methods
- **Targeted SNP Genotyping**: High-throughput SNP arrays
- **Targeted Sequencing**: NGS with gene-specific coverage
- **Multiplex PCR**: Cost-effective for single genes
- **Copy Number Analysis**: For CYP2D6, CYP2A6 variants

## Clinical Implementation

### Phenotype Assignment

**Algorithm**:
1. Identify all alleles present
2. Sum activity scores for each allele
3. Calculate composite activity score
4. Map to phenotype category
5. Apply gene-specific rules (e.g., CYP2D6 duplications)

**Phenotype Categories**:
- **Poor Metabolizer (PM)**: Minimal/no enzyme activity
- **Intermediate Metabolizer (IM)**: Reduced activity
- **Normal Metabolizer (NM)**: Expected enzyme activity
- **Rapid Metabolizer (RM)**: Increased activity
- **Ultra-Rapid Metabolizer (URM)**: Significantly elevated activity

### Reporting

**Essential Components**:
1. **Gene Name**: Standardized HGNC symbol
2. **Alleles**: Specific variant nomenclature
3. **Phenotype**: PM/IM/NM/RM/URM
4. **Drugs Affected**: Clinically relevant medications
5. **Recommendations**: Dose adjustments, alternatives
6. **Evidence Level**: CPIC/FDA guidance tier
7. **Limitations**: Gene-gene interactions, environmental factors

### CPIC Guideline Levels

**Level A (Actionable)**:
- Strong evidence for clinical PGx association
- Recommended testing before medication
- Dose adjustment or alternative medication required
- Examples: CYP2C19-clopidogrel, TPMT-thiopurines

**Level B (Supporting)**:
- Moderate evidence for clinical association
- Recommended testing consideration
- Potential dose adjustment or monitoring needed
- Examples: CYP2D6-codeine, CYP2C9-warfarin

**Level C (Clinical Consultation)**:
- Emerging evidence for PGx association
- Testing consideration based on clinical context
- Examples: CYP3A4-many drugs, variable effect

## Drug-Gene Interactions Table

| Drug | Gene | Phenotype | Recommendation |
|------|------|-----------|-----------------|
| Clopidogrel | CYP2C19 | PM/IM | Alternative P2Y12 inhibitor |
| Codeine | CYP2D6 | PM | Ineffective; avoid |
| Escitalopram | CYP2C19 | PM | Dose reduction, QT monitoring |
| Tamoxifen | CYP2D6 | PM | Reduced breast cancer benefit |
| Warfarin | CYP2C9 | IM/PM | Lower maintenance dose |
| 6-Mercaptopurine | TPMT | PM | 85-90% dose reduction |
| 5-Fluorouracil | DPYD | Deficient | Avoid or alter regimen |
| Abacavir | HLA-B*5701 | Positive | Avoid absolutely |
| Simvastatin | SLCO1B1 | Non-expresser | Alternative statin |

## Gene-Gene Interactions

### CYP2D6 + CYP2C19 + CYP1A2
- **Interaction**: Multiple substrate drugs metabolized by multiple pathways
- **Example**: Some antidepressants (CYP2D6, CYP2C19)
- **Recommendation**: Cumulative consideration of multiple genes

### TPMT + NUDT15
- **Interaction**: Synergistic effect on 6-MP metabolism
- **Impact**: Additional risk stratification
- **Testing**: Both genes recommended for thiopurine therapy

## Emerging Areas

### RNA-Level Pharmacogenomics
- **Expression Variants**: eQTL affecting mRNA levels
- **Post-transcriptional**: miRNA interactions
- **Tissue-Specific**: Differential expression in liver, kidney

### Microbiome Pharmacogenomics
- **Microbial Metabolism**: Prodrug activation by gut bacteria
- **Beta-Glucuronidase**: Varies with microbiome composition
- **Examples**: Digoxin, estrogens, antibiotics

### Epigenetic Factors
- **DNA Methylation**: CpG methylation in gene promoters
- **Histone Modifications**: Affecting gene expression
- **Environmental**: Inducer exposure history
