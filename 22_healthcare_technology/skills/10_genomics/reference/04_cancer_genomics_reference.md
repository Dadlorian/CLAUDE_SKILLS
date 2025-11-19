# Cancer Genomics Reference

## Cancer Genomic Principles

### Cancer Development Model
**Multi-Hit Hypothesis**: Multiple genetic alterations accumulate:
1. **Initiation**: First oncogenic mutation
2. **Promotion**: Additional driver mutations
3. **Progression**: Selective advantage accumulation
4. **Malignant Transformation**: Full cancer phenotype

**Clonal Evolution**:
- Early mutations present in all cancer cells
- Late mutations present in subclones only
- Intratumoral heterogeneity significant
- Impacts treatment response and resistance

## Somatic Variant Analysis

### Driver vs. Passenger Mutations
**Driver Mutations** (Pathogenic in somatic context):
- Confer selective advantage to cancer cells
- Recurrently mutated across patients
- Often in oncogenes or tumor suppressors
- Actionable for targeted therapy

**Passenger Mutations**:
- Do not confer growth advantage
- Variable across patients
- Accumulated through cell divisions
- Represent mutational background

**Identification Methods**:
- **Recurrence Analysis**: Frequency across cohort
- **Functional Impact**: Predicted effect on protein
- **Population Comparison**: Less frequent in normal tissue
- **Mechanistic**: Known to affect cancer biology

### Oncogenes
**Definition**: Genes that promote cell growth when mutated.

**Activation Mechanisms**:
- **Point Mutations**: Constitutive activation (KRAS, BRAF)
- **Gene Amplification**: Increased copy number (MYC, HER2, EGFR)
- **Chromosomal Translocation**: Fusion proteins (BCR-ABL, EML4-ALK)

**Common Oncogenes**:
| Gene | Cancer Type | Mechanism | Drug |
|------|-----------|-----------|------|
| KRAS | Lung, pancreatic, colorectal | Point mutation | Sotorasib (G12C), Adagrasib |
| BRAF | Melanoma, colorectal | V600E point mutation | Vemurafenib, Dabrafenib |
| HER2 | Breast, gastric | Amplification | Trastuzumab, Pertuzumab |
| EGFR | Lung, head-neck | Point mutation, amplification | Gefitinib, Erlotinib |
| ALK | Lung | EML4-ALK fusion | Crizotinib, Alectinib |
| NTRK | Multiple | NTRK1/2/3 fusion | Larotrectinib, Entrectinib |
| ROS1 | Lung | ROS1 fusion | Crizotinib, Entrectinib |
| MET | Gastric, lung | MET exon 14 skipping | Crizotinib |

### Tumor Suppressor Genes
**Definition**: Genes that inhibit cell growth; loss-of-function promotes cancer.

**Inactivation Mechanisms**:
- **Point Mutations**: Loss of function
- **Deletions**: Copy number loss
- **Frameshift**: Truncating mutations
- **Epigenetic Silencing**: Promoter methylation

**Key TSGs**:
| Gene | Cancer Type | Loss Consequence | Status |
|------|-----------|------------------|--------|
| TP53 | >50% all cancers | Impaired DNA damage response | Most critical |
| RB1 | Retinoblastoma, SCLC | Uncontrolled cell cycle | Pathway target |
| PTEN | Breast, prostate, glioma | Loss of growth inhibition | PI3K pathway |
| APC | Colorectal | Wnt pathway dysregulation | Inherited/somatic |
| BRCA1/BRCA2 | Breast, ovarian | Impaired DNA repair | Therapeutic target (PARP) |
| VHL | Renal | HIF-alpha dysregulation | Therapy target |
| NF1 | Neurofibromatosis | Ras signaling loss | Emerging targets |

## Specific Cancer Types

### Breast Cancer
**Key Driver Genes**:
- **HER2**: 20-25% amplification; trastuzumab benefit
- **ER/PR**: Hormone receptor status; endocrine therapy
- **PIK3CA**: ~15-25% mutations; PI3K/AKT pathway inhibitors
- **TP53**: ~50% mutated; genomic instability
- **PTEN**: Loss associated with PI3K activation

**Actionable Profile**:
1. HER2 status (IHC/FISH)
2. Hormone receptor status
3. Genomic instability (HRD, TMB)
4. BRCA1/2 mutation status
5. PD-L1 expression

**Treatment Implications**:
- HER2+ → Trastuzumab/pertuzumab
- ER+ → Endocrine therapy ± CDK4/6i
- Triple negative → Chemotherapy ± pembrolizumab (if PD-L1+)
- BRCA1/2 mut → PARP inhibitors, platinum sensitivity

### Lung Cancer (NSCLC)
**Oncogenic Drivers**:
- **EGFR**: L858R, exon 19 deletion; TKI response ~80%
- **ALK**: EML4-ALK fusion; ALK inhibitor response excellent
- **ROS1**: Fusion; crizotinib effective
- **KRAS**: G12C mutations; new sotorasib approval
- **BRAF**: V600E; vemurafenib/dabrafenib + trametinib

**First-Line Molecular Screening**:
- EGFR mutation status (PCR or NGS)
- ALK rearrangement (FISH or immunohistochemistry)
- ROS1 rearrangement (FISH or immunohistochemistry)
- PD-L1 expression (immunohistochemistry)
- Tumor mutational burden (TMB)

**Treatment Selection**:
- EGFR mut → EGFR TKI (gefitinib, erlotinib, afatinib)
- ALK+ → ALK inhibitor (crizotinib → alectinib/ceritinib)
- PD-L1 ≥50% → Immunotherapy (pembrolizumab monotherapy)
- High TMB + PD-L1 ≥1% → Immunotherapy ± chemotherapy
- Wild-type for above → Chemotherapy + pembrolizumab

### Colorectal Cancer
**Metastatic CRC (mCRC) Testing**:
- **KRAS/NRAS**: RAS wild-type → EGFR inhibitor (cetuximab, panitumumab)
- **BRAF V600E**: ~10% mCRC; poor prognosis; vemurafenib + cetuximab + irinotecan
- **MSI-H/dMMR**: ~15% mCRC; pembrolizumab or nivolumab + ipilimumab
- **ERBB2 (HER2)**: Amplification/mutation; trastuzumab + chemotherapy

**Actionable Results**:
- RAS WT + EGFR inhibitor-eligible
- BRAF V600E mutant-specific regimen
- MSI-H/dMMR: Immunotherapy regardless of stage
- HER2 amplified: HER2-directed therapy

### Melanoma
**Somatic Profile**:
- **BRAF V600E**: ~40-50% cutaneous melanoma
- **NRAS**: ~15-20%; alternative to BRAF
- **NF1**: ~15%; loss of growth inhibition
- **Immune Markers**: PD-L1, CD8+ infiltrate

**Treatment Stratification**:
- BRAF V600E → Vemurafenib/dabrafenib ± trametinib
- NRAS mutant → Selumetinib ± dacarbazine
- BRAF/NRAS/NF1 WT → Immunotherapy-first
- Stage III/IV → Adjuvant immunotherapy consideration

### Gastrointestinal Cancers

**Gastric Cancer**:
- **HER2 amplification**: 10-15%; trastuzumab-containing regimen
- **MSI-H/dMMR**: 10-15%; immunotherapy option
- **FGFR2 amplification**: ~5%; emerging target
- **PD-L1 expression**: Immunotherapy selection

**Esophageal Cancer**:
- **FGFR/FGF amplification**: FGFR inhibitor opportunity
- **HER2 amplification**: HER2-targeted therapy
- **MSI-H/dMMR**: Immunotherapy eligible

## Genomic Biomarkers

### Tumor Mutational Burden (TMB)
**Definition**: Number of nonsynonymous mutations per megabase (mut/Mb).

**Calculation**:
```
TMB = Total nonsynonymous variants / Sequenced length (Mb)
```

**Clinical Significance**:
- **High TMB** (≥10 mut/Mb): Increased immunotherapy response potential
- **Mismatch repair deficiency**: Results in high TMB
- **Smoking-related**: Lung cancers often high TMB
- **Checkpoint inhibitor response**: TMB-high associated with better response

**Assessment Methods**:
- Panel-based: Normalize to 1 Mb equivalent
- Whole exome: Full exome TMB assessment
- Whole genome: Most comprehensive but less accessible

### Microsatellite Instability (MSI)
**Definition**: Abnormal replication slippage in repetitive sequences.

**Causes**:
- **Lynch Syndrome**: Germline mismatch repair gene mutations
- **MLH1 Promoter Methylation**: Somatic epigenetic silencing
- **Rare**: Somatic MMR mutations

**Detection Methods**:
- **PCR**: Marker-based panel (5-10 microsatellite markers)
- **IHC**: MLH1, MSH2, MSH6, PMS2 protein expression
- **NGS**: In-house bioinformatics detection
- **Fragment Analysis**: Capillary electrophoresis-based

**Significance**:
- **MSI-H/dMMR**: Predicts immunotherapy response
- **Lynch Syndrome Diagnosis**: Germline testing indicated
- **Cancer Syndrome Screening**: Family counseling needs

### Homologous Recombination Deficiency (HRD)
**Definition**: Impaired DNA double-strand break repair.

**Causes**:
- **BRCA1/BRCA2 mutations**: Germline or somatic
- **Other BRCA-pathway genes**: RAD51, PALB2, etc.
- **Epigenetic silencing**: BRCA1 promoter methylation

**Clinical Significance**:
- **PARP Inhibitor Response**: HRD tumors sensitive to PARPi
- **Platinum Sensitivity**: Correlation with HRD status
- **Prognosis**: Generally favorable for HRD cancers

**Assessment**:
- **BRCA1/2 Genotyping**: Genetic testing
- **Genomic Scar Assays**: Loss of heterozygosity, large-scale transitions
- **Functional Assays**: RAD51 immunostaining, gene expression profiles

### Immune Microenvironment Markers
**PD-L1 Expression**:
- **Testing**: Immunohistochemistry with FDA-approved assays
- **Thresholds**: ≥50%, ≥1%, variable by cancer type and drug
- **Prognostic**: PD-L1+ tumors often better checkpoint inhibitor response

**TMB Integration**:
- **Combined Assessment**: PD-L1 and TMB together often ordered
- **Guidelines**: FDA approves pembrolizumab based on TMB in some cancers

**CD8+ Infiltration**:
- **Prognostic**: Higher CD8 infiltrate generally favorable
- **Research**: Active study in immunotherapy prediction

## Fusion Gene Detection

### Common Fusion Partners

**BCR-ABL (Chronic Myeloid Leukemia)**:
- Breakpoint variations: e1a2, e13a2, e14a2
- Classic Philadelphia chromosome t(9;22)
- Imatinib response depends on BCR-ABL type
- Resistance: Secondary mutations in kinase domain

**EML4-ALK (Lung Cancer)**:
- Multiple EML4 breakpoints (E1-E20)
- Crizotinib response variable by breakpoint
- G1269A acquisition: ALK inhibitor resistance
- Next-generation ALK inhibitors overcome resistance

**TMPRSS2-ERG (Prostate Cancer)**:
- Recurrent translocation t(21;21)
- Prognostic significance: Associated with worse outcomes
- Not yet therapeutic target
- Research: PARP inhibitor trials ongoing

**KMT2A Rearrangements (Hematologic)**:
- Multiple partner genes (>80 described)
- Infant ALL common with KMT2A-MLLT3
- Adult ALL/AML with various partners
- Poor prognosis, experimental therapies

## Mutation Signatures

### COSMIC Signatures
**Signature Database**: 30-60 established mutational signatures.

**Signature 1**: Clock-like, age-associated (all cancers).
**Signature 2/13**: APOBEC activity (breast, ovarian, CLL).
**Signature 3**: HRD-related (BRCA1/2 mutations).
**Signature 4**: Smoking-related (lung, head-neck).
**Signature 5**: Clock-like alternative, age-related.
**Signature 6**: Mismatch repair deficiency (Lynch syndrome).

**Clinical Applications**:
- **HRD Detection**: Signature 3 enrichment suggests HRD
- **MMR Status**: Signature 6 indicates MSI/MMR deficiency
- **Etiology Clues**: Smoking, alcohol, carcinogen exposure
- **Actionable Insights**: Links mutation process to treatment targets

## Cancer-Specific Gene Panels

### Solid Tumor Panels

**MSK-IMPACT (Memorial Sloan Kettering)**:
- 468 cancer genes
- Comprehensive somatic profiling
- FDA-listed clinical use
- Research collaborations available

**Tempus xT Panel**:
- 595 genes
- Includes germline/somatic distinction
- TMB, MSI, copy number assessment
- Treatment recommendation algorithm

**Foundation Medicine FoundationOne**:
- 324 genes
- Tumor mutational burden
- Biomarker detection across cancer types

### Liquid Biopsy Panels

**Digital PCR (ddPCR)**:
- Highly sensitive for specific known mutations
- Cost-effective for targeted hotspot screening
- Not discovery-based, requires hypothesis

**Cell-Free DNA (cfDNA)**:
- Circulating tumor DNA fragments
- Non-invasive "liquid biopsy"
- Useful for monitoring and MRD detection
- Emerging for early detection

### Germline Cancer Syndrome Panels

**BRCA1/BRCA2 + Extended Panel**:
- Expanded panels include 25-75 genes
- Hereditary cancer predisposition
- Critical for family counseling and surveillance

**Lynch Syndrome Panels**:
- MLH1, MSH2, MSH6, PMS2, EPCAM
- Hereditary colorectal cancer
- Surveillance and preventive strategies

## Treatment Resistance Mechanisms

### Acquired Resistance Mutations

**EGFR TKI Resistance** (Lung Cancer):
- **Secondary EGFR mutations**: T790M (50% of resistance)
- **MET amplification**: HGF pathway activation
- **EMT transition**: Loss of EGFR dependence
- **Small cell transformation**: Lineage switch

**ALK Inhibitor Resistance**:
- **ALK mutations**: L1196M (crizotinib), G1269A (multi-ALK inhibitors)
- **Kinase domain mutations**: Variable inhibitor sensitivity
- **Activation loop mutations**: Enhanced sensitivity predictable
- **G1128A**: Pan-ALK inhibitor resistant

**PARP Inhibitor Resistance**:
- **BRCA1/2 reversion mutations**: Restore DNA repair
- **Replication fork protection complex loss**: Drug efflux, increased stability
- **Lack of p53 loss**: Synthetic lethality altered

## Clinical Reporting

### Standard Elements
1. **Gene**: Official HGNC symbol
2. **Variant**: HGVS nomenclature, protein effect
3. **Allele Frequency**: VAF (variant allele frequency)
4. **Zygosity**: Hemizygous, heterozygous based on copy number
5. **Classification**: Somatic driver, passenger, pathogenic
6. **FDA Approval**: Companion diagnostic status
7. **Clinical Trial**: Eligibility with specific mutations
8. **Prognosis**: Prognostic implications if known
9. **Treatment**: FDA-approved or guideline-recommended therapies
10. **References**: Supporting citations and database entries

### Report Organization
1. **Executive Summary**: Key actionable findings
2. **Somatic Variants**: Pathogenic/actionable mutations
3. **Tumor Characteristics**: TMB, MSI, copy number profile
4. **Actionable Findings**: Tier 1/2/3 therapies
5. **Incidental Findings**: Germline recommendations if identified
6. **Methods**: Sequencing platform, coverage, analysis tools
7. **Limitations**: Sensitivity, specificity, coverage gaps
8. **References**: Therapy and guideline citations
