# Legacy Research System Modernization Guide
## Migrating from Legacy LIMS, Data Systems, and Instruments

### Common Legacy Systems
- **Lab systems**: LabWare 5.x, STARLIMS pre-cloud, custom Access databases
- **Instruments**: GPIB/RS-232 connected equipment, standalone PCs
- **Data formats**: Proprietary formats (.spc, .dx), Excel workbooks with macros
- **Analysis**: MATLAB R2010b, Origin 6.0, SigmaPlot 10

### Assessment Phase

**Inventory Legacy Systems**:
1. List all systems (LIMS, ELN, instruments, analysis software)
2. Document: Age, vendor support status, user count, data volume
3. Identify integration points (manual data transfer, file exports)
4. Assess business criticality (high/medium/low)

**Risk Assessment**:
- Data loss risk (no backups, degrading media)
- Compliance risk (21 CFR Part 11, ISO 17025)
- Performance issues (crashes, slow queries)
- Vendor discontinuation (no patches, security vulnerabilities)

### Migration Strategies

**1. Lift-and-Shift** (virtualization):
- Migrate legacy Windows XP/7 machines to VMs
- Preserve exact environment (for archived data access)
- Pros: Quick, low risk
- Cons: Doesn't solve underlying problems, technical debt persists

**2. Replatform** (minimal changes):
- Move to modern version of same system (LabWare 7.x → 8.x)
- Update OS (Windows 7 → Windows 10/11 or Linux)
- Pros: Familiar interface, vendor support
- Cons: May require revalidation (GxP environments)

**3. Refactor** (modernize):
- Replace legacy system with cloud-native alternative
- Data migration to new format (SQL database, Parquet files)
- Pros: Future-proof, scalability, modern features
- Cons: Expensive, training required, validation effort

**4. Retire** (archive and decommission):
- Export all data to long-term archive
- Document system for future reference
- Decommission hardware
- Pros: Cost savings, reduced attack surface
- Cons: Data may become inaccessible (format obsolescence)

### Data Migration

**Extract**:
- Export data from legacy system (SQL dump, CSV export, API)
- Include all tables/relationships (don't just export views)
- Capture metadata (column definitions, relationships)

**Transform**:
- Map legacy schema to target schema
- Convert data types (legacy date formats → ISO 8601)
- Clean data (remove duplicates, fix encoding issues)
- Validate constraints (referential integrity, ranges)

**Load**:
- Incremental loading (batch by date ranges)
- Verify record counts match source
- Test queries on migrated data

**Validation**:
- Compare summary statistics (source vs target)
- Spot-check high-value records
- UAT with end users

**Example: Access Database → PostgreSQL**:
```python
import pyodbc
import psycopg2
import pandas as pd

# Extract from Access
conn_access = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=legacy.accdb')
df = pd.read_sql('SELECT * FROM samples', conn_access)

# Transform
df['collection_date'] = pd.to_datetime(df['collection_date'])
df['sample_id'] = df['sample_id'].str.strip()

# Load to PostgreSQL
conn_pg = psycopg2.connect('dbname=lims user=postgres password=xxx')
df.to_sql('samples', conn_pg, if_exists='append', index=False)

# Validate
count_access = pd.read_sql('SELECT COUNT(*) FROM samples', conn_access).iloc[0,0]
count_pg = pd.read_sql('SELECT COUNT(*) FROM samples', conn_pg).iloc[0,0]
assert count_access == count_pg, 'Record count mismatch!'
```

### Instrument Integration

**Legacy Instruments** (GPIB, RS-232):
- Use USB-to-GPIB adapters (NI GPIB-USB-HS)
- Python PyVISA library for instrument control
- Log data to modern LIMS via API

**Example: GPIB Instrument Data Capture**:
```python
import pyvisa

rm = pyvisa.ResourceManager()
instrument = rm.open_resource('GPIB0::10::INSTR')

# Query instrument
data = instrument.query('READ?')

# Parse and upload to cloud LIMS
import requests
headers = {'Authorization': f'Bearer {api_token}'}
result = {
    'sample_id': 'SAMP-001',
    'instrument': 'HPLC-01',
    'data': data,
    'timestamp': datetime.now().isoformat()
}
requests.post('https://lims.cloud/api/results', headers=headers, json=result)
```

### File Format Conversion

**Common Legacy Formats**:
- Spectroscopy: `.spc`, `.jdx`, `.dx` → CSV, HDF5
- Chromatography: `.d` (Agilent Chemstation) → CSV
- Microscopy: `.lif`, `.nd2` → OME-TIFF
- Office: `.xls`, `.doc` → `.xlsx`, `.docx` (or CSV for data)

**Tools**:
- **OpenChrom**: Convert chromatography formats
- **Bio-Formats**: Convert microscopy images
- **pandas**: Read old Excel formats (xlrd library)
- **LibreOffice**: Batch convert docs (headless mode)

**Example: Batch Convert .spc to CSV**:
```python
from spc import File
import pandas as pd

for spc_file in glob.glob('*.spc'):
    f = File(spc_file)
    df = pd.DataFrame({'wavelength': f.x, 'absorbance': f.sub[0].y})
    csv_file = spc_file.replace('.spc', '.csv')
    df.to_csv(csv_file, index=False)
```

### Compliance Considerations (GxP)

**Revalidation Requirements**:
- Change control: Document what changed and why
- Risk assessment: Impact on data integrity, patient safety
- Revalidation protocol: IQ/OQ/PQ (Installation/Operational/Performance Qualification)
- User training: New system SOPs
- Data migration validation: Source vs target comparison

**21 CFR Part 11 Compliance**:
- Audit trails must be preserved during migration
- Electronic signatures: Re-establish in new system
- Data integrity: ALCOA+ principles (Attributable, Legible, Contemporaneous, Original, Accurate)

### Legacy Code Migration

**MATLAB → Python**:
```matlab
% Legacy MATLAB
data = load('data.mat');
filtered = butter(data, 4, 0.1);
plot(filtered);
```

```python
# Modern Python
import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

data = np.load('data.npy')
b, a = butter(4, 0.1)
filtered = filtfilt(b, a, data)
plt.plot(filtered)
```

**SAS → R**:
```sas
/* Legacy SAS */
PROC IMPORT DATAFILE='data.csv' OUT=mydata DBMS=CSV;
PROC MEANS DATA=mydata MEAN STD;
```

```r
# Modern R
library(tidyverse)
mydata <- read_csv('data.csv')
mydata %>% summarize(across(everything(), list(mean = mean, sd = sd)))
```

### Archival Strategy

**Long-Term Preservation** (10-30 years):
- Format: Open standards (CSV, PDF/A, TIFF, HDF5)
- Medium: Enterprise-grade storage (not DVDs)
- Documentation: README, data dictionary, schema
- Verification: Checksums (MD5, SHA-256), periodic integrity checks

**Repository Options**:
- Institutional archive (university library)
- Cloud archival (AWS Glacier, Azure Archive)
- Domain repository (GenBank, PDB)

### Checklist

**Pre-Migration**:
- [ ] Full backup of legacy system
- [ ] Document current workflows
- [ ] Stakeholder buy-in
- [ ] Budget approved (software, consulting, validation)
- [ ] Timeline with milestones

**Migration**:
- [ ] Pilot migration (10% of data)
- [ ] Validation of pilot
- [ ] Iterative full migration
- [ ] Parallel operation (legacy + new) for 1-3 months

**Post-Migration**:
- [ ] User acceptance testing
- [ ] Performance monitoring
- [ ] Documentation updated
- [ ] Legacy system decommissioned or archived
- [ ] Lessons learned documented

### Common Pitfalls

1. **Underestimating data quality issues**: Expect 20-30% of time on data cleaning
2. **Insufficient user training**: Plan 2-3 training sessions per user role
3. **No rollback plan**: Keep legacy system operational until new system proven
4. **Ignoring integrations**: Instruments, printers, other systems
5. **Inadequate testing**: Test with real users, real data, real workflows

### References
- FDA Guidance: "Data Integrity and Compliance"
- GAMP 5: "Good Automated Manufacturing Practice"
- ISPE Baseline Guide Vol 5: "Commissioning and Qualification"
- Migration methodology: Kimball "Data Warehouse Toolkit"
