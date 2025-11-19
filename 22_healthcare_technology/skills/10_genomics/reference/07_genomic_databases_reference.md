# Genomic Databases & Resources Reference

## Population Frequency Databases

### gnomAD (Genome Aggregation Database)
**Overview**: Largest population frequency database.

**Coverage**:
- **Exome Sequences**: >140,000 individuals
- **Genome Sequences**: >80,000 individuals
- **Total Variants**: ~1 billion SNPs + indels tracked
- **Population Subgroups**:
  - AFR (African/African American): ~20k
  - AMR (Latino/Admixed American): ~17k
  - ASJ (Ashkenazi Jewish): ~12k
  - EAS (East Asian): ~10k
  - FIN (Finnish): ~14k
  - NFE (Non-Finnish European): ~70k
  - OTH (Other): ~12k
  - SAS (South Asian): ~15k

**Allele Frequency Categories**:
- **Common**: AF ≥ 1% (usually benign)
- **Low Frequency**: 0.01% ≤ AF < 1%
- **Rare**: AF < 0.01% (more likely pathogenic)
- **Singleton**: Observed only once (de novo potential)

**Key Features**:
- Ancestry-specific allele frequencies
- Filter non-PASS variants separately
- Constraint metrics (pLI, LOEUF)
- Copy number variation data
- Structural variation catalog

**Access**: gnomad.broadinstitute.org

### ClinVar
**Purpose**: Clinical significance assertions by laboratories.

**Coverage**:
- >200,000 variants with clinical assertions
- RCV (record submitter) and SCV (single-submitter) differentiation
- Assertion levels: 4-star (highest) to 1-star (lowest)
- Conflicting interpretations flagged

**Classification Tracking**:
- Pathogenic
- Likely pathogenic
- Uncertain significance (VUS)
- Likely benign
- Benign

**Key Metrics**:
- **Assertion Level**: Reviews by multiple labs = higher confidence
- **Assertion Criteria**: Evidence supporting classification
- **Review Status**: Practice guideline, expert panel, multiple submitters, single submitter
- **Conflicting Interpretations**: Noted for VUS variants

**Phenotypes**:
- OMIM identifiers linked to conditions
- MedGen disease concepts
- Comprehensive disease associations

**Frequency Update**: Weekly updates, searchable website & downloadable database

### 1000 Genomes Project
**Overview**: Completed phase 3 (2015) with 2,504 individuals.

**Data**:
- **Populations**: 26 populations across 5 continents
- **Variants**: ~88 million SNPs identified
- **Inheritance Patterns**: Family trios included for phase-aware calling
- **Read Depth**: ~4-5x whole genome coverage (lower than gnomAD)

**Usage**:
- Population allele frequency background
- Historical reference (now largely superseded by gnomAD)
- Specific population frequencies when available
- Linkage disequilibrium calculations

### dbSNP
**Purpose**: Central SNP database (NCBI).

**Features**:
- **rs IDs**: Unique identifiers for known variants
- **Allele Information**: Alleles, frequencies (when available)
- **Genome Assembly Locations**: Current GRCh38 coordinates
- **Reference Sequences**: RefSeq/Ensembl IDs
- **Validation Status**: By 1000G, HapMap, or literature

**Current Status**:
- Primarily historical reference now
- gnomAD largely supersedes for frequency data
- Still used for rs ID lookups
- Integration with clinical databases

## Variant Consequence Databases

### ClinVar
(Already covered above, includes consequence predictions)

### COSMIC (Catalogue of Somatic Mutations in Cancer)
**Purpose**: Cancer-specific somatic variants.

**Coverage**:
- ~750,000+ somatic mutations
- 37+ cancer types tracked
- Tumor samples and cell lines
- Histology-specific annotations

**Key Features**:
- **Cancer Type**: Specific tissue of origin
- **Histology**: Detailed cancer classification
- **Variant Type**: SNV, fusion, CNV, etc.
- **Sample Source**: Primary tumor, cell line, xenograft
- **Associated Therapies**: Treatment response when documented
- **Functional Impact**: Consequence predictions
- **Sample Count**: Frequency across cancer samples

**Search Approaches**:
- By gene: All mutations in KRAS, TP53, etc.
- By position: Specific genomic location
- By mutation description: HGVS nomenclature
- By cancer type: Tissue-specific profiling

**Integration**: Cross-referenced with OncoKB, CIViC for therapy

### CIViC (Clinical Interpretation of Variants in Cancer)
**Purpose**: Clinical evidence for cancer variant interpretation.

**Curated Evidence**:
- **Predictive**: Therapy response/resistance
- **Diagnostic**: Cancer type/subtype identification
- **Prognostic**: Clinical outcome prediction
- **Predisposing**: Heritable susceptibility

**Evidence Tiers**:
- **Tier 1**: FDA-approved biomarker
- **Tier 2**: Published clinical trial evidence
- **Tier 3**: Functional evidence, case reports
- **Tier 4**: Pre-clinical evidence

**Assertion Levels**:
- **A (Strong)**: Multiple peer-reviewed publications or FDA approval
- **B (Moderate)**: Published data in peer-reviewed journals
- **C (Emerging)**: Limited evidence, preliminary studies
- **D (Preliminary)**: Pre-clinical or case-level evidence

**Access**: civicdb.org

### OncoKB (Memorial Sloan Kettering)
**Purpose**: FDA-approved, clinically actionable cancer mutations.

**Annotation Tiers**:
| Tier | Definition | Treatment |
|------|-----------|-----------|
| 1 | FDA-approved in this disease | Standard care |
| 2 | Approved in another disease | Off-label use |
| 3 | Clinical trial available | Investigational |
| 4 | Biological evidence | Research only |
| R1 | Resistance (vs. approved therapy) | Therapeutic change |
| R2 | Resistance (emerging evidence) | Developing strategies |

**Levels of Evidence**:
- **FDA Level**: FDA-approved biomarker
- **NCCN Level**: NCCN guidelines
- **Clinical Trial Level**: Active trials
- **Case Reports**: Individual case evidence
- **Pre-clinical**: Functional studies

**Integration**: Updates quarterly with new approvals/data

## Gene & Phenotype Databases

### OMIM (Online Mendelian Inheritance in Man)
**Purpose**: Comprehensive gene-disease and inheritance pattern database.

**Content**:
- **Gene Entries**: ~15,000 genes with disease associations
- **Phenotypes**: ~25,000 described phenotypes
- **Inheritance Patterns**: Clear documentation
- **Mutation Database**: Specific pathogenic mutations listed
- **Clinical Features**: Detailed phenotype descriptions
- **Molecular Basis**: Pathophysiologic mechanism

**Unique Identifiers**:
- **Genes**: Prefixed with # (e.g., #113705 for BRCA1)
- **Phenotypes**: Prefixed with * (e.g., *114480 for breast cancer)

**Inheritance Codes**:
- AD: Autosomal dominant
- AR: Autosomal recessive
- XL: X-linked
- MT: Mitochondrial
- Multiple patterns sometimes

**Access**: omim.org, free with registration

### Gene Cards
**Purpose**: Comprehensive gene information aggregation.

**Features**:
- **Gene Essentiality**: Knockout mouse data
- **Gene Function**: Natural language descriptions
- **Protein Function**: InterPro domains, structure
- **Gene Ontology**: Biological processes, molecular functions
- **Expression Patterns**: RNA-seq tissue distribution
- **Disease Associations**: Pubmed-derived connections
- **Variants**: Known pathogenic mutations
- **Pathways**: Involved signaling/metabolic pathways
- **Homologs**: Orthologous proteins across species

**Integration**: Links to OMIM, HGNC, Uniprot, many databases

**Access**: genecards.org

### DECIPHER (Database of Chromosomal Imbalance and Phenotype)
**Purpose**: Structural variants and developmental disorders.

**Content**:
- **Structural Variants**: CNVs, balanced translocations
- **Phenotype Data**: Detailed clinical descriptions
- **Patient Cohorts**: ~16,000 individuals with variants
- **Genotype-Phenotype Matching**: Similar variant analysis
- **Array CGH**: Copy number variation data

**Clinical Uses**:
- Finding patients with similar CNVs
- Phenotype-genotype correlation
- Disease gene discovery
- Determining pathogenicity of variants

**Access**: decipher.sanger.ac.uk

### HGNC (Human Gene Nomenclature Committee)
**Purpose**: Official human gene naming authority.

**Responsibilities**:
- **Gene Symbol Standardization**: Official HGNC symbols
- **Gene Names**: Unambiguous full names
- **Symbol Changes**: Tracking renames over time
- **Aliases**: Alternative names/symbols
- **Locus Type**: Protein-coding, non-coding RNA, pseudo, etc.
- **Chromosomal Location**: Gene position
- **Ensembl/Refseq IDs**: Database cross-references

**Importance**:
- All publications should use official HGNC symbols
- Ensures consistency in literature
- Enables database interoperability
- Required for clinical reporting

**Access**: genenames.org

## Expression & Regulation Databases

### GTEx (Genotype-Tissue Expression)
**Purpose**: Gene expression variation across tissues.

**Dataset**:
- **Samples**: ~17,000 tissue samples from ~1,000 individuals
- **Tissues**: 54 human tissue types (native + cell lines)
- **Genes**: Expression profiles for 56,000+ genes
- **eQTLs**: Expression quantitative trait loci associations

**Applications**:
- Understanding tissue-specific expression
- eQTL mapping for regulatory variants
- Identifying tissue-relevant genes
- Predicting regulatory variant effects
- Tissue-specific disease understanding

**Access**: gtexportal.org

### ENCODE (Encyclopedia of DNA Elements)
**Purpose**: Genome-wide regulatory element mapping.

**Data Types**:
- **Histone Modifications**: ChIP-seq for H3K4me3, H3K27ac, etc.
- **Transcription Factors**: TF binding sites
- **DNase Hypersensitivity**: Open chromatin regions
- **RNA-seq**: mRNA expression
- **Small RNA**: miRNA, siRNA data
- **Chromatin State**: ChromHMM state assignments

**Regulatory Elements**:
- **Promoters**: Active, poised, inactive
- **Enhancers**: Active, poised, weak
- **Silencers**: Repressive elements
- **Insulators**: CTCF-binding boundaries

**Access**: encodeproject.org

## Pathogenic Variant Databases

### PharmGKB (Pharmacogenomics Knowledge Base)
**Purpose**: Genetic variants affecting drug response.

**Content**:
- **Genes**: Pharmacogenes with clinical importance
- **Variants**: SNPs, indels affecting drug metabolism
- **Drugs**: Therapeutic recommendations per genotype
- **Phenotypes**: Metabolizer status per genotype
- **Clinical Guidelines**: CPIC, FDA, PNGC recommendations
- **Level of Evidence**: Strength of association

**Key Features**:
- **CPIC Guidelines**: FDA-endorsed recommendations
- **Gene-Drug Relationships**: Specific interactions
- **Phenotype Assignments**: PM/IM/NM/RM/URM
- **Dose Recommendations**: Guidance for prescribing
- **Patient-Friendly Materials**: Explanation documents

**Access**: pharmgkb.org

### ClinGen (Clinical Genome Resource)
**Purpose**: Standardized gene-disease assertions.

**Activities**:
- **Gene-Disease Validity**: Established vs. limited evidence
- **Dosage Sensitivity**: Haploinsufficiency/triplosensitivity
- **Curation Standards**: Evidence-based frameworks
- **Conflict Resolution**: Harmonizing contradictory submissions

**Assessment Levels**:
- **Definitive**: Sufficient evidence of association
- **Strong**: Well-established evidence
- **Moderate**: Some evidence
- **Limited**: Minimal evidence
- **No evidence**: Insufficient or contradictory

**Clinical Implementation**:
- Guides variant interpretation frameworks
- Informs ACMG secondary findings lists
- Supports laboratory reporting standards

**Access**: clinicalgenome.org

## Pathway & Function Databases

### Reactome
**Purpose**: Biological pathway database.

**Content**:
- **Pathways**: >2,300 human signaling/metabolic pathways
- **Proteins**: ~13,000 human proteins
- **Reactions**: Biochemical reactions with enzymes
- **Cross-references**: Integration with other databases
- **Evidence Levels**: Literature-backed curations

**Uses**:
- Understanding protein function in context
- Identifying related genes in pathways
- Predicting gene interaction networks
- Finding variants in pathway components

### KEGG (Kyoto Encyclopedia of Genes & Genomes)
**Purpose**: Gene, protein, and pathway database.

**Coverage**:
- **Organisms**: ~5,000 organisms including human
- **Pathways**: ~500 human pathways
- **Genes**: Functional classifications and orthologs
- **Compounds**: Small molecule compounds and reactions
- **Diseases**: Disease-pathway associations

**Pathway Categories**:
- Metabolism
- Human Diseases
- Drug Development
- Signal Transduction

**Access**: kegg.jp

## Variant Evaluation Resources

### American College of Medical Genetics (ACMG)
**Key Documents**:
- 2015 Standards for Variant Classification
- 2017 Incidental Findings Guidelines
- Secondary Findings Gene List (SF v3.0 = 73 genes)
- Application notes for specific gene groups

**Resources**:
- Official variant interpretation criteria
- ACMG-AMP joint recommendations
- Reporting standards and guidelines
- Educational webinars and publications

### ClinGen's Gene Validity Curations
**Database**: Gene-specific evidence assessments.

**Information Provided**:
- Genes with definitive disease associations
- Genes with limited/no evidence
- Dosage sensitivity classifications
- Supporting evidence documentation

### InterVar
**Purpose**: Automated ACMG variant interpretation tool.

**Features**:
- Automated PVS1/PS1-4, PM1-6, PP1-5, BP1-7, BS1-4, BA1 scoring
- Rule-based classification
- Requires variant annotation input (VEP, SnpEff)
- Evidence-based ACMG 2015 classification
- Available as web tool and command-line

## Database Selection Guide

**For Frequency Assessment**:
→ gnomAD (primary), then 1000G, dbSNP

**For Clinical Significance**:
→ ClinVar (first), then OMIM, Gene Cards

**For Cancer Mutations**:
→ OncoKB (FDA-approved), CIViC (evidence-based), COSMIC (frequency)

**For Pharmacogenomics**:
→ PharmGKB (definitive), then CPIC guidelines

**For Tissue Expression**:
→ GTEx (eQTL), ENCODE (regulatory), Gene Cards (aggregated)

**For Pathway Context**:
→ Reactome (detailed pathways), KEGG (broader coverage)

**For Gene Validity**:
→ ClinGen, OMIM (established associations), DECIPHER (new associations)

**Integration Strategy**:
1. Search ClinVar first for clinical significance
2. Check gnomAD for frequency
3. Validate with OMIM/Gene Cards for gene-disease relationship
4. Assess functional impact with prediction tools
5. Use disease-specific databases (cancer, PGx, etc.) as applicable
