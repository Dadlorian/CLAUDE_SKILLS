# Variant Interpretation & Classification Reference

## Variant Types and Analysis

### Single Nucleotide Variants (SNVs)
**Definition**: Single base substitution at genomic position.

**Categorization**:
- **Synonymous (Silent)**: No change in amino acid (wobble position). Generally benign unless affects splicing.
- **Missense**: Amino acid change. Requires functional impact assessment.
- **Nonsense**: Premature stop codon. Usually pathogenic in LoF genes.
- **UTR Variants**: 5' and 3' untranslated regions. May affect translation efficiency, stability.

**Analysis Approach**:
- Predict functional consequence
- Assess constraint in region
- Check population frequency
- Review published reports
- Evaluate segregation patterns

### Insertions and Deletions (Indels)
**Definition**: Addition or removal of nucleotide segments.

**Categories**:
- **In-Frame Indels**: Multiple of 3 nucleotides, preserves reading frame
- **Frameshift Indels**: Not multiple of 3, disrupts reading frame (usually pathogenic)
- **Structural Impact**: Location in functional domains vs. linker regions

**Special Considerations**:
- Large indels affecting multiple exons (multi-exon deletions)
- Tandem duplications vs. simple insertions
- Repeat expansion disorders (trinucleotide repeats)
- Complex rearrangements requiring long-read sequencing

### Splice Site Variants
**Definition**: Variants affecting RNA splicing machinery.

**Categories**:
- **Canonical Splice Sites**: ±1,2 positions of intron-exon boundaries (GT-AG rule)
- **Branch Points**: Adenine upstream of polypyrimidine tract (~20bp before 3' splice site)
- **Deep Intronic**: Mutations creating cryptic splice sites within introns
- **Exonic Splicing Enhancers**: Facilitate normal splicing
- **Exonic Splicing Silencers**: Inhibit splicing

**Impact Assessment**:
- Use MaxEntScan, SpliceAI, GenSplice tools
- Consider exon skipping vs. intron retention
- Evaluate NMD (nonsense-mediated decay) triggering
- Assess isoform-specific effects

### Structural Variants (SVs)
**Definition**: Large genomic rearrangements (>50bp typically).

**Types**:
- **Deletions**: Loss of genomic segment, copy number loss
- **Duplications**: Gain of genomic segment, copy number gain
- **Inversions**: Reversal of sequence orientation
- **Translocations**: Segment movement between chromosomes
- **Complex Rearrangements**: Multiple coordinate changes

**Detection Methods**:
- Array CGH for copy number changes
- Long-read sequencing for breakpoints
- Optical mapping for large events
- Read-pair analysis from short-read data
- qPCR for targeted confirmation

### Copy Number Variations (CNVs)
**Definition**: Segments with variable number of copies (typically 2 copies normal).

**Analysis Metrics**:
- **Copy Number State**: Loss (0,1), normal (2), gain (3,4+)
- **Size Ranges**: Small (<100kb) to large (>5Mb) segments
- **Gene Coverage**: Partial vs. complete gene deletion/duplication
- **Dosage Balance**: Assessment of clinical significance

**Dosage Sensitivity Categories**:
- **LoF Intolerant** (pLI >0.9): Deletions likely pathogenic, duplications uncertain
- **Balanced Genes**: Deletions and duplications both potentially pathogenic
- **LoF Tolerant**: Rare deletions pathogenic, duplications usually benign

## Evidence Integration Framework

### Population Frequency Evidence

**Database Sources**:
- **gnomAD**: Largest population database (>140k exomes, >80k genomes)
- **1000 Genomes**: Phase 3, population subgroups
- **ExAC**: Earlier version, now part of gnomAD
- **NHLBI GO ESP**: Cardiac exome project
- **TopMed**: Trans-Omics for Precision Medicine

**Allele Frequency Thresholds**:
- **BA1/BS1**: ≥5% or ≥1% depending on inheritance pattern
- **PM2**: Absent or extremely rare (<0.005% for dominant, <1% for recessive)
- **Ancestry-Specific**: Consider African, Asian, European, etc.
- **Technical Artifacts**: Pseudogenes, segmental duplications can inflate frequency

### Computational Predictions

**Missense Impact Tools**:
| Tool | Method | Interpretation |
|------|--------|-----------------|
| SIFT | Sequence homology | Deleterious vs. Tolerated |
| PolyPhen-2 | Structure/sequence | Probably damaging, Possibly damaging, Benign |
| Mutation Taster | ML integration | Disease-causing, Polymorphism |
| CADD | Conservation + ML | PHRED score (>20 deleterious) |
| MetaLR | Ensemble prediction | Deleterious/Tolerated |
| AlphaMissense | Deep learning structure | Pathogenic/Benign score |

**RNA Impact Tools**:
- **SpliceAI**: Deep learning splice site prediction (-1 to 1 score)
- **MaxEntScan**: Position weight matrix scoring
- **Human Splicing Finder**: Multiple algorithms combined
- **NetGene2**: Neural network splice prediction

**Protein Function Tools**:
- **InterPro**: Protein domain and function annotation
- **Pfam**: Protein family database
- **PROVEAN**: Evolutionary conservation assessment
- **MutPred**: Structural/functional predictions

### Functional Evidence

**In Vitro Assays**:
- **Luciferase Assays**: Promoter/enhancer activity measurement
- **Cell-Based Assays**: Protein localization, stability, function
- **Splicing Assays**: RT-PCR, RNA-seq for isoform identification
- **Enzymatic Assays**: Protein activity quantification
- **Binding Assays**: Protein-protein interaction disruption

**In Vivo Evidence**:
- **Animal Models**: Knock-in mice, CRISPR modifications, zebrafish
- **Functional Rescue**: Restoration of wild-type phenotype
- **Transgenic Studies**: Overexpression effects
- **Disease Correlation**: Phenotype-genotype associations

**Literature Mining**:
- Recent functional studies (past 5-10 years)
- Multiple independent studies confirming findings
- Publication quality and statistical significance
- Conflict resolution between studies

### Segregation Analysis

**De Novo Mutations**:
- Confirmed parental origin testing (both parents unaffected)
- Stronger evidence than PM6 (unconfirmed de novo)
- Applicable to dominant inheritance patterns
- Rules out inherited carrier state

**Co-Segregation Studies**:
- Variant present in all affected family members
- Variant absent in unaffected relatives
- Multiple generations strengthens evidence
- Large families provide stronger statistical support
- LOD score calculation (>3.0 supports linkage)

**Complex Segregation Analysis**:
- Calculate penetrance in families
- Assess variable expressivity
- Account for reduced penetrance
- Determine inheritance pattern

## Nomenclature Standards

### HGVS Nomenclature
**Format**: Gene.Transcript[DNA position][nucleotide change]

**Examples**:
- `BRCA1.NM_007294.4:c.68_69delAG` (deletion of AG at positions 68-69)
- `TTN.NM_001267550.1:c.100113C>A` (C to A substitution at position 100113)
- `DMD.NM_000109.3:c.600+2T>G` (intron splice site variant)
- `KRAS.NM_033360.4:c.35G>A:p.(Gly12Asp)` (with protein notation)

**Components**:
- **Gene**: Official HGNC gene symbol
- **Transcript**: Preferred NCBI RefSeq (NM_) or Ensembl (ENST_)
- **c.**: DNA coordinate (cDNA nomenclature)
- **p.**: Protein notation (single letter amino acid code)
- **+/-**: Splice site coordinate (positive = 3' of exon, negative = 5' of intron)

### SPDI Format
**Structure**: Sequence:Position:Deleted:Inserted

**Examples**:
- `NC_000013.11:32889611:G:A` (BRCA2 c.68-69delAG equivalent)
- `NC_000001.11:12345:AAA:A` (3-bp deletion)
- Normalized for left-alignment and decomposition

### Protein Nomenclature
**Standards**:
- Single letter code (M, V, L, I, F, W, P, A, G, C, S, T, D, N, E, Q, K, R, H, Y)
- Position number refers to mature protein (not including signal peptide unless specified)
- `p.(Gly12Asp)` = glycine at position 12 changed to aspartate (predicted)
- `p.Gly12Asp` = confirmed protein-level change

## Disease-Gene Relationship Classification

### Genotype-Phenotype Patterns

**Pattern 1: Autosomal Dominant (AD)**
- One mutated allele sufficient for phenotype
- Affected individuals heterozygous
- 50% transmission risk to offspring
- De novo mutations common
- Examples: BRCA1, TP53, FGFR3

**Pattern 2: Autosomal Recessive (AR)**
- Two mutated alleles required (compound heterozygous or homozygous)
- Parents usually unaffected carriers
- 25% recurrence risk (if both parents carriers)
- More common in consanguineous families
- Examples: CFTR, TTN, GBA

**Pattern 3: X-Linked Recessive (XLR)**
- Males affected with one mutation
- Females carriers (heterozygous) usually unaffected
- Affected males from carrier mothers
- Male-to-male transmission absent
- Examples: DMD, F8, F9

**Pattern 4: X-Linked Dominant (XLD)**
- Males hemizygous usually more severe/lethal
- Heterozygous females affected
- No male-to-male transmission
- Examples: CDKL5, ARX, PCDH19

**Pattern 5: Mitochondrial Inheritance**
- Maternal transmission exclusively
- Variable heteroplasmy levels
- Variable phenotype severity
- Disease threshold concept
- Examples: MT-TL1, MT-ND5

### Modifier Effects
- **Genetic Modifiers**: Other variants affecting disease severity
- **Environmental Modifiers**: Lifestyle, medication, exposure factors
- **Age-Dependent Penetrance**: Manifestation changes with age
- **Sex-Influenced Expression**: Differential manifestation by sex

## Quality Assessment Metrics

### Variant Quality Scores
**GATK Quality Metrics**:
- **QUAL**: Phred-scaled quality (>20 reliable, >30 high confidence)
- **DP**: Sequencing depth (10-30x minimum for solid calls)
- **GQ**: Genotype quality (>20 for confident genotyping)
- **AF**: Allele frequency (VAF for somatic variants)
- **AD**: Allele depth counts (reference, alternate alleles)

**Variant Filtering**:
- **PASS/FAIL**: VCF filter status
- **vcftools Hard Filters**: Custom threshold application
- **Bcftools Filtering**: Quality score combinations
- **VQSR (Variant Quality Score Recalibration)**: ML-based quality assignment

### Confidence Metrics
- **Sequencing Error Rate**: Typically 0.1-1% depending on platform
- **Strand Bias**: Variants stronger on one DNA strand
- **Homopolymer Tract Errors**: Indels in repetitive sequences
- **GC Content Bias**: Coverage variation with GC%

## Interpretation Decision Trees

### For Missense Variants
1. Check if location is mutation hot spot (PM1)
2. Assess computational predictions
3. Evaluate conservation (GERP, PhyloP scores)
4. Check similar amino acid substitutions
5. Review functional studies
6. Assess population frequency
7. Determine if Met-Thr-Val-Ala-Gly (hydrophobic core common)
8. Final classification based on aggregate evidence

### For Frameshift/Nonsense
1. Assess if in LoF-intolerant gene (high pLI)
2. Determine if triggers NMD
3. Check if C-terminal truncation (may retain function)
4. Evaluate gene isoforms affected
5. Check population frequency
6. Classification typically straightforward

### For Regulatory Variants
1. Identify regulatory element type (promoter, enhancer, silencer)
2. Assess functional annotation (ENCODE, Roadmap)
3. Evaluate conservation of element
4. Check splicing predictions
5. Look for functional studies
6. Often classified as VUS if unproven functional impact
