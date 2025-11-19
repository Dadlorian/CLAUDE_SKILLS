"""
Patent Claim Analyzer
Analyzes patent claims for scope, structure, validity, and infringement
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import re
from enum import Enum

logger = logging.getLogger(__name__)


class ClaimType(Enum):
    """Patent claim types"""
    INDEPENDENT = "independent"
    DEPENDENT = "dependent"
    PREAMBLE = "preamble"


class ClaimScope(Enum):
    """Claim scope analysis"""
    BROAD = "broad"
    NARROW = "narrow"
    MODERATE = "moderate"


@dataclass
class ClaimElement:
    """Patent claim element"""
    element_number: int
    text: str
    element_type: str  # "apparatus", "method", "composition"
    limitations: List[str] = field(default_factory=list)
    is_optional: bool = False


@dataclass
class ClaimAnalysis:
    """Detailed claim analysis"""
    claim_number: int
    claim_type: ClaimType
    total_words: int
    element_count: int
    limitation_count: int
    scope: ClaimScope
    clarity_score: float  # 0-1, higher is clearer
    validity_score: float  # 0-1, higher is more likely valid
    breadth_score: float  # 0-1, higher is broader
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PatentClaimComparison:
    """Compare claims for infringement"""
    accused_product_features: List[str]
    claim_limitations: List[str]
    literal_infringement: bool
    doctrine_of_equivalents: bool
    infringement_elements: List[str]
    non_infringement_elements: List[str]
    infringement_score: float


class ClaimParser:
    """Parse patent claims"""

    def __init__(self):
        """Initialize claim parser"""
        self.antecedent_basis_keywords = {"a ", "an ", "the ", "said ", "such "}

    def parse_claim(self, claim_text: str) -> Dict[str, any]:
        """
        Parse claim text

        Args:
            claim_text: Claim text

        Returns:
            Parsed claim structure
        """
        claim_data = {
            "original_text": claim_text,
            "words": claim_text.split(),
            "word_count": len(claim_text.split()),
            "sentences": self._extract_sentences(claim_text),
            "limitations": self._extract_limitations(claim_text),
            "transitional_phrases": self._extract_transitional_phrases(claim_text),
            "antecedent_basis": self._check_antecedent_basis(claim_text),
        }

        return claim_data

    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from claim"""
        # Split on periods and semicolons
        sentences = re.split(r'[.;]', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_limitations(self, text: str) -> List[str]:
        """Extract claim limitations"""
        limitations = []

        # Look for common limitation patterns
        patterns = [
            r'a\s+(\w+)',
            r'the\s+(\w+)',
            r'comprising\s+(.+?)(?=[,;]|$)',
            r'including\s+(.+?)(?=[,;]|$)',
            r'having\s+(.+?)(?=[,;]|$)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            limitations.extend(matches)

        return limitations

    def _extract_transitional_phrases(self, text: str) -> List[str]:
        """Extract transitional phrases (comprising, including, etc.)"""
        phrases = ["comprising", "including", "consisting of", "containing", "having"]
        found = []

        for phrase in phrases:
            if phrase.lower() in text.lower():
                found.append(phrase)

        return found

    def _check_antecedent_basis(self, text: str) -> Dict[str, bool]:
        """Check for proper antecedent basis"""
        issues = {}

        # Check for "a/an" without introduction
        if re.search(r'\ba\s+\w+', text):
            issues["indefinite_article"] = True

        # Check for use of "said" or "the"
        if re.search(r'\b(said|the)\s+\w+', text):
            issues["definite_reference"] = True

        return issues


class ClaimAnalyzer:
    """Analyze patent claims"""

    def __init__(self):
        """Initialize claim analyzer"""
        self.parser = ClaimParser()

    def analyze_claim(
        self,
        claim_number: int,
        claim_text: str,
        claim_type: ClaimType
    ) -> ClaimAnalysis:
        """
        Analyze a patent claim

        Args:
            claim_number: Claim number
            claim_text: Claim text
            claim_type: Type of claim

        Returns:
            ClaimAnalysis object
        """
        parsed = self.parser.parse_claim(claim_text)

        # Calculate metrics
        total_words = parsed["word_count"]
        element_count = len(parsed["limitations"])
        limitation_count = len(parsed["limitations"])

        # Determine scope
        scope = self._determine_scope(claim_text)

        # Calculate clarity score
        clarity_score = self._calculate_clarity_score(claim_text)

        # Calculate validity score
        validity_score = self._calculate_validity_score(claim_text)

        # Calculate breadth score
        breadth_score = self._calculate_breadth_score(claim_text)

        # Identify issues
        issues = self._identify_issues(claim_text, claim_type, parsed)

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, clarity_score)

        return ClaimAnalysis(
            claim_number=claim_number,
            claim_type=claim_type,
            total_words=total_words,
            element_count=element_count,
            limitation_count=limitation_count,
            scope=scope,
            clarity_score=clarity_score,
            validity_score=validity_score,
            breadth_score=breadth_score,
            issues=issues,
            recommendations=recommendations
        )

    def analyze_claim_set(
        self,
        claims: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Analyze entire set of claims

        Args:
            claims: List of claim dictionaries

        Returns:
            Set-level analysis
        """
        analyses = []
        antecedent_basis_map = {}

        for claim in claims:
            claim_number = claim.get("number", 0)
            claim_text = claim.get("text", "")
            claim_type = claim.get("type", ClaimType.INDEPENDENT)

            analysis = self.analyze_claim(claim_number, claim_text, claim_type)
            analyses.append(analysis)

        # Check for dependent claim validity
        for i, analysis in enumerate(analyses):
            if analysis.claim_type == ClaimType.DEPENDENT:
                # Check that parent claim exists
                parent = self._find_parent_claim(analyses, i)
                if not parent:
                    analysis.issues.append("Parent claim not found")

        # Calculate set-level metrics
        return {
            "total_claims": len(analyses),
            "independent_claims": sum(1 for a in analyses if a.claim_type == ClaimType.INDEPENDENT),
            "dependent_claims": sum(1 for a in analyses if a.claim_type == ClaimType.DEPENDENT),
            "avg_clarity_score": sum(a.clarity_score for a in analyses) / len(analyses) if analyses else 0,
            "avg_validity_score": sum(a.validity_score for a in analyses) / len(analyses) if analyses else 0,
            "claims": [self._analysis_to_dict(a) for a in analyses],
            "common_issues": self._identify_common_issues(analyses),
        }

    def compare_claims_for_infringement(
        self,
        claim: str,
        accused_features: List[str]
    ) -> PatentClaimComparison:
        """
        Compare claim against accused product for infringement

        Args:
            claim: Patent claim text
            accused_features: Features of accused product

        Returns:
            Infringement comparison
        """
        # Extract claim limitations
        claim_limitations = self.parser._extract_limitations(claim)

        # Check each limitation against accused product
        infringement_elements = []
        non_infringement_elements = []

        for limitation in claim_limitations:
            if self._limitation_found_in_product(limitation, accused_features):
                infringement_elements.append(limitation)
            else:
                non_infringement_elements.append(limitation)

        # Determine infringement
        literal_infringement = len(non_infringement_elements) == 0
        doctrine_of_equivalents = self._check_doctrine_of_equivalents(
            non_infringement_elements,
            accused_features
        )

        # Calculate infringement score
        if not claim_limitations:
            infringement_score = 0.0
        else:
            infringement_score = len(infringement_elements) / len(claim_limitations)

        return PatentClaimComparison(
            accused_product_features=accused_features,
            claim_limitations=claim_limitations,
            literal_infringement=literal_infringement,
            doctrine_of_equivalents=doctrine_of_equivalents,
            infringement_elements=infringement_elements,
            non_infringement_elements=non_infringement_elements,
            infringement_score=infringement_score
        )

    def check_claim_validity(self, claim_text: str) -> Dict[str, any]:
        """
        Check claim validity issues

        Args:
            claim_text: Claim text

        Returns:
            Validity issues
        """
        validity_issues = {
            "indefiniteness": [],
            "antecedent_basis": [],
            "functional_limitations": [],
            "means_plus_function": [],
            "dependent_claim_issues": [],
        }

        # Check for indefiniteness
        if self._is_indefinite(claim_text):
            validity_issues["indefiniteness"].append("Vague or ambiguous terminology")

        # Check antecedent basis
        antecedent_check = self.parser._check_antecedent_basis(claim_text)
        if antecedent_check:
            validity_issues["antecedent_basis"].append(str(antecedent_check))

        # Check for functional limitations
        if "function" in claim_text.lower() or "step of" in claim_text.lower():
            validity_issues["functional_limitations"].append("Functional limitation detected")

        # Check for means-plus-function
        if "means for" in claim_text.lower():
            validity_issues["means_plus_function"].append("Means-plus-function limitation")

        return validity_issues

    def _determine_scope(self, claim_text: str) -> ClaimScope:
        """Determine claim scope"""
        # Count limitations
        limitations = self.parser._extract_limitations(claim_text)
        num_limitations = len(limitations)

        if num_limitations <= 3:
            return ClaimScope.BROAD
        elif num_limitations >= 8:
            return ClaimScope.NARROW
        else:
            return ClaimScope.MODERATE

    def _calculate_clarity_score(self, claim_text: str) -> float:
        """Calculate claim clarity score"""
        score = 1.0

        # Deduct for complex structures
        if len(claim_text) > 500:
            score -= 0.2
        if claim_text.count(";") > 5:
            score -= 0.1

        # Bonus for clear transitional phrases
        if any(phrase in claim_text.lower() for phrase in ["comprising", "including"]):
            score += 0.1

        return max(0.0, min(1.0, score))

    def _calculate_validity_score(self, claim_text: str) -> float:
        """Calculate claim validity score"""
        score = 0.8  # Start with reasonable score

        # Check for common validity issues
        if self._is_indefinite(claim_text):
            score -= 0.3

        if not self.parser._check_antecedent_basis(claim_text):
            score += 0.1

        if "means for" in claim_text.lower():
            # Means-plus-function claims require structure
            score -= 0.2

        return max(0.0, min(1.0, score))

    def _calculate_breadth_score(self, claim_text: str) -> float:
        """Calculate claim breadth score"""
        limitations = self.parser._extract_limitations(claim_text)
        # More limitations = narrower scope
        num_limitations = len(limitations)

        if num_limitations == 0:
            return 1.0
        elif num_limitations <= 3:
            return 0.8
        elif num_limitations <= 5:
            return 0.6
        elif num_limitations <= 10:
            return 0.4
        else:
            return 0.2

    def _identify_issues(
        self,
        claim_text: str,
        claim_type: ClaimType,
        parsed: Dict[str, any]
    ) -> List[str]:
        """Identify claim issues"""
        issues = []

        # Check for indefiniteness
        if self._is_indefinite(claim_text):
            issues.append("Potential indefiniteness")

        # Check for antecedent basis
        if parsed.get("antecedent_basis"):
            issues.append("Antecedent basis issues")

        # Check for excessive length
        if parsed["word_count"] > 500:
            issues.append("Claim is excessively long (>500 words)")

        # Check transitional phrase
        if not parsed.get("transitional_phrases"):
            issues.append("No clear transitional phrase")

        return issues

    def _generate_recommendations(
        self,
        issues: List[str],
        clarity_score: float
    ) -> List[str]:
        """Generate recommendations"""
        recommendations = []

        if issues:
            recommendations.append("Address identified issues")

        if clarity_score < 0.7:
            recommendations.append("Simplify and clarify claim language")

        if len(issues) > 2:
            recommendations.append("Consider redrafting claim")

        return recommendations

    def _is_indefinite(self, claim_text: str) -> bool:
        """Check if claim is indefinite"""
        indefinite_terms = [
            "approximately",
            "about",
            "generally",
            "substantially",
            "wherein",
        ]

        for term in indefinite_terms:
            if term in claim_text.lower():
                return True

        return False

    def _find_parent_claim(self, analyses: List[ClaimAnalysis], index: int) -> Optional[ClaimAnalysis]:
        """Find parent claim for dependent claim"""
        if index < len(analyses):
            for parent in analyses[:index]:
                if parent.claim_type == ClaimType.INDEPENDENT:
                    return parent
        return None

    def _limitation_found_in_product(self, limitation: str, features: List[str]) -> bool:
        """Check if limitation exists in product features"""
        limitation_lower = limitation.lower()
        for feature in features:
            if limitation_lower in feature.lower():
                return True
        return False

    def _check_doctrine_of_equivalents(
        self,
        missing_elements: List[str],
        product_features: List[str]
    ) -> bool:
        """Check if missing elements might be covered by doctrine of equivalents"""
        if not missing_elements:
            return True

        # Simplified equivalence check
        for element in missing_elements:
            # Check for similar functionality
            for feature in product_features:
                if self._are_equivalent(element, feature):
                    return True

        return False

    def _are_equivalent(self, element: str, feature: str) -> bool:
        """Check if element and feature are equivalent"""
        # Simplified equivalence - would need more sophisticated NLP in production
        element_lower = element.lower()
        feature_lower = feature.lower()

        # Check for semantic similarity
        common_words = set(element_lower.split()) & set(feature_lower.split())
        similarity = len(common_words) / max(len(element_lower.split()), len(feature_lower.split()))

        return similarity > 0.5

    def _identify_common_issues(self, analyses: List[ClaimAnalysis]) -> List[str]:
        """Identify issues common across claim set"""
        all_issues = []
        for analysis in analyses:
            all_issues.extend(analysis.issues)

        # Count frequencies
        from collections import Counter
        issue_counts = Counter(all_issues)

        return [issue for issue, count in issue_counts.most_common(5) if count > 1]

    def _analysis_to_dict(self, analysis: ClaimAnalysis) -> Dict[str, any]:
        """Convert analysis to dictionary"""
        return {
            "claim_number": analysis.claim_number,
            "claim_type": analysis.claim_type.value,
            "word_count": analysis.total_words,
            "limitations": analysis.limitation_count,
            "scope": analysis.scope.value,
            "clarity_score": round(analysis.clarity_score, 2),
            "validity_score": round(analysis.validity_score, 2),
            "breadth_score": round(analysis.breadth_score, 2),
            "issues": analysis.issues,
            "recommendations": analysis.recommendations,
        }


class ClaimComparator:
    """Compare claims for invalidity (obviousness, etc.)"""

    def __init__(self):
        """Initialize comparator"""
        self.analyzer = ClaimAnalyzer()

    def compare_claims_for_validity(
        self,
        patent_claim: str,
        prior_art: List[str]
    ) -> Dict[str, any]:
        """
        Compare claim against prior art

        Args:
            patent_claim: Patent claim to analyze
            prior_art: List of prior art references

        Returns:
            Validity analysis
        """
        claim_limitations = self.analyzer.parser._extract_limitations(patent_claim)

        # Check coverage by prior art
        covered_by_art = []
        not_covered = claim_limitations.copy()

        for reference in prior_art:
            art_limitations = self.analyzer.parser._extract_limitations(reference)
            for limitation in claim_limitations:
                if limitation in art_limitations:
                    covered_by_art.append((limitation, reference))
                    if limitation in not_covered:
                        not_covered.remove(limitation)

        # Calculate obviousness risk
        coverage_ratio = len(covered_by_art) / len(claim_limitations) if claim_limitations else 0
        obviousness_risk = "high" if coverage_ratio > 0.8 else "medium" if coverage_ratio > 0.5 else "low"

        return {
            "claim_limitations": claim_limitations,
            "covered_by_prior_art": covered_by_art,
            "not_covered": not_covered,
            "coverage_ratio": round(coverage_ratio, 2),
            "obviousness_risk": obviousness_risk,
            "recommendations": self._validity_recommendations(not_covered, coverage_ratio),
        }

    def _validity_recommendations(self, uncovered: List[str], coverage: float) -> List[str]:
        """Generate recommendations for claim validity"""
        recommendations = []

        if coverage > 0.8:
            recommendations.append("Claim appears obvious over prior art - consider amendments")

        if not uncovered:
            recommendations.append("All limitations found in prior art - high invalidity risk")
        else:
            recommendations.append(f"Novel elements: {', '.join(uncovered[:3])}")

        return recommendations


def main():
    """Example usage"""
    analyzer = ClaimAnalyzer()

    # Sample claim
    claim_text = """
    1. A method for manufacturing solar panels comprising:
    providing a substrate;
    depositing a photovoltaic material onto said substrate;
    applying electrical contacts to said photovoltaic material;
    testing the resulting panel for performance.
    """

    # Analyze claim
    analysis = analyzer.analyze_claim(1, claim_text, ClaimType.INDEPENDENT)

    print(f"Claim Analysis:")
    print(f"  Scope: {analysis.scope.value}")
    print(f"  Clarity Score: {analysis.clarity_score:.2f}")
    print(f"  Validity Score: {analysis.validity_score:.2f}")
    print(f"  Issues: {analysis.issues}")

    # Compare for infringement
    product_features = [
        "substrate material",
        "photovoltaic layer",
        "electrical contact",
        "performance measurement"
    ]

    comparison = analyzer.compare_claims_for_infringement(claim_text, product_features)
    print(f"\nInfringement Analysis:")
    print(f"  Literal Infringement: {comparison.literal_infringement}")
    print(f"  Infringement Score: {comparison.infringement_score:.2f}")

    # Check validity
    validity = analyzer.check_claim_validity(claim_text)
    print(f"\nValidity Check:")
    for issue_type, issues in validity.items():
        if issues:
            print(f"  {issue_type}: {issues}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
