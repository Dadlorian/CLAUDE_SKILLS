# Research Data Management Skill

## Purpose
Implement FAIR data principles (Findable, Accessible, Interoperable, Reusable) for research data lifecycle management, compliance with NIH/NSF policies, and long-term preservation.

## Core Principles: FAIR

### Findable (F1-F4)
**F1**: Globally unique persistent identifier (DOI, Handle, ARK)
**F2**: Rich metadata (DataCite, Dublin Core, domain ontologies)
**F3**: Metadata references identifier
**F4**: Indexed in searchable resource (Google Dataset Search, DataCite, re3data)

### Accessible (A1-A2)
**A1**: Retrievable by identifier using standard protocol (HTTP, FTP, API)
**A1.1**: Protocol open, free, universal
**A1.2**: Metadata persist even if data removed
**A2**: Metadata accessible even if data restricted

### Interoperable (I1-I3)
**I1**: Formal, accessible, shared language (RDF, JSON-LD, OWL)
**I2**: FAIR vocabularies (Gene Ontology, MeSH, SNOMED)
**I3**: Qualified references (related datasets, publications)

### Reusable (R1-R1.3)
**R1**: Rich metadata with provenance
**R1.1**: Clear usage license (CC0, CC-BY recommended)
**R1.2**: Provenance (PROV-O ontology, workflow provenance)
**R1.3**: Domain-relevant standards (file formats, metadata schemas)

## Data Lifecycle

### 1. Planning (Before Data Collection)

**Data Management Plan (DMP)**:
- Data type and scale (genomic, clinical, survey; GB/TB)
- Metadata standards (DataCite, DDI, ISA)
- Access and sharing (public, embargoed, restricted)
- Preservation (repository, format, retention period)
- Budget (repository fees, curation effort)

**Tools**: DMPTool (US), DMPonline (UK), Argos (EU)

**Funder Requirements**:
- **NIH**: DMP required (2023 policy), data sharing within publication or 1 year
- **NSF**: DMP required (2 pages max), reviewed as part of proposal
- **Wellcome Trust**: Open access within 6 months
- **Horizon Europe**: DMP within 6 months, updates at milestones

### 2. Collection (During Research)

**Electronic Lab Notebooks (ELN)**:
- Digital record-keeping (LabArchives, Benchling, SciNote)
- Timestamp, version control, witnessing
- Multimedia (images, spectra, videos)
- Export for archiving

**Quality Control**:
- Range checks (values within expected range?)
- Consistency checks (sum of parts = total?)
- Duplicate detection
- Missing data codes (NA, -999, blank)

**Metadata Capture**:
- Contemporaneous (record at time of experiment)
- Who, what, when, where, why, how
- Instrument settings, reagent lots, environmental conditions

### 3. Processing (Data Cleaning & Analysis)

**Reproducible Workflows**:
- Version control: Git for code, DVC (Data Version Control) for data
- Literate programming: Jupyter notebooks, R Markdown, Quarto
- Workflow management: Snakemake, Nextflow, CWL (Common Workflow Language)
- Containerization: Docker, Singularity (capture entire environment)

**Data Cleaning**:
- Document all changes (log file)
- Keep raw data immutable (never overwrite original)
- Processed data in separate directory

**Example**:
```python
# Log data cleaning
with open('cleaning_log.txt', 'a') as log:
    log.write('2024-11-19: Removed row 45 - duplicate entry\n')
    log.write('2024-11-19: Corrected typo in row 78: age 250 → 25\n')
```

### 4. Analysis (Statistical/Computational)

**Code Documentation**:
- README: Overview, installation, usage
- Inline comments: Explain why, not what
- Docstrings: Function/class documentation
- CITATION.cff: How to cite your code

**Testing**:
- Unit tests (pytest, testthat)
- Integration tests (full pipeline)
- Regression tests (ensure updates don't break)

**Reproducibility Checklist**:
- [ ] Random seeds set
- [ ] Dependencies documented (requirements.txt, environment.yml)
- [ ] Code versioned (Git tags for releases)
- [ ] Data versioned (DVC, or DOI for static snapshots)
- [ ] Analysis pre-registered (OSF, AsPredicted)

### 5. Preservation (Long-Term Archiving)

**Repository Selection**:

**Disciplinary** (preferred):
- **Genomics**: GenBank, ENA, DDBJ
- **Proteomics**: PRIDE, MassIVE
- **Crystallography**: PDB, CSD
- **Social Sciences**: ICPSR, UK Data Service
- **Astronomy**: CDS, IRSA

**General**:
- **Zenodo**: Free, unlimited (EU-funded), DOI, integrated with GitHub
- **Dryad**: $120 for <20GB, curated, associated with publications
- **Figshare**: Free <5GB, good for figures/posters
- **OSF**: Free, unlimited, project management + data

**Institutional**: Check if your university has a data repository

**Format Conversion**:
- Open formats preferred (CSV, HDF5, TIFF, PDF/A, NetCDF)
- Convert proprietary: Excel → CSV, SPSS .sav → CSV + codebook
- Document conversions (what, why, how)

**Metadata**:
- DataCite schema (DOI metadata)
- Domain-specific (ISA for systems biology, DDI for social surveys)
- README.txt (human-readable overview)
- Data dictionary (variable definitions)

### 6. Sharing (Publication)

**Data Availability Statement**:
```
Data are available at Zenodo: DOI 10.5281/zenodo.#######.
Analysis code is available at GitHub: github.com/user/repo.
```

**License**:
- **CC0** (public domain): Maximum reuse, recommended for data
- **CC-BY-4.0**: Attribution required (acceptable)
- **CC-BY-NC**: Non-commercial (limits reuse, not recommended)

**Access Control**:
- **Open**: Public, no registration
- **Registered**: Free registration (track usage)
- **Controlled**: Data Use Agreement (DUA), committee review
- **Embargoed**: Temporary restriction (6-12 months typical)

## Metadata Standards

**Core Metadata (DataCite)**:
- Identifier (DOI)
- Creator (authors with ORCID)
- Title
- Publisher (repository)
- Publication Year
- Resource Type (Dataset)
- Subject/Keywords
- Related Identifier (paper, code)
- Description (abstract, methods)

**Domain-Specific**:
- **Biological**: ISA (Investigation-Study-Assay), MIAME (microarrays), MINSEQE (sequencing)
- **Social Sciences**: DDI (Data Documentation Initiative) for surveys
- **Geosciences**: ISO 19115, CF Conventions (NetCDF)
- **Materials**: CIF (Crystallographic Information File)

## Data Governance

**Sensitive Data**:
- **Human subjects**: De-identification (HIPAA Safe Harbor: remove 18 identifiers)
- **Anonymization**: Remove direct identifiers, aggregate small cells (<5)
- **Controlled access**: dbGaP (genomic), ICPSR (restricted use)

**Data Use Agreements (DUA)**:
- Terms of use (allowed purposes, restricted uses)
- Citation requirements
- No redistribution
- Destruction upon completion

**Compliance**:
- **GDPR** (EU): Right to be forgotten, data minimization, consent
- **HIPAA** (US): De-identification, Business Associate Agreements
- **Export control**: ITAR (defense), EAR (dual-use technology)

## File Organization

**Directory Structure**:
```
project_name/
├── data/
│   ├── raw/              # Original, immutable
│   ├── processed/        # Cleaned, analysis-ready
│   └── metadata/         # Data dictionaries, codebooks
├── code/
│   ├── scripts/          # Analysis scripts
│   └── notebooks/        # Jupyter/R Markdown
├── docs/
│   ├── protocols.md
│   ├── data_dictionary.md
│   └── changelog.md
├── results/
│   ├── figures/
│   └── tables/
├── README.md
├── LICENSE
└── CITATION.cff
```

**File Naming**:
- Descriptive (not "data1.csv")
- No spaces (use underscores/hyphens)
- Include date (YYYY-MM-DD)
- Version numbers (v01, v02)
- Example: `2024-11-19_survey_responses_pilot_v01.csv`

## Tools

**Data Management**:
- **DVC**: Data version control (Git for data)
- **Git**: Code version control
- **Datalad**: Decentralized data management

**Data Quality**:
- **Great Expectations** (Python): Data validation framework
- **Assertr** (R): Data pipeline testing
- **OpenRefine**: Data cleaning, transformation

**Metadata**:
- **DataCite**: DOI registration and metadata
- **Frictionless Data**: Data package specification
- **CEDAR**: Metadata authoring tool (templates)

**Repositories**:
- **Zenodo**: Integrated with GitHub, automatic archiving
- **Dryad**: Curated, peer-reviewed datasets
- **OSF**: Project management + data repository

**Workflow**:
- **Snakemake**, **Nextflow**: Workflow management
- **Jupyter**, **R Markdown**: Literate programming
- **Docker**, **Singularity**: Containerization

## Success Criteria
- [ ] DMP completed before data collection
- [ ] Data deposited in public repository within 1 year of publication
- [ ] DOI obtained for dataset
- [ ] Metadata includes: Title, authors (ORCID), description, keywords, license, related paper
- [ ] README and data dictionary included
- [ ] Analysis code shared (GitHub, Zenodo)
- [ ] Reproducible: Another researcher can reproduce analysis

## Common Pitfalls
- No DMP until end of project (too late)
- Data on personal hard drive only (lost if drive fails)
- Poor metadata (dataset incomprehensible to others)
- Proprietary formats (Excel with macros, vendor-specific)
- No license (legal ambiguity, limits reuse)
- Missing data dictionary (variable names unclear)

## Key References
- Wilkinson et al. (2016). "The FAIR Guiding Principles." *Scientific Data*, 3, 160018
- NIH Data Sharing Policy (2023)
- GO FAIR Initiative: go-fair.org
- FORCE11 Data Citation Principles
- DataCite Metadata Schema: schema.datacite.org
- Research Data Alliance: rd-alliance.org

## Advanced Topics in Data Management

### Reproducible Research: Complete Workflow

**Scenario**: Clinical genomics study analyzing biomarkers for cancer prognosis

**Step 1: Planning (DMP)**
```
Project: Genomic Biomarkers in Ovarian Cancer
Data types:
- RNA-seq data: ~10 GB per sample, 50 samples = 500 GB
- Clinical metadata: ~1 MB (patient age, stage, treatment, outcome)
- Processed results: ~50 GB (normalized counts, differential expression)

Preservation:
- Repository: GEO (Gene Expression Omnibus) + Zenodo
- Format: BAM files (aligned reads), CSV (metadata)
- Retention: Indefinite (raw sequencing data per NIH policy)
- Budget: $5k for Zenodo storage, $2k curation effort

Sharing:
- Timeline: Data + code released upon publication (or 1 year, whichever first)
- Access: Open (publicly available)
- License: CC0 (public domain)
```

**Step 2: Collection & Documentation**
```
Raw data structure:
project_ovarian_genomics/
├── data/
│   ├── raw/
│   │   ├── Sample_001_R1.fastq.gz
│   │   ├── Sample_001_R2.fastq.gz
│   │   └── ... (100 fastq files, 500 GB total)
│   └── metadata/
│       └── sample_metadata.csv  # Patient ID, age, stage, outcome
├── docs/
│   ├── README.md
│   ├── data_dictionary.md
│   ├── sequencing_methods.md
│   └── data_collection_protocol.md
└── code/
    └── analysis/
        ├── 01_qc.R
        ├── 02_alignment.sh
        └── 03_differential_expression.R
```

**Sample metadata CSV**:
```
sample_id,patient_id,age,stage,treatment,survival_months,status
Sample_001,PT001,55,IIIB,Chemotherapy,48,Alive
Sample_002,PT002,62,IV,Chemotherapy + Immunotherapy,12,Dead
Sample_003,PT003,58,IIIA,Surgery only,36,Alive
```

**Step 3: Processing & Analysis**
```r
# R workflow with documentation
# Title: Differential Expression Analysis
# Author: Dr. Jane Smith
# Date: 2024-11-19
# Description: Compare gene expression between responders vs non-responders

library(DESeq2)
library(tidyverse)

# Load data
counts <- read.csv('data/processed/expression_matrix.csv', row.names = 1)
metadata <- read.csv('data/metadata/sample_metadata.csv', row.names = 1)

# Create DESeq2 object
dds <- DESeqDataSetFromMatrix(countData = counts,
                               colData = metadata,
                               design = ~ treatment)

# Run analysis
dds <- DESeq(dds)
results <- results(dds, contrast = c('treatment', 'Immunotherapy', 'Chemotherapy'))

# Save results
write.csv(results, 'results/differential_expression.csv')
save(dds, file = 'results/dds_object.RData')

# Session info for reproducibility
sessionInfo()  # Captures R version + all packages used
```

**Step 4: Version Control with Git**
```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit: raw data, metadata, analysis code"

# Document major milestones
git tag -a v1.0 -m "First quality control complete"
git tag -a v2.0 -m "Differential expression analysis done"

# Push to GitHub
git remote add origin https://github.com/mylab/ovarian_genomics
git push -u origin main
```

**Step 5: Archiving & Publication**
```
Zenodo deposit:
- Upload: All code + processed data (500 MB) + metadata
- Metadata:
  * Title: "Genomic biomarkers for ovarian cancer prognosis: Raw and processed data"
  * Authors: Smith J, Johnson M, et al. (with ORCID)
  * Description: RNA-seq from 50 ovarian cancer patients...
  * License: CC0
  * Related: Link to GitHub repo, link to paper
- DOI: 10.5281/zenodo.12345678 (assigned automatically)

Data availability statement in paper:
"Sequence data and processed gene expression matrices are available at GEO (accession GSE123456) and Zenodo (doi: 10.5281/zenodo.12345678). Analysis code is available at GitHub (github.com/mylab/ovarian_genomics). Raw sequencing data is available upon request (contact: jane@institution.edu) due to patient privacy restrictions."
```

## Data Security & Compliance

### HIPAA De-identification (US Healthcare)

**Safe Harbor Method** (remove these 18 identifiers):
1. Names
2. Geographic locations (smaller than state)
3. Dates (except year; patient age OK)
4. Phone/fax numbers
5. Email addresses
6. Social Security numbers
7. Medical record numbers
8. Health plan beneficiary numbers
9. Account numbers
10. Certificate/license numbers
11. Vehicle IDs
12. Device identifiers
13. Web URLs
14. IP addresses
15. Biometric identifiers
16. Photographs
17. Any other unique identifier
18. Related information (employment records, etc.)

**Example - Before De-identification**:
```
Name: John Smith
DOB: January 15, 1960 (age 64)
Address: 123 Main St, Boston, MA 02101
Phone: (617) 555-1234
MRN: 012345678
Hospital: Massachusetts General Hospital
Diagnosis: Type 2 diabetes
```

**After De-identification**:
```
Participant ID: STUDY_001
Age: 64
Location: Northeast US (by region, not city)
Diagnosis: Type 2 diabetes
Note: Dates removed except year; all direct identifiers removed
```

### GDPR Compliance (EU)

**Key requirements**:
- Data minimization: Collect only necessary data
- Purpose limitation: Use data only for stated purpose
- Consent: Explicit, informed consent (not pre-checked boxes)
- Right to be forgotten: Allow data deletion request
- Data Protection Impact Assessment (DPIA)
- Data Privacy Officer (DPO) if processing sensitive data

**Implementation**:
- Consent form: "I consent to my data being used for cancer research and de-identified data being shared publicly"
- Data retention: "Data will be stored for X years, then securely deleted unless participant consents to longer retention"
- Withdrawal: "You can withdraw from the study at any time; your data will be deleted within 30 days"

## Data Quality Assessment

### Great Expectations Framework (Python)

**Purpose**: Automated data validation + documentation

```python
import pandas as pd
import great_expectations as ge

# Load data
df = pd.read_csv('data/raw/patient_data.csv')
ge_df = ge.from_pandas(df)

# Define expectations
ge_df.expect_column_to_exist('patient_id')
ge_df.expect_column_values_to_be_in_set('age', value_set=range(0, 120))
ge_df.expect_column_values_to_be_between('height_cm', min_value=100, max_value=230)
ge_df.expect_column_values_to_not_be_null('patient_id')
ge_df.expect_column_values_to_match_regex('email', regex=r'[\w\.-]+@[\w\.-]+\.\w+')

# Run validation
results = ge_df.validate()

# Generate report
ge_df.save_expectation_suite('expectations/patient_data.json')
results.save_as_json_file('validation_reports/patient_data_report.json')
```

**Output**: Validation report showing which checks passed/failed + recommendations for fixing

## Large-Scale Data Management

### Datalad: Distributed Data Management

**Problem**: 500 GB genomics dataset + 10 GB software + 1 GB analysis results
- Can't fit on laptop
- Need version control for data (like Git for code)
- Multiple sites collaborating

**Solution**: Datalad

```bash
# Initialize a Datalad dataset
datalad create my_genomics_project
cd my_genomics_project

# Add large data files (stored on external server, not in repo)
datalad save --path data/raw/sequences.tar.gz \
  -d "Raw sequencing data from site A"

# Track which files have been accessed/modified
datalad status

# Synchronize with colleague's copy (with conflict resolution)
datalad update --how=merge

# Publish results
datalad push --to backup_server
```

### High-Performance Computing (HPC) Data Management

**Challenge**: Analysis on 1,000-core supercomputer with 100 GB/s I/O

**Best practices**:
- Store small metadata files (experiments, parameters) on fast storage
- Store large raw data on high-capacity storage (slower access)
- Use parallel I/O: MPI-IO, HDF5 with collective I/O
- Temporary scratch space: Delete after job completes
- Archive important results: Daily backup to archive storage

## Metadata Standards Deep Dive

### ISA Framework (Investigation-Study-Assay)

**For systems biology / omics research**

**Structure**:
```
Investigation: "Ovarian Cancer Genomics"
├── Study 1: "RNA-seq analysis of primary tumors"
│   ├── Assay 1: "mRNA sequencing"
│   │   ├── Sample: Tumor_001
│   │   ├── Material: RNA (extracted from tissue)
│   │   ├── Technology: Illumina NovaSeq
│   │   └── Result: Expression counts
│   └── Assay 2: "Protein sequencing"
│       ├── Sample: Tumor_001
│       ├── Material: Protein (extracted from tissue)
│       ├── Technology: Tandem MS
│       └── Result: Protein ID + abundance
└── Study 2: "Patient clinical outcomes"
    ├── Sample: Patient metadata
    ├── Parameters: Age, stage, treatment
    └── Results: Survival, response
```

### DataCite Metadata (for DOI/Archiving)

**Minimum required fields**:
1. **Identifier** (DOI): 10.5281/zenodo.12345
2. **Creators** (with ORCID): Smith, J. (0000-0001-2345-6789)
3. **Title**: "Genomic biomarkers for ovarian cancer prognosis: RNA-seq data and metadata"
4. **Publisher**: Zenodo
5. **PublicationYear**: 2024
6. **ResourceType**: Dataset
7. **Description**: "RNA-seq data from 50 ovarian cancer patients used to identify biomarkers..."
8. **Subjects** (keywords): genomics, cancer, biomarkers, oncology
9. **License**: CC0 1.0 Universal
10. **Related Identifiers**:
    - Paper DOI: 10.1234/journal.2024.12345
    - Code repo: https://github.com/mylab/ovarian_genomics

## Common Data Management Mistakes

### Mistake 1: Proprietary Formats
**Problem**: Excel file with macros → Can't open in 10 years (Excel proprietary)
**Solution**: Export to CSV, document all formulas in README

### Mistake 2: Inconsistent Naming
**Problem**: `data1.csv`, `data_final.csv`, `data_final_FINAL.csv`, `data_actual_final.csv`
**Solution**: Versioned naming: `2024-11-19_patient_data_v02.csv`

### Mistake 3: No Data Dictionary
**Problem**: Column named `var_x_1` - what does it mean?
**Solution**: Create data dictionary:
```
Variable | Description | Units | Range | Missing Codes
var_x_1 | Patient age at enrollment | years | 18-100 | 999 for unknown
var_x_2 | BMI | kg/m^2 | 15-60 | -999 for not measured
```

### Mistake 4: Lost Context
**Problem**: Dataset with no methods → Impossible to interpret
**Solution**: README.md with:
- Who collected the data
- When + where
- How (protocol reference)
- Why (study objective)
- Any known limitations

---

**Version**: 2.0 (Expanded)
**Expertise Level**: Intermediate to Advanced
**Estimated Learning Time**: 60-120 hours
**Total Content**: 450+ lines of comprehensive material
