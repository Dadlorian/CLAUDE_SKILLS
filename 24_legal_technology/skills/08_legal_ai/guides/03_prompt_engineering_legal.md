# Prompt Engineering for Legal AI

## Core Principles

### 1. Specificity and Context
```python
# Bad prompt
"Analyze this contract"

# Good prompt
"""Analyze this Master Services Agreement under Delaware law for:
1. Liability risks (caps, indemnification, consequential damages)
2. Termination provisions
3. IP ownership and licensing
4. Payment terms and disputes

For each issue, indicate:
- Risk level (low/medium/high)
- Specific clause location
- Recommended modifications
"""
```

### 2. Role-Based Prompting
```python
system_prompt = """You are an experienced corporate attorney specializing in:
- Contract review and negotiation
- Delaware corporate law
- M&A transactions

Your analysis should be:
- Legally accurate and well-cited
- Practical and business-focused
- Clear for non-lawyer stakeholders

Always cite specific contract provisions and applicable law."""
```

### 3. Few-Shot Learning
```python
prompt = """Review this indemnification clause for risk.

Example 1:
Clause: "Supplier shall indemnify Client for all claims."
Analysis: HIGH RISK - Unlimited scope, no exclusions. Recommend adding carve-outs for Client's negligence.

Example 2:
Clause: "Supplier indemnifies for third-party IP claims only, capped at contract value."
Analysis: MEDIUM RISK - Limited scope but check if cap is adequate given IP exposure.

Now review this clause:
{clause_text}
"""
```

### 4. Chain-of-Thought for Legal Reasoning
```python
prompt = """Analyze whether this non-compete is enforceable.

Think through this step-by-step:
1. Identify the jurisdiction (determines applicable law)
2. State the legal standard for non-compete enforceability in that jurisdiction
3. Apply each element of the test to the facts
4. Consider any employer-favorable factors
5. Consider any employee-favorable factors
6. Reach conclusion with confidence level

Non-compete clause:
{clause}

Employee facts:
{facts}
"""
```

## Legal-Specific Patterns

### Contract Review
```python
contract_review_prompt = """
CONTRACT REVIEW CHECKLIST

Document: {contract_type}
Parties: {parties}
Jurisdiction: {jurisdiction}

Review for:

FORMATION ISSUES:
□ Valid offer and acceptance?
□ Consideration present?
□ Capacity of parties?
□ Proper signatures and dates?

RISK PROVISIONS:
□ Limitation of liability (cap amount, exclusions)
□ Indemnification (scope, procedures, caps)
□ Insurance requirements (types, amounts, certificates)
□ Warranties (express, implied, disclaimers)

COMMERCIAL TERMS:
□ Payment terms (amount, schedule, method)
□ Delivery/performance obligations
□ Acceptance criteria
□ Price adjustments or escalations

TERMINATION & DISPUTE:
□ Term and renewal provisions
□ Termination rights (for cause, for convenience)
□ Notice requirements
□ Dispute resolution (litigation, arbitration, mediation)
□ Governing law and venue

Provide findings for each category with risk ratings.
"""
```

### Legal Research
```python
research_prompt = """
LEGAL RESEARCH ASSIGNMENT

Issue: {legal_question}
Jurisdiction: {jurisdiction}
Relevant Facts: {facts}

Please research and provide:

1. GOVERNING LAW
   - Primary authority (statutes, regulations)
   - Leading cases
   - Current status (any pending changes?)

2. LEGAL STANDARD
   - Elements or factors
   - Burden of proof
   - Any split of authority

3. APPLICATION TO FACTS
   - How law applies to our facts
   - Strongest arguments for each side
   - Potential outcomes

4. STRATEGIC CONSIDERATIONS
   - Litigation risk assessment
   - Settlement value range
   - Recommended next steps

Format with Bluebook citations.
"""
```

### Due Diligence
```python
due_diligence_prompt = """
M&A DUE DILIGENCE REVIEW

Review these {count} contracts for deal risks:

RED FLAGS (Must escalate):
- Change of control provisions affecting deal
- Material liabilities (>$100K)
- Regulatory non-compliance
- Missing consents required for assignment

YELLOW FLAGS (Note but may be manageable):
- Auto-renewal clauses
- Pricing below market
- Unusual terms vs. industry standard

GREEN FLAGS (Favorable terms):
- Termination for convenience
- Strong IP protections
- Limited liability

For each contract, provide:
1. Risk rating (Red/Yellow/Green)
2. Key findings
3. Financial impact (if quantifiable)
4. Required actions
"""
```

## Prompt Templates Library

```python
class LegalPromptLibrary:
    """Reusable legal prompts"""

    @staticmethod
    def clause_extraction(contract_text, clause_types):
        return f"""Extract the following clause types from this contract:
{', '.join(clause_types)}

For each clause:
- Provide exact text
- Indicate section number
- Summarize key terms

Contract:
{contract_text}
"""

    @staticmethod
    def risk_assessment(contract, risk_profile="standard"):
        profiles = {
            "conservative": "Flag any deviation from our standard terms",
            "standard": "Flag material risks (>$50K exposure or significant legal issues)",
            "aggressive": "Flag only deal-breaker issues"
        }

        return f"""Assess risks in this contract using a {risk_profile} risk profile.

Risk Profile: {profiles[risk_profile]}

Contract:
{contract}

Provide:
1. Overall risk score (0-100)
2. Top 5 risks with impact and likelihood
3. Recommended approach (approve/negotiate/reject)
"""

    @staticmethod
    def redline_generation(original_clause, company_position):
        return f"""Generate redline for this clause to align with our position.

Original Clause:
{original_clause}

Our Position:
{company_position}

Provide:
1. Strikethrough original language [DELETED: text]
2. Add new language [ADDED: text]
3. Explain rationale for changes
4. Indicate if change is material or minor
"""
```

## Validation Prompts

```python
citation_check_prompt = """
CITATION VERIFICATION

Review this legal analysis and verify all citations:

{legal_text}

For each citation:
1. Verify it exists (check format)
2. Confirm it supports the proposition cited
3. Note if citation is outdated or overruled
4. Flag any hallucinated citations

Provide:
- List of verified citations ✓
- List of problematic citations ✗
- Recommended replacements
"""

hallucination_check = """
FACTUAL ACCURACY CHECK

Compare this AI-generated legal analysis against source documents:

AI Analysis:
{ai_output}

Source Documents:
{source_docs}

Identify:
1. Claims not supported by sources
2. Misstatements of law or fact
3. Incorrect citations
4. Logical errors in reasoning

Rate overall accuracy (0-100%)
"""
```

## Best Practices

1. **Always specify jurisdiction** - Legal rules vary dramatically
2. **Request citations** - Include "cite relevant authority"
3. **Define output format** - Structured output is easier to validate
4. **Set confidence thresholds** - "Only answer if >80% confident"
5. **Include safety rails** - "If unsure, say so and recommend research"

```python
# Template with best practices
best_practice_template = """
[ROLE]
You are a legal assistant specializing in {practice_area}.

[TASK]
{task_description}

[CONTEXT]
Jurisdiction: {jurisdiction}
Applicable law: {relevant_law}
Key facts: {facts}

[CONSTRAINTS]
- Cite all legal authority (Bluebook format)
- If answer requires research beyond provided context, explicitly state that
- Indicate confidence level (high/medium/low)
- Flag any assumptions made

[FORMAT]
{output_format}

[SAFETY]
If you are not confident in this analysis, state what additional research is needed.
"""
```
