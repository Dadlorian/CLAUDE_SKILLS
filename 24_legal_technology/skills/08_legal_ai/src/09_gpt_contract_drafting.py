"""
GPT-based Contract Drafting Assistant
Generate contract drafts using GPT-4 with legal templates
"""

import openai
from typing import Dict

class ContractDrafter:
    """AI-powered contract drafting"""

    def __init__(self, api_key: str):
        openai.api_key = api_key

    def draft_nda(self, params: Dict) -> str:
        """Generate NDA from parameters"""

        prompt = f"""Draft a {params.get('type', 'mutual')} Non-Disclosure Agreement with:

Disclosing Party: {params['disclosing_party']}
Receiving Party: {params['receiving_party']}
Effective Date: {params['effective_date']}
Purpose: {params['purpose']}
Confidentiality Period: {params['confidentiality_period']}
Governing Law: {params['governing_law']}

Include:
1. Definition of Confidential Information
2. Obligations of Receiving Party
3. Exclusions from Confidential Information
4. Term and Termination
5. Return of Information
6. Remedies
7. Governing Law and Jurisdiction

Use professional legal language and Delaware law conventions."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert corporate attorney drafting contracts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    def draft_clause(self, clause_type: str, requirements: str) -> str:
        """Draft specific contract clause"""

        prompt = f"""Draft a {clause_type} clause with the following requirements:

{requirements}

The clause should be:
- Legally enforceable
- Clear and unambiguous
- Balanced and fair
- Include any necessary definitions

Format as a complete contract provision."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert contract attorney."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content
