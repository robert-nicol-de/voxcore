from typing import Any

from backend.control_plane.context import (
    build_control_plane_context,
    build_control_plane_metadata,
    build_query_route_plan,
)
from backend.services.query_job_queue import enqueue_query_job


class ControlPlaneOrchestrator:
    def handle_query(self, request: Any, payload: Any) -> dict[str, Any]:
        from backend.api import query as query_api

        context = build_control_plane_context(request, payload, operation="query.execute", entrypoint="api")
        route_plan = build_query_route_plan(mode="sync")
        result = query_api.process_query_payload(request, payload)
        result["control_plane"] = build_control_plane_metadata(
            context,
            route_plan,
            status=str(result.get("status", "unknown")),
        )
        return result

    def enqueue_query(self, request: Any, payload: Any) -> dict[str, Any]:
        from backend.api import query as query_api

        context = build_control_plane_context(request, payload, operation="query.execute", entrypoint="api")
        route_plan = build_query_route_plan(mode="queued")
        company_id, workspace_id = query_api._resolve_tenant_context(
            request,
            payload.company_id,
            payload.workspace_id,
        )
        queued_payload = payload.model_dump()
        queued_payload["company_id"] = company_id
        queued_payload["workspace_id"] = workspace_id
        queued_payload["control_plane_operation"] = context.operation
        queued_payload["control_plane_route"] = route_plan.as_dict()
        job_id = enqueue_query_job(queued_payload)

        previous_plan = query_api._get_previous_plan(company_id, workspace_id)
        semantic_payload = query_api._build_semantic_payload(
            request,
            payload.query,
            workspace_id,
            previous_plan=previous_plan,
        )
        query_api._save_latest_plan(company_id, workspace_id, semantic_payload["analytical_plan"])

        response = {
            "status": "queued",
            "job_id": job_id,
            "message": "Query queued for worker execution",
        } | semantic_payload
        response["control_plane"] = build_control_plane_metadata(
            context,
            route_plan,
            status="queued",
            extra={"job_id": job_id},
        )
        return response


_CONTROL_PLANE = ControlPlaneOrchestrator()


def get_control_plane() -> ControlPlaneOrchestrator:
    return _CONTROL_PLANE
