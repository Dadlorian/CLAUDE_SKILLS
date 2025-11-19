"""
Patent Classification Example
Maps patents to CPC and IPC classifications
"""

from typing import List, Dict, Tuple
from enum import Enum

class PatentClassifier:
    """Classify patents into standard classification systems"""

    # CPC to IPC mappings (simplified example)
    CPC_TO_IPC_MAPPING = {
        'G06F17/18': 'G06F',  # Machine learning
        'G06F3/0481': 'G06F',  # User interfaces
        'G06Q20/38': 'G06Q',  # Payment systems
        'H04L63/00': 'H04L',  # Network security
        'C12N15/10': 'C12N',  # Genetic engineering
    }

    # Keyword to CPC mappings
    KEYWORD_TO_CPC_MAPPING = {
        'machine learning': 'G06F17/18',
        'neural network': 'G06F17/18',
        'deep learning': 'G06F17/18',
        'artificial intelligence': 'G06F17/18',
        'blockchain': 'G06F17/30',
        'cryptocurrency': 'G06Q20/38',
        'cryptography': 'H04L63/00',
        'genetic algorithm': 'C12N15/10',
        'biotechnology': 'C12N',
        'nanotechnology': 'B82Y',
    }

    def classify_patent(self, title: str, abstract: str, claims: List[str]) -> Dict:
        """
        Classify patent into CPC and IPC systems

        Args:
            title: Patent title
            abstract: Patent abstract
            claims: List of claims

        Returns:
            Dictionary with classification results
        """
        # Extract keywords from patent documents
        keywords = self._extract_keywords(title, abstract, claims)

        # Identify CPC classifications
        cpc_classifications = self._identify_cpc(keywords, title, abstract)

        # Map to IPC classifications
        ipc_classifications = self._map_to_ipc(cpc_classifications)

        # Calculate confidence scores
        classifications = self._rank_classifications(cpc_classifications, keywords)

        return {
            'cpc_primary': classifications[0] if classifications else None,
            'cpc_all': classifications,
            'ipc_primary': ipc_classifications[0] if ipc_classifications else None,
            'ipc_all': ipc_classifications,
            'keywords': keywords,
            'confidence': self._calculate_confidence(classifications)
        }

    def _extract_keywords(self, title: str, abstract: str, claims: List[str]) -> List[str]:
        """Extract relevant keywords from patent documents"""
        text = f"{title} {abstract} {' '.join(claims)}".lower()

        keywords = []
        for keyword, cpc in self.KEYWORD_TO_CPC_MAPPING.items():
            if keyword.lower() in text:
                keywords.append(keyword)

        return keywords

    def _identify_cpc(self, keywords: List[str], title: str, abstract: str) -> List[str]:
        """Identify applicable CPC classifications"""
        cpc_codes = []

        # Map keywords to CPC
        for keyword in keywords:
            if keyword in self.KEYWORD_TO_CPC_MAPPING:
                cpc = self.KEYWORD_TO_CPC_MAPPING[keyword]
                if cpc not in cpc_codes:
                    cpc_codes.append(cpc)

        return cpc_codes

    def _map_to_ipc(self, cpc_codes: List[str]) -> List[str]:
        """Map CPC codes to IPC codes"""
        ipc_codes = []

        for cpc in cpc_codes:
            if cpc in self.CPC_TO_IPC_MAPPING:
                ipc = self.CPC_TO_IPC_MAPPING[cpc]
                if ipc not in ipc_codes:
                    ipc_codes.append(ipc)

        return ipc_codes

    def _rank_classifications(self, cpc_codes: List[str],
                             keywords: List[str]) -> List[Tuple[str, float]]:
        """Rank classifications by relevance"""
        ranked = []

        for cpc in cpc_codes:
            # Count keyword matches for this classification
            matches = sum(1 for kw in keywords
                         if self.KEYWORD_TO_CPC_MAPPING.get(kw) == cpc)
            confidence = min(0.95, 0.5 + (matches * 0.15))

            ranked.append((cpc, confidence))

        # Sort by confidence
        ranked.sort(key=lambda x: x[1], reverse=True)

        return ranked

    def _calculate_confidence(self, classifications: List[Tuple[str, float]]) -> float:
        """Calculate overall classification confidence"""
        if not classifications:
            return 0.0

        # Average confidence of top classifications
        top_confidences = [conf for _, conf in classifications[:3]]
        return sum(top_confidences) / len(top_confidences)

    def get_cpc_definition(self, cpc_code: str) -> str:
        """Get definition of CPC code"""
        definitions = {
            'G06F17/18': 'Machine learning and artificial intelligence',
            'G06F3/0481': 'User interface systems and techniques',
            'G06Q20/38': 'Payment systems and methods',
            'H04L63/00': 'Network security and protection',
            'C12N15/10': 'Genetic engineering and biotechnology',
        }

        return definitions.get(cpc_code, 'Unknown classification')


# Example usage
if __name__ == "__main__":
    classifier = PatentClassifier()

    title = "Deep Learning Neural Network for Image Classification"
    abstract = "A machine learning system using neural networks for image processing"
    claims = [
        "A method for classifying images using neural networks",
        "A computer system implementing machine learning algorithms"
    ]

    results = classifier.classify_patent(title, abstract, claims)

    print(f"Primary CPC: {results['cpc_primary']}")
    print(f"All CPC codes: {results['cpc_all']}")
    print(f"Primary IPC: {results['ipc_primary']}")
    print(f"Confidence: {results['confidence']:.2%}")
