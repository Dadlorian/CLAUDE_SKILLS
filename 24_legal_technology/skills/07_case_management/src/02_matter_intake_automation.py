"""
Matter Intake Automation - Automated Case Management Workflow
Automates client intake, matter creation, and initial document collection
"""

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class MatterStatus(Enum):
    """Matter status enumeration"""
    PROSPECTIVE = "Prospective"
    ACTIVE = "Active"
    ON_HOLD = "On Hold"
    CLOSED = "Closed"
    ARCHIVED = "Archived"


class PracticePantherIntakeAutomation:
    """Automates matter intake process through PracticePanther API"""

    def __init__(self, api_key: str, base_url: str = "https://api.practicepanther.com/v3"):
        """
        Initialize PracticePanther intake automation

        Args:
            api_key: PracticePanther API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str,
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request to PracticePanther"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
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

    def create_client_from_intake(self, intake_form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create client record from intake form submission

        Args:
            intake_form: Intake form data with client information

        Returns:
            Created client record
        """
        client_data = {
            "first_name": intake_form.get("first_name"),
            "last_name": intake_form.get("last_name"),
            "email": intake_form.get("email"),
            "phone": intake_form.get("phone"),
            "address": intake_form.get("address"),
            "city": intake_form.get("city"),
            "state": intake_form.get("state"),
            "zip_code": intake_form.get("zip_code"),
            "company_name": intake_form.get("company_name"),
            "notes": intake_form.get("background_info"),
            "intake_date": datetime.now().isoformat(),
            "source": intake_form.get("source", "Web Form")
        }

        return self._make_request("POST", "/contacts", data=client_data)

    def create_matter_from_intake(self, client_id: str,
                                 intake_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create matter from intake information

        Args:
            client_id: Client ID from created client record
            intake_data: Matter intake data

        Returns:
            Created matter record
        """
        matter_data = {
            "name": intake_data.get("matter_name"),
            "client_id": client_id,
            "description": intake_data.get("matter_description"),
            "matter_type": intake_data.get("matter_type"),
            "practice_area": intake_data.get("practice_area"),
            "status": MatterStatus.PROSPECTIVE.value,
            "open_date": datetime.now().isoformat(),
            "responsible_attorney": intake_data.get("assigned_attorney_id"),
            "notes": self._generate_intake_summary(intake_data),
            "conflict_check_status": "Pending",
            "custom_fields": {
                "intake_form_completed": True,
                "intake_completed_date": datetime.now().isoformat()
            }
        }

        return self._make_request("POST", "/matters", data=matter_data)

    def _generate_intake_summary(self, intake_data: Dict[str, Any]) -> str:
        """Generate intake summary from form data"""
        summary = f"""
INTAKE SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Matter Description:
{intake_data.get('matter_description', 'N/A')}

Key Facts:
{intake_data.get('key_facts', 'N/A')}

Desired Outcomes:
{intake_data.get('desired_outcomes', 'N/A')}

Budget Expectations:
{intake_data.get('budget', 'N/A')}

Opposing Party:
{intake_data.get('opposing_party', 'N/A')}

Opposing Counsel:
{intake_data.get('opposing_counsel', 'N/A')}
        """
        return summary.strip()

    def upload_intake_documents(self, matter_id: str,
                               documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Upload documents from intake process

        Args:
            matter_id: Matter ID to attach documents to
            documents: List of document data (name, content, type)

        Returns:
            List of uploaded document records
        """
        uploaded_docs = []

        for doc in documents:
            doc_data = {
                "matter_id": matter_id,
                "name": doc.get("name"),
                "document_type": doc.get("type", "Intake Document"),
                "file_size": doc.get("file_size"),
                "upload_date": datetime.now().isoformat(),
                "description": f"Uploaded during intake process: {doc.get('name')}"
            }

            uploaded_doc = self._make_request("POST", "/documents", data=doc_data)
            uploaded_docs.append(uploaded_doc)

        return uploaded_docs

    def schedule_intake_meeting(self, matter_id: str,
                               meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule intake meeting/consultation

        Args:
            matter_id: Matter ID
            meeting_data: Meeting details (date, time, attendees, etc.)

        Returns:
            Created event record
        """
        event_data = {
            "matter_id": matter_id,
            "title": f"Client Intake Meeting - {meeting_data.get('client_name')}",
            "description": "Initial client consultation and matter intake",
            "start_time": meeting_data.get("start_time"),
            "end_time": meeting_data.get("end_time"),
            "attendees": meeting_data.get("attendees", []),
            "location": meeting_data.get("location", "Office"),
            "event_type": "Client Meeting",
            "status": "Scheduled"
        }

        return self._make_request("POST", "/events", data=event_data)

    def set_intake_follow_up_tasks(self, matter_id: str,
                                   attorney_id: str) -> List[Dict[str, Any]]:
        """
        Create automatic follow-up tasks after intake

        Args:
            matter_id: Matter ID
            attorney_id: Responsible attorney ID

        Returns:
            List of created task records
        """
        from datetime import timedelta

        follow_up_tasks = [
            {
                "title": "Confirm conflict check results",
                "description": "Verify no conflicts of interest exist",
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "priority": "High",
                "assigned_to": attorney_id
            },
            {
                "title": "Prepare retainer agreement",
                "description": "Draft and prepare engagement letter/retainer agreement",
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "priority": "High",
                "assigned_to": attorney_id
            },
            {
                "title": "Collect additional documents",
                "description": "Request any additional information from client",
                "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "priority": "Medium",
                "assigned_to": attorney_id
            },
            {
                "title": "Analyze case and develop strategy",
                "description": "Review all intake materials and develop initial strategy",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "priority": "Medium",
                "assigned_to": attorney_id
            }
        ]

        created_tasks = []
        for task in follow_up_tasks:
            task["matter_id"] = matter_id
            created_task = self._make_request("POST", "/tasks", data=task)
            created_tasks.append(created_task)

        return created_tasks

    def send_intake_confirmation_email(self, client_email: str,
                                      matter_details: Dict[str, Any]) -> bool:
        """
        Send intake confirmation email to client

        Args:
            client_email: Client email address
            matter_details: Matter details for email content

        Returns:
            Success status
        """
        email_content = f"""
Dear Client,

Thank you for completing our intake form. We have received and are reviewing your information.

Matter Details:
- Matter: {matter_details.get('matter_name')}
- Practice Area: {matter_details.get('practice_area')}
- Assigned Attorney: {matter_details.get('attorney_name')}

Next Steps:
1. We will conduct a conflict of interest check (1-2 business days)
2. Once confirmed, we will send you our engagement agreement
3. Your attorney will schedule an initial consultation meeting

If you have any questions, please don't hesitate to contact us.

Best regards,
{matter_details.get('firm_name', 'Legal Team')}
        """

        # Email integration would be implemented here
        print(f"Sending confirmation email to {client_email}")
        return True


# Example usage
if __name__ == "__main__":
    automation = PracticePantherIntakeAutomation(api_key="your_api_key")

    # Sample intake form
    intake_form = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105",
        "background_info": "Seeking legal advice on business contract",
        "source": "Website"
    }

    # Create client
    # client = automation.create_client_from_intake(intake_form)
    # print(f"Client created: {client.get('id')}")

    # Create matter
    intake_data = {
        "matter_name": "Doe v. ABC Corp",
        "matter_description": "Contract dispute resolution",
        "matter_type": "Contract",
        "practice_area": "Business Law",
        "assigned_attorney_id": "attorney_123",
        "key_facts": "Breach of contract regarding service agreement",
        "desired_outcomes": "Damages recovery",
        "opposing_party": "ABC Corporation"
    }
    # matter = automation.create_matter_from_intake(client.get('id'), intake_data)
    # print(f"Matter created: {matter.get('id')}")
