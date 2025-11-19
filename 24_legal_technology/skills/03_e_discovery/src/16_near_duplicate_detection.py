"""
Near-Duplicate Detection Example
Demonstrates identifying and handling near-duplicate documents
"""

from typing import List, Dict, Set, Tuple
from difflib import SequenceMatcher
import hashlib

class NearDuplicateDetector:
    """Detects near-duplicate documents using similarity metrics"""

    def __init__(self, similarity_threshold: float = 0.90):
        """
        Initialize near-duplicate detector

        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider duplicates
        """
        self.similarity_threshold = similarity_threshold
        self.document_hashes = {}

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)
        """
        # Normalize texts
        t1 = " ".join(text1.lower().split())
        t2 = " ".join(text2.lower().split())

        # Use SequenceMatcher for similarity
        matcher = SequenceMatcher(None, t1, t2)
        return matcher.ratio()

    def find_near_duplicates(self, documents: List[Dict],
                            content_field: str = 'Body') -> List[Tuple]:
        """
        Find near-duplicate documents

        Args:
            documents: List of documents
            content_field: Field containing document content

        Returns:
            List of (doc1_id, doc2_id, similarity_score) tuples
        """
        duplicates = []

        for i in range(len(documents)):
            for j in range(i + 1, len(documents)):
                doc1 = documents[i]
                doc2 = documents[j]

                text1 = str(doc1.get(content_field, ''))
                text2 = str(doc2.get(content_field, ''))

                similarity = self.calculate_text_similarity(text1, text2)

                if similarity >= self.similarity_threshold:
                    duplicates.append((
                        doc1.get('DocumentID'),
                        doc2.get('DocumentID'),
                        similarity
                    ))

        return sorted(duplicates, key=lambda x: x[2], reverse=True)

    def group_duplicates(self, duplicates: List[Tuple]) -> Dict[str, List]:
        """
        Group duplicate documents into clusters

        Args:
            duplicates: List of duplicate tuples

        Returns:
            Dict mapping primary document to duplicates
        """
        groups = {}

        for doc1_id, doc2_id, score in duplicates:
            # Add to group (use first seen as key)
            if doc1_id not in groups:
                groups[doc1_id] = {
                    "primary": doc1_id,
                    "duplicates": [],
                    "similarity_scores": []
                }

            groups[doc1_id]["duplicates"].append(doc2_id)
            groups[doc1_id]["similarity_scores"].append(score)

        return groups

    def calculate_content_hash(self, content: str,
                              algorithm: str = 'sha256',
                              normalize: bool = True) -> str:
        """
        Calculate hash of document content

        Args:
            content: Document content
            algorithm: Hash algorithm
            normalize: Normalize content before hashing

        Returns:
            Hash string
        """
        if normalize:
            # Remove whitespace and normalize
            content = " ".join(content.lower().split())

        if algorithm == 'md5':
            return hashlib.md5(content.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(content.encode()).hexdigest()
        else:  # sha256
            return hashlib.sha256(content.encode()).hexdigest()


class DuplicateManagementStrategy:
    """Manages strategy for handling duplicates"""

    @staticmethod
    def evaluate_deduplication_impact(total_documents: int,
                                     duplicate_percentage: float,
                                     cost_per_document: float = 5.0) -> Dict:
        """
        Evaluate impact of deduplication

        Args:
            total_documents: Total document count
            duplicate_percentage: Percentage of documents that are duplicates
            cost_per_document: Cost per document review

        Returns:
            Deduplication impact analysis
        """
        duplicate_count = int(total_documents * duplicate_percentage / 100)
        non_duplicate_count = total_documents - duplicate_count

        cost_with_dedup = non_duplicate_count * cost_per_document
        cost_without_dedup = total_documents * cost_per_document
        savings = cost_without_dedup - cost_with_dedup

        return {
            "total_documents": total_documents,
            "duplicate_documents": duplicate_count,
            "unique_documents": non_duplicate_count,
            "duplicate_percentage": duplicate_percentage,
            "cost_without_dedup": cost_without_dedup,
            "cost_with_dedup": cost_with_dedup,
            "savings": savings,
            "savings_percentage": round(savings / cost_without_dedup * 100, 1)
        }

    @staticmethod
    def classify_duplicates(duplicates: List[Tuple]) -> Dict:
        """
        Classify duplicates by type

        Args:
            duplicates: List of duplicate tuples

        Returns:
            Classification of duplicate types
        """
        exact = []      # 100% similarity
        near = []       # 95-99% similarity
        partial = []    # 80-94% similarity

        for doc1_id, doc2_id, score in duplicates:
            if score >= 0.99:
                exact.append((doc1_id, doc2_id, score))
            elif score >= 0.95:
                near.append((doc1_id, doc2_id, score))
            else:
                partial.append((doc1_id, doc2_id, score))

        return {
            "exact_duplicates": len(exact),
            "near_duplicates": len(near),
            "partial_duplicates": len(partial),
            "total_duplicate_pairs": len(duplicates),
            "classification": {
                "exact": exact[:5],  # Sample
                "near": near[:5],
                "partial": partial[:5]
            }
        }

    @staticmethod
    def recommend_deduplication_approach(duplicate_stats: Dict) -> str:
        """
        Recommend deduplication approach based on analysis

        Args:
            duplicate_stats: Duplicate statistics

        Returns:
            Recommended approach
        """
        total_dups = duplicate_stats.get("total_duplicate_pairs", 0)
        dedup_rate = (duplicate_stats.get("duplicate_documents", 0) /
                     max(duplicate_stats.get("total_documents", 1), 1) * 100)

        if dedup_rate > 30:
            return "aggressive"  # Remove many duplicates
        elif dedup_rate > 15:
            return "moderate"    # Selective deduplication
        else:
            return "minimal"     # Only exact matches


class DeduplicationWorkflow:
    """Manages deduplication workflow"""

    @staticmethod
    def prepare_for_deduplication(documents: List[Dict]) -> Dict:
        """
        Prepare documents for deduplication process

        Args:
            documents: Documents to prepare

        Returns:
            Preparation report
        """
        return {
            "total_documents": len(documents),
            "documents_ready": len([d for d in documents if d.get('Body')]),
            "documents_missing_content": len([d for d in documents if not d.get('Body')]),
            "preparation_status": "ready" if len(documents) > 0 else "no_documents"
        }

    @staticmethod
    def mark_duplicates(documents: List[Dict],
                       duplicates: List[Tuple],
                       keep_strategy: str = 'first_received') -> Dict:
        """
        Mark documents as primary or duplicate

        Args:
            documents: All documents
            duplicates: List of duplicate tuples
            keep_strategy: Strategy for keeping document ('first_received', 'longest', 'most_recipients')

        Returns:
            Updated document list with marking
        """
        # Create document map
        doc_map = {doc.get('DocumentID'): doc for doc in documents}

        # Mark duplicates
        for doc1_id, doc2_id, score in duplicates:
            if doc2_id in doc_map:
                doc_map[doc2_id]['IsDuplicate'] = True
                doc_map[doc2_id]['DuplicateOf'] = doc1_id
                doc_map[doc2_id]['SimilarityScore'] = score

            if doc1_id in doc_map:
                doc_map[doc1_id]['IsPrimary'] = True

        return {
            "primary_documents": len([d for d in documents if d.get('IsPrimary')]),
            "duplicate_documents": len([d for d in documents if d.get('IsDuplicate')]),
            "total_marked": len([d for d in documents if d.get('IsDuplicate') or d.get('IsPrimary')])
        }

    @staticmethod
    def generate_deduplication_report(documents: List[Dict],
                                     duplicates: List[Tuple]) -> Dict:
        """
        Generate final deduplication report

        Args:
            documents: All documents
            duplicates: Duplicate pairs

        Returns:
            Final report
        """
        primary_count = len([d for d in documents if d.get('IsPrimary')])
        duplicate_count = len([d for d in documents if d.get('IsDuplicate')])

        # Calculate review hours saved (estimate 3 minutes per duplicate)
        hours_saved = duplicate_count * 3 / 60

        return {
            "pre_dedup_count": len(documents),
            "post_dedup_count": primary_count,
            "duplicates_removed": duplicate_count,
            "deduplication_rate": round(duplicate_count / len(documents) * 100, 1),
            "duplicate_pairs_identified": len(duplicates),
            "estimated_review_hours_saved": round(hours_saved, 1),
            "estimated_cost_savings": round(hours_saved * 200, 0)  # $200/hour rate
        }


# Example usage
if __name__ == "__main__":
    detector = NearDuplicateDetector(similarity_threshold=0.90)

    docs = [
        {"DocumentID": 1, "Body": "This is a contract agreement between parties"},
        {"DocumentID": 2, "Body": "This is a contract agreement between the parties"},  # Near duplicate
        {"DocumentID": 3, "Body": "This is a completely different document"}
    ]

    # Calculate similarity
    sim1_2 = detector.calculate_text_similarity(
        docs[0]["Body"],
        docs[1]["Body"]
    )
    print(f"Similarity between Doc 1 and 2: {sim1_2:.2%}")

    # Find duplicates
    duplicates = detector.find_near_duplicates(docs)
    print(f"Found {len(duplicates)} duplicate pairs")

    # Impact analysis
    impact = DuplicateManagementStrategy.evaluate_deduplication_impact(
        total_documents=10000,
        duplicate_percentage=25
    )
    print(f"Potential Savings: ${impact['savings']:,.0f}")
