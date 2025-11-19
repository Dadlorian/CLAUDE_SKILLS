"""
Research Quality Assurance
Ensures quality and accuracy of legal research
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QualityCheckResult:
    """Result of quality check"""
    check_id: str
    passed: bool
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    score: float  # 0-100


class ResearchQualityAssurance:
    """
    Quality assurance for legal research
    """

    def __init__(self):
        """Initialize QA system"""
        self.checks_performed = []
        self.quality_standards = self._load_standards()

    @staticmethod
    def _load_standards() -> Dict:
        """Load quality standards"""
        return {
            "citation_accuracy": 0.95,
            "legal_authority": 0.90,
            "completeness": 0.90,
            "clarity": 0.85,
            "timeliness": 0.90
        }

    def check_research_quality(self, research: Dict) -> QualityCheckResult:
        """
        Check research quality

        Args:
            research: Research document

        Returns:
            Quality check result
        """
        issues = []
        warnings = []
        recommendations = []

        # Check citations
        if not self._check_citations(research):
            issues.append("Citation format errors detected")

        # Check authorities
        if not self._check_authorities(research):
            warnings.append("Some authorities may be outdated")
            recommendations.append("Verify currency of all citations")

        # Check completeness
        completeness = self._check_completeness(research)
        if completeness < 0.90:
            warnings.append(f"Research may be incomplete ({completeness:.0%})")

        # Check clarity
        clarity = self._check_clarity(research)
        if clarity < 0.85:
            recommendations.append("Improve clarity and organization")

        # Calculate score
        score = self._calculate_quality_score(issues, warnings, clarity)

        passed = len(issues) == 0 and score >= 75

        result = QualityCheckResult(
            check_id=f"qc_{len(self.checks_performed)}",
            passed=passed,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
            score=score
        )

        self.checks_performed.append(result)
        logger.info(f"Quality check {result.check_id}: Score {result.score:.1f}, Passed: {result.passed}")

        return result

    @staticmethod
    def _check_citations(research: Dict) -> bool:
        """Check citation formatting"""
        citations = research.get("citations", [])

        if not citations:
            return False

        valid_count = 0
        for citation in citations:
            # Check basic format
            if isinstance(citation, str) and len(citation) > 5:
                valid_count += 1

        return valid_count / len(citations) > 0.95 if citations else False

    @staticmethod
    def _check_authorities(research: Dict) -> bool:
        """Check authority quality"""
        authorities = research.get("authorities", [])

        if not authorities:
            return False

        # Check for primary vs secondary authorities
        primary = sum(1 for a in authorities if a.get("type") == "primary")

        return primary > 0

    @staticmethod
    def _check_completeness(research: Dict) -> float:
        """Check research completeness"""
        required_sections = [
            "facts", "legal_issue", "analysis", "conclusion"
        ]

        sections_present = sum(1 for s in required_sections if research.get(s))

        return sections_present / len(required_sections)

    @staticmethod
    def _check_clarity(research: Dict) -> float:
        """Check clarity of writing"""
        text = research.get("analysis", "") + research.get("conclusion", "")

        if not text:
            return 0.0

        # Simple clarity check: average sentence length
        sentences = text.split(".")
        if not sentences:
            return 0.0

        avg_words_per_sentence = sum(len(s.split()) for s in sentences) / len(sentences)

        # Ideal range: 15-25 words per sentence
        if 15 <= avg_words_per_sentence <= 25:
            return 0.95
        elif 10 <= avg_words_per_sentence <= 30:
            return 0.80
        else:
            return 0.60

    @staticmethod
    def _calculate_quality_score(issues: List[str], warnings: List[str], clarity: float) -> float:
        """Calculate overall quality score"""
        score = 100.0

        # Deduct for issues
        score -= len(issues) * 25

        # Deduct for warnings
        score -= len(warnings) * 10

        # Include clarity component
        score = score * (clarity / 100) + (100 - score) * 0.5

        return max(0, min(100, score))

    def review_research(self, research: Dict, reviewer_notes: str = "") -> Dict:
        """
        Comprehensive research review

        Args:
            research: Research document
            reviewer_notes: Reviewer comments

        Returns:
            Review summary
        """
        quality_check = self.check_research_quality(research)

        review = {
            "quality_score": quality_check.score,
            "passed_qa": quality_check.passed,
            "issues": quality_check.issues,
            "warnings": quality_check.warnings,
            "recommendations": quality_check.recommendations,
            "reviewer_notes": reviewer_notes,
            "status": "approved" if quality_check.passed else "needs_revision"
        }

        logger.info(f"Research review complete: {review['status']}")

        return review

    def generate_qa_report(self) -> Dict:
        """
        Generate QA report

        Returns:
            QA statistics and summary
        """
        if not self.checks_performed:
            return {"total_checks": 0, "data": "no_checks_performed"}

        total = len(self.checks_performed)
        passed = sum(1 for c in self.checks_performed if c.passed)
        avg_score = sum(c.score for c in self.checks_performed) / total

        return {
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total,
            "average_score": avg_score,
            "quality_status": "good" if avg_score >= 80 else "needs_improvement"
        }


# Usage example
if __name__ == "__main__":
    qa = ResearchQualityAssurance()

    # Check research
    research = {
        "facts": "The plaintiff alleges...",
        "legal_issue": "Whether the defendant breached the contract",
        "analysis": "Under contract law, a breach occurs when...",
        "conclusion": "Therefore, the defendant breached the contract.",
        "citations": ["42 U.S.C. § 1983", "Example v. Defendant, 123 F.3d 456 (9th Cir. 2020)"],
        "authorities": [
            {"type": "primary", "citation": "42 U.S.C. § 1983"},
            {"type": "secondary", "citation": "Contract Law Treatise"}
        ]
    }

    result = qa.check_research_quality(research)
    print(f"Quality Check: Score {result.score:.1f}, Passed: {result.passed}")

    # Generate report
    report = qa.generate_qa_report()
    print(f"QA Report: {report}")
