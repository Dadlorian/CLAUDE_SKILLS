"""
Relativity API Authentication Example
Demonstrates proper authentication with Relativity REST API
"""

import requests
import json
from typing import Dict, Optional

class RelativityAPIClient:
    """Client for authenticating and communicating with Relativity"""

    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize Relativity API client

        Args:
            base_url: Relativity instance URL (e.g., https://relativity.example.com)
            username: Relativity user account
            password: User password or API token
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def authenticate(self) -> bool:
        """
        Authenticate with Relativity and obtain session token

        Returns:
            bool: True if authentication successful
        """
        auth_url = f"{self.base_url}/Relativity.Rest/api/login"

        payload = {
            "username": self.username,
            "password": self.password,
            "bindingType": 0
        }

        try:
            response = self.session.post(
                auth_url,
                json=payload,
                headers=self.headers,
                verify=True
            )
            response.raise_for_status()

            # Store session for subsequent requests
            self.headers["Authorization"] = f"Bearer {response.cookies}"
            return True

        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            return False

    def get_workspace(self, workspace_id: int) -> Optional[Dict]:
        """
        Retrieve workspace information

        Args:
            workspace_id: Relativity workspace ID

        Returns:
            Workspace data or None if failed
        """
        url = f"{self.base_url}/Relativity.Rest/api/Relativity.Core/workspaces({workspace_id})"

        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get workspace: {e}")
            return None

    def get_documents(self, workspace_id: int, limit: int = 100,
                     offset: int = 0) -> Optional[Dict]:
        """
        Retrieve documents from workspace

        Args:
            workspace_id: Relativity workspace ID
            limit: Maximum documents to return
            offset: Number of documents to skip

        Returns:
            Documents data or None if failed
        """
        url = f"{self.base_url}/Relativity.Rest/api/Relativity.Objects/workspaces({workspace_id})/documents"

        params = {
            "$skip": offset,
            "$top": limit,
            "$select": "ArtifactID,FileName,FileType,CreatedDate,DocumentModifiedDate"
        }

        try:
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve documents: {e}")
            return None

    def create_saved_search(self, workspace_id: int, search_name: str,
                           conditions: Dict) -> Optional[int]:
        """
        Create a saved search in Relativity

        Args:
            workspace_id: Relativity workspace ID
            search_name: Name for the search
            conditions: Search condition criteria

        Returns:
            Search artifact ID or None if failed
        """
        url = f"{self.base_url}/Relativity.Rest/api/Relativity.Objects/workspaces({workspace_id})/searches"

        payload = {
            "Name": search_name,
            "SearchDefinition": conditions,
            "Owner": self.username
        }

        try:
            response = self.session.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json().get("ArtifactID")
        except requests.exceptions.RequestException as e:
            print(f"Failed to create saved search: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = RelativityAPIClient(
        base_url="https://relativity.example.com",
        username="discovery_user",
        password="secure_password"
    )

    # Authenticate
    if client.authenticate():
        print("Authentication successful")

        # Get workspace info
        workspace = client.get_workspace(workspace_id=1000001)
        if workspace:
            print(f"Workspace: {workspace}")

        # Get documents
        docs = client.get_documents(workspace_id=1000001, limit=10)
        if docs:
            print(f"Retrieved {len(docs.get('Results', []))} documents")
