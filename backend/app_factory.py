import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.action_api import router as action_router
from backend.api.action_learning_sqlite import (
    ensure_action_learning_runtime,
    router as action_learning_router,
)
from backend.api.admin_audit import router as admin_audit_router
from backend.api.approval_api import router as approval_api_router
from backend.api.auth import ensure_auth_bootstrap, router as auth_router
from backend.api.auto_action_metrics_api import router as auto_action_metrics_router
from backend.api.auto_action_rules_sqlite import (
    ensure_auto_action_rules_db,
    router as auto_action_rules_router,
)
from backend.api.build_os import build_router
from backend.api.daily_digest import router as daily_digest_router
from backend.api.data_upload_api import router as data_upload_router
from backend.api.google_oauth_api import router as google_oauth_router
from backend.api.google_sheets_api import router as google_sheets_router
from backend.api.google_sheets_picker_api import router as google_sheets_picker_router
from backend.api.impact_story_api import router as impact_story_router
from backend.api.impact_summary_api import router as impact_summary_router
from backend.api.insight_timeline_api import router as insight_timeline_router
from backend.api.insights import router as insights_router
from backend.api.integration_services import router as integration_router
from backend.api.pr_api import router as pr_router
from backend.api.query import router as canonical_query_router
from backend.api.workflow_api import router as workflow_router
from backend.api.workflow_simulation_ai_api import router as workflow_simulation_ai_router
from backend.api.workflow_simulation_api import router as workflow_simulation_router
from backend.app.api.brief_alerts_api import router as brief_alerts_router
from backend.app.api.owner_workspace_api_persistence import router as owner_workspace_router
from backend.app.api.phase2_api import router as phase2_router
from backend.db.insight_store import create_tables
from backend.routers.logs import router as logs_router
from backend.routers.metrics import router as metrics_router
from backend.session_cleanup import start_session_cleanup_thread
from voxcore.api.analytics_api import router as analytics_router
from voxcore.api.connectors_api import router as connectors_router
from backend.voxcore.api.conversation_api import router as conversation_router
from voxcore.api.dashboard_api import router as dashboard_router
from voxcore.api.schema_api import router as schema_router

logger = logging.getLogger(__name__)


ROUTER_SPECS = [
    (build_router, {}),
    (google_sheets_picker_router, {"prefix": "/api"}),
    (google_oauth_router, {"prefix": "/api"}),
    (google_sheets_router, {"prefix": "/api"}),
    (data_upload_router, {"prefix": "/api"}),
    (workflow_simulation_ai_router, {"prefix": "/api"}),
    (workflow_simulation_router, {"prefix": "/api"}),
    (workflow_router, {"prefix": "/api"}),
    (insight_timeline_router, {"prefix": "/api"}),
    (schema_router, {"prefix": "/api"}),
    (analytics_router, {}),
    (action_router, {"prefix": "/api"}),
    (impact_summary_router, {"prefix": "/api/actions"}),
    (action_learning_router, {"prefix": "/api/actions"}),
    (auto_action_rules_router, {"prefix": "/api/actions"}),
    (auto_action_metrics_router, {"prefix": "/api"}),
    (impact_story_router, {"prefix": "/api"}),
    (integration_router, {"prefix": "/api"}),
    (connectors_router, {}),
    (auth_router, {}),
    (daily_digest_router, {"prefix": "/api"}),
    (admin_audit_router, {}),
    (owner_workspace_router, {}),
    (phase2_router, {}),
    (brief_alerts_router, {}),
    (canonical_query_router, {}),
    (conversation_router, {}),
    (approval_api_router, {}),
    (metrics_router, {"prefix": "/api"}),
    (logs_router, {"prefix": "/api/v1/query"}),
    (dashboard_router, {}),
    (insights_router, {}),
    (pr_router, {}),
]


def _cors_origins() -> list[str]:
    default_origins = [
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    configured = os.getenv(
        "CORS_ORIGINS",
        ",".join(default_origins),
    )
    origins = [origin.strip() for origin in configured.split(",") if origin.strip()]

    for origin in default_origins:
        if origin not in origins:
            origins.append(origin)

    return origins


def configure_app(app: FastAPI) -> None:
    allow_credentials = (
        os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )


def include_application_routes(app: FastAPI) -> None:
    for router, kwargs in ROUTER_SPECS:
        app.include_router(router, **kwargs)

    @app.get("/")
    def root():
        return {"status": "ok"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    ensure_auto_action_rules_db()
    ensure_action_learning_runtime()
    start_session_cleanup_thread()
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    configure_app(app)
    include_application_routes(app)
    return app


app = create_app()
