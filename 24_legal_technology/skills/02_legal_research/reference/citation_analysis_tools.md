# Citation Analysis Tools: Technical Reference

## Overview

Citation analysis tools validate the current authority of legal precedent, map citation networks, and identify treatment by subsequent courts. This reference covers technical implementation, comparison, and best practices for citation validation systems.

## Major Citation Analysis Systems

### KeyCite (Westlaw Edge)

#### System Architecture

**Components**:
1. **Citation Extraction Engine**: Identifies all citations in corpus
2. **Treatment Analysis**: Editorial and algorithmic classification
3. **Signal Assignment**: Red/yellow/green flag logic
4. **Depth Calculation**: Citation frequency and discussion depth
5. **Overruling Risk Model**: ML-based prediction of precedent stability

**Technical Stack**:
```
Data Pipeline:
1. Opinion ingestion → 2. Citation extraction → 3. Treatment classification
→ 4. Editorial review → 5. Signal assignment → 6. Index update

Technologies:
- NLP for citation extraction (regex + ML)
- Editorial team for treatment coding
- Graph database for citation networks
- Machine learning for overruling risk
- Real-time indexing (< 24 hour updates)
```

#### Status Indicators

**Red Flag** (Negative Treatment)
- **Criteria**: Case has been reversed, overruled, or vacated
- **Example**: "Roe v. Wade, 410 U.S. 113 (1973) - Red Flag (overruled by Dobbs v. Jackson Women's Health Organization)"
- **Action**: Do NOT cite as good law
- **API Response**: `"status": "red_flag", "treatment": "overruled"`

**Yellow Flag** (Some Negative Treatment)
- **Criteria**: Distinguished, criticized, limited, or questioned
- **Example**: Case criticized on specific point but not overruled
- **Action**: Review treatment carefully; may cite with explanation
- **API Response**: `"status": "yellow_flag", "treatment": ["criticized", "distinguished"]`

**Green C** (Cited)
- **Criteria**: Cited by other cases without negative treatment
- **Example**: Followed, affirmed, or cited positively
- **Action**: Good law (subject to jurisdiction)
- **API Response**: `"status": "green_c", "citing_count": 542`

**Blue H** (History)
- **Criteria**: Case has direct appellate history
- **Example**: Affirmed on appeal, reversed in part
- **Action**: Review history for complete understanding
- **API Response**: `"status": "blue_h", "history": "affirmed_on_appeal"`

#### Depth of Treatment Bars

**Algorithm**:
```python
def calculate_depth_bars(citation_analysis):
    """
    Calculate KeyCite depth of treatment bars (1-4)
    """
    depth_score = 0

    # Factors
    if "examined" in citation_analysis or "discussed_extensively" in citation_analysis:
        depth_score = 4  # Examined (most extensive)
    elif "discussed" in citation_analysis or "analyzed" in citation_analysis:
        depth_score = 3  # Discussed
    elif "cited" in citation_analysis and len(citation_analysis["text_mentions"]) > 1:
        depth_score = 2  # Cited (multiple references)
    else:
        depth_score = 1  # Mentioned (brief reference)

    return depth_score
```

**Bar Levels**:
- **4 Bars (Examined)**: Case is central to citing opinion's analysis
- **3 Bars (Discussed)**: Substantive discussion of case's holdings
- **2 Bars (Cited)**: Referenced with some analysis
- **1 Bar (Mentioned)**: Brief citation without extensive discussion

**Use Case**:
```python
# Filter for most influential citations
import requests

def get_influential_citations(citation, min_bars=3):
    """
    Retrieve citations with high depth of treatment
    """
    keycite_url = f"https://api.westlaw.com/keycite/v1/validate"
    headers = {"Authorization": f"Bearer {WESTLAW_TOKEN}"}

    response = requests.post(keycite_url,
                           json={"citations": [citation]},
                           headers=headers)

    data = response.json()

    # Filter for deep treatment
    influential = [
        cite for cite in data["citing_references"]
        if cite["depth_bars"] >= min_bars
    ]

    return influential
```

#### KeyCite Overruling Risk

**Machine Learning Model**:
```
Input Features:
1. Negative treatment patterns (criticized, distinguished)
2. Circuit splits (conflicting interpretations)
3. Age of precedent
4. Citation frequency trends (declining citations)
5. Supreme Court docket (related cases on docket)
6. Academic criticism (law review negativity)
7. Statutory changes (superseding legislation)
8. Doctrinal shifts (legal trend analysis)

Output: Risk Score (High / Medium / Low)
```

**Risk Levels**:
- **High Risk (Red)**: Strong indicators of potential overruling
  - Example: Case criticized by multiple circuits, related case on SCOTUS docket
- **Medium Risk (Yellow)**: Some instability indicators
  - Example: Circuit split, declining citations
- **Low Risk (Green)**: Stable precedent
  - Example: Frequently cited positively, no negative treatment

**API Implementation**:
```python
def check_overruling_risk(citation):
    """
    Get KeyCite Overruling Risk analysis
    """
    endpoint = "https://api.westlaw.com/keycite/v1/overruling-risk"
    headers = {"Authorization": f"Bearer {WESTLAW_TOKEN}"}

    response = requests.get(endpoint,
                          params={"citation": citation},
                          headers=headers)

    data = response.json()

    return {
        "risk_level": data["risk_level"],  # high, medium, low
        "risk_factors": data["factors"],
        "explanation": data["explanation"],
        "recommendation": data["recommendation"]
    }

# Example usage
risk = check_overruling_risk("410 U.S. 113")
print(f"Risk: {risk['risk_level']}")
print(f"Factors: {risk['risk_factors']}")
```

### Shepard's Citations Service (LexisNexis)

#### System Architecture

**Components**:
1. **Citation Capture**: Comprehensive citation extraction
2. **Editorial Analysis**: Attorney-editor treatment coding
3. **Algorithmic Enhancement**: ML-augmented treatment detection
4. **Signal Logic**: Treatment-based signal assignment
5. **Analysis Types**: Appellate history, citing decisions, table of authorities

**Historical Advantage**: Shepard's has longest history (since 1873 in print)

#### Status Signals

**Red Stop Sign** (Warning: Negative Treatment)
- **Criteria**: Reversed, overruled, superseded
- **Example**: Precedent no longer valid
- **Action**: Do not cite; find alternative authority
- **API**: `"signal": "warning", "treatment": "overruled"`

**Orange Q** (Questioned)
- **Criteria**: Validity questioned by citing references
- **Example**: Court expresses doubt about precedent's reasoning
- **Action**: Use with caution; note questioning treatment
- **API**: `"signal": "questioned"`

**Yellow Triangle** (Caution: Possible Negative Treatment)
- **Criteria**: Distinguished, criticized, limited
- **Example**: Court limits holding to specific facts
- **Action**: Review treatment; may still be citable
- **API**: `"signal": "caution", "treatment": ["distinguished", "limited"]`

**Green Plus** (Positive Treatment)
- **Criteria**: Affirmed, followed, approved
- **Example**: Court endorses precedent's reasoning
- **Action**: Strong authority
- **API**: `"signal": "positive", "treatment": ["followed", "affirmed"]`

**Blue A** (Analyzed)
- **Criteria**: Neutral analytical treatment
- **Example**: Discussed without clear positive/negative treatment
- **Action**: Review analysis for context
- **API**: `"signal": "cited", "treatment": "analyzed"`

**White Circle** (Cited)
- **Criteria**: Referenced without substantive treatment
- **Example**: Cited in string citation
- **Action**: Authority acknowledged
- **API**: `"signal": "cited", "treatment": "neutral"`

#### Shepard's Analysis Types

**1. Appellate History**
- Direct history of case through appeal process
- Shows procedural path: trial → appeal → supreme court
- Critical for understanding final authority

**2. Citing Decisions**
- Cases that subsequently cite this precedent
- Treatment indicators (positive, negative, neutral)
- Filterable by jurisdiction, date, treatment

**3. Table of Authorities**
- Cases cited within the Shepardized opinion
- Validates authorities relied upon
- Historical context

**API Implementation**:
```python
def shepardize_full_analysis(citation):
    """
    Comprehensive Shepard's analysis
    """
    endpoint = "https://api.lexisnexis.com/shepards/v1/citation"
    headers = {"Authorization": f"Bearer {LEXIS_API_KEY}"}

    params = {
        "citation": citation,
        "analysis": "full",  # appellate_history, citing_decisions, table_of_authorities
        "signal_filter": "negative"  # focus on negative treatment
    }

    response = requests.get(endpoint, params=params, headers=headers)
    data = response.json()

    return {
        "signal": data["shepards_signal"],
        "appellate_history": data["history"],
        "negative_treatment": [
            cite for cite in data["citing_decisions"]
            if cite["treatment"] in ["reversed", "overruled", "criticized"]
        ],
        "positive_treatment": [
            cite for cite in data["citing_decisions"]
            if cite["treatment"] in ["followed", "affirmed"]
        ],
        "neutral_citations": data["citing_count"] - len(negative) - len(positive)
    }
```

### SmartCite (Casetext)

#### Technology Approach

**AI-Powered Analysis**:
- Machine learning for treatment detection
- Natural language processing for context
- Automated signal assignment (no editorial staff)
- Real-time updates

**Status Indicators**:
- **Red Flag**: Negative treatment detected
- **Yellow Flag**: Caution advised
- **Green Checkmark**: No negative treatment found

**Strengths**:
- Fast updates (algorithmic, no editorial lag)
- Cost-effective
- Modern interface

**Limitations**:
- Less historical depth than KeyCite/Shepard's
- Algorithmic errors possible (no editorial review)
- Newer system (less established)

**API Example**:
```python
def smartcite_check(citation):
    """
    Casetext SmartCite validation
    """
    endpoint = "https://api.casetext.com/v1/smartcite"
    headers = {"Authorization": f"Bearer {CASETEXT_API_KEY}"}

    response = requests.post(endpoint,
                           json={"citation": citation},
                           headers=headers)

    data = response.json()

    return {
        "status": data["status"],  # valid, cautionary, negative
        "treatment": data["treatment_summary"],
        "citing_cases": data["citing_cases"][:10],  # top 10
        "last_updated": data["last_check"]
    }
```

### BCite (Bloomberg Law)

**Approach**: Algorithmic citation validation
**Features**:
- Automated treatment detection
- Integration with docket analytics
- Judge-specific citation patterns

**Signals**:
- Negative treatment warnings
- Citing reference counts
- Treatment categories

**Strength**: Integration with litigation analytics (judge history with similar precedents)

### Bad Law Bot (Fastcase)

**Innovation**: AI-powered negative treatment detection

**Technology**:
```python
# Conceptual algorithm
def bad_law_bot_analysis(case):
    """
    Fastcase Bad Law Bot detection algorithm
    """
    negative_indicators = []

    # Check for explicit negative treatment
    if has_overruling_language(case):
        negative_indicators.append("overruled")

    # Check for distinguishing treatment
    if has_distinguishing_pattern(case):
        negative_indicators.append("distinguished")

    # Check citation trends
    if declining_citation_rate(case):
        negative_indicators.append("declining_influence")

    # ML-based negative treatment detection
    ml_score = ml_model.predict(case_features)
    if ml_score > NEGATIVE_THRESHOLD:
        negative_indicators.append("ml_detected_negative")

    return {
        "status": "bad_law" if negative_indicators else "good_law",
        "confidence": calculate_confidence(negative_indicators),
        "indicators": negative_indicators
    }
```

**Strengths**:
- Free (with Fastcase subscription or bar membership)
- Automated detection
- Good for cost-conscious research

**Limitations**:
- Less comprehensive than KeyCite/Shepard's
- Algorithmic (potential false positives/negatives)

### Authority Check (Fastcase)

**Feature**: Citation validation with timeline visualization

**Visualization**:
```
Timeline: [1950]----[1975]----[2000]----[2025]
             ↓        ↓         ↓         ↓
          Initial  Followed  Questioned  Status
```

**Interactive Elements**:
- Click on timeline points to see citations
- Filter by treatment type
- Visualize precedent evolution

## Comparative Analysis

### Accuracy Comparison

| System | Editorial Review | Algorithmic | Accuracy Estimate |
|--------|------------------|-------------|-------------------|
| KeyCite | Yes | Yes | 99.1% |
| Shepard's | Yes | Yes | 99.0% |
| SmartCite | No | Yes | 93-95% (est.) |
| BCite | Limited | Yes | 90-93% (est.) |
| Bad Law Bot | No | Yes | 85-90% (est.) |

**Note**: Estimates based on independent studies and vendor claims

### Coverage Comparison

| System | Federal Cases | State Cases | Administrative | Historical Depth |
|--------|---------------|-------------|----------------|------------------|
| KeyCite | Excellent | Excellent | Excellent | 1790+ |
| Shepard's | Excellent | Excellent | Excellent | 1790+ |
| SmartCite | Good | Good | Fair | 1950+ |
| BCite | Good | Good | Fair | 1950+ |
| Bad Law Bot | Good | Fair | Fair | Varies |

### Speed Comparison

| System | Update Frequency | Real-Time | Lag Time |
|--------|------------------|-----------|----------|
| KeyCite | Continuous | Near real-time | < 24hrs |
| Shepard's | Continuous | Near real-time | < 24hrs |
| SmartCite | Daily | No | 24-48hrs |
| BCite | Daily | No | 24-48hrs |
| Bad Law Bot | Daily | No | 24-48hrs |

## Advanced Citation Analysis Techniques

### Citation Network Mapping

**Concept**: Visualize citation relationships as a graph

**Implementation**:
```python
import networkx as nx
import matplotlib.pyplot as plt

def build_citation_network(root_case, depth=2):
    """
    Build citation network graph
    """
    G = nx.DiGraph()

    # Add root node
    G.add_node(root_case)

    # Recursively add citing and cited cases
    def add_citations(case, current_depth):
        if current_depth > depth:
            return

        # Get cases cited by this case
        cited_by_case = get_cited_cases(case)
        for cited in cited_by_case:
            G.add_edge(case, cited, relationship="cites")
            add_citations(cited, current_depth + 1)

        # Get cases citing this case
        citing_cases = get_citing_cases(case)
        for citing in citing_cases[:10]:  # Limit to top 10
            G.add_edge(citing, case, relationship="cited_by")

    add_citations(root_case, 0)

    return G

def visualize_network(G):
    """
    Visualize citation network
    """
    pos = nx.spring_layout(G)

    # Color nodes by treatment
    node_colors = [get_treatment_color(node) for node in G.nodes()]

    nx.draw(G, pos, node_color=node_colors, with_labels=True,
            node_size=500, font_size=8, arrows=True)

    plt.title("Citation Network")
    plt.show()

# Usage
network = build_citation_network("410 U.S. 113", depth=2)
visualize_network(network)
```

### Citation Influence Scoring

**PageRank for Case Law**:
```python
import networkx as nx

def calculate_case_influence(citation_network):
    """
    Calculate influence score using PageRank algorithm
    """
    # Build directed graph from citation data
    G = nx.DiGraph()

    for case, citing_cases in citation_network.items():
        for citing_case in citing_cases:
            G.add_edge(citing_case, case)  # citing → cited

    # Calculate PageRank (influence score)
    pagerank_scores = nx.pagerank(G, alpha=0.85)

    # Sort by influence
    ranked_cases = sorted(pagerank_scores.items(),
                         key=lambda x: x[1],
                         reverse=True)

    return ranked_cases

# Example
influential_cases = calculate_case_influence(all_citations)
print(f"Most influential: {influential_cases[:10]}")
```

### Negative Treatment Detection Pipeline

**Automated Detection**:
```python
def detect_negative_treatment(case_citation):
    """
    Comprehensive negative treatment detection
    """
    results = {
        "keycite": None,
        "shepards": None,
        "smartcite": None,
        "consensus": None
    }

    # Check KeyCite
    keycite_result = keycite_check(case_citation)
    results["keycite"] = keycite_result["status"] in ["red_flag", "yellow_flag"]

    # Check Shepard's
    shepards_result = shepardize(case_citation)
    results["shepards"] = shepards_result["signal"] in ["warning", "questioned", "caution"]

    # Check SmartCite
    smartcite_result = smartcite_check(case_citation)
    results["smartcite"] = smartcite_result["status"] in ["cautionary", "negative"]

    # Consensus
    negative_count = sum([results["keycite"], results["shepards"], results["smartcite"]])

    if negative_count >= 2:
        results["consensus"] = "NEGATIVE_TREATMENT_LIKELY"
    elif negative_count == 1:
        results["consensus"] = "CAUTION_ADVISED"
    else:
        results["consensus"] = "APPEARS_GOOD_LAW"

    return results

# Usage
treatment = detect_negative_treatment("505 U.S. 144")
if treatment["consensus"] == "NEGATIVE_TREATMENT_LIKELY":
    print("WARNING: Do not cite this case without reviewing treatment")
```

### Temporal Citation Analysis

**Track Precedent Evolution**:
```python
from datetime import datetime
import matplotlib.pyplot as plt

def analyze_citation_trends(case_citation):
    """
    Analyze how citation treatment changes over time
    """
    citing_cases = get_all_citing_cases(case_citation)

    # Group by year and treatment
    timeline = {}
    for citing_case in citing_cases:
        year = citing_case["date"].year
        treatment = citing_case["treatment"]  # positive, neutral, negative

        if year not in timeline:
            timeline[year] = {"positive": 0, "neutral": 0, "negative": 0}

        timeline[year][treatment] += 1

    # Visualize
    years = sorted(timeline.keys())
    positive = [timeline[y]["positive"] for y in years]
    neutral = [timeline[y]["neutral"] for y in years]
    negative = [timeline[y]["negative"] for y in years]

    plt.figure(figsize=(12, 6))
    plt.plot(years, positive, 'g-', label='Positive', marker='o')
    plt.plot(years, neutral, 'b-', label='Neutral', marker='s')
    plt.plot(years, negative, 'r-', label='Negative', marker='^')
    plt.xlabel('Year')
    plt.ylabel('Citation Count')
    plt.title(f'Citation Treatment Over Time: {case_citation}')
    plt.legend()
    plt.grid(True)
    plt.show()

    return timeline
```

## Best Practices

### Citation Validation Workflow

```
1. Initial Check: Primary system (KeyCite OR Shepard's)
2. Red/Yellow Flag: STOP - Review treatment carefully
3. Cross-Validation: Check secondary system for critical cases
4. Treatment Analysis: Read distinguishing/criticizing opinions
5. Currency Verification: Confirm last update date
6. Alternative Authority: Find backup citations if negative treatment
7. Client Memo: Document validation process
```

### Multi-Platform Validation Protocol

**For Critical Cases** (e.g., dispositive motion, appellate brief):
1. Check KeyCite status
2. Check Shepard's status
3. If discrepancy: Review both platforms' treatment lists
4. Read key negative treatment cases
5. Document validation date and method

**Cost-Effective Alternative**:
- Primary: KeyCite or Shepard's (choose one)
- Secondary: SmartCite or Bad Law Bot (free/low-cost verification)

### Automation Recommendations

**Daily Citation Monitoring**:
```python
import schedule
import time

def daily_citation_check():
    """
    Automated daily validation of key citations
    """
    key_citations = load_matter_citations()  # From case database

    alerts = []

    for citation in key_citations:
        # Check status
        status = keycite_check(citation)

        # Alert if status changed
        if status_changed(citation, status):
            alerts.append({
                "citation": citation,
                "old_status": get_previous_status(citation),
                "new_status": status["status"],
                "matter": get_associated_matter(citation)
            })

            # Update stored status
            update_citation_status(citation, status)

    # Send alerts
    if alerts:
        send_email_alert(alerts)

# Schedule daily at 6 AM
schedule.every().day.at("06:00").do(daily_citation_check)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Integration Examples

### Microsoft Word Integration

**Real-Time Citation Checking**:
```python
# Conceptual Word Add-in
def check_document_citations(word_doc):
    """
    Extract and validate all citations in Word document
    """
    import re

    # Extract citations (simplified regex)
    citation_pattern = r'\d+ [A-Z][a-z\.]+ \d+'
    citations = re.findall(citation_pattern, word_doc.text)

    results = []

    for citation in citations:
        # Validate
        status = keycite_check(citation)

        # Highlight in document if negative treatment
        if status["status"] in ["red_flag", "yellow_flag"]:
            highlight_citation(word_doc, citation, color="red")
            results.append({
                "citation": citation,
                "status": status["status"],
                "action_required": True
            })

    return results
```

### Practice Management Integration

**Matter-Based Citation Tracking**:
```python
def link_citations_to_matter(matter_id):
    """
    Track all citations used in a matter
    """
    # Get all documents for matter
    documents = get_matter_documents(matter_id)

    # Extract citations
    all_citations = []
    for doc in documents:
        citations = extract_citations(doc)
        all_citations.extend(citations)

    # Deduplicate and validate
    unique_citations = list(set(all_citations))

    for citation in unique_citations:
        # Validate
        status = shepardize(citation)

        # Store in matter database
        store_matter_citation(matter_id, citation, status)

        # Set up monitoring alert
        create_citation_alert(citation, matter_id)

    return unique_citations
```

---

*This reference provides comprehensive technical coverage of citation analysis tools for legal research professionals.*
