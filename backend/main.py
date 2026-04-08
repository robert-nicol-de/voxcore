import json
from fastapi import APIRouter
from backend.services.security_redaction import sanitize_exception_message
build_router = APIRouter()

@build_router.post("/api/build/auto-tasks")
def generate_tasks():
    build = load_yaml()
    def detect_problems(build):
        problems = []
        for phase in build.get("phases", []):
            for task in phase.get("tasks", []):
                if task.get("status") == "blocked":
                    problems.append(f"{task['id']} is blocked")
                if not task.get("definition_of_done"):
                    problems.append(f"{task['id']} missing definition of done")
                if not task.get("depends_on"):
                    problems.append(f"{task['id']} may lack dependencies")
        return problems
    problems = detect_problems(build)
    prompt = f"""
You are an expert engineering system.\n\nAnalyze this build system and these detected problems:\n{problems}\n\nThen generate NEW tasks to fix them.\n\nReturn JSON format:\n[\n  {{\n    \"phase\": \"phase_1\",\n    \"id\": \"AUTO-1\",\n    \"description\": \"...\",\n    \"depends_on\": [],\n    \"definition_of_done\": [\"...\"],\n    \"priority\": \"high\",\n    \"reason\": \"Why this task is needed\"\n  }}\n]\n\nBuild:\n{build}\n+"""
    if not openai_client:
        return {"error": "OpenAI client not available. Please install openai package and set up credentials."}
    response = openai_client.chat.completions.create(
        model="gpt-5.3",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        tasks = json.loads(response.choices[0].message.content)
    except Exception as exc:
        return {"error": sanitize_exception_message(exc)}
    if not isinstance(tasks, list):
        return {"error": "Invalid AI response"}
    return {"suggestions": tasks}

@build_router.post("/api/build/approve-task")
def approve_task(task: dict):
    build = load_yaml()
    for phase in build["phases"]:
        if phase["id"] == task["phase"]:
            task["status"] = "not-started"
            task["owner"] = "ai"
            phase["tasks"].append(task)
    save_yaml(build)
    return {"status": "approved"}
from pydantic import BaseModel
import os
try:
    from openai import OpenAI
    if os.getenv("OPENAI_API_KEY"):
        openai_client = OpenAI()
    else:
        openai_client = None
except (ImportError, Exception):
    openai_client = None

class AssistantRequest(BaseModel):
    message: str

def summarize_build(build):
    total = 0
    done = 0
    blocked = 0
    for p in build.get("phases", []):
        for t in p.get("tasks", []):
            total += 1
            if t.get("status") == "done":
                done += 1
            if t.get("status") == "blocked":
                blocked += 1
    return {
        "completion": int(done / total * 100) if total else 0,
        "blocked_tasks": blocked
    }

@build_router.post("/api/build/assistant")
def build_assistant(req: AssistantRequest):
    try:
        build = load_yaml()
        summary = summarize_build(build)
        context = {
            "build": build,
            "summary": summary
        }
        # ...existing code...
        return context
    except Exception as exc:
        return {"error": sanitize_exception_message(exc)}
    prompt = f"""
You are the VoxCore Build OS AI assistant.\nYou analyze a structured build system and give actionable insights.\n\nBuild Data:\n{context}\n\nUser Question:\n{req.message}\n\nInstructions:\n- Be concise\n- Be actionable\n- Highlight blockers, risks, and next steps\n- Prefer bullet points\n"""
    if not openai_client:
        return {"reply": "OpenAI client not available. Please install openai package and set up credentials."}
    response = openai_client.chat.completions.create(
        model="gpt-5.3",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"reply": response.choices[0].message.content}
from fastapi import Body
def load_yaml():
    import yaml
    with open("build_phases.yaml", "r") as f:
        return yaml.safe_load(f)

def save_yaml(data):
    import yaml
    with open("build_phases.yaml", "w") as f:
        yaml.safe_dump(data, f)
import sys
import yaml
import subprocess
from fastapi.responses import JSONResponse
def load_build_status():
    # Load build status from YAML
    try:
        with open("build_phases.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        return {"error": str(e)}

def run_validate_system():
    # Import and run validate_system from buildctl.py
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("buildctl", "buildctl.py")
        buildctl = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(buildctl)
        # validate_system prints and sys.exit(1) on fail, so capture output
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                buildctl.validate_system()
                return {"system": "healthy", "output": buf.getvalue()}
            except SystemExit as e:
                return {"system": "unhealthy", "output": buf.getvalue(), "exit_code": e.code}
    except Exception as e:
        return {"system": "error", "error": str(e)}
# --- VoxCore Build OS API ---

# Use build_router for all build endpoints
@build_router.post("/api/build/task/{task_id}/action")
def update_task_action(task_id: str, data: dict = Body(...)):
    action = data.get("action")
    demo = data.get("demo")
    build = load_yaml()
    for phase in build["phases"]:
        for task in phase["tasks"]:
            if task["id"] == task_id:
                if action == "start":
                    task["status"] = "in-progress"
                elif action == "done":
                    task["status"] = "done"
                if demo is not None:
                    task["demo"] = demo
    save_yaml(build)
    return {"status": "ok"}

@build_router.get("/api/build/status")
def get_build_status():
    return JSONResponse(load_build_status())

@build_router.get("/api/build/validate")
def get_build_validate():
    return JSONResponse(run_validate_system())

from backend.api.google_sheets_picker_api import router as google_sheets_picker_router
from backend.api.google_oauth_api import router as google_oauth_router
from backend.api.google_sheets_api import router as google_sheets_router
from backend.api.data_upload_api import router as data_upload_router
from backend.api.workflow_simulation_ai_api import router as workflow_simulation_ai_router
from backend.api.workflow_simulation_api import router as workflow_simulation_router
from backend.api.workflow_api import router as workflow_router
from backend.api.insight_timeline_api import router as insight_timeline_router
from backend.api.approval_api import router as approval_api_router
from voxcore.api.connectors_api import router as connectors_router

import logging
import os
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.query import router as query_router
from backend.api.insights import router as insights_router
from backend.routers.metrics import router as metrics_router
from backend.routers.logs import router as logs_router
from voxcore.api.schema_api import router as schema_router
from voxcore.api.analytics_api import router as analytics_router
from backend.api.pr_api import router as pr_router
from backend.api.action_api import router as action_router
from backend.api.impact_summary_api import router as impact_summary_router
from backend.api.action_learning_sqlite import router as action_learning_router
from backend.api.auto_action_rules_sqlite import router as auto_action_rules_router
from backend.api.auto_action_metrics_api import router as auto_action_metrics_router
from backend.api.impact_story_api import router as impact_story_router
from backend.api.integration_services import router as integration_router
from backend.api.daily_digest import router as daily_digest_router

import threading
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.services.session_singleton import session_service
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.query import router as query_router


#  Session cleanup with lifespan
def session_cleanup_worker():
    while True:
        time.sleep(300)
        session_service.cleanup()

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=session_cleanup_worker, daemon=True)
    thread.start()
    yield
    # No shutdown needed for daemon thread



from backend.db.insight_store import create_tables

app = FastAPI(lifespan=lifespan)
create_tables()
app.include_router(build_router)

# ✅ CORS middleware must be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add this import to mount dashboard API

# Add this import to mount dashboard API
from voxcore.api.dashboard_api import router as dashboard_router
# Add this import to mount playground API
from voxcore.api.playground_api import router as playground_router

# Routers (all after app is created)
app.include_router(google_sheets_picker_router, prefix="/api")
app.include_router(google_oauth_router, prefix="/api")
app.include_router(google_sheets_router, prefix="/api")
app.include_router(data_upload_router, prefix="/api")
app.include_router(workflow_simulation_ai_router, prefix="/api")
app.include_router(workflow_simulation_router, prefix="/api")
app.include_router(workflow_router, prefix="/api")
app.include_router(insight_timeline_router, prefix="/api")
app.include_router(schema_router, prefix="/api")
app.include_router(analytics_router)
app.include_router(action_router, prefix="/api")
app.include_router(impact_summary_router, prefix="/api/actions")
app.include_router(action_learning_router, prefix="/api/actions")
app.include_router(auto_action_rules_router, prefix="/api/actions")
app.include_router(auto_action_metrics_router, prefix="/api")
app.include_router(impact_story_router, prefix="/api")
app.include_router(integration_router, prefix="/api")
app.include_router(connectors_router)

app.include_router(daily_digest_router, prefix="/api")
# Register playground API router (fix for missing endpoint)
app.include_router(playground_router)

app.include_router(approval_api_router)

@app.get("/")
def root():
    return {"status": "ok"}

# ✅ Route after middleware


# Add timeline endpoint at /api/insights/{insight_id}/timeline
app.include_router(insight_timeline_router, prefix="/api")
# Add metrics endpoint at /api/metrics
app.include_router(metrics_router, prefix="/api")
# Add logs endpoint at /api/v1/query
app.include_router(logs_router, prefix="/api/v1/query")

# Add dashboard API endpoints (must be after app is defined)
app.include_router(dashboard_router)

# Add insights API endpoints
app.include_router(insights_router)

# Add PR API endpoints
app.include_router(pr_router)



# --- Session cleanup automation ---
from backend.session_cleanup import start_session_cleanup_thread

@app.on_event("startup")
def launch_session_cleanup():
    start_session_cleanup_thread()

logger = logging.getLogger(__name__)
