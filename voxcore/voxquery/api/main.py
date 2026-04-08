from fastapi import FastAPI

# Routers (convert sub-apps to routers if needed)
from voxcore.api.connectors_api import router as connectors_router
from voxcore.api.audit_api import router as audit_router
from voxcore.api.alerts_api import router as alerts_router
from voxcore.api.monitoring_ws import router as monitoring_ws_router

# Existing APIs (temporary mount if still apps)

from voxcore.api.conversation_api import router as conversation_router
from voxcore.api.dashboard_api import router as dashboard_router
from voxcore.api.timeline_api import router as timeline_router

app = FastAPI(title="VoxCore API")

# ✅ Core routers
app.include_router(connectors_router)
app.include_router(audit_router)
app.include_router(alerts_router)
app.include_router(monitoring_ws_router)


# ✅ Add as routers
app.include_router(conversation_router)
app.include_router(dashboard_router)
app.include_router(timeline_router)
