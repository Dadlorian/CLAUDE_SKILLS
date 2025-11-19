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

## Detailed Methodology Examples

### RCT Protocol Example (Clinical Trial)
**Study**: Testing a new antihypertensive drug

**Phase 1: Question Formulation**
- Population: Adults age 40-75 with hypertension (BP ≥140/90)
- Intervention: Drug X 50mg daily
- Comparison: Placebo
- Outcome: Change in systolic BP at 12 weeks
- PICO: "Does Drug X reduce BP more than placebo in hypertensive adults?"

**Phase 2: Design & Power Analysis**
- Design: Double-blind, parallel-group RCT
- Primary outcome: Mean systolic BP change from baseline to week 12
- Expected effect: 15 mmHg reduction (Drug X) vs 5 mmHg (placebo) = 10 mmHg difference
- Effect size (Cohen's d): d = (15-5)/12 = 0.833 (large)
- Power analysis: G*Power
  - α = 0.05 (two-tailed), Power = 0.90, d = 0.833
  - N = 58 per group → 116 total (accounting for 10% dropout: 130 total)

**Phase 3: Randomization & Blinding**
- Randomization: Stratified block randomization (gender, age group)
- Blinding: Double-blind (patients & investigators)
- Random number generation: Sealed envelopes, independent allocation
- Primary analysis: Intention-to-treat (ITT) + Per-protocol sensitivity

### Qualitative Research Example (Grounded Theory)
**Study**: How diabetes patients adapt to dietary restrictions

**Data Collection**:
- Sample: 20-30 patients (diabetes >1 year)
- Sampling: Theoretical sampling (continue until saturation)
- Method: In-depth interviews (60-90 minutes)
- Recording: Audio-recorded, professionally transcribed

**Coding Process**:
1. **Open Coding** (line-by-line analysis):
   - Identify concepts: "Denial," "Discovery," "Adaptation," "Acceptance"
   - Create code labels for recurring themes

2. **Axial Coding** (relate codes to categories):
   - Category: "Coping Mechanisms"
   - Subcategories: Emotional (denial → acceptance), Behavioral (dietary changes), Social (family support)
   - Conditions: Triggered by diagnosis, influenced by family, healthcare provider support

3. **Selective Coding** (integration into theory):
   - Core category: "Journey to Dietary Self-Management"
   - Narrative: Patients move through phases of denial, struggle, adaptation, and mastery
   - Outcomes: Self-efficacy, quality of life, adherence

**Example Open Code**:
```
Quote: "At first, I just couldn't give up bread. It felt impossible."
Code: Resistance to Change
Memo: Emotional barrier to dietary modification; food as comfort
```

### Mixed Methods Example (Convergent Design)
**Study**: Effectiveness of a new diabetes educational program

**Quantitative Component**:
- RCT: 200 patients (100 intervention, 100 control)
- Outcomes: HbA1c, blood glucose, diabetes knowledge test
- Timeline: 3 months

**Qualitative Component**:
- In-parallel: 15 intervention patients interviewed about experiences
- Timing: 3-month follow-up (same time as RCT assessment)
- Focus: What worked, what didn't, barriers, facilitators

**Integration**:
- Quantitative shows HbA1c decreased by 1.2% (statistically significant)
- Qualitative reveals: Patients appreciated peer support but found group meetings hard to attend
- Merged interpretation: Program effective, but delivery method needs adjustment for accessibility

## Advanced Statistical Techniques

### Structural Equation Modeling (SEM)
**When to use**: Testing complex pathways with latent variables
**Example**: How does self-efficacy (latent variable, measured by 5 items) influence exercise adherence → fitness outcomes?

**Steps**:
1. Specify measurement model (which items measure self-efficacy?)
2. Specify structural model (paths between constructs)
3. Fit model (lavaan in R)
4. Evaluate fit (CFI >0.95, RMSEA <0.06)
5. Interpret path coefficients and indirect effects

### Multilevel Modeling
**When to use**: Nested data (students within schools, repeated measures)
**Example**: Testing a classroom-based intervention
- Level 1: Individual student outcomes
- Level 2: School effects (school funding, class size)
- Partition variance: How much is student-level vs school-level?

### Propensity Score Methods
**When to use**: Observational data with confounding (can't do RCT)
**Example**: Comparing outcomes between antidepressant users vs non-users
- Calculate propensity score (probability of receiving treatment)
- Match/stratify/weight on propensity score
- Compare outcomes between balanced groups
- Result: More credible causal inference from observational data

## Open Science & Reproducibility

### Pre-Registration
**Why**: Prevent p-hacking, demonstrate rigor
**Where**: Open Science Framework (osf.io) or AsPredicted
**What to register**:
- Primary and secondary hypotheses
- Study design, sample size, power analysis
- Exclusion/inclusion criteria
- Planned analyses (not results!)
- Timeline

**Benefits**:
- Distinguish confirmatory vs exploratory analyses
- Published as "pre-registered" study (more credible)
- Can be made public at publication or kept private until analysis

### Data & Code Sharing
**Best Practices**:
- Share raw data (de-identified) in trusted repository
- Share analysis code (R/Python scripts) on GitHub or Zenodo
- Include README (what each file does)
- License data (CC-BY) and code (MIT/GPL)
- Example: GitHub repo linked to OSF, both linked to publication

**Benefits**:
- Transparency: Others can verify claims
- Reusability: Others can apply methods to new data
- Impact: Cited more, collaborations, funding

## Common Analysis Mistakes (and How to Avoid)

### P-Hacking / Multiple Comparisons
**Mistake**: Test 100 hypotheses, report only p<.05 ones
**Solution**:
- Pre-register hypotheses
- Correct for multiple testing (Bonferroni, FDR, or pre-specify primary outcome)
- Disclose all hypotheses tested
- Example: If testing 20 hypotheses, need p<.0025 (0.05/20) for significance

### Underpowered Studies
**Mistake**: Small sample, high Type II error (false negatives)
**Solution**:
- Do power analysis before study (not after!)
- Use "power=0.90" (not 0.80)
- Report actual achieved power in results
- Interpret non-significant results cautiously

### Confounding
**Mistake**: Attribute causation to treatment when confounder responsible
**Example**: Vitamin supplement → better health (but supplement users also exercise more)
**Solution**:
- Control for confounders in analysis (regression, ANCOVA)
- Match/stratify on confounders
- Use instrumental variables or Mendelian randomization
- Discuss limitations

### Small Effect Sizes Reported as Meaningful
**Mistake**: p<.001 but d=0.1 (tiny effect)
**Solution**:
- Always report effect sizes
- Cohen's guidelines: d=0.2 (small), 0.5 (medium), 0.8 (large)
- Discuss practical significance, not just statistical significance
- In clinical context: What difference matters to patients?

## Reporting & Publication

### CONSORT Checklist (Randomized Trials)
Essential items to report:
- Trial design (parallel, crossover, factorial)
- Participants: Inclusion/exclusion criteria, where recruited
- Randomization: Sequence generation, allocation concealment, blinding
- Blinding: Who was blinded (participants, providers, assessors)
- Results: Participant flow (consort diagram), baseline characteristics, primary/secondary outcomes
- Ancillary: Harms, subgroup analyses

### STROBE Checklist (Observational Studies)
Adapted CONSORT for non-randomized studies:
- Study design (cohort, case-control, cross-sectional)
- Setting, participants, variables
- Bias reduction (matching, adjustment)
- Results: Sample characteristics, unadjusted/adjusted estimates

### PRISMA Checklist (Meta-Analyses)
- Protocol registration
- Search strategy (databases, date ranges)
- Study selection (criteria, flow diagram)
- Data extraction & quality assessment
- Synthesis: Forest plots, heterogeneity, publication bias

## Research Ethics

### Institutional Review Board (IRB) Process
**Needed for studies involving human subjects**

1. **Protocol Submission**:
   - Scientific background, specific aims
   - Detailed methods, inclusion/exclusion criteria
   - Informed consent form
   - Risk-benefit analysis
   - Data privacy & security plan

2. **Review Categories**:
   - **Exempt**: Minimal risk (surveys, secondary data)
   - **Expedited**: Minor risks, quick review
   - **Full board**: Complex risks, longer process

3. **Timeline**: 2-8 weeks typical

### Informed Consent Elements
- Purpose, procedures, duration
- Foreseeable risks & benefits
- Right to withdraw
- Confidentiality & data protection
- Contact for questions/problems
- Voluntary participation statement

## Tools & Tutorials

**Statistical Software Tutorials**:
- R: DataCamp, Coursera (Johns Hopkins Data Science)
- Python: Kaggle, Real Python, YouTube tutorials
- SPSS: Video tutorials (youtube.com/SPSSbyExample)

**Design Resources**:
- EQUATOR Network (equator-network.org): Reporting guidelines
- Cochrane Handbook: For systematic reviews & meta-analysis
- Campbell Collaboration: For social science reviews

**Open-Access Journals**:
- PLOS (PLOS Medicine, PLOS ONE)
- Frontiers (open peer review)
- eLife (selective, high quality)

## Software Mastery for Research

### R Programming for Statistics

**Key packages**:
- **tidyverse**: Data wrangling (dplyr, ggplot2)
- **lme4**: Mixed effects (multilevel) models
- **lavaan**: Structural equation modeling (SEM)
- **meta**: Meta-analysis
- **survival**: Survival analysis (Kaplan-Meier, Cox)

**Workflow Example**:
```r
library(tidyverse)
library(lme4)

# Load data
data <- read.csv('patient_data.csv')

# Exploratory analysis
data %>%
  group_by(treatment) %>%
  summarise(mean_outcome = mean(value),
            sd = sd(value),
            n = n())

# Mixed model (accounting for clustering within hospitals)
model <- lmer(outcome ~ treatment + (1 | hospital), data = data)
summary(model)

# Visualize
ggplot(data, aes(x = treatment, y = outcome, color = hospital)) +
  geom_boxplot() +
  theme_minimal() +
  labs(title = "Treatment Effect by Hospital")
```

### Python for Data Science

**Key libraries**:
- **pandas**: Data manipulation
- **numpy**: Numerical computation
- **scipy**: Statistical functions
- **scikit-learn**: Machine learning
- **matplotlib/seaborn**: Visualization

## Interpreting & Visualizing Results

### Effect Size Interpretation

**Cohen's d Guidelines**:
```
d = 0.2 → Small effect (meaningful at population level)
d = 0.5 → Medium effect (noticeable effect)
d = 0.8 → Large effect (obvious difference)
d > 1.0 → Very large effect
```

**Odds Ratio (OR) Interpretation**:
- OR = 1.0 → No difference
- OR = 1.5 → 50% higher odds
- OR = 2.0 → 2x higher odds (doubling)
- OR = 0.5 → 50% lower odds

### Visualization Best Practices

**Good Figures Include**:
- Clear title + axis labels
- Appropriate scale (starts at 0 if comparing groups)
- Error bars (SD, SEM, or 95% CI)
- Sample size (n) notation
- Caption explaining what shown

**Poor Visualization Examples**:
- 3D pie charts (hard to read, misleading angles)
- Dual y-axes (can exaggerate differences)
- Chartjunk (decorative elements)
- Too many categories without grouping

## Transparency & Reproducibility Checklist

**Before Publication**:
- [ ] Methods detailed enough for replication
- [ ] All analyses pre-specified (or clearly marked exploratory)
- [ ] Code available (GitHub or supplementary)
- [ ] Raw data available or justification for restriction
- [ ] Conflicts of interest disclosed
- [ ] Funding sources listed
- [ ] Effect sizes & confidence intervals reported
- [ ] Sample size/power analysis reported
- [ ] Protocol pre-registered (where applicable)
- [ ] Results replicated in independent sample (where possible)

## Research Ethics - Additional Considerations

### Data Privacy & Security

**HIPAA Compliance** (US healthcare):
- De-identify data (remove 18 identifiers)
- Encrypt data in transit & at rest
- Limit access to research team only
- Secure destruction when study ends

**GDPR Compliance** (EU):
- Obtain explicit consent
- Right to access your data
- Right to be forgotten (deletion)
- Data processing agreements with vendors
- Report breaches within 72 hours

### Research Integrity

**Authorship Guidelines** (ICMJE):
- Substantial contributions to conception/design OR data acquisition/analysis
- Drafting or critical revision of manuscript
- Final approval of version
- Agreement to be accountable for accuracy

**Data Retention** (varies by funder):
- NIH/NSF: 3-5 years minimum
- Clinical trials: 5-10 years
- Some fields: 20+ years
- Document retention plan

---

**Version**: 2.0 (Expanded)
**Expertise Level**: Intermediate to Advanced
**Estimated Learning Time**: 120-200 hours
**Total Content**: 450+ lines of comprehensive material
