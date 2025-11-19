"""Claims workflow management"""
from enum import Enum
from typing import Dict

class WorkflowState(Enum):
    INTAKE = "intake"
    ASSESSMENT = "assessment"
    DECISION = "decision"
    SETTLEMENT = "settlement"

class ClaimsWorkflow:
    def __init__(self):
        self.current_state = WorkflowState.INTAKE
    
    def advance_workflow(self, claim: Dict) -> Dict:
        """Move to next workflow state"""
        if self.current_state == WorkflowState.INTAKE:
            self.current_state = WorkflowState.ASSESSMENT
        elif self.current_state == WorkflowState.ASSESSMENT:
            self.current_state = WorkflowState.DECISION
        elif self.current_state == WorkflowState.DECISION:
            self.current_state = WorkflowState.SETTLEMENT
        
        return {"current_state": self.current_state.value}
