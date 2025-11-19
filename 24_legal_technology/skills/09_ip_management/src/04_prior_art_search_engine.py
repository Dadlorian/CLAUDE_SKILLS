"""
Prior Art Search Engine Example
Combines multiple search strategies for comprehensive prior art identification
"""

from typing import List, Dict, Set
from dataclasses import dataclass
import re

@dataclass
class PriorArtResult:
    """Represents a prior art search result"""
    source: str
    document_id: str
    title: str
    relevance_score: float
    publication_date: str
    url: str

class PriorArtSearchEngine:
    """Conduct multi-source prior art searches"""

    def __init__(self):
        self.patent_sources = ["USPTO", "Google Patents", "Espacenet"]
        self.literature_sources = ["arXiv", "IEEE Xplore", "Google Scholar"]
        self.results_cache: Dict[str, List[PriorArtResult]] = {}

    def comprehensive_search(self, invention_title: str, abstract: str,
                            claims: List[str]) -> List[PriorArtResult]:
        """
        Perform comprehensive prior art search

        Args:
            invention_title: Title of invention
            abstract: Abstract text
            claims: List of claim texts

        Returns:
            Combined list of prior art results
        """
        all_results = []

        # Extract key terms from title and abstract
        key_terms = self._extract_key_terms(invention_title, abstract)

        # Search patents
        patent_results = self._search_patents(key_terms)
        all_results.extend(patent_results)

        # Search literature
        literature_results = self._search_literature(key_terms)
        all_results.extend(literature_results)

        # Search by classification
        cpc_results = self._search_by_classification(key_terms)
        all_results.extend(cpc_results)

        # Deduplicate and rank
        results = self._deduplicate_and_rank(all_results)

        return results

    def _extract_key_terms(self, title: str, abstract: str) -> List[str]:
        """Extract key search terms"""
        # Simple keyword extraction
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at'}
        text = f"{title} {abstract}".lower()

        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()

        # Filter stop words and short terms
        key_terms = [w for w in words if w not in stop_words and len(w) > 3]

        # Return unique terms (limit to top 10)
        return list(set(key_terms))[:10]

    def _search_patents(self, key_terms: List[str]) -> List[PriorArtResult]:
        """Search patent databases"""
        results = []

        # USPTO search
        USPTO_results = self._search_uspto(key_terms)
        results.extend(USPTO_results)

        # Google Patents search
        google_results = self._search_google_patents(key_terms)
        results.extend(google_results)

        # Espacenet search
        espacenet_results = self._search_espacenet(key_terms)
        results.extend(espacenet_results)

        return results

    def _search_literature(self, key_terms: List[str]) -> List[PriorArtResult]:
        """Search scientific literature"""
        results = []

        # arXiv search
        arxiv_results = self._search_arxiv(key_terms)
        results.extend(arxiv_results)

        # IEEE Xplore search
        ieee_results = self._search_ieee(key_terms)
        results.extend(ieee_results)

        return results

    def _search_by_classification(self, key_terms: List[str]) -> List[PriorArtResult]:
        """Search by patent classification"""
        # Map keywords to CPC classifications
        cpc_mappings = {
            'machine learning': ['G06F17/18', 'G06F3/0481'],
            'neural network': ['G06F17/18'],
            'blockchain': ['G06F17/30'],
            'cryptocurrency': ['G06Q20/38']
        }

        results = []
        for term in key_terms:
            if term in cpc_mappings:
                for cpc in cpc_mappings[term]:
                    # Search by CPC
                    cpc_results = self._search_cpc_class(cpc)
                    results.extend(cpc_results)

        return results

    def _search_uspto(self, key_terms: List[str]) -> List[PriorArtResult]:
        """Search USPTO database"""
        # Placeholder for actual USPTO API calls
        return []

    def _search_google_patents(self, key_terms: List[str]) -> List[PriorArtResult]:
        """Search Google Patents"""
        # Placeholder for actual Google Patents search
        return []

    def _search_espacenet(self, key_terms: List[str]) -> List[PriorArtResult]:
        """Search Espacenet database"""
        # Placeholder for actual Espacenet search
        return []

    def _search_arxiv(self, key_terms: List[str]) -> List[PriorArtResult]:
        """Search arXiv papers"""
        # Placeholder for actual arXiv search
        return []

    def _search_ieee(self, key_terms: List[str]) -> List[PriorArtResult]:
        """Search IEEE Xplore"""
        # Placeholder for actual IEEE search
        return []

    def _search_cpc_class(self, cpc_code: str) -> List[PriorArtResult]:
        """Search by CPC classification"""
        # Placeholder for classification search
        return []

    def _deduplicate_and_rank(self, results: List[PriorArtResult]) -> List[PriorArtResult]:
        """Remove duplicates and rank by relevance"""
        # Remove duplicates by document_id
        unique_results = {}
        for result in results:
            key = f"{result.source}:{result.document_id}"
            if key not in unique_results:
                unique_results[key] = result

        # Sort by relevance score
        sorted_results = sorted(unique_results.values(),
                               key=lambda x: x.relevance_score,
                               reverse=True)

        return sorted_results


# Example usage
if __name__ == "__main__":
    engine = PriorArtSearchEngine()

    title = "Machine Learning Patent Classification System"
    abstract = "A system and method for automatically classifying patents using AI"
    claims = ["A method comprising: receiving patents", "A system for patent classification"]

    results = engine.comprehensive_search(title, abstract, claims)
    print(f"Found {len(results)} prior art results")
