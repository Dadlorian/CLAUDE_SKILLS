"""
Patent Claim Analysis Example
Analyzes patent claims for scope, dependencies, and validity assessment
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from enum import Enum

class ClaimType(Enum):
    """Patent claim types"""
    INDEPENDENT = "independent"
    DEPENDENT = "dependent"

@dataclass
class Claim:
    """Represents a patent claim"""
    number: int
    claim_type: ClaimType
    text: str
    dependent_on: Optional[int] = None
    term_count: int = 0

class PatentClaimAnalyzer:
    """Analyze patent claims"""

    def __init__(self):
        self.claims: Dict[int, Claim] = {}

    def add_claim(self, claim_number: int, claim_text: str,
                  claim_type: ClaimType, dependent_on: Optional[int] = None):
        """Add a claim for analysis"""
        claim = Claim(
            number=claim_number,
            claim_type=claim_type,
            text=claim_text,
            dependent_on=dependent_on,
            term_count=len(claim_text.split())
        )
        self.claims[claim_number] = claim

    def analyze_claim_scope(self, claim_number: int) -> Dict:
        """Analyze the scope of a claim"""
        if claim_number not in self.claims:
            return {}

        claim = self.claims[claim_number]

        # Extract key elements
        method_words = ['method', 'system', 'apparatus', 'device']
        comprises_words = ['comprising', 'consisting of', 'including', 'containing']

        is_method = any(word in claim.text.lower() for word in method_words)
        comprises_type = next((word for word in comprises_words
                              if word in claim.text.lower()), None)

        # Count limitation terms
        limitations = claim.text.count(';') + 1

        # Estimate scope (narrower = more limitations)
        scope_level = "Broad" if limitations <= 3 else "Medium" if limitations <= 6 else "Narrow"

        return {
            'claim_number': claim_number,
            'claim_type': claim.claim_type.value,
            'scope_level': scope_level,
            'limitations_count': limitations,
            'terms_count': claim.term_count,
            'claim_type_structure': 'Method' if is_method else 'Apparatus/System',
            'transition_phrase': comprises_type or 'Unknown'
        }

    def get_claim_dependencies(self, claim_number: int) -> List[int]:
        """Get all claims that depend on this claim (directly or indirectly)"""
        dependents = []

        for other_num, other_claim in self.claims.items():
            if other_claim.dependent_on == claim_number:
                dependents.append(other_num)
                # Recursively get claims depending on this dependent
                dependents.extend(self.get_claim_dependencies(other_num))

        return dependents

    def get_claim_hierarchy(self) -> Dict:
        """Get hierarchical structure of dependent claims"""
        hierarchy = {}

        # Find independent claims
        independent = [num for num, claim in self.claims.items()
                      if claim.claim_type == ClaimType.INDEPENDENT]

        for ind_num in independent:
            hierarchy[ind_num] = self.get_claim_dependencies(ind_num)

        return hierarchy

    def analyze_claim_coverage(self) -> Dict:
        """Analyze overall claim coverage"""
        independent_count = sum(1 for claim in self.claims.values()
                               if claim.claim_type == ClaimType.INDEPENDENT)
        dependent_count = len(self.claims) - independent_count

        # Average limitation count
        avg_limitations = sum(self.analyze_claim_scope(num).get('limitations_count', 0)
                             for num in self.claims.keys()) / len(self.claims) if self.claims else 0

        return {
            'total_claims': len(self.claims),
            'independent_claims': independent_count,
            'dependent_claims': dependent_count,
            'average_limitations': avg_limitations,
            'claim_hierarchy': self.get_claim_hierarchy(),
            'portfolio_breadth': "Broad" if avg_limitations < 5 else "Medium" if avg_limitations < 8 else "Narrow"
        }

    def assess_validity_risk(self, claim_number: int,
                            prior_art_terms: List[str] = None) -> Dict:
        """Assess potential invalidity risk of a claim"""
        if claim_number not in self.claims:
            return {}

        claim = self.claims[claim_number]
        prior_art_terms = prior_art_terms or []

        # Risk factors
        risks = []
        risk_score = 0

        # Check for disclosure limitations
        if claim.term_count < 20:
            risks.append("Short claim may lack sufficient detail")
            risk_score += 1

        # Check for indefinite terms
        indefinite_words = ['substantially', 'approximately', 'about', 'essentially']
        indefinite_count = sum(claim.text.lower().count(word) for word in indefinite_words)
        if indefinite_count > 2:
            risks.append("Multiple indefinite terms may create definiteness issues")
            risk_score += 2

        # Check for means-plus-function
        if 'means for' in claim.text.lower():
            risks.append("Means-plus-function language may require specific structure")
            risk_score += 1

        # Check for prior art terms
        if prior_art_terms:
            matching_terms = [term for term in prior_art_terms
                            if term.lower() in claim.text.lower()]
            if matching_terms:
                risks.append(f"Prior art overlap with terms: {', '.join(matching_terms)}")
                risk_score += len(matching_terms)

        # Translate risk score to level
        if risk_score <= 1:
            validity_level = "Low Risk"
        elif risk_score <= 3:
            validity_level = "Medium Risk"
        else:
            validity_level = "High Risk"

        return {
            'claim_number': claim_number,
            'validity_assessment': validity_level,
            'risk_score': risk_score,
            'identified_risks': risks
        }

    def suggest_narrowing_amendments(self, claim_number: int) -> List[str]:
        """Suggest ways to narrow a claim"""
        if claim_number not in self.claims:
            return []

        claim = self.claims[claim_number]
        suggestions = []

        # Look for terms that could be more specific
        vague_terms = ['suitable', 'appropriate', 'desirable', 'effective']
        for term in vague_terms:
            if term in claim.text.lower():
                suggestions.append(f"Replace '{term}' with more specific language")

        # Check for overly broad transitions
        if 'comprising' in claim.text.lower():
            suggestions.append("Consider 'consisting of' for narrower scope if needed")

        # Look for dependent vs independent optimization
        if claim.claim_type == ClaimType.INDEPENDENT and claim.term_count > 100:
            suggestions.append("Consider dividing into independent + dependent claim structure")

        return suggestions

    def compare_claims(self, claim_num1: int, claim_num2: int) -> Dict:
        """Compare two claims for scope differences"""
        if claim_num1 not in self.claims or claim_num2 not in self.claims:
            return {}

        claim1 = self.claims[claim_num1]
        claim2 = self.claims[claim_num2]

        # Analyze both claims
        scope1 = self.analyze_claim_scope(claim_num1)
        scope2 = self.analyze_claim_scope(claim_num2)

        # Compare
        comparison = {
            'claim_1_limitations': scope1.get('limitations_count'),
            'claim_2_limitations': scope2.get('limitations_count'),
            'scope_difference': "Claim 1 is broader" if scope1.get('limitations_count', 0) < scope2.get('limitations_count', 0)
                               else "Claim 2 is broader" if scope2.get('limitations_count', 0) < scope1.get('limitations_count', 0)
                               else "Claims appear equivalent",
            'common_elements': self._find_common_terms(claim1.text, claim2.text),
            'unique_to_claim_1': self._find_unique_terms(claim1.text, claim2.text),
            'unique_to_claim_2': self._find_unique_terms(claim2.text, claim1.text)
        }

        return comparison

    def _find_common_terms(self, text1: str, text2: str) -> List[str]:
        """Find common terms between two claim texts"""
        words1 = set(word.lower() for word in text1.split())
        words2 = set(word.lower() for word in text2.split())
        common = words1 & words2

        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'of', 'in', 'at', 'to', 'for'}
        return [w for w in sorted(common) if w not in stop_words and len(w) > 3]

    def _find_unique_terms(self, text1: str, text2: str) -> List[str]:
        """Find terms unique to text1"""
        words1 = set(word.lower() for word in text1.split())
        words2 = set(word.lower() for word in text2.split())
        unique = words1 - words2

        stop_words = {'the', 'a', 'an', 'and', 'or', 'of', 'in', 'at', 'to', 'for'}
        return [w for w in sorted(unique) if w not in stop_words and len(w) > 3]


# Example usage
if __name__ == "__main__":
    analyzer = PatentClaimAnalyzer()

    # Add claims
    analyzer.add_claim(1, "A method comprising: receiving input data; processing with machine learning; outputting result",
                      ClaimType.INDEPENDENT)
    analyzer.add_claim(2, "The method of claim 1, wherein the machine learning is neural network based",
                      ClaimType.DEPENDENT, dependent_on=1)
    analyzer.add_claim(3, "The method of claim 1, wherein the processing includes optimization",
                      ClaimType.DEPENDENT, dependent_on=1)

    # Analyze coverage
    coverage = analyzer.analyze_claim_coverage()
    print(f"Total claims: {coverage['total_claims']}")
    print(f"Independent: {coverage['independent_claims']}")
    print(f"Portfolio breadth: {coverage['portfolio_breadth']}")

    # Analyze specific claim
    scope = analyzer.analyze_claim_scope(1)
    print(f"\nClaim 1 scope: {scope['scope_level']}")

    # Assess validity risk
    validity = analyzer.assess_validity_risk(1)
    print(f"Validity assessment: {validity['validity_assessment']}")
