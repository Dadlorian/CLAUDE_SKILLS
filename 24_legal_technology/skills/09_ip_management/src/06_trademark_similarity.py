"""
Trademark Similarity Analysis
Analyzes trademark similarity using multiple methods for infringement and opposition analysis
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from difflib import SequenceMatcher
from collections import defaultdict

logger = logging.getLogger(__name__)


class SimilarityMetric(Enum):
    """Similarity metrics for trademark comparison"""
    VISUAL = "visual"  # Visual similarity
    PHONETIC = "phonetic"  # Sound-alike similarity
    CONCEPTUAL = "conceptual"  # Meaning similarity
    ORTHOGRAPHIC = "orthographic"  # Spelling similarity


@dataclass
class SimilarityScore:
    """Trademark similarity score"""
    mark1: str
    mark2: str
    overall_score: float  # 0.0 to 1.0
    visual_score: float
    phonetic_score: float
    conceptual_score: float
    orthographic_score: float
    likelihood_of_confusion: str  # "high", "medium", "low"


@dataclass
class TrademarkComparison:
    """Detailed trademark comparison"""
    mark1: str
    mark2: str
    similarity_score: SimilarityScore
    goods_services: Tuple[str, str]  # Goods/services for each mark
    classes: Tuple[List[int], List[int]]  # Classification codes
    analysis: Dict[str, str]
    recommendations: List[str]


class PhoneticAnalyzer:
    """Analyze phonetic similarity of trademarks"""

    def __init__(self):
        """Initialize phonetic analyzer"""
        self.metaphone_dict = self._build_metaphone_dict()

    def phonetic_similarity(self, mark1: str, mark2: str) -> float:
        """
        Calculate phonetic similarity between two marks

        Args:
            mark1: First trademark
            mark2: Second trademark

        Returns:
            Similarity score 0.0 to 1.0
        """
        # Remove spaces and punctuation
        m1 = re.sub(r'[^a-z0-9]', '', mark1.lower())
        m2 = re.sub(r'[^a-z0-9]', '', mark2.lower())

        # Use Soundex algorithm
        soundex1 = self._soundex(m1)
        soundex2 = self._soundex(m2)

        if soundex1 == soundex2:
            return 0.9  # Likely phonetically similar

        # Also try Metaphone
        metaphone1 = self._metaphone(m1)
        metaphone2 = self._metaphone(m2)

        if metaphone1 == metaphone2:
            return 0.7

        # Calculate phonetic distance
        distance = self._levenshtein_distance(soundex1, soundex2)
        return max(0, 1 - (distance / 4.0))

    def _soundex(self, text: str) -> str:
        """
        Soundex algorithm for phonetic encoding

        Args:
            text: Input text

        Returns:
            Soundex code
        """
        if not text:
            return ""

        # Keep first letter
        first = text[0].upper()
        text = text.upper()

        # Mapping for Soundex
        mapping = {
            'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3',
            'L': '4',
            'M': '5', 'N': '5',
            'R': '6'
        }

        result = first
        prev_code = mapping.get(first, '0')

        for char in text[1:]:
            code = mapping.get(char, '0')
            if code != '0' and code != prev_code:
                result += code
            if len(result) == 4:
                break
            if code != '0':
                prev_code = code

        # Pad with zeros
        result = (result + '000')[:4]
        return result

    def _metaphone(self, text: str) -> str:
        """
        Simplified Metaphone algorithm

        Args:
            text: Input text

        Returns:
            Metaphone code
        """
        # Simplified metaphone implementation
        text = text.upper()
        metaphone = ""

        for i, char in enumerate(text):
            if char in "AEIOUWY":
                metaphone += char if not metaphone else ""
            elif char == "B":
                if i == len(text) - 1 or text[i + 1] != "B":
                    metaphone += "B"
            elif char in "CGJKQSXZ":
                metaphone += self._metaphone_consonant(char, text, i)
            elif char == "D":
                metaphone += "T"
            elif char == "F":
                metaphone += "F"
            elif char == "H":
                metaphone += "H"
            elif char == "L":
                metaphone += "L"
            elif char in "MN":
                metaphone += char
            elif char == "P":
                metaphone += "P"
            elif char == "R":
                metaphone += "R"
            elif char == "T":
                metaphone += "T"
            elif char == "V":
                metaphone += "F"
            elif char == "W":
                metaphone += "W"

        return metaphone

    def _metaphone_consonant(self, char: str, text: str, pos: int) -> str:
        """Metaphone consonant mapping"""
        if char == "C":
            return "K" if pos < len(text) - 1 and text[pos + 1] in "AOUV" else "S"
        elif char in "SXZ":
            return "S"
        else:
            return char

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _build_metaphone_dict(self) -> Dict[str, str]:
        """Build metaphone dictionary"""
        return {}


class VisualAnalyzer:
    """Analyze visual similarity of trademarks"""

    def __init__(self):
        """Initialize visual analyzer"""
        pass

    def visual_similarity(self, mark1: str, mark2: str) -> float:
        """
        Calculate visual similarity between two marks

        Args:
            mark1: First trademark
            mark2: Second trademark

        Returns:
            Similarity score 0.0 to 1.0
        """
        # Simple string similarity as proxy for visual similarity
        m1 = mark1.lower()
        m2 = mark2.lower()

        # Use sequence matching
        ratio = SequenceMatcher(None, m1, m2).ratio()

        # Check for similar visual elements
        visual_score = ratio

        # Analyze length difference
        len_diff = abs(len(m1) - len(m2))
        if len_diff <= 2:
            visual_score += 0.1

        # Check for common starting letters (creates visual impression)
        if m1[0] == m2[0]:
            visual_score += 0.1

        return min(visual_score, 1.0)

    def analyze_visual_elements(self, mark: str) -> Dict[str, any]:
        """
        Analyze visual elements of a trademark

        Args:
            mark: Trademark to analyze

        Returns:
            Visual characteristics
        """
        elements = {
            "length": len(mark),
            "has_numbers": any(c.isdigit() for c in mark),
            "has_special_chars": bool(re.search(r'[^a-zA-Z0-9]', mark)),
            "capitalization_pattern": self._analyze_capitalization(mark),
            "vowel_count": sum(1 for c in mark.lower() if c in "aeiou"),
            "common_bigrams": self._extract_bigrams(mark)
        }

        return elements

    def _analyze_capitalization(self, mark: str) -> str:
        """Analyze capitalization pattern"""
        if mark.isupper():
            return "all_caps"
        elif mark.islower():
            return "all_lower"
        elif mark[0].isupper():
            return "title_case"
        else:
            return "mixed"

    def _extract_bigrams(self, mark: str) -> List[str]:
        """Extract character bigrams"""
        mark_lower = mark.lower()
        return [mark_lower[i:i+2] for i in range(len(mark_lower) - 1)]


class ConceptualAnalyzer:
    """Analyze conceptual similarity of trademarks"""

    def __init__(self):
        """Initialize conceptual analyzer"""
        self.semantic_relationships = self._build_semantic_relationships()

    def conceptual_similarity(self, mark1: str, mark2: str) -> float:
        """
        Calculate conceptual similarity between two marks

        Args:
            mark1: First trademark
            mark2: Second trademark

        Returns:
            Similarity score 0.0 to 1.0
        """
        m1_lower = mark1.lower()
        m2_lower = mark2.lower()

        # Check for direct meaning relationships
        if m1_lower in self.semantic_relationships:
            related = self.semantic_relationships[m1_lower]
            if m2_lower in related:
                return 0.8

        # Check for word associations
        score = self._calculate_semantic_distance(m1_lower, m2_lower)
        return score

    def _calculate_semantic_distance(self, word1: str, word2: str) -> float:
        """Calculate semantic distance between words"""
        # Simplified semantic distance calculation
        # In production, would use word embeddings or WordNet

        # Extract root words (remove common suffixes)
        root1 = self._extract_root(word1)
        root2 = self._extract_root(word2)

        if root1 == root2:
            return 0.7

        return 0.0

    def _extract_root(self, word: str) -> str:
        """Extract root of word"""
        suffixes = ["ing", "ed", "er", "est", "ly", "tion", "ness"]
        for suffix in suffixes:
            if word.endswith(suffix):
                return word[:-len(suffix)]
        return word

    def _build_semantic_relationships(self) -> Dict[str, List[str]]:
        """Build semantic relationships dictionary"""
        return {
            "sun": ["solar", "sunny", "sunshine"],
            "moon": ["lunar", "night"],
            "fire": ["flame", "hot", "burning"],
            "water": ["aqua", "hydro", "liquid"],
        }


class TrademarkSimilarityAnalyzer:
    """Main trademark similarity analyzer"""

    def __init__(self):
        """Initialize trademark similarity analyzer"""
        self.phonetic = PhoneticAnalyzer()
        self.visual = VisualAnalyzer()
        self.conceptual = ConceptualAnalyzer()

    def compare_trademarks(
        self,
        mark1: str,
        mark2: str,
        goods_services1: Optional[str] = None,
        goods_services2: Optional[str] = None
    ) -> SimilarityScore:
        """
        Compare two trademarks for similarity

        Args:
            mark1: First trademark
            mark2: Second trademark
            goods_services1: Goods/services for first mark
            goods_services2: Goods/services for second mark

        Returns:
            SimilarityScore object
        """
        try:
            # Calculate similarity scores
            visual_score = self.visual.visual_similarity(mark1, mark2)
            phonetic_score = self.phonetic.phonetic_similarity(mark1, mark2)
            conceptual_score = self.conceptual.conceptual_similarity(mark1, mark2)
            orthographic_score = self._orthographic_similarity(mark1, mark2)

            # Weighted overall score
            overall_score = (
                visual_score * 0.35 +
                phonetic_score * 0.35 +
                conceptual_score * 0.20 +
                orthographic_score * 0.10
            )

            # Determine likelihood of confusion
            likelihood = self._determine_confusion_likelihood(
                overall_score,
                goods_services1,
                goods_services2
            )

            return SimilarityScore(
                mark1=mark1,
                mark2=mark2,
                overall_score=overall_score,
                visual_score=visual_score,
                phonetic_score=phonetic_score,
                conceptual_score=conceptual_score,
                orthographic_score=orthographic_score,
                likelihood_of_confusion=likelihood
            )

        except Exception as e:
            logger.error(f"Trademark comparison failed: {e}")
            return SimilarityScore(
                mark1=mark1,
                mark2=mark2,
                overall_score=0.0,
                visual_score=0.0,
                phonetic_score=0.0,
                conceptual_score=0.0,
                orthographic_score=0.0,
                likelihood_of_confusion="unknown"
            )

    def batch_compare(
        self,
        mark: str,
        comparison_marks: List[str]
    ) -> List[SimilarityScore]:
        """
        Compare one mark against multiple marks

        Args:
            mark: Reference trademark
            comparison_marks: List of marks to compare

        Returns:
            List of similarity scores sorted by overall score
        """
        results = []

        for comp_mark in comparison_marks:
            score = self.compare_trademarks(mark, comp_mark)
            results.append(score)

        # Sort by overall score descending
        results.sort(key=lambda x: x.overall_score, reverse=True)

        return results

    def _orthographic_similarity(self, mark1: str, mark2: str) -> float:
        """Calculate orthographic (spelling) similarity"""
        # Character-level similarity
        ratio = SequenceMatcher(None, mark1.lower(), mark2.lower()).ratio()
        return ratio

    def _determine_confusion_likelihood(
        self,
        overall_score: float,
        goods1: Optional[str],
        goods2: Optional[str]
    ) -> str:
        """Determine likelihood of confusion"""
        if overall_score >= 0.75:
            if goods1 and goods2 and self._related_goods(goods1, goods2):
                return "high"
            return "medium"
        elif overall_score >= 0.50:
            return "medium"
        else:
            return "low"

    def _related_goods(self, goods1: str, goods2: str) -> bool:
        """Check if goods/services are related"""
        # Simplified related goods check
        common_categories = [
            ["electronics", "computers", "devices"],
            ["beverages", "drinks", "juice"],
            ["clothing", "apparel", "fashion"],
        ]

        goods1_lower = goods1.lower()
        goods2_lower = goods2.lower()

        for category in common_categories:
            goods1_in_cat = any(g in goods1_lower for g in category)
            goods2_in_cat = any(g in goods2_lower for g in category)

            if goods1_in_cat and goods2_in_cat:
                return True

        return False


class TrademarkConflictDetector:
    """Detect potential trademark conflicts"""

    def __init__(self):
        """Initialize conflict detector"""
        self.analyzer = TrademarkSimilarityAnalyzer()

    def find_conflicts(
        self,
        mark: str,
        database_marks: List[Dict[str, str]],
        threshold: float = 0.70
    ) -> List[Dict[str, any]]:
        """
        Find potential trademark conflicts

        Args:
            mark: New trademark to check
            database_marks: List of existing marks in database
            threshold: Similarity threshold

        Returns:
            List of potential conflicts
        """
        conflicts = []

        for db_mark in database_marks:
            comparison = self.analyzer.compare_trademarks(
                mark,
                db_mark["mark"],
                goods_services1=None,
                goods_services2=db_mark.get("goods_services")
            )

            if comparison.overall_score >= threshold:
                conflicts.append({
                    "conflicting_mark": db_mark["mark"],
                    "similarity_score": comparison.overall_score,
                    "likelihood": comparison.likelihood_of_confusion,
                    "analysis": comparison
                })

        # Sort by score
        conflicts.sort(key=lambda x: x["similarity_score"], reverse=True)

        return conflicts


def main():
    """Example usage"""
    analyzer = TrademarkSimilarityAnalyzer()

    # Compare two trademarks
    result = analyzer.compare_trademarks("APPLE", "APPEL")
    print(f"Similarity between 'APPLE' and 'APPEL':")
    print(f"  Overall Score: {result.overall_score:.2%}")
    print(f"  Visual: {result.visual_score:.2%}")
    print(f"  Phonetic: {result.phonetic_score:.2%}")
    print(f"  Conceptual: {result.conceptual_score:.2%}")
    print(f"  Likelihood of Confusion: {result.likelihood_of_confusion}")

    # Batch comparison
    marks = ["APPL", "APLE", "APPLE INC", "HAPPEL"]
    batch_results = analyzer.batch_compare("APPLE", marks)

    print(f"\nBatch comparison results:")
    for result in batch_results:
        print(f"  {result.mark2}: {result.overall_score:.2%}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
