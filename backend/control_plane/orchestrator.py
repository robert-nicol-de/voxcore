from typing import Any

from backend.control_plane.context import (
    build_control_plane_context,
    build_control_plane_metadata,
    build_query_route_plan,
)
from backend.services.query_job_queue import enqueue_query_job, is_using_fallback_queue


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

    def handle_query_from_connector(
        self,
        request: Any,
        payload: Any,
        connector_type: str,
        connector_config: dict,
        connector_user_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Adapter method: route connector queries through canonical governed path.
        
        Preserves connector context in control_plane metadata while applying
        full governance pipeline (policies, risk, approval, clarification, fallback).
        
        Args:
            request: FastAPI Request object
            payload: Canonical QueryRequest
            connector_type: Connector type identifier
            connector_config: Connector configuration
            connector_user_id: ID of user executing via connector
        
        Returns:
            Governed query result with connector context preserved
        """
        from backend.api import query as query_api

        # Build base control plane context
        context = build_control_plane_context(
            request, 
            payload, 
            operation="query.connector_execute",
            entrypoint="connector",
        )
        
        # Use sync mode for synchronous execution
        route_plan = build_query_route_plan(mode="sync")
        
        # Execute through canonical governed pipeline
        result = query_api.process_query_payload(request, payload)
        
        # Build control plane metadata with connector context
        connector_context = {
            "connector_type": connector_type,
            "connector_user_id": connector_user_id,
            # Don't include full config in metadata (security)
            "connector_config_keys": list(connector_config.keys()) if isinstance(connector_config, dict) else [],
        }
        
        result["control_plane"] = build_control_plane_metadata(
            context,
            route_plan,
            status=str(result.get("status", "unknown")),
            extra={"connector": connector_context},
        )
        
        return result

    def handle_query_from_pr(
        self,
        request: Any,
        payload: Any,
        pr_type: str,
        pr_domain: str,
        pr_approach: str,
        pr_title: str,
    ) -> dict[str, Any]:
        """
        Route PR queries through the canonical governed query path while
        preserving PR context in control-plane metadata.
        
        Args:
            request: FastAPI Request object
            payload: Canonical QueryRequest
            pr_type: PR type identifier
            pr_domain: PR domain
            pr_approach: PR approach
            pr_title: PR title
        
        Returns:
            Governed query result with PR context preserved
        """
        from backend.api import query as query_api

        control_plane_ctx = build_control_plane_context(
            request,
            payload,
            operation="query.pr_execute",
            entrypoint="pr_api",
        )

        route_plan = build_query_route_plan(mode="sync")

        # Canonical governed execution authority
        result = query_api.process_query_payload(request, payload)

        pr_context = {
            "pr_type": pr_type,
            "pr_domain": pr_domain,
            "pr_approach": pr_approach,
            "pr_title": pr_title,
        }

        # Safely preserve/attach control-plane metadata
        existing_cp = result.get("control_plane") or {}
        existing_extra = existing_cp.get("extra") or {}

        result["control_plane"] = build_control_plane_metadata(
            control_plane_ctx,
            route_plan,
            status=str(result.get("status", "unknown")),
            extra={
                **existing_extra,
                "pr": pr_context,
            },
        )

        return result

    def enqueue_query(self, request: Any, payload: Any) -> dict[str, Any]:
        from backend.api import query as query_api
        from backend.workers.query_worker import start_worker_thread

        context = build_control_plane_context(request, payload, operation="query.execute", entrypoint="api")
        route_plan = build_query_route_plan(mode="queued")
        company_id, workspace_id = query_api._resolve_tenant_context(
            request,
            payload.company_id,
            payload.workspace_id,
        )
        queued_payload = payload.model_dump()
        request_state = getattr(request, "state", None)
        queued_payload["company_id"] = company_id
        queued_payload["workspace_id"] = workspace_id
        queued_payload["user_id"] = getattr(request_state, "user_id", None)
        queued_payload["role"] = getattr(request_state, "role", None)
        queued_payload["user_email"] = getattr(request_state, "user_email", None)
        queued_payload["datasource_id"] = getattr(request_state, "datasource_id", None)
        queued_payload["schema_name"] = (
            request.headers.get("X-Schema-Name")
            if getattr(request, "headers", None) is not None and hasattr(request.headers, "get")
            else None
        )
        queued_payload["control_plane_operation"] = context.operation
        queued_payload["control_plane_route"] = route_plan.as_dict()
        job_id = enqueue_query_job(queued_payload)

        # When Redis is unavailable, the queue falls back to in-process memory.
        # Ensure the API process owns a lightweight worker thread so queued jobs
        # still progress instead of stalling forever in a separate empty process.
        if is_using_fallback_queue():
            start_worker_thread()

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
