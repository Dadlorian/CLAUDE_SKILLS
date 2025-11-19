"""
Clio Matter Synchronization - Sync matters between Clio and external systems
Demonstrates data transformation and synchronization patterns
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum


class MatterStatus(Enum):
    """Matter status enumeration"""
    ACTIVE = "active"
    PENDING = "pending"
    CLOSED = "closed"
    ON_HOLD = "on_hold"
    WITHDRAWN = "withdrawn"


class MatterType(Enum):
    """Matter type enumeration"""
    LITIGATION = "litigation"
    CORPORATE = "corporate"
    IP = "ip"
    REAL_ESTATE = "real_estate"
    EMPLOYMENT = "employment"


@dataclass
class Contact:
    """Contact/Client representation"""
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    company: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class Matter:
    """Matter representation"""
    id: str
    display_name: str
    matter_type: MatterType
    status: MatterStatus
    client: Contact
    open_date: datetime
    close_date: datetime = None
    description: str = ""
    estimated_hours: float = 0.0
    billing_rate: float = 0.0
    internal_notes: str = ""

    def to_clio_format(self) -> Dict[str, Any]:
        """Convert to Clio API format"""
        return {
            "id": self.id,
            "display_name": self.display_name,
            "matter_type": self.matter_type.value,
            "status": self.status.value,
            "client": {"id": self.client.id},
            "open_date": self.open_date.isoformat(),
            "close_date": self.close_date.isoformat() if self.close_date else None,
            "description": self.description,
            "estimated_hours": self.estimated_hours,
            "custom_field_billing_rate": self.billing_rate,
            "internal_notes": self.internal_notes
        }

    @classmethod
    def from_clio_format(cls, clio_data: Dict[str, Any], client: Contact) -> "Matter":
        """Create Matter from Clio API response"""
        return cls(
            id=clio_data.get("id"),
            display_name=clio_data.get("display_name"),
            matter_type=MatterType(clio_data.get("matter_type")),
            status=MatterStatus(clio_data.get("status")),
            client=client,
            open_date=datetime.fromisoformat(clio_data.get("open_date", "")),
            close_date=datetime.fromisoformat(clio_data.get("close_date")) if clio_data.get("close_date") else None,
            description=clio_data.get("description", ""),
            estimated_hours=clio_data.get("estimated_hours", 0.0),
            billing_rate=clio_data.get("custom_field_billing_rate", 0.0),
            internal_notes=clio_data.get("internal_notes", "")
        )


class MatterSynchronizer:
    """Synchronizes matters between Clio and external systems"""

    def __init__(self, clio_client, local_database):
        """
        Initialize synchronizer

        Args:
            clio_client: Clio API client instance
            local_database: Local database connection
        """
        self.clio_client = clio_client
        self.db = local_database
        self.sync_log = []

    def sync_matters_from_clio(self) -> Dict[str, Any]:
        """
        Sync all matters from Clio to local database

        Returns:
            Sync statistics
        """
        stats = {
            "created": 0,
            "updated": 0,
            "deleted": 0,
            "errors": 0,
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Fetch all matters from Clio
            page = 1
            while True:
                response = self.clio_client.get_matters(page=page)
                matters = response.get("results", [])

                if not matters:
                    break

                for matter_data in matters:
                    try:
                        self._sync_single_matter(matter_data, stats)
                    except Exception as e:
                        self.sync_log.append(f"Error syncing matter {matter_data.get('id')}: {e}")
                        stats["errors"] += 1

                page += 1

        except Exception as e:
            self.sync_log.append(f"Fatal sync error: {e}")
            stats["errors"] += 1

        return stats

    def _sync_single_matter(self, matter_data: Dict[str, Any], stats: Dict) -> None:
        """
        Sync single matter from Clio

        Args:
            matter_data: Matter data from Clio API
            stats: Sync statistics dictionary to update
        """
        # Get client information
        client_id = matter_data.get("client", {}).get("id")
        client_data = self.clio_client.get_contact(client_id) if client_id else None

        if not client_data:
            raise ValueError(f"Client not found for matter {matter_data.get('id')}")

        # Create client object
        client = Contact(
            id=client_data.get("id"),
            first_name=client_data.get("first_name", ""),
            last_name=client_data.get("last_name", ""),
            email=client_data.get("email", ""),
            phone=client_data.get("phone", ""),
            company=client_data.get("company", "")
        )

        # Create matter object
        matter = Matter.from_clio_format(matter_data, client)

        # Check if matter exists locally
        local_matter = self.db.get_matter(matter.id)

        if local_matter:
            # Update existing matter
            self.db.update_matter(matter)
            stats["updated"] += 1
        else:
            # Create new matter
            self.db.create_matter(matter)
            stats["created"] += 1

    def sync_matter_to_clio(self, matter: Matter) -> Dict[str, Any]:
        """
        Sync single matter to Clio

        Args:
            matter: Matter object to sync

        Returns:
            Clio API response
        """
        clio_data = matter.to_clio_format()

        if self.clio_client.get_matter(matter.id):
            # Update existing matter
            return self.clio_client.update_matter(matter.id, clio_data)
        else:
            # Create new matter
            return self.clio_client.create_matter(clio_data)

    def get_sync_log(self) -> List[str]:
        """Get synchronization log entries"""
        return self.sync_log

    def clear_sync_log(self) -> None:
        """Clear synchronization log"""
        self.sync_log = []


class LocalMatterDatabase:
    """Simulated local database for matters"""

    def __init__(self):
        self.matters = {}

    def get_matter(self, matter_id: str) -> Matter:
        """Get matter by ID"""
        return self.matters.get(matter_id)

    def create_matter(self, matter: Matter) -> Matter:
        """Create new matter"""
        self.matters[matter.id] = matter
        return matter

    def update_matter(self, matter: Matter) -> Matter:
        """Update existing matter"""
        self.matters[matter.id] = matter
        return matter

    def delete_matter(self, matter_id: str) -> bool:
        """Delete matter"""
        if matter_id in self.matters:
            del self.matters[matter_id]
            return True
        return False

    def list_matters(self) -> List[Matter]:
        """List all matters"""
        return list(self.matters.values())


# Example usage
if __name__ == "__main__":
    # Initialize (would use actual Clio client and database)
    # clio_client = ClioAPIClient(access_token="token")
    # local_db = LocalMatterDatabase()
    # synchronizer = MatterSynchronizer(clio_client, local_db)

    # Sync matters from Clio
    # stats = synchronizer.sync_matters_from_clio()
    # print(f"Sync completed: {stats}")

    # Example local matter creation
    local_db = LocalMatterDatabase()

    contact = Contact(
        id="c123",
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone="555-1234",
        company="Smith Corp"
    )

    matter = Matter(
        id="m456",
        display_name="Smith v. Johnson",
        matter_type=MatterType.LITIGATION,
        status=MatterStatus.ACTIVE,
        client=contact,
        open_date=datetime.now(),
        estimated_hours=100.0,
        billing_rate=250.0
    )

    local_db.create_matter(matter)
    print(f"Matter created: {matter.display_name}")
    print(f"Clio format: {json.dumps(matter.to_clio_format(), default=str, indent=2)}")
