"""
LexisNexis API Client
Production-ready client for LexisNexis API with Shepard's integration
"""

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LexisSearchResult:
    """Search result from LexisNexis"""
    citation: str
    title: str
    court: str
    date: str
    summary: str
    shepards_signal: Optional[str] = None


class LexisNexisAPIClient:
    """
    Production LexisNexis API client
    """

    def __init__(self, api_key: str):
        """
        Initialize client

        Args:
            api_key: LexisNexis API key
        """
        self.api_key = api_key
        self.api_base = "https://api.lexisnexis.com"
        self.session = requests.Session()

    def search(self, query: str, sources: List[str] = None,
               limit: int = 50) -> List[LexisSearchResult]:
        """
        Execute search query

        Args:
            query: Search query (Boolean or natural language)
            sources: List of sources to search (e.g., ["Federal Cases, Combined"])
            limit: Maximum results

        Returns:
            List of LexisSearchResult objects
        """
        endpoint = f"{self.api_base}/search/v1"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": query,
            "sources": sources or ["Federal Cases, Combined"],
            "limit": limit,
            "sortBy": "relevance"
        }

        logger.info(f"Searching LexisNexis: {query}")

        response = self.session.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()

        results = [
            LexisSearchResult(
                citation=doc.get("citation", ""),
                title=doc.get("title", ""),
                court=doc.get("court", ""),
                date=doc.get("date", ""),
                summary=doc.get("summary", "")
            )
            for doc in data.get("documents", [])
        ]

        logger.info(f"Found {len(results)} results")

        return results

    def shepardize(self, citation: str) -> Dict:
        """
        Shepardize citation

        Args:
            citation: Citation to Shepardize

        Returns:
            Shepard's analysis dictionary
        """
        endpoint = f"{self.api_base}/shepards/v1/citation"

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        params = {
            "citation": citation,
            "analysis": "full"
        }

        logger.info(f"Shepardizing: {citation}")

        response = self.session.get(endpoint, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()

        return {
            "citation": citation,
            "signal": data.get("shepards_signal"),
            "citing_decisions_count": data.get("citing_count"),
            "negative_treatment": data.get("negative_treatment", []),
            "positive_treatment": data.get("positive_treatment", []),
            "appellate_history": data.get("appellate_history", [])
        }

    def get_document(self, citation: str) -> Dict:
        """
        Retrieve full document

        Args:
            citation: Document citation

        Returns:
            Document dictionary
        """
        endpoint = f"{self.api_base}/document/v1"

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        params = {"citation": citation}

        response = self.session.get(endpoint, params=params, headers=headers)
        response.raise_for_status()

        return response.json()


def main():
    """Example usage"""
    client = LexisNexisAPIClient("YOUR_API_KEY")

    # Search
    results = client.search("summary judgment", limit=10)

    print(f"\nSearch Results ({len(results)}):\n")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result.citation}: {result.title}")
        print(f"   Court: {result.court}")
        print()

    # Shepardize
    if results:
        shepards = client.shepardize(results[0].citation)

        print(f"\nShepard's for {shepards['citation']}:")
        print(f"  Signal: {shepards['signal']}")
        print(f"  Citing Decisions: {shepards['citing_decisions_count']}")


if __name__ == "__main__":
    main()
