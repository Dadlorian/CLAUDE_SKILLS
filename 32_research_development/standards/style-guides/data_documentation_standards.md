# Data Documentation Standards
## FAIR-Compliant Research Data Management

### Philosophy
Based on:
- **FAIR Principles** (Findable, Accessible, Interoperable, Reusable)
- **NIH Data Sharing Policy** (2023)
- **NSF Data Management Plan** requirements
- **GO FAIR Initiative**
- **Research Data Alliance** (RDA) recommendations

---

## FAIR Principles Implementation

### Findable (F1-F4)

**F1. Globally Unique Persistent Identifiers**:
- **DOI** (Digital Object Identifier): Zenodo, Dryad, Figshare
- **Handle**: Dataverse
- **ARK** (Archival Resource Key): Long-term persistence
- Format: Include in all citations and metadata

**F2. Rich Metadata**:
- Descriptive: Title, authors, abstract, keywords
- Administrative: License, embargo, access rights
- Structural: File formats, relationships, versions
- Domain-specific: Ontologies, controlled vocabularies

**F3. Metadata Include Identifier**:
- Metadata must reference the data's persistent identifier
- Enables discovery even if data location changes

**F4. Indexed in Searchable Resource**:
- Deposit in disciplinary repositories (PubMed, GenBank) or general (Zenodo)
- Ensure repository is indexed by Google Dataset Search, DataCite, BASE

### Accessible (A1-A2)

**A1. Retrievable by Identifier Using Standard Protocol**:
- HTTP/HTTPS for web-accessible data
- FTP for large datasets (less common now)
- APIs with authentication (OAuth2, API keys)

**A1.1. Protocol Open, Free, Universal**:
- Avoid proprietary access systems
- Use standard web protocols
- Document API access

**A1.2. Metadata Persist Even If Data Removed**:
- "Tombstone" pages with reason for removal
- Permanent metadata record with identifier

**A2. Metadata Accessible Even If Data Restricted**:
- Metadata always public (title, abstract, keywords)
- Data may be access-controlled (human subjects, proprietary)
- Document access process (application, DUA)

### Interoperable (I1-I3)

**I1. Formal, Accessible, Shared Language**:
- Use standard vocabularies (Gene Ontology, MeSH, SNOMED)
- RDF, JSON-LD for linked data
- Avoid lab-specific jargon in metadata

**I2. FAIR Vocabularies**:
- Vocabularies themselves must be FAIR
- Cite ontology versions (e.g., GO version 2024-01-01)

**I3. Qualified References**:
- Link to related datasets, publications, code
- Use persistent identifiers (DOIs, ORCIDs)
- Machine-readable relationships (Dublin Core, DataCite)

### Reusable (R1-R1.3)

**R1. Plurality of Attributes**:
- Rich, accurate metadata
- Provenance: How was data collected? Processed? Analyzed?
- Context: Study design, instruments, conditions

**R1.1. Clear License**:
- **CC0** (public domain): Maximum reuse, recommended for data
- **CC-BY-4.0**: Attribution required
- **CC-BY-NC**: Non-commercial only (limits reuse)
- Avoid "All Rights Reserved" or no license

**R1.2. Provenance**:
- PROV-O ontology for provenance
- Document: who, what, when, where, why, how
- Workflow tools auto-capture provenance (Snakemake, CWL)

**R1.3. Domain Standards**:
- File formats: Domain-specific (e.g., FASTQ for sequencing, NetCDF for climate)
- Metadata schemas: DataCite, Dublin Core, DDI, ISO 19115

---

## Data Management Plan (DMP)

### Required Components (NIH/NSF)

**1. Data Type and Scale**:
- What data will be generated? (genomic, clinical, survey, imaging)
- Scale: File counts, total size (GB/TB)
- Format: CSV, HDF5, TIFF, proprietary

**2. Metadata and Standards**:
- Metadata schema to be used (DataCite, domain-specific)
- Ontologies and controlled vocabularies
- File naming conventions

**3. Access and Sharing**:
- When will data be shared? (Publication? End of grant? Embargo?)
- Where? (Repository, institutional archive, supplementary materials)
- Who can access? (Public, registered users, restricted)

**4. Reuse and Redistribution**:
- License (CC0, CC-BY recommended)
- Format for reuse (open formats, documentation)

**5. Archiving and Preservation**:
- Long-term repository (domain or institutional)
- Retention period (NIH: 10 years post-publication)
- Format migration plan (for obsolete formats)

**6. Roles and Responsibilities**:
- Who manages data during project? (PI, data manager, postdoc)
- Who ensures deposit? (PI, data steward)

**7. Budget**:
- Repository fees ($0-$500 per dataset typically)
- Curation effort (data cleaning, metadata creation)
- Long-term storage (if institutional)

### DMP Tools
- **DMPTool** (US): Templates for NIH, NSF, DOE
- **DMPonline** (UK): Templates for UKRI, Wellcome Trust
- **Argos** (EU): H2020, Horizon Europe templates

---

## Metadata Standards

### Core Metadata (DataCite Schema)

**Mandatory**:
- Identifier (DOI)
- Creator (authors with ORCID)
- Title
- Publisher (repository)
- Publication Year
- Resource Type (Dataset, Software, etc.)

**Recommended**:
- Subject/Keywords
- Contributor (data collectors, funders)
- Date (created, modified, embargo)
- Language
- Related Identifier (paper, code, prior version)
- Description (abstract, methods)
- Geo-location
- Funding Reference

### Domain-Specific Metadata

**Biological Sciences**:
- **ISA** (Investigation-Study-Assay): Systems biology, omics
- **MIAME** (Minimum Information About a Microarray Experiment)
- **MINSEQE** (Sequencing): Now part of ISA

**Social Sciences**:
- **DDI** (Data Documentation Initiative): Surveys, censuses
- **CESSDA** (European social science data)

**Geosciences**:
- **ISO 19115**: Geographic information metadata
- **CF Conventions**: Climate and Forecast NetCDF

**Materials Science**:
- **CIF** (Crystallographic Information File)

---

## File Organization

### Directory Structure

```
project_name/
├── data/
│   ├── raw/                  # Original, immutable data
│   │   ├── 2024-01-15_experiment_A.csv
│   │   └── README.md         # Describe raw data files
│   ├── processed/            # Cleaned, transformed data
│   │   ├── cleaned_data.csv
│   │   └── PROCESSING.md     # Document processing steps
│   └── metadata/
│       └── datacite.json     # Structured metadata
├── code/
│   ├── scripts/              # Analysis scripts
│   ├── notebooks/            # Jupyter/R Markdown
│   └── README.md             # Code documentation
├── docs/
│   ├── protocols.md          # Experimental protocols
│   ├── data_dictionary.md    # Variable definitions
│   └── changelog.md          # Version history
├── results/
│   ├── figures/
│   ├── tables/
│   └── stats/
├── README.md                 # Project overview
├── LICENSE                   # Data license (CC0, CC-BY)
└── CITATION.cff              # Citation metadata
```

### File Naming Conventions

**Principles**:
- Descriptive, not generic ("2024-01-15_cell_viability_A549.csv" not "data1.csv")
- No spaces (use underscores or hyphens)
- Include dates: YYYY-MM-DD format (ISO 8601)
- Version numbers: v01, v02 or semantic versioning (1.0.0)
- Avoid special characters (!@#$%^&*)

**Examples**:
- `2024-11-19_survey_responses_pilot_v01.csv`
- `exp03_sample012_microscopy_20x_488nm.tif`
- `patient_demographics_clean_2024-11-19.parquet`

### Version Control

**Data Version Control (DVC)**:
- Track large files without storing in Git
- `.dvc` files in Git, data in cloud storage (S3, GCS)
- Commands: `dvc add`, `dvc push`, `dvc pull`

**Semantic Versioning**:
- MAJOR.MINOR.PATCH (1.0.0)
- MAJOR: Incompatible changes (structure change)
- MINOR: Backward-compatible additions (new variables)
- PATCH: Bug fixes (correction of errors)

---

## Data Dictionaries

### Purpose
Define every variable in dataset for users who didn't collect the data.

### Components

**For each variable**:
- **Name**: Variable name in dataset (e.g., `age_years`)
- **Label**: Human-readable description ("Participant age in years")
- **Type**: Data type (integer, float, string, categorical, date)
- **Units**: If numeric (years, mg/L, μm)
- **Valid range**: Min-max (e.g., 18-65 for adult study)
- **Missing values**: Code for missing (NA, -999, blank)
- **Categorical levels**: If categorical, list all levels
  - Example: `treatment`: 1 = Control, 2 = Drug A, 3 = Drug B
- **Derivation**: If calculated, provide formula
  - Example: `bmi = weight_kg / (height_m^2)`

### Format

**CSV Example**:
```csv
variable,description,type,units,valid_range,missing_code,notes
subject_id,Unique participant ID,string,NA,NA,NA,Format: SUB-####
age_years,Age at enrollment,integer,years,18-65,NA,Self-reported
weight_kg,Body weight,float,kg,40-150,-999,Measured at baseline
treatment,Treatment group,categorical,NA,1-3,NA,1=Control|2=DrugA|3=DrugB
bmi,Body Mass Index,float,kg/m²,15-40,-999,weight_kg/(height_m^2)
```

**Markdown Example**:
```markdown
## subject_id
- **Description**: Unique participant identifier
- **Type**: String
- **Format**: SUB-#### (e.g., SUB-0001)
- **Missing**: None (required field)

## age_years
- **Description**: Participant age at enrollment
- **Type**: Integer
- **Units**: years
- **Range**: 18-65 (inclusion criteria)
- **Missing**: NA
```

---

## README Files

### Dataset README

**Template**:
```markdown
# Dataset Title

## Description
Brief overview of the dataset (2-3 sentences).

## Study Information
- **Principal Investigator**: Name (ORCID)
- **Institution**: University/Organization
- **Funding**: Grant number, funder
- **Date Range**: 2023-01-01 to 2024-06-30
- **IRB Approval**: Protocol #12345 (if human subjects)

## Data Collection
- **Study Design**: Cross-sectional, longitudinal, RCT, etc.
- **Participants**: n=150, inclusion/exclusion criteria
- **Procedures**: Brief methods
- **Instruments**: Equipment, software used

## File Descriptions
- `raw_data.csv`: Original survey responses (n=150 rows, 45 variables)
- `processed_data.csv`: Cleaned data, outliers removed (n=147 rows)
- `data_dictionary.csv`: Variable definitions
- `analysis_code.R`: Reproducible analysis script

## Variable Definitions
See `data_dictionary.csv` for complete definitions.

## Missing Data
- Code: -999 for numeric, NA for categorical
- Reasons: Participant refusal, equipment malfunction

## Usage Notes
- License: CC0 (public domain)
- Citation: Author et al. (2024). Dataset Title. Zenodo. DOI:10.5281/zenodo.#######
- Contact: email@university.edu

## Related Resources
- Publication: DOI:10.1000/journal.xxx
- Code Repository: github.com/user/project
- Protocol: protocols.io/view/protocol-xyz

## Version History
- v1.0.0 (2024-11-19): Initial release
```

---

## Data Formats

### Open Formats (Preferred)

**Tabular**:
- **CSV**: Universal, human-readable, no formulas
- **Parquet**: Columnar, compressed, efficient for large data (Python, R)
- **HDF5**: Hierarchical, multi-dimensional arrays, metadata support

**Text**:
- **TXT, MD**: Plain text, markdown
- **JSON, YAML**: Structured, human-readable
- **XML**: Hierarchical, verbose

**Images**:
- **TIFF**: Uncompressed, metadata support, scientific standard
- **PNG**: Lossless compression, web-friendly

**Scientific**:
- **NetCDF**: Climate, oceanography, geosciences
- **FITS**: Astronomy
- **NeXus (HDF5)**: Neutron/X-ray scattering

### Proprietary Formats (Convert to Open)

- Excel (.xlsx) → CSV
- SPSS (.sav) → CSV + codebook
- MATLAB (.mat) → HDF5 or NumPy .npz
- Proprietary images → TIFF

### Format Conversion Tools

- **Pandas** (Python): Read 20+ formats, write CSV/Parquet/HDF5
- **R**: readxl, haven, rio packages
- **OpenRefine**: Data cleaning and format conversion

---

## Access Control

### Open Data
- Public, no registration required
- License: CC0 or CC-BY
- Use cases: Non-sensitive, publicly funded, reproducibility

### Registered Access
- Free registration, email verification
- Tracking usage (analytics)
- Use cases: Some human subjects data, genomic data

### Controlled Access
- Data Use Agreement (DUA) required
- Committee review
- Auditing
- Use cases: Identifiable human subjects, commercial restrictions

### Embargoes
- Temporary restriction (6-12 months typical)
- Protect priority for publication
- Metadata public, data embargoed

---

## Repositories

### Disciplinary Repositories (Preferred)

**Biological Sciences**:
- **GenBank/NCBI**: Sequence data
- **PDB**: Protein structures
- **GEO**: Gene expression
- **ArrayExpress**: Functional genomics

**Social Sciences**:
- **ICPSR**: Social science data
- **UK Data Service**: UK social/economic data

**Geosciences**:
- **NOAA NCEI**: Climate data
- **PANGAEA**: Earth system sciences

### General Repositories

**Zenodo**:
- Free, unlimited storage (up to 50GB per dataset)
- Integrated with GitHub
- Automatic DOIs
- CERN-backed (stable)

**Dryad**:
- $120 fee for <20GB (waived for some journals)
- Curated (improves metadata)
- Associated with publications

**Figshare**:
- Free for <5GB (institutional accounts larger)
- Good for figures, posters, media
- DOIs for everything

**OSF** (Open Science Framework):
- Free, unlimited (within reason)
- Project management + data sharing
- Preregistration, version control

### Institutional Repositories
- Check if your university has a repository
- Often free for affiliated researchers
- Long-term preservation commitment

---

## Quality Assurance

### Data Validation

**Automated Checks**:
- **Great Expectations** (Python): Data validation framework
- **Assertr** (R): Data pipeline testing
- **Frictionless Data**: Data package validation

**Validation Rules**:
- Range checks (age between 0-120)
- Type checks (date fields are dates)
- Consistency (sum of parts = total)
- Uniqueness (IDs are unique)
- Completeness (required fields not missing)

### Cleaning Documentation

**Record all cleaning**:
- What was changed?
- Why was it changed? (outlier, error, correction)
- Who made the change?
- When?

**Example log**:
```
2024-11-19: Removed row 45 - duplicate entry (confirmed with lab notes)
2024-11-20: Corrected age in row 78 from 250 to 25 (typo)
2024-11-21: Imputed missing weight values using MICE algorithm (R mi package)
```

---

## CITATION.cff

### Purpose
Machine-readable citation metadata for GitHub, Zenodo, etc.

### Example
```yaml
cff-version: 1.2.0
message: "If you use this data, please cite it as below."
authors:
  - family-names: Smith
    given-names: Jane
    orcid: https://orcid.org/0000-0002-1234-5678
  - family-names: Doe
    given-names: John
    orcid: https://orcid.org/0000-0003-9876-5432
title: "Research Data for: Impact of Treatment X on Y"
version: 1.0.0
doi: 10.5281/zenodo.1234567
date-released: 2024-11-19
url: "https://github.com/user/repo"
license: CC0-1.0
keywords:
  - cancer
  - drug discovery
  - proteomics
```

---

## Compliance Checklist

### Before Data Collection
- [ ] Data Management Plan created
- [ ] IRB/IACUC approval (if applicable)
- [ ] Informed consent includes data sharing language
- [ ] File naming convention established
- [ ] Data dictionary template prepared

### During Data Collection
- [ ] Data entered in structured format (not Word docs)
- [ ] Metadata recorded contemporaneously
- [ ] Version control used
- [ ] Regular backups (3-2-1 rule: 3 copies, 2 media, 1 offsite)

### Before Publication
- [ ] Data cleaned and validated
- [ ] README and data dictionary complete
- [ ] Analysis code documented and tested
- [ ] Repository selected
- [ ] License chosen (CC0/CC-BY)
- [ ] DOI obtained

### At Publication
- [ ] Data deposited in repository
- [ ] DOI cited in paper (Data Availability Statement)
- [ ] Code deposited (GitHub, Zenodo)
- [ ] CITATION.cff created

### Post-Publication
- [ ] Metadata updated if errors found
- [ ] Respond to data requests/questions
- [ ] Monitor usage (citations, downloads)

---

## References

- Wilkinson et al. (2016). "The FAIR Guiding Principles." Scientific Data.
- NIH Data Sharing Policy (2023)
- GO FAIR Initiative: go-fair.org
- FORCE11 Data Citation Principles
- DataCite Metadata Schema
- Research Data Alliance: rd-alliance.org

---

**Version**: 1.0
**Last Updated**: 2025-11-19
