from __future__ import annotations

from typing import Any

from .analysis_session import AnalysisSession, AnalysisSessionStore
from .intent_parser import extract_query_intent
from .semantic_service import SemanticBrainService

_service = SemanticBrainService()


def extract_schema_summary(ai_context: dict[str, Any], max_lines: int = 8) -> list[str]:
    return _service.extract_schema_summary(ai_context, max_lines=max_lines)


def build_understanding(intent: dict[str, Any]) -> dict[str, str]:
    return _service.build_understanding(intent)


def suggest_sql(query_text: str, intent: dict[str, Any]) -> str:
    return _service.suggest_sql(query_text, intent)


def recommend_chart(intent: dict[str, Any]) -> dict[str, str]:
    plan = {
        "analysis_type": "comparison" if intent.get("comparison") else "trend" if intent.get("has_trend") else "ranking",
        "comparison": intent.get("comparison"),
    }
    return _service.recommend_visualization(plan)


def build_preview_chart(preview_rows: list[dict[str, Any]], intent: dict[str, Any]) -> dict[str, Any] | None:
    plan = {
        "analysis_type": "comparison" if intent.get("comparison") else "trend" if intent.get("has_trend") else "ranking",
        "comparison": intent.get("comparison"),
        "dimension": intent.get("dimension"),
        "metric": intent.get("metric"),
    }
    return _service.build_preview_chart(preview_rows, intent, plan)


def build_semantic_brain_snapshot(workspace_id: Any, ai_context: dict[str, Any] | None = None) -> dict[str, Any]:
    return _service.build_snapshot(workspace_id, ai_context)


def build_analytical_plan(query_text: str, brain: dict[str, Any], intent: dict[str, Any] | None = None) -> dict[str, Any]:
    return _service.build_analytical_plan(query_text, brain, intent)


def apply_followup_context(query_text: str, plan: dict[str, Any], previous_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    return _service.planner.apply_followup_context(query_text, plan, previous_plan)


def recommend_visualization(plan: dict[str, Any]) -> dict[str, str]:
    return _service.recommend_visualization(plan)


def generate_semantic_sql(plan: dict[str, Any], brain: dict[str, Any], fallback_sql: str = "") -> str:
    return _service.generate_sql(plan, fallback_sql=fallback_sql)


def detect_insights(plan: dict[str, Any], preview_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return _service.detect_insights(plan, preview_rows)


def generate_insight_summary(plan: dict[str, Any], preview_rows: list[dict[str, Any]]) -> str:
    insights = _service.detect_insights(plan, preview_rows)
    return str(insights.get("narrative") or "No clear insights yet.")


def generate_suggested_questions(plan: dict[str, Any], insights: dict[str, Any] | None = None) -> list[str]:
    return _service.generate_suggested_questions(plan, insights)


def build_semantic_context_prompt(brain: dict[str, Any], max_metrics: int = 12, max_dimensions: int = 20) -> str:
    # max_metrics/max_dimensions are accepted for backward compatibility.
    _ = max_metrics
    _ = max_dimensions
    return _service.build_semantic_context_prompt(brain)


def build_semantic_payload(
    query_text: str,
    workspace_id: Any,
    ai_context: dict[str, Any],
    previous_plan: dict[str, Any] | None = None,
    preview_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return _service.build_payload(
        query_text=query_text,
        workspace_id=workspace_id,
        ai_context=ai_context,
        previous_plan=previous_plan,
        preview_rows=preview_rows,
    )


__all__ = [
    "AnalysisSession",
    "AnalysisSessionStore",
    "SemanticBrainService",
    "extract_query_intent",
    "extract_schema_summary",
    "build_understanding",
    "suggest_sql",
    "recommend_chart",
    "build_preview_chart",
    "build_semantic_brain_snapshot",
    "build_analytical_plan",
    "apply_followup_context",
    "recommend_visualization",
    "generate_semantic_sql",
    "detect_insights",
    "generate_insight_summary",
    "generate_suggested_questions",
    "build_semantic_context_prompt",
    "build_semantic_payload",
]
