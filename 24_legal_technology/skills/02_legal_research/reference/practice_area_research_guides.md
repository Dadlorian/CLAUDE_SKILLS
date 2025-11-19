# Practice Area-Specific Research Guides

## Overview

Different practice areas require specialized research strategies, databases, and resources. This reference provides targeted guidance for major practice areas.

## Litigation Research

### Civil Litigation

**Primary Research Needs**:
- Procedural rules (Federal and state)
- Evidence standards
- Motion practice
- Discovery rules
- Trial procedure

**Essential Resources**:

**Federal Practice**:
- **Federal Rules of Civil Procedure** (FRCP)
- **Federal Rules of Evidence** (FRE)
- **Wright & Miller, Federal Practice and Procedure** (authoritative treatise)
- **Moore's Federal Practice** (comprehensive)
- **Manual for Complex Litigation**

**Westlaw Databases**:
```
FRCP - Federal Rules of Civil Procedure
FRE - Federal Rules of Evidence
USCODE (Title 28 - Judiciary)
FED-LITIGAT (Federal litigation materials)
```

**State-Specific**:
```python
def civil_litigation_research(jurisdiction, procedure_issue):
    """
    Civil procedure research strategy
    """
    # Federal or state?
    if jurisdiction == "federal":
        # Federal rules
        rules = search_frcp(procedure_issue)
        treatise = wright_miller_search(procedure_issue)
        cases = westlaw_search(procedure_issue, "ALLFEDS")
    else:
        # State rules
        state_code = f"{jurisdiction}-RULES"
        rules = search_state_rules(state_code, procedure_issue)
        state_practice_guide = get_state_practice_guide(jurisdiction)
        cases = westlaw_search(procedure_issue, f"{jurisdiction}-CS")

    # Cross-reference
    return {
        "applicable_rules": rules,
        "treatise_analysis": treatise if jurisdiction == "federal" else state_practice_guide,
        "controlling_cases": cases[:20],
        "practice_tips": extract_practice_tips(rules, cases)
    }
```

**Litigation Analytics**:
- **Bloomberg Law**: Judge analytics, attorney analytics, docket research
- **Westlaw Edge**: Litigation Analytics module
- **LexisNexis**: Lexis Analytics

**Example Judge Research**:
```python
def research_judge(judge_name, case_type):
    """
    Research judge's history and tendencies
    """
    # Bloomberg Law judge analytics
    bloomberg_profile = bloomberg_judge_lookup(judge_name)

    analytics = {
        "grant_rate_summary_judgment": bloomberg_profile["sj_grant_rate"],
        "grant_rate_motions_to_dismiss": bloomberg_profile["mtd_grant_rate"],
        "average_time_to_decision": bloomberg_profile["avg_decision_time"],
        "trial_rate": bloomberg_profile["trial_rate"],
        "similar_cases": bloomberg_profile.filter_cases(case_type),
        "reversal_rate": bloomberg_profile["reversal_rate_on_appeal"]
    }

    return analytics
```

### Criminal Defense

**Primary Research Needs**:
- Criminal statutes (federal and state)
- Constitutional law (4th, 5th, 6th, 8th Amendments)
- Sentencing guidelines
- Evidence and procedure

**Essential Resources**:

**Federal Criminal**:
- **Title 18 U.S.C.** (Crimes and Criminal Procedure)
- **Federal Rules of Criminal Procedure** (FRCrP)
- **Federal Sentencing Guidelines** (USSG)
- **LaFave, Criminal Law** (leading treatise)
- **LaFave, Search and Seizure** (4th Amendment authority)

**Constitutional Law**:
```python
def criminal_constitutional_research(issue):
    """
    Constitutional criminal law research
    """
    # Identify constitutional provision
    if "search" in issue or "seizure" in issue:
        amendment = "Fourth Amendment"
        treatise = "LaFave, Search and Seizure"
    elif "self-incrimination" in issue or "confession" in issue:
        amendment = "Fifth Amendment"
        treatise = "LaFave, Criminal Procedure"
    elif "right to counsel" in issue:
        amendment = "Sixth Amendment"

    # Search Supreme Court cases (constitutional criminal law)
    scotus_cases = westlaw_search(f"{issue} & court(Supreme)", "SCT")

    # Circuit-specific application
    circuit_cases = westlaw_search(f"{issue} & {amendment}", your_circuit)

    return {
        "constitutional_basis": amendment,
        "supreme_court_precedent": scotus_cases[:10],
        "circuit_precedent": circuit_cases[:20],
        "treatise_analysis": search_treatise(treatise, issue)
    }
```

**Sentencing Research**:
```python
def sentencing_research(offense, criminal_history):
    """
    Federal sentencing guidelines research
    """
    # Identify guideline provision
    guideline_section = identify_ussg_section(offense)

    # Calculate guideline range
    base_level = guideline_section["base_offense_level"]
    adjustments = calculate_adjustments(offense_facts)
    criminal_history_category = determine_chc(criminal_history)

    guideline_range = calculate_range(base_level + adjustments, criminal_history_category)

    # Research departures and variances
    departure_cases = search_departure_cases(offense, guideline_section)
    variance_cases = search_variance_cases(offense)

    return {
        "guideline_range": guideline_range,
        "potential_departures": departure_cases,
        "variance_arguments": variance_cases,
        "recommendation": "Argue for variance based on [factors]"
    }
```

## Corporate & Transactional Research

### Corporate Law

**Primary Research Needs**:
- Corporate statutes (especially Delaware)
- Corporate governance
- Fiduciary duties
- M&A law
- Securities regulation

**Essential Resources**:

**Delaware Corporate Law**:
- **Delaware General Corporation Law** (DGCL)
- **Folk on Delaware General Corporation Law** (authoritative commentary)
- **Delaware Court of Chancery** opinions (equity court for corporate disputes)
- **Delaware Supreme Court** opinions

**Federal Securities**:
- **Securities Act of 1933**
- **Securities Exchange Act of 1934**
- **SEC Rules and Regulations**
- **SEC No-Action Letters**
- **SEC Interpretive Guidance**

**Research Strategy**:
```python
def corporate_law_research(issue):
    """
    Corporate law research strategy
    """
    # Delaware law (most U.S. corporations incorporated in DE)
    dgcl = search_delaware_statute(issue)
    chancery_cases = search_delaware_chancery(issue)
    folk_commentary = search_folk_treatise(issue)

    # Federal securities (if applicable)
    if is_securities_issue(issue):
        securities_laws = search_federal_securities_laws(issue)
        sec_guidance = search_sec_releases(issue)
        sec_no_action = search_sec_no_action_letters(issue)
    else:
        securities_laws = None
        sec_guidance = None
        sec_no_action = None

    return {
        "delaware_statute": dgcl,
        "delaware_cases": chancery_cases[:15],
        "expert_commentary": folk_commentary,
        "securities_laws": securities_laws,
        "sec_guidance": sec_guidance,
        "no_action_letters": sec_no_action
    }
```

**Specialized Databases**:
- **Westlaw**: DE-CS (Delaware cases), FED-SEC (federal securities)
- **LexisNexis**: Delaware corporate law collections
- **SEC EDGAR**: sec.gov/edgar (public company filings)

### Contracts

**Primary Research Needs**:
- Contract formation
- Interpretation
- Performance and breach
- Remedies
- UCC (for sales of goods)

**Essential Resources**:
- **Restatement (Second) of Contracts** (highly influential)
- **Uniform Commercial Code** (Article 2 - Sales)
- **Williston on Contracts** (comprehensive treatise)
- **Corbin on Contracts** (scholarly approach)
- **Farnsworth on Contracts** (modern synthesis)

**Research Strategy**:
```python
def contract_law_research(issue, contract_type):
    """
    Contract law research
    """
    # Determine if UCC applies
    if contract_type == "sale_of_goods":
        # UCC Article 2
        ucc_provision = search_ucc_article_2(issue)
        ucc_commentary = white_summers_commentary(ucc_provision)
        sources = [ucc_provision, ucc_commentary]
    else:
        # Common law contracts
        restatement = search_restatement_contracts(issue)
        treatise = search_williston(issue)
        sources = [restatement, treatise]

    # Case law
    jurisdiction_cases = search_jurisdiction_cases(issue, your_jurisdiction)

    return {
        "applicable_law": sources,
        "jurisdiction_precedent": jurisdiction_cases[:20],
        "restatement_rule": restatement if contract_type != "sale_of_goods" else None,
        "ucc_provision": ucc_provision if contract_type == "sale_of_goods" else None
    }
```

## Intellectual Property Research

### Patent Law

**Primary Research Needs**:
- Patent statutes (35 U.S.C.)
- Patent regulations (37 C.F.R.)
- USPTO examination guidelines
- Federal Circuit case law
- Prior art searches

**Essential Resources**:
- **35 U.S.C.** (Patent Act)
- **USPTO Patent Rules** (37 C.F.R.)
- **Manual of Patent Examining Procedure** (MPEP)
- **Chisum on Patents** (leading treatise)

**Specialized Databases**:
- **USPTO Patent Database**: patents.uspto.gov
- **Google Patents**: patents.google.com (free, comprehensive)
- **Westlaw**: PATENT (patent cases, CAFC opinions)
- **Derwent Innovation**: Commercial patent database

**Research Strategy**:
```python
def patent_research(issue):
    """
    Patent law research strategy
    """
    # Federal Circuit (exclusive patent appeal jurisdiction)
    cafc_cases = search_federal_circuit(issue)

    # District court cases (technology-specific courts)
    # E.D. Tex, D. Del, N.D. Cal (major patent venues)
    district_cases = search_patent_district_courts(issue)

    # USPTO guidance
    mpep = search_mpep(issue)
    examination_guidelines = search_uspto_guidelines(issue)

    # Treatise
    chisum_analysis = search_chisum(issue)

    return {
        "federal_circuit_precedent": cafc_cases[:15],
        "district_court_cases": district_cases[:10],
        "uspto_guidance": mpep,
        "examination_guidelines": examination_guidelines,
        "treatise_analysis": chisum_analysis
    }
```

### Copyright Law

**Primary Research Needs**:
- Copyright Act (17 U.S.C.)
- Copyright Office regulations
- Fair use analysis
- DMCA provisions
- Registration requirements

**Essential Resources**:
- **17 U.S.C.** (Copyright Act)
- **Copyright Office Compendium** (examination practices)
- **Nimmer on Copyright** (definitive treatise)
- **Patry on Copyright** (modern comprehensive treatise)

**Fair Use Research**:
```python
def fair_use_research(use_case):
    """
    Fair use analysis research
    """
    # Four factor analysis
    factors = {
        "purpose_character": analyze_factor_one(use_case),
        "nature_work": analyze_factor_two(use_case),
        "amount_substantiality": analyze_factor_three(use_case),
        "market_effect": analyze_factor_four(use_case)
    }

    # Find analogous cases
    similar_cases = search_fair_use_cases(use_case)

    # Nimmer analysis
    nimmer_guidance = search_nimmer("fair use", use_case)

    return {
        "four_factor_analysis": factors,
        "analogous_cases": similar_cases,
        "treatise_guidance": nimmer_guidance,
        "likelihood_fair_use": predict_fair_use_outcome(factors, similar_cases)
    }
```

### Trademark Law

**Primary Research Needs**:
- Lanham Act (15 U.S.C. § 1051 et seq.)
- Likelihood of confusion analysis
- Trademark registration
- TTAB decisions
- Common law trademark rights

**Essential Resources**:
- **15 U.S.C. §§ 1051-1141n** (Lanham Act)
- **McCarthy on Trademarks** (authoritative treatise)
- **USPTO TTAB decisions** (Trademark Trial and Appeal Board)

**Likelihood of Confusion Research**:
```python
def likelihood_of_confusion_research(mark1, mark2):
    """
    Trademark likelihood of confusion analysis
    """
    # Identify circuit test (varies by circuit)
    circuit_test = get_circuit_test(your_circuit)
    # e.g., 2nd Cir: Polaroid factors, 9th Cir: Sleekcraft factors

    # Apply factors
    factor_analysis = apply_loc_factors(mark1, mark2, circuit_test)

    # Find similar cases
    similar_cases = search_trademark_cases({
        "industry": mark1["industry"],
        "similarity": calculate_similarity(mark1, mark2),
        "circuit": your_circuit
    })

    # McCarthy commentary
    mccarthy_analysis = search_mccarthy("likelihood of confusion")

    return {
        "applicable_test": circuit_test,
        "factor_analysis": factor_analysis,
        "analogous_cases": similar_cases,
        "expert_commentary": mccarthy_analysis,
        "prediction": predict_loc_outcome(factor_analysis, similar_cases)
    }
```

## Tax Law Research

**Primary Research Needs**:
- Internal Revenue Code (26 U.S.C.)
- Treasury Regulations
- IRS Revenue Rulings
- Private Letter Rulings
- Tax Court decisions

**Essential Resources**:
- **Internal Revenue Code** (26 U.S.C.)
- **Treasury Regulations** (26 C.F.R.)
- **IRS Publications and Guidance**
- **Tax Court Opinions** (ustaxcourt.gov)
- **Mertens Law of Federal Income Taxation** (treatise)

**Research Strategy**:
```python
def tax_research(tax_issue):
    """
    Tax law research workflow
    """
    # IRC provision
    irc_section = identify_irc_section(tax_issue)

    # Treasury Regulations (authoritative interpretation)
    treasury_reg = get_treasury_regulation(irc_section)

    # IRS guidance
    revenue_rulings = search_revenue_rulings(tax_issue)
    revenue_procedures = search_revenue_procedures(tax_issue)
    private_letter_rulings = search_plrs(tax_issue)  # Not precedential but informative

    # Tax Court
    tax_court_cases = search_tax_court(tax_issue)

    # Circuit court (tax appeal jurisdiction)
    circuit_cases = search_circuit_tax_cases(tax_issue)

    return {
        "code_section": irc_section,
        "regulations": treasury_reg,
        "irs_guidance": {
            "revenue_rulings": revenue_rulings,
            "revenue_procedures": revenue_procedures,
            "private_letter_rulings": private_letter_rulings
        },
        "tax_court_precedent": tax_court_cases,
        "circuit_precedent": circuit_cases
    }
```

**Specialized Tax Databases**:
- **Westlaw**: FTX-ALL (all federal tax)
- **LexisNexis**: Federal Tax library
- **Bloomberg Tax** (formerly BNA): Comprehensive tax research platform
- **CCH IntelliConnect**: Tax research platform
- **RIA Checkpoint**: Tax research platform

## Employment & Labor Law Research

**Primary Research Needs**:
- Federal employment statutes
- NLRB decisions (labor law)
- EEOC guidance (discrimination)
- DOL regulations (wage and hour)
- State employment laws

**Essential Resources**:

**Federal Statutes**:
- **Title VII** (Civil Rights Act of 1964)
- **ADA** (Americans with Disabilities Act)
- **ADEA** (Age Discrimination in Employment Act)
- **FMLA** (Family and Medical Leave Act)
- **FLSA** (Fair Labor Standards Act - wage and hour)
- **NLRA** (National Labor Relations Act)

**Agency Guidance**:
- **EEOC Compliance Manual**
- **NLRB Decisions**
- **DOL Opinion Letters**

**Research Strategy**:
```python
def employment_law_research(issue):
    """
    Employment law research
    """
    # Identify applicable statute
    statute = identify_employment_statute(issue)

    # Agency guidance
    if statute in ["Title VII", "ADA", "ADEA"]:
        agency_guidance = search_eeoc_guidance(issue)
    elif statute == "NLRA":
        agency_guidance = search_nlrb_decisions(issue)
    elif statute == "FLSA":
        agency_guidance = search_dol_opinions(issue)

    # Circuit court precedent (employment cases often circuit-specific)
    circuit_cases = search_circuit_employment_cases(issue, your_circuit)

    # District court cases (employment litigation)
    district_cases = search_district_employment_cases(issue)

    return {
        "applicable_statute": statute,
        "agency_interpretation": agency_guidance,
        "circuit_precedent": circuit_cases,
        "district_court_cases": district_cases[:15],
        "state_law_supplement": search_state_employment_law(issue, your_state)
    }
```

## Administrative Law Research

**Primary Research Needs**:
- Enabling statutes
- Agency regulations (Code of Federal Regulations)
- Agency adjudications and rulings
- Judicial review standards
- APA (Administrative Procedure Act)

**Essential Resources**:
- **5 U.S.C. §§ 551-559** (Administrative Procedure Act)
- **Code of Federal Regulations** (C.F.R.)
- **Federal Register** (proposed and final rules)
- **Agency-specific databases**

**Research Strategy**:
```python
def administrative_law_research(agency, issue):
    """
    Administrative law research
    """
    # Enabling statute (agency's statutory authority)
    enabling_statute = get_agency_enabling_statute(agency)

    # Regulations
    cfr_provisions = search_cfr(agency, issue)

    # Agency adjudications
    agency_decisions = search_agency_decisions(agency, issue)

    # Judicial review
    # APA standards: arbitrary and capricious, substantial evidence
    judicial_review_cases = search_agency_judicial_review(agency, issue)

    return {
        "statutory_authority": enabling_statute,
        "regulations": cfr_provisions,
        "agency_interpretations": agency_decisions,
        "judicial_review_precedent": judicial_review_cases,
        "deference_standard": determine_deference_standard(agency, issue)
        # Chevron deference, Auer deference, Skidmore respect
    }
```

**Agency-Specific Resources**:

**SEC** (Securities and Exchange Commission):
- SEC.gov (official site)
- EDGAR (public company filings)
- SEC releases and interpretive guidance

**EPA** (Environmental Protection Agency):
- EPA.gov
- Environmental regulations (40 C.F.R.)

**FCC** (Federal Communications Commission):
- FCC.gov
- Communications regulations (47 C.F.R.)

**FDA** (Food and Drug Administration):
- FDA.gov
- Drug and device regulations (21 C.F.R.)

## Best Practices for Practice Area Research

### 1. Develop Practice Area Expertise

**Build Knowledge Base**:
- Subscribe to practice area newsletters
- Join practice area bar sections
- Attend CLEs in specialty area
- Read leading treatises cover-to-cover (or major portions)

### 2. Create Research Templates

**Standardized Workflows**:
```python
# Example: Contract dispute research template
CONTRACT_DISPUTE_TEMPLATE = {
    "formation_issues": ["offer", "acceptance", "consideration"],
    "interpretation_issues": ["plain meaning", "ambiguity", "extrinsic evidence"],
    "performance_issues": ["substantial performance", "material breach"],
    "remedies": ["damages", "specific performance", "restitution"],
    "defenses": ["statute of frauds", "unconscionability", "impossibility"],
    "ucc_applicability": "if sale of goods"
}

def contract_research_workflow(case_facts):
    for issue_category in CONTRACT_DISPUTE_TEMPLATE:
        research_issue(issue_category, case_facts)
```

### 3. Maintain Practice Area Research Files

**Knowledge Management**:
- Save research memoranda by issue
- Create authority databases by topic
- Bookmark key treatise sections
- Organize forms and templates

### 4. Track Developments

**Stay Current**:
- Set up KeyCite/Shepard's alerts for key cases
- Monitor agency rulemaking
- Read practice area blogs and newsletters
- Track pending legislation

### 5. Network with Specialists

**Leverage Expertise**:
- Join practice area listservs
- Consult with specialist co-counsel
- Attend practice area conferences
- Build referral network

---

*Practice area-specific research requires specialized knowledge of substantive law, procedural rules, agency guidance, and specialized resources unique to each field.*
