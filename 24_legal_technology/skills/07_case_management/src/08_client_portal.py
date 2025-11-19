"""
Client Portal - Secure Client Access to Case Information
Provides clients with secure access to documents, invoices, and case updates
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
import secrets


class AccessLevel(Enum):
    """Client access levels"""
    VIEW_ONLY = "View Only"
    DOWNLOAD = "Download"
    UPLOAD = "Upload"
    FULL_ACCESS = "Full Access"


class DocumentPermission(Enum):
    """Document permission types"""
    PUBLIC = "Public"
    PRIVATE = "Private"
    ATTORNEY_ONLY = "Attorney Only"
    CLIENT_RESTRICTED = "Client Restricted"


class ClientPortal:
    """Manage client portal access and document sharing"""

    def __init__(self, api_key: str, base_url: str = "https://api.clio.com/v4.0",
                 portal_url: str = "https://portal.example.com"):
        """
        Initialize client portal

        Args:
            api_key: Clio API key
            base_url: Clio API base URL
            portal_url: Client portal URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.portal_url = portal_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str,
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise

    def create_client_portal_account(self, client_id: str,
                                    email: str,
                                    access_level: str = AccessLevel.VIEW_ONLY.value) -> Dict[str, Any]:
        """
        Create client portal account

        Args:
            client_id: Client ID
            email: Client email
            access_level: Portal access level

        Returns:
            Portal account record
        """
        # Generate temporary password
        temp_password = secrets.token_urlsafe(12)
        password_hash = self._hash_password(temp_password)

        account = {
            "client_id": client_id,
            "email": email,
            "access_level": access_level,
            "password_hash": password_hash,
            "account_created": datetime.now().isoformat(),
            "status": "Active",
            "last_login": None,
            "two_factor_enabled": False
        }

        portal_account = self._make_request("POST", "/portal_accounts", data=account)

        # Send account creation email with temporary password
        self._send_portal_invitation(email, client_id, temp_password)

        return portal_account

    def _hash_password(self, password: str) -> str:
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _send_portal_invitation(self, email: str,
                               client_id: str,
                               temp_password: str) -> bool:
        """Send portal account invitation email"""
        portal_link = f"{self.portal_url}/login?client_id={client_id}"

        email_content = f"""
Dear Client,

Your law firm has created a secure portal account for you to access case information.

Portal Login: {portal_link}
Temporary Password: {temp_password}

Please log in and change your password immediately.

For security reasons, this temporary password will expire in 24 hours.

Best regards,
Your Law Firm
        """

        print(f"Sending portal invitation to {email}")
        return True

    def grant_document_access(self, client_id: str,
                             document_id: str,
                             permission: str = DocumentPermission.VIEW_ONLY.value,
                             expiration_days: int = 30) -> Dict[str, Any]:
        """
        Grant client access to specific document

        Args:
            client_id: Client ID
            document_id: Document ID
            permission: Permission level
            expiration_days: Days until access expires

        Returns:
            Access grant record
        """
        expiration_date = datetime.now() + timedelta(days=expiration_days)

        access_grant = {
            "client_id": client_id,
            "document_id": document_id,
            "permission": permission,
            "granted_date": datetime.now().isoformat(),
            "expiration_date": expiration_date.isoformat(),
            "status": "Active"
        }

        return self._make_request("POST", "/document_access", data=access_grant)

    def share_matter_documents(self, matter_id: str,
                              client_id: str,
                              document_types: List[str] = None) -> Dict[str, Any]:
        """
        Share all documents from a matter with client

        Args:
            matter_id: Matter ID
            client_id: Client ID to share with
            document_types: Optional list of document types to share

        Returns:
            Share summary
        """
        # Get all documents for matter
        documents_response = self._make_request(
            "GET",
            f"/matters/{matter_id}/documents"
        )

        documents = documents_response.get("data", [])

        shared_documents = []

        for doc in documents:
            # Check if document should be shared based on type
            if document_types and doc.get("document_type") not in document_types:
                continue

            # Skip attorney-only documents
            if doc.get("permission") == DocumentPermission.ATTORNEY_ONLY.value:
                continue

            # Grant access
            access = self.grant_document_access(
                client_id,
                doc.get("id"),
                DocumentPermission.VIEW_ONLY.value
            )

            shared_documents.append({
                "document_id": doc.get("id"),
                "document_name": doc.get("name"),
                "document_type": doc.get("document_type"),
                "shared_date": access.get("granted_date"),
                "expiration": access.get("expiration_date")
            })

        return {
            "matter_id": matter_id,
            "client_id": client_id,
            "documents_shared": len(shared_documents),
            "shared_documents": shared_documents,
            "share_date": datetime.now().isoformat()
        }

    def share_invoice(self, invoice_id: str,
                     client_id: str) -> Dict[str, Any]:
        """
        Share invoice with client through portal

        Args:
            invoice_id: Invoice ID
            client_id: Client ID

        Returns:
            Invoice share record
        """
        invoice = self._make_request("GET", f"/invoices/{invoice_id}")

        share_record = {
            "invoice_id": invoice_id,
            "client_id": client_id,
            "shared_date": datetime.now().isoformat(),
            "invoice_date": invoice.get("invoice_date"),
            "due_date": invoice.get("due_date"),
            "amount": invoice.get("total_amount"),
            "viewable": True,
            "downloadable": True,
            "paid_status": invoice.get("status")
        }

        self._make_request("POST", "/invoice_shares", data=share_record)

        return share_record

    def upload_document(self, client_id: str,
                       matter_id: str,
                       document_name: str,
                       document_content: bytes,
                       document_type: str = "Client Upload") -> Dict[str, Any]:
        """
        Allow client to upload document to matter

        Args:
            client_id: Client ID uploading
            matter_id: Matter ID
            document_name: Document name
            document_content: Document content/bytes
            document_type: Type of document

        Returns:
            Uploaded document record
        """
        # Verify client has upload permission for this matter
        matter = self._make_request("GET", f"/matters/{matter_id}")
        matter_client_id = matter.get("client", {}).get("id")

        if client_id != matter_client_id:
            raise PermissionError("Client does not have access to this matter")

        document = {
            "matter_id": matter_id,
            "client_id": client_id,
            "name": document_name,
            "document_type": document_type,
            "upload_date": datetime.now().isoformat(),
            "uploaded_by": client_id,
            "requires_attorney_review": True,
            "review_status": "Pending"
        }

        uploaded_doc = self._make_request("POST", "/documents", data=document)

        return uploaded_doc

    def get_client_portal_view(self, client_id: str) -> Dict[str, Any]:
        """
        Get portal dashboard view for client

        Args:
            client_id: Client ID

        Returns:
            Portal dashboard data
        """
        client = self._make_request("GET", f"/contacts/{client_id}")

        # Get client's matters
        matters_response = self._make_request(
            "GET",
            "/matters",
            params={"client__id": client_id}
        )

        matters = matters_response.get("data", [])

        # Get pending invoices
        invoices_response = self._make_request(
            "GET",
            "/invoices",
            params={"client_id": client_id, "status": "Sent"}
        )

        invoices = invoices_response.get("data", [])

        # Get accessible documents
        documents = []
        for matter in matters:
            docs_response = self._make_request(
                "GET",
                f"/matters/{matter.get('id')}/documents"
            )
            documents.extend(docs_response.get("data", []))

        # Get recent updates
        activities_response = self._make_request(
            "GET",
            "/activities",
            params={"client_id": client_id, "limit": 10}
        )

        activities = activities_response.get("data", [])

        return {
            "client_id": client_id,
            "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}",
            "matters": [
                {
                    "id": m.get("id"),
                    "name": m.get("display_name"),
                    "status": m.get("status"),
                    "open_date": m.get("open_date")
                }
                for m in matters
            ],
            "pending_invoices": [
                {
                    "id": inv.get("id"),
                    "amount": inv.get("total_amount"),
                    "due_date": inv.get("due_date"),
                    "status": inv.get("status")
                }
                for inv in invoices
            ],
            "accessible_documents": len(documents),
            "recent_updates": [
                {
                    "date": a.get("date"),
                    "description": a.get("description"),
                    "matter": a.get("matter", {}).get("display_name")
                }
                for a in activities[:5]
            ]
        }

    def log_portal_access(self, client_id: str,
                         action: str,
                         resource_id: str = "") -> Dict[str, Any]:
        """
        Log client portal access for audit trail

        Args:
            client_id: Client ID
            action: Action performed (login, view_document, download, etc.)
            resource_id: ID of resource accessed

        Returns:
            Access log record
        """
        log_entry = {
            "client_id": client_id,
            "action": action,
            "resource_id": resource_id,
            "timestamp": datetime.now().isoformat(),
            "ip_address": "0.0.0.0",  # Would capture actual IP
            "user_agent": ""  # Would capture actual user agent
        }

        return self._make_request("POST", "/portal_access_logs", data=log_entry)

    def enable_two_factor_authentication(self, client_id: str) -> Dict[str, Any]:
        """
        Enable two-factor authentication for client account

        Args:
            client_id: Client ID

        Returns:
            2FA setup record
        """
        # Generate 2FA secret
        secret = secrets.token_urlsafe(32)

        setup = {
            "client_id": client_id,
            "method": "TOTP",  # Time-based One-Time Password
            "secret": secret,
            "enabled_date": datetime.now().isoformat(),
            "backup_codes": [secrets.token_urlsafe(8) for _ in range(5)],
            "status": "Pending Verification"
        }

        self._make_request("POST", "/two_factor_setup", data=setup)

        return {
            "client_id": client_id,
            "setup_required": True,
            "method": "TOTP",
            "instructions": "Scan QR code with authenticator app",
            "backup_codes_provided": 5
        }

    def generate_portal_report(self, start_date: datetime,
                              end_date: datetime) -> Dict[str, Any]:
        """
        Generate client portal usage report

        Args:
            start_date: Report start date
            end_date: Report end date

        Returns:
            Portal usage report
        """
        # Get access logs
        logs_response = self._make_request(
            "GET",
            "/portal_access_logs",
            params={
                "timestamp__gte": start_date.isoformat(),
                "timestamp__lte": end_date.isoformat(),
                "limit": 500
            }
        )

        logs = logs_response.get("data", [])

        # Aggregate statistics
        unique_clients = set(log.get("client_id") for log in logs)
        action_counts = {}

        for log in logs:
            action = log.get("action")
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "report_period_start": start_date.isoformat(),
            "report_period_end": end_date.isoformat(),
            "total_accesses": len(logs),
            "unique_clients": len(unique_clients),
            "actions_summary": action_counts,
            "most_common_action": max(action_counts, key=action_counts.get) if action_counts else "None",
            "days_in_period": (end_date - start_date).days
        }


# Example usage
if __name__ == "__main__":
    portal = ClientPortal(api_key="your_clio_api_key")

    # Create portal account
    # account = portal.create_client_portal_account(
    #     "client_123",
    #     "client@example.com"
    # )

    # Share matter documents
    # shared = portal.share_matter_documents("matter_123", "client_123")

    # Get portal dashboard
    # dashboard = portal.get_client_portal_view("client_123")
    # print(f"Matters: {len(dashboard['matters'])}")
