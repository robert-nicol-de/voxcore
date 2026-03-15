from __future__ import annotations

from typing import Any


class ConfidenceScorer:
    """
    Compute a holistic confidence score for a single query pipeline run by
    combining signals from four sources.

    Score weights
    -------------
    Intent classification  — 30 %
    Semantic validation    — 35 %
    SQL validation         — 25 %
    Historical success rate — 10 %

    A score below 0.60 triggers a clarification request.
    """

    def score(
        self,
        intent_classification: dict[str, Any],
        semantic_validation: dict[str, Any],
        sql_validation: dict[str, Any],
        historical_success_rate: float | None = None,
    ) -> dict[str, Any]:
        intent_conf  = float(intent_classification.get("confidence")          or 0.50)
        semantic_conf = float(semantic_validation.get("semantic_confidence")  or 0.50)
        sql_valid    = sql_validation.get("sql_valid", True)
        sql_risk     = str(sql_validation.get("risk_level") or "low").lower()
        history      = float(historical_success_rate) if historical_success_rate is not None else 0.75

        sql_score = 1.0 if (sql_valid and sql_risk == "low") else (
            0.60 if sql_risk == "medium" else 0.20
        )

        composite = (
            intent_conf   * 0.30
            + semantic_conf * 0.35
            + sql_score     * 0.25
            + history       * 0.10
        )
        confidence_score = round(min(1.0, max(0.0, composite)), 2)

        # Clarification is needed when confidence is low OR the upstream
        # classifier / validator already flagged the query as ambiguous.
        clarification_needed = (
            confidence_score < 0.60
            or bool(intent_classification.get("clarification_needed"))
            or not bool(semantic_validation.get("overall_valid", True))
        )

        # Prefer the intent classifier's prompt; fall back to a validation hint.
        clarification_prompt: str | None = intent_classification.get("clarification_prompt")
        if not clarification_prompt and not semantic_validation.get("overall_valid", True):
            issues = semantic_validation.get("issues") or []
            if issues:
                clarification_prompt = (
                    f"I noticed a potential issue: {issues[0]}  "
                    f"Please refine your query or check the metric / dimension names."
                )

        return {
            "confidence_score": confidence_score,
            "breakdown": {
                "intent_confidence":   intent_conf,
                "semantic_confidence": semantic_conf,
                "sql_score":           sql_score,
                "history_score":       history,
            },
            "clarification_needed": clarification_needed,
            "clarification_prompt": clarification_prompt,
        }
