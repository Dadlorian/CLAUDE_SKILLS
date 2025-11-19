"""
Research Memo Generator
Generates legal research memoranda from research findings
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemoSection:
    """Section of research memo"""
    title: str
    content: str


@dataclass
class ResearchMemo:
    """Legal research memorandum"""
    to: str
    from_: str
    date: str
    re: str  # subject
    question_presented: str
    brief_answer: str
    facts: str
    legal_analysis: str
    conclusion: str
    recommendations: Optional[List[str]] = None


class ResearchMemoGenerator:
    """
    Generates legal research memoranda
    """

    def __init__(self, author_name: str = "Legal Research Team"):
        """
        Initialize memo generator

        Args:
            author_name: Default author name
        """
        self.author_name = author_name
        self.memo_template = self._load_template()

    @staticmethod
    def _load_template() -> str:
        """Load memo template"""
        return """
{header}

TO:       {to}
FROM:     {from_}
DATE:     {date}
RE:       {re}

QUESTION PRESENTED
==================
{question_presented}

BRIEF ANSWER
============
{brief_answer}

FACTS
=====
{facts}

LEGAL ANALYSIS
==============
{legal_analysis}

CONCLUSION
==========
{conclusion}

{recommendations_section}
"""

    def create_memo(self,
                    to: str,
                    re: str,
                    question_presented: str,
                    facts: str,
                    legal_analysis: str,
                    conclusion: str,
                    brief_answer: Optional[str] = None,
                    recommendations: Optional[List[str]] = None) -> ResearchMemo:
        """
        Create a research memo

        Args:
            to: Recipient
            re: Subject
            question_presented: Legal question
            facts: Factual background
            legal_analysis: Legal analysis
            conclusion: Conclusion
            brief_answer: Brief answer to question
            recommendations: Recommendations

        Returns:
            ResearchMemo object
        """
        if not brief_answer:
            brief_answer = self._generate_brief_answer(conclusion)

        memo = ResearchMemo(
            to=to,
            from_=self.author_name,
            date=datetime.now().strftime("%B %d, %Y"),
            re=re,
            question_presented=question_presented,
            brief_answer=brief_answer,
            facts=facts,
            legal_analysis=legal_analysis,
            conclusion=conclusion,
            recommendations=recommendations or []
        )

        logger.info(f"Created memo: {re}")
        return memo

    def format_memo(self, memo: ResearchMemo) -> str:
        """
        Format memo as text document

        Args:
            memo: ResearchMemo object

        Returns:
            Formatted memo text
        """
        recommendations_section = ""
        if memo.recommendations:
            recs = "\n".join([f"  {i+1}. {rec}" for i, rec in enumerate(memo.recommendations)])
            recommendations_section = f"\nRECOMMENDATIONS\n===============\n{recs}"

        formatted = self.memo_template.format(
            header="LEGAL RESEARCH MEMORANDUM",
            to=memo.to,
            from_=memo.from_,
            date=memo.date,
            re=memo.re,
            question_presented=memo.question_presented,
            brief_answer=memo.brief_answer,
            facts=memo.facts,
            legal_analysis=memo.legal_analysis,
            conclusion=memo.conclusion,
            recommendations_section=recommendations_section
        )

        return formatted

    @staticmethod
    def _generate_brief_answer(conclusion: str) -> str:
        """
        Generate brief answer from conclusion

        Args:
            conclusion: Conclusion text

        Returns:
            Brief answer
        """
        # Extract first sentence as brief answer
        sentences = conclusion.split('.')
        if sentences:
            answer = sentences[0].strip()
            if answer:
                return answer + "."
        return "Based on applicable law and facts, see analysis below."

    def add_authorities(self, memo: ResearchMemo, authorities: List[Dict]) -> str:
        """
        Add legal authorities section to memo

        Args:
            memo: ResearchMemo object
            authorities: List of authority dicts with 'citation' and 'description'

        Returns:
            Memo with authorities section
        """
        authorities_section = "\nAUTHORITIES\n===========\n"
        for auth in authorities:
            authorities_section += f"\n{auth.get('citation', 'Unknown')}"
            if auth.get('description'):
                authorities_section += f"\n  {auth['description']}"

        formatted = self.format_memo(memo)
        return formatted + authorities_section

    def generate_outline(self, question: str, authorities: List[str]) -> str:
        """
        Generate research outline

        Args:
            question: Legal question
            authorities: Relevant authorities

        Returns:
            Outline text
        """
        outline = f"""RESEARCH OUTLINE

Question: {question}

AUTHORITIES TO RESEARCH:
"""
        for i, auth in enumerate(authorities, 1):
            outline += f"\n{i}. {auth}"

        outline += """

STRUCTURE:
I. Question Presented
II. Brief Answer
III. Facts
IV. Legal Analysis
    A. Authority 1
    B. Authority 2
    C. Application to Facts
V. Conclusion
VI. Recommendations
"""
        return outline


# Usage example
if __name__ == "__main__":
    generator = ResearchMemoGenerator(author_name="Jane Smith, Legal Counsel")

    memo = generator.create_memo(
        to="Senior Partner",
        re="Enforceability of Non-Compete Agreement",
        question_presented="Whether the non-compete agreement is enforceable under state law?",
        facts="""
        Our client, ABC Corporation, entered into an employment agreement
        with employee John Doe that includes a non-compete clause restricting
        him from working for competitors for two years within a 50-mile radius.
        Doe has been terminated and has received an offer from a competitor.
        """,
        legal_analysis="""
        State law requires that non-compete agreements be reasonable in scope,
        duration, and geographic area. Case law has consistently upheld
        non-competes that are reasonable. The two-year period and 50-mile
        radius appear to be within established precedent.
        """,
        conclusion="The non-compete agreement is likely enforceable.",
        recommendations=["Send cease and desist letter", "Prepare for litigation if necessary"]
    )

    print(generator.format_memo(memo))
