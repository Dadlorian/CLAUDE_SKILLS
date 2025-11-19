"""
Contract Clause Extraction using Pattern Matching and ML
Extract specific clauses from contracts: indemnification, liability, termination, etc.
"""

import re
from typing import List, Dict, Tuple
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ClauseExtractor:
    """Extract clauses from legal contracts"""

    def __init__(self):
        # Load spaCy model for sentence segmentation
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Downloading spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        # Define clause patterns
        self.clause_patterns = self.get_clause_patterns()

        # Initialize vectorizer for semantic matching
        self.vectorizer = TfidfVectorizer()

    def get_clause_patterns(self) -> Dict[str, List[str]]:
        """Define regex patterns for different clause types"""

        return {
            "indemnification": [
                r"indemnif[yz]",
                r"hold\s+harmless",
                r"defend.*against.*claims",
                r"reimburse.*for.*losses"
            ],
            "limitation_of_liability": [
                r"limitation\s+of\s+liability",
                r"liability.*shall.*not\s+exceed",
                r"in\s+no\s+event.*liable",
                r"maximum\s+liability",
                r"cap\s+on\s+damages"
            ],
            "termination": [
                r"terminat(e|ion)",
                r"cancel(lation)?",
                r"end\s+this\s+agreement",
                r"upon.*notice"
            ],
            "confidentiality": [
                r"confidential(ity)?",
                r"proprietary\s+information",
                r"non-disclosure",
                r"keep.*secret"
            ],
            "governing_law": [
                r"governing\s+law",
                r"governed\s+by",
                r"laws\s+of\s+(the\s+)?state",
                r"jurisdiction"
            ],
            "payment_terms": [
                r"payment",
                r"invoice",
                r"fees?",
                r"compensation",
                r"shall\s+pay"
            ],
            "intellectual_property": [
                r"intellectual\s+property",
                r"IP\s+rights",
                r"copyright",
                r"trademark",
                r"patent",
                r"work\s+for\s+hire"
            ],
            "warranty": [
                r"warrant(y|ies)",
                r"guarantee",
                r"represent\s+and\s+warrant",
                r"disclaim.*warranties"
            ],
            "dispute_resolution": [
                r"arbitration",
                r"mediation",
                r"dispute\s+resolution",
                r"litigation",
                r"venue"
            ],
            "force_majeure": [
                r"force\s+majeure",
                r"act\s+of\s+god",
                r"beyond.*control",
                r"unforeseeable\s+circumstances"
            ]
        }

    def extract_sentences(self, text: str) -> List[str]:
        """Split contract into sentences"""

        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        return sentences

    def pattern_match_clause(self, sentence: str, patterns: List[str]) -> bool:
        """Check if sentence matches clause patterns"""

        sentence_lower = sentence.lower()
        for pattern in patterns:
            if re.search(pattern, sentence_lower):
                return True
        return False

    def extract_clauses_by_pattern(self, contract_text: str) -> Dict[str, List[str]]:
        """Extract clauses using pattern matching"""

        sentences = self.extract_sentences(contract_text)
        extracted_clauses = {clause_type: [] for clause_type in self.clause_patterns}

        for sentence in sentences:
            for clause_type, patterns in self.clause_patterns.items():
                if self.pattern_match_clause(sentence, patterns):
                    extracted_clauses[clause_type].append(sentence)

        return extracted_clauses

    def extract_clause_by_semantic_search(
        self,
        contract_text: str,
        clause_examples: List[str],
        threshold: float = 0.3
    ) -> List[Tuple[str, float]]:
        """Extract clauses using semantic similarity"""

        sentences = self.extract_sentences(contract_text)

        # Vectorize examples and sentences
        all_texts = clause_examples + sentences
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)

        # Calculate similarity
        example_vectors = tfidf_matrix[:len(clause_examples)]
        sentence_vectors = tfidf_matrix[len(clause_examples):]

        similarities = cosine_similarity(sentence_vectors, example_vectors)

        # Get max similarity for each sentence
        max_similarities = similarities.max(axis=1)

        # Extract matching clauses
        matching_clauses = []
        for i, similarity in enumerate(max_similarities):
            if similarity >= threshold:
                matching_clauses.append((sentences[i], similarity))

        return sorted(matching_clauses, key=lambda x: x[1], reverse=True)

    def extract_clause_context(
        self,
        contract_text: str,
        clause_sentence: str,
        context_sentences: int = 2
    ) -> str:
        """Extract clause with surrounding context"""

        sentences = self.extract_sentences(contract_text)

        # Find clause position
        try:
            idx = sentences.index(clause_sentence)
        except ValueError:
            return clause_sentence

        # Get context
        start = max(0, idx - context_sentences)
        end = min(len(sentences), idx + context_sentences + 1)

        context = " ".join(sentences[start:end])
        return context

    def extract_section_by_heading(
        self,
        contract_text: str,
        heading_pattern: str
    ) -> str:
        """Extract entire section by heading"""

        # Find section heading
        match = re.search(
            rf"^\s*\d+\.?\s*{heading_pattern}.*$",
            contract_text,
            re.MULTILINE | re.IGNORECASE
        )

        if not match:
            return ""

        start = match.start()

        # Find next section heading
        next_section = re.search(
            r"^\s*\d+\.?\s+[A-Z]",
            contract_text[start + len(match.group()):],
            re.MULTILINE
        )

        if next_section:
            end = start + len(match.group()) + next_section.start()
        else:
            end = len(contract_text)

        return contract_text[start:end].strip()

def main():
    """Demonstrate clause extraction"""

    # Sample contract
    contract = """
    MASTER SERVICES AGREEMENT

    1. CONFIDENTIALITY
    Each party agrees to maintain the confidentiality of all Confidential Information
    disclosed by the other party. Neither party shall disclose such information to third
    parties without prior written consent.

    2. INDEMNIFICATION
    Supplier shall indemnify, defend, and hold harmless Client from any and all claims,
    damages, losses, and expenses arising out of Supplier's breach of this Agreement or
    negligence in performing the Services.

    3. LIMITATION OF LIABILITY
    In no event shall either party's total liability under this Agreement exceed the fees
    paid by Client in the twelve (12) months preceding the claim. Neither party shall be
    liable for indirect, incidental, consequential, or punitive damages.

    4. TERMINATION
    Either party may terminate this Agreement upon thirty (30) days' written notice.
    Client may terminate immediately upon Supplier's material breach that remains uncured
    for fifteen (15) days after notice.

    5. PAYMENT TERMS
    Client shall pay Supplier the fees specified in the Statement of Work within thirty
    (30) days of receipt of invoice. Late payments shall accrue interest at 1.5% per month.

    6. GOVERNING LAW
    This Agreement shall be governed by and construed in accordance with the laws of the
    State of Delaware, without regard to its conflicts of law principles.

    7. DISPUTE RESOLUTION
    Any dispute arising under this Agreement shall be resolved through binding arbitration
    in accordance with the Commercial Arbitration Rules of the American Arbitration Association.
    """

    print("="*70)
    print("CONTRACT CLAUSE EXTRACTION DEMO")
    print("="*70)

    extractor = ClauseExtractor()

    # Method 1: Pattern-based extraction
    print("\n1. PATTERN-BASED EXTRACTION")
    print("-"*70)

    clauses = extractor.extract_clauses_by_pattern(contract)

    for clause_type, sentences in clauses.items():
        if sentences:
            print(f"\n{clause_type.upper().replace('_', ' ')} ({len(sentences)} found):")
            for sent in sentences:
                print(f"  - {sent[:100]}...")

    # Method 2: Semantic search
    print("\n\n2. SEMANTIC SEARCH EXTRACTION")
    print("-"*70)

    # Example indemnification clauses for semantic matching
    indem_examples = [
        "The supplier shall indemnify the client against all claims.",
        "Company agrees to defend and hold harmless the customer."
    ]

    print("\nSearching for indemnification clauses (semantic similarity):")
    semantic_matches = extractor.extract_clause_by_semantic_search(
        contract,
        indem_examples,
        threshold=0.2
    )

    for clause, score in semantic_matches[:3]:
        print(f"\nSimilarity: {score:.2f}")
        print(f"Clause: {clause[:150]}...")

    # Method 3: Section extraction
    print("\n\n3. SECTION EXTRACTION BY HEADING")
    print("-"*70)

    liability_section = extractor.extract_section_by_heading(contract, "LIABILITY")
    print(f"\nLIABILITY Section:\n{liability_section}")

    # Method 4: Extract with context
    print("\n\n4. CLAUSE WITH CONTEXT")
    print("-"*70)

    termination_clause = "Either party may terminate this Agreement upon thirty (30) days' written notice."
    context = extractor.extract_clause_context(contract, termination_clause, context_sentences=1)
    print(f"\nTermination clause with context:\n{context}")

if __name__ == "__main__":
    main()
