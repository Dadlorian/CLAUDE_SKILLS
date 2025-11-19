"""
Semantic Legal Search using BERT embeddings
Find conceptually similar cases beyond keyword matching
"""

import numpy as np
from typing import List, Dict, Tuple
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity


class LegalSemanticSearch:
    """
    Semantic search for legal documents using Legal-BERT
    """

    def __init__(self, model_name="nlpaueb/legal-bert-base-uncased"):
        """
        Initialize with Legal-BERT model

        Args:
            model_name: HuggingFace model identifier
        """
        print(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

        self.case_database = []
        self.case_embeddings = []

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate BERT embedding for text

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Use [CLS] token embedding
        embedding = outputs.last_hidden_state[:, 0, :].numpy()[0]

        return embedding

    def index_cases(self, cases: List[Dict]):
        """
        Index case law database

        Args:
            cases: List of case dictionaries with 'text' field
        """
        print(f"Indexing {len(cases)} cases...")

        self.case_database = cases
        self.case_embeddings = []

        for i, case in enumerate(cases):
            if i % 10 == 0:
                print(f"  Indexed {i}/{len(cases)}")

            embedding = self.generate_embedding(case["text"])
            self.case_embeddings.append(embedding)

        self.case_embeddings = np.array(self.case_embeddings)

        print("Indexing complete")

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Dict, float]]:
        """
        Semantic search for similar cases

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (case, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Calculate cosine similarity
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1),
            self.case_embeddings
        )[0]

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Return results
        results = [
            (self.case_database[idx], float(similarities[idx]))
            for idx in top_indices
        ]

        return results


def main():
    """Example usage"""
    # Sample case database (in practice, load from database)
    cases = [
        {
            "citation": "410 U.S. 113",
            "title": "Roe v. Wade",
            "text": "The Court held that a woman's right to an abortion fell within the right to privacy protected by the Fourteenth Amendment..."
        },
        {
            "citation": "505 U.S. 833",
            "title": "Planned Parenthood v. Casey",
            "text": "The Court reaffirmed Roe but replaced the trimester framework with an undue burden standard..."
        },
        # Add more cases...
    ]

    # Initialize semantic search
    search_engine = LegalSemanticSearch()

    # Index cases
    search_engine.index_cases(cases)

    # Search
    query = "Can states restrict abortion access?"

    print(f"\nSearching for: {query}\n")

    results = search_engine.search(query, top_k=5)

    for i, (case, score) in enumerate(results, 1):
        print(f"{i}. {case['citation']}: {case['title']}")
        print(f"   Similarity: {score:.4f}")
        print(f"   {case['text'][:150]}...")
        print()


if __name__ == "__main__":
    main()
