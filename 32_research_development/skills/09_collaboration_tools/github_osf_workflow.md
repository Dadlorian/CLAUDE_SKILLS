# Integrated GitHub + OSF Research Workflow

Complete guide for reproducible, collaborative research using GitHub for code and OSF for project management.

## Overview

This workflow integrates:
- **GitHub**: Version control for code, scripts, and notebooks
- **OSF (Open Science Framework)**: Project registration, preregistration, data archiving
- **Zenodo**: Long-term code archiving with DOI
- **Overleaf**: Collaborative manuscript writing

## Setup Instructions

### 1. Initialize OSF Project

```bash
# Install OSF CLI
pip install osfclient

# Configure OSF credentials
osf init

# Create new project
osf create "My Research Project"
```

**OSF Project Structure:**
```
My Research Project (OSF)
├── Preregistration
│   └── study_protocol.md
├── Data
│   ├── raw/
│   └── processed/
├── Materials
│   └── survey_instruments.pdf
├── Code (linked to GitHub)
└── Manuscript (linked to Overleaf)
```

### 2. Initialize GitHub Repository

```bash
# Create local repository
mkdir my-research-project
cd my-research-project
git init

# Create standard research directory structure
mkdir -p data/{raw,processed,metadata}
mkdir -p code/{analysis,preprocessing}
mkdir -p docs
mkdir -p results/{figures,tables}

# Create README
cat > README.md << 'EOF'
# My Research Project

## Overview
[Brief description of the research]

## Project Organization
- `data/raw/` - Original, immutable data
- `data/processed/` - Cleaned, analysis-ready data
- `code/` - Analysis scripts and notebooks
- `results/` - Figures, tables, and reports
- `docs/` - Documentation and protocols

## Reproducibility
All analyses use conda environment (see `environment.yml`)

## Citation
[Will be added upon publication]

## License
MIT License (code), CC-BY 4.0 (data/docs)
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Data files (use Git LFS or OSF for large data)
data/raw/*.csv
data/raw/*.xlsx
data/processed/*.pkl

# Temporary files
*.tmp
*.log
.DS_Store
__pycache__/
.ipynb_checkpoints/

# Credentials
.env
secrets.yml

# Large output files
results/*.png
results/*.pdf
EOF

# Create environment.yml for reproducibility
cat > environment.yml << 'EOF'
name: research-project
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - pandas=1.5
  - numpy=1.24
  - matplotlib=3.7
  - seaborn=0.12
  - scipy=1.10
  - scikit-learn=1.2
  - jupyter=1.0
  - pip
  - pip:
    - osfclient==0.0.5
EOF

# Initial commit
git add .
git commit -m "Initial project setup"

# Create GitHub repository and push
gh repo create my-research-project --public --source=. --remote=origin
git push -u origin main
```

### 3. Link GitHub to OSF

1. Go to your OSF project
2. Click "Add Component" → "GitHub"
3. Authorize OSF to access GitHub
4. Select repository: `username/my-research-project`
5. OSF now mirrors your GitHub repository

### 4. Connect Zenodo for Code Archiving

```bash
# On GitHub repository page:
# 1. Go to Settings → Integrations → Zenodo
# 2. Enable Zenodo integration
# 3. Create a release to trigger DOI minting

git tag -a v1.0 -m "First release"
git push origin v1.0

# Zenodo automatically:
# - Creates archive snapshot
# - Mints DOI (e.g., 10.5281/zenodo.12345)
# - Provides citation
```

## Workflow: From Data Collection to Publication

### Phase 1: Preregistration

**Create preregistration on OSF:**

```markdown
# Preregistration: [Study Title]

## Study Design
- Type: Randomized controlled trial
- Sample size: N=100 (50 per group)
- Power analysis: 80% power to detect d=0.5

## Hypotheses
1. Treatment group will show 20% improvement vs control
2. Effect will be moderated by baseline severity

## Planned Analyses
- Primary: Independent t-test comparing groups at endpoint
- Secondary: ANCOVA controlling for baseline
- Exploratory: Subgroup analysis by gender

## Exclusion Criteria
- Age < 18 or > 65
- Prior treatment with study drug
- Significant comorbidities

## Deviations
[Will be documented post-data collection]

**Registered on:** 2024-01-15
**Registration URL:** https://osf.io/abc123/
```

**Submit for timestamped registration:**
- OSF → Registrations → Create New Registration
- Choose template: "OSF Preregistration"
- Complete form
- Submit → Creates permanent, timestamped record

### Phase 2: Data Collection

```python
# code/data_collection/collect_survey_data.py

import pandas as pd
from datetime import datetime
import hashlib

def collect_and_validate_data(raw_file, output_file):
    """
    Load raw survey data, validate, and export

    Quality checks:
    - Range validation
    - Duplicate detection
    - Missing data logging
    """
    # Load data
    df = pd.read_csv(raw_file)

    # Log original file checksum
    with open(raw_file, 'rb') as f:
        checksum = hashlib.md5(f.read()).hexdigest()

    print(f"Original file MD5: {checksum}")

    # Validation checks
    issues = []

    # Check age range
    invalid_age = df[(df['age'] < 18) | (df['age'] > 65)]
    if len(invalid_age) > 0:
        issues.append(f"Invalid age: {len(invalid_age)} records")

    # Check duplicates
    duplicates = df[df.duplicated(subset=['participant_id'], keep=False)]
    if len(duplicates) > 0:
        issues.append(f"Duplicate IDs: {len(duplicates)} records")

    # Check missing data
    missing = df.isnull().sum()
    if missing.sum() > 0:
        issues.append(f"Missing values: {missing.to_dict()}")

    # Save validation log
    with open('data/metadata/validation_log.txt', 'a') as log:
        log.write(f"\n=== Validation: {datetime.now()} ===\n")
        log.write(f"Input file: {raw_file}\n")
        log.write(f"MD5 checksum: {checksum}\n")
        log.write(f"Total records: {len(df)}\n")
        if issues:
            log.write("Issues found:\n")
            for issue in issues:
                log.write(f"  - {issue}\n")
        else:
            log.write("No issues found\n")

    # Export clean data
    df_clean = df.dropna().drop_duplicates()
    df_clean.to_csv(output_file, index=False)
    print(f"Clean data saved: {output_file}")

    return df_clean

if __name__ == "__main__":
    collect_and_validate_data(
        'data/raw/survey_responses_2024-01-15.csv',
        'data/processed/survey_clean.csv'
    )
```

**Commit and document:**

```bash
git add code/data_collection/collect_survey_data.py
git add data/metadata/validation_log.txt
git commit -m "Add data validation script with quality checks"
git push
```

### Phase 3: Analysis

```python
# code/analysis/primary_analysis.py

import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

def primary_analysis():
    """
    Primary analysis: Compare treatment vs control

    Preregistered analysis plan:
    - Independent t-test
    - Effect size (Cohen's d)
    - 95% confidence intervals
    """
    # Load data
    data = pd.read_csv('data/processed/survey_clean.csv')

    # Split by group
    treatment = data[data['group'] == 'treatment']['outcome']
    control = data[data['group'] == 'control']['outcome']

    # Descriptive statistics
    desc = {
        'treatment_n': len(treatment),
        'treatment_mean': treatment.mean(),
        'treatment_sd': treatment.std(),
        'control_n': len(control),
        'control_mean': control.mean(),
        'control_sd': control.std()
    }

    # T-test
    t_stat, p_value = stats.ttest_ind(treatment, control)

    # Effect size (Cohen's d)
    pooled_sd = ((len(treatment)-1)*treatment.std()**2 +
                 (len(control)-1)*control.std()**2) / (len(treatment)+len(control)-2)
    pooled_sd = pooled_sd ** 0.5
    cohens_d = (treatment.mean() - control.mean()) / pooled_sd

    # Results
    results = {
        **desc,
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d
    }

    # Save results
    import json
    with open('results/primary_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.boxplot([treatment, control], labels=['Treatment', 'Control'])
    ax.set_ylabel('Outcome Score')
    ax.set_title(f'Primary Outcome\nt({len(treatment)+len(control)-2}) = {t_stat:.2f}, p = {p_value:.3f}')
    plt.savefig('results/figures/primary_outcome.png', dpi=300, bbox_inches='tight')

    return results

if __name__ == "__main__":
    results = primary_analysis()
    print("Primary Analysis Results:")
    print(f"  t = {results['t_statistic']:.3f}")
    print(f"  p = {results['p_value']:.4f}")
    print(f"  Cohen's d = {results['cohens_d']:.3f}")
```

**Commit with clear message:**

```bash
git add code/analysis/primary_analysis.py
git add results/primary_analysis_results.json
git add results/figures/primary_outcome.png
git commit -m "Complete primary analysis (preregistered)

- Independent t-test: t(98) = 3.45, p = .001
- Effect size: Cohen's d = 0.82 (large)
- Confirms hypothesis: treatment > control"

git push
```

### Phase 4: Manuscript Writing (Overleaf Integration)

**Link Overleaf project:**

1. Create new Overleaf project
2. In Overleaf: Menu → GitHub → Import from GitHub → Select repo
3. Overleaf syncs with `manuscript/` folder in GitHub

**manuscript/main.tex:**

```latex
\documentclass{article}
\usepackage{natbib}

\title{Treatment Effects on Clinical Outcomes: A Randomized Controlled Trial}
\author{Your Name et al.}

\begin{document}

\maketitle

\section{Introduction}
[Write introduction...]

\section{Methods}
This study was preregistered (OSF: https://osf.io/abc123/) before data collection.

\subsection{Design}
Randomized controlled trial with 100 participants...

\section{Results}
The treatment group showed significantly better outcomes than control
(M = 75.3, SD = 12.1 vs M = 62.4, SD = 14.3; t(98) = 3.45, p < .001, d = 0.82).

\begin{figure}
\includegraphics{../results/figures/primary_outcome.png}
\caption{Primary outcome by group}
\end{figure}

\section{Discussion}
[Interpret results...]

\bibliography{references}

\section*{Data and Code Availability}
All data and analysis code are available at GitHub
(https://github.com/username/my-research-project) and archived at Zenodo
(DOI: 10.5281/zenodo.12345). The project is registered on OSF (https://osf.io/project123/).

\end{document}
```

### Phase 5: Publication and Archiving

**Before submission:**

```bash
# Create release for publication
git tag -a v1.0-publication -m "Code and data for manuscript submission"
git push origin v1.0-publication

# Zenodo automatically creates DOI: 10.5281/zenodo.67890
```

**Upload data to OSF:**

```bash
# Upload final dataset
osf upload data/processed/survey_clean.csv osf://abc123/data/

# Upload results
osf upload results/ osf://abc123/results/
```

**Data availability statement:**

```
All data are available at OSF (https://osf.io/abc123/).
Analysis code is available at GitHub (https://github.com/user/repo)
and archived at Zenodo (DOI: 10.5281/zenodo.67890).
```

## Best Practices

### 1. Commit Frequently
```bash
# Good practice: Small, focused commits
git commit -m "Fix bug in data cleaning script"
git commit -m "Add power analysis calculation"
git commit -m "Update figure formatting"
```

### 2. Use Branches for Experimental Changes
```bash
# Create branch for new analysis
git checkout -b sensitivity-analysis

# Make changes, test
git add code/sensitivity_analysis.py
git commit -m "Add sensitivity analysis"

# Merge when ready
git checkout main
git merge sensitivity-analysis
```

### 3. Document Everything
- **README.md**: Project overview, setup instructions
- **METHODS.md**: Detailed data collection protocols
- **CHANGELOG.md**: Track major changes
- **LICENSE**: Code (MIT) and data (CC-BY) licenses

### 4. Automate Quality Checks
```python
# tests/test_data_quality.py
import pytest
import pandas as pd

def test_no_missing_ids():
    """Ensure all records have participant ID"""
    df = pd.read_csv('data/processed/survey_clean.csv')
    assert df['participant_id'].notna().all()

def test_age_range():
    """Ensure ages within protocol range (18-65)"""
    df = pd.read_csv('data/processed/survey_clean.csv')
    assert df['age'].between(18, 65).all()
```

Run tests before commits:
```bash
pytest tests/
git add .
git commit -m "Pass all data quality tests"
```

## Troubleshooting

**Problem: Large data files slow down Git**

Solution: Use Git LFS (Large File Storage)
```bash
git lfs install
git lfs track "*.csv"
git lfs track "*.xlsx"
git add .gitattributes
git commit -m "Configure Git LFS for data files"
```

**Problem: Accidentally committed sensitive data**

Solution: Remove from history
```bash
# Remove file from all commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch data/sensitive.csv" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: Rewrites history)
git push origin --force --all
```

**Problem: Merge conflicts in notebooks**

Solution: Use nbdime for notebook-aware diffing
```bash
pip install nbdime
nbdiff notebook1.ipynb notebook2.ipynb
```

## Summary Checklist

- [ ] OSF project created and structured
- [ ] GitHub repository initialized with standard structure
- [ ] GitHub linked to OSF
- [ ] Zenodo integration enabled
- [ ] Preregistration completed (if applicable)
- [ ] README.md with project overview
- [ ] LICENSE files added
- [ ] .gitignore configured for data files
- [ ] environment.yml for reproducibility
- [ ] Analysis scripts documented
- [ ] Results archived before publication
- [ ] Data availability statement in manuscript
- [ ] DOI obtained for code (Zenodo) and data (OSF/Zenodo)
