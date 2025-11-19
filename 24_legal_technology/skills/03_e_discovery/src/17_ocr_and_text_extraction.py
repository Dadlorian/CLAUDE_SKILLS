"""
OCR and Text Extraction Example
Demonstrates optical character recognition and text extraction
"""

from typing import List, Dict, Optional
import re

class TextExtractor:
    """Extracts and processes text from documents"""

    @staticmethod
    def extract_text_from_document(document: Dict) -> str:
        """
        Extract searchable text from document

        Args:
            document: Document data

        Returns:
            Extracted text
        """
        # Combine searchable fields
        text_parts = []

        # Extract from common fields
        fields = ['Body', 'Subject', 'Title', 'Content', 'OCRText', 'ExtractedText']

        for field in fields:
            if field in document and document[field]:
                text_parts.append(str(document[field]))

        return "\n".join(text_parts)

    @staticmethod
    def clean_extracted_text(text: str) -> str:
        """
        Clean extracted text for indexing

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep alphanumeric and basic punctuation
        text = re.sub(r'[^\w\s\.\,\:\;\-\(\)]', '', text)

        # Remove very long words (likely OCR errors)
        words = text.split()
        cleaned_words = [w for w in words if len(w) <= 50]

        return " ".join(cleaned_words)

    @staticmethod
    def extract_key_phrases(text: str,
                           phrase_length: int = 3) -> List[str]:
        """
        Extract key phrases from text

        Args:
            text: Document text
            phrase_length: Words per phrase

        Returns:
            List of key phrases
        """
        words = text.lower().split()
        phrases = []

        for i in range(len(words) - phrase_length + 1):
            phrase = " ".join(words[i:i + phrase_length])
            phrases.append(phrase)

        # Return most frequent phrases
        from collections import Counter
        counts = Counter(phrases)
        return [phrase for phrase, count in counts.most_common(10)]


class OCRProcessor:
    """Manages OCR processing for image-based documents"""

    def __init__(self, confidence_threshold: float = 0.75):
        """
        Initialize OCR processor

        Args:
            confidence_threshold: Minimum confidence for OCR acceptance
        """
        self.confidence_threshold = confidence_threshold
        self.ocr_results = {}

    def process_image_document(self, document_id: str,
                              image_path: str) -> Dict:
        """
        Process image document through OCR

        Args:
            document_id: Document identifier
            image_path: Path to image file

        Returns:
            OCR processing result
        """
        # Simulated OCR result
        result = {
            "document_id": document_id,
            "image_path": image_path,
            "ocr_status": "processed",
            "confidence_score": 0.87,
            "extracted_text": "This is extracted text from OCR",
            "character_count": 100,
            "language_detected": "English"
        }

        self.ocr_results[document_id] = result
        return result

    def evaluate_ocr_quality(self, ocr_result: Dict) -> Dict:
        """
        Evaluate quality of OCR extraction

        Args:
            ocr_result: Result from OCR processing

        Returns:
            Quality assessment
        """
        confidence = ocr_result.get('confidence_score', 0)

        if confidence >= 0.90:
            quality = "high"
        elif confidence >= 0.75:
            quality = "acceptable"
        else:
            quality = "poor"

        return {
            "document_id": ocr_result.get('document_id'),
            "confidence_score": confidence,
            "quality_assessment": quality,
            "requires_manual_review": quality == "poor",
            "recommendation": "use_as_is" if quality != "poor" else "manual_correction_needed"
        }

    def batch_ocr_process(self, documents: List[Dict]) -> Dict:
        """
        Process multiple documents through OCR

        Args:
            documents: List of documents to process

        Returns:
            Batch processing summary
        """
        results = {
            "total_documents": len(documents),
            "successfully_processed": 0,
            "high_quality": 0,
            "acceptable_quality": 0,
            "poor_quality": 0,
            "failed": 0,
            "average_confidence": 0.0
        }

        confidence_scores = []

        for doc in documents:
            # Simulate OCR processing
            confidence = 0.85  # Example confidence

            results["successfully_processed"] += 1
            confidence_scores.append(confidence)

            if confidence >= 0.90:
                results["high_quality"] += 1
            elif confidence >= 0.75:
                results["acceptable_quality"] += 1
            else:
                results["poor_quality"] += 1

        if confidence_scores:
            results["average_confidence"] = sum(confidence_scores) / len(confidence_scores)

        return results


class TextNormalization:
    """Normalizes extracted text for searching and analysis"""

    @staticmethod
    def normalize_names(text: str) -> str:
        """
        Normalize person names in text

        Args:
            text: Text containing names

        Returns:
            Normalized text
        """
        # Convert common name patterns
        # Example: "Smith, John" -> "John Smith"
        text = re.sub(r'([A-Z][a-z]+),\s+([A-Z][a-z]+)', r'\2 \1', text)

        return text

    @staticmethod
    def normalize_dates(text: str) -> str:
        """
        Normalize dates to standard format

        Args:
            text: Text with dates

        Returns:
            Text with normalized dates
        """
        # Convert various date formats to YYYY-MM-DD
        patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{2,4})', r'\3-\1-\2'),  # MM/DD/YYYY
            (r'(\d{1,2})-(\d{1,2})-(\d{2,4})', r'\3-\1-\2'),  # MM-DD-YYYY
        ]

        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)

        return text

    @staticmethod
    def normalize_phone_numbers(text: str) -> str:
        """
        Normalize phone numbers

        Args:
            text: Text with phone numbers

        Returns:
            Text with normalized numbers
        """
        # Convert to standard format: (XXX) XXX-XXXX
        pattern = r'(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{4})'
        replacement = r'(\1) \2-\3'

        return re.sub(pattern, replacement, text)

    @staticmethod
    def remove_boilerplate(text: str,
                          boilerplate_patterns: List[str]) -> str:
        """
        Remove boilerplate text

        Args:
            text: Document text
            boilerplate_patterns: Patterns to remove

        Returns:
            Text with boilerplate removed
        """
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text


class TextIndexing:
    """Creates searchable text indexes"""

    @staticmethod
    def create_text_index(documents: List[Dict],
                         text_field: str = 'Body') -> Dict:
        """
        Create text index for documents

        Args:
            documents: Documents to index
            text_field: Field containing text

        Returns:
            Text index
        """
        from collections import defaultdict

        index = defaultdict(list)

        for doc in documents:
            doc_id = doc.get('DocumentID')
            text = str(doc.get(text_field, '')).lower()

            # Create word index
            words = re.findall(r'\b\w+\b', text)

            for word in set(words):
                index[word].append(doc_id)

        return dict(index)

    @staticmethod
    def search_index(index: Dict, search_terms: List[str]) -> Dict:
        """
        Search text index

        Args:
            index: Text index
            search_terms: Terms to search

        Returns:
            Search results
        """
        results = defaultdict(set)

        for term in search_terms:
            term_lower = term.lower()
            if term_lower in index:
                results[term] = set(index[term_lower])

        # Find documents matching all terms
        if results:
            all_matches = set.intersection(*results.values())
        else:
            all_matches = set()

        return {
            "search_terms": search_terms,
            "matching_documents": list(all_matches),
            "match_count": len(all_matches)
        }


# Example usage
if __name__ == "__main__":
    extractor = TextExtractor()

    # Sample document
    doc = {
        "DocumentID": "001",
        "Subject": "Contract Review",
        "Body": "This is a sample contract document with terms and conditions"
    }

    text = extractor.extract_text_from_document(doc)
    cleaned = extractor.clean_extracted_text(text)
    phrases = extractor.extract_key_phrases(cleaned)

    print(f"Extracted Text: {text}")
    print(f"Key Phrases: {phrases}")

    # OCR Processing
    ocr = OCRProcessor()
    result = ocr.process_image_document("001", "/path/to/image.tiff")
    quality = ocr.evaluate_ocr_quality(result)

    print(f"OCR Quality: {quality['quality_assessment']}")
