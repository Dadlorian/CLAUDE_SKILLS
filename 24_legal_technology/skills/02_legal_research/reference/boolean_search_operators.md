# Boolean Search Operators: Complete Technical Reference

## Overview

Boolean search operators form the foundation of precise legal research, enabling complex queries that combine keywords, phrases, and proximity requirements. This reference provides comprehensive coverage of Boolean logic, platform-specific syntax, and advanced search techniques.

## Boolean Logic Fundamentals

### Core Boolean Operators

#### AND
**Function**: Both terms must appear in the document
**Syntax**: `term1 AND term2` or `term1 & term2`
**Use Case**: Narrow search to documents containing all specified terms

```
Query: negligence AND damages
Matches: Documents containing both "negligence" AND "damages"
Does NOT match: Documents with only "negligence" or only "damages"
```

**Example Results**:
- "The plaintiff proved negligence resulting in damages" ✓
- "Negligence was established" ✗ (missing "damages")
- "Damages were awarded" ✗ (missing "negligence")

#### OR
**Function**: Either term (or both) must appear
**Syntax**: `term1 OR term2`
**Use Case**: Broaden search to capture synonyms or related concepts

```
Query: automobile OR vehicle OR car
Matches: Documents containing any of the three terms
```

**Synonym Expansion**:
```
contract OR agreement OR covenant
attorney OR lawyer OR counsel
negligence OR malpractice OR carelessness
```

#### NOT (AND NOT)
**Function**: Exclude documents containing specified term
**Syntax**: `term1 AND NOT term2` or `term1 BUT NOT term2`
**Use Case**: Filter out irrelevant results

```
Query: Apple AND NOT fruit
Matches: Documents about Apple Inc., not apple fruit
```

**WARNING**: Use NOT sparingly - may exclude relevant documents

### Parentheses (Grouping)

**Function**: Control order of operations
**Syntax**: `(term1 OR term2) AND term3`

```
Query: (negligence OR malpractice) AND (damages OR injury)
Logic: (A OR B) AND (C OR D)
Matches: Any combination where one term from each group appears

Examples that match:
- "negligence" + "damages" ✓
- "negligence" + "injury" ✓
- "malpractice" + "damages" ✓
- "malpractice" + "injury" ✓
```

**Complex Grouping**:
```
((contract OR agreement) AND breach) OR (specific AND performance)

Expands to:
- (contract AND breach) OR
- (agreement AND breach) OR
- (specific AND performance)
```

## Proximity Operators

### Westlaw Proximity Connectors

#### /s (Same Sentence)
**Function**: Terms must appear in the same sentence
**Syntax**: `term1 /s term2`

```
Query: negligence /s medical
Matches: "The medical negligence claim was dismissed"
Matches: "Negligence in the medical context requires..."
Does NOT match: "Negligence was established. The medical expert testified..."
```

**Use Cases**:
- Ensure close relationship between concepts
- Filter broad terms with context
- Find specific legal relationships

#### /p (Same Paragraph)
**Function**: Terms must appear in the same paragraph
**Syntax**: `term1 /p term2`

```
Query: summary /p judgment
Matches: Paragraph discussing summary judgment
Allows: More distance than /s but maintains topical connection
```

**Typical Use**:
```
statute /p limitations
jurisdiction /p personal
motion /p dismiss
```

#### /n (Within n Words)
**Function**: Terms within specified word distance
**Syntax**: `term1 /n term2` (n = number of words)

```
Query: breach /5 contract
Matches: "breach of contract" (3 words apart)
Matches: "breach of the employment contract" (4 words apart)
Does NOT match: "breach of duty under the parties' contract" (6 words apart)

Common values:
/1 - Adjacent words
/3 - Closely related
/5 - Related concepts
/10 - Same topic
/25 - Same section
```

**Ordered vs. Unordered**:
```
Westlaw:
term1 /5 term2 - Unordered (either direction)
term1 +5 term2 - Ordered (term1 must precede term2)

Example:
"statute /3 limitations" matches both:
- "statute of limitations"
- "limitations on the statute"

"statute +3 limitations" matches only:
- "statute of limitations"
```

### LexisNexis Proximity Connectors

#### w/s (Within Same Sentence)
**Syntax**: `term1 w/s term2`
**Equivalent**: Westlaw /s

#### w/p (Within Same Paragraph)
**Syntax**: `term1 w/p term2`
**Equivalent**: Westlaw /p

#### w/n (Within n Words)
**Syntax**: `term1 w/n term2`
**Equivalent**: Westlaw /n

```
Query: negligent w/5 misrepresentation
Matches: "negligent misrepresentation"
Matches: "negligent and fraudulent misrepresentation"
```

#### pre/n (Precedes Within n Words)
**Syntax**: `term1 pre/n term2`
**Function**: Ordered proximity (term1 must appear before term2)

```
Query: reasonable pre/3 person
Matches: "reasonable person standard"
Does NOT match: "person of reasonable judgment"
```

### Bloomberg Law Proximity

**Similar to Westlaw**:
- `/s` - Same sentence
- `/p` - Same paragraph
- `/n` - Within n words

### Casetext and Fastcase

**Natural Language + Boolean Hybrid**:
- Support basic Boolean (AND, OR, NOT)
- Proximity operators vary by platform
- Emphasis on natural language understanding

## Truncation and Wildcards

### Westlaw Truncation

#### ! (Unlimited Truncation)
**Function**: Matches any ending
**Syntax**: `root!`

```
Query: employ!
Matches: employ, employs, employed, employee, employer, employment, employing

Query: negligen!
Matches: negligent, negligence, negligently

Query: litigat!
Matches: litigate, litigates, litigated, litigating, litigation, litigator
```

**WARNING**: Can over-broaden
```
Query: contract!
Matches: contract, contracts, contracted, contracting, contractor, contractual
BUT ALSO: contracture (medical term) - may not want this
```

#### * (Single Character Wildcard)
**Function**: Represents exactly one character
**Syntax**: `term with * placeholder`

```
Query: wom*n
Matches: woman, women

Query: lab*r
Matches: labor, labour

Query: organi*ation
Matches: organization, organisation
```

### LexisNexis Truncation

#### ! (Unlimited Truncation)
**Same as Westlaw**

#### * (Unlimited Wildcard)
**Function**: Replaces one or more characters
**Syntax**: `term*`

```
Query: contract*
Matches: contract, contracts, contractual, contractor
```

#### ? (Single Character Wildcard)
**Function**: Replaces exactly one character
**Syntax**: `term with ? placeholder`

```
Query: wom?n
Matches: woman, women
```

### Universal Character
**Westcard**: `*` (single character)
**LexisNexis**: `?` (single character)

**Be careful with platform differences!**

## Phrase Searching

### Exact Phrase
**Syntax**: `"phrase in quotes"`

```
Query: "statute of limitations"
Matches: Exact phrase only (in that word order)
Does NOT match: "limitations established by the statute"
```

**Best Practices**:
```
Good phrase searches (high precision):
- "res ipsa loquitur"
- "breach of contract"
- "summary judgment"
- "personal jurisdiction"

Poor phrase searches (may miss variations):
- "the court held" (too common/variable)
- "it was determined" (passive variations)
```

### Phrase with Wildcard (Westlaw)
**Syntax**: `"phrase with *"`

```
Query: "motion * dismiss"
Matches: "motion to dismiss"
Matches: "motion for dismiss"

Query: "breach * contract"
Matches: "breach of contract"
Matches: "breach of the contract"
```

## Field and Segment Searching

### Westlaw Field Restrictions

**Common Fields**:
```
TI() - Title
JU() - Judge
AT() - Attorney
CO() - Court
DA() - Date
SY() - Synopsis
HE() - Headnote
TO() - Topic (Key Number)
```

**Examples**:
```
Query: TI(summary judgment) & jurisdiction
Meaning: "summary judgment" in title AND "jurisdiction" anywhere

Query: JU(Posner) & antitrust
Meaning: Cases authored by Judge Posner containing "antitrust"

Query: CO("Supreme Court") & DA(aft 2020)
Meaning: Supreme Court cases decided after 2020

Query: HE(negligence /s duty)
Meaning: Headnotes discussing negligence and duty in same sentence
```

**Date Restrictions**:
```
DA(2024) - Year 2024
DA(aft 2020) - After 2020
DA(bef 2015) - Before 2015
DA(2020 - 2024) - Range from 2020 to 2024
DA(aft 01/01/2023 & bef 12/31/2023) - Calendar year 2023
```

### LexisNexis Segment Searching

**Common Segments**:
```
TITLE() - Case name
COURT() - Court
DATE() - Decision date
JUDGE() or WRITTENBY() - Authoring judge
COUNSEL() - Attorney names
OVERVIEW() - Editorial summary
HEADNOTES() - Headnotes
DISSENT() - Dissenting opinion
CONCUR() - Concurring opinion
```

**Examples**:
```
Query: TITLE(Smith) AND negligence
Meaning: Cases named Smith involving negligence

Query: WRITTENBY(Ginsburg) AND gender
Meaning: Opinions authored by Justice Ginsburg discussing gender

Query: COUNSEL(Johnnie Cochran)
Meaning: Cases where Johnnie Cochran was counsel

Query: DISSENT(strict w/5 scrutiny)
Meaning: Dissenting opinions discussing "strict scrutiny"
```

## Advanced Search Strategies

### Concept Searching (Westlaw Natural Language)

**Conceptual Queries**:
```
Query: What are the elements of negligence in medical malpractice?
System: Translates to conceptual search, ranks by relevance

Behind the scenes:
- Identifies key concepts (negligence, elements, medical malpractice)
- Expands to related terms
- Ranks results by relevance
```

**When to Use**:
- Exploratory research
- Complex fact patterns
- When unsure of exact terminology

**When NOT to Use**:
- Precise term-of-art searches
- Known case citation
- Comprehensive research (may miss edge cases)

### Boolean Concept Combination

**Hybrid Approach**:
```
Query: (negligence malpractice) AND "standard of care" AND physician
Logic: Conceptual search for negligence/malpractice + required phrase + required term

Benefits:
- Flexibility of natural language
- Precision of Boolean requirements
```

### Citation Searching

**Westlaw**:
```
Query: 505 U.S. 144
System: Retrieves exact case

Query: 505 +5 144
System: Finds documents citing 505 U.S. 144 (proximity search on citation)
```

**Citing References**:
```
Westlaw: Use KeyCite to find all citing cases
LexisNexis: Use Shepard's to find all citing cases
Boolean: Use citation as search term in full-text search (less comprehensive)
```

### Table of Contents/Key Number Searching (Westlaw)

**Key Number System**:
```
Query: 272k1605
Meaning: Topic 272 (Negligence), Key Number 1605 (specific point of law)

Query: 170Ak1681
Meaning: Topic 170A (Automobiles), Key Number 1681

Benefits:
- Conceptual consistency (same Key Number across all cases)
- Comprehensive retrieval (all cases on same point)
- Jurisdiction-neutral (find persuasive authority)
```

**Combined with Boolean**:
```
Query: 272k1605 AND California
Meaning: All California cases with Negligence Key Number 1605

Query: 170Ak1681 & DA(aft 2020)
Meaning: Recent automobile cases on specific point
```

## Platform-Specific Syntax

### Westlaw Terms & Connectors Cheat Sheet

```
AND (&) - Both terms required
OR - Either term acceptable
/s - Same sentence
/p - Same paragraph
/n - Within n words
+n - Precedes within n words (ordered)
"phrase" - Exact phrase
! - Unlimited truncation
* - Single character wildcard
% - Grammatical variation
TI() - Title field
JU() - Judge field
DA() - Date field
TO() - Topic/Key Number
HE() - Headnote
SY() - Synopsis
```

**Example Complex Query**:
```
TI("United States" /3 Microsoft) & DA(aft 2000) & HE(antitrust /s monopoly)
```

### LexisNexis Syntax Cheat Sheet

```
AND - Both terms required
OR - Either term acceptable
w/s - Within same sentence
w/p - Within same paragraph
w/n - Within n words
pre/n - Precedes within n words
"phrase" - Exact phrase
! - Unlimited truncation
* - Wildcard
? - Single character wildcard
ATLEAST[n](term) - Term appears at least n times
TITLE() - Case name
COURT() - Court
DATE() - Date
JUDGE() - Judge
COUNSEL() - Attorney
HEADNOTES() - Headnotes
```

**Example Complex Query**:
```
TITLE(Google) AND ATLEAST3(patent) AND DATE(aft 2015) AND HEADNOTES(infringement w/10 damages)
```

### Google Scholar Case Law

**Limited Boolean**:
```
AND, OR, NOT (or -, minus sign)
"exact phrase"
court:supreme (court filter)
after:2020, before:2023 (date filters)
```

**Note**: Google Scholar uses primarily algorithmic relevance ranking

## Query Optimization Techniques

### 1. Start Broad, Then Narrow

**Iterative Refinement**:
```
Initial: negligence
↓
Refined: negligence /s medical
↓
More Refined: (negligence /s medical) /p "standard of care"
↓
Highly Refined: (negligence /s medical) /p "standard of care" & physician & DA(aft 2020)
```

### 2. Use Proximity to Add Context

**Instead of**:
```
negligence AND medical (too broad)
```

**Use**:
```
negligence /s medical (same sentence, tighter relationship)
negligence /5 medical (very close proximity)
```

### 3. Leverage Synonym Expansion

```
attorney OR lawyer OR counsel OR advocate
vehicle OR automobile OR car OR truck
contract OR agreement OR covenant OR compact
```

**Use thesaurus tools**:
- Westlaw: Thesaurus feature
- LexisNexis: Suggest Terms feature

### 4. Combine Restrictive and Expansive Elements

```
(negligence OR malpractice) /s (physician OR doctor OR surgeon) /p "standard of care"

Logic:
- Broad concept terms (negligence OR malpractice)
- Broad subject terms (physician OR doctor OR surgeon)
- Restrictive phrase ("standard of care")
```

### 5. Use Field Restrictions for Precision

```
Instead of: Smith (retrieves all cases mentioning "Smith")
Use: TI(Smith) (retrieves only cases with Smith in title)

Instead of: antitrust (may retrieve cases merely citing antitrust cases)
Use: HE(antitrust) (retrieves cases with antitrust in headnotes)
```

## Common Mistakes and Solutions

### Mistake 1: Over-Truncation

**Problem**:
```
Query: contract!
Unwanted: contracture, contracted (medical), contractor (construction)
```

**Solution**:
```
Query: contract OR contracts OR contractual
Better control over variations
```

### Mistake 2: Missing Parentheses

**Problem**:
```
Query: negligence OR malpractice AND medical
Interpreted as: negligence OR (malpractice AND medical)
Missing: (negligence AND medical) results
```

**Solution**:
```
Query: (negligence OR malpractice) AND medical
Explicit grouping ensures correct logic
```

### Mistake 3: Overuse of NOT

**Problem**:
```
Query: Apple AND NOT fruit
May exclude: "Apple Computer was the fruit of Steve Jobs' labor"
```

**Solution**:
- Use NOT sparingly
- Prefer positive terms: Apple /s (computer OR inc OR corporation)

### Mistake 4: Phrase Search Too Restrictive

**Problem**:
```
Query: "the court held that"
Misses: "the Court held that"
Misses: "the district court held that"
Misses: "this Court has held that"
```

**Solution**:
```
Query: court /5 held (more flexible)
```

### Mistake 5: Ignoring Grammatical Variations

**Problem**:
```
Query: "breach of contract"
Misses: "breached the contract"
Misses: "breaching the contract"
```

**Solution (Westlaw)**:
```
Query: breach! /5 contract (captures all forms)
```

## Testing and Validation

### Query Testing Protocol

```python
def test_boolean_query(query, expected_results, unexpected_results):
    """
    Validate Boolean query effectiveness
    """
    # Execute search
    results = execute_search(query)

    # Check precision (relevant results in top 10)
    top_10 = results[:10]
    precision = len([r for r in top_10 if r in expected_results]) / 10

    # Check recall (capturing known relevant cases)
    recall = len([r for r in expected_results if r in results]) / len(expected_results)

    # Check false positives (unwanted results)
    false_positives = len([r for r in top_10 if r in unexpected_results])

    return {
        "precision": precision,
        "recall": recall,
        "false_positive_rate": false_positives / 10,
        "recommendation": "refine" if precision < 0.7 or recall < 0.8 else "acceptable"
    }
```

### A/B Query Testing

```
Query A: negligence AND medical
Results: 50,000 cases (too broad)

Query B: negligence /s medical
Results: 12,000 cases (better)

Query C: (negligence /s medical) /p "standard of care"
Results: 2,500 cases (optimal for comprehensive research)

Query D: (negligence /s medical) /p "standard of care" & physician
Results: 800 cases (optimal for focused research)

Choose based on research goals (comprehensive vs. targeted)
```

## Practical Examples by Practice Area

### Contracts
```
(breach /3 contract) /p damages
"specific performance" /s (enforce! /3 agreement)
(material /3 breach) AND (contract OR agreement)
"anticipatory breach" /s repudiat!
```

### Torts
```
(negligence OR malpractice) /s "standard of care"
"strict liability" /p (defect! /5 product)
"intentional infliction" /5 "emotional distress"
(assault OR battery) /p intent!
```

### Civil Procedure
```
"summary judgment" /s (genuine /3 "material fact")
"personal jurisdiction" /p "minimum contacts"
"forum non conveniens" /s (dismiss! OR transfer)
"class action" /p (certif! /10 requirement!)
```

### Constitutional Law
```
"strict scrutiny" /p (compelling /5 interest)
"equal protection" /s (suspect /3 classification)
"due process" /p (procedural OR substantive)
"dormant commerce clause" /s discriminat!
```

### Intellectual Property
```
(patent /s infringement) /p (literal OR "doctrine of equivalents")
trademark /s (likelihood /3 confusion)
copyright /s "fair use" /p (transform! OR parody)
"trade secret" /s (misappropriat! OR disclosure)
```

---

*Master Boolean search operators to conduct precise, efficient legal research across all major platforms.*
