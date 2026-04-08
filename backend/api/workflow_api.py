# FastAPI endpoints for workflow orchestration
from fastapi import APIRouter, HTTPException
from typing import List
from ..models.workflow import Workflow, WorkflowStep, WorkflowExecution
from ..schemas.workflow import WorkflowModel, WorkflowStepModel, WorkflowExecutionModel
from ..core.workflow_engine import run_workflow, trigger_workflows, resume_workflow
from .. import db
import uuid
import datetime
import json

router = APIRouter()

@router.post("/api/workflows", response_model=WorkflowModel)
def create_workflow(wf: WorkflowModel):
    session = db.Session()
    db_wf = Workflow(
        id=wf.id or str(uuid.uuid4()),
        name=wf.name,
        trigger_type=wf.trigger_type,
        enabled=wf.enabled,
        created_at=datetime.datetime.utcnow()
    )
    session.add(db_wf)
    for step in wf.steps:
        db_step = WorkflowStep(
            id=step.id or str(uuid.uuid4()),
            workflow_id=db_wf.id,
            step_order=step.step_order,
            step_type=step.step_type,
            config=json.dumps(step.config)
        )
        session.add(db_step)
    session.commit()
    session.close()
    return wf

@router.get("/api/workflows", response_model=List[WorkflowModel])
def list_workflows():
    session = db.Session()
    workflows = session.query(Workflow).all()
    result = []
    for wf in workflows:
        steps = session.query(WorkflowStep).filter_by(workflow_id=wf.id).order_by(WorkflowStep.step_order).all()
        wf_model = WorkflowModel(
            id=wf.id,
            name=wf.name,
            trigger_type=wf.trigger_type,
            enabled=wf.enabled,
            created_at=str(wf.created_at),
            steps=[WorkflowStepModel(
                id=s.id,
                workflow_id=s.workflow_id,
                step_order=s.step_order,
                step_type=s.step_type,
                config=json.loads(s.config)
            ) for s in steps]
        )
        result.append(wf_model)
    session.close()
    return result

@router.post("/api/workflows/trigger/{trigger_type}")
def trigger_workflow(trigger_type: str, context: dict):
    trigger_workflows(trigger_type, context)
    return {"status": "triggered"}

@router.post("/api/workflows/resume/{execution_id}")
def resume_workflow_api(execution_id: str):
    resume_workflow(execution_id)
    return {"status": "resumed"}
