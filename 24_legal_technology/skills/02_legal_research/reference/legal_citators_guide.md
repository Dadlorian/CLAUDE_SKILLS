# Legal Citators Guide: Comprehensive Reference

## Overview

Legal citators are essential tools for validating legal authority, tracking subsequent treatment, and ensuring citations represent current good law. This guide covers citator systems, interpretation methodologies, and best practices.

## Purpose of Legal Citators

### Primary Functions

1. **Validation**: Determine if case/statute is still good law
2. **Treatment Analysis**: Track how subsequent authorities treat the citation
3. **Citation Network**: Map relationship between legal authorities
4. **Research Expansion**: Find related authorities citing same precedent
5. **Historical Context**: Understand evolution of legal doctrine

### When to Citator Check

**Always Before Citing**:
- Cases in briefs, motions, or memoranda
- Statutes relied upon for legal propositions
- Regulations central to argument
- Secondary sources cited as authority

**During Research**:
- Validating promising search results
- Tracking precedent development
- Identifying most current authority
- Finding additional relevant cases

**Ongoing Monitoring**:
- Key cases in pending matters
- Statutes affecting clients
- Precedent in practice area
- Cases cited in filed documents

## KeyCite (Westlaw) Comprehensive Guide

### Signal System

#### Red Flag: Negative Treatment

**Meaning**: Case is no longer good law for at least one point

**Specific Treatments**:
- **Overruled**: Holding explicitly rejected by higher court
- **Reversed**: Overturned on appeal in same case
- **Vacated**: Appellate court vacated lower court decision
- **Superseded by Statute**: Legislative enactment replaces case law rule

**Example**:
```
Roe v. Wade, 410 U.S. 113 (1973) - RED FLAG
Treatment: Overruled by Dobbs v. Jackson Women's Health Organization, 597 U.S. ___ (2022)

Action Required: DO NOT CITE as controlling authority
Alternative: Cite Dobbs for current law on abortion rights
```

**API Check**:
```python
def keycite_red_flag_analysis(citation):
    """
    Detailed analysis of red flag status
    """
    kc_result = keycite_check(citation)

    if kc_result["status"] == "red_flag":
        return {
            "cite_status": "DO_NOT_CITE",
            "negative_treatment": kc_result["negative_treatment"],
            "overruling_case": kc_result["overruling_case"],
            "affected_points": kc_result["affected_headnotes"],
            "recommendation": "Find alternative authority or cite only for historical context"
        }
```

#### Yellow Flag: Caution

**Meaning**: Case has some negative history but not completely overruled

**Specific Treatments**:
- **Distinguished**: Court limited holding to specific facts
- **Criticized**: Court expressed disapproval but followed
- **Limited**: Holding's scope narrowed by subsequent decision
- **Questioned**: Court cast doubt on reasoning or holding
- **Declined to Extend**: Court refused to expand holding

**Analysis Requirement**:
```python
def analyze_yellow_flag(citation):
    """
    Determine if yellow flag case is still citable
    """
    kc_result = keycite_check(citation)

    # Read distinguishing cases
    negative_treatment = kc_result["negative_cases"]

    analysis = {
        "still_good_law": True,  # Default assumption
        "limitations": [],
        "jurisdictional_issues": [],
        "recommended_action": ""
    }

    for negative_case in negative_treatment:
        # Check if your issue affected
        if your_legal_issue_affected(negative_case):
            analysis["still_good_law"] = False
            analysis["limitations"].append(negative_case)

        # Check jurisdiction
        if negative_case["jurisdiction"] == your_jurisdiction:
            analysis["jurisdictional_issues"].append(negative_case)

    # Recommendation
    if not analysis["still_good_law"]:
        analysis["recommended_action"] = "Find alternative authority; cite with explanation of limitations"
    elif analysis["jurisdictional_issues"]:
        analysis["recommended_action"] = "Cite with note addressing distinguishing treatment"
    else:
        analysis["recommended_action"] = "Acceptable to cite; yellow flag not applicable to your issue"

    return analysis
```

**Example**:
```
Sony Corp. v. Universal City Studios, 464 U.S. 417 (1984) - YELLOW FLAG

Negative Treatment:
- Distinguished by MGM Studios Inc. v. Grokster, Ltd., 545 U.S. 913 (2005)
  (limited Sony safe harbor for peer-to-peer file sharing)

Analysis: Sony still good law for time-shifting / personal use
         Yellow flag reflects limitation in P2P context
         Cite Sony for VCR/DVR fair use; distinguish Grokster for P2P
```

#### Green C: Cited

**Meaning**: Case has been cited by other cases (no negative treatment)

**Interpretation**: Presumptively good law (subject to verification)

**Additional Information**:
- **Citing Reference Count**: Number of cases citing this case
- **Depth of Treatment**: How extensively citing cases discuss it

**Confidence Level**:
```
High Citing References + No Negative Treatment = Strong Authority
Low Citing References + No Negative Treatment = Limited Precedent
Many Citations from Lower Courts = Widely Accepted Holding
```

#### Blue H: History

**Meaning**: Case has direct appellate history

**Types of History**:
- **Affirmed**: Upheld on appeal (strengthens authority)
- **Reversed in Part**: Some holdings reversed, others affirmed
- **Remanded**: Sent back to lower court for further proceedings
- **Certiorari Denied**: Supreme Court declined review

**Example**:
```
District Court Decision → BLUE H
  ↓
Circuit Court: Affirmed in part, reversed in part
  ↓
Supreme Court: Certiorari denied

Analysis:
- Affirmed portions: Good law (circuit binding)
- Reversed portions: Not good law
- Cert denied: Circuit decision final (not Supreme Court endorsement)
```

### Depth of Treatment

**4-Bar System**:

**4 Bars (Examined)**:
- Extensive discussion of case
- Central to citing opinion's holding
- Detailed analysis of reasoning
- Often multiple pages of discussion

**3 Bars (Discussed)**:
- Substantive discussion
- Important to citing opinion
- Analysis of holding and application

**2 Bars (Cited)**:
- Referenced with some analysis
- Supporting authority
- Proposition cited

**1 Bar (Mentioned)**:
- Brief citation
- String citation
- Passing reference

**Research Application**:
```python
def prioritize_citing_cases(citation, min_depth=3):
    """
    Prioritize highly influential citing cases
    """
    kc_result = keycite_check(citation)

    citing_cases = kc_result["citing_references"]

    # Filter by depth
    influential_cases = [
        case for case in citing_cases
        if case["depth_bars"] >= min_depth
    ]

    # Sort by authority level + recency
    sorted_cases = sorted(
        influential_cases,
        key=lambda c: (c["court_level"], c["date"]),
        reverse=True
    )

    return sorted_cases[:20]  # Top 20 most influential
```

### KeyCite Filters

**Available Filters**:
- **Jurisdiction**: Limit to specific courts
- **Headnote**: Filter to specific legal points
- **Depth of Treatment**: Minimum bar level
- **Document Type**: Cases, secondary sources, briefs
- **Date**: Specific time ranges
- **KeyCite Status**: Red/yellow flags only

**Advanced Filtering**:
```python
def keycite_filtered_research(citation, filters):
    """
    Apply sophisticated filters to KeyCite results
    """
    kc_url = "https://api.westlaw.com/keycite/v1/citing-references"

    params = {
        "citation": citation,
        "jurisdiction": filters.get("jurisdiction", "all"),
        "headnote": filters.get("headnote_number"),  # Specific legal point
        "min_depth": filters.get("min_depth", 1),
        "start_date": filters.get("start_date"),
        "end_date": filters.get("end_date"),
        "doc_types": filters.get("doc_types", ["cases"])
    }

    response = requests.get(kc_url, params=params, headers=westlaw_headers)

    return response.json()["citing_references"]
```

### KeyCite for Statutes

**Statute Citator Functions**:
- **Amendment Status**: Track legislative changes
- **Citing Cases**: Cases interpreting statute
- **Proposed Legislation**: Pending amendments
- **Effective Dates**: When amendments take effect
- **Legislative History**: Links to legislative materials

**Example**:
```python
def keycite_statute_analysis(statute_citation):
    """
    Comprehensive statute validation
    """
    kc_statute = keycite_check(statute_citation, doc_type="statute")

    return {
        "current_version": kc_statute["current_text"],
        "amendments": kc_statute["amendment_history"],
        "pending_amendments": kc_statute["proposed_legislation"],
        "citing_cases": kc_statute["citing_cases"][:50],
        "annotations": kc_statute["case_annotations"],
        "effective_date": kc_statute["effective_date"],
        "recommendation": validate_statute_currency(kc_statute)
    }
```

### KeyCite Overruling Risk

**Risk Assessment Model**:

**High Risk (Red)**:
- Circuit split exists
- Multiple courts have criticized reasoning
- Related case on Supreme Court docket
- Legal doctrine shifting away from holding
- Declining citation rate

**Medium Risk (Yellow)**:
- Some circuit disagreement
- Occasional critical treatment
- Alternative approaches emerging
- Aging precedent with modern challenges

**Low Risk (Green)**:
- Consistently followed
- No circuit splits
- Recent positive treatment
- Stable legal doctrine

**Practical Application**:
```python
def assess_citation_stability(citation, matter_type):
    """
    Determine risk of relying on potentially unstable precedent
    """
    overruling_risk = keycite_overruling_risk(citation)

    if overruling_risk["level"] == "high":
        return {
            "use_case": "DO_NOT_RELY_HEAVILY",
            "recommendation": "Find additional supporting authorities",
            "explanation": overruling_risk["risk_factors"],
            "alternative_research": "Search for recent cases on same issue"
        }
    elif overruling_risk["level"] == "medium":
        return {
            "use_case": "USE_WITH_CAUTION",
            "recommendation": "Include backup authorities; address potential weakness",
            "explanation": overruling_risk["risk_factors"]
        }
    else:
        return {
            "use_case": "RELIABLE_AUTHORITY",
            "recommendation": "Cite confidently",
            "explanation": "Stable precedent"
        }
```

## Shepard's Citations (LexisNexis) Comprehensive Guide

### Signal System

#### Red Stop Sign: Warning

**Meaning**: Case has strong negative treatment

**Treatments**:
- Reversed
- Overruled
- Vacated
- Superseded by statute

**Action**: Do not cite as good law

#### Orange Q: Questioned

**Meaning**: Validity questioned by citing references

**Interpretation**: Precedential value in doubt

**Action**: Use extreme caution; find alternative authority

#### Yellow Triangle: Caution

**Meaning**: Possible negative treatment

**Treatments**:
- Distinguished
- Criticized
- Limited
- Clarified (with some negative aspect)

**Action**: Review treatment; may still be citable with qualifications

#### Green Plus: Positive Treatment

**Meaning**: Affirmative treatment by citing references

**Treatments**:
- Followed
- Affirmed
- Approved
- Explained favorably

**Interpretation**: Strong authority

#### Blue A: Analyzed

**Meaning**: Substantive neutral treatment

**Interpretation**: Neither positive nor negative

#### White Circle: Cited

**Meaning**: Referenced without substantive treatment

**Interpretation**: Precedent acknowledged

### Shepard's Analysis Types

#### Appellate History

**Direct Case History**:
```
Trial Court (District Court)
    ↓
Appeals Court (Circuit Court) - Affirmed in part, reversed in part
    ↓
Supreme Court - Certiorari granted, vacated and remanded
    ↓
Circuit Court on Remand - Affirmed as modified
```

**Understanding History**:
- Follow case through complete appellate process
- Identify which holdings survived appeal
- Determine final authoritative decision

**API Implementation**:
```python
def get_complete_case_history(citation):
    """
    Trace case through entire appellate history
    """
    shepards_result = shepardize(citation)

    history = {
        "original_decision": shepards_result["case"],
        "appellate_chain": [],
        "final_status": ""
    }

    # Build history chain
    for hist in shepards_result["appellate_history"]:
        history["appellate_chain"].append({
            "court": hist["court"],
            "date": hist["date"],
            "treatment": hist["treatment"],
            "citation": hist["citation"]
        })

    # Determine final status
    if history["appellate_chain"]:
        final = history["appellate_chain"][-1]
        history["final_status"] = final["treatment"]

    return history
```

#### Citing Decisions

**Subsequent Case Treatment**:

**Filter Options**:
- **Analysis**: Type of treatment (positive, negative, neutral)
- **Jurisdiction**: Court hierarchy
- **Date**: Time range
- **Headnote**: Specific legal point

**Research Workflow**:
```python
def analyze_citing_decisions(citation, focus_issue):
    """
    Analyze how subsequent courts treated specific issue
    """
    shepards = shepardize(citation)

    citing_decisions = shepards["citing_decisions"]

    # Filter to relevant headnote
    relevant_cites = [
        cite for cite in citing_decisions
        if focus_issue in cite["headnotes_referenced"]
    ]

    # Categorize treatment
    treatment_summary = {
        "positive": [],
        "negative": [],
        "neutral": [],
        "distinguishing": []
    }

    for cite in relevant_cites:
        if cite["treatment"] in ["followed", "affirmed"]:
            treatment_summary["positive"].append(cite)
        elif cite["treatment"] in ["reversed", "overruled", "criticized"]:
            treatment_summary["negative"].append(cite)
        elif cite["treatment"] in ["distinguished", "limited"]:
            treatment_summary["distinguishing"].append(cite)
        else:
            treatment_summary["neutral"].append(cite)

    return treatment_summary
```

#### Table of Authorities

**Cases Cited Within Shepardized Opinion**:

**Purpose**:
- Understand legal foundation of shepardized case
- Validate authorities relied upon
- Identify doctrinal lineage

**Use Case**:
```python
def validate_precedent_chain(target_case):
    """
    Validate authority chain of cited case
    """
    shepards = shepardize(target_case)

    authorities_cited = shepards["table_of_authorities"]

    # Check status of each cited authority
    validation_results = []

    for authority in authorities_cited:
        # Shepardize each cited case
        auth_status = shepardize(authority["citation"])

        validation_results.append({
            "cited_authority": authority["citation"],
            "shepards_signal": auth_status["signal"],
            "still_good_law": auth_status["signal"] not in ["warning", "questioned"],
            "recommendation": "Review foundation" if not auth_status["signal"] in ["positive", "cited"] else "Valid"
        })

    # Summarize
    problematic_authorities = [
        v for v in validation_results
        if not v["still_good_law"]
    ]

    return {
        "target_case": target_case,
        "total_authorities_cited": len(validation_results),
        "problematic_count": len(problematic_authorities),
        "problematic_authorities": problematic_authorities,
        "overall_assessment": "CAUTION" if problematic_authorities else "VALID_FOUNDATION"
    }
```

### Shepard's for Statutes

**Statute Citator Features**:
- Legislative history
- Amendments and effective dates
- Citing cases with interpretation
- Regulatory references
- Law review citations

**Comprehensive Statute Research**:
```python
def comprehensive_statute_research(statute_citation):
    """
    Full statutory research workflow
    """
    shepards = shepardize(statute_citation, doc_type="statute")

    return {
        "current_text": get_current_statute_text(statute_citation),
        "shepards_signal": shepards["signal"],
        "amendments": shepards["legislative_history"],
        "pending_legislation": shepards["pending_amendments"],
        "key_interpreting_cases": shepards["citing_cases"][:25],
        "regulations": shepards["citing_regulations"],
        "secondary_sources": shepards["citing_secondary_sources"],
        "last_amendment": shepards["last_amendment_date"],
        "research_notes": generate_research_notes(shepards)
    }
```

## SmartCite (Casetext) Guide

### AI-Powered Citation Analysis

**Technology**: Machine learning for treatment detection

**Signals**:
- **Red Flag**: Negative treatment detected
- **Yellow Flag**: Cautionary treatment
- **Green Checkmark**: No negative treatment

**Features**:
- Automated treatment classification
- Natural language explanation of treatment
- Visual citation map

**Limitations**:
- Algorithmic (no editorial review)
- May miss nuanced treatment
- Should be cross-validated for critical cases

**Use Case**:
```python
def smartcite_validation(citation):
    """
    Quick citation validation with SmartCite
    """
    sc_result = smartcite_check(citation)

    if sc_result["status"] == "negative":
        # Cross-validate with KeyCite or Shepard's
        kc_check = keycite_check(citation)
        shepards_check = shepardize(citation)

        consensus = {
            "smartcite": sc_result["status"],
            "keycite": kc_check["status"],
            "shepards": shepards_check["signal"],
            "recommendation": ""
        }

        # All agree on negative treatment?
        if all(x in ["red_flag", "warning", "negative"] for x in consensus.values()):
            consensus["recommendation"] = "CONFIRMED: Do not cite"
        else:
            consensus["recommendation"] = "CONFLICT: Manual review required"

        return consensus
```

## Bad Law Bot (Fastcase)

**AI Detection System**:
- Automated negative treatment detection
- Free (with Fastcase subscription)
- Real-time analysis

**Functionality**:
```python
def bad_law_bot_check(citation):
    """
    Fastcase Bad Law Bot analysis
    """
    blb_result = fastcase_bad_law_check(citation)

    return {
        "status": blb_result["status"],  # good_law, caution, bad_law
        "negative_indicators": blb_result["negative_treatment_detected"],
        "confidence": blb_result["confidence_score"],
        "recommendation": "Manual verification recommended" if blb_result["status"] != "good_law" else "Appears valid"
    }
```

## Cross-Platform Citator Comparison

### Accuracy and Comprehensiveness

| Feature | KeyCite | Shepard's | SmartCite | Bad Law Bot |
|---------|---------|-----------|-----------|-------------|
| Editorial Review | Yes | Yes | No | No |
| Algorithm Enhanced | Yes | Yes | Yes | Yes |
| Accuracy | 99%+ | 99%+ | 93-95% | 85-90% |
| Historical Depth | Excellent | Excellent | Good | Fair |
| Speed | Real-time | Real-time | Fast | Fast |
| Cost | Premium | Premium | Mid-tier | Low/Free |

### When to Use Each

**KeyCite**:
- Westlaw subscribers
- Need for overruling risk analysis
- Preference for depth of treatment bars
- Complex research requiring precision

**Shepard's**:
- LexisNexis subscribers
- Preference for detailed treatment categories
- Need for table of authorities
- Tradition/familiarity

**SmartCite**:
- Casetext subscribers
- Cost-conscious research
- Quick validation
- Modern AI-first workflow

**Bad Law Bot**:
- Budget research
- Fastcase bar membership
- Initial screening
- Supplemental check

## Best Practices

### 1. Always Citator Check Before Citing

**Workflow**:
```
1. Find potentially relevant case
2. IMMEDIATELY citator check (before reading full opinion)
3. If red/yellow flag: Assess whether still useful
4. Read case with awareness of treatment
5. Final citator check before including in brief/memo
```

### 2. Understand Treatment Context

**Not All Negative Treatment Is Equal**:
```python
def contextualize_negative_treatment(citation, your_issue):
    """
    Determine if negative treatment affects your specific issue
    """
    kc_result = keycite_check(citation)

    if kc_result["status"] in ["red_flag", "yellow_flag"]:
        # Read negative treatment cases
        negative_cases = kc_result["negative_treatment_cases"]

        affects_your_issue = False

        for neg_case in negative_cases:
            # Check if affects same legal point
            if legal_point_affected(neg_case, your_issue):
                affects_your_issue = True
                break

        return {
            "negative_treatment_exists": True,
            "affects_your_issue": affects_your_issue,
            "recommendation": "Do not cite" if affects_your_issue else "Cite with explanation of distinction"
        }
```

### 3. Monitor Key Citations

**Set Up Alerts**:
```python
def setup_citation_monitoring(citations, matter_id):
    """
    Monitor key citations for subsequent treatment
    """
    for citation in citations:
        # KeyCite Alert
        westlaw_alert = create_keycite_alert(citation, matter_id)

        # Shepard's Alert
        lexis_alert = create_shepards_alert(citation, matter_id)

        # Store alert configuration
        store_alert_config({
            "matter_id": matter_id,
            "citation": citation,
            "westlaw_alert_id": westlaw_alert["id"],
            "lexis_alert_id": lexis_alert["id"],
            "created_date": datetime.now(),
            "frequency": "immediate"  # or daily, weekly
        })
```

### 4. Cross-Validate Critical Citations

**For Dispositive Motions, Appellate Briefs**:
```
1. Check KeyCite
2. Check Shepard's
3. If discrepancy: Manual review of citing cases
4. Document validation process
```

### 5. Understand Jurisdiction-Specific Weight

**Treatment by Different Courts**:
- Treatment by same jurisdiction: Most important
- Treatment by higher court in jurisdiction: Controlling
- Treatment by other jurisdictions: Informative only (unless persuasive)

---

*Legal citators are indispensable tools for ensuring cited authorities represent good law. Master citator interpretation to avoid malpractice risks and strengthen legal arguments.*
