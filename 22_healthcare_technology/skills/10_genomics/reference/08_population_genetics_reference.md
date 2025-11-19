# Population Genetics & Statistics Reference

## Allele Frequency Concepts

### Minor Allele Frequency (MAF)
**Definition**: Frequency of less common allele in population.

**Calculation**:
```
MAF = min(allele1_frequency, allele2_frequency)
```

**Examples**:
- Allele frequencies: A=0.95, T=0.05 → MAF=0.05 (5%)
- Allele frequencies: G=0.51, C=0.49 → MAF=0.49 (49%)

**Significance**:
- **Common variant**: MAF >1% (typically benign)
- **Low frequency**: 0.01% ≤ MAF ≤ 1%
- **Rare variant**: MAF <0.01% (potentially pathogenic)
- **Very rare**: Observed in single individual/family

**Population Context**:
- MAF varies by ancestry
- gnomAD tracks ancestry-specific frequencies
- Must report population-specific MAF
- Same variant may be common in one, rare in another population

### Allele Frequency Filtering

**Conservative Thresholds** (suggest benignity):
- **Autosomal Dominant**: MAF >0.1% or >0.5% depending on penetrance
- **Autosomal Recessive (Homozygous)**: MAF >1%
- **Autosomal Recessive (Heterozygous Carriers)**: MAF 1-5%
- **X-Linked Recessive (Males)**: MAF >0.1%
- **X-Linked Recessive (Females)**: MAF >0.1%

**Notes**:
- Lower thresholds for Mendelian disorders (more pathogenic rare variants)
- Higher thresholds for complex disorders (common variants with small effect)
- Population expansion affects rarity assessment

## Hardy-Weinberg Equilibrium (HWE)

### Principle
Allele and genotype frequencies remain stable across generations without evolutionary forces.

### HWE Calculations

**Given allele frequencies**:
- Let p = frequency of allele A
- Let q = frequency of allele a
- p + q = 1

**Expected genotype frequencies**:
- AA: p²
- Aa: 2pq
- aa: q²
- p² + 2pq + q² = 1

**Example**:
```
If p(A) = 0.7, q(a) = 0.3
Expected: AA = 0.49, Aa = 0.42, aa = 0.09
```

### HWE Testing

**Chi-Square Goodness of Fit**:
```
χ² = Σ[(Observed - Expected)² / Expected]
```

**Interpretation**:
- **p > 0.05**: Population in HWE (no deviation)
- **p < 0.05**: Deviation from HWE (possible artifact or selection)

**Common Deviations**:
- **Excess Heterozygotes**: Population mixture, null alleles
- **Deficit Heterozygotes**: Population stratification, inbreeding
- **Allele Frequency Skew**: Selection pressure, founder effect

### Clinical Implications

**HWE Deviation Significance**:
- Large sample deviation: Check for quality control issues
- Small sample deviation: Expected random variation
- Consistent deviation: May suggest pathogenic filtering
- Population-specific assessment needed

## Linkage Analysis & Haplotype

### Linkage Disequilibrium (LD)
**Definition**: Non-random association of alleles at different loci.

**Measures**:
- **D**: Difference from expected frequency under independence
- **D'**: Standardized measure of D (-1 to +1 range)
- **r²**: Squared correlation coefficient
- **LOD**: Log-odds ratio for linkage

**LD Decay**:
- Decreases with physical distance between variants
- Affected by recombination rate
- Historical population bottlenecks increase LD
- Admixed populations show shorter LD blocks

**Block Structure**:
- **LD Blocks**: Regions with strong LD (common in genome)
- **Recombination Hotspots**: Between blocks (LD breaks)
- **Tag SNPs**: Representatives of LD blocks for efficient genotyping

### Haplotype Inference

**Phasing Methods**:
- **Family-based**: Use pedigree structure (definitive)
- **Statistical**: SHAPEIT, Beagle, Eagle (probabilistic)
- **Reference-based**: Phase against large reference panels (most accurate)
- **Long-read Sequencing**: Direct physical haplotyping

**Applications**:
- **Disease Mapping**: Track disease alleles through families
- **Association Studies**: Haplotype-based analysis
- **Compound Heterozygosity Assessment**: Are variants in trans or cis?
- **Imputation**: Infer ungenotyped variants

### Compound Heterozygosity

**Definition**: Different mutations on each chromosome (trans configuration).

**Assessment in VUS Interpretation**:
1. Confirm both variants present in heterozygous state
2. Verify from different parents if available
3. Phase variants (same chromosome vs. different)
4. If in trans: Supports recessive inheritance
5. If in cis: May represent single haplotype

**Importance**:
- Recessive disorders require both alleles affected
- Compound heterozygotes have same phenotype as homozygotes
- Critical for variant classification in AR conditions

## Population Structure & Ancestry

### Ancestry Inference
**Methods**:
- **Principal Component Analysis (PCA)**: Unsupervised clustering
- **Admixture/Frappe**: Ancestral population inference
- **Structure**: Bayesian clustering into K populations
- **Machine Learning**: RFMix, fastSTRUCTURE

**Applications**:
- Quality control (sample clustering)
- Ancestry-specific allele frequency assessment
- Admixture mapping in diverse populations
- Correcting for population stratification in GWAS

### Population-Specific Allele Frequencies

**Importance**:
- Same variant frequency varies 10-100x between populations
- gnomAD provides ancestry-specific frequencies (8+ groups)
- Must use matched population frequency
- Mismatched frequency causes misclassification

**Major Population Groups**:
| Abbreviation | Description | Size in gnomAD |
|--------------|-------------|-----------------|
| AFR | African/African American | ~20k |
| AMR | Latino/Admixed American | ~17k |
| ASJ | Ashkenazi Jewish | ~12k |
| EAS | East Asian | ~10k |
| FIN | Finnish | ~14k |
| NFE | Non-Finnish European | ~70k |
| OTH | Other | ~12k |
| SAS | South Asian | ~15k |

**Ancestry-Specific Filtering**:
1. Determine patient ancestry/ethnicity
2. Use population-specific allele frequency
3. If unknown/admixed: Use conservative threshold (across all populations)
4. Document which population frequency used

## Constraint Metrics

### pLI (Probability of Loss-of-Function Intolerance)
**Definition**: Probability gene is intolerant to loss-of-function.

**Range**: 0 to 1
- **pLI > 0.9**: Loss-of-function intolerant (LoFi) genes
- **0.1 < pLI < 0.9**: Intermediate
- **pLI < 0.1**: Loss-of-function tolerant genes

**Interpretation**:
- **LoFi Genes**: Deletions/frameshifts more pathogenic
- **LoF-Tolerant Genes**: LOF mutations likely benign
- **Clinical Application**: Guides interpretation of null variants

### LOEUF (Loss-of-Function Observed/Expected Upper Bound Fraction)
**Definition**: Newer metric, more robust than pLI.

**Range**: 0 to 1+
- **LOEUF < 0.35**: Extremely LoF-intolerant
- **0.35 ≤ LOEUF < 0.50**: Very LoF-intolerant
- **0.50 ≤ LOEUF < 1**: Moderately LoF-intolerant
- **LOEUF ≥ 1**: LoF-tolerant

**Advantages**:
- More stable across rare variants
- Better handles small sample sizes
- Continuous scale more informative than categorical pLI
- Recommended for modern interpretation

### Constraint-Based Variant Interpretation
**Application**:
1. Assess LOEUF for gene in question
2. For frameshift/stop-gain variants:
   - LOEUF < 0.5: Likely pathogenic
   - LOEUF > 0.5: Likely benign
3. For missense variants: Use with caution (less informative)
4. Consider in combination with other evidence

## Population Mixing & Admixture

### Admixture Mapping
**Principle**: Track disease alleles through admixed populations.

**Method**:
1. Genotype dense markers in admixed population
2. Assign local ancestry at each locus
3. Test for association between local ancestry and disease
4. Fine-map disease gene to region with excess ancestry

**Applications**:
- Gene discovery in understudied populations
- Identifying novel disease associations
- Refining risk loci in complex diseases

### Population Stratification Confounding

**Problem**: Allele frequency differences between populations → spurious associations.

**Example**:
- Allele A: 20% frequency in population 1, 5% in population 2
- Disease: More common in population 1
- Association detected: Not causal, just population difference

**Correction Methods**:
- **Ancestry Adjustment**: Include ancestry principal components in model
- **Stratified Analysis**: Analyze each ancestry separately
- **Genomic Control**: Inflation factor correction
- **Association Testing**: Methods accounting for stratification

## Penetrance & Expressivity

### Penetrance
**Definition**: Proportion of individuals with genotype who show phenotype.

**Types**:
- **Complete Penetrance** (100%): All mutation carriers affected
- **Reduced Penetrance** (<100%): Some mutation carriers unaffected
- **Age-Dependent**: Penetrance increases with age
- **Gender-Specific**: Different penetrance in males vs. females

**Examples**:
- BRCA1 hereditary breast cancer: ~72% penetrance by age 80
- Huntington disease: ~100% penetrance (fully penetrant)
- Retinoblastoma: ~90% penetrance (highly penetrant)

**Clinical Implications**:
- Affects genetic counseling (recurrence risk)
- Explains unaffected mutation carriers
- Impacts predictive testing recommendations

### Expressivity
**Definition**: Variability in severity/manifestation of phenotype.

**Variable Expressivity**:
- Same mutation produces different clinical severity
- Different tissues affected in different individuals
- Age of onset varies
- Comorbid features vary

**Example**: Marfan syndrome phenotype varies even within families with same FBN1 mutation.

**Genetic and Environmental Modifiers**:
- Background genetic variation (modifier genes)
- Environmental factors (lifestyle, exposure)
- Epigenetic effects
- X-inactivation (in X-linked conditions)

## Hardy-Weinberg Equilibrium in Disease Context

### Using HWE to Detect Pathogenic Variants

**Principle**: Pathogenic variants in dominant conditions may deviate from HWE.

**Scenario 1: Reduced Homozygotes**
- If variant causes early lethality in homozygotes
- Expected homozygotes: p²
- Observed homozygotes: 0
- HWE test: p < 0.05 (significant deviation)
- Interpretation: Possible pathogenic homozygous effect

**Scenario 2: Reduced Heterozygotes**
- If control population excludes affected individuals
- Expected heterozygotes: 2pq
- Observed heterozygotes: less than expected
- Cause: Dominant disease filtering out affected individuals
- Not failure of HWE per se

## Statistical Power & Sample Size

### GWAS Sample Size Considerations

**Factors Affecting Power**:
- **Effect Size**: Larger effect needs smaller sample
- **MAF**: Common variants easier to detect
- **Alpha**: Significance threshold (5×10⁻⁸ for GWAS)
- **Power**: Usually target 80%

**Example Calculation**:
```
For detecting association with:
- Effect size (OR) = 1.3
- MAF = 0.1
- Alpha = 5×10⁻⁸
- Power = 0.8
Required N ≈ 25,000-50,000 individuals
```

### Sequencing Sample Size for Rare Variants

**Burden Testing**:
- Aggregate rare variants in gene
- Requires large sample sizes (1000s+)
- Better power with functional annotation

**Single-Variant Testing**:
- High-impact variants (LoF)
- Lower sample size needed
- Critical for clinical diagnostics

## Mutation Spectrum Analysis

### Synonymous vs. Non-Synonymous Ratio

**dN/dS Ratio**:
```
dN/dS = (# non-synonymous changes) / (# synonymous changes)
        / (# possible non-synonymous) / (# possible synonymous)
```

**Interpretation**:
- **dN/dS < 1**: Purifying selection (LoF constraint)
- **dN/dS = 1**: Neutral evolution
- **dN/dS > 1**: Positive selection

**Gene-Specific Significance**:
- Essential genes: dN/dS << 1 (highly constrained)
- Oncogenes: dN/dS > 1 (positive selection hotspots)
- Tumor suppressors: dN/dS < 1 (negative selection)

### Mutation Hotspots
**Definition**: Positions with recurrent mutations.

**Identification**:
- High-density variant calling (cancer, large databases)
- Structural/functional analysis (functional domains)
- Population comparison (common in cases vs. controls)

**Examples**:
- KRAS G12: Hotspot in multiple cancer types
- TP53 DNA-binding domain: Frequently mutated
- BRCA1/2 hotspots: Common founder mutations

**Clinical Application**:
- Hotspot mutations → Higher pathogenic probability
- New mutations at hotspot → Suspicious for pathogenicity
- Used as ACMG PM1 criterion
