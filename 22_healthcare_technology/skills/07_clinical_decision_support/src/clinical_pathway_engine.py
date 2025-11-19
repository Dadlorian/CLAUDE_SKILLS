"""Clinical Pathway Automation Engine"""
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional

class PathwayStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    DEVIATED = "DEVIATED"

class PathwayTask:
    def __init__(self, name, time_target_minutes, required=True):
        self.name = name
        self.time_target = time_target_minutes
        self.required = required
        self.completed = False
        self.completion_time = None
    
    def complete(self):
        self.completed = True
        self.completion_time = datetime.now()

class ClinicalPathway:
    def __init__(self, name, patient_id):
        self.name = name
        self.patient_id = patient_id
        self.activation_time = datetime.now()
        self.tasks: List[PathwayTask] = []
        self.status = PathwayStatus.ACTIVE
    
    def add_task(self, task: PathwayTask):
        self.tasks.append(task)
    
    def check_compliance(self) -> Dict:
        """Check pathway compliance and time metrics"""
        overdue_tasks = []
        completed_tasks = []
        
        for task in self.tasks:
            if task.completed:
                completed_tasks.append(task)
            else:
                deadline = self.activation_time + timedelta(minutes=task.time_target)
                if datetime.now() > deadline and task.required:
                    overdue_tasks.append({
                        'task': task.name,
                        'overdue_by_minutes': (datetime.now() - deadline).seconds // 60
                    })
        
        return {
            'status': self.status.value,
            'completion_rate': len(completed_tasks) / len(self.tasks),
            'overdue_tasks': overdue_tasks,
            'compliance': len(overdue_tasks) == 0
        }

class SepsisPathway(ClinicalPathway):
    def __init__(self, patient_id):
        super().__init__("Sepsis Bundle", patient_id)
        self._initialize_tasks()
    
    def _initialize_tasks(self):
        self.add_task(PathwayTask("Blood cultures obtained", 60, required=True))
        self.add_task(PathwayTask("Lactate measured", 60, required=True))
        self.add_task(PathwayTask("Antibiotics administered", 60, required=True))
        self.add_task(PathwayTask("Fluid bolus 30mL/kg", 180, required=True))
        self.add_task(PathwayTask("Lactate remeasured if >2", 180, required=False))
