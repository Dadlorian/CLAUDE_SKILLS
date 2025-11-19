#!/usr/bin/env python3
"""
Template Versioning - Document template version management and tracking.

Production-ready module for managing template versions, tracking changes,
enabling rollback, and maintaining version history with change logs.
"""

import logging
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import hashlib
import uuid
from difflib import unified_diff

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class VersionStatus(Enum):
    """Status of a template version."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ChangeType(Enum):
    """Type of change in a template."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"
    RENAMED = "renamed"


@dataclass
class VersionChange:
    """Represents a single change in a version."""
    change_type: ChangeType
    element_name: str
    description: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    line_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['change_type'] = self.change_type.value
        return data


@dataclass
class VersionApproval:
    """Approval record for a version."""
    approval_id: str
    approver: str
    approved_at: datetime
    comments: str = ""
    approval_type: str = "standard"  # standard, legal_review, compliance_review

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['approved_at'] = self.approved_at.isoformat()
        return data


@dataclass
class TemplateVersion:
    """Represents a single version of a template."""
    version_id: str
    template_id: str
    version_number: str
    content: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    status: VersionStatus = VersionStatus.DRAFT
    description: str = ""
    changes: List[VersionChange] = field(default_factory=list)
    approvals: List[VersionApproval] = field(default_factory=list)
    content_hash: str = ""
    parent_version_id: Optional[str] = None
    release_notes: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Calculate content hash."""
        if not self.content_hash:
            self.content_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate hash of content."""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def is_approved(self) -> bool:
        """Check if version is approved."""
        return len(self.approvals) > 0

    def get_approval_chain(self) -> List[VersionApproval]:
        """Get approval chain."""
        return self.approvals

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['status'] = self.status.value
        data['changes'] = [c.to_dict() for c in self.changes]
        data['approvals'] = [a.to_dict() for a in self.approvals]
        return data


class VersionControl:
    """Version control system for templates."""

    def __init__(self):
        """Initialize version control."""
        self.versions: Dict[str, TemplateVersion] = {}
        self.template_history: Dict[str, List[str]] = {}  # template_id -> [version_ids]
        self.active_versions: Dict[str, str] = {}  # template_id -> active_version_id
        logger.info("Initialized template version control system")

    def create_version(
        self,
        template_id: str,
        content: Dict[str, Any],
        version_number: str,
        created_by: str,
        description: str = "",
        parent_version_id: Optional[str] = None
    ) -> TemplateVersion:
        """Create new template version."""
        logger.info(f"Creating version {version_number} for template {template_id}")

        version_id = str(uuid.uuid4())
        version = TemplateVersion(
            version_id=version_id,
            template_id=template_id,
            version_number=version_number,
            content=content,
            created_by=created_by,
            description=description,
            parent_version_id=parent_version_id
        )

        # Calculate changes if parent exists
        if parent_version_id and parent_version_id in self.versions:
            parent = self.versions[parent_version_id]
            changes = self._calculate_changes(parent.content, content)
            version.changes = changes

        self.versions[version_id] = version

        # Track history
        if template_id not in self.template_history:
            self.template_history[template_id] = []
        self.template_history[template_id].append(version_id)

        logger.info(f"Created version: {version_id}")
        return version

    def _calculate_changes(
        self,
        old_content: Dict[str, Any],
        new_content: Dict[str, Any]
    ) -> List[VersionChange]:
        """Calculate changes between versions."""
        changes = []

        # Check for added/modified keys
        for key, new_value in new_content.items():
            if key not in old_content:
                changes.append(VersionChange(
                    change_type=ChangeType.ADDED,
                    element_name=key,
                    description=f"Added field: {key}",
                    new_value=new_value
                ))
            elif old_content[key] != new_value:
                changes.append(VersionChange(
                    change_type=ChangeType.MODIFIED,
                    element_name=key,
                    description=f"Modified field: {key}",
                    old_value=old_content[key],
                    new_value=new_value
                ))

        # Check for deleted keys
        for key in old_content:
            if key not in new_content:
                changes.append(VersionChange(
                    change_type=ChangeType.DELETED,
                    element_name=key,
                    description=f"Deleted field: {key}",
                    old_value=old_content[key]
                ))

        return changes

    def get_version(self, version_id: str) -> Optional[TemplateVersion]:
        """Get version by ID."""
        return self.versions.get(version_id)

    def get_template_versions(self, template_id: str) -> List[TemplateVersion]:
        """Get all versions of a template."""
        version_ids = self.template_history.get(template_id, [])
        return [self.versions[vid] for vid in version_ids if vid in self.versions]

    def get_active_version(self, template_id: str) -> Optional[TemplateVersion]:
        """Get active version of template."""
        active_version_id = self.active_versions.get(template_id)
        return self.versions.get(active_version_id) if active_version_id else None

    def set_active_version(self, template_id: str, version_id: str) -> bool:
        """Set active version for template."""
        if version_id not in self.versions:
            logger.warning(f"Version not found: {version_id}")
            return False

        version = self.versions[version_id]
        if version.status not in [VersionStatus.APPROVED, VersionStatus.ACTIVE]:
            logger.warning(f"Version not approved: {version_id}")
            return False

        self.active_versions[template_id] = version_id
        version.status = VersionStatus.ACTIVE
        logger.info(f"Set active version for template {template_id}: {version_id}")
        return True

    def approve_version(
        self,
        version_id: str,
        approver: str,
        comments: str = ""
    ) -> bool:
        """Approve a version."""
        version = self.versions.get(version_id)
        if not version:
            logger.warning(f"Version not found: {version_id}")
            return False

        approval = VersionApproval(
            approval_id=str(uuid.uuid4()),
            approver=approver,
            approved_at=datetime.now(),
            comments=comments
        )

        version.approvals.append(approval)
        version.status = VersionStatus.APPROVED
        logger.info(f"Approved version: {version_id}")
        return True

    def deprecate_version(self, version_id: str, reason: str = "") -> bool:
        """Mark version as deprecated."""
        version = self.versions.get(version_id)
        if not version:
            return False

        version.status = VersionStatus.DEPRECATED
        version.release_notes = f"Deprecated: {reason}"
        logger.info(f"Deprecated version: {version_id}")
        return True

    def rollback_to_version(self, template_id: str, version_id: str) -> bool:
        """Rollback to previous version."""
        version = self.versions.get(version_id)
        if not version or version.template_id != template_id:
            logger.warning(f"Invalid rollback attempt: {version_id}")
            return False

        return self.set_active_version(template_id, version_id)

    def get_version_diff(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> List[str]:
        """Get diff between two versions."""
        v1 = self.versions.get(version_id_1)
        v2 = self.versions.get(version_id_2)

        if not v1 or not v2:
            return []

        content1 = json.dumps(v1.content, indent=2).split("\n")
        content2 = json.dumps(v2.content, indent=2).split("\n")

        diff = unified_diff(content1, content2, lineterm="")
        return list(diff)

    def get_version_history(self, template_id: str) -> Dict[str, Any]:
        """Get complete version history."""
        versions = self.get_template_versions(template_id)
        active = self.get_active_version(template_id)

        return {
            "template_id": template_id,
            "total_versions": len(versions),
            "active_version_id": active.version_id if active else None,
            "active_version_number": active.version_number if active else None,
            "versions": [v.to_dict() for v in versions]
        }


class VersionComparison:
    """Compares two versions."""

    def __init__(self, version1: TemplateVersion, version2: TemplateVersion):
        """Initialize comparison."""
        self.version1 = version1
        self.version2 = version2

    def get_summary(self) -> Dict[str, Any]:
        """Get comparison summary."""
        return {
            "version1": self.version1.version_number,
            "version2": self.version2.version_number,
            "changes_count": len(self.version2.changes),
            "content_hash_changed": self.version1.content_hash != self.version2.content_hash,
            "approvals_changed": len(self.version1.approvals) != len(self.version2.approvals)
        }

    def get_change_details(self) -> List[Dict[str, Any]]:
        """Get detailed change information."""
        return [c.to_dict() for c in self.version2.changes]


class VersionBranch:
    """Represents a development branch of template versions."""

    def __init__(self, branch_name: str, template_id: str, base_version_id: str):
        """Initialize branch."""
        self.name = branch_name
        self.template_id = template_id
        self.base_version_id = base_version_id
        self.versions: List[str] = []
        self.created_at = datetime.now()
        self.is_merged = False
        logger.info(f"Created branch: {branch_name}")

    def add_version(self, version_id: str) -> None:
        """Add version to branch."""
        self.versions.append(version_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "template_id": self.template_id,
            "base_version_id": self.base_version_id,
            "versions": self.versions,
            "created_at": self.created_at.isoformat(),
            "is_merged": self.is_merged
        }


def create_sample_versions() -> Tuple[VersionControl, str]:
    """Create sample template versions."""
    vc = VersionControl()

    # Create v1.0
    v1_content = {
        "title": "Service Agreement",
        "sections": ["terms", "conditions"],
        "signature_required": True
    }

    v1 = vc.create_version(
        template_id="TMPL-001",
        content=v1_content,
        version_number="1.0",
        created_by="alice@example.com",
        description="Initial template"
    )

    # Create v1.1 (patch)
    v1_1_content = v1_content.copy()
    v1_1_content["updated_date_field"] = True

    v1_1 = vc.create_version(
        template_id="TMPL-001",
        content=v1_1_content,
        version_number="1.1",
        created_by="bob@example.com",
        description="Added date field",
        parent_version_id=v1.version_id
    )

    # Approve versions
    vc.approve_version(v1.version_id, "approver@example.com", "Initial version")
    vc.approve_version(v1_1.version_id, "approver@example.com", "Patch version")

    # Set active
    vc.set_active_version("TMPL-001", v1_1.version_id)

    return vc, "TMPL-001"


if __name__ == "__main__":
    # Create versions
    vc, template_id = create_sample_versions()

    # Get history
    history = vc.get_version_history(template_id)
    print("Version History:")
    print(json.dumps(history, indent=2, default=str))

    # Get active version
    active = vc.get_active_version(template_id)
    print(f"\nActive Version: {active.version_number if active else 'None'}")

    # Get comparison
    versions = vc.get_template_versions(template_id)
    if len(versions) >= 2:
        comparison = VersionComparison(versions[0], versions[1])
        print("\nVersion Comparison:")
        print(json.dumps(comparison.get_summary(), indent=2))
        print("\nChanges:")
        for change in comparison.get_change_details():
            print(f"  - {change['change_type']}: {change['element_name']}")
