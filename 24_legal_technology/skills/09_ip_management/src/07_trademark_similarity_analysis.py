"""
Trademark Similarity Analysis Example
Analyzes similarity between trademarks using multiple metrics
"""

from typing import Dict, List, Tuple
import difflib
import Levenshtein
from dataclasses import dataclass

@dataclass
class SimilarityScore:
    """Represents similarity analysis results"""
    mark1: str
    mark2: str
    overall_score: float  # 0-1 scale
    phonetic_score: float
    visual_score: float
    semantic_score: float
    likelihood_of_confusion: str  # Low, Moderate, High

class TrademarkSimilarityAnalyzer:
    """Analyze trademark similarity"""

    # Phonetic conversion rules (simplified Soundex-like)
    PHONETIC_MAPPINGS = {
        'c': 'k', 'q': 'k',
        'f': 'v', 'gh': 'f',
        's': 'z',
        'y': 'i',
    }

    def analyze_similarity(self, mark1: str, mark2: str) -> SimilarityScore:
        """
        Comprehensive trademark similarity analysis

        Args:
            mark1: First trademark
            mark2: Second trademark

        Returns:
            SimilarityScore with detailed metrics
        """
        phonetic_score = self._calculate_phonetic_similarity(mark1, mark2)
        visual_score = self._calculate_visual_similarity(mark1, mark2)
        semantic_score = self._calculate_semantic_similarity(mark1, mark2)

        # Calculate weighted overall score
        overall_score = (phonetic_score * 0.4 +
                        visual_score * 0.35 +
                        semantic_score * 0.25)

        # Determine likelihood of confusion
        if overall_score >= 0.75:
            confusion = "High"
        elif overall_score >= 0.50:
            confusion = "Moderate"
        else:
            confusion = "Low"

        return SimilarityScore(
            mark1=mark1,
            mark2=mark2,
            overall_score=overall_score,
            phonetic_score=phonetic_score,
            visual_score=visual_score,
            semantic_score=semantic_score,
            likelihood_of_confusion=confusion
        )

    def _calculate_phonetic_similarity(self, mark1: str, mark2: str) -> float:
        """
        Calculate how similar marks sound
        Uses Levenshtein distance and phonetic analysis
        """
        # Normalize to lowercase
        m1 = mark1.lower().strip()
        m2 = mark2.lower().strip()

        # Calculate phonetic versions
        phon1 = self._convert_to_phonetic(m1)
        phon2 = self._convert_to_phonetic(m2)

        # Use Levenshtein distance
        max_len = max(len(phon1), len(phon2))
        if max_len == 0:
            return 0.0

        distance = Levenshtein.distance(phon1, phon2)
        similarity = 1.0 - (distance / max_len)

        return max(0.0, min(1.0, similarity))

    def _calculate_visual_similarity(self, mark1: str, mark2: str) -> float:
        """
        Calculate visual similarity (spelling, appearance)
        """
        m1 = mark1.lower().strip()
        m2 = mark2.lower().strip()

        # Check for exact match
        if m1 == m2:
            return 1.0

        # Use sequence matching for visual similarity
        matcher = difflib.SequenceMatcher(None, m1, m2)
        ratio = matcher.ratio()

        # Check for common prefixes
        common_prefix_bonus = 0.0
        min_len = min(len(m1), len(m2))
        if min_len > 0:
            common_len = 0
            for i in range(min_len):
                if m1[i] == m2[i]:
                    common_len += 1
                else:
                    break
            common_prefix_bonus = (common_len / min_len) * 0.15

        return min(1.0, ratio + common_prefix_bonus)

    def _calculate_semantic_similarity(self, mark1: str, mark2: str) -> float:
        """
        Calculate semantic similarity (meaning)
        Uses dictionary of related terms
        """
        semantic_relations = {
            'apple': ['fruit', 'company', 'tech'],
            'amazon': ['river', 'company', 'jungle'],
            'microsoft': ['soft', 'computer'],
            'google': ['search', 'web'],
        }

        m1_key = mark1.lower().strip()
        m2_key = mark2.lower().strip()

        # Check if marks have direct semantic relationship
        if m1_key in semantic_relations:
            m2_semantics = semantic_relations.get(m2_key, [m2_key])
            if any(term in mark2.lower() for term in semantic_relations.get(m1_key, [])):
                return 0.8

        # Default: low semantic relationship unless marks contain common terms
        common_terms = set(m1_key.split()) & set(m2_key.split())
        if common_terms:
            return 0.4
        else:
            return 0.0

    def _convert_to_phonetic(self, text: str) -> str:
        """Convert text to phonetic representation"""
        result = text.lower()

        # Apply phonetic mappings
        for original, replacement in self.PHONETIC_MAPPINGS.items():
            result = result.replace(original, replacement)

        # Remove duplicate consecutive letters
        cleaned = ""
        prev = ""
        for char in result:
            if char != prev:
                cleaned += char
                prev = char
            elif char.isalpha():
                prev = char

        return cleaned

    def batch_analyze(self, reference_mark: str, comparison_marks: List[str]) -> List[SimilarityScore]:
        """
        Analyze reference mark against multiple marks

        Args:
            reference_mark: The mark to compare against
            comparison_marks: List of marks to compare

        Returns:
            List of similarity scores sorted by overall score
        """
        results = []
        for mark in comparison_marks:
            result = self.analyze_similarity(reference_mark, mark)
            results.append(result)

        # Sort by overall similarity score (descending)
        results.sort(key=lambda x: x.overall_score, reverse=True)

        return results

    def find_potential_conflicts(self, reference_mark: str, comparison_marks: List[str],
                                threshold: float = 0.65) -> List[SimilarityScore]:
        """
        Find marks that may create likelihood of confusion

        Args:
            reference_mark: Mark to check for conflicts
            comparison_marks: Marks to check against
            threshold: Minimum similarity score to consider conflict

        Returns:
            List of potential conflicting marks
        """
        results = self.batch_analyze(reference_mark, comparison_marks)

        # Filter to potential conflicts
        conflicts = [r for r in results if r.overall_score >= threshold]

        return conflicts


# Example usage
if __name__ == "__main__":
    analyzer = TrademarkSimilarityAnalyzer()

    # Analyze similarity between two marks
    result = analyzer.analyze_similarity("APPLE", "APLE")
    print(f"Overall Similarity: {result.overall_score:.2%}")
    print(f"Likelihood of Confusion: {result.likelihood_of_confusion}")

    # Batch analysis
    marks_to_check = ["APPLE", "APLE", "APPLE TREE", "FRESH APPLE", "APPL"]
    similar_marks = analyzer.batch_analyze("APPLE", marks_to_check)

    for mark_result in similar_marks:
        print(f"{mark_result.mark2}: {mark_result.overall_score:.2%}")
