#!/usr/bin/env python3
"""Workflow Orchestration - Coordinate multi-step healthcare workflows"""

from enum import Enum
from typing import Callable, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowStep:
    """Single workflow step"""
    def __init__(self, name: str, handler: Callable):
        self.name = name
        self.handler = handler

class Workflow:
    """Healthcare workflow orchestrator"""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[WorkflowStep] = []
        self.status = WorkflowStatus.PENDING

    def add_step(self, step: WorkflowStep):
        """Add workflow step"""
        self.steps.append(step)

    def execute(self, context: Dict) -> bool:
        """Execute workflow"""
        self.status = WorkflowStatus.RUNNING

        try:
            for step in self.steps:
                logger.info(f"Executing {step.name}")
                result = step.handler(context)
                if not result:
                    raise Exception(f"Step {step.name} failed")

            self.status = WorkflowStatus.COMPLETED
            return True

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            self.status = WorkflowStatus.FAILED
            return False
