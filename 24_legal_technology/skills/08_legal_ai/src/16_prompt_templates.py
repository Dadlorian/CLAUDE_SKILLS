"""
Legal Prompt Templates Library
Reusable prompts for common legal AI tasks
"""

class LegalPromptLibrary:
    """Library of legal prompt templates"""

    @staticmethod
    def contract_review(contract_text, focus_areas=None):
        """Prompt for contract review"""

        focus = ', '.join(focus_areas) if focus_areas else "all key provisions"

        return f"""Review this contract focusing on: {focus}

Contract:
{contract_text}

Provide:
1. Risk assessment (Low/Medium/High)
2. Key findings with clause references
3. Recommendations for negotiation
4. Deal-breaker issues (if any)

Format your response with clear sections."""

    @staticmethod
    def clause_extraction(contract_text, clause_types):
        """Prompt for clause extraction"""

        return f"""Extract the following clause types from this contract:
{', '.join(clause_types)}

Contract:
{contract_text}

For each clause:
- Provide exact text
- Indicate section number
- Summarize key terms in plain language"""

    @staticmethod
    def legal_research(question, jurisdiction):
        """Prompt for legal research"""

        return f"""Research this legal question:

Question: {question}
Jurisdiction: {jurisdiction}

Provide:
1. Governing Law (statutes, regulations, case law)
2. Legal Standard (elements, factors, burden of proof)
3. Application to Facts
4. Conclusion with confidence level

Use proper legal citations."""

    @staticmethod
    def memo_generation(issue, facts, jurisdiction):
        """Prompt for legal memo"""

        return f"""Draft a legal memorandum:

ISSUE: {issue}
JURISDICTION: {jurisdiction}
FACTS: {facts}

Structure:
I. QUESTION PRESENTED
II. BRIEF ANSWER
III. FACTS
IV. DISCUSSION
   A. Legal Standard
   B. Analysis
   C. Counterarguments
V. CONCLUSION

Use proper legal writing conventions and citations."""

    @staticmethod
    def due_diligence(contract_text, transaction_type):
        """Prompt for due diligence review"""

        return f"""Due diligence review for {transaction_type}:

Contract:
{contract_text}

Red Flags (Must escalate):
- Change of control provisions
- Material liabilities
- Regulatory non-compliance
- Assignment restrictions affecting deal

Yellow Flags (Note but manageable):
- Unusual commercial terms
- Auto-renewal clauses
- Below-market pricing

Provide risk rating and deal impact analysis."""
