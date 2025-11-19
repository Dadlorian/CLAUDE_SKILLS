"""
Task Automation - Automated Legal Task Generation and Management
Automatically creates and manages workflow tasks based on case events and deadlines
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TaskStatus(Enum):
    """Task status"""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class TaskCategory(Enum):
    """Task categories"""
    INTAKE = "Intake"
    DISCOVERY = "Discovery"
    MOTIONS = "Motions"
    TRIAL = "Trial"
    SETTLEMENT = "Settlement"
    ADMINISTRATIVE = "Administrative"
    COMPLIANCE = "Compliance"
    BILLING = "Billing"
    FOLLOW_UP = "Follow Up"


class TaskAutomation:
    """Automate task creation and management based on case workflow"""

    def __init__(self, api_key: str, base_url: str = "https://api.clio.com/v4.0"):
        """
        Initialize task automation

        Args:
            api_key: Clio API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.workflows = {}

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

    def create_intake_workflow(self, matter_id: str,
                              attorney_id: str) -> List[Dict[str, Any]]:
        """
        Create automatic intake tasks for new matter

        Args:
            matter_id: Matter ID
            attorney_id: Attorney ID

        Returns:
            List of created tasks
        """
        tasks = [
            {
                "title": "Conflict Check - New Matter",
                "description": "Run comprehensive conflict of interest check",
                "category": TaskCategory.INTAKE.value,
                "priority": TaskPriority.CRITICAL.value,
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Prepare Engagement Letter",
                "description": "Draft and prepare retainer agreement/engagement letter",
                "category": TaskCategory.INTAKE.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "dependent_on": "Conflict Check - New Matter"
            },
            {
                "title": "Gather Client Documents",
                "description": "Request initial documents from client",
                "category": TaskCategory.INTAKE.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Initial Case Assessment",
                "description": "Review documents and prepare initial strategy memo",
                "category": TaskCategory.INTAKE.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "dependent_on": "Gather Client Documents"
            }
        ]

        created_tasks = []
        for task in tasks:
            created = self._make_request("POST", "/tasks", data=task)
            created_tasks.append(created)

        return created_tasks

    def create_discovery_workflow(self, matter_id: str,
                                 attorney_id: str,
                                 discovery_deadline: datetime) -> List[Dict[str, Any]]:
        """
        Create discovery phase tasks

        Args:
            matter_id: Matter ID
            attorney_id: Attorney ID
            discovery_deadline: Discovery cutoff date

        Returns:
            List of created tasks
        """
        days_until_deadline = (discovery_deadline - datetime.now()).days

        tasks = [
            {
                "title": "Review Discovery Requests",
                "description": "Review opponent's discovery requests (interrogatories, requests for production)",
                "category": TaskCategory.DISCOVERY.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Prepare Discovery Responses",
                "description": "Draft responses to discovery requests",
                "category": TaskCategory.DISCOVERY.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=10)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "dependent_on": "Review Discovery Requests"
            },
            {
                "title": "Prepare Own Discovery Requests",
                "description": "Draft interrogatories and requests for production",
                "category": TaskCategory.DISCOVERY.value,
                "priority": TaskPriority.MEDIUM.value,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Submit Discovery Responses",
                "description": "File discovery responses with court",
                "category": TaskCategory.DISCOVERY.value,
                "priority": TaskPriority.CRITICAL.value,
                "due_date": (discovery_deadline - timedelta(days=1)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "dependent_on": "Prepare Discovery Responses"
            },
            {
                "title": "Follow Up on Outstanding Discovery",
                "description": "Track and follow up on incomplete discovery responses",
                "category": TaskCategory.DISCOVERY.value,
                "priority": TaskPriority.MEDIUM.value,
                "due_date": (discovery_deadline + timedelta(days=5)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            }
        ]

        created_tasks = []
        for task in tasks:
            created = self._make_request("POST", "/tasks", data=task)
            created_tasks.append(created)

        return created_tasks

    def create_motion_workflow(self, matter_id: str,
                              attorney_id: str,
                              motion_deadline: datetime) -> List[Dict[str, Any]]:
        """
        Create motion practice tasks

        Args:
            matter_id: Matter ID
            attorney_id: Attorney ID
            motion_deadline: Motion filing deadline

        Returns:
            List of created tasks
        """
        tasks = [
            {
                "title": "Research Motion Issues",
                "description": "Research case law and statute for motion preparation",
                "category": TaskCategory.MOTIONS.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Draft Motion Memorandum",
                "description": "Prepare detailed memorandum in support of motion",
                "category": TaskCategory.MOTIONS.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (motion_deadline - timedelta(days=3)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "dependent_on": "Research Motion Issues"
            },
            {
                "title": "Prepare Declarations/Affidavits",
                "description": "Prepare declarations or affidavits in support of motion",
                "category": TaskCategory.MOTIONS.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (motion_deadline - timedelta(days=3)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "File Motion",
                "description": "File motion with court and serve on opposing counsel",
                "category": TaskCategory.MOTIONS.value,
                "priority": TaskPriority.CRITICAL.value,
                "due_date": motion_deadline.isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "dependent_on": "Draft Motion Memorandum"
            },
            {
                "title": "Monitor Motion Response",
                "description": "Track filing of opposing party's response",
                "category": TaskCategory.MOTIONS.value,
                "priority": TaskPriority.MEDIUM.value,
                "due_date": (motion_deadline + timedelta(days=14)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            }
        ]

        created_tasks = []
        for task in tasks:
            created = self._make_request("POST", "/tasks", data=task)
            created_tasks.append(created)

        return created_tasks

    def create_trial_preparation_workflow(self, matter_id: str,
                                         attorney_id: str,
                                         trial_date: datetime) -> List[Dict[str, Any]]:
        """
        Create trial preparation tasks

        Args:
            matter_id: Matter ID
            attorney_id: Attorney ID
            trial_date: Trial date

        Returns:
            List of created tasks
        """
        weeks_until_trial = (trial_date - datetime.now()).days // 7

        tasks = [
            {
                "title": "Finalize Exhibit List",
                "description": "Prepare and finalize list of exhibits for trial",
                "category": TaskCategory.TRIAL.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (trial_date - timedelta(days=14)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Prepare Witness Outlines",
                "description": "Prepare examination outlines for all witnesses",
                "category": TaskCategory.TRIAL.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (trial_date - timedelta(days=7)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Prepare Trial Brief",
                "description": "Prepare trial brief with key issues and legal arguments",
                "category": TaskCategory.TRIAL.value,
                "priority": TaskPriority.CRITICAL.value,
                "due_date": (trial_date - timedelta(days=7)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Pre-Trial Conference Preparation",
                "description": "Prepare for pre-trial conference with judge",
                "category": TaskCategory.TRIAL.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (trial_date - timedelta(days=3)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "dependent_on": "Prepare Trial Brief"
            },
            {
                "title": "Final Trial Preparation",
                "description": "Final review of all trial materials and strategy",
                "category": TaskCategory.TRIAL.value,
                "priority": TaskPriority.CRITICAL.value,
                "due_date": (trial_date - timedelta(days=1)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            }
        ]

        created_tasks = []
        for task in tasks:
            created = self._make_request("POST", "/tasks", data=task)
            created_tasks.append(created)

        return created_tasks

    def create_settlement_workflow(self, matter_id: str,
                                  attorney_id: str) -> List[Dict[str, Any]]:
        """
        Create settlement negotiation tasks

        Args:
            matter_id: Matter ID
            attorney_id: Attorney ID

        Returns:
            List of created tasks
        """
        tasks = [
            {
                "title": "Evaluate Settlement Position",
                "description": "Analyze case strength and settlement range",
                "category": TaskCategory.SETTLEMENT.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Prepare Settlement Demand/Offer",
                "description": "Draft initial settlement demand or response",
                "category": TaskCategory.SETTLEMENT.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "dependent_on": "Evaluate Settlement Position"
            },
            {
                "title": "Negotiate Settlement Terms",
                "description": "Negotiate settlement with opposing party",
                "category": TaskCategory.SETTLEMENT.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value
            },
            {
                "title": "Prepare Settlement Agreement",
                "description": "Draft settlement agreement once terms agreed",
                "category": TaskCategory.SETTLEMENT.value,
                "priority": TaskPriority.HIGH.value,
                "due_date": (datetime.now() + timedelta(days=21)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "dependent_on": "Negotiate Settlement Terms"
            }
        ]

        created_tasks = []
        for task in tasks:
            created = self._make_request("POST", "/tasks", data=task)
            created_tasks.append(created)

        return created_tasks

    def auto_create_deadline_tasks(self, matter_id: str,
                                   deadline_data: Dict[str, Any],
                                   attorney_id: str) -> List[Dict[str, Any]]:
        """
        Automatically create tasks for upcoming deadlines

        Args:
            matter_id: Matter ID
            deadline_data: Deadline information
            attorney_id: Responsible attorney

        Returns:
            List of created tasks
        """
        tasks = []

        for deadline_type, deadline_info in deadline_data.get("calculated_deadlines", {}).items():
            deadline_date = datetime.fromisoformat(deadline_info["deadline_date"])

            # Create task to prepare for deadline
            task = {
                "title": f"Prepare for {deadline_info['type']}",
                "description": f"""
Deadline Type: {deadline_info['type']}
Final Deadline: {deadline_info['deadline_date']}
Days Allowed: {deadline_info['days_allowed']}

Please ensure all necessary work is completed and filed by the deadline.
                """,
                "category": TaskCategory.COMPLIANCE.value,
                "priority": TaskPriority.CRITICAL.value,
                "due_date": (deadline_date - timedelta(days=3)).isoformat(),
                "assigned_to": attorney_id,
                "matter_id": matter_id,
                "status": TaskStatus.OPEN.value,
                "deadline_date": deadline_date.isoformat()
            }

            created = self._make_request("POST", "/tasks", data=task)
            tasks.append(created)

        return tasks

    def get_pending_tasks(self, attorney_id: str,
                         matter_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all pending tasks for attorney

        Args:
            attorney_id: Attorney ID
            matter_id: Optional matter filter

        Returns:
            List of pending tasks
        """
        params = {
            "assigned_to": attorney_id,
            "status": TaskStatus.OPEN.value,
            "limit": 500
        }

        if matter_id:
            params["matter_id"] = matter_id

        response = self._make_request("GET", "/tasks", params=params)
        return response.get("data", [])

    def complete_task(self, task_id: str,
                     completion_notes: str = "") -> Dict[str, Any]:
        """
        Mark task as completed

        Args:
            task_id: Task ID
            completion_notes: Completion notes

        Returns:
            Updated task
        """
        task_data = {
            "status": TaskStatus.COMPLETED.value,
            "completion_date": datetime.now().isoformat(),
            "completion_notes": completion_notes
        }

        return self._make_request("PUT", f"/tasks/{task_id}", data=task_data)

    def generate_workflow_status(self, matter_id: str) -> Dict[str, Any]:
        """
        Generate workflow status for matter

        Args:
            matter_id: Matter ID

        Returns:
            Workflow status summary
        """
        # Get all tasks for matter
        response = self._make_request(
            "GET",
            "/tasks",
            params={"matter_id": matter_id, "limit": 500}
        )

        tasks = response.get("data", [])

        # Categorize by status
        by_status = {}
        by_category = {}
        by_priority = {}

        for task in tasks:
            status = task.get("status", "Unknown")
            category = task.get("category", "Other")
            priority = task.get("priority", "Medium")

            by_status[status] = by_status.get(status, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

        # Get overdue tasks
        now = datetime.now()
        overdue_tasks = [
            t for t in tasks
            if t.get("status") == TaskStatus.OPEN.value and
            datetime.fromisoformat(t.get("due_date", now.isoformat())) < now
        ]

        return {
            "matter_id": matter_id,
            "total_tasks": len(tasks),
            "tasks_by_status": by_status,
            "tasks_by_category": by_category,
            "tasks_by_priority": by_priority,
            "overdue_count": len(overdue_tasks),
            "overdue_tasks": [
                {
                    "id": t.get("id"),
                    "title": t.get("title"),
                    "due_date": t.get("due_date"),
                    "assigned_to": t.get("assigned_to")
                }
                for t in overdue_tasks
            ],
            "status_report_date": now.isoformat()
        }


# Example usage
if __name__ == "__main__":
    automation = TaskAutomation(api_key="your_clio_api_key")

    # Create intake workflow
    # tasks = automation.create_intake_workflow("matter_123", "attorney_456")

    # Create discovery workflow
    # discovery_deadline = datetime.now() + timedelta(days=60)
    # discovery_tasks = automation.create_discovery_workflow(
    #     "matter_123",
    #     "attorney_456",
    #     discovery_deadline
    # )

    # Get workflow status
    # status = automation.generate_workflow_status("matter_123")
    # print(f"Pending tasks: {status['tasks_by_status'].get('Open', 0)}")
