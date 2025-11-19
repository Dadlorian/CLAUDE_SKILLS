"""
Relativity API Mass Operations Example
Demonstrates bulk field updates and mass tagging
"""

import requests
import json
from typing import List, Dict, Tuple
import time

class MassOperations:
    """Handles bulk operations on documents"""

    def __init__(self, api_client):
        """Initialize mass operations handler"""
        self.client = api_client

    def tag_documents_for_privilege(self, workspace_id: int,
                                   artifact_ids: List[int],
                                   privilege_type: str = "Attorney-Client Privilege") -> bool:
        """
        Tag multiple documents as privileged

        Args:
            workspace_id: Workspace ID
            artifact_ids: List of document artifact IDs
            privilege_type: Type of privilege to assign

        Returns:
            True if successful
        """
        url = f"{self.client.base_url}/Relativity.Rest/api/Relativity.Objects/workspaces({workspace_id})/documents/batch"

        updates = []
        for artifact_id in artifact_ids:
            updates.append({
                "ArtifactID": artifact_id,
                "FieldValues": [
                    {
                        "Field": {"Name": "Privilege"},
                        "Value": privilege_type
                    }
                ]
            })

        try:
            response = self.client.session.post(
                url,
                json={"updates": updates},
                headers=self.client.headers
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Privilege tagging failed: {e}")
            return False

    def set_responsiveness(self, workspace_id: int,
                          artifact_ids: List[int],
                          responsive: bool) -> bool:
        """
        Set responsiveness status for documents

        Args:
            workspace_id: Workspace ID
            artifact_ids: Document IDs to update
            responsive: True for responsive, False for non-responsive

        Returns:
            True if successful
        """
        url = f"{self.client.base_url}/Relativity.Rest/api/Relativity.Objects/workspaces({workspace_id})/documents/batch"

        updates = []
        responsiveness = "Responsive" if responsive else "Non-Responsive"

        for artifact_id in artifact_ids:
            updates.append({
                "ArtifactID": artifact_id,
                "FieldValues": [
                    {
                        "Field": {"Name": "Responsiveness"},
                        "Value": responsiveness
                    }
                ]
            })

        # Process in batches to avoid API limits
        batch_size = 100
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            try:
                response = self.client.session.post(
                    url,
                    json={"updates": batch},
                    headers=self.client.headers
                )
                response.raise_for_status()
                time.sleep(0.5)  # Rate limiting
            except requests.exceptions.RequestException as e:
                print(f"Responsiveness update failed: {e}")
                return False

        return True

    def assign_issue_tags(self, workspace_id: int,
                         artifact_ids: List[int],
                         issues: List[str]) -> bool:
        """
        Assign issue tags to documents

        Args:
            workspace_id: Workspace ID
            artifact_ids: Document IDs to tag
            issues: List of issue names to assign

        Returns:
            True if successful
        """
        url = f"{self.client.base_url}/Relativity.Rest/api/Relativity.Objects/workspaces({workspace_id})/documents/batch"

        updates = []
        for artifact_id in artifact_ids:
            issue_values = [{"Name": issue} for issue in issues]
            updates.append({
                "ArtifactID": artifact_id,
                "FieldValues": [
                    {
                        "Field": {"Name": "Issues"},
                        "Value": issue_values
                    }
                ]
            })

        # Process in batches
        batch_size = 50
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            try:
                response = self.client.session.post(
                    url,
                    json={"updates": batch},
                    headers=self.client.headers
                )
                response.raise_for_status()
                time.sleep(0.5)
            except requests.exceptions.RequestException as e:
                print(f"Issue tagging failed: {e}")
                return False

        return True

    def apply_redactions(self, workspace_id: int,
                        artifact_id: int,
                        redaction_data: List[Dict]) -> bool:
        """
        Apply redactions to document

        Args:
            workspace_id: Workspace ID
            artifact_id: Document to redact
            redaction_data: List of redaction coordinates and reasons

        Returns:
            True if successful
        """
        url = f"{self.client.base_url}/Relativity.Rest/api/Relativity.Core/workspaces({workspace_id})/documents({artifact_id})/redactions"

        payload = {
            "redactions": redaction_data,
            "redactionReason": "Privileged/Confidential",
            "redactionType": "Image"
        }

        try:
            response = self.client.session.post(
                url,
                json=payload,
                headers=self.client.headers
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Redaction application failed: {e}")
            return False

    def create_production_set(self, workspace_id: int,
                            production_name: str,
                            artifact_ids: List[int]) -> Tuple[bool, str]:
        """
        Create production set with specified documents

        Args:
            workspace_id: Workspace ID
            production_name: Name for production
            artifact_ids: Documents to include

        Returns:
            Tuple of (success bool, production ID)
        """
        url = f"{self.client.base_url}/Relativity.Rest/api/Relativity.Objects/workspaces({workspace_id})/productions"

        payload = {
            "Name": production_name,
            "Documents": [{"ArtifactID": aid} for aid in artifact_ids],
            "ProductionType": "Standard"
        }

        try:
            response = self.client.session.post(
                url,
                json=payload,
                headers=self.client.headers
            )
            response.raise_for_status()
            result = response.json()
            return True, result.get("ArtifactID", "")
        except requests.exceptions.RequestException as e:
            print(f"Production creation failed: {e}")
            return False, ""


# Example usage
if __name__ == "__main__":
    from relativity_api_authentication import RelativityAPIClient

    client = RelativityAPIClient(
        base_url="https://relativity.example.com",
        username="discovery_user",
        password="password"
    )

    if client.authenticate():
        ops = MassOperations(client)
        workspace_id = 1000001

        # Example: Tag specific documents as privileged
        doc_ids = [1001, 1002, 1003, 1004, 1005]
        if ops.tag_documents_for_privilege(workspace_id, doc_ids):
            print("Successfully tagged documents as privileged")

        # Example: Set responsiveness
        if ops.set_responsiveness(workspace_id, doc_ids, responsive=False):
            print("Successfully marked documents as non-responsive")

        # Example: Assign issue tags
        issues = ["Contract Dispute", "Damages"]
        if ops.assign_issue_tags(workspace_id, doc_ids, issues):
            print("Successfully assigned issue tags")
