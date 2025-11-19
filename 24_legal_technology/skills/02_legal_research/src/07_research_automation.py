"""
Legal Research Automation Framework
Automates repetitive legal research tasks and coordinates research workflows
"""

import asyncio
import json
from typing import List, Dict, Optional, Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ResearchTask:
    """Represents a single legal research task"""
    task_id: str
    query: str
    research_type: str  # case_law, statutory, regulatory, etc.
    jurisdiction: Optional[str] = None
    priority: int = 1
    deadline: Optional[datetime] = None
    results: List[Dict] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ResearchAutomationEngine:
    """
    Coordinates automated legal research workflows
    """

    def __init__(self, max_concurrent_tasks: int = 5):
        """
        Initialize automation engine

        Args:
            max_concurrent_tasks: Maximum concurrent research tasks
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue: List[ResearchTask] = []
        self.active_tasks: Dict[str, ResearchTask] = {}
        self.handlers: Dict[str, Callable] = {}
        self.research_history: List[ResearchTask] = []

    def register_handler(self, research_type: str, handler: Callable):
        """
        Register handler for specific research type

        Args:
            research_type: Type of research (case_law, statutory, etc.)
            handler: Async handler function
        """
        self.handlers[research_type] = handler
        logger.info(f"Registered handler for {research_type}")

    def queue_research(self, task: ResearchTask):
        """
        Queue a research task for execution

        Args:
            task: ResearchTask to queue
        """
        self.task_queue.append(task)
        logger.info(f"Queued research task: {task.task_id}")

    def queue_research_batch(self, tasks: List[ResearchTask]):
        """
        Queue multiple research tasks

        Args:
            tasks: List of ResearchTask objects
        """
        self.task_queue.extend(tasks)
        logger.info(f"Queued {len(tasks)} research tasks")

    async def execute_task(self, task: ResearchTask) -> ResearchTask:
        """
        Execute a single research task

        Args:
            task: Task to execute

        Returns:
            Completed task with results
        """
        task.status = "in_progress"
        self.active_tasks[task.task_id] = task

        try:
            handler = self.handlers.get(task.research_type)
            if not handler:
                raise ValueError(f"No handler for research type: {task.research_type}")

            # Execute handler
            if asyncio.iscoroutinefunction(handler):
                results = await handler(task)
            else:
                results = handler(task)

            task.results = results
            task.status = "completed"
            task.completed_at = datetime.now()

            logger.info(f"Completed task: {task.task_id} with {len(results)} results")

        except Exception as e:
            task.status = "failed"
            task.results = [{"error": str(e)}]
            logger.error(f"Task failed: {task.task_id} - {str(e)}")

        finally:
            del self.active_tasks[task.task_id]
            self.research_history.append(task)

        return task

    async def run_automation(self) -> List[ResearchTask]:
        """
        Run automation engine with concurrent task execution

        Returns:
            List of completed tasks
        """
        logger.info(f"Starting automation engine with {len(self.task_queue)} tasks")

        completed_tasks = []

        while self.task_queue or self.active_tasks:
            # Fill active task slots
            while len(self.active_tasks) < self.max_concurrent_tasks and self.task_queue:
                task = self.task_queue.pop(0)

                # Sort by priority
                self.task_queue.sort(key=lambda t: (-t.priority, t.created_at))

            # Wait for any task to complete
            if self.active_tasks:
                tasks = list(self.active_tasks.values())
                completed_task = await self.execute_task(tasks[0])
                completed_tasks.append(completed_task)

            await asyncio.sleep(0.1)

        logger.info(f"Automation complete: {len(completed_tasks)} tasks processed")
        return completed_tasks

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Get status of a research task

        Args:
            task_id: Task ID

        Returns:
            Task status dictionary
        """
        task = self.active_tasks.get(task_id)
        if not task:
            for h_task in self.research_history:
                if h_task.task_id == task_id:
                    task = h_task
                    break

        if task:
            return {
                "task_id": task.task_id,
                "status": task.status,
                "progress": len(task.results),
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }

        return None

    def get_statistics(self) -> Dict:
        """
        Get automation engine statistics

        Returns:
            Statistics dictionary
        """
        completed = [t for t in self.research_history if t.status == "completed"]
        failed = [t for t in self.research_history if t.status == "failed"]

        return {
            "total_tasks": len(self.research_history) + len(self.task_queue),
            "completed": len(completed),
            "failed": len(failed),
            "pending": len(self.task_queue),
            "active": len(self.active_tasks),
            "total_results": sum(len(t.results) for t in self.research_history),
            "success_rate": len(completed) / (len(completed) + len(failed)) if completed or failed else 0
        }


# Example handler implementations
async def handle_case_law_search(task: ResearchTask) -> List[Dict]:
    """Example handler for case law research"""
    logger.info(f"Searching case law for: {task.query}")
    # Simulated results
    return [
        {
            "citation": "123 F.3d 456 (9th Cir. 2020)",
            "title": "Example Case v. Defendant",
            "relevance": 0.95
        }
    ]


async def handle_statutory_research(task: ResearchTask) -> List[Dict]:
    """Example handler for statutory research"""
    logger.info(f"Searching statutes for: {task.query}")
    return [
        {
            "statute": "42 U.S.C. § 1983",
            "title": "Civil action for deprivation of rights",
            "relevance": 0.92
        }
    ]


# Usage example
if __name__ == "__main__":
    async def main():
        engine = ResearchAutomationEngine(max_concurrent_tasks=3)

        # Register handlers
        engine.register_handler("case_law", handle_case_law_search)
        engine.register_handler("statutory", handle_statutory_research)

        # Create tasks
        tasks = [
            ResearchTask(
                task_id="task_001",
                query="employment discrimination",
                research_type="case_law",
                jurisdiction="federal",
                priority=1
            ),
            ResearchTask(
                task_id="task_002",
                query="civil rights violations",
                research_type="statutory",
                priority=2
            )
        ]

        engine.queue_research_batch(tasks)

        # Run automation
        completed = await engine.run_automation()

        # Print results
        stats = engine.get_statistics()
        print(f"Automation Statistics: {json.dumps(stats, indent=2)}")

    asyncio.run(main())
