# Research Methodologies Skill

## Purpose
Master rigorous experimental design, statistical analysis, and research methods across quantitative, qualitative, and mixed approaches for reproducible, impactful research.

## Core Competencies

### Quantitative Methods
- **Experimental Design**: RCTs, quasi-experimental, factorial designs
- **Statistical Analysis**: Parametric/non-parametric tests, regression, ANOVA, Bayesian methods
- **Power Analysis**: Sample size determination using G*Power, R pwr
- **Causal Inference**: Propensity scores, instrumental variables, difference-in-differences

### Qualitative Methods
- **Grounded Theory**: Open/axial/selective coding, theoretical saturation
- **Phenomenology**: Lived experience analysis, bracketing
- **Ethnography**: Participant observation, field notes, thick description
- **Case Studies**: Multiple case analysis, pattern matching, cross-case synthesis

### Mixed Methods
- **Convergent Design**: Simultaneous quant+qual, merge results
- **Explanatory Sequential**: Quant → Qual (explain quantitative findings)
- **Exploratory Sequential**: Qual → Quant (test qualitative insights)
- **Embedded Design**: One method within another framework

### Advanced Techniques
- **Structural Equation Modeling (SEM)**: Latent variables, path analysis
- **Multilevel Modeling (HLM)**: Nested data, random effects
- **Survival Analysis**: Time-to-event, Cox regression, Kaplan-Meier
- **Meta-Analysis**: Fixed/random effects, forest plots, publication bias detection

## Workflow

### 1. Research Question Formulation
- Literature review (systematic search: PubMed, Web of Science)
- Gap identification (what's unknown or contradictory?)
- PICO framework (Population, Intervention, Comparison, Outcome)
- Pre-registration (OSF, ClinicalTrials.gov)

### 2. Study Design
- Select appropriate design (experimental vs observational)
- Power analysis (effect size, alpha, power → sample size)
- Randomization strategy (simple, block, stratified)
- Control selection (positive, negative, vehicle)
- Blinding protocol (single, double, triple)

### 3. Data Collection
- Standard Operating Procedures (SOPs)
- Data quality checks (range, consistency, completeness)
- Electronic data capture (REDCap, Qualtrics)
- Audit trail (21 CFR Part 11 compliance if GxP)

### 4. Statistical Analysis
- Data cleaning (outliers, missing data, normality checks)
- Descriptive statistics (mean, SD, distributions)
- Assumption testing (normality: Shapiro-Wilk, homogeneity: Levene's)
- Primary analysis (pre-specified in protocol)
- Sensitivity analysis (robustness checks)
- Multiple testing correction (Bonferroni, FDR)

### 5. Reporting
- Follow reporting guidelines (CONSORT, STROBE, PRISMA)
- Report: test statistic, df, p-value, effect size, confidence interval
- Example: "t(58) = 3.45, p = .001, d = 0.82, 95% CI [0.35, 1.29]"
- Share data and analysis code (Zenodo, OSF, GitHub)

## Tools

**Statistical Software**:
- **R**: tidyverse, lme4 (multilevel), lavaan (SEM), meta (meta-analysis)
- **Python**: scipy, statsmodels, pingouin, pymc (Bayesian)
- **Commercial**: SPSS, SAS, Stata, Mplus (SEM)

**Power Analysis**:
- G*Power (free, GUI-based)
- R pwr package
- Python statsmodels.stats.power

**Qualitative Analysis**:
- NVivo, MAXQDA, Atlas.ti (CAQDAS software)
- Dedoose (cloud-based, mixed methods)

**Reporting**:
- EQUATOR Network (equator-network.org): Reporting guidelines
- Zotero, Mendeley: Reference management

## Success Criteria
- [ ] Pre-registration completed before data collection
- [ ] Power analysis confirms adequate sample size
- [ ] All assumptions tested and reported
- [ ] Effect sizes and confidence intervals reported (not just p-values)
- [ ] Reporting guideline checklist completed (CONSORT, STROBE)
- [ ] Data and code shared in public repository
- [ ] Reproducible: Another researcher can replicate analysis

## Common Pitfalls
- Underpowered studies (Type II error)
- P-hacking (trying analyses until p<.05)
- HARKing (Hypothesizing After Results Known)
- Ignoring assumptions (using parametric tests on non-normal data)
- Confusing statistical significance with practical importance
- Not correcting for multiple comparisons

## Key References
- Shadish, Cook & Campbell (2002). *Experimental and Quasi-Experimental Designs*
- Creswell & Creswell (2023). *Research Design* (6th ed)
- Cohen (1988). *Statistical Power Analysis*
- Montgomery (2019). *Design and Analysis of Experiments* (10th ed)
- Yin (2018). *Case Study Research* (6th ed)

---

**Version**: 1.0
**Expertise Level**: Intermediate to Advanced
**Estimated Learning Time**: 100-200 hours
