"""
Document Clustering Example
Demonstrates similarity clustering for efficient batch review
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple
import json

class DocumentClusterer:
    """Clusters similar documents for batch processing"""

    def __init__(self, n_clusters: int = 50, max_features: int = 1000):
        """
        Initialize document clusterer

        Args:
            n_clusters: Number of clusters to create
            max_features: Maximum TF-IDF features
        """
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=2,
            max_df=0.8,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.kmeans = None
        self.feature_names = None

    def cluster_documents(self, documents: List[Dict]) -> Dict:
        """
        Cluster documents by content similarity

        Args:
            documents: List of document dicts with 'id' and 'text' keys

        Returns:
            Dict mapping cluster_id to list of document IDs
        """
        # Extract text content
        texts = [doc.get('text', '') for doc in documents]
        doc_ids = [doc.get('id') for doc in documents]

        # Vectorize documents
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()

        # Cluster
        self.kmeans = KMeans(
            n_clusters=min(self.n_clusters, len(documents)),
            random_state=42,
            n_init=10
        )
        clusters = self.kmeans.fit_predict(tfidf_matrix)

        # Group documents by cluster
        cluster_map = {}
        for doc_id, cluster_id in zip(doc_ids, clusters):
            if cluster_id not in cluster_map:
                cluster_map[cluster_id] = []
            cluster_map[cluster_id].append(doc_id)

        return cluster_map

    def get_cluster_keywords(self, cluster_id: int, top_n: int = 10) -> List[str]:
        """
        Get top keywords for a cluster

        Args:
            cluster_id: Cluster ID
            top_n: Number of top keywords to return

        Returns:
            List of keyword strings
        """
        if self.kmeans is None:
            return []

        # Get cluster center
        center = self.kmeans.cluster_centers_[cluster_id]

        # Get top feature indices
        top_indices = center.argsort()[-top_n:][::-1]

        # Get feature names
        keywords = [self.feature_names[i] for i in top_indices]
        return keywords

    def get_cluster_statistics(self, cluster_map: Dict,
                              document_map: Dict) -> Dict:
        """
        Generate statistics for clusters

        Args:
            cluster_map: Mapping of cluster_id to document IDs
            document_map: Mapping of document_id to document metadata

        Returns:
            Statistics dictionary
        """
        stats = {}

        for cluster_id, doc_ids in cluster_map.items():
            docs = [document_map[did] for did in doc_ids if did in document_map]

            keywords = self.get_cluster_keywords(cluster_id)

            stats[cluster_id] = {
                "document_count": len(doc_ids),
                "keywords": keywords,
                "avg_date": self._avg_date(docs),
                "custodians": list(set(doc.get('custodian', '') for doc in docs))
            }

        return stats

    @staticmethod
    def _avg_date(documents: List[Dict]) -> str:
        """Calculate average document date"""
        dates = [doc.get('date', '') for doc in documents if doc.get('date')]
        return dates[len(dates) // 2] if dates else ""

    def recommend_sample_for_review(self, cluster_map: Dict,
                                   sample_size: int = 5) -> Dict[int, List]:
        """
        Recommend documents to sample for review from each cluster

        Args:
            cluster_map: Cluster mapping
            sample_size: Documents per cluster to review

        Returns:
            Dict mapping cluster_id to sample document IDs
        """
        samples = {}

        for cluster_id, doc_ids in cluster_map.items():
            # Sample evenly distributed documents from cluster
            if len(doc_ids) <= sample_size:
                samples[cluster_id] = doc_ids
            else:
                step = len(doc_ids) // sample_size
                samples[cluster_id] = [doc_ids[i * step] for i in range(sample_size)]

        return samples


class SimilarityDetector:
    """Identifies near-duplicate and similar documents"""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize similarity detector

        Args:
            similarity_threshold: Minimum similarity score (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english'
        )

    def find_similar_documents(self, documents: List[Dict]) -> List[Tuple]:
        """
        Find groups of similar documents

        Args:
            documents: List of documents with 'id' and 'text'

        Returns:
            List of tuples (doc_id1, doc_id2, similarity_score)
        """
        texts = [doc.get('text', '') for doc in documents]
        doc_ids = [doc.get('id') for doc in documents]

        tfidf_matrix = self.vectorizer.fit_transform(texts)
        similarity_matrix = (tfidf_matrix * tfidf_matrix.T).toarray()

        similar_pairs = []
        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                score = similarity_matrix[i, j]
                if score >= self.similarity_threshold:
                    similar_pairs.append((doc_ids[i], doc_ids[j], float(score)))

        return sorted(similar_pairs, key=lambda x: x[2], reverse=True)

    def identify_near_duplicates(self, documents: List[Dict]) -> Dict[int, List[int]]:
        """
        Group near-duplicate documents

        Args:
            documents: List of documents

        Returns:
            Dict mapping primary doc_id to list of duplicate doc_ids
        """
        similar_pairs = self.find_similar_documents(documents)

        # Build groups
        groups = {}
        mapped = set()

        for primary_id, dup_id, score in similar_pairs:
            if primary_id not in mapped:
                groups[primary_id] = [dup_id]
                mapped.add(primary_id)
                mapped.add(dup_id)

        return groups


# Example usage
if __name__ == "__main__":
    # Sample documents
    documents = [
        {"id": 1, "text": "Contract between Company A and Company B regarding services"},
        {"id": 2, "text": "Service agreement between Company A and Company B"},
        {"id": 3, "text": "Email discussing quarterly financial results and performance metrics"},
        {"id": 4, "text": "Email about Q3 financial results and company performance"},
        {"id": 5, "text": "Legal opinion on contract interpretation and enforcement"},
    ]

    # Clustering
    clusterer = DocumentClusterer(n_clusters=2)
    clusters = clusterer.cluster_documents(documents)

    print("Document Clusters:")
    for cluster_id, doc_ids in clusters.items():
        keywords = clusterer.get_cluster_keywords(cluster_id)
        print(f"  Cluster {cluster_id}: {doc_ids}")
        print(f"    Keywords: {keywords}")

    # Similarity detection
    detector = SimilarityDetector(similarity_threshold=0.7)
    duplicates = detector.find_similar_documents(documents)

    print("\nSimilar Documents:")
    for doc1, doc2, score in duplicates:
        print(f"  Doc {doc1} <-> Doc {doc2}: {score:.2%} similarity")
