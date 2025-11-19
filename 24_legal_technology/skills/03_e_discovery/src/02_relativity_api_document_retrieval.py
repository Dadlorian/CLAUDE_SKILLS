"""
Relativity API Document Retrieval Example
Demonstrates batch document retrieval and export
"""

import requests
import json
from typing import List, Dict, Iterator
from datetime import datetime

class DocumentRetriever:
    """Retrieves and exports documents from Relativity"""

    def __init__(self, api_client):
        """
        Initialize document retriever

        Args:
            api_client: Authenticated RelativityAPIClient instance
        """
        self.client = api_client

    def search_documents(self, workspace_id: int, search_query: Dict) -> List[Dict]:
        """
        Search documents with advanced criteria

        Args:
            workspace_id: Workspace ID
            search_query: Search criteria dictionary

        Returns:
            List of matching documents
        """
        documents = []
        offset = 0
        batch_size = 1000

        while True:
            docs = self.client.get_documents(
                workspace_id=workspace_id,
                limit=batch_size,
                offset=offset
            )

            if not docs or not docs.get("Results"):
                break

            documents.extend(docs["Results"])
            offset += batch_size

            # Check if we've retrieved all documents
            if len(docs.get("Results", [])) < batch_size:
                break

        return documents

    def export_documents(self, workspace_id: int, artifact_ids: List[int],
                        export_format: str = "pdf") -> Iterator[bytes]:
        """
        Export documents in specified format

        Args:
            workspace_id: Workspace ID
            artifact_ids: List of document artifact IDs
            export_format: Export format (pdf, tiff, native)

        Yields:
            Document content chunks
        """
        url = f"{self.client.base_url}/Relativity.Rest/api/Relativity.Core/workspaces({workspace_id})/documents/export"

        payload = {
            "artifacts": artifact_ids,
            "format": export_format,
            "includePageLevelMetadata": True,
            "imageFormat": "TIFF" if export_format == "tiff" else "PDF"
        }

        try:
            response = self.client.session.post(
                url,
                json=payload,
                headers=self.client.headers,
                stream=True
            )
            response.raise_for_status()

            # Yield content in chunks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        except requests.exceptions.RequestException as e:
            print(f"Export failed: {e}")

    def get_document_metadata(self, workspace_id: int,
                             artifact_id: int) -> Dict:
        """
        Retrieve complete metadata for a document

        Args:
            workspace_id: Workspace ID
            artifact_id: Document artifact ID

        Returns:
            Document metadata dictionary
        """
        url = f"{self.client.base_url}/Relativity.Rest/api/Relativity.Objects/workspaces({workspace_id})/documents({artifact_id})"

        try:
            response = self.client.session.get(url, headers=self.client.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get metadata: {e}")
            return {}

    def batch_update_documents(self, workspace_id: int, updates: List[Dict]) -> bool:
        """
        Batch update document fields

        Args:
            workspace_id: Workspace ID
            updates: List of update dictionaries with artifact ID and field values

        Returns:
            True if successful
        """
        url = f"{self.client.base_url}/Relativity.Rest/api/Relativity.Objects/workspaces({workspace_id})/documents/batch"

        try:
            response = self.client.session.put(
                url,
                json={"updates": updates},
                headers=self.client.headers
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Batch update failed: {e}")
            return False

    def filter_by_custodian(self, workspace_id: int,
                           custodian: str) -> List[Dict]:
        """
        Retrieve documents for specific custodian

        Args:
            workspace_id: Workspace ID
            custodian: Custodian name

        Returns:
            List of custodian's documents
        """
        search_criteria = {
            "FilteredFieldConditions": [
                {
                    "Field": {"Name": "Custodian"},
                    "Condition": "Contains",
                    "Value": custodian
                }
            ]
        }

        return self.search_documents(workspace_id, search_criteria)

    def filter_by_date_range(self, workspace_id: int,
                            start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Retrieve documents within date range

        Args:
            workspace_id: Workspace ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of documents within date range
        """
        search_criteria = {
            "FilteredFieldConditions": [
                {
                    "Field": {"Name": "Created"},
                    "Condition": "IsBetween",
                    "Value": start_date.isoformat(),
                    "Value2": end_date.isoformat()
                }
            ]
        }

        return self.search_documents(workspace_id, search_criteria)


# Example usage
if __name__ == "__main__":
    from relativity_api_authentication import RelativityAPIClient

    # Setup client and retriever
    client = RelativityAPIClient(
        base_url="https://relativity.example.com",
        username="discovery_user",
        password="password"
    )

    if client.authenticate():
        retriever = DocumentRetriever(client)
        workspace_id = 1000001

        # Get documents for specific custodian
        custodian_docs = retriever.filter_by_custodian(workspace_id, "john.doe@company.com")
        print(f"Found {len(custodian_docs)} documents for custodian")

        # Export first 10 as PDF
        if custodian_docs:
            artifact_ids = [doc["ArtifactID"] for doc in custodian_docs[:10]]
            for chunk in retriever.export_documents(workspace_id, artifact_ids):
                print(f"Exported chunk of {len(chunk)} bytes")
