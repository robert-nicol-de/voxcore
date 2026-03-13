from types import SimpleNamespace
from typing import Any

from backend.control_plane.models import ControlPlaneContext, QueryRoutePlan


def _get_header_value(request: Any, header_name: str) -> str | None:
    headers = getattr(request, "headers", None)
    if headers is None:
        return None
    if hasattr(headers, "get"):
        return headers.get(header_name)
    return None


def build_control_plane_context(
    request: Any,
    payload: Any,
    operation: str,
    entrypoint: str = "api",
) -> ControlPlaneContext:
    state = getattr(request, "state", None)
    company_id = str(getattr(state, "org_id", getattr(payload, "company_id", "default")))
    workspace_id = str(getattr(state, "workspace_id", getattr(payload, "workspace_id", "default")))
    user_id = getattr(state, "user_id", None)
    role = getattr(state, "role", None)
    datasource_id = getattr(state, "datasource_id", None)
    schema_name = _get_header_value(request, "X-Schema-Name")

    return ControlPlaneContext(
        operation=operation,
        company_id=company_id,
        workspace_id=workspace_id,
        user_id=user_id,
        role=role,
        datasource_id=datasource_id,
        schema_name=schema_name,
        entrypoint=entrypoint,
    )


def build_query_route_plan(mode: str) -> QueryRoutePlan:
    queued = mode == "queued"
    return QueryRoutePlan(
        mode=mode,
        query_queue=queued,
        telemetry=True,
    )


def build_control_plane_metadata(
    context: ControlPlaneContext,
    route_plan: QueryRoutePlan,
    status: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = {
        "layer": "voxcore_control_plane",
        "operation": context.operation,
        "status": status,
        "context": context.as_dict(),
        "route_plan": route_plan.as_dict(),
    }
    if extra:
        metadata["extra"] = extra
    return metadata


def build_worker_request_context(payload: dict[str, Any]) -> Any:
    return SimpleNamespace(
        state=SimpleNamespace(
            org_id=payload.get("company_id"),
            workspace_id=payload.get("workspace_id"),
            datasource_id=payload.get("datasource_id"),
            user_id=payload.get("user_id"),
            role=payload.get("role"),
        ),
        headers={"X-Schema-Name": payload.get("schema_name")},
    )
