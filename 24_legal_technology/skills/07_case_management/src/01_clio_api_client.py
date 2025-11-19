"""
Clio API Client - Basic API Integration Example
Demonstrates how to authenticate and make API calls to Clio
"""

import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

class ClioAPIClient:
    """Basic Clio API client for practice management integration"""

    def __init__(self, access_token: str, base_url: str = "https://api.clio.com/v4.0"):
        """
        Initialize Clio API client

        Args:
            access_token: OAuth 2.0 access token from Clio
            base_url: Clio API base URL
        """
        self.access_token = access_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _make_request(self, method: str, endpoint: str,
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make API request to Clio

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data

        Returns:
            Response JSON as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise

    # Matter Management
    def get_matters(self, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get list of matters with pagination"""
        params = {"page": page, "limit": limit}
        return self._make_request("GET", "/matters", params=params)

    def get_matter(self, matter_id: str) -> Dict[str, Any]:
        """Get specific matter by ID"""
        return self._make_request("GET", f"/matters/{matter_id}")

    def create_matter(self, matter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new matter"""
        return self._make_request("POST", "/matters", data=matter_data)

    def update_matter(self, matter_id: str, matter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing matter"""
        return self._make_request("PATCH", f"/matters/{matter_id}", data=matter_data)

    # Contact/Client Management
    def get_contacts(self, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get list of contacts with pagination"""
        params = {"page": page, "limit": limit}
        return self._make_request("GET", "/contacts", params=params)

    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get specific contact by ID"""
        return self._make_request("GET", f"/contacts/{contact_id}")

    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new contact"""
        return self._make_request("POST", "/contacts", data=contact_data)

    # Time Tracking
    def get_timekeepers(self) -> Dict[str, Any]:
        """Get list of timekeepers (attorneys/staff)"""
        return self._make_request("GET", "/timekeepers")

    def get_time_entries(self, matter_id: str, page: int = 1) -> Dict[str, Any]:
        """Get time entries for specific matter"""
        params = {"page": page, "limit": 100, "matter__id": matter_id}
        return self._make_request("GET", "/time_entries", params=params)

    def create_time_entry(self, time_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new time entry"""
        return self._make_request("POST", "/time_entries", data=time_data)

    # Invoice and Billing
    def get_invoices(self, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get list of invoices with pagination"""
        params = {"page": page, "limit": limit}
        return self._make_request("GET", "/invoices", params=params)

    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get specific invoice by ID"""
        return self._make_request("GET", f"/invoices/{invoice_id}")

    def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new invoice"""
        return self._make_request("POST", "/invoices", data=invoice_data)

    # Activity and Events
    def get_activities(self, matter_id: str, page: int = 1) -> Dict[str, Any]:
        """Get activities for specific matter"""
        params = {"page": page, "limit": 100, "matter__id": matter_id}
        return self._make_request("GET", "/activities", params=params)

    def create_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new activity (note, task, etc.)"""
        return self._make_request("POST", "/activities", data=activity_data)

    # Documents
    def get_documents(self, matter_id: str, page: int = 1) -> Dict[str, Any]:
        """Get documents for specific matter"""
        params = {"page": page, "limit": 100, "matter__id": matter_id}
        return self._make_request("GET", "/documents", params=params)

    def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new document reference"""
        return self._make_request("POST", "/documents", data=document_data)


# Example usage
if __name__ == "__main__":
    # Initialize client (replace with actual token)
    client = ClioAPIClient(access_token="your_clio_access_token")

    # Get matters
    matters_response = client.get_matters()
    print(f"Total matters: {matters_response.get('count', 0)}")

    # Example: Create a matter
    new_matter_data = {
        "display_name": "Smith v. Johnson",
        "matter_type": {"id": 1},  # Reference to matter type
        "status": "Active",
        "client": {"id": 123}  # Reference to client contact
    }
    # new_matter = client.create_matter(new_matter_data)

    # Example: Create a time entry
    time_entry_data = {
        "date": datetime.now().isoformat(),
        "duration": 1.5,  # 1.5 hours
        "description": "Client consultation",
        "matter": {"id": 456},
        "user": {"id": 789}  # Timekeeper ID
    }
    # time_entry = client.create_time_entry(time_entry_data)
