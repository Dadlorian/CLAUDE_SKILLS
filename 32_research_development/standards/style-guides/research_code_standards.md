# Research Code Standards
## Reproducible and Sustainable Research Software

### Philosophy
Based on:
- **Wilson et al.** "Good Enough Practices in Scientific Computing" (PLOS Comp Bio 2017)
- **Software Sustainability Institute** guidelines
- **Gentzkow & Shapiro** "Code and Data for the Social Sciences"
- **rOpenSci** package development standards
- **FAIR4RS** (FAIR for Research Software) principles

---

## Core Principles

### 1. Reproducibility
- Code produces same results on different machines
- Dependencies explicitly documented
- Random seeds set for stochastic processes
- Computational environment captured

### 2. Readability
- Code is read 10x more than written
- Self-documenting code (clear names, structure)
- Comments explain "why," not "what"
- Consistent style

### 3. Modularity
- Functions do one thing well
- DRY: Don't Repeat Yourself
- Reusable components
- Clear interfaces

### 4. Testing
- Automated tests catch errors
- Tests document expected behavior
- Regression tests prevent breakage
- Continuous integration

### 5. Version Control
- Git for all code (and small data)
- Meaningful commit messages
- Branches for features
- Tags for releases

---

## Project Structure

### Standard Layout

```
project_name/
├── README.md                 # Project overview, setup instructions
├── LICENSE                   # Software license (MIT, GPL, Apache)
├── CITATION.cff              # Citation metadata
├── environment.yml           # Conda environment (or requirements.txt)
├── Dockerfile                # Container definition (optional but recommended)
├── .gitignore                # Git ignore patterns
│
├── data/
│   ├── raw/                  # Original, immutable
│   ├── processed/            # Cleaned, transformed
│   └── README.md             # Data provenance
│
├── src/                      # Source code (reusable functions)
│   ├── __init__.py           # Python package init
│   ├── data_processing.py
│   ├── analysis.py
│   ├── visualization.py
│   └── utils.py
│
├── notebooks/                # Jupyter/R Markdown for exploration
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_main_results.ipynb
│   └── README.md             # Notebook descriptions
│
├── scripts/                  # Executable scripts (workflows)
│   ├── download_data.sh
│   ├── run_analysis.py
│   └── generate_figures.R
│
├── tests/                    # Unit tests
│   ├── test_data_processing.py
│   ├── test_analysis.py
│   └── README.md
│
├── docs/                     # Documentation (Sphinx, pkgdown)
│   ├── index.md
│   ├── installation.md
│   └── usage.md
│
├── results/                  # Generated outputs
│   ├── figures/
│   ├── tables/
│   └── models/
│
└── Snakefile                 # Workflow definition (or Makefile, Nextflow)
```

### Language-Specific Additions

**Python**:
- `setup.py` or `pyproject.toml` (package metadata)
- `requirements.txt` or `environment.yml`

**R**:
- `DESCRIPTION` (package metadata)
- `renv.lock` (package versions)
- `_pkgdown.yml` (website generation)

---

## Coding Style

### Python (PEP 8)

**Naming**:
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore`

**Whitespace**:
- 4 spaces per indentation level (no tabs)
- 2 blank lines before top-level function/class
- 1 blank line between methods

**Line length**: 79 characters (PEP 8), 88 (Black formatter)

**Imports**:
```python
# Standard library
import os
import sys

# Third-party
import numpy as np
import pandas as pd

# Local
from src import data_processing
```

**Docstrings** (NumPy/Numpydoc style):
```python
def calculate_effect_size(group1, group2, method='cohen_d'):
    """Calculate effect size between two groups.

    Parameters
    ----------
    group1 : array-like
        First group observations
    group2 : array-like
        Second group observations
    method : {'cohen_d', 'hedges_g'}, default='cohen_d'
        Effect size measure to calculate

    Returns
    -------
    float
        Effect size estimate

    Examples
    --------
    >>> calculate_effect_size([1, 2, 3], [4, 5, 6])
    -2.449
    """
    pass
```

**Type hints**:
```python
from typing import List, Dict, Optional
import numpy as np

def analyze_data(
    data: np.ndarray,
    method: str = 'linear',
    alpha: float = 0.05
) -> Dict[str, float]:
    """Analyze data with specified method."""
    pass
```

### R (Tidyverse Style Guide)

**Naming**:
- Functions/variables: `snake_case`
- No periods in names (old style: `my.function`)

**Whitespace**:
- 2 spaces per indentation
- Space after comma: `func(a, b)` not `func(a,b)`
- Space around operators: `x + y` not `x+y`

**Assignment**: `<-` (not `=`)
```r
# Good
x <- 5

# Bad
x = 5
```

**Pipes**:
```r
# tidyverse pipe
data %>%
  filter(age > 18) %>%
  select(id, age, treatment) %>%
  group_by(treatment) %>%
  summarize(mean_age = mean(age))

# base R pipe (R >= 4.1)
data |>
  subset(age > 18) |>
  transform(age_group = cut(age, breaks = c(0, 30, 50, 100)))
```

**Roxygen documentation**:
```r
#' Calculate effect size between two groups
#'
#' @param group1 Numeric vector of first group observations
#' @param group2 Numeric vector of second group observations
#' @param method Effect size method: "cohen_d" or "hedges_g"
#'
#' @return Numeric effect size estimate
#' @export
#'
#' @examples
#' calculate_effect_size(c(1, 2, 3), c(4, 5, 6))
calculate_effect_size <- function(group1, group2, method = "cohen_d") {
  # Implementation
}
```

---

## Version Control (Git)

### Commit Messages

**Format** (Conventional Commits):
```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Add/modify tests
- `chore`: Maintenance (dependencies, CI)

**Examples**:
```
feat: add Bayesian analysis module

Implemented hierarchical Bayesian model using PyMC for
multilevel data analysis. Includes prior selection helpers
and diagnostic plots.

Closes #42

---

fix: correct p-value calculation in t-test

Previous implementation used one-tailed test when two-tailed
was intended. Updated tests to catch this.

Fixes #87
```

### Branching Strategy

**Main branches**:
- `main` (or `master`): Stable, released code
- `develop`: Integration branch

**Feature branches**:
- `feature/new-analysis-method`
- `fix/issue-123`
- `docs/update-readme`

**Workflow**:
1. Branch from `develop`: `git checkout -b feature/new-feature develop`
2. Commit changes with clear messages
3. Push and create Pull Request to `develop`
4. Code review
5. Merge to `develop`
6. Periodically merge `develop` → `main` for releases

### `.gitignore`

**Python**:
```
# Byte-compiled
__pycache__/
*.py[cod]

# Distribution
build/
dist/
*.egg-info/

# Jupyter
.ipynb_checkpoints/

# IDEs
.vscode/
.idea/

# Data (large files tracked with DVC)
data/raw/*
!data/raw/README.md
data/processed/*
!data/processed/README.md

# Results (regeneratable)
results/figures/
results/models/

# Environment
.env
venv/
```

**R**:
```
# R history and data
.Rhistory
.RData
.Rproj.user/

# Output
results/
*.pdf
*.png

# Package builds
*.tar.gz
*.Rcheck/
```

---

## Dependency Management

### Python (Conda)

**environment.yml**:
```yaml
name: myproject
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy=1.24
  - pandas=2.0
  - scipy=1.11
  - matplotlib=3.7
  - jupyter=1.0
  - pytest=7.4
  - black=23.7  # code formatter
  - pip:
    - domain-specific-package==1.2.3
```

**Create environment**: `conda env create -f environment.yml`
**Activate**: `conda activate myproject`
**Update**: `conda env update -f environment.yml`

### Python (pip + venv)

**requirements.txt**:
```
numpy==1.24.3
pandas==2.0.2
scipy==1.11.0
matplotlib==3.7.1
# Optional: with hash for security
# numpy==1.24.3 --hash=sha256:...
```

**Setup**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### R (renv)

**Setup**:
```r
# Initialize project
renv::init()

# Install packages (recorded in lockfile)
install.packages(c("tidyverse", "ggplot2", "lme4"))

# Snapshot dependencies
renv::snapshot()

# Restore on another machine
renv::restore()
```

**renv.lock** (auto-generated):
```json
{
  "R": {"Version": "4.3.0"},
  "Packages": {
    "ggplot2": {
      "Package": "ggplot2",
      "Version": "3.4.2",
      "Source": "Repository",
      "Repository": "CRAN"
    }
  }
}
```

---

## Testing

### Python (pytest)

**test_analysis.py**:
```python
import pytest
import numpy as np
from src.analysis import calculate_mean, t_test

def test_calculate_mean():
    """Test mean calculation."""
    data = [1, 2, 3, 4, 5]
    assert calculate_mean(data) == 3.0

def test_calculate_mean_empty():
    """Test mean with empty input."""
    with pytest.raises(ValueError):
        calculate_mean([])

def test_t_test():
    """Test t-test returns expected structure."""
    group1 = np.random.normal(0, 1, 30)
    group2 = np.random.normal(0.5, 1, 30)
    result = t_test(group1, group2)

    assert 'statistic' in result
    assert 'pvalue' in result
    assert 0 <= result['pvalue'] <= 1

@pytest.mark.parametrize("group1,group2,expected_p", [
    ([1, 2, 3], [1, 2, 3], 1.0),  # Identical groups
    ([1, 1, 1], [2, 2, 2], 0.0),  # Clearly different
])
def test_t_test_parametrized(group1, group2, expected_p):
    """Test t-test with various inputs."""
    result = t_test(group1, group2)
    assert result['pvalue'] == pytest.approx(expected_p, abs=1e-2)
```

**Run tests**: `pytest tests/`
**With coverage**: `pytest --cov=src tests/`

### R (testthat)

**tests/testthat/test-analysis.R**:
```r
library(testthat)

test_that("calculate_mean works correctly", {
  expect_equal(calculate_mean(c(1, 2, 3, 4, 5)), 3)
  expect_error(calculate_mean(c()), "empty input")
})

test_that("t_test returns expected structure", {
  group1 <- rnorm(30, mean = 0)
  group2 <- rnorm(30, mean = 0.5)
  result <- t_test(group1, group2)

  expect_named(result, c("statistic", "pvalue", "conf_int"))
  expect_true(result$pvalue >= 0 && result$pvalue <= 1)
})
```

**Run tests**: `devtools::test()` or `testthat::test_dir("tests")`

---

## Documentation

### README.md Template

```markdown
# Project Title

Brief description (1-2 sentences).

## Installation

### Prerequisites
- Python 3.10+
- Conda (recommended) or pip

### Setup
```bash
git clone https://github.com/user/project.git
cd project
conda env create -f environment.yml
conda activate project
```

## Usage

### Basic Example
```python
from src import analysis

data = load_data("data/processed/clean_data.csv")
results = analysis.run_analysis(data, method='linear')
```

### Reproducing Results
```bash
# Download data
bash scripts/download_data.sh

# Run full pipeline
snakemake --cores 4

# Or step-by-step
python scripts/01_preprocess.py
python scripts/02_analyze.py
python scripts/03_visualize.py
```

## Project Structure
- `data/`: Raw and processed data (not in Git, see DVC)
- `src/`: Reusable Python modules
- `notebooks/`: Exploratory analysis
- `scripts/`: Workflow scripts
- `tests/`: Unit tests

## Citation
```bibtex
@software{author2024,
  author = {Last, First},
  title = {Project Title},
  year = {2024},
  doi = {10.5281/zenodo.#######}
}
```

## License
MIT License (see LICENSE file)

## Contact
- Author: name@email.com
- Issues: https://github.com/user/project/issues
```

### Inline Documentation

**When to comment**:
- Complex algorithms (cite source)
- Non-obvious workarounds
- Parameter constraints
- Assumptions

**When NOT to comment**:
- Obvious code (`i = i + 1  # increment i`)
- Redundant docstrings

**Good comments**:
```python
# Use Welch's t-test (unequal variances) based on Levene test result
t_stat, p_val = stats.ttest_ind(group1, group2, equal_var=False)

# Sample size calculation using G*Power 3.1 (Faul et al., 2007)
# Effect size d=0.5, power=0.8, alpha=0.05
required_n = 64  # per group
```

---

## Reproducibility

### Random Seeds

**Python**:
```python
import random
import numpy as np

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)

# For libraries
import torch
torch.manual_seed(42)

import tensorflow as tf
tf.random.set_seed(42)
```

**R**:
```r
set.seed(42)

# For parallel processing
library(doRNG)
registerDoRNG(42)
```

### Containerization (Docker)

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY environment.yml .
RUN conda env create -f environment.yml

# Copy code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Set entrypoint
CMD ["python", "scripts/run_analysis.py"]
```

**Build and run**:
```bash
docker build -t myproject:1.0 .
docker run -v $(pwd)/data:/app/data myproject:1.0
```

### Workflow Management

**Snakefile** (Snakemake):
```python
rule all:
    input:
        "results/figures/figure1.png",
        "results/tables/table1.csv"

rule preprocess:
    input:
        "data/raw/data.csv"
    output:
        "data/processed/clean_data.csv"
    conda:
        "environment.yml"
    script:
        "scripts/01_preprocess.py"

rule analyze:
    input:
        "data/processed/clean_data.csv"
    output:
        "results/tables/table1.csv"
    params:
        method="linear",
        alpha=0.05
    script:
        "scripts/02_analyze.py"

rule visualize:
    input:
        "results/tables/table1.csv"
    output:
        "results/figures/figure1.png"
    script:
        "scripts/03_visualize.R"
```

**Run**: `snakemake --cores 4 --use-conda`

---

## Code Review Checklist

### Functionality
- [ ] Code runs without errors
- [ ] Produces expected output
- [ ] Edge cases handled

### Reproducibility
- [ ] Random seeds set
- [ ] Dependencies documented (environment.yml, renv.lock)
- [ ] Data provenance clear (where did data come from?)

### Code Quality
- [ ] Follows style guide (PEP 8, tidyverse)
- [ ] Functions < 50 lines (if longer, refactor)
- [ ] No hardcoded paths (use relative or config)
- [ ] No magic numbers (define as named constants)

### Documentation
- [ ] README explains setup and usage
- [ ] Functions have docstrings
- [ ] Complex logic commented
- [ ] CITATION.cff or equivalent

### Testing
- [ ] Unit tests for key functions
- [ ] Tests pass (`pytest`, `testthat`)
- [ ] Coverage > 80% for critical code

### Version Control
- [ ] Meaningful commit messages
- [ ] `.gitignore` excludes generated files
- [ ] Large data tracked with DVC or external

---

## Tools

**Formatters**:
- **Python**: Black, autopep8, YAPF
- **R**: styler package

**Linters**:
- **Python**: flake8, pylint, ruff
- **R**: lintr package

**Type Checkers**:
- **Python**: mypy, pyright

**Documentation**:
- **Python**: Sphinx (NumPy/Google style)
- **R**: pkgdown, roxygen2

**CI/CD**:
- GitHub Actions
- GitLab CI
- Travis CI

---

## References

- Wilson et al. (2017). "Good Enough Practices in Scientific Computing." PLOS Computational Biology.
- Gentzkow & Shapiro. "Code and Data for the Social Sciences: A Practitioner's Guide."
- Software Sustainability Institute: software.ac.uk
- rOpenSci Packages: ropensci.org
- FAIR4RS: doi.org/10.15497/RDA00068

---

**Version**: 1.0
**Last Updated**: 2025-11-19
