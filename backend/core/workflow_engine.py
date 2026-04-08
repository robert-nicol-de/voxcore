# Core workflow runner for VoxCore orchestration
import datetime
import json
from typing import Dict, Any
from backend.models.workflow import Workflow, WorkflowStep, WorkflowExecution
from backend.schemas.workflow import WorkflowModel, WorkflowStepModel, WorkflowExecutionModel
from backend.api.action_api import execute_action
from backend.api.integration_services import send_slack_message, send_email
from backend import db

# --- Step Executor ---
def execute_step(step: Dict[str, Any], context: Dict[str, Any]):
    t = step["type"]
    if t == "action":
        execute_action(step["config"].get("action_type"), context)
    elif t == "slack":
        send_slack_message("#alerts", step["config"].get("message", ""))
    elif t == "wait":
        # Persist execution and schedule resume (pseudo)
        days = step["config"].get("days", 1)
        # schedule_next_step(days)  # To be implemented with APScheduler
        pass
    elif t == "evaluate":
        # Evaluate outcome (custom logic)
        pass
    elif t == "email":
        send_email(context.get("email", "executive@company.com"), "Workflow Summary", "Workflow completed.")

# --- Workflow Runner ---
def run_workflow(workflow: Dict[str, Any], context: Dict[str, Any]):
    for step in workflow["steps"]:
        execute_step(step, context)

# --- Trigger Integration ---
def trigger_workflows(trigger_type: str, context: Dict[str, Any]):
    # Query enabled workflows with this trigger
    session = db.Session()
    workflows = session.query(Workflow).filter_by(trigger_type=trigger_type, enabled=True).all()
    for wf in workflows:
        wf_dict = {
            "id": wf.id,
            "name": wf.name,
            "trigger": wf.trigger_type,
            "steps": [json.loads(s.config) for s in session.query(WorkflowStep).filter_by(workflow_id=wf.id).order_by(WorkflowStep.step_order)]
        }
        run_workflow(wf_dict, context)
    session.close()

# --- Resume Logic (for async steps) ---
def resume_workflow(execution_id: str):
    session = db.Session()
    exec = session.query(WorkflowExecution).filter_by(id=execution_id).first()
    if not exec:
        session.close()
        return
    context = json.loads(exec.context)
    wf = session.query(Workflow).filter_by(id=exec.workflow_id).first()
    steps = [json.loads(s.config) for s in session.query(WorkflowStep).filter_by(workflow_id=wf.id).order_by(WorkflowStep.step_order)]
    if exec.current_step < len(steps):
        execute_step(steps[exec.current_step], context)
        exec.current_step += 1
        session.commit()
    session.close()
