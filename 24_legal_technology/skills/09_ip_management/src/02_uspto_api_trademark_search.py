"""
USPTO API Trademark Search Example
Demonstrates trademark search and retrieval using USPTO API
"""

import requests
from typing import List, Dict, Optional

class USPTOTrademarkSearcher:
    """Search for trademarks using USPTO API"""

    def __init__(self):
        self.base_url = "https://api.uspto.gov/api/v1"
        self.session = requests.Session()

    def search_trademarks(self, query: str, status_filter: Optional[str] = None) -> Dict:
        """
        Search USPTO trademark database

        Args:
            query: Search query
            status_filter: Filter by status (e.g., "REGISTERED", "PENDING")

        Returns:
            Dictionary with search results
        """
        endpoint = f"{self.base_url}/trademark/search"
        params = {
            "q": query,
            "rows": 100
        }

        if status_filter:
            params["q"] += f' AND status:"{status_filter}"'

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_trademark_details(self, serial_number: str) -> Dict:
        """
        Retrieve detailed trademark information

        Args:
            serial_number: Trademark serial number

        Returns:
            Detailed trademark information
        """
        endpoint = f"{self.base_url}/trademark/{serial_number}"
        response = self.session.get(endpoint)
        response.raise_for_status()
        return response.json()

    def search_by_mark(self, mark_text: str) -> List[Dict]:
        """
        Search by trademark text/mark

        Args:
            mark_text: The trademark text

        Returns:
            List of matching trademarks
        """
        query = f'mark_text:("{mark_text}")'
        results = self.search_trademarks(query, "REGISTERED")

        trademarks = []
        for tm in results.get("trademarks", []):
            trademarks.append({
                "serial_number": tm.get("serial_number"),
                "mark": tm.get("mark_text"),
                "owner": tm.get("owner_entity"),
                "status": tm.get("status"),
                "goods_services": tm.get("goods_services")
            })

        return trademarks

    def search_by_owner(self, owner_name: str) -> List[Dict]:
        """
        Search trademarks by owner/company

        Args:
            owner_name: Owner company name

        Returns:
            List of trademarks owned by company
        """
        query = f'owner_entity:("{owner_name}")'
        results = self.search_trademarks(query)

        return results.get("trademarks", [])

    def search_by_class(self, nice_class: int) -> List[Dict]:
        """
        Search trademarks by Nice Classification

        Args:
            nice_class: Nice classification number (1-45)

        Returns:
            List of trademarks in that class
        """
        query = f'nice_class:{nice_class}'
        results = self.search_trademarks(query)

        return results.get("trademarks", [])

    def check_trademark_status(self, serial_number: str) -> str:
        """
        Check current status of a trademark application

        Args:
            serial_number: Trademark serial number

        Returns:
            Status string
        """
        details = self.get_trademark_details(serial_number)
        return details.get("status_description", "Unknown")


# Example usage
if __name__ == "__main__":
    searcher = USPTOTrademarkSearcher()

    # Search for specific trademark
    apple_trademarks = searcher.search_by_mark("Apple")
    print(f"Found {len(apple_trademarks)} trademarks for 'Apple'")

    # Search by owner
    microsoft_marks = searcher.search_by_owner("Microsoft Corporation")
    print(f"Microsoft trademarks: {len(microsoft_marks)}")

    # Search by class (Class 9 is electrical/software)
    class_9_marks = searcher.search_by_class(9)
    print(f"Class 9 trademarks: {len(class_9_marks)}")
