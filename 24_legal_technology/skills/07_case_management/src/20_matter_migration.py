"""
Matter Migration - Practice Management Automation

Handles matter transfers between attorneys, practice transfers,
and bulk migration of matter data across systems.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import json


class MigrationStatus(Enum):
    """Status of matter migration"""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    VALIDATION = "validation"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationReason(Enum):
    """Reason for matter migration"""
    ATTORNEY_CHANGE = "attorney_change"
    PRACTICE_TRANSFER = "practice_transfer"
    OFFICE_RELOCATION = "office_relocation"
    SYSTEM_UPGRADE = "system_upgrade"
    CLIENT_REQUEST = "client_request"
    MATTER_CONSOLIDATION = "matter_consolidation"


class MigrationComponent(Enum):
    """Components being migrated"""
    DOCUMENTS = "documents"
    COMMUNICATIONS = "communications"
    BILLING_RECORDS = "billing_records"
    DISCOVERY = "discovery"
    CALENDAR = "calendar"
    CONTACTS = "contacts"
    WORK_PRODUCT = "work_product"
    METADATA = "metadata"


@dataclass
class MigrationComponent:
    """Component migration task"""
    component_type: str
    total_items: int
    migrated_items: int = 0
    status: str = "pending"  # "pending", "in_progress", "completed", "failed"
    errors: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: str = ""


@dataclass
class MatterMigration:
    """Represents a matter migration task"""
    migration_id: str
    matter_id: str
    source_attorney: str
    target_attorney: str
    reason: MigrationReason
    initiated_date: datetime
    scheduled_date: datetime
    status: MigrationStatus = MigrationStatus.INITIATED
    components: Dict[str, MigrationComponent] = field(default_factory=dict)
    total_documents: int = 0
    migrated_documents: int = 0
    validation_errors: List[str] = field(default_factory=list)
    completion_date: Optional[datetime] = None
    notes: str = ""


@dataclass
class BulkMigrationTask:
    """Represents bulk migration of multiple matters"""
    task_id: str
    description: str
    reason: MigrationReason
    matter_count: int
    initiated_date: datetime
    scheduled_date: datetime
    status: MigrationStatus = MigrationStatus.INITIATED
    matters: List[str] = field(default_factory=list)
    completed_matters: List[str] = field(default_factory=list)
    failed_matters: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    estimated_completion_time: Optional[datetime] = None


class MatterMigrationManager:
    """Manages matter migrations and transfers"""

    def __init__(self):
        self.migrations: Dict[str, MatterMigration] = {}
        self.bulk_tasks: Dict[str, BulkMigrationTask] = {}
        self.migration_log: List[Dict] = []

    def initiate_matter_migration(self, matter_migration: MatterMigration) -> str:
        """Initiate a matter migration"""
        self.migrations[matter_migration.migration_id] = matter_migration

        self._log_event(
            matter_migration.migration_id,
            "migration_initiated",
            f"Matter migration initiated from {matter_migration.source_attorney} to {matter_migration.target_attorney}"
        )

        return matter_migration.migration_id

    def add_migration_component(self, migration_id: str, component_type: str, total_items: int) -> bool:
        """Add a component to migrate"""
        if migration_id not in self.migrations:
            return False

        migration = self.migrations[migration_id]
        component = MigrationComponent(
            component_type=component_type,
            total_items=total_items
        )
        migration.components[component_type] = component

        return True

    def start_migration(self, migration_id: str) -> bool:
        """Start a matter migration"""
        if migration_id not in self.migrations:
            return False

        migration = self.migrations[migration_id]
        migration.status = MigrationStatus.IN_PROGRESS

        for component in migration.components.values():
            component.status = "in_progress"
            component.start_time = datetime.now()

        self._log_event(migration_id, "migration_started", "Matter migration started")
        return True

    def update_component_progress(self, migration_id: str, component_type: str,
                                  migrated_items: int, errors: List[str] = None) -> bool:
        """Update progress of a migration component"""
        if migration_id not in self.migrations:
            return False

        migration = self.migrations[migration_id]
        if component_type not in migration.components:
            return False

        component = migration.components[component_type]
        component.migrated_items = migrated_items

        if errors:
            component.errors.extend(errors)
            component.status = "failed" if len(errors) > 0 else "in_progress"

        if migrated_items >= component.total_items:
            component.status = "completed"
            component.end_time = datetime.now()

        migration.migrated_documents = sum(
            c.migrated_items for c in migration.components.values()
        )

        return True

    def validate_migration(self, migration_id: str) -> Tuple[bool, List[str]]:
        """Validate migration completeness and integrity"""
        if migration_id not in self.migrations:
            return False, ["Migration not found"]

        migration = self.migrations[migration_id]
        migration.status = MigrationStatus.VALIDATION
        errors = []

        # Check all components are complete
        for component_type, component in migration.components.items():
            if component.migrated_items < component.total_items:
                errors.append(f"{component_type}: {component.total_items - component.migrated_items} items not migrated")

            if component.errors:
                errors.extend([f"{component_type}: {error}" for error in component.errors])

        if errors:
            migration.validation_errors = errors
            return False, errors

        migration.status = MigrationStatus.REVIEW
        self._log_event(migration_id, "validation_passed", "Migration validation passed")
        return True, []

    def complete_migration(self, migration_id: str) -> bool:
        """Complete a migration"""
        if migration_id not in self.migrations:
            return False

        migration = self.migrations[migration_id]

        # Validate before completion
        is_valid, errors = self.validate_migration(migration_id)
        if not is_valid:
            return False

        migration.status = MigrationStatus.COMPLETED
        migration.completion_date = datetime.now()

        self._log_event(
            migration_id,
            "migration_completed",
            f"Matter migration completed. {migration.migrated_documents} items migrated."
        )

        return True

    def rollback_migration(self, migration_id: str, reason: str = "") -> bool:
        """Rollback a failed migration"""
        if migration_id not in self.migrations:
            return False

        migration = self.migrations[migration_id]
        migration.status = MigrationStatus.ROLLED_BACK
        migration.notes = f"Rolled back: {reason}" if reason else "Rolled back"

        self._log_event(migration_id, "migration_rolled_back", f"Migration rolled back. Reason: {reason}")
        return True

    def create_bulk_migration(self, bulk_task: BulkMigrationTask) -> str:
        """Create a bulk migration task"""
        self.bulk_tasks[bulk_task.task_id] = bulk_task

        self._log_event(
            bulk_task.task_id,
            "bulk_migration_initiated",
            f"Bulk migration initiated: {bulk_task.matter_count} matters"
        )

        return bulk_task.task_id

    def add_matter_to_bulk_migration(self, task_id: str, matter_id: str) -> bool:
        """Add matter to bulk migration task"""
        if task_id not in self.bulk_tasks:
            return False

        task = self.bulk_tasks[task_id]
        if matter_id not in task.matters:
            task.matters.append(matter_id)
            return True

        return False

    def update_bulk_migration_progress(self, task_id: str, completed_matter: str) -> bool:
        """Update progress of bulk migration"""
        if task_id not in self.bulk_tasks:
            return False

        task = self.bulk_tasks[task_id]

        if completed_matter in task.matters and completed_matter not in task.completed_matters:
            task.completed_matters.append(completed_matter)
            task.progress_percentage = (len(task.completed_matters) / len(task.matters)) * 100

            if len(task.completed_matters) == len(task.matters):
                task.status = MigrationStatus.COMPLETED

            return True

        return False

    def mark_bulk_matter_failed(self, task_id: str, matter_id: str) -> bool:
        """Mark a matter as failed in bulk migration"""
        if task_id not in self.bulk_tasks:
            return False

        task = self.bulk_tasks[task_id]

        if matter_id in task.matters and matter_id not in task.failed_matters:
            task.failed_matters.append(matter_id)
            return True

        return False

    def get_migration_status(self, migration_id: str) -> Dict:
        """Get detailed migration status"""
        if migration_id not in self.migrations:
            return {}

        migration = self.migrations[migration_id]

        component_statuses = {}
        for component_type, component in migration.components.items():
            component_statuses[component_type] = {
                "total": component.total_items,
                "migrated": component.migrated_items,
                "progress": (component.migrated_items / component.total_items * 100) if component.total_items > 0 else 0,
                "status": component.status,
                "errors": len(component.errors)
            }

        return {
            "migration_id": migration_id,
            "matter_id": migration.matter_id,
            "status": migration.status.value,
            "reason": migration.reason.value,
            "source_attorney": migration.source_attorney,
            "target_attorney": migration.target_attorney,
            "initiated_date": migration.initiated_date.isoformat(),
            "completion_date": migration.completion_date.isoformat() if migration.completion_date else None,
            "overall_progress": (migration.migrated_documents / migration.total_documents * 100) if migration.total_documents > 0 else 0,
            "components": component_statuses,
            "validation_errors": migration.validation_errors
        }

    def get_bulk_migration_status(self, task_id: str) -> Dict:
        """Get bulk migration task status"""
        if task_id not in self.bulk_tasks:
            return {}

        task = self.bulk_tasks[task_id]

        return {
            "task_id": task_id,
            "description": task.description,
            "status": task.status.value,
            "total_matters": len(task.matters),
            "completed_matters": len(task.completed_matters),
            "failed_matters": len(task.failed_matters),
            "progress_percentage": task.progress_percentage,
            "estimated_completion": task.estimated_completion_time.isoformat() if task.estimated_completion_time else None
        }

    def _log_event(self, entity_id: str, event_type: str, description: str) -> None:
        """Log migration event"""
        self.migration_log.append({
            "timestamp": datetime.now().isoformat(),
            "entity_id": entity_id,
            "event_type": event_type,
            "description": description
        })

    def export_migration_report(self, migration_id: str) -> str:
        """Export migration report as JSON"""
        if migration_id not in self.migrations:
            return ""

        migration = self.migrations[migration_id]
        status = self.get_migration_status(migration_id)

        report = {
            "migration_report": status,
            "events": [
                e for e in self.migration_log
                if e["entity_id"] == migration_id
            ]
        }

        return json.dumps(report, indent=2)

    def get_migration_history(self, limit: int = 50) -> List[Dict]:
        """Get recent migration history"""
        return sorted(
            self.migration_log,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]


from typing import Tuple

# Example usage
if __name__ == "__main__":
    manager = MatterMigrationManager()

    # Create matter migration
    migration = MatterMigration(
        migration_id="MIG-2024-001",
        matter_id="MAT-2024-001",
        source_attorney="ATT-001",
        target_attorney="ATT-002",
        reason=MigrationReason.ATTORNEY_CHANGE,
        initiated_date=datetime.now(),
        scheduled_date=datetime.now(),
        total_documents=150
    )

    manager.initiate_matter_migration(migration)
    manager.add_migration_component("MIG-2024-001", "documents", 150)
    manager.add_migration_component("MIG-2024-001", "communications", 50)

    manager.start_migration("MIG-2024-001")
    manager.update_component_progress("MIG-2024-001", "documents", 150)
    manager.update_component_progress("MIG-2024-001", "communications", 50)

    manager.complete_migration("MIG-2024-001")

    status = manager.get_migration_status("MIG-2024-001")
    print(f"Migration Status: {status}")
