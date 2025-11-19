"""
Legal NLP Engine
Natural Language Processing for legal documents and case analysis
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Named entity extracted from legal text"""
    text: str
    entity_type: str  # PERSON, ORGANIZATION, STATUTE, CASE, DATE, etc.
    position: Tuple[int, int]  # Start and end positions
    confidence: float


@dataclass
class LegalConcept:
    """Legal concept identified in text"""
    name: str
    category: str  # tort, contract, criminal, etc.
    mentions: int
    context_snippets: List[str]


class LegalNLPEngine:
    """
    NLP engine for legal document analysis
    """

    # Entity patterns
    ENTITY_PATTERNS = {
        "STATUTE": r"\d+\s+U\.S\.C\.|C\.F\.R\.|[A-Z][a-z]+\.?\s+(?:Code|Stat\.)",
        "CASE": r"[A-Z][a-z\.\s]+(?:v\.|v\.\.)\s+[A-Z][a-z\.\s]+",
        "DATE": r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
        "PERSON": r"\b(?:Mr\.|Ms\.|Dr\.|Judge|Justice|Hon\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?",
        "ORGANIZATION": r"\b(?:Court|Department|Agency|Administration|Office|Commission)\s+(?:of|for)\s+[A-Z][a-z\s]+",
    }

    # Legal concepts
    LEGAL_CONCEPTS = {
        "contract": ["agreement", "consideration", "offer", "acceptance", "breach", "performance"],
        "tort": ["negligence", "duty", "breach of duty", "causation", "damages", "strict liability"],
        "criminal": ["felony", "misdemeanor", "mens rea", "actus reus", "guilt", "innocence"],
        "property": ["title", "possession", "ownership", "lien", "mortgage", "deed"],
        "constitutional": ["amendment", "due process", "equal protection", "fundamental right"],
    }

    def __init__(self):
        """Initialize NLP engine"""
        self.compiled_patterns = {
            name: re.compile(pattern)
            for name, pattern in self.ENTITY_PATTERNS.items()
        }

    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """
        Extract named entities from legal text

        Args:
            text: Legal text to analyze

        Returns:
            List of extracted entities
        """
        entities = []

        for entity_type, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                entity = ExtractedEntity(
                    text=match.group(0),
                    entity_type=entity_type,
                    position=(match.start(), match.end()),
                    confidence=0.85
                )
                entities.append(entity)

        # Sort by position
        entities.sort(key=lambda e: e.position[0])

        logger.info(f"Extracted {len(entities)} entities from text")
        return entities

    def identify_legal_concepts(self, text: str) -> List[LegalConcept]:
        """
        Identify legal concepts in text

        Args:
            text: Legal text to analyze

        Returns:
            List of identified legal concepts
        """
        concepts = []
        text_lower = text.lower()

        for category, keywords in self.LEGAL_CONCEPTS.items():
            for keyword in keywords:
                mentions = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))

                if mentions > 0:
                    # Extract context snippets
                    snippets = []
                    for match in re.finditer(r'.{0,50}' + re.escape(keyword) + r'.{0,50}', text_lower):
                        snippets.append(match.group(0))

                    concept = LegalConcept(
                        name=keyword,
                        category=category,
                        mentions=mentions,
                        context_snippets=snippets[:3]
                    )
                    concepts.append(concept)

        logger.info(f"Identified {len(concepts)} legal concepts")
        return concepts

    def extract_key_phrases(self, text: str, num_phrases: int = 10) -> List[Tuple[str, float]]:
        """
        Extract key phrases from legal text

        Args:
            text: Legal text to analyze
            num_phrases: Number of phrases to extract

        Returns:
            List of (phrase, importance_score) tuples
        """
        # Simple TF-IDF-like approach
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}

        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        sorted_phrases = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # Score based on frequency
        max_freq = sorted_phrases[0][1] if sorted_phrases else 1
        key_phrases = [
            (phrase, freq / max_freq)
            for phrase, freq in sorted_phrases[:num_phrases]
        ]

        return key_phrases

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Simple sentiment analysis for legal text

        Args:
            text: Legal text to analyze

        Returns:
            Dictionary with sentiment scores
        """
        positive_indicators = ["upheld", "affirmed", "valid", "enforceable", "prevails"]
        negative_indicators = ["violated", "breach", "denied", "reversed", "invalid"]
        neutral_indicators = ["held", "determined", "found", "stated", "concluded"]

        text_lower = text.lower()

        positive_count = sum(1 for indicator in positive_indicators if indicator in text_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
        neutral_count = sum(1 for indicator in neutral_indicators if indicator in text_lower)

        total = positive_count + negative_count + neutral_count or 1

        return {
            "positive": positive_count / total,
            "negative": negative_count / total,
            "neutral": neutral_count / total,
            "overall": (positive_count - negative_count) / total
        }

    def extract_legal_obligations(self, text: str) -> List[str]:
        """
        Extract legal obligations and requirements from text

        Args:
            text: Legal text to analyze

        Returns:
            List of identified obligations
        """
        obligation_patterns = [
            r"(?:shall|must|is required to)\s+([^.]+)",
            r"(?:party|parties)\s+(?:shall|must)\s+([^.]+)",
            r"(?:the|a)\s+(?:defendant|plaintiff|party)\s+(?:shall|will)\s+([^.]+)"
        ]

        obligations = []
        for pattern in obligation_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                obligations.append(match.group(1).strip())

        return obligations[:10]  # Limit to 10 obligations

    def summarize_text(self, text: str, num_sentences: int = 3) -> str:
        """
        Extract key sentences as summary

        Args:
            text: Legal text to summarize
            num_sentences: Number of sentences to include

        Returns:
            Summary text
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= num_sentences:
            return text

        # Score sentences by keyword frequency
        concepts = self.identify_legal_concepts(text)
        concept_names = [c.name for c in concepts]

        def score_sentence(sentence):
            score = 0
            for concept in concept_names:
                score += sentence.lower().count(concept)
            return score

        scored_sentences = [(i, s, score_sentence(s)) for i, s in enumerate(sentences)]
        top_sentences = sorted(scored_sentences, key=lambda x: x[2], reverse=True)[:num_sentences]
        top_sentences.sort(key=lambda x: x[0])

        return '. '.join([s[1] for s in top_sentences]) + '.'


# Usage example
if __name__ == "__main__":
    engine = LegalNLPEngine()

    sample_text = """
    In this contract, Party A agrees to deliver goods by January 15, 2024.
    The defendant breached the agreement by failing to perform.
    The court held that the breach was material and enforceable.
    """

    # Extract entities
    entities = engine.extract_entities(sample_text)
    print(f"Entities: {[(e.text, e.entity_type) for e in entities]}")

    # Identify legal concepts
    concepts = engine.identify_legal_concepts(sample_text)
    print(f"Legal Concepts: {[(c.name, c.category) for c in concepts]}")

    # Extract obligations
    obligations = engine.extract_legal_obligations(sample_text)
    print(f"Obligations: {obligations}")

    # Analyze sentiment
    sentiment = engine.analyze_sentiment(sample_text)
    print(f"Sentiment: {sentiment}")
