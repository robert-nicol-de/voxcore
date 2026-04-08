# Pydantic models for workflow orchestration
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class WorkflowStepModel(BaseModel):
    id: str
    workflow_id: str
    step_order: int
    step_type: str
    config: Dict[str, Any]

class WorkflowModel(BaseModel):
    id: str
    name: str
    trigger_type: str
    enabled: bool
    created_at: str
    steps: List[WorkflowStepModel] = []

class WorkflowExecutionModel(BaseModel):
    id: str
    workflow_id: str
    current_step: int
    status: str
    context: Dict[str, Any]
    started_at: str
