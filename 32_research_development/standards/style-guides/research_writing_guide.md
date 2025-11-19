# Research Writing Guide

## Overview

This guide establishes standards for scientific writing in research and development contexts, drawing from leading journal publishers, academic institutions, and international reporting standards.

**Primary References:**
- Nature Research: Author Guidelines (2024)
- Science Magazine: Writing Standards
- APA Publication Manual (7th Edition, 2020)
- ICMJE (International Committee of Medical Journal Editors) Recommendations
- EQUATOR Network Reporting Guidelines (CONSORT, STROBE, PRISMA)
- The Chicago Manual of Style (17th Edition)

**Adoption by Industry Leaders:**
- Google Research, DeepMind: Follow ICMJE and Nature guidelines
- Meta AI Research: APA 7th + venue-specific formatting
- Amazon Science: IEEE + Nature Research standards
- Microsoft Research: Venue-specific + APA guidelines

---

## Table of Contents

1. [Document Structure](#document-structure)
2. [Abstract Writing](#abstract-writing)
3. [Introduction Standards](#introduction-standards)
4. [Methods & Materials](#methods--materials)
5. [Results Presentation](#results-presentation)
6. [Discussion & Conclusions](#discussion--conclusions)
7. [Statistical Reporting](#statistical-reporting)
8. [Figures & Tables](#figures--tables)
9. [Citations & References](#citations--references)
10. [Supplementary Materials](#supplementary-materials)
11. [Ethical Reporting](#ethical-reporting)
12. [Language & Style](#language--style)

---

## Document Structure

### IMRaD Format (Introduction, Methods, Results, and Discussion)

The gold standard for scientific papers, mandated by:
- Nature journals
- Science and Science family journals
- PLOS journals
- Most Elsevier, Springer, and Wiley journals

**Standard Structure:**
```
1. Title
2. Author list and affiliations
3. Abstract
4. Keywords (3-6 terms)
5. Introduction
6. Methods/Materials and Methods
7. Results
8. Discussion
9. Conclusions (may be part of Discussion)
10. Acknowledgments
11. Author Contributions
12. Conflicts of Interest
13. Funding
14. Data Availability Statement
15. References
16. Supplementary Materials (separate file)
```

### Title Standards

**Nature Guidelines:**
- Maximum 20 words (preferably 15)
- Avoid abbreviations, jargon, and questions
- Be specific and descriptive
- No "Study of..." or "Observations on..."

**Examples:**

✅ **Good:**
- "CRISPR-Cas9 gene editing restores dystrophin expression in mdx mice"
- "Machine learning predicts protein structure from amino acid sequences"
- "Global patterns of nitrogen deposition from satellite observations"

❌ **Bad:**
- "A Study of Gene Editing in Mice" (vague, contains "Study of")
- "ML for Proteins" (abbreviations, too brief)
- "Can Satellites Detect Nitrogen?" (question format)

### Author List

**ICMJE Authorship Criteria** (ALL must be met):
1. Substantial contributions to conception/design OR acquisition/analysis/interpretation
2. Drafting the work OR revising it critically for important intellectual content
3. Final approval of the version to be published
4. Agreement to be accountable for all aspects of the work

**Format:**
```
FirstName LastName¹*, FirstName LastName²†, FirstName LastName¹

¹Department, Institution, City, State/Province, Postal Code, Country
²Department, Institution, City, State/Province, Postal Code, Country

*Corresponding author: email@institution.edu
†These authors contributed equally
```

**CRediT Taxonomy** (Contributor Roles Taxonomy):
- Conceptualization
- Methodology
- Software
- Validation
- Formal analysis
- Investigation
- Resources
- Data curation
- Writing - original draft
- Writing - review & editing
- Visualization
- Supervision
- Project administration
- Funding acquisition

---

## Abstract Writing

### Structured Abstract (Required by most medical journals)

**CONSORT Format** (Clinical trials):
```
Background: [1-2 sentences]
Methods: [3-4 sentences]
Results: [4-5 sentences with key numbers]
Conclusions: [1-2 sentences]
Trial Registration: [Registry name and number]
```

**Example:**
```
Background: Alzheimer's disease affects 50 million people worldwide, with limited
therapeutic options. We evaluated the efficacy of XYZ-123, a novel BACE1 inhibitor.

Methods: In this randomized, double-blind, placebo-controlled trial, we assigned
1,200 patients with mild-to-moderate Alzheimer's disease to receive either XYZ-123
(150 mg daily) or placebo for 78 weeks. The primary endpoint was change in CDR-SB
score from baseline to week 78.

Results: Mean CDR-SB score increased by 1.2 points in the XYZ-123 group versus
1.9 points in the placebo group (difference, -0.7; 95% CI, -1.1 to -0.3; P=0.001).
Serious adverse events occurred in 24% of the XYZ-123 group and 23% of the placebo
group. Brain imaging showed 15% reduction in amyloid-β plaques (P<0.001).

Conclusions: XYZ-123 modestly slowed cognitive decline in Alzheimer's disease over
78 weeks, with an acceptable safety profile. Further studies are needed to assess
long-term efficacy.

Trial Registration: ClinicalTrials.gov NCT12345678
```

### Unstructured Abstract (Most science journals)

**Requirements:**
- 150-250 words (Nature: 150-200, Science: <125)
- Single paragraph
- No citations or abbreviations (except standard units)
- Include: Background (1-2 sentences), key methods, main results (with numbers), conclusions

**Example:**
```
The global nitrogen cycle has been dramatically altered by human activities, with
consequences for climate, biodiversity, and human health. However, the spatial and
temporal patterns of nitrogen deposition remain poorly characterized. Here we use
satellite observations of tropospheric NO₂ columns from 2005-2020 to estimate
global nitrogen deposition at 0.1° resolution. We find that global nitrogen
deposition increased by 23% over this period, from 128 Tg N/year to 157 Tg N/year,
driven primarily by agricultural expansion in South and East Asia. Hotspots of
deposition (>50 kg N/ha/year) expanded by 3.2 million km², now affecting 18% of
global biodiversity hotspots. Machine learning models trained on surface
measurements achieved r²=0.84 in cross-validation. Our results provide the first
high-resolution global assessment of nitrogen deposition trends and reveal that
current mitigation efforts are insufficient to prevent widespread ecological impacts.
```

### Abstract Checklist

- [ ] Within word limit
- [ ] No citations
- [ ] Abbreviations defined on first use (or avoided)
- [ ] Specific numerical results included
- [ ] Statistical significance reported (p-values or confidence intervals)
- [ ] Conclusion addresses the main question
- [ ] Standalone (understandable without reading full paper)
- [ ] Active voice where possible
- [ ] Past tense for completed actions, present for conclusions

---

## Introduction Standards

### Structure (Funnel Approach)

**Four-paragraph model** (recommended by Nature):

1. **Broad context** (2-3 sentences)
   - What is the general field?
   - Why does this field matter?

2. **Specific problem** (3-4 sentences)
   - What is unknown or controversial?
   - What are the current limitations?
   - Brief review of key prior work

3. **Gap and opportunity** (2-3 sentences)
   - What specific gap does this study address?
   - Why is this gap important?

4. **Study overview** (2-3 sentences)
   - What did you do?
   - What did you find?
   - Why is it important?

### Example Introduction (Excerpt)

```
Neurodegenerative diseases affect over 50 million people worldwide, with prevalence
expected to triple by 2050 [1]. Alzheimer's disease (AD) accounts for 60-80% of cases,
characterized by progressive cognitive decline and accumulation of amyloid-β plaques
and neurofibrillary tangles [2]. Despite intensive research, there are no disease-
modifying treatments that substantially slow progression.

Current therapeutic strategies target amyloid-β or tau pathology, based on the amyloid
cascade hypothesis [3,4]. However, over 99% of clinical trials for AD have failed [5],
raising questions about these targets. Recent evidence suggests that neuroinflammation,
mediated by microglia, plays a central role in disease pathogenesis [6-8]. Activated
microglia can adopt both pro-inflammatory (M1) and anti-inflammatory (M2) phenotypes,
with M1 microglia promoting neuronal damage through release of cytokines and reactive
oxygen species [9]. Several genetic risk factors for AD, including TREM2 and CD33, are
expressed in microglia and regulate their activation state [10,11].

A major obstacle to targeting neuroinflammation therapeutically is the inability to
monitor microglial activation in living patients. Positron emission tomography (PET)
tracers for the 18-kDa translocator protein (TSPO) have shown promise but lack
specificity for M1 versus M2 activation states [12,13]. New imaging tools that can
distinguish beneficial from harmful microglial activation are urgently needed.

Here we report the development and validation of [¹¹C]PK11195-M1, a novel PET tracer
with selective binding to M1-activated microglia. Using a combination of in vitro
binding assays, autoradiography in AD mouse models, and PET imaging in 24 AD patients,
we demonstrate that [¹¹C]PK11195-M1 specifically labels pro-inflammatory microglia and
correlates with cognitive decline. This tracer may enable stratification of patients
for anti-inflammatory therapies and provide a pharmacodynamic biomarker for clinical
trials.
```

### Introduction Best Practices

**Length:**
- Short papers (<3000 words): 400-600 words
- Regular articles: 600-1000 words
- Reviews: 1000-1500 words

**Citations:**
- Cite primary sources, not reviews (unless discussing review findings)
- Use recent literature (<5 years for 60-70% of citations)
- Include key historical papers that established the field
- Cite diverse sources (not just own work or collaborators)

**Common Errors to Avoid:**
- ❌ Starting too broadly ("Since the beginning of time...")
- ❌ Excessive literature review (save for Discussion)
- ❌ Not stating the specific gap being addressed
- ❌ Burying the study question
- ❌ Using future tense ("We will show...") instead of past ("We found...")

---

## Methods & Materials

### General Principles

**ICMJE Requirements:**
- Sufficient detail for replication
- Identify equipment by manufacturer name and location
- Report software versions
- Describe statistical methods
- State ethical approvals

**Good Laboratory Practice (GLP) Standards:**
- Standard operating procedures (SOPs) referenced
- Reagent lot numbers recorded
- Calibration of equipment documented
- Quality control measures described

### Subsection Organization

```markdown
## Methods

### Study Design
[Overview of experimental design, controls, blinding, randomization]

### Materials
[Reagents, kits, equipment with manufacturers and catalog numbers]

### Sample Collection and Processing
[Detailed protocols]

### Analytical Methods
[Step-by-step procedures]

### Data Analysis
[Software, statistical tests, significance thresholds]

### Quality Control
[QC measures, validation experiments]
```

### Equipment and Reagent Reporting

**Format:**
```
Equipment: Manufacturer (City, State/Province, Country), Model Number
Reagents: Chemical Name (Manufacturer, Catalog Number, Lot Number if relevant)
Software: Software Name (Publisher, Version Number, URL if open-source)
```

**Examples:**

✅ **Good:**
```
DNA was extracted using the DNeasy Blood & Tissue Kit (Qiagen, Hilden, Germany,
Cat. No. 69506) according to the manufacturer's protocol with the following
modifications: incubation time was extended to 3 hours and elution volume was
reduced to 30 μL. DNA concentration was measured using a NanoDrop 2000c
spectrophotometer (Thermo Fisher Scientific, Wilmington, DE, USA). PCR
amplification was performed using Q5 High-Fidelity DNA Polymerase (New England
Biolabs, Ipswich, MA, USA, Cat. No. M0491).
```

❌ **Bad:**
```
DNA was extracted using a kit and measured. PCR was then performed.
```

### Statistical Methods Section

**Required Elements (per ICMJE):**
- Software package and version
- Statistical tests used
- Significance threshold (α level)
- Adjustments for multiple comparisons
- Sample size justification (if applicable)
- Handling of missing data

**Example:**
```
### Statistical Analysis

All statistical analyses were performed using R version 4.3.1 (R Core Team, 2023)
with packages tidyverse (v2.0.0), lme4 (v1.1-34), and emmeans (v1.8.7). Data are
presented as mean ± standard deviation (SD) unless otherwise specified.

For comparisons between two groups, we used two-sided Student's t-tests for normally
distributed data (assessed by Shapiro-Wilk test) or Mann-Whitney U tests for
non-normally distributed data. For multiple group comparisons, we used one-way ANOVA
followed by Tukey's HSD post-hoc test, with Bonferroni correction for multiple
comparisons (adjusted α = 0.05/n comparisons).

Longitudinal data were analyzed using linear mixed-effects models with random
intercepts for subjects and fixed effects for time, treatment, and their interaction.
Model assumptions were verified by visual inspection of residual plots.

Sample size was determined by power analysis (G*Power v3.1.9.7) targeting 80% power
to detect a medium effect size (Cohen's d = 0.5) at α = 0.05, resulting in n = 64
per group. We recruited 70 per group to account for ~10% attrition.

Missing data (<5% of observations) were handled using listwise deletion. Sensitivity
analyses using multiple imputation (mice package, v3.16.0) yielded consistent results.

All statistical tests were two-sided with significance threshold α = 0.05 unless
otherwise specified. Exact p-values are reported; p < 0.001 is indicated where
p-values are extremely small.
```

---

## Results Presentation

### Organization Principles

**CONSORT/STROBE Guidelines:**
1. Present results in logical sequence matching Methods
2. Report both positive and negative results
3. Include measures of precision (confidence intervals)
4. Report actual p-values, not just "significant" or "NS"
5. Avoid interpretation (save for Discussion)

### Text-Figure-Table Coordination

**Rule of Three:**
- Don't repeat the same data in text, tables, AND figures
- Choose the most effective format for each result:
  - **Text:** Simple comparisons, 1-3 values
  - **Tables:** Precise values, many variables, categorical data
  - **Figures:** Trends, distributions, relationships, complex patterns

### Reporting Numbers and Statistics

**APA 7th Edition Standards:**

**Numbers:**
- Use numerals for numbers ≥10
- Use words for numbers <10 (except units, percentages, ratios)
- Use numerals before units: "5 mg" not "five mg"

**Decimal Places:**
- Report 2 decimal places for most statistics
- Report exact p-values to 3 decimal places: "p = 0.043"
- For very small p-values: "p < 0.001" not "p = 0.000"

**Statistical Reporting Format:**

```
Mean ± SD: "The mean concentration was 45.3 ± 8.7 μg/mL"

t-test: t(df) = value, p = value
Example: "t(28) = 3.45, p = 0.002"

ANOVA: F(df1, df2) = value, p = value
Example: "F(2, 57) = 8.92, p < 0.001"

Correlation: r(df) = value, p = value
Example: "r(48) = 0.67, p < 0.001"

Chi-square: χ²(df, N = n) = value, p = value
Example: "χ²(1, N = 90) = 5.43, p = 0.020"

Confidence intervals: [lower, upper]
Example: "Mean difference = 12.4 (95% CI [8.2, 16.6])"

Effect sizes: Cohen's d, η², r²
Example: "Cohen's d = 0.8 (large effect)"
```

### Results Section Example

```
## Results

### Patient Characteristics

We enrolled 128 patients with mild-to-moderate Alzheimer's disease between January
2020 and December 2021 (Figure 1). Baseline characteristics were similar between
the treatment (n = 64) and placebo (n = 64) groups (Table 1). Mean age was 71.3 ±
7.8 years, and 58% were female. Mean MMSE score was 22.4 ± 3.1, and mean CDR-SB
score was 4.2 ± 1.8.

### Primary Outcome: Cognitive Function

At week 78, mean CDR-SB score increased by 1.2 ± 1.9 points in the treatment group
compared with 1.9 ± 2.1 points in the placebo group (between-group difference,
-0.7; 95% CI, -1.3 to -0.1; p = 0.028; Figure 2A). This represents a 37% reduction
in cognitive decline. The treatment effect was consistent across prespecified
subgroups, including age (<75 vs ≥75 years), sex, and baseline MMSE score (all
p-interactions >0.05; Figure S1).

Secondary outcomes showed concordant effects. ADAS-Cog13 scores increased by 4.2 ±
5.8 points in the treatment group versus 6.9 ± 6.4 points in placebo (difference,
-2.7; 95% CI, -4.8 to -0.6; p = 0.012). ADCS-ADL scores decreased by 3.1 ± 7.2
points in treatment versus 5.8 ± 8.1 points in placebo (difference, 2.7; 95% CI,
0.2 to 5.2; p = 0.036).

### Biomarker Analysis

PET imaging at week 78 showed a 15% reduction in cortical amyloid-β plaque burden
in the treatment group (mean SUVr change: -0.12 ± 0.18) compared with a 2%
increase in the placebo group (mean SUVr change: +0.02 ± 0.15; between-group
difference, -0.14; 95% CI, -0.20 to -0.08; p < 0.001; Figure 2B). Plasma p-tau181
levels decreased by 28% in the treatment group versus 3% in placebo (p < 0.001;
Figure 2C).

### Safety and Tolerability

Treatment-emergent adverse events occurred in 89% of the treatment group and 86%
of the placebo group (Table 2). Most were mild to moderate in severity. Serious
adverse events occurred in 24% of treatment and 23% of placebo groups (p = 0.87).
There were 4 deaths in the treatment group (cerebrovascular accident, n=2;
myocardial infarction, n=1; pneumonia, n=1) and 3 in the placebo group
(cerebrovascular accident, n=2; sepsis, n=1), none judged related to study drug.

The most common adverse events were headache (treatment 28% vs placebo 19%),
diarrhea (23% vs 17%), and dizziness (19% vs 14%). MRI monitoring revealed
amyloid-related imaging abnormalities (ARIA) in 32% of treatment versus 8% of
placebo groups (p < 0.001). ARIA-E (edema) occurred in 18% of treatment versus
3% of placebo; ARIA-H (hemorrhage) in 21% versus 6%. Most ARIA was asymptomatic
and resolved without intervention.
```

---

## Discussion & Conclusions

### Discussion Structure (Nature Recommended)

1. **Summary of key findings** (1 paragraph)
2. **Interpretation in context of existing literature** (2-3 paragraphs)
3. **Mechanisms and implications** (2-3 paragraphs)
4. **Limitations** (1 paragraph)
5. **Future directions** (1 paragraph)
6. **Conclusions** (1 paragraph, may be separate section)

### Best Practices

**Do:**
- Start with a brief restatement of main findings
- Compare with specific prior studies
- Explain unexpected results
- Be honest about limitations
- Discuss clinical/practical implications
- End with strong, justified conclusions

**Don't:**
- Introduce new results
- Repeat Methods or Results sections
- Overstate conclusions
- Ignore contradictory findings
- Use vague statements ("further research is needed")

### Limitations Section

**Required Elements:**
- Sample size or power limitations
- Generalizability constraints
- Methodological limitations
- Potential confounders not addressed
- Missing data or attrition

**Example:**
```
### Limitations

This study has several limitations. First, our sample was recruited from a single
academic medical center, potentially limiting generalizability to community settings
or diverse populations. Our cohort was predominantly White (87%) and highly educated
(mean 16 years of education), which may not reflect the broader AD population.
Second, the study duration of 78 weeks may be insufficient to assess long-term
safety and durability of treatment effects. Third, while we observed biomarker
changes consistent with target engagement, we cannot definitively establish that
amyloid-β reduction mediated the cognitive benefits. Fourth, the placebo group
showed less decline than anticipated based on historical data, which reduced
statistical power. Finally, 12% of participants discontinued treatment early,
which could introduce bias despite our intention-to-treat analysis.
```

---

## Statistical Reporting

### CONSORT Guidelines for Clinical Trials

**Required Reporting:**
- Sample size calculation with assumptions
- Randomization method
- Allocation concealment mechanism
- Blinding procedure
- Participant flow diagram (CONSORT flowchart)
- Baseline characteristics table
- Primary and secondary outcomes with effect sizes and CIs
- Harms/adverse events
- Trial registration number

### STROBE Guidelines for Observational Studies

**Required Reporting:**
- Study design in title/abstract
- Setting, locations, dates
- Eligibility criteria
- Matching criteria (case-control)
- Data sources and measurements
- Bias discussion
- Sensitivity analyses

### PRISMA Guidelines for Systematic Reviews

**Required Reporting:**
- Protocol registration
- Search strategy (full electronic search for ≥1 database)
- Study selection process
- Data extraction process
- Risk of bias assessment
- Summary measures and synthesis methods
- Publication bias assessment

### Effect Size Reporting

**Cohen's Standards:**
```
Small effect:    d = 0.2, r = 0.1, η² = 0.01
Medium effect:   d = 0.5, r = 0.3, η² = 0.06
Large effect:    d = 0.8, r = 0.5, η² = 0.14
```

**Always report:**
- Point estimate
- Measure of precision (95% CI preferred over SE)
- Effect size (standardized when possible)
- Exact p-value (not "p < 0.05")

---

## Figures & Tables

### General Principles

**Nature Figure Guidelines:**
- Figures should be understandable without reading the text
- Use color purposefully (avoid red-green combinations)
- Include scale bars and units
- Export at ≥300 DPI for publication
- Use vector formats (PDF, EPS) for line art
- Maximum width: 89 mm (single column) or 183 mm (double column)

### Figure Components

**Required Elements:**
1. **Figure number and title** (brief, descriptive)
2. **Figure legend** (detailed description)
3. **Axis labels** with units
4. **Error bars** with definition (SD, SEM, or 95% CI)
5. **Statistical annotations** (significance markers)
6. **Scale bars** (microscopy images)
7. **Sample sizes** (n values)

### Figure Legend Template

```
Figure 1. [Brief descriptive title, <10 words]

[Detailed description of what is shown, 2-5 sentences]

(A) [Description of panel A, including what is plotted, sample size, statistical test]
(B) [Description of panel B...]

[Description of symbols, colors, error bars, etc.]

[Statistical methods: "Data are presented as mean ± SD from n=3 independent
experiments. *p < 0.05, **p < 0.01, ***p < 0.001 by one-way ANOVA with Tukey's
post-hoc test."]

[Abbreviations defined]
```

### Example Figure Legend

```
Figure 2. XYZ-123 treatment reduces cognitive decline and amyloid-β burden in
Alzheimer's disease

Clinical and biomarker outcomes in patients treated with XYZ-123 (150 mg daily,
blue) or placebo (gray) for 78 weeks.

(A) Change from baseline in CDR-SB score. Higher scores indicate greater cognitive
impairment. Treatment group showed significantly less decline (mean difference
-0.7 points, 95% CI [-1.3, -0.1], p = 0.028 by linear mixed-effects model).
(B) Change in cortical amyloid-β PET SUVr. Treatment group showed significant
reduction in amyloid burden (mean difference -0.14, 95% CI [-0.20, -0.08],
p < 0.001 by two-sided t-test). (C) Plasma p-tau181 concentration. Treatment
group showed significant reduction (28% vs 3% in placebo, p < 0.001 by
Mann-Whitney U test).

Data are presented as mean ± SEM (panels A-B) or median with IQR (panel C).
Treatment group n = 64, placebo n = 64. Individual patient trajectories shown
as thin lines; group means shown as thick lines. Gray shading indicates 95% CI.

CDR-SB, Clinical Dementia Rating Scale Sum of Boxes; SUVr, standardized uptake
value ratio; p-tau181, phosphorylated tau at threonine 181; IQR, interquartile
range.
```

### Table Standards

**Table Components:**
1. Table number and title (descriptive, standalone)
2. Column headers with units
3. Row labels
4. Footnotes for abbreviations, statistical tests, significance markers
5. Horizontal lines only (no vertical lines per APA/Nature style)

### Table 1 Example (Baseline Characteristics)

```
Table 1. Baseline Characteristics of Study Participants

Characteristic                          Treatment       Placebo         p-value
                                        (n = 64)        (n = 64)
─────────────────────────────────────────────────────────────────────────────
Age, years                              71.8 ± 7.9      70.8 ± 7.7      0.47
Female sex, n (%)                       38 (59)         36 (56)         0.73
Race, n (%)                                                             0.62
  White                                 56 (88)         55 (86)
  Black or African American             5 (8)           7 (11)
  Asian                                 3 (5)           2 (3)
Education, years                        16.2 ± 2.8      15.9 ± 3.1      0.58
Body mass index, kg/m²                  26.3 ± 4.2      27.1 ± 4.6      0.31
APOE ε4 carrier, n (%)                  42 (66)         40 (63)         0.71

Cognitive assessments
  MMSE score (0-30)                     22.6 ± 3.0      22.2 ± 3.2      0.48
  CDR-SB score (0-18)                   4.1 ± 1.7       4.3 ± 1.9       0.54
  ADAS-Cog13 score (0-85)               24.8 ± 8.3      25.9 ± 9.1      0.47

Biomarkers
  Cortical amyloid-β PET SUVr           1.42 ± 0.28     1.45 ± 0.31     0.56
  Plasma p-tau181, pg/mL                28.7 ± 12.4     30.1 ± 13.8     0.54
  Hippocampal volume, cm³               5.8 ± 1.2       5.6 ± 1.3       0.39

Comorbidities, n (%)
  Hypertension                          38 (59)         42 (66)         0.45
  Diabetes mellitus                     12 (19)         15 (23)         0.53
  Hyperlipidemia                        45 (70)         48 (75)         0.54
─────────────────────────────────────────────────────────────────────────────

Data are presented as mean ± standard deviation or n (%). P-values from two-sided
t-tests (continuous variables) or chi-square tests (categorical variables). No
significant differences between groups (all p > 0.05).

MMSE, Mini-Mental State Examination; CDR-SB, Clinical Dementia Rating Scale Sum
of Boxes; ADAS-Cog13, Alzheimer's Disease Assessment Scale-Cognitive Subscale
(13-item); PET, positron emission tomography; SUVr, standardized uptake value
ratio; p-tau181, phosphorylated tau at threonine 181.
```

---

## Citations & References

### Citation Styles

**Nature (numbered):**
- In-text: superscript numbers [1], [2,3], [4-6]
- Order: by first appearance in text

**Science (numbered):**
- In-text: parenthetical numbers (1), (2, 3), (4-6)
- Order: by first appearance in text

**APA 7th (author-date):**
- In-text: (Smith, 2020), (Smith & Jones, 2020), (Smith et al., 2020)
- Order: alphabetically by first author surname

### Reference Formatting

**Journal Article (Nature style):**
```
1. Smith, J., Jones, A. B. & Wilson, C. D. Title of article in sentence case.
   Journal Name Abbrev. 123, 456-478 (2020).
```

**Journal Article (APA 7th):**
```
Smith, J., Jones, A. B., & Wilson, C. D. (2020). Title of article in sentence
case. Journal Name, 123(4), 456-478. https://doi.org/10.xxxx/xxxxx
```

**Book:**
```
Nature: Author, A. B. Book Title in Title Case (Publisher, Year).
APA: Author, A. B., & Author, C. D. (Year). Book title in sentence case
     (Edition). Publisher. https://doi.org/xxxxx
```

**Website:**
```
Nature: Author, A. B. Title of webpage. Website Name
        https://www.example.com/page (Year).
APA: Author, A. B. (Year, Month Day). Title of webpage. Website Name.
     Retrieved Month Day, Year, from https://www.example.com/page
```

**Preprint:**
```
Nature: Author, A. B. Title of preprint. Preprint at https://doi.org/xxxxx (Year).
APA: Author, A. B. (Year). Title of preprint [Preprint]. Repository Name.
     https://doi.org/xxxxx
```

### Digital Object Identifiers (DOIs)

**Best Practices:**
- Always include DOIs when available
- Use doi.org URLs: https://doi.org/10.1038/nature12345
- Don't include "doi:" label in APA 7th (was required in 6th edition)
- Crossref and DataCite are authoritative DOI registries

### Reference Management

**Recommended Tools:**
- Zotero (open source, excellent browser integration)
- Mendeley (free, good PDF annotation)
- EndNote (commercial, powerful but expensive)
- Papers (Mac-focused, good for literature review)

**Citation Style Language (CSL):**
- Open standard for citation formatting
- 10,000+ journal styles available
- Supported by Zotero, Mendeley, Papers
- Repository: https://www.zotero.org/styles

---

## Supplementary Materials

### Organization

```
Supplementary Information

Supplementary Figures
  Figure S1. [Title]
  Figure S2. [Title]
  ...

Supplementary Tables
  Table S1. [Title]
  Table S2. [Title]
  ...

Supplementary Methods
  [Extended methods, protocols, code]

Supplementary References
  [References cited only in SI]

Supplementary Data Files (separate)
  Data S1. [Description]
  Data S2. [Description]
```

### Data Availability

**Nature Requirements:**
- Describe how to access all data supporting the findings
- Deposit large datasets in public repositories
- Use persistent identifiers (DOIs)
- Specify any access restrictions

**Recommended Repositories:**
- **General:** Zenodo, Figshare, Dryad, OSF
- **Genomics:** NCBI GEO, ENA, DDBJ
- **Proteomics:** PRIDE, ProteomeXchange
- **Structural biology:** PDB, EMDB
- **Imaging:** BioImage Archive
- **Clinical trials:** ClinicalTrials.gov, EudraCT

**Data Availability Statement Template:**
```
Data Availability

The data that support the findings of this study are available from the
corresponding author upon reasonable request. Raw sequencing data have been
deposited in the NCBI Sequence Read Archive under BioProject accession number
PRJNA123456. Processed data are available at Zenodo: https://doi.org/10.5281/
zenodo.1234567. Clinical data are subject to privacy restrictions and available
upon approval from the institutional review board. Analysis code is available
at GitHub: https://github.com/username/repo.
```

### Code Availability

**Nature Requirements:**
- Provide sufficient information to reproduce computational results
- Deposit code in public repositories (GitHub, GitLab, Bitbucket)
- Use open-source licenses (MIT, GPL, Apache, BSD)
- Include documentation, dependencies, version numbers

**Example Statement:**
```
Code Availability

All analysis code is available at GitHub (https://github.com/username/
project_name, v1.0.2, https://doi.org/10.5281/zenodo.7654321). Code is
provided under the MIT License. Analysis was performed using Python 3.10.8
with packages listed in requirements.txt. Computational workflows are
documented as Jupyter notebooks in the /notebooks directory.
```

---

## Ethical Reporting

### Human Subjects Research

**Required Elements (ICMJE):**
- IRB/Ethics committee approval statement
- Informed consent statement
- ClinicalTrials.gov registration (interventional studies)
- Adherence to Declaration of Helsinki

**Example:**
```
Ethics Approval

This study was approved by the Stanford University Institutional Review Board
(Protocol #12345, approved 15 January 2020) and conducted in accordance with
the Declaration of Helsinki and Good Clinical Practice guidelines. All
participants provided written informed consent. The trial was registered at
ClinicalTrials.gov (NCT01234567) before enrollment of the first participant.
```

### Animal Research

**ARRIVE Guidelines 2.0:**
- Ethical statement and approval number
- Species, strain, sex, age, weight
- Housing and husbandry conditions
- Sample size determination
- Inclusion/exclusion criteria
- Randomization and blinding
- Humane endpoints
- Statistical methods

---

## Language & Style

### Tense Usage

**Abstract:**
- Background: Present tense
- Methods: Past tense
- Results: Past tense
- Conclusions: Present tense

**Introduction:**
- General facts: Present tense
- Prior research: Past tense
- Study objectives: Past tense

**Methods:**
- Past tense throughout

**Results:**
- Past tense throughout

**Discussion:**
- Study findings: Past tense
- Interpretation: Present tense
- Implications: Present tense

### Voice

**Preference:** Active voice > Passive voice

✅ **Active:** "We measured protein concentration using a BCA assay."
❌ **Passive:** "Protein concentration was measured using a BCA assay."

**Exception:** Methods section can use passive voice to emphasize the procedure over the actor.

### Abbreviations

**Rules:**
- Define on first use: "polymerase chain reaction (PCR)"
- Don't define if used <3 times (spell out instead)
- Don't define standard units: mL, kg, bp, kDa
- Don't start sentences with abbreviations

### Precision and Clarity

**Be specific:**
- ❌ "The temperature was high"
- ✅ "The temperature was 65°C"

**Avoid hedging:**
- ❌ "The data seem to suggest that..."
- ✅ "The data indicate that..."

**Avoid ambiguity:**
- ❌ "Subjects received drug A or B"
- ✅ "Subjects received either drug A or drug B"

---

## Checklist

Before submission, verify:

### Content
- [ ] All required sections included
- [ ] Results match methods described
- [ ] Figures and tables referenced in order
- [ ] All abbreviations defined
- [ ] All citations in reference list
- [ ] Data availability statement included
- [ ] Ethical approvals stated
- [ ] Author contributions listed
- [ ] Conflicts of interest disclosed
- [ ] Funding sources acknowledged

### Format
- [ ] Word count within limits
- [ ] Line numbering enabled (if required)
- [ ] Double-spaced (if required)
- [ ] Figures at ≥300 DPI
- [ ] Tables formatted per journal guidelines
- [ ] References formatted correctly
- [ ] Supplementary files organized

### Quality
- [ ] Spell-checked
- [ ] Grammar-checked
- [ ] Statistical reporting complete
- [ ] P-values exact (not just <0.05)
- [ ] Effect sizes reported
- [ ] Confidence intervals included
- [ ] Sample sizes stated
- [ ] Limitations discussed

---

## Additional Resources

### Style Guides
- Nature Portfolio author policies: https://www.nature.com/nature-portfolio/editorial-policies/authorship
- Science author guidelines: https://www.science.org/content/page/instructions-authors
- APA Publication Manual (7th ed.): https://apastyle.apa.org/
- Chicago Manual of Style: https://www.chicagomanualofstyle.org/

### Reporting Guidelines (EQUATOR Network)
- CONSORT (RCTs): http://www.consort-statement.org/
- STROBE (observational): https://www.strobe-statement.org/
- PRISMA (systematic reviews): http://www.prisma-statement.org/
- ARRIVE (animal research): https://arriveguidelines.org/
- STARD (diagnostic accuracy): https://www.equator-network.org/reporting-guidelines/stard/
- CHEERS (health economics): https://www.equator-network.org/reporting-guidelines/cheers/

### Training
- Nature Masterclasses: https://masterclasses.nature.com/
- Publons Academy: https://publons.com/community/academy
- AuthorAID: https://www.authoraid.info/
- EASE (European Association of Science Editors): https://ease.org.uk/

---

**Document Version:** 1.0
**Last Updated:** 2024
**Maintained By:** Research & Development Standards Committee
**Review Cycle:** Annual
