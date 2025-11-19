#!/usr/bin/env python3
"""
Batch Processor - High-performance batch processing of legal documents.

Production-ready module for processing multiple documents with
parallel execution, error handling, and progress tracking.
"""

import logging
import json
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from queue import Queue
import time
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ProcessingStatus(Enum):
    """Status of batch processing."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ItemStatus(Enum):
    """Status of individual item."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ProcessingResult:
    """Result of processing a single item."""
    item_id: str
    status: ItemStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    max_workers: int = 4
    batch_size: int = 100
    timeout_seconds: int = 300
    retry_attempts: int = 3
    continue_on_error: bool = True
    enable_progress_tracking: bool = True
    use_threading: bool = True  # False for ProcessPoolExecutor


class BatchJob:
    """Represents a batch processing job."""

    def __init__(
        self,
        job_id: Optional[str] = None,
        name: str = "Batch Job",
        config: Optional[BatchConfig] = None
    ):
        """Initialize batch job."""
        self.id = job_id or str(uuid.uuid4())
        self.name = name
        self.config = config or BatchConfig()
        self.items: List[Dict[str, Any]] = []
        self.results: List[ProcessingResult] = []
        self.status = ProcessingStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_messages: List[str] = []
        logger.info(f"Created batch job: {self.name} ({self.id})")

    def add_item(self, item_id: str, data: Dict[str, Any]) -> None:
        """Add item to batch."""
        self.items.append({"id": item_id, "data": data})
        logger.debug(f"Added item to batch: {item_id}")

    def add_items(self, items: List[Tuple[str, Dict[str, Any]]]) -> None:
        """Add multiple items to batch."""
        for item_id, data in items:
            self.add_item(item_id, data)
        logger.info(f"Added {len(items)} items to batch")

    def get_progress(self) -> Dict[str, Any]:
        """Get processing progress."""
        total = len(self.items)
        completed = len([r for r in self.results if r.status == ItemStatus.COMPLETED])
        failed = len([r for r in self.results if r.status == ItemStatus.FAILED])
        pending = total - completed - failed

        return {
            "job_id": self.id,
            "total_items": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
            "status": self.status.value
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_items": len(self.items),
            "completed_items": len([r for r in self.results if r.status == ItemStatus.COMPLETED]),
            "failed_items": len([r for r in self.results if r.status == ItemStatus.FAILED]),
            "error_messages": self.error_messages
        }


class BatchProcessor:
    """Processes batches of items with parallel execution."""

    def __init__(self, config: Optional[BatchConfig] = None):
        """Initialize processor."""
        self.config = config or BatchConfig()
        self.jobs: Dict[str, BatchJob] = {}
        logger.info(f"Initialized batch processor with {self.config.max_workers} workers")

    def process(
        self,
        job: BatchJob,
        process_func: Callable[[str, Dict[str, Any]], ProcessingResult]
    ) -> Dict[str, Any]:
        """Process batch job."""
        logger.info(f"Starting batch processing for job: {job.name}")

        job.status = ProcessingStatus.RUNNING
        job.started_at = datetime.now()
        self.jobs[job.id] = job

        executor_class = ThreadPoolExecutor if self.config.use_threading else ProcessPoolExecutor

        with executor_class(max_workers=self.config.max_workers) as executor:
            futures = {}
            processed_count = 0

            # Submit all items
            for item in job.items:
                item_id = item["id"]
                data = item["data"]

                future = executor.submit(
                    self._process_item_with_retry,
                    item_id,
                    data,
                    process_func
                )
                futures[future] = item_id

            # Process results as they complete
            for future in as_completed(futures):
                item_id = futures[future]
                processed_count += 1

                try:
                    result = future.result(timeout=self.config.timeout_seconds)
                    job.results.append(result)

                    if self.config.enable_progress_tracking:
                        self._log_progress(job, processed_count)

                except Exception as e:
                    error_result = ProcessingResult(
                        item_id=item_id,
                        status=ItemStatus.FAILED,
                        error=str(e)
                    )
                    job.results.append(error_result)
                    job.error_messages.append(f"{item_id}: {str(e)}")

                    if not self.config.continue_on_error:
                        executor.shutdown(wait=False)
                        job.status = ProcessingStatus.FAILED
                        return self._get_job_result(job)

        job.status = ProcessingStatus.COMPLETED
        job.completed_at = datetime.now()
        logger.info(f"Batch processing completed for job: {job.name}")

        return self._get_job_result(job)

    def _process_item_with_retry(
        self,
        item_id: str,
        data: Dict[str, Any],
        process_func: Callable
    ) -> ProcessingResult:
        """Process item with retry logic."""
        start_time = time.time()
        last_error = None

        for attempt in range(self.config.retry_attempts):
            try:
                result = process_func(item_id, data)
                result.processing_time = time.time() - start_time
                result.retry_count = attempt
                return result

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Error processing {item_id} (attempt {attempt + 1}): {e}"
                )
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(1)  # Back-off delay

        # All retries exhausted
        return ProcessingResult(
            item_id=item_id,
            status=ItemStatus.FAILED,
            error=str(last_error),
            processing_time=time.time() - start_time,
            retry_count=self.config.retry_attempts
        )

    @staticmethod
    def _log_progress(job: BatchJob, processed_count: int) -> None:
        """Log processing progress."""
        progress = job.get_progress()
        logger.info(
            f"Job {job.id}: {processed_count}/{len(job.items)} items "
            f"({progress['completion_percentage']:.1f}%)"
        )

    @staticmethod
    def _get_job_result(job: BatchJob) -> Dict[str, Any]:
        """Get job result summary."""
        processing_time = (
            (job.completed_at - job.started_at).total_seconds()
            if job.completed_at and job.started_at else 0
        )

        results_by_status = {}
        for status in ItemStatus:
            count = len([r for r in job.results if r.status == status])
            if count > 0:
                results_by_status[status.value] = count

        return {
            "job_id": job.id,
            "job_name": job.name,
            "status": job.status.value,
            "total_items": len(job.items),
            "results_by_status": results_by_status,
            "processing_time_seconds": processing_time,
            "items_per_second": (
                len(job.items) / processing_time if processing_time > 0 else 0
            ),
            "success_rate": (
                len([r for r in job.results if r.status == ItemStatus.COMPLETED]) /
                len(job.items) * 100
                if job.items else 0
            ),
            "errors": job.error_messages
        }


class DocumentBatchProcessor:
    """Specialized processor for legal documents."""

    def __init__(self, config: Optional[BatchConfig] = None):
        """Initialize document processor."""
        self.processor = BatchProcessor(config)
        self.config = config or BatchConfig()
        logger.info("Initialized document batch processor")

    def process_documents(
        self,
        job: BatchJob,
        processing_func: Callable
    ) -> Dict[str, Any]:
        """Process batch of documents."""
        return self.processor.process(job, processing_func)


class ProgressTracker:
    """Tracks progress of batch processing."""

    def __init__(self):
        """Initialize tracker."""
        self.progress_updates: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def start(self) -> None:
        """Start tracking."""
        self.start_time = datetime.now()

    def end(self) -> None:
        """End tracking."""
        self.end_time = datetime.now()

    def log_update(self, update: Dict[str, Any]) -> None:
        """Log progress update."""
        update["timestamp"] = datetime.now().isoformat()
        self.progress_updates.append(update)

    def get_duration(self) -> Optional[timedelta]:
        """Get total duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                self.get_duration().total_seconds()
                if self.get_duration() else None
            ),
            "total_updates": len(self.progress_updates),
            "updates": self.progress_updates
        }


def sample_document_processor(item_id: str, data: Dict[str, Any]) -> ProcessingResult:
    """Sample document processing function."""
    try:
        # Simulate processing
        time.sleep(0.1)

        result = {
            "document_id": item_id,
            "processed": True,
            "data": data
        }

        return ProcessingResult(
            item_id=item_id,
            status=ItemStatus.COMPLETED,
            output=result
        )

    except Exception as e:
        return ProcessingResult(
            item_id=item_id,
            status=ItemStatus.FAILED,
            error=str(e)
        )


if __name__ == "__main__":
    # Create batch job
    config = BatchConfig(max_workers=4, batch_size=10)
    job = BatchJob(name="Sample Document Batch", config=config)

    # Add items
    for i in range(10):
        job.add_item(f"doc_{i:03d}", {"content": f"Document {i}"})

    # Process
    processor = BatchProcessor(config)
    result = processor.process(job, sample_document_processor)

    print("Batch Processing Result:")
    print(json.dumps(result, indent=2, default=str))

    print("\nJob Progress:")
    print(json.dumps(job.get_progress(), indent=2))
