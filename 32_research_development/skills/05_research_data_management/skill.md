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

---

**Version**: 1.0
**Expertise Level**: Intermediate
**Estimated Learning Time**: 40-80 hours
