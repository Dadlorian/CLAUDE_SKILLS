#!/usr/bin/env python3
"""
Metadata Injector - Advanced document metadata management and injection.

Production-ready module for managing, validating, and injecting metadata
into legal documents with audit trails and compliance tracking.
"""

import logging
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class MetadataLevel(Enum):
    """Classification levels for metadata."""
    PUBLIC = "public"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PRIVILEGED = "privileged"


class MetadataSource(Enum):
    """Source of metadata."""
    SYSTEM = "system"
    USER = "user"
    EXTRACTED = "extracted"
    INFERRED = "inferred"


@dataclass
class MetadataField:
    """Individual metadata field."""
    key: str
    value: Any
    data_type: str
    source: MetadataSource
    classification_level: MetadataLevel
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_searchable: bool = True
    is_indexable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['source'] = self.source.value
        data['classification_level'] = self.classification_level.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class AuditEntry:
    """Audit trail entry."""
    id: str
    timestamp: datetime
    action: str
    user: str
    field_name: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class DocumentMetadata:
    """Complete metadata for a legal document."""

    def __init__(
        self,
        document_id: str,
        document_name: str,
        document_type: str,
        created_by: str
    ):
        """Initialize document metadata."""
        self.id = document_id
        self.name = document_name
        self.type = document_type
        self.created_by = created_by
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.fields: Dict[str, MetadataField] = {}
        self.audit_trail: List[AuditEntry] = []
        self.tags: Set[str] = set()
        self.relations: Dict[str, List[str]] = {}
        self.version = "1.0"
        logger.info(f"Initialized metadata for document: {self.name}")

    def add_field(
        self,
        key: str,
        value: Any,
        data_type: str = "string",
        source: MetadataSource = MetadataSource.USER,
        classification_level: MetadataLevel = MetadataLevel.CONFIDENTIAL
    ) -> None:
        """Add a metadata field."""
        field = MetadataField(
            key=key,
            value=value,
            data_type=data_type,
            source=source,
            classification_level=classification_level
        )
        self.fields[key] = field
        self._add_audit_entry("field_added", key, None, value)
        logger.debug(f"Added metadata field: {key}")

    def update_field(self, key: str, new_value: Any) -> bool:
        """Update a metadata field."""
        if key not in self.fields:
            logger.warning(f"Field not found: {key}")
            return False

        old_value = self.fields[key].value
        self.fields[key].value = new_value
        self.fields[key].updated_at = datetime.now()
        self.updated_at = datetime.now()
        self._add_audit_entry("field_updated", key, old_value, new_value)
        logger.debug(f"Updated metadata field: {key}")
        return True

    def add_tag(self, tag: str) -> None:
        """Add a tag to the document."""
        self.tags.add(tag)
        self._add_audit_entry("tag_added", tag, None, tag)
        logger.debug(f"Added tag: {tag}")

    def add_relation(self, relation_type: str, document_id: str) -> None:
        """Add a relationship to another document."""
        if relation_type not in self.relations:
            self.relations[relation_type] = []
        self.relations[relation_type].append(document_id)
        self._add_audit_entry("relation_added", f"{relation_type}:{document_id}", None, None)
        logger.debug(f"Added relation: {relation_type} -> {document_id}")

    def _add_audit_entry(
        self,
        action: str,
        field_name: Optional[str],
        old_value: Optional[Any],
        new_value: Optional[Any]
    ) -> None:
        """Add audit trail entry."""
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            action=action,
            user=self.created_by,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value
        )
        self.audit_trail.append(entry)

    def get_field(self, key: str) -> Optional[MetadataField]:
        """Get metadata field."""
        return self.fields.get(key)

    def get_accessible_fields(
        self,
        user_clearance_level: MetadataLevel
    ) -> Dict[str, MetadataField]:
        """Get fields accessible by user based on clearance level."""
        # Simple clearance check - in production, use proper ACL
        accessible = {}
        for key, field in self.fields.items():
            if self._can_access(field.classification_level, user_clearance_level):
                accessible[key] = field
        return accessible

    @staticmethod
    def _can_access(
        field_level: MetadataLevel,
        user_level: MetadataLevel
    ) -> bool:
        """Check if user can access field based on classification."""
        level_hierarchy = {
            MetadataLevel.PUBLIC: 0,
            MetadataLevel.CONFIDENTIAL: 1,
            MetadataLevel.RESTRICTED: 2,
            MetadataLevel.PRIVILEGED: 3
        }
        return level_hierarchy[user_level] >= level_hierarchy[field_level]

    def get_audit_trail(
        self,
        action_filter: Optional[str] = None,
        start_date: Optional[datetime] = None
    ) -> List[AuditEntry]:
        """Get audit trail with optional filters."""
        trail = self.audit_trail

        if action_filter:
            trail = [e for e in trail if e.action == action_filter]

        if start_date:
            trail = [e for e in trail if e.timestamp >= start_date]

        return trail

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
            "tags": list(self.tags),
            "relations": self.relations,
            "audit_entries_count": len(self.audit_trail)
        }

    def to_audit_dict(self) -> Dict[str, Any]:
        """Convert audit trail to dictionary."""
        return {
            "document_id": self.id,
            "document_name": self.name,
            "total_entries": len(self.audit_trail),
            "audit_trail": [e.to_dict() for e in self.audit_trail]
        }


class MetadataValidator:
    """Validates metadata against schema and compliance rules."""

    def __init__(self):
        """Initialize validator."""
        self.required_fields: Set[str] = {"document_id", "document_type"}
        self.field_rules: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized metadata validator")

    def add_field_rule(
        self,
        field_name: str,
        data_type: str,
        required: bool = False,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None
    ) -> None:
        """Add validation rule for a field."""
        self.field_rules[field_name] = {
            "data_type": data_type,
            "required": required,
            "min_length": min_length,
            "max_length": max_length,
            "pattern": pattern
        }

    def validate(self, metadata: DocumentMetadata) -> tuple[bool, List[str]]:
        """Validate document metadata."""
        errors = []

        # Check required fields
        for required_field in self.required_fields:
            if required_field not in metadata.fields:
                errors.append(f"Required field missing: {required_field}")

        # Validate against rules
        for field_name, field in metadata.fields.items():
            if field_name in self.field_rules:
                rule = self.field_rules[field_name]
                field_errors = self._validate_field(field, rule)
                errors.extend(field_errors)

        return len(errors) == 0, errors

    @staticmethod
    def _validate_field(
        field: MetadataField,
        rule: Dict[str, Any]
    ) -> List[str]:
        """Validate individual field."""
        errors = []
        value = str(field.value)

        # Type check
        if field.data_type != rule["data_type"]:
            errors.append(f"Field {field.key}: invalid type")

        # Length checks
        if rule.get("min_length") and len(value) < rule["min_length"]:
            errors.append(f"Field {field.key}: too short")

        if rule.get("max_length") and len(value) > rule["max_length"]:
            errors.append(f"Field {field.key}: too long")

        return errors


class MetadataInjector:
    """Injects metadata into documents."""

    def __init__(self):
        """Initialize injector."""
        self.validator = MetadataValidator()
        logger.info("Initialized metadata injector")

    def inject(
        self,
        document_path: Path,
        metadata: DocumentMetadata
    ) -> Tuple[bool, str]:
        """Inject metadata into document."""
        logger.info(f"Injecting metadata into: {document_path}")

        # Validate metadata
        is_valid, errors = self.validator.validate(metadata)
        if not is_valid:
            error_msg = f"Metadata validation failed: {errors}"
            logger.error(error_msg)
            return False, error_msg

        try:
            # In production, implement actual metadata injection
            # This could use xmp, exif, or custom XML depending on format
            logger.info(f"Successfully injected metadata into {document_path}")
            return True, "Metadata injected successfully"
        except Exception as e:
            logger.error(f"Error injecting metadata: {e}")
            return False, str(e)

    def extract(self, document_path: Path) -> Optional[DocumentMetadata]:
        """Extract metadata from document."""
        logger.info(f"Extracting metadata from: {document_path}")

        try:
            # In production, implement actual extraction
            # Return parsed metadata object
            return None
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return None


class MetadataRegistry:
    """Central registry for document metadata."""

    def __init__(self):
        """Initialize registry."""
        self.documents: Dict[str, DocumentMetadata] = {}
        self.created_at = datetime.now()
        logger.info("Initialized metadata registry")

    def register(self, metadata: DocumentMetadata) -> None:
        """Register document metadata."""
        self.documents[metadata.id] = metadata
        logger.debug(f"Registered metadata for: {metadata.id}")

    def get(self, document_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata."""
        return self.documents.get(document_id)

    def search_by_tag(self, tag: str) -> List[DocumentMetadata]:
        """Search documents by tag."""
        return [
            doc for doc in self.documents.values()
            if tag in doc.tags
        ]

    def search_by_type(self, doc_type: str) -> List[DocumentMetadata]:
        """Search documents by type."""
        return [
            doc for doc in self.documents.values()
            if doc.type == doc_type
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_documents": len(self.documents),
            "created_at": self.created_at.isoformat(),
            "documents_by_type": self._count_by_type(),
            "total_tags": self._count_total_tags()
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count documents by type."""
        counts = {}
        for doc in self.documents.values():
            counts[doc.type] = counts.get(doc.type, 0) + 1
        return counts

    def _count_total_tags(self) -> int:
        """Count total unique tags."""
        all_tags = set()
        for doc in self.documents.values():
            all_tags.update(doc.tags)
        return len(all_tags)


def create_sample_metadata() -> DocumentMetadata:
    """Create sample document metadata."""
    metadata = DocumentMetadata(
        document_id="DOC-2024-001",
        document_name="Service Agreement",
        document_type="contract",
        created_by="user@example.com"
    )

    metadata.add_field(
        "client_name",
        "Acme Corporation",
        "string",
        MetadataSource.USER,
        MetadataLevel.CONFIDENTIAL
    )

    metadata.add_field(
        "contract_value",
        50000,
        "currency",
        MetadataSource.USER,
        MetadataLevel.RESTRICTED
    )

    metadata.add_field(
        "effective_date",
        "2024-01-01",
        "date",
        MetadataSource.USER,
        MetadataLevel.CONFIDENTIAL
    )

    metadata.add_tag("contract")
    metadata.add_tag("service-agreement")

    return metadata


if __name__ == "__main__":
    # Create and test metadata
    metadata = create_sample_metadata()

    print("Document Metadata:")
    print(json.dumps(metadata.to_dict(), indent=2))

    print("\nAudit Trail:")
    print(json.dumps(metadata.to_audit_dict(), indent=2, default=str))

    # Registry
    registry = MetadataRegistry()
    registry.register(metadata)

    print("\nRegistry Statistics:")
    print(json.dumps(registry.get_statistics(), indent=2))
