# eDiscovery Workflow Pattern (EDRM)

## Overview

The eDiscovery Workflow Pattern implements the Electronic Discovery Reference Model (EDRM) framework for managing complex litigation and regulatory investigation workflows. This pattern provides a structured approach to identifying, preserving, processing, analyzing, and producing electronically stored information (ESI) while maintaining compliance with legal standards and reducing costs.

**EDRM Lifecycle Stages:**
1. Information Governance
2. Identification
3. Preservation
4. Collection
5. Processing
6. Review
7. Analysis
8. Production
9. Presentation

**Expected Outcomes:**
- 50-70% reduction in eDiscovery costs
- 95%+ compliance with discovery rules
- Reduced time to produce responsive documents
- Enhanced privilege protection and waiver prevention

## Architecture Components

### 1. Information Governance and Hold Management

```python
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import json

class CustodianRole(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    WITNESS = "witness"
    EXTERNAL = "external"

class HoldStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    RELEASED = "released"
    MODIFIED = "modified"

@dataclass
class LegalHold:
    hold_id: str
    matter_id: str
    matter_name: str
    hold_creation_date: datetime
    hold_release_date: Optional[datetime]
    status: HoldStatus
    custody_period_start: datetime
    custody_period_end: Optional[datetime]
    custodians: List[str]
    data_sources: List[str]
    hold_notice: str
    keywords: List[str]

@dataclass
class Custodian:
    custodian_id: str
    name: str
    email: str
    department: str
    role: CustodianRole
    data_sources: List[str] = field(default_factory=list)
    certification_status: str = "pending"
    certification_date: Optional[datetime] = None

class HoldManagementSystem:
    def __init__(self, storage_backend: str = "postgresql"):
        self.holds: Dict[str, LegalHold] = {}
        self.custodians: Dict[str, Custodian] = {}
        self.hold_audit_log: List[Dict] = []

    def create_legal_hold(self, hold: LegalHold) -> str:
        """Create a new legal hold"""
        self.holds[hold.hold_id] = hold

        self._log_audit_event({
            "event_type": "hold_created",
            "hold_id": hold.hold_id,
            "matter_id": hold.matter_id,
            "custodians": hold.custodians,
            "timestamp": datetime.now().isoformat()
        })

        return hold.hold_id

    def add_custodian(self, custodian: Custodian):
        """Add custodian to system"""
        self.custodians[custodian.custodian_id] = custodian

        self._log_audit_event({
            "event_type": "custodian_added",
            "custodian_id": custodian.custodian_id,
            "name": custodian.name,
            "timestamp": datetime.now().isoformat()
        })

    def issue_hold_notice(self, hold_id: str, custodian_ids: List[str]) -> Dict[str, Any]:
        """Issue hold notice to custodians"""
        hold = self.holds.get(hold_id)
        if not hold:
            raise ValueError(f"Hold {hold_id} not found")

        notifications = []
        for custodian_id in custodian_ids:
            custodian = self.custodians.get(custodian_id)
            if custodian:
                notification = {
                    "custodian_id": custodian_id,
                    "custodian_name": custodian.name,
                    "email": custodian.email,
                    "hold_notice": hold.hold_notice,
                    "issued_date": datetime.now().isoformat(),
                    "status": "issued"
                }
                notifications.append(notification)

                self._log_audit_event({
                    "event_type": "hold_notice_issued",
                    "hold_id": hold_id,
                    "custodian_id": custodian_id,
                    "timestamp": datetime.now().isoformat()
                })

        hold.status = HoldStatus.ACTIVE
        return {"notifications": notifications, "total_issued": len(notifications)}

    def release_hold(self, hold_id: str, reason: str):
        """Release a legal hold"""
        hold = self.holds.get(hold_id)
        if not hold:
            raise ValueError(f"Hold {hold_id} not found")

        hold.status = HoldStatus.RELEASED
        hold.hold_release_date = datetime.now()

        self._log_audit_event({
            "event_type": "hold_released",
            "hold_id": hold_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })

    def certify_custodian_hold(self, custodian_id: str, hold_id: str) -> bool:
        """Record custodian certification of hold compliance"""
        custodian = self.custodians.get(custodian_id)
        if not custodian:
            raise ValueError(f"Custodian {custodian_id} not found")

        custodian.certification_status = "certified"
        custodian.certification_date = datetime.now()

        self._log_audit_event({
            "event_type": "custodian_certified",
            "custodian_id": custodian_id,
            "hold_id": hold_id,
            "timestamp": datetime.now().isoformat()
        })

        return True

    def _log_audit_event(self, event: Dict[str, Any]):
        """Log audit event for compliance"""
        self.hold_audit_log.append(event)

    def get_hold_audit_trail(self, hold_id: str) -> List[Dict[str, Any]]:
        """Retrieve audit trail for a hold"""
        return [log for log in self.hold_audit_log if log.get("hold_id") == hold_id]
```

### 2. Data Source Identification and Collection

```python
from enum import Enum

class DataSourceType(Enum):
    EMAIL = "email"
    FILE_SHARES = "file_shares"
    CLOUD_STORAGE = "cloud_storage"
    DATABASES = "databases"
    MESSAGING = "messaging"
    MOBILE = "mobile"
    BACKUP_SYSTEMS = "backup_systems"
    STRUCTURED_DATA = "structured_data"

@dataclass
class DataSource:
    source_id: str
    source_type: DataSourceType
    custodian_id: Optional[str]
    location: str  # Path, URL, etc.
    estimated_volume_gb: float
    collection_status: str = "identified"
    collection_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataSourceCollector:
    def __init__(self):
        self.data_sources: Dict[str, DataSource] = {}
        self.collection_history: List[Dict] = []

    def identify_data_sources(self, custodian: Custodian) -> List[DataSource]:
        """Identify all relevant data sources for a custodian"""
        sources = []

        # Email systems
        email_source = DataSource(
            source_id=f"{custodian.custodian_id}_email",
            source_type=DataSourceType.EMAIL,
            custodian_id=custodian.custodian_id,
            location=f"Exchange://{custodian.email}",
            estimated_volume_gb=0.0,  # To be calculated
            metadata={
                "provider": "Microsoft Exchange",
                "account_type": "corporate"
            }
        )
        sources.append(email_source)

        # File shares
        shares_source = DataSource(
            source_id=f"{custodian.custodian_id}_shares",
            source_type=DataSourceType.FILE_SHARES,
            custodian_id=custodian.custodian_id,
            location=f"\\\\network\\{custodian.department}\\{custodian.name}",
            estimated_volume_gb=0.0,
            metadata={
                "share_type": "departmental",
                "access_level": "high"
            }
        )
        sources.append(shares_source)

        return sources

    def collect_from_source(self, source: DataSource) -> Dict[str, Any]:
        """Collect data from identified source"""
        collection_result = {
            "source_id": source.source_id,
            "source_type": source.source_type.value,
            "start_time": datetime.now().isoformat(),
            "items_collected": 0,
            "total_size_gb": 0.0,
            "status": "collecting"
        }

        # Implementation varies by source type
        if source.source_type == DataSourceType.EMAIL:
            collection_result = self._collect_email(source)
        elif source.source_type == DataSourceType.FILE_SHARES:
            collection_result = self._collect_file_shares(source)

        source.collection_status = "collected"
        source.collection_date = datetime.now()

        self.collection_history.append({
            "source_id": source.source_id,
            "collection_result": collection_result,
            "timestamp": datetime.now().isoformat()
        })

        return collection_result

    def _collect_email(self, source: DataSource) -> Dict[str, Any]:
        """Collect from email system"""
        return {
            "source_id": source.source_id,
            "source_type": "email",
            "items_collected": 15000,  # Placeholder
            "total_size_gb": 25.5,
            "folders_collected": ["Inbox", "Sent", "Deleted Items"],
            "date_range": "2020-2024",
            "status": "completed"
        }

    def _collect_file_shares(self, source: DataSource) -> Dict[str, Any]:
        """Collect from file shares"""
        return {
            "source_id": source.source_id,
            "source_type": "file_shares",
            "items_collected": 5000,
            "total_size_gb": 45.0,
            "directories_collected": 12,
            "status": "completed"
        }
```

### 3. Processing and Deduplication

```python
from hashlib import md5, sha256
import mimetypes

@dataclass
class ProcessedItem:
    item_id: str
    original_filename: str
    file_hash_md5: str
    file_hash_sha256: str
    file_type: str
    file_size: int
    collection_date: datetime
    source_id: str
    custodian_id: str
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    processing_metadata: Dict[str, Any] = field(default_factory=dict)

class ProcessingEngine:
    def __init__(self, dedup_threshold: float = 0.99):
        self.dedup_threshold = dedup_threshold
        self.hash_index: Dict[str, str] = {}  # MD5 -> item_id
        self.processed_items: Dict[str, ProcessedItem] = {}
        self.duplicate_sets: List[List[str]] = []

    def process_item(self, file_path: str, source_id: str, custodian_id: str) -> ProcessedItem:
        """Process a collected item"""
        import os

        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_type = mimetypes.guess_type(file_path)[0] or "unknown"

        # Calculate hashes
        md5_hash = self._calculate_hash(file_path, 'md5')
        sha256_hash = self._calculate_hash(file_path, 'sha256')

        item_id = md5_hash[:16]

        # Check for duplicates
        is_duplicate = md5_hash in self.hash_index
        duplicate_of = self.hash_index.get(md5_hash)

        if not is_duplicate:
            self.hash_index[md5_hash] = item_id

        processed_item = ProcessedItem(
            item_id=item_id,
            original_filename=filename,
            file_hash_md5=md5_hash,
            file_hash_sha256=sha256_hash,
            file_type=file_type,
            file_size=file_size,
            collection_date=datetime.now(),
            source_id=source_id,
            custodian_id=custodian_id,
            is_duplicate=is_duplicate,
            duplicate_of=duplicate_of,
            processing_metadata={
                "extraction_status": "pending",
                "ocr_status": "pending",
                "metadata_extracted": False
            }
        )

        self.processed_items[item_id] = processed_item
        return processed_item

    def _calculate_hash(self, file_path: str, algorithm: str) -> str:
        """Calculate file hash"""
        if algorithm == 'md5':
            hasher = md5()
        elif algorithm == 'sha256':
            hasher = sha256()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)

        return hasher.hexdigest()

    def get_deduplication_report(self) -> Dict[str, Any]:
        """Generate deduplication statistics"""
        total_items = len(self.processed_items)
        duplicate_items = sum(1 for item in self.processed_items.values() if item.is_duplicate)
        unique_items = total_items - duplicate_items

        total_size = sum(item.file_size for item in self.processed_items.values())
        dedup_size = sum(
            item.file_size for item in self.processed_items.values()
            if item.is_duplicate
        )

        return {
            "total_items": total_items,
            "unique_items": unique_items,
            "duplicate_items": duplicate_items,
            "deduplication_ratio": (duplicate_items / total_items * 100) if total_items > 0 else 0,
            "total_size_gb": total_size / (1024**3),
            "deduplicated_size_gb": dedup_size / (1024**3),
            "storage_savings_percent": (dedup_size / total_size * 100) if total_size > 0 else 0
        }
```

### 4. Review Workflow Management

```python
from enum import Enum

class ReviewStatus(Enum):
    UNREVIEWED = "unreviewed"
    IN_REVIEW = "in_review"
    PRIVILEGED = "privileged"
    RESPONSIVE = "responsive"
    NOT_RESPONSIVE = "not_responsive"
    OBJECTIONABLE = "objectionable"

class PrivilegeType(Enum):
    ATTORNEY_CLIENT = "attorney_client"
    WORK_PRODUCT = "work_product"
    NONE = "none"

@dataclass
class DocumentReview:
    item_id: str
    reviewer_id: str
    review_date: datetime
    review_status: ReviewStatus
    privilege_assertion: PrivilegeType
    responsiveness: bool
    bates_number: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    comments: str = ""
    family_members: List[str] = field(default_factory=list)

class ReviewWorkflowManager:
    def __init__(self):
        self.reviews: Dict[str, DocumentReview] = {}
        self.review_queue: List[str] = []
        self.reviewer_assignments: Dict[str, List[str]] = {}
        self.quality_control_samples: List[str] = []

    def assign_for_review(self, item_ids: List[str], reviewer_id: str):
        """Assign items to reviewer"""
        if reviewer_id not in self.reviewer_assignments:
            self.reviewer_assignments[reviewer_id] = []

        self.reviewer_assignments[reviewer_id].extend(item_ids)
        self.review_queue.extend(item_ids)

    def submit_review(self, review: DocumentReview):
        """Submit document review"""
        self.reviews[review.item_id] = review

    def assign_quality_control_sample(self, sample_size: int = 0.05):
        """Assign QC sample for quality validation"""
        import random

        total_reviewed = len(self.reviews)
        sample_size_count = int(total_reviewed * sample_size)

        self.quality_control_samples = random.sample(
            list(self.reviews.keys()),
            min(sample_size_count, total_reviewed)
        )

        return self.quality_control_samples

    def calculate_work_metrics(self, reviewer_id: str) -> Dict[str, Any]:
        """Calculate reviewer metrics"""
        reviewer_items = self.reviewer_assignments.get(reviewer_id, [])
        reviewer_reviews = [
            r for r in self.reviews.values()
            if r.reviewer_id == reviewer_id
        ]

        total_items = len(reviewer_items)
        reviewed_items = len(reviewer_reviews)
        responsive_items = sum(
            1 for r in reviewer_reviews
            if r.responsiveness is True
        )

        return {
            "reviewer_id": reviewer_id,
            "total_assigned": total_items,
            "total_reviewed": reviewed_items,
            "review_completion_percent": (reviewed_items / total_items * 100) if total_items > 0 else 0,
            "responsive_count": responsive_items,
            "responsive_percent": (responsive_items / reviewed_items * 100) if reviewed_items > 0 else 0,
            "avg_items_per_hour": reviewed_items / 8 if reviewed_items > 0 else 0  # Assuming 8-hour day
        }

    def generate_production_set(self, include_privileged: bool = False) -> Dict[str, Any]:
        """Generate set of documents for production"""
        production_items = []

        for item_id, review in self.reviews.items():
            if review.review_status == ReviewStatus.RESPONSIVE:
                if include_privileged or review.privilege_assertion == PrivilegeType.NONE:
                    production_items.append({
                        "item_id": item_id,
                        "bates_number": review.bates_number,
                        "responsiveness": review.responsiveness
                    })

        return {
            "total_responsive": len([r for r in self.reviews.values() if r.responsiveness]),
            "total_produced": len(production_items),
            "privilege_withheld": len([
                r for r in self.reviews.values()
                if r.privilege_assertion != PrivilegeType.NONE
            ]),
            "production_set": production_items
        }
```

### 5. Analytics and Reporting

```python
from collections import defaultdict

class AnalyticsEngine:
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.timeline_data: List[Dict] = []

    def generate_case_statistics(self, reviews: Dict[str, DocumentReview]) -> Dict[str, Any]:
        """Generate comprehensive case statistics"""
        if not reviews:
            return {}

        responsiveness_counts = defaultdict(int)
        privilege_counts = defaultdict(int)
        by_custodian: Dict[str, int] = defaultdict(int)

        for review in reviews.values():
            responsiveness_counts[str(review.responsiveness)] += 1
            privilege_counts[review.privilege_assertion.value] += 1

        return {
            "total_reviewed": len(reviews),
            "responsive_documents": responsiveness_counts.get("True", 0),
            "non_responsive_documents": responsiveness_counts.get("False", 0),
            "privileged_documents": privilege_counts.get("attorney_client", 0) + privilege_counts.get("work_product", 0),
            "responsiveness_rate": responsiveness_counts.get("True", 0) / len(reviews) * 100 if reviews else 0
        }

    def generate_timeline_report(self, reviews: Dict[str, DocumentReview]) -> List[Dict[str, Any]]:
        """Generate review progress timeline"""
        by_date = defaultdict(int)

        for review in reviews.values():
            date_key = review.review_date.date().isoformat()
            by_date[date_key] += 1

        timeline = []
        cumulative = 0
        for date_str in sorted(by_date.keys()):
            cumulative += by_date[date_str]
            timeline.append({
                "date": date_str,
                "daily_reviews": by_date[date_str],
                "cumulative_reviews": cumulative
            })

        return timeline

    def generate_cost_analysis(self, processed_items_count: int, duplicate_count: int,
                              review_hours: float, hourly_rate: float) -> Dict[str, Any]:
        """Calculate eDiscovery costs"""
        return {
            "total_items": processed_items_count,
            "duplicate_items": duplicate_count,
            "unique_items_reviewed": processed_items_count - duplicate_count,
            "review_labor_hours": review_hours,
            "labor_cost": review_hours * hourly_rate,
            "cost_per_document": (review_hours * hourly_rate) / (processed_items_count - duplicate_count),
            "cost_savings_from_dedup": duplicate_count * ((review_hours * hourly_rate) / processed_items_count)
        }

    def generate_production_report(self, case_id: str, produced_items: List[Dict]) -> Dict[str, Any]:
        """Generate production report"""
        return {
            "case_id": case_id,
            "production_date": datetime.now().isoformat(),
            "total_produced": len(produced_items),
            "bates_ranges": self._generate_bates_ranges(produced_items),
            "file_types_produced": self._count_by_type(produced_items),
            "custodians_represented": len(set(item.get("custodian_id") for item in produced_items))
        }

    def _generate_bates_ranges(self, items: List[Dict]) -> List[str]:
        """Generate Bates number ranges"""
        bates_numbers = sorted([item.get("bates_number") for item in items if item.get("bates_number")])
        ranges = []

        if bates_numbers:
            start = bates_numbers[0]
            prev = bates_numbers[0]

            for current in bates_numbers[1:]:
                if int(current[4:]) != int(prev[4:]) + 1:
                    ranges.append(f"{start}-{prev}")
                    start = current
                prev = current

            ranges.append(f"{start}-{prev}")

        return ranges

    def _count_by_type(self, items: List[Dict]) -> Dict[str, int]:
        """Count items by file type"""
        counts = defaultdict(int)
        for item in items:
            counts[item.get("file_type", "unknown")] += 1
        return dict(counts)
```

## EDRM Implementation Workflow

```python
class EDRMWorkflow:
    def __init__(self):
        self.hold_system = HoldManagementSystem()
        self.collector = DataSourceCollector()
        self.processor = ProcessingEngine()
        self.review_manager = ReviewWorkflowManager()
        self.analytics = AnalyticsEngine()

    def execute_full_workflow(self, matter_id: str, custodians: List[Custodian]) -> Dict[str, Any]:
        """Execute complete EDRM workflow"""

        # Stage 1: Information Governance
        hold = LegalHold(
            hold_id=f"hold_{matter_id}",
            matter_id=matter_id,
            matter_name="Discovery Matter",
            hold_creation_date=datetime.now(),
            hold_release_date=None,
            status=HoldStatus.PENDING,
            custody_period_start=datetime.now() - timedelta(days=1095),
            custody_period_end=datetime.now(),
            custodians=[c.custodian_id for c in custodians],
            data_sources=[],
            hold_notice="Standard preservation notice",
            keywords=["contract", "agreement", "liability"]
        )

        self.hold_system.create_legal_hold(hold)

        for custodian in custodians:
            self.hold_system.add_custodian(custodian)

        self.hold_system.issue_hold_notice(hold.hold_id, [c.custodian_id for c in custodians])

        # Stage 2-3: Identification and Preservation
        all_sources = []
        for custodian in custodians:
            sources = self.collector.identify_data_sources(custodian)
            all_sources.extend(sources)

        # Stage 4: Collection
        collection_results = []
        for source in all_sources:
            result = self.collector.collect_from_source(source)
            collection_results.append(result)

        # Stage 5: Processing
        processed_count = 0
        duplicate_count = 0

        for source in all_sources:
            # Simulated file collection
            for i in range(100):  # Example
                processed_item = self.processor.process_item(
                    f"/path/to/item_{i}.txt",
                    source.source_id,
                    source.custodian_id or ""
                )
                if processed_item.is_duplicate:
                    duplicate_count += 1
                processed_count += 1

        # Stage 6-7: Review and Analysis
        review_items = list(self.processor.processed_items.keys())[:500]  # Subset for review
        self.review_manager.assign_for_review(review_items, "reviewer_001")

        # Simulate reviews
        for item_id in review_items:
            review = DocumentReview(
                item_id=item_id,
                reviewer_id="reviewer_001",
                review_date=datetime.now(),
                review_status=ReviewStatus.RESPONSIVE,
                privilege_assertion=PrivilegeType.NONE,
                responsiveness=True,
                bates_number=f"BATES_{str(1000 + processed_count).zfill(6)}",
                tags=["responsive", "on-topic"],
                comments="Relevant to claims"
            )
            self.review_manager.submit_review(review)
            processed_count += 1

        # Stage 8-9: Production and Presentation
        dedup_report = self.processor.get_deduplication_report()
        production = self.review_manager.generate_production_set(include_privileged=False)
        case_stats = self.analytics.generate_case_statistics(self.review_manager.reviews)

        return {
            "matter_id": matter_id,
            "hold_status": hold.status.value,
            "collection_results": collection_results,
            "deduplication_report": dedup_report,
            "production_summary": production,
            "case_statistics": case_stats
        }
```

## Best Practices

### 1. Preservation Excellence
- Implement automated, continuous preservation monitoring
- Maintain detailed custodian certifications
- Track all preservation holds with audit trails
- Regular compliance audits

### 2. Processing Optimization
- Target 30-50% deduplication rate
- Implement early case assessment (ECA) filtering
- Use technology-assisted review (TAR) for large datasets
- Staged processing approach

### 3. Review Quality
- Implement dual-review for privileged documents
- QC sampling at 5-10% of production set
- Reviewer calibration sessions
- Consistent application of review standards

### 4. Compliance and Reporting
- Maintain comprehensive audit logs at all stages
- Generate weekly progress reports
- Track costs and metrics continuously
- Document all custodian interactions

## Metrics and KPIs

| Metric | Target |
|--------|--------|
| Data Identification Completeness | 98%+ |
| Deduplication Rate | 30-50% |
| Review Completion Time | 15-25 items/hour |
| QC Accuracy Rate | 98%+ |
| Cost per Document | <$2 |
| Privilege Log Completeness | 100% |
| Production Timeliness | On schedule |

## Integration with External Systems

```python
from abc import ABC, abstractmethod

class EDRMConnector(ABC):
    @abstractmethod
    def export_to_review_platform(self, items: List[ProcessedItem]) -> str:
        """Export to review platform"""
        pass

    @abstractmethod
    def export_to_litigation_support(self, production_set: Dict) -> str:
        """Export production set to litigation support"""
        pass

class EDRMLDConnector(EDRMConnector):
    """Connector to RELATIVITY"""
    def export_to_review_platform(self, items: List[ProcessedItem]) -> str:
        # Relativity export implementation
        return "relativity_workspace_id"

    def export_to_litigation_support(self, production_set: Dict) -> str:
        # Production export for Summation/other tools
        return "production_export_id"
```

## Regulatory Compliance

- Federal Rules of Civil Procedure (FRCP)
- Uniform Rules Relating to Discovery (URRED)
- GDPR and international privacy requirements
- Industry-specific regulations (HIPAA, FINRA, etc.)

This pattern ensures comprehensive eDiscovery management while maintaining cost efficiency and regulatory compliance throughout the entire litigation lifecycle.
