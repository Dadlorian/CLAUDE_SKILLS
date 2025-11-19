"""
USPTO API Patent Search Example
Demonstrates basic patent search using USPTO API endpoints
"""

import requests
import json
from typing import List, Dict, Optional

class USPTOPatentSearcher:
    """Search for patents using USPTO API"""

    def __init__(self):
        self.base_url = "https://api.uspto.gov/api/v1"
        self.session = requests.Session()

    def search_patents(self, query: str, start_index: int = 0) -> Dict:
        """
        Search USPTO patent database

        Args:
            query: Search query (e.g., "machine learning AND classification")
            start_index: Starting position for pagination

        Returns:
            Dictionary with search results
        """
        endpoint = f"{self.base_url}/patent/search"
        params = {
            "q": query,
            "start": start_index,
            "rows": 100
        }

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_patent_details(self, patent_number: str) -> Dict:
        """
        Retrieve detailed information for a specific patent

        Args:
            patent_number: US patent number

        Returns:
            Detailed patent information
        """
        endpoint = f"{self.base_url}/patent/{patent_number}"
        response = self.session.get(endpoint)
        response.raise_for_status()
        return response.json()

    def search_by_classification(self, cpc_code: str, limit: int = 100) -> List[Dict]:
        """
        Search patents by CPC (Cooperative Patent Classification)

        Args:
            cpc_code: CPC classification code
            limit: Maximum number of results

        Returns:
            List of patent results
        """
        query = f"cpc_classification:({cpc_code})"
        results = self.search_patents(query)

        patents = []
        for patent in results.get("patents", []):
            if len(patents) < limit:
                patents.append({
                    "number": patent.get("patent_number"),
                    "title": patent.get("patent_title"),
                    "classification": patent.get("primary_cpc")
                })

        return patents

    def search_by_inventor(self, inventor_name: str) -> List[Dict]:
        """
        Search patents by inventor name

        Args:
            inventor_name: Name of inventor

        Returns:
            List of patents by inventor
        """
        query = f'inventor_first_name:("{inventor_name.split()[0]}") ' \
                f'AND inventor_last_name:("{inventor_name.split()[-1]}")'
        results = self.search_patents(query)

        return results.get("patents", [])

    def search_by_assignee(self, company_name: str) -> List[Dict]:
        """
        Search patents by patent assignee/company

        Args:
            company_name: Assignee company name

        Returns:
            List of patents assigned to company
        """
        query = f'assignee_name:("{company_name}")'
        results = self.search_patents(query)

        return results.get("patents", [])


# Example usage
if __name__ == "__main__":
    searcher = USPTOPatentSearcher()

    # Search for machine learning patents
    results = searcher.search_patents("machine learning AND neural network")
    print(f"Found {len(results.get('patents', []))} results")

    # Search by CPC classification
    ml_patents = searcher.search_by_classification("G06F17/18")
    print(f"ML classification patents: {len(ml_patents)}")

    # Search by assignee
    company_patents = searcher.search_by_assignee("Microsoft Corporation")
    print(f"Microsoft patents: {len(company_patents)}")
