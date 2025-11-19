# Hypothesis Testing Research Pattern
## Systematic Approach to Experimental Research

### Pattern Overview

**When to use**: Confirmatory research with specific, testable hypotheses

**Phases**: Literature Review → Hypothesis → Design → Execute → Analyze → Disseminate

**Timeline**: 6-24 months (varies by field)

---

## Phase 1: Literature Review & Hypothesis Formation (2-4 weeks)

### Systematic Search
```
Databases: PubMed, Web of Science, Scopus
Search terms: (concept A) AND (concept B) AND (outcome)
Filters: Last 10 years, English, peer-reviewed
```

### Critical Appraisal
- **PICO framework** (Population, Intervention, Comparison, Outcome)
- **Gap identification**: What's unknown? What's contradictory?
- **Theoretical grounding**: Which theory supports your hypothesis?

### Hypothesis Formulation
- **Null hypothesis (H0)**: No effect/relationship
- **Alternative hypothesis (H1)**: Specific directional or non-directional prediction
- **Example**:
  - H0: Drug X does not reduce tumor size compared to placebo
  - H1: Drug X reduces tumor size by ≥20% compared to placebo (at 8 weeks)

### Pre-Registration
Register hypothesis, methods, analysis plan before data collection:
- **ClinicalTrials.gov**: Clinical trials (FDA requirement for many studies)
- **OSF**: Lab studies, surveys, observational research
- **AsPredicted.org**: Quick preregistration (no peer review)

**Benefits**: Reduces p-hacking, HARKing, publication bias

---

## Phase 2: Experimental Design (2-6 weeks)

### Design Selection

**Randomized Controlled Trial (RCT)** (gold standard):
- Random assignment to treatment/control
- Blinding (single, double, triple)
- Parallel groups or crossover

**Quasi-Experimental**:
- Non-random assignment (regression discontinuity, difference-in-differences)
- Use when randomization unethical or impractical

**Observational**:
- Cohort (longitudinal), case-control, cross-sectional
- Control for confounders (matching, stratification, regression)

### Power Analysis

**Required inputs**:
1. **Effect size**: Expected magnitude (from pilot data or literature)
2. **Alpha (α)**: Type I error rate (typically 0.05)
3. **Power (1-β)**: Type II error rate (typically 0.80)

**Tools**: G*Power, R pwr package, Python statsmodels

**Example (t-test)**:
```r
library(pwr)

# Two-sample t-test
# Effect size d = 0.5 (medium), alpha = 0.05, power = 0.8
pwr.t.test(d = 0.5, sig.level = 0.05, power = 0.8, type = 'two.sample')
# Result: n = 64 per group
```

### Randomization

**Simple randomization**: Coin flip, random number generator
```python
import random
participants = ['P01', 'P02', ..., 'P100']
random.shuffle(participants)
treatment = participants[:50]
control = participants[50:]
```

**Block randomization**: Ensure balance across time
```python
import numpy as np
block_size = 4
n_blocks = 25
for i in range(n_blocks):
    block = ['T', 'T', 'C', 'C']
    np.random.shuffle(block)
    print(f'Block {i+1}: {block}')
```

**Stratified randomization**: Balance on prognostic factors (age, sex)

### Controls

**Positive control**: Known effective treatment (benchmark)
**Negative control**: Known ineffective (detect artifacts)
**Vehicle control**: Delivery method without active ingredient
**Blinding**: Participants, assessors, data analysts unaware of assignments

---

## Phase 3: Data Collection (Variable, 1-18 months)

### Standard Operating Procedures (SOPs)
- Detailed protocols for every procedure
- Training and certification of personnel
- Deviation log (document any protocol violations)

### Quality Control
- **Calibration**: Instruments calibrated before use
- **Replicates**: Technical (same sample) and biological (different samples)
- **Blanks**: Negative controls to detect contamination
- **Standards**: Known concentrations for quantification

### Data Management
- **Electronic data capture (EDC)**: REDCap, Qualtrics, custom databases
- **Real-time validation**: Range checks, required fields
- **Audit trail**: Who entered data, when, what changed
- **Backups**: Daily automated backups to multiple locations

### Monitoring
- **Data Safety Monitoring Board (DSMB)**: For clinical trials, independent review
- **Interim analyses**: Pre-specified time points (be cautious of α-inflation)
- **Stopping rules**: Futility (unlikely to show effect) or overwhelming efficacy

---

## Phase 4: Statistical Analysis (2-8 weeks)

### Data Cleaning
```r
library(tidyverse)

data <- read_csv('raw_data.csv')

# Check for outliers
summary(data$outcome)
boxplot(data$outcome)

# Remove outliers (document criteria)
data_clean <- data %>%
  filter(outcome > mean(outcome) - 3*sd(outcome),
         outcome < mean(outcome) + 3*sd(outcome))

# Missing data
sum(is.na(data_clean))
# If <5%, list-wise deletion; if >5%, consider imputation (mice package)
```

### Assumption Testing
```r
# Normality (for parametric tests)
shapiro.test(data_clean$outcome)  # p > 0.05 = normal
hist(data_clean$outcome)
qqnorm(data_clean$outcome); qqline(data_clean$outcome)

# Homogeneity of variance
bartlett.test(outcome ~ group, data = data_clean)  # p > 0.05 = equal variances
```

### Primary Analysis (Pre-specified)
```r
# Independent t-test
t.test(outcome ~ group, data = data_clean, var.equal = TRUE)

# With effect size
library(effectsize)
cohens_d(outcome ~ group, data = data_clean)

# Report:
# t(df) = statistic, p = value, d = effect size, 95% CI [lower, upper]
```

### Secondary Analyses (Exploratory)
- Subgroup analyses (pre-specified vs post-hoc)
- Covariates (ANCOVA to control for baseline differences)
- **Caution**: Correct for multiple comparisons (Bonferroni, Holm, FDR)

### Sensitivity Analysis
- Robustness to outliers (remove, analyze, report both)
- Missing data (complete case vs imputation)
- Alternative statistical tests (parametric vs non-parametric)

---

## Phase 5: Interpretation (1-2 weeks)

### Statistical Significance vs Practical Significance
- p < 0.05 means unlikely due to chance (if H0 true)
- **Does NOT mean**: Large effect, clinically important, replicable
- **Effect size** more important than p-value

### Confidence Intervals
- Prefer CI over p-value alone
- Example: "Mean difference = 5.2 kg (95% CI [2.1, 8.3]), p = .002"
- CI excludes zero → statistically significant
- CI width → precision of estimate

### Causality (Bradford Hill Criteria)
1. **Strength**: Large effect size
2. **Consistency**: Replicated across studies
3. **Specificity**: Specific cause → specific effect
4. **Temporality**: Cause precedes effect
5. **Dose-response**: More exposure → more effect
6. **Plausibility**: Biological mechanism
7. **Coherence**: Consistent with known facts
8. **Experiment**: RCT evidence
9. **Analogy**: Similar examples exist

### Limitations
- **Internal validity**: Selection bias, confounders, measurement error
- **External validity**: Generalizability to other populations/settings
- **Statistical**: Underpowered, multiple testing, regression to mean

---

## Phase 6: Dissemination (2-6 months)

### Manuscript Preparation

**IMRAD Structure**:
- **Introduction**: Background, gap, aims
- **Methods**: Design, participants, procedures, analysis
- **Results**: Descriptive stats, primary analysis, secondary
- **Discussion**: Interpretation, limitations, implications

**Reporting Guidelines** (EQUATOR network):
- **RCT**: CONSORT (flow diagram, all outcomes, ITT analysis)
- **Observational**: STROBE (cohort, case-control, cross-sectional)
- **Animal research**: ARRIVE

### Data & Code Sharing
- Deposit data in repository (Zenodo, Dryad, OSF)
- Share analysis code (GitHub, OSF)
- Document: README, data dictionary, codebook

### Preprint
- Post to preprint server *before* journal submission
- **Biomedical**: bioRxiv, medRxiv
- **Social sciences**: SocArXiv, PsyArXiv
- **Physics/CS**: arXiv
- **Benefits**: Rapid dissemination, timestamp, feedback before peer review

### Peer Review
- Respond to reviewers constructively (point-by-point response)
- Revise manuscript, highlight changes
- Re-analyze if needed (but don't p-hack!)

### Publication
- Open access (gold, green, diamond) for maximum impact
- Use persistent identifier (DOI) for data/code
- Promote on social media (Twitter thread, blog post)

---

## Success Criteria Checklist

### Planning
- [ ] Pre-registration completed (ClinicalTrials.gov, OSF)
- [ ] Power analysis conducted (sufficient sample size)
- [ ] Ethics approval obtained (IRB/IACUC)
- [ ] Data management plan written

### Execution
- [ ] SOPs followed consistently
- [ ] Data quality checks passed
- [ ] Blinding maintained (if applicable)
- [ ] Protocol deviations documented

### Analysis
- [ ] Pre-specified analysis conducted
- [ ] Assumptions tested
- [ ] Effect sizes reported (not just p-values)
- [ ] Multiple testing corrected (if applicable)

### Reporting
- [ ] Reporting guideline followed (CONSORT, STROBE)
- [ ] Data & code shared publicly
- [ ] Limitations acknowledged
- [ ] Conflicts of interest disclosed

---

## Common Pitfalls

1. **Underpowered studies**: Too small → false negatives
2. **P-hacking**: Trying multiple analyses until p < .05
3. **HARKing**: Hypothesizing After Results Known (present exploratory as confirmatory)
4. **Cherry-picking**: Report only significant results
5. **Ignore assumptions**: Use parametric tests on non-normal data
6. **Confuse significance with importance**: p < .05 but effect size trivial

---

## Tools & Resources

**Power analysis**: G*Power, R pwr, Python statsmodels.stats.power
**Pre-registration**: OSF (osf.io), AsPredicted (aspredicted.org), ClinicalTrials.gov
**Data collection**: REDCap, Qualtrics, Google Forms
**Analysis**: R (tidyverse, lme4), Python (scipy, statsmodels), SPSS, SAS
**Reporting**: Overleaf (LaTeX), Google Docs, Zotero (references)
**Sharing**: OSF, Zenodo, GitHub, Dryad

---

## References

- Shadish, Cook & Campbell (2002). *Experimental and Quasi-Experimental Designs*
- Cohen (1988). *Statistical Power Analysis for the Behavioral Sciences*
- Cumming (2013). *Understanding the New Statistics*: Effect sizes, CIs, meta-analysis
- Simmons et al. (2011). "False-Positive Psychology." *Psychological Science*, 22(11), 1359-1366
- EQUATOR Network: equator-network.org (reporting guidelines)
