# Secondary Sources Reference Guide

## Overview

Secondary sources provide expert analysis, commentary, and synthesis of primary law. They are invaluable for understanding complex legal areas, finding primary authority, and developing persuasive arguments. This reference covers major secondary sources, access methods, and strategic use.

## Types of Secondary Sources

### Legal Encyclopedias

#### American Jurisprudence 2d (Am. Jur. 2d)

**Publisher**: Thomson Reuters (Westlaw)
**Scope**: National in scope, comprehensive legal encyclopedia
**Coverage**: 400+ topics covering all major areas of law

**Organization**:
- Alphabetical by topic
- Detailed table of contents
- Comprehensive index
- Cross-references to related topics

**Content Features**:
- Overview of legal principles
- Citations to primary authority (cases, statutes)
- Practice tips and forms
- Regularly updated

**Research Strategy**:
```python
def research_with_am_jur(legal_issue):
    """
    Use Am. Jur. 2d for foundational research
    """
    # Step 1: Identify relevant topic
    topic = identify_am_jur_topic(legal_issue)
    # Example: "Negligence" or "Contracts"

    # Step 2: Review table of contents for specific section
    relevant_sections = get_am_jur_sections(topic, legal_issue)

    # Step 3: Read overview and analysis
    analysis = read_am_jur_section(relevant_sections[0])

    # Step 4: Extract cited authorities
    primary_authorities = extract_citations(analysis)

    # Step 5: Validate and research primary authorities
    validated_authorities = [
        keycite_check(auth) for auth in primary_authorities
    ]

    return {
        "overview": analysis["text"],
        "key_authorities": validated_authorities,
        "related_topics": analysis["cross_references"]
    }
```

**Westlaw Access**: AM-JUR database
**Citation Format**: 61A Am. Jur. 2d Physician, Surgeons, Etc. § 360

**Best Use Cases**:
- Unfamiliar legal topic (get overview)
- Identify key cases and statutes
- Understand majority vs. minority rules
- Find practice forms

#### Corpus Juris Secundum (C.J.S.)

**Publisher**: Thomson Reuters (Westlaw)
**Scope**: National encyclopedia, more comprehensive than Am. Jur. 2d
**Distinguishing Feature**: Cites ALL cases (not just key cases)

**Comparison to Am. Jur. 2d**:
| Feature | Am. Jur. 2d | C.J.S. |
|---------|-------------|--------|
| Citation Approach | Key cases only | Comprehensive (all cases) |
| Length | More concise | More extensive |
| Analysis | Practical focus | Scholarly approach |
| Updates | More frequent | Less frequent |

**When to Use C.J.S.**:
- Need exhaustive case citations
- Academic research
- Comprehensive survey of precedent
- When Am. Jur. 2d insufficient

**Westlaw Access**: CJS database

#### State-Specific Encyclopedias

**Major State Encyclopedias**:

**California Jurisprudence 3d (Cal. Jur. 3d)**:
- Comprehensive California law encyclopedia
- State-specific precedent and statutes
- Practice-oriented
- Westlaw: CA-JUR

**Florida Jurisprudence 2d (Fla. Jur. 2d)**:
- Florida-specific legal encyclopedia
- Extensive citations to Florida cases and statutes

**Illinois Law and Practice**:
- Illinois-focused encyclopedia

**New York Jurisprudence 2d (NY Jur. 2d)**:
- New York law encyclopedia
- Particularly valuable given NY's unique legal system

**Pennsylvania Law Encyclopedia**

**Texas Jurisprudence 3d (Tex. Jur. 3d)**:
- Texas law encyclopedia

**Research Advantage**:
```
State Encyclopedia > National Encyclopedia
When:
- State-specific practice
- Need state precedent (not persuasive authority)
- State has unique legal rules
- Want state-specific practice tips
```

### Legal Treatises

#### What Is a Treatise?

**Definition**: Scholarly, in-depth analysis of specific legal subject
**Authors**: Leading experts, professors, practitioners
**Depth**: Much more detailed than encyclopedias
**Authority**: Often cited by courts (highly persuasive)

#### Major Treatises by Practice Area

**Contracts**:
- **Williston on Contracts** (comprehensive, multi-volume)
- **Corbin on Contracts** (scholarly, influential)
- **Farnsworth on Contracts** (modern, practical)

**Torts**:
- **Prosser and Keeton on Torts** (foundational)
- **Harper, James and Gray on Torts** (comprehensive)
- **Dobbs Law of Torts** (modern synthesis)

**Evidence**:
- **Wigmore on Evidence** (classic, comprehensive)
- **McCormick on Evidence** (practitioner-focused)
- **Mueller & Kirkpatrick Federal Evidence**

**Civil Procedure**:
- **Wright & Miller, Federal Practice and Procedure** (authoritative)
- **Moore's Federal Practice** (comprehensive)

**Constitutional Law**:
- **Tribe, American Constitutional Law** (leading treatise)
- **Nowak & Rotunda, Constitutional Law** (widely used)
- **Chemerinsky, Constitutional Law** (modern, clear)

**Criminal Law**:
- **LaFave, Criminal Law** (definitive)
- **Wayne LaFave, Search and Seizure** (4th Amendment authority)

**Intellectual Property**:
- **Nimmer on Copyright** (copyright bible)
- **Chisum on Patents** (patent law authority)
- **McCarthy on Trademarks** (trademark authority)

**Corporate Law**:
- **Fletcher Cyclopedia of Corporations** (comprehensive)
- **Folk on Delaware General Corporation Law** (Delaware-specific)

**Tax**:
- **Mertens Law of Federal Income Taxation**
- **Bittker & Eustice, Federal Income Taxation of Corporations**

**Commercial Law**:
- **White & Summers, Uniform Commercial Code** (UCC authority)

**Research Strategy with Treatises**:
```python
def treatise_research_workflow(legal_issue, practice_area):
    """
    Strategic use of treatises
    """
    # Step 1: Identify leading treatise
    treatise = get_leading_treatise(practice_area)

    # Step 2: Use index/table of contents
    relevant_sections = search_treatise(treatise, legal_issue)

    # Step 3: Read analysis
    expert_analysis = read_treatise_section(relevant_sections)

    # Step 4: Extract authorities cited by treatise
    authorities = extract_treatise_citations(expert_analysis)

    # Step 5: Note any critique or alternative approaches
    alternative_views = expert_analysis["scholarly_debate"]

    # Step 6: Check if courts cite this treatise
    citing_cases = find_cases_citing_treatise(treatise, relevant_sections)

    return {
        "expert_analysis": expert_analysis["text"],
        "primary_authorities": authorities,
        "alternative_approaches": alternative_views,
        "judicial_acceptance": len(citing_cases),
        "citability": "highly_persuasive" if len(citing_cases) > 50 else "persuasive"
    }
```

**Citation Format**:
- 8 Wigmore, Evidence § 2285 (McNaughton rev. 1961)
- 1 Nimmer on Copyright § 1.01[A] (2024)

### American Law Reports (ALR)

**Publisher**: Thomson Reuters (formerly Lawyers Co-op)
**Series**: ALR, ALR2d, ALR3d, ALR4th, ALR5th, ALR6th, ALR7th, ALR Federal

**Unique Feature**: Annotation format
- Reported case (illustrative case on topic)
- Extensive annotation (comprehensive survey of law on specific issue)

**ALR Annotation Structure**:
```
Table of Contents
§ 1 - Introduction/Scope
§ 2 - Summary and Comment
§ 3 - Practice Pointers
§§ 4-20 - Legal Analysis (organized by jurisdiction or sub-issue)
§ 21 - Conclusion
```

**Research Value**:
- Comprehensive survey of law across all jurisdictions
- Identifies majority vs. minority rules
- Citations to cases from all 50 states
- Practice tips

**Access**:
- Westlaw: ALR database
- LexisNexis: ALR library

**Research Strategy**:
```python
def alr_annotation_research(narrow_legal_issue):
    """
    Use ALR for comprehensive jurisdictional survey
    """
    # Step 1: Find relevant annotation
    annotation = search_alr(narrow_legal_issue)

    if not annotation:
        return "No ALR annotation on this specific issue"

    # Step 2: Read summary and comment
    overview = annotation["summary_and_comment"]

    # Step 3: Identify majority rule
    majority_rule = overview["majority_approach"]

    # Step 4: Find cases from your jurisdiction
    jurisdiction_cases = annotation.filter_by_jurisdiction(your_jurisdiction)

    # Step 5: Identify minority/alternative rules
    minority_rules = overview["minority_approaches"]

    # Step 6: Review practice pointers
    practice_tips = annotation["practice_pointers"]

    return {
        "issue_overview": overview,
        "majority_rule": majority_rule,
        "your_jurisdiction_law": jurisdiction_cases,
        "alternative_approaches": minority_rules,
        "practice_guidance": practice_tips
    }
```

**When to Use ALR**:
- Narrow, specific legal issue
- Need survey of all jurisdictions
- Want to identify majority vs. minority rule
- Looking for persuasive authority from other states

### Restatements of the Law

**Publisher**: American Law Institute (ALI)
**Purpose**: Distill common law into clear, systematic principles

**Major Restatements**:
- **Restatement (Second) of Contracts** (most widely adopted)
- **Restatement (Second) of Torts**
- **Restatement (Third) of Torts** (Liability for Physical and Emotional Harm)
- **Restatement (Third) of Torts** (Products Liability)
- **Restatement (Second) of Agency**
- **Restatement (Third) of Agency**
- **Restatement (Second) of Conflict of Laws**
- **Restatement (Third) of Property**
- **Restatement (Third) of Restitution and Unjust Enrichment**
- **Restatement (Third) of Torts** (Intentional Torts to Persons)

**Structure**:
```
Black Letter Rule (concise statement of legal principle)
  ↓
Comments (explanation and elaboration)
  ↓
Illustrations (hypothetical examples)
  ↓
Reporter's Notes (citations to cases and other authority)
```

**Authority Level**:
- Not binding (secondary source)
- Highly persuasive
- Many states adopt Restatement provisions as law
- Frequently cited by courts

**Research Strategy**:
```python
def restatement_research(legal_issue, jurisdiction):
    """
    Research with Restatements
    """
    # Step 1: Identify relevant Restatement section
    restatement_section = find_restatement_section(legal_issue)

    # Step 2: Read black letter rule
    rule = restatement_section["black_letter_rule"]

    # Step 3: Review comments and illustrations
    analysis = restatement_section["comments"]
    examples = restatement_section["illustrations"]

    # Step 4: Check if jurisdiction adopted this Restatement provision
    adoption_status = check_restatement_adoption(jurisdiction, restatement_section)

    # Step 5: Find cases citing Restatement
    citing_cases = find_cases_citing_restatement(restatement_section, jurisdiction)

    return {
        "restatement_rule": rule,
        "explanatory_comments": analysis,
        "examples": examples,
        "adopted_in_jurisdiction": adoption_status["adopted"],
        "citing_cases": citing_cases,
        "authority_level": "binding" if adoption_status["adopted"] else "persuasive"
    }
```

**Citation Format**:
- Restatement (Second) of Contracts § 90 (1981)
- Restatement (Third) of Torts: Liab. for Physical & Emotional Harm § 7 (2010)

### Law Review Articles

**Types**:
- **Lead Articles**: Scholarly analysis by professors or experts
- **Student Notes and Comments**: Student-authored pieces
- **Case Notes**: Analysis of recent decisions
- **Book Reviews**: Review of legal scholarship

**Top Law Reviews** (highly cited):
- Harvard Law Review
- Yale Law Journal
- Stanford Law Review
- Columbia Law Review
- University of Chicago Law Review
- NYU Law Review
- Michigan Law Review
- Virginia Law Review
- California Law Review
- Pennsylvania Law Review

**Specialized Journals**:
- Harvard Civil Rights-Civil Liberties Law Review
- Yale Journal on Regulation
- Stanford Technology Law Review
- NYU Journal of Intellectual Property & Entertainment Law

**Research Value**:
- Cutting-edge legal analysis
- Comprehensive citation to authority
- Policy arguments
- Critique of existing law
- Proposals for reform

**Access**:
- **Westlaw**: TP-ALL (all law reviews)
- **LexisNexis**: Law Reviews, Combined
- **HeinOnline**: Comprehensive law review database
- **SSRN** (Social Science Research Network): Preprints and working papers
- **Google Scholar**: Free access to many articles

**Research Strategy**:
```python
def law_review_research(legal_issue):
    """
    Strategic use of law reviews
    """
    # Step 1: Search for relevant articles
    articles = search_law_reviews(legal_issue)

    # Step 2: Prioritize by journal prestige and citation count
    ranked_articles = rank_by_prestige_and_citations(articles)

    # Step 3: Read abstracts/introductions
    relevant_articles = filter_most_relevant(ranked_articles)

    # Step 4: Mine footnotes for primary authority
    authorities_from_footnotes = extract_citations_from_articles(relevant_articles)

    # Step 5: Check if courts cite these articles
    judicial_citations = find_cases_citing_law_review(relevant_articles)

    return {
        "key_articles": relevant_articles[:5],
        "primary_authorities": authorities_from_footnotes,
        "judicial_acceptance": judicial_citations,
        "scholarly_consensus": identify_consensus(relevant_articles)
    }
```

**Citation Format**:
- Richard A. Posner, *An Economic Analysis of Contract Law*, 8 J. Legal Stud. 83 (1979)

### Practice Guides and Manuals

#### Practice-Oriented Secondary Sources

**Westlaw Practical Law**:
- Practice notes (how-to guidance)
- Standard documents and forms
- Checklists
- Timelines
- Resource kits

**LexisNexis Practice Advisor**:
- Similar to Practical Law
- Practice notes by area
- Forms and templates

**State-Specific Practice Guides**:

**California**:
- Rutter Group Practice Guides (highly practical)
- CEB (Continuing Education of the Bar) publications
- Witkin treatises (substantive law)

**New York**:
- New York Practice Series (various authors)
- McKinney's practice commentaries

**Texas**:
- State Bar of Texas practice manuals
- Texas Practice Series

**Federal**:
- Federal Procedure, Lawyers Edition
- Federal Forms
- Federal Litigation Guide

**Research Value**:
- Step-by-step guidance
- Forms and templates
- Practical tips
- Citations to authority

**Use Case**:
```python
def practice_guide_research(procedure_question):
    """
    Use practice guides for procedural guidance
    """
    # Step 1: Identify relevant practice guide
    guide = find_practice_guide(procedure_question)

    # Step 2: Review practice note
    guidance = guide["practice_note"]

    # Step 3: Get checklist
    checklist = guidance["checklist"]

    # Step 4: Download forms
    forms = guidance["standard_forms"]

    # Step 5: Review cited authority
    authority = guidance["authorities"]

    return {
        "step_by_step_guidance": guidance["instructions"],
        "checklist": checklist,
        "forms": forms,
        "legal_authority": authority,
        "practice_tips": guidance["tips"]
    }
```

### Legal Dictionaries and Words & Phrases

**Black's Law Dictionary**:
- Definitive legal dictionary
- Definitions of legal terms of art
- Citations to cases defining terms
- Westlaw: BLACKS

**Words and Phrases**:
- Multi-volume set of judicial definitions
- Organizes definitions by term
- Citations to all cases defining each term
- Westlaw: WORDS (Words and Phrases)

**Use Case**:
```python
def define_legal_term(term):
    """
    Research legal definition
    """
    # Black's Law Dictionary definition
    blacks_def = search_blacks_law_dictionary(term)

    # Find cases defining term
    judicial_definitions = search_words_and_phrases(term)

    # Find definitions in your jurisdiction
    jurisdiction_definitions = [
        jd for jd in judicial_definitions
        if jd["jurisdiction"] == your_jurisdiction
    ]

    return {
        "blacks_definition": blacks_def,
        "judicial_definitions": jurisdiction_definitions,
        "common_usage": blacks_def["common_meaning"],
        "technical_meaning": blacks_def["legal_meaning"]
    }
```

## Strategic Use of Secondary Sources

### Research Workflow with Secondary Sources

**Phase 1: Understanding (Unfamiliar Area)**:
```
1. Legal Encyclopedia (Am. Jur. 2d or state encyclopedia)
   → Get overview of law
   → Identify key concepts
   → Find initial cases/statutes

2. Leading Treatise
   → Deep dive into specific issue
   → Expert analysis
   → Comprehensive authorities

3. Restatement (if applicable)
   → Black letter rule
   → Jurisdictional adoption status
```

**Phase 2: Comprehensive Research**:
```
4. ALR Annotation (if available)
   → Survey of all jurisdictions
   → Majority vs. minority rules
   → Comprehensive case citations

5. Law Review Articles
   → Scholarly analysis
   → Policy arguments
   → Critique of current law
   → Mine footnotes for authorities
```

**Phase 3: Practice Application**:
```
6. Practice Guides
   → Procedural guidance
   → Forms and checklists
   → Practical tips
```

### When to Cite Secondary Sources

**Appropriate to Cite**:
- No primary authority on point
- Secondary source widely accepted (e.g., leading treatise)
- Policy argument (law review for persuasive policy analysis)
- Definition of legal term (Black's Law Dictionary)
- Expert analysis adds value

**Authority Hierarchy**:
```
1. Mandatory primary authority (controlling jurisdiction)
2. Persuasive primary authority (other jurisdictions)
3. Leading treatises (highly persuasive secondary)
4. Restatements (if adopted by jurisdiction)
5. Law review articles (persuasive analysis)
6. Legal encyclopedias (least persuasive secondary)
```

**Citation Example**:
```
"As Professor Nimmer explains, '[quote].' 1 Nimmer on Copyright § 1.01[A] (2024)."

"The Restatement provides that '[rule].' Restatement (Second) of Contracts § 90."

"Courts have recognized that '[proposition].' See 61A Am. Jur. 2d Physicians § 360."
```

### Mining Secondary Sources for Primary Authority

**Most Valuable Feature**: Citations to primary authority

**Strategy**:
```python
def mine_secondary_sources_for_authority(legal_issue):
    """
    Use secondary sources to find primary authority
    """
    # Step 1: Find relevant secondary sources
    treatise = find_treatise(legal_issue)
    alr = find_alr_annotation(legal_issue)
    law_review = search_law_reviews(legal_issue)

    # Step 2: Extract all cited primary authorities
    treatise_cites = extract_citations(treatise)
    alr_cites = extract_citations(alr)
    law_review_cites = extract_citations(law_review)

    # Step 3: Combine and deduplicate
    all_authorities = deduplicate(treatise_cites + alr_cites + law_review_cites)

    # Step 4: Filter to jurisdiction
    jurisdiction_authorities = filter_by_jurisdiction(all_authorities, your_jurisdiction)

    # Step 5: Validate currency
    validated = [keycite_check(auth) for auth in jurisdiction_authorities]

    # Step 6: Rank by importance
    ranked = rank_by_importance(validated)

    return ranked[:25]  # Top 25 authorities
```

## Best Practices

### 1. Start with Secondary Sources for Unfamiliar Topics

**Why**:
- Provides context and overview
- Identifies key issues and terminology
- Leads to primary authority more efficiently than blind searching

### 2. Update Secondary Sources

**Check Publication Date**:
- Law changes rapidly
- Ensure secondary source reflects current law
- Supplement with recent cases

### 3. Validate Citations from Secondary Sources

**Always**:
- KeyCite/Shepardize cases cited in secondary sources
- Verify case still represents good law
- Confirm proposition accurately reflects case holding

### 4. Use Multiple Secondary Sources

**Cross-Validate**:
- Different secondary sources may present different perspectives
- Scholarly debate may exist
- Ensure comprehensive understanding

### 5. Transition from Secondary to Primary

**Remember**:
- Secondary sources are research tools
- Primary authority is what courts will follow
- Brief/memo should rely primarily on binding primary authority
- Secondary sources supplement and support

---

*Secondary sources are essential research tools providing expert analysis, comprehensive citations, and efficient pathways to primary authority.*
