# Precision Medicine & Treatment Selection Reference

## Precision Medicine Framework

### Definition & Goals
**Precision Medicine**: Tailoring medical treatment to individual patient characteristics (genetic, environmental, lifestyle).

**Goals**:
1. **Right Drug**: Select effective therapy based on genetics
2. **Right Dose**: Personalize dosing based on pharmacogenomics
3. **Right Patient**: Identify treatment-responsive populations
4. **Right Time**: Administer therapy when patient is ready
5. **Right Monitoring**: Track response and adjust as needed

### Actionability Hierarchy

**Tier 1A (Highest Evidence)**:
- FDA-approved companion diagnostic
- FDA-approved targeted therapy
- Standard care treatment
- Example: HER2 amplification → Trastuzumab in breast cancer

**Tier 1B**:
- NCCN guideline recommendation
- Strong clinical evidence
- Standard or preferred therapy
- Example: EGFR mutation → EGFR inhibitor in lung cancer

**Tier 2 (Emerging)**:
- Clinical trial ongoing
- Emerging evidence in literature
- Potential therapeutic option
- Example: KRAS G12C → Sotorasib, early adoption

**Tier 3 (Research)**:
- Pre-clinical evidence
- Functional significance known
- Investigational agents
- Example: Novel fusion genes, functional targets

## Somatic Tumor Profiling Strategy

### Comprehensive Genomic Profiling (CGP)

**Standard Panel Components**:

**1. Driver Mutation Analysis**
- **Oncogenes**: KRAS, EGFR, ALK, ROS1, BRAF, NTRK, MET, HER2, etc.
- **Tumor Suppressors**: TP53, PTEN, RB1, BRCA1/2, etc.
- **Detection**: Hotspot SNVs, indels, fusions, amplifications
- **Clinical Use**: Identify targeted therapy opportunities

**2. Biomarker Assessment**

| Biomarker | Method | Significance | Therapy |
|-----------|--------|--------------|---------|
| PD-L1 Expression | IHC | Immunotherapy selection | Pembrolizumab, nivolumab |
| TMB (Tumor Mutational Burden) | WES/WGS | Immunotherapy response | Checkpoint inhibitors |
| MSI-H/dMMR | IHC or PCR | Immunotherapy eligible | Pembrolizumab, nivolumab |
| HRD (Homologous Recombination Deficiency) | Genomic scarring | PARP inhibitor response | Olaparib, rucaparib |
| BRCA1/2 Mutations | Targeted sequencing | Platinum sensitivity, PARP benefit | Carboplatin, olaparib |

**3. Resistance Mutation Detection**
- **Acquired Mutations**: Secondary alterations from prior therapy
- **Surveillance**: Monitoring for treatment failure
- **Adaptation**: Modifying therapy based on resistance pattern

### Therapeutic Decision Tree

```
Patient with Advanced Cancer
    ↓
Step 1: Obtain comprehensive genomic profile
    ↓
Step 2: Identify Tier 1 actionable mutations
    ├→ FDA-approved + available → Offer targeted therapy
    └→ Multiple options → Discuss alternatives
    ↓
Step 3: Check Tier 1B (NCCN) recommendations
    └→ Evidence-based therapy options
    ↓
Step 4: Assess immunotherapy biomarkers
    ├→ PD-L1 high + TMB high → Immunotherapy
    ├→ MSI-H/dMMR → Pembrolizumab
    └→ TMB high (but PD-L1 low) → Immunotherapy + chemotherapy
    ↓
Step 5: Clinical trial eligibility
    └→ Mutation-matched trials
    ↓
Step 6: Prognosis & monitoring
    └→ Establish baseline, track mutations
```

## Gene-Specific Treatment Implications

### EGFR-Mutant Lung Cancer
**Mutations**:
- **L858R**: Exon 21 point mutation
- **Exon 19 Deletions**: In-frame deletions (most common activating)
- **Exon 20 Insertions**: De novo, TKI-resistant
- **T790M**: Acquired resistance during TKI therapy

**Treatment**:
| Mutation | First-Line | Mechanism | Response |
|----------|-----------|-----------|----------|
| L858R or Ex19del | Gefitinib/Erlotinib | 1st-gen EGFR TKI | 60-70% RR |
| L858R or Ex19del | Afatinib | 2nd-gen EGFR TKI | 60-70% RR |
| L858R or Ex19del | Osimertinib | 3rd-gen EGFR TKI | 80%+ RR |
| Ex20ins | Mobocertinib | Specific for Ex20ins | Emerging |
| T790M acquired | Osimertinib | 3rd-gen (resistant mut) | 60-70% RR |

**Monitoring**:
- Baseline profiling: EGFR, ALK, ROS1, KRAS, TP53
- Serial ctDNA: Track acquired resistance mutations
- Progression: Re-biopsy if possible, new mutations

### ALK-Rearranged Lung Cancer
**Fusions**:
- **EML4-ALK**: Most common (85% of ALK+ cases)
- **KIF5B-ALK, TFG-ALK**: Other partners (~15%)
- **Breakpoint Variants**: E1-E20 in EML4, associate with therapy response

**Treatment Evolution**:
| Drug | Class | ALK Mutations Sensitive | Resistance |
|------|-------|------------------------|-----------|
| Crizotinib | 1st-gen | G1269A resistant | Frequent |
| Alectinib | 2nd-gen | IM superior | G1269A resistant |
| Ceritinib | 2nd-gen | High-dose ALK+ | Complex resistance |
| Brigatinib | 2nd-gen | Better CNS penetration | Uncommon |
| Ensartinib | 2nd-gen | Approved | Uncommon |
| Alectinib | 3rd-gen | Pan-inhibitor candidate | Rare |

**Resistance Mechanisms**:
1. **Kinase Domain Mutations**: L1196M, G1269A
2. **G1128A**: Pan-resistance mutation
3. **Secondary Mutations**: Combinations of multiple mutations
4. **Bypass Pathway Activation**: EGFR, KIT, MET upregulation

### KRAS G12C Mutations
**Significance**:
- ~3% of lung adenocarcinoma (common in non-smokers)
- ~1-3% of other solid tumors
- Historically "undruggable"
- 2021 FDA approval changed paradigm

**Targeted Therapies**:
| Drug | Mechanism | Response | Resistance |
|------|-----------|----------|-----------|
| Sotorasib (Lumakras) | G12C-specific covalent inhibitor | 37% RR | G12D, G12V secondary |
| Adagrasib (Krazysana) | Pocket binder | 43% RR | G12D, G12V secondary |
| BI-1701963 | Preclinical | TBD | Under development |

**Combination Strategies**:
- KRAS G12C inhibitor + EGFR inhibitor
- KRAS G12C inhibitor + immunotherapy
- KRAS G12C inhibitor + chemotherapy

### BRAF V600E Mutations
**Cancer Types**:
- **Melanoma**: 40-50% of cutaneous melanoma
- **Colorectal Cancer**: 8-12% of mCRC
- **Thyroid Cancer**: 25-40% of papillary thyroid cancer
- **Hairy Cell Leukemia**: ~100%

**Treatment**:
| Cancer | Standard Therapy | Response | Monitor |
|--------|-----------------|----------|---------|
| Melanoma | Vemurafenib + Trametinib | 70-80% RR | Acquired mutations |
| mCRC | Encorafenib + Cetuximab ± Irinotecan | 50-60% RR | EGFR, MEK resistance |
| Thyroid | Vemurafenib + MEK inhibitor | Emerging | Clinical trials |

**Resistance Mutations**:
- **MEK pathway**: MEK mutations, BRAF secondary mutations
- **EGFR pathway**: EGFR activation, amplification
- **MAPK bypass**: NRAS, KRAS, NF1 loss

## Immunotherapy Biomarker Integration

### PD-L1 Expression Assessment

**Testing Methods**:
- **IHC (Immunohistochemistry)**: Staining intensity and distribution
- **Quantification**: Percentage of positive cells (tumor or immune cells)
- **Assay Platforms**: Different antibodies show variable concordance

**FDA-Approved Assays**:
- **22C3 (Dako)**: PD-L1 on tumor cells
- **28-8 (Dako)**: PD-L1 on tumor + immune cells
- **SP263 (Ventana)**: PD-L1 on tumor + immune cells
- **SP142 (Ventana)**: PD-L1 on immune cells

**Cutoff Values**:
| Cancer Type | Cutoff | Therapy | Approval |
|-----------|--------|---------|----------|
| NSCLC | ≥50% | Pembrolizumab monotherapy | FDA |
| NSCLC | ≥1% | Nivolumab + chemotherapy | FDA |
| Melanoma | ≥1% | Nivolumab + ipilimumab | FDA |
| Merkel Cell | ≥50% | Avelumab | FDA |

**Caveats**:
- Assay/antibody dependent
- Tumor heterogeneity
- Sample timing (fresh vs. archived)
- Can change with treatment

### Tumor Mutational Burden (TMB)

**Calculation**:
```
TMB = Total nonsynonymous mutations / Target sequenced (Mb)
```

**Interpretation**:
- **High TMB** (≥10 mut/Mb): Better checkpoint inhibitor response
- **Low TMB** (<10 mut/Mb): Limited benefit from immunotherapy
- **Panel-specific**: Normalize to 1 Mb equivalent

**Clinical Applications**:
- **NSCLC**: High TMB + PD-L1 ≥1% → Pembrolizumab
- **SCLC**: TMB-high → Nivolumab + ipilimumab
- **Emerging**: TMB-only indicator across cancer types

**Sources of TMB**:
- **Smoking**: High TMB in smokers (mutagen exposure)
- **MSI**: Very high TMB with dMMR
- **Mutation Burden**: Increases with age, tumor size
- **Sequencing Artifacts**: May inflate TMB

### MSI-H/dMMR Assessment

**Detection Methods**:
- **IHC**: MLH1, MSH2, MSH6, PMS2 protein expression
- **PCR**: Microsatellite marker-based detection
- **NGS**: In-house bioinformatics detection
- **NGS Accuracy**: Depends on panel coverage

**Significance**:
- **MSI-H/dMMR**: Eligible for checkpoint inhibitors
- **Predictive**: Excellent response to immunotherapy
- **Prognostic**: Better prognosis in certain cancers
- **Hereditary**: Lynch syndrome screening needed if germine

**FDA-Approved Indications**:
- **Pembrolizumab**: MSI-H/dMMR metastatic solid tumors
- **Nivolumab + Ipilimumab**: MSI-H/dMMR colorectal cancer

## Liquid Biopsy Integration

### Circulating Tumor DNA (ctDNA)

**Clinical Applications**:
1. **Monitoring**: Serial ctDNA levels track disease burden
2. **Resistance Detection**: Acquired mutations in ctDNA
3. **Treatment Response**: ctDNA decrease correlates with response
4. **Minimal Residual Disease (MRD)**: Post-treatment surveillance
5. **Early Detection**: Emerging for asymptomatic cancer screening

**Liquid Biopsy Platforms**:
- **ddPCR**: Hotspot mutation detection (sensitive, specific)
- **cfDNA Sequencing**: Unbiased variant detection
- **Digital Sequencing**: Enhanced sensitivity for rare variants
- **Whole Genome**: Maximum mutation discovery

**Advantages**:
- Non-invasive (blood draw)
- Faster turnaround than tissue biopsy
- Real-time monitoring possible
- Capture clonal heterogeneity

**Limitations**:
- ctDNA fraction varies
- Affects sensitivity threshold
- Not all mutations detected
- Interpretation challenges

### Serial Genomic Profiling

**Workflow**:
1. **Baseline**: Comprehensive tumor profiling at diagnosis
2. **On-Treatment**: Monitor ctDNA every 4-8 weeks
3. **Progression**: Re-biopsy/profiling to detect resistance mutations
4. **Next Line**: Adjust therapy based on new mutations
5. **Surveillance**: Post-treatment MRD monitoring

**Key Metrics**:
- **ctDNA Clearance**: Rapid decrease with effective therapy
- **ctDNA Persistence**: Predicts early relapse
- **Mutation Evolution**: Track dominant clone changes
- **VAF Dynamics**: Allele frequency changes indicate selection

## Treatment Resistance Prediction

### Mechanisms of Resistance

**Primary Resistance** (No initial response):
- Mutation status misread
- Missing second hit in recessive pathway
- Baseline copy number loss in drug target
- Lineage transformation

**Acquired Resistance** (Response then progression):
1. **Target Gene Mutations**: Secondary kinase domain mutations
2. **Pathway Bypass**: Alternative pathway activation
3. **Amplification**: Gene amplification of target or bypass gene
4. **Loss of Tumor Suppressor**: Loss of co-dependent gene
5. **Epithelial-Mesenchymal Transition (EMT)**: Phenotypic change

### Predictive Models

**Genomic Features**:
- **TP53 Status**: Mutant TP53 associated with poor immunotherapy response
- **PTEN Loss**: Associated with resistance to multiple therapies
- **High Mutation Burden**: Generally favorable (except some exceptions)
- **Copy Number Burden**: Increased CNV associated with worse prognosis

**Gene Expression Signatures**:
- **Inflammatory Signature**: Higher CD8+, better immunotherapy response
- **Angiogenic Signature**: High angiogenesis, poor immunotherapy response
- **Proliferative Signature**: Higher proliferation, better chemotherapy response

## Real-World Implementation

### Genomic Report Integration

**Key Report Sections**:
1. **Executive Summary**: Main findings and recommendations
2. **Pathogenic Variants**: Driver mutations identified
3. **Biomarkers**: TMB, MSI, HRD status, others
4. **Actionable Findings**:
   - Tier 1A: FDA-approved + therapy available
   - Tier 1B: NCCN guideline recommendation
   - Tier 2: Clinical trial or emerging evidence
   - Tier 3: Research only
5. **Clinical Interpretation**: Integrative narrative
6. **Limitations**: Coverage gaps, low VAF calls excluded
7. **Recommendations**: Clinical action items, follow-up

### Multidisciplinary Tumor Board (MTB)

**Review Process**:
1. **Case Presentation**: Patient demographics, cancer histology, imaging
2. **Genomic Review**: Pathologist/molecular pathologist presents findings
3. **Literature Discussion**: Recent publications on mutations identified
4. **Trial Identification**: Mutation-matched clinical trials
5. **Recommendation Consensus**: Oncologist leads discussion
6. **Documentation**: Treatment plan recorded

**Outcomes**:
- ~15-30% of MTB recommendations are genomically guided
- Improved accrual to clinical trials
- Delayed median progression by months
- Enhanced patient satisfaction

## Pharmacogenomics in Cancer Treatment

### Drug-PGx Gene Interactions

| Drug | Gene | Phenotype | Action |
|------|------|-----------|--------|
| Irinotecan | TPMT, NUDT15 | PM/IM | Dose reduction |
| 5-Fluorouracil | DPYD | PM/heterozygous | Avoid or reduce |
| Tamoxifen | CYP2D6 | IM/PM | Questionable benefit |
| Warfarin | CYP2C9, VKORC1 | IM/PM | Dose reduction |
| Capecitabine | DPYD | Deficient | Avoid |

### Pre-Treatment Screening
- **Standard of Care**: DPYD for 5-FU/capecitabine
- **Emerging**: TPMT before 6-MP (pediatric ALL)
- **Optional**: CYP3A5 for tacrolimus/everolimus dosing
- **Supportive**: Other genes on comprehensive PGx panels

## Evolving Precision Medicine Areas

### Polygenic Risk Scores (PRS)
- **Concept**: Aggregate effect of multiple risk variants
- **Applications**: Cancer risk stratification, treatment response
- **Limitations**: Currently not standard clinical use
- **Future**: Potential for refined patient selection

### Immune Checkpoint Mutations
- **Assessment**: Mutations in PD-1, PD-L1, CTLA-4 pathways
- **Clinical Use**: Emerging understanding of intrinsic resistance
- **Research**: Active development of predictive models

### Tumor-Specific Mutational Signatures
- **COSMIC Signatures**: 30-60 established patterns
- **Clinical Application**: HRD detection, therapy prediction
- **Emerging**: Refine precision medicine decisions
