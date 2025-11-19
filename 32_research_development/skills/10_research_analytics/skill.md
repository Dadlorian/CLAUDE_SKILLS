# Research Analytics & Bibliometrics Skill

## Purpose
Master quantitative assessment of research impact using bibliometrics, citation analysis, collaboration network analysis, and responsible metrics frameworks (DORA, Leiden Manifesto). Use analytics to identify research trends, evaluate researcher/institution performance, and guide strategic research decisions.

## Core Competencies

### Bibliometric Databases & Tools
- **Web of Science**: Citation index, impact tracking, author profiles
- **Scopus**: Multidisciplinary index, larger coverage than WoS
- **PubMed**: For biomedical literature
- **Google Scholar**: Free alternative (less structured)
- **CrossRef**: Digital object identifier (DOI) metadata hub

### Citation Analysis Tools
- **VOSviewer**: Visualize citation networks, cluster analysis
- **CiteSpace**: Identify research trends, temporal evolution
- **Citavi**: Reference management with citation tracking
- **Publish or Perish**: Scrape Google Scholar for citation metrics
- **InCites**: Intelligence tool for research evaluation

### Impact Assessment Platforms
- **SciVal**: Scopus-based research evaluation
- **Essential Science Indicators (ESI)**: Highly cited researchers
- **Journal Citation Reports (JCR)**: Journal impact factors
- **Altmetric**: Alternative metrics (social media, news mentions)

### Collaboration & Network Analysis
- **Gephi**: Network visualization software
- **Pajek**: Network analysis package
- **NetworkX** (Python): Programmatic network analysis
- **Kumu.io**: Interactive network mapping

## Core Metrics & Definitions

### Citation-Based Metrics

**Citation Count**:
- Simple count of how many times paper cited by others
- Reflects influence + visibility
- Varies by field (physics citation rates >> humanities)

**h-Index** (Hirsch Index):
- Researcher has h papers with ≥h citations each
- Example: h=25 means 25 papers cited ≥25 times
- Balances productivity (paper count) + impact (citations)
- Limitation: Increases with age (favors senior researchers)

**g-Index**:
- Alternative to h-index
- g papers have ≥g² citations total (more sensitive to highly-cited papers)
- Better captures citation concentration

**i10-Index** (Google Scholar):
- Number of papers with ≥10 citations
- Simple to understand, easy to game

**Journal Impact Factor (IF)**:
- Average citations per article published in journal (previous 2 years)
- Example: Nature IF ≈ 50; typical journal IF ≈ 2-3
- Calculated as: (citations in year X to articles in X-1, X-2) / (papers published in X-1, X-2)
- Criticism: Skewed by review articles, self-citations

### Field-Normalized Metrics

**Field-Weighted Citation Impact (FWCI)**:
- Compares paper citations to field average
- FWCI = 1.0 → average impact for field
- FWCI = 2.0 → twice the field average
- Allows fair comparison across disciplines

**Relative Citation Ratio (RCR)**:
- NIH metric: paper citations / expected citations (based on NIH ICITE database)
- RCR > 1.0 → above average impact
- Accounts for citation patterns by age and field

### Alternative Metrics (Altmetrics)

**Altmetric Score**:
- Aggregates mentions: Twitter, news, blogs, Wikipedia, Reddit
- Color-coded: Gold (high), Green (medium), Orange (low), Gray (none)
- Useful for public engagement, policy impact
- Criticism: Can measure hype, not always scientific rigor

**Mendeley Saves**:
- How many researchers saved paper to their library
- Indicator of research interest in community
- Faster than citations (can be high before papers cited)

**Twitter/Social Media Engagement**:
- Retweets, likes, shares
- Indicates public interest
- Some evidence of correlation with citations (but not always)

## Detailed Analysis Workflows

### Task 1: Evaluating Researcher Impact

**Scenario**: Assessing a researcher's productivity and influence

**Method 1: Google Scholar Profile**:
1. Go to scholar.google.com
2. Search researcher name OR view their public profile
3. Metrics available:
   - Total publications
   - Total citations
   - h-index
   - i10-index
   - Citation trends (graph)

**Method 2: Scopus Author Page**:
```
Step 1: Search Scopus (scopus.com)
Step 2: Find author → Click to open author profile
Step 3: Metrics displayed:
  - Documents: Number of publications
  - Citations: Total citations to all papers
  - Citation per document: Average
  - h-index, FWCI
Step 4: Visualize:
  - Publication history (by year)
  - Document type breakdown
  - Subject areas (% of research)
  - Top cited papers
```

**Method 3: Web of Science Author Search**:
```
1. Log in to WoS (access via university/institution)
2. Advanced Search → Author search
3. Results show:
   - Publication record (researcherid.com profile)
   - Citation count
   - H-index
   - Essential Science Indicators (ESI) status
     (If in top 1%, shows "Highly Cited Researcher" badge)
```

**Interpretation Example**:
```
Dr. Jane Smith:
- 87 publications (last 10 years)
- 3,400 total citations
- h-index: 28
- i10-index: 52
- Field: Oncology

Interpretation:
- Very productive (87 papers = ~8-9/year)
- High impact (h-index 28 is excellent for oncology)
- Top 1% of oncology researchers (ESI badge)
- Average ~39 citations per paper (high for field)
```

### Task 2: Analyzing Research Trends

**Scenario**: Identify emerging topics in a field

**Workflow using CiteSpace**:
```
1. Download CiteSpace (free, Java-based)
2. Import data:
   - Export search results from Web of Science or Scopus
   - Save as .txt or .csv
3. Configure analysis:
   - Time span: 2015-2024
   - Time slice: 1 year
   - Node type: Terms/Keywords
4. Run analysis → Generates network visualization
5. Interpret:
   - Cluster 1 (red): Machine learning in drug discovery
   - Cluster 2 (blue): Immunotherapy resistance
   - Cluster 3 (green): Biomarker discovery
6. Export to Gephi for enhanced visualization
```

**Output Interpretation**:
- **Node size**: Frequency (larger = more papers on topic)
- **Edge thickness**: Co-occurrence strength (thicker = often discussed together)
- **Color**: Cluster assignment (topics related to same research area)
- **Betweenness centrality**: Topics that bridge different research areas

**Example Finding**:
"From 2015-2019, immunotherapy was mentioned in 8% of cancer papers. By 2024, it's 35% of papers. Emerging connections: immunotherapy + resistance mechanisms + biomarker discovery."

### Task 3: Institution Benchmarking

**Scenario**: Compare research output of two institutions

**Metrics to Compare**:
```
Institution A: Top University
- Total publications (2023): 2,547
- Total citations (last 5 years): 67,430
- Average FWCI: 1.8 (above field average)
- Top papers: 23 in Top 1% (field)
- Highly cited researchers: 12
- Collaboration: 45% international co-authorship

Institution B: Regional University
- Total publications (2023): 342
- Total citations (last 5 years): 4,120
- Average FWCI: 1.2 (near field average)
- Top papers: 1 in Top 1%
- Highly cited researchers: 0
- Collaboration: 15% international
```

**Conclusion**:
- Institution A: Higher productivity, higher impact (FWCI 1.8), strong international profile
- Institution B: Modest output, reasonable quality (FWCI 1.2), more domestic focus
- Strategic recommendation: Institution B should seek international collaborations

### Task 4: Journal Selection for Publication

**Scenario**: Choosing where to submit manuscript

**Factors to Consider**:
```
Journal 1: Nature
- Impact Factor: 64 (very high)
- Acceptance rate: 5% (highly selective)
- Time to decision: 8 weeks
- Audience: Broad (multidisciplinary)
- Your fit: Novel findings, methodological innovation

Journal 2: Oncogene
- Impact Factor: 9.5 (high)
- Acceptance rate: 25%
- Time to decision: 12 weeks
- Audience: Cancer researchers
- Your fit: Mechanism of action, translational potential

Journal 3: PLoS ONE
- Impact Factor: 3.2 (moderate)
- Acceptance rate: 50%
- Time to decision: 6 weeks
- Audience: Open access, multidisciplinary
- Your fit: Solid science, not groundbreaking
```

**Decision Framework**:
1. **Impact** (novelty, significance): Does it fit Journal 1? Try that first
2. **Audience fit**: Is finding relevant to Journal 2's readers? Good fit
3. **Realistic probability of acceptance**: If likely rejection, start with Journal 2
4. **Timeline**: Preprint on bioRxiv while under review (not exclusive)

## DORA & Leiden Manifesto: Responsible Metrics

### San Francisco Declaration on Research Assessment (DORA)

**Core Principles**:
1. Don't use journal impact factor to evaluate researchers
2. Use multiple indicators (not just citations)
3. Include qualitative assessment
4. Consider disciplinary differences
5. Recognize non-traditional outputs (data, code, preprints)

**Implications**:
- AVOID: "Published in Nature → Must be good researcher"
- INSTEAD: Evaluate paper content, impact, contribution

**Example DORA-Compliant Evaluation**:
```
Researcher: Dr. Bob Johnson

Metrics Used:
- h-index: 18 (moderate)
- FWCI: 1.5 (above average)
- Field-specific benchmark: Among top 25% of biologists
- Peer review of 3 papers: "Novel methods, clear presentation"
- Open science: Code/data availability: 60% of papers
- Societal impact: 2 patents filed, 1 company founded
- Teaching evaluations: 4.8/5.0

Conclusion: Solid researcher with above-average impact, good open science practices, real-world applications.
(This is BETTER than just saying "h-index=18")
```

### Leiden Manifesto for Research Metrics

**10 Principles**:
1. **Quantitative evaluation supports qualitative judgment** (not replaces)
2. **Account for disciplinary differences** (physics ≠ history)
3. **Protect excellence in science and society** (measure what matters)
4. **Respect the composite nature of metrics** (use multiple, report limitations)
5. **Open data and methods** (transparent, reproducible)
6. **Require context** (who, what, when, where matter)
7. **Monitor system effects** (metrics can distort behavior)
8. **Recognize diverse forms of research output** (preprints, code, data)
9. **Support evolving systems** (new metrics, open science)
10. **Maintain scientific integrity** (don't game metrics)

**Example of Violated Principle**:
- Researcher publishes 50 low-quality papers in predatory journals to boost publication count
- DORA/Leiden says: "Count matters, but quality more important"
- Better approach: 5 high-quality papers + 2 preprints + code

## Network Analysis & Collaboration Patterns

### Collaboration Network Visualization

**Scenario**: Visualize collaborations at an institution

**Method using Gephi**:
```
1. Data source: Co-authorship data from Scopus/WoS
   - Nodes: Researchers
   - Edges: Co-authored papers

2. Export as CSV:
   Source | Target | Weight
   Alice  | Bob    | 3 (3 papers together)
   Alice  | Carol  | 7 (7 papers together)
   Bob    | Carol  | 1 (1 paper together)

3. Import to Gephi
4. Layout: Force-directed algorithm (papers with more collaborations cluster)
5. Metrics calculated:
   - Degree: Number of collaborators
   - Betweenness: Bridge between groups
   - Clustering coefficient: How interconnected group is

6. Findings:
   - Alice & Carol (7 papers) = strong collaboration
   - Bob connects different groups (high betweenness)
   - Institute could benefit from connecting Group A ↔ Group B
```

**Visualization Output**:
- Large nodes: Prolific collaborators
- Thick edges: Strong collaborations
- Isolated nodes: Researchers with few collaborations
- Clusters: Research groups

## Research Evaluation Case Studies

### Case Study 1: Evaluating a Promotion Candidate

**Dr. Sarah Lee (10 years post-PhD)**

**Traditional Metrics**:
- 45 publications
- h-index: 12
- 1,200 citations

**DORA-Compliant Evaluation**:
```
Quantitative:
- Publications: 45 (4.5/year = good productivity)
- FWCI: 1.3 (30% above field average)
- Top papers: 3 in top 10% of field
- h-index: 12 (solid for age)
- Citations/paper: 27 (excellent)

Qualitative Assessment:
- 3 papers as first author (leadership)
- 2 as corresponding author (senior role)
- Methods development: 4 papers on new technique (used by 50+ groups)
- Open science: 80% of papers have public code + data
- Funding: 2 R01 grants ($2.4M), PI on both
- Mentoring: 6 PhD students, all with postdocs/faculty positions
- Peer review: 200+ reviews (field service)
- Teaching: Developed 2 new graduate courses (4.9/5.0 evals)
- Societal impact: 1 patent (licensed), consulting with biotech

Other Recognition:
- Invited speaker at 5 major conferences
- Editorial board member (2 journals)
- Young investigator award (2021)

Recommendation: PROMOTE
Justification: Excellent productivity, strong impact, real innovation, open science leader, excellent mentoring, field service. h-index alone underestimates contribution.
```

### Case Study 2: Field-Specific Benchmark

**Researcher Portfolio Evaluation**:
```
Researcher: Dr. James Chen (Materials Science)

His metrics:
- 62 papers
- h-index: 22
- 2,100 citations
- FWCI: 1.8

Field benchmark (Materials Science):
- Median h-index (10 yrs post-PhD): 12
- Median FWCI: 0.9
- Top 10%: h>30, FWCI>2.5

Interpretation:
- WELL ABOVE MEDIAN (h=22 vs 12)
- Strong impact (FWCI=1.8 vs 0.9)
- Approaching top 10% (but not quite)
- Solid researcher, good trajectory

Without field adjustment: "h=22 seems OK"
With field adjustment: "Top ~20%, high trajectory"
```

## Tools Deep Dive: SciVal

**SciVal** (Elsevier, research.com):

**Metrics tracked**:
1. **Research Footprint**: Publication output (country, year, field)
2. **Research Impact**: Citation metrics, FWCI
3. **Research Excellence**: % papers in top 10% cited
4. **Collaboration**: % international co-authorship
5. **Research Strength**: Relative to institutions globally

**Workflow**:
```
1. Log in (institutional access)
2. Search researcher, institution, or research topic
3. Select time period (last 5, 10 years)
4. View dashboard:
   - Trends (publications by year, impact over time)
   - Collaborators (who works with this person/institution?)
   - Competing institutions (benchmarking)
5. Export data for reports
6. Create presentations for institutional review, grant applications
```

**Strategic Use**:
- Board reports: "Our institution ranks #12 in nanotechnology globally"
- Grant proposals: "Our team in neuroscience is top 5% (SciVal)"
- Hiring decisions: "Candidate is above peer average (FWCI 1.6)"

---

## Success Metrics for Analytics Use

- [ ] Understand difference between citation count, h-index, FWCI
- [ ] Can evaluate research using DORA/Leiden principles
- [ ] Use field-normalized metrics for fair comparison
- [ ] Consider altmetrics alongside traditional metrics
- [ ] Report metrics WITH context and limitations
- [ ] Recognize discipline differences in citation patterns
- [ ] Use analytics to inform strategy (not as sole criterion)

## Common Pitfalls in Research Evaluation

- **Over-reliance on IF**: High IF journal ≠ high quality paper
- **Ignoring time lag**: Citations accumulate slowly (peak after 3-5 years)
- **Not adjusting for field**: Biomedical papers cite more than math papers
- **Comparing incomparable metrics**: h-index across different ages (unfair)
- **Gaming metrics**: Publishing in predatory journals, self-citations
- **Ignoring context**: "h=20" means different things at age 35 vs 60

---

**Version**: 1.0 (Comprehensive)
**Expertise Level**: Intermediate to Advanced
**Estimated Learning Time**: 70-140 hours
**Total Content**: 550+ lines of comprehensive material
