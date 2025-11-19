# Research Writing Standards
## Elite Professional Scientific Communication

### Philosophy
Based on:
- **Nature/Science/Cell** editorial guidelines
- **APA Publication Manual** (7th edition)
- **ICMJE** (International Committee of Medical Journal Editors)
- **Google Developer Documentation Style Guide**
- **NIH/NSF grant writing best practices**

---

## Core Principles

### 1. Clarity and Precision
- Use precise, unambiguous language
- Define technical terms on first use
- Avoid jargon when plain language suffices
- One idea per sentence, one topic per paragraph

### 2. Objectivity and Accuracy
- Present data honestly, without spin
- Acknowledge limitations and uncertainties
- Distinguish observations from interpretations
- Report negative results

### 3. Conciseness
- Eliminate redundancy
- Use active voice (70%+ of sentences)
- Avoid nominalizations ("the measurement of" → "measuring")
- Delete unnecessary qualifiers ("very," "quite," "rather")

### 4. Structure and Logic
- Follow IMRAD structure (Introduction, Methods, Results, Discussion)
- Use signposting (topic sentences, transitions)
- Maintain parallel structure
- Build arguments logically

---

## Document Types

### Research Papers

**Abstract** (150-300 words):
- Background: 1-2 sentences (what problem?)
- Methods: 2-3 sentences (how did you address it?)
- Results: 3-4 sentences (what did you find?)
- Conclusion: 1-2 sentences (what does it mean?)
- No citations, no abbreviations (except standard units)

**Introduction**:
- Funnel structure: broad → specific → research question
- Establish importance (why should readers care?)
- Review relevant literature (cite key papers, not exhaustive)
- Identify gap (what's unknown or unclear?)
- State objectives and hypotheses (what you aimed to do)
- Length: 2-4 pages (double-spaced)

**Methods**:
- Sufficient detail for replication
- Subheadings for organization (Study Design, Participants, Procedures, Analysis)
- Equipment: manufacturer, model, location (e.g., "Agilent 1260 HPLC, Santa Clara, CA")
- Software: name, version, source (e.g., "R v4.3.0, R Core Team, 2023")
- Statistics: tests used, alpha level, power (if applicable)
- Ethics: IRB approval, informed consent, registration (ClinicalTrials.gov)

**Results**:
- Present findings objectively (no interpretation yet)
- Follow logical sequence (not chronological order of experiments)
- Use tables/figures for complex data (not text repetition)
- Report statistics: "t(28) = 3.45, p = .002, d = 0.82" (include effect sizes)
- All p-values: exact values (not "p < .05"), unless p < .001

**Discussion**:
- Reverse funnel: specific → broad implications
- Restate main findings (1 paragraph)
- Interpret results (what do they mean?)
- Compare to literature (consistent? contradictory? why?)
- Address limitations (be forthright)
- Suggest future directions (specific, actionable)
- Conclusion: broader impact, take-home message

**References**:
- Use reference manager (Zotero, Mendeley, EndNote)
- Follow journal style exactly (APA, ACS, Vancouver, etc.)
- Cite primary sources, not reviews (for key claims)
- Include DOIs

### Grant Proposals

**Specific Aims** (1 page):
- Opening paragraph: significance, innovation, impact
- 2-4 specific aims: hypothesis-driven, testable, achievable
- Expected outcomes and impact

**Research Strategy** (6-12 pages, NIH format):
- **Significance**: Why important? Gap in knowledge? Impact potential?
- **Innovation**: What's novel? Technology? Approach? Conceptual framework?
- **Approach**: For each aim:
  - Rationale and feasibility
  - Experimental design (controls, sample size, power)
  - Expected results and interpretation
  - Potential problems and alternative approaches
  - Timeline (Gantt chart)

**References Cited**: Recent, relevant, 30-50 citations

### Technical Reports

**Executive Summary** (1-2 pages):
- Objectives, methods (brief), key findings, recommendations
- Standalone document (readers may only read this)

**Body**:
- Introduction: context, objectives, scope
- Methods: detailed, reproducible
- Results: tables, figures, data
- Discussion: interpretation, implications
- Conclusions: summary, recommendations
- Appendices: raw data, detailed protocols, calculations

---

## Style Guidelines

### Voice and Tense

**Active vs Passive**:
- Prefer active: "We measured" (not "Measurements were taken")
- Passive acceptable: "Samples were stored at -80°C" (focus on samples, not who stored them)

**Tense**:
- Introduction: present (established facts), past (previous studies)
- Methods: past ("We collected samples")
- Results: past ("Levels increased significantly")
- Discussion: present (interpretations), past (your study), future (implications)

### Person

**First person acceptable**:
- "We hypothesized" (clearer than "It was hypothesized")
- "Our results suggest" (ownership, clarity)
- Avoid excessive "I/we" (focus on science, not authors)

### Numbers and Units

**Numerals vs Words**:
- Use numerals: 0-9 with units (5 mL, 3 weeks), 10 and above (15 participants)
- Use words: zero, one (when no units), at start of sentence

**Units**:
- SI units (meters, kilograms, seconds)
- Space between number and unit: "5 mg" (not "5mg")
- Use scientific notation: 3.2 × 10⁻⁵ (not 0.000032)
- Temperature: 37°C or 310 K (no degree symbol with Kelvin)

**Statistics**:
- Italicize statistical symbols: p, t, F, r, R², n, M, SD
- Report: M = 23.4, SD = 5.2, or mean ± SD: 23.4 ± 5.2
- Confidence intervals: 95% CI [18.3, 28.5]

### Abbreviations

**First use**: spell out with abbreviation in parentheses
- "polymerase chain reaction (PCR)"
- Use abbreviation thereafter

**Don't abbreviate**:
- Short terms (4 letters or less, unless very common like DNA, RNA)
- Terms used fewer than 3 times

**Plural**: add lowercase "s" (PCRs, not PCR's)

### Tables and Figures

**Tables**:
- Number sequentially (Table 1, Table 2)
- Title above table (descriptive, standalone)
- Notes below table (abbreviations, statistics)
- Horizontal lines only (no vertical lines)
- Align numbers on decimal point

**Figures**:
- Number sequentially (Figure 1, Fig. 1 in text)
- Caption below figure (description + key findings)
- High resolution (300+ dpi for print)
- Colorblind-friendly palettes (viridis, ColorBrewer)
- Label axes with units
- Error bars: specify (SE, SD, 95% CI)

**Placement**: After first mention in text, or at end (journal-dependent)

---

## Reporting Standards (EQUATOR Network)

### Clinical Trials: CONSORT
- Flow diagram (enrollment → allocation → analysis)
- Report all outcomes (primary and secondary)
- Intention-to-treat analysis
- Trial registration number

### Observational Studies: STROBE
- Study design, setting, participants
- Variables, data sources, bias mitigation
- Statistical methods, subgroup analyses
- Flow diagram for cohort studies

### Systematic Reviews: PRISMA
- Flow diagram (identification → screening → included)
- Search strategy (databases, terms, dates)
- Inclusion/exclusion criteria
- Risk of bias assessment
- Meta-analysis methods (if applicable)

### Animal Research: ARRIVE
- Sample size calculation
- Randomization and blinding
- Humane endpoints
- Statistical methods

### Qualitative Research: COREQ
- Researcher characteristics and reflexivity
- Study design (sampling, data collection)
- Analysis and findings (coding, themes, quotations)

---

## Common Errors to Avoid

### Language

**Wordiness**:
- ❌ "Due to the fact that" → ✅ "Because"
- ❌ "In order to" → ✅ "To"
- ❌ "A majority of" → ✅ "Most"

**Vague language**:
- ❌ "Data suggests" → ✅ "Data suggest" (data is plural)
- ❌ "Very significant" → ✅ "Significant" (don't exaggerate)
- ❌ "Quite interesting" → ✅ Delete (let readers judge)

**Misused words**:
- "Significant" = statistically significant (not "important")
- "Compared to" = likeness; "Compared with" = differences
- "While" = temporal; "Although/Whereas" = contrast

### Logic

**Circular reasoning**:
- ❌ "The high correlation is due to the strong relationship"

**Overinterpretation**:
- ❌ Correlation ≠ causation
- ❌ "Proved" (use "supported," "consistent with")

**Insufficient evidence**:
- ❌ Citing one paper as definitive
- ❌ Ignoring contradictory evidence

### Statistics

**P-value misinterpretation**:
- ❌ "p = 0.05 means 95% probability hypothesis is true"
- ✅ "p = 0.05 means 5% chance of observing this result if null is true"

**Missing information**:
- Always report: test statistic, df, p-value, effect size, CI
- Not just: "Results were significant (p < .05)"

---

## Revision Checklist

### Structure
- [ ] Clear research question stated
- [ ] Logical flow (intro → methods → results → discussion)
- [ ] Figures/tables referenced in text
- [ ] Supplementary materials mentioned

### Clarity
- [ ] Abstract standalone and accurate
- [ ] Methods reproducible
- [ ] Results clearly presented (no interpretation)
- [ ] Discussion interpretation-focused (no new results)

### Accuracy
- [ ] All citations accurate and formatted correctly
- [ ] Numbers consistent across text, tables, figures
- [ ] Statistics reported completely
- [ ] Limitations acknowledged

### Concision
- [ ] Every sentence necessary
- [ ] No redundancy between abstract/intro/discussion
- [ ] Tables/figures efficient (not duplicating text)

### Style
- [ ] Active voice predominant
- [ ] Tense consistent and appropriate
- [ ] Abbreviations defined at first use
- [ ] Reporting guidelines followed (CONSORT, STROBE, etc.)

---

## Tools

**Writing**:
- Overleaf (collaborative LaTeX)
- Google Docs (track changes, comments)
- Microsoft Word (track changes)

**Grammar/Style**:
- Grammarly (grammar, clarity)
- Hemingway Editor (readability)
- ProWritingAid (style)

**Citation Management**:
- Zotero (open-source, browser integration)
- Mendeley (PDF annotation)
- EndNote (institutional standard)
- Paperpile (Google Docs integration)

**Readability**:
- Target: 12th grade level (Flesch-Kincaid)
- Check: readability-score.com

---

## Journal-Specific Formatting

**Nature**:
- 3000-word limit (excluding methods)
- 6-8 display items (figures/tables)
- References: numbered, up to 50

**Science**:
- 2500-word limit
- 5-6 display items
- References: numbered, up to 40

**PLOS ONE**:
- No word limit
- No display item limit
- References: numbered, unlimited

**Always check**: journal's "Instructions for Authors"

---

## References

- APA Publication Manual (7th edition)
- Scientific Style and Format (CSE, 8th edition)
- Strunk & White: "The Elements of Style"
- Sword: "Stylish Academic Writing"
- Pinker: "The Sense of Style"
- EQUATOR Network: equator-network.org

---

**Version**: 1.0
**Last Updated**: 2025-11-19
