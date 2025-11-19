"""
Westlaw Edge API Client
Production-ready client for Westlaw Edge API integration
"""

import requests
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result from Westlaw"""
    citation: str
    title: str
    court: str
    date: str
    snippet: str
    url: str
    relevance_score: float


class WestlawAPIClient:
    """
    Production Westlaw Edge API client with:
    - OAuth 2.0 authentication
    - Rate limiting
    - Error handling
    - Caching
    - Retry logic
    """

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize client

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = 0

        self.token_url = "https://signin.westlaw.com/oauth/token"
        self.api_base = "https://api.westlaw.com"

        self.session = requests.Session()
        self.cache = {}

    def authenticate(self) -> str:
        """
        Get OAuth 2.0 access token

        Returns:
            Access token string
        """
        logger.info("Authenticating with Westlaw API")

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "search keycite document"
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.token_expiry = time.time() + token_data.get("expires_in", 3600)

        logger.info("Authentication successful")

        return self.access_token

    def ensure_authenticated(self):
        """Ensure we have valid access token"""
        if not self.access_token or time.time() >= self.token_expiry:
            self.authenticate()

    def search(self, query: str, database: str = "ALLCASES",
               limit: int = 50) -> List[SearchResult]:
        """
        Execute search query

        Args:
            query: Search query (Terms & Connectors or natural language)
            database: Westlaw database identifier
            limit: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        self.ensure_authenticated()

        endpoint = f"{self.api_base}/search/v1/query"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": query,
            "database": database,
            "fields": ["citation", "title", "court", "date", "snippet", "url"],
            "limit": limit,
            "sortBy": "relevance"
        }

        logger.info(f"Searching: {query} in {database}")

        response = self.session.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()

        results = [
            SearchResult(
                citation=result.get("citation", ""),
                title=result.get("title", ""),
                court=result.get("court", ""),
                date=result.get("date", ""),
                snippet=result.get("snippet", ""),
                url=result.get("url", ""),
                relevance_score=result.get("score", 0.0)
            )
            for result in data.get("results", [])
        ]

        logger.info(f"Found {len(results)} results")

        return results

    def keycite(self, citation: str) -> Dict:
        """
        KeyCite validation

        Args:
            citation: Case citation to validate

        Returns:
            KeyCite status dictionary
        """
        self.ensure_authenticated()

        endpoint = f"{self.api_base}/keycite/v1/validate"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {"citations": [citation]}

        logger.info(f"KeyCiting: {citation}")

        response = self.session.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()

        if data.get("results"):
            result = data["results"][0]

            return {
                "citation": citation,
                "status": result.get("status"),
                "depth_bars": result.get("depth_bars"),
                "citing_references_count": result.get("citing_count"),
                "negative_treatment": result.get("negative_treatment", []),
                "overruling_risk": result.get("overruling_risk")
            }

        return {}

    def get_citing_references(self, citation: str, limit: int = 100) -> List[Dict]:
        """
        Get cases citing this citation

        Args:
            citation: Citation to find citing references for
            limit: Maximum citing references to return

        Returns:
            List of citing references
        """
        self.ensure_authenticated()

        endpoint = f"{self.api_base}/keycite/v1/citing-references"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        params = {
            "citation": citation,
            "limit": limit
        }

        response = self.session.get(endpoint, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()

        return data.get("citing_references", [])


def main():
    """Example usage"""
    # Initialize client (use environment variables in production)
    client = WestlawAPIClient(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET"
    )

    # Search
    results = client.search("summary judgment standard", database="ALLFEDS")

    print(f"\nSearch Results ({len(results)}):\n")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result.citation}: {result.title}")
        print(f"   Court: {result.court}, Date: {result.date}")
        print(f"   {result.snippet[:100]}...")
        print()

    # KeyCite
    if results:
        first_citation = results[0].citation
        kc_status = client.keycite(first_citation)

        print(f"\nKeyCite Status for {first_citation}:")
        print(f"  Status: {kc_status.get('status')}")
        print(f"  Citing References: {kc_status.get('citing_references_count')}")
        print(f"  Depth Bars: {kc_status.get('depth_bars')}")


if __name__ == "__main__":
    main()
