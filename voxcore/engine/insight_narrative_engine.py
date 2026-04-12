"""
VoxCore Insight Narrative Engine

Converts technical outputs and root cause chains into executive-grade, 
structured narratives. Every insight gets a headline, summary, and next step.

No hype. No developer phrasing. Calm, operational, premium.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, Dict, List


class ToneStyle(str, Enum):
    """Narrative tone for different contexts"""
    EXECUTIVE = "executive"  # C-suite, strategic
    OPERATIONAL = "operational"  # Team leads, tactical
    ANALYTICAL = "analytical"  # Data teams, technical but clear


@dataclass
class Narrative:
    """
    Structured narrative output for insights.
    
    Designed to be rendered directly into UI:
    - headline: Show as hero insight (1 line)
    - summary: Show as expanded explanation (2-3 lines)
    - next_step: Show as suggested action (1 line)
    - tone: Hints at how to render (style, icon, color)
    """
    
    # Three-layer structure
    headline: str  # One-liner hero insight (e.g., "Revenue declined 12% in Q4")
    summary: str  # Expanded explanation (2-3 sentences, max 150 chars)
    next_step: str  # Suggested action (e.g., "Drill into regional breakdown")
    
    # Context
    insight_type: str  # "trend_increase" | "trend_decline" | "top_performer" | etc.
    tone: ToneStyle = ToneStyle.EXECUTIVE
    
    # Optional enrichment
    confidence: float = 1.0  # 0.0-1.0 confidence in this narrative
    keywords: List[str] = field(default_factory=list)  # For search/filtering
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            "headline": self.headline,
            "summary": self.summary,
            "next_step": self.next_step,
            "insight_type": self.insight_type,
            "tone": self.tone.value,
            "confidence": self.confidence,
            "keywords": self.keywords,
        }


# ============================================================================
# NARRATIVE TEMPLATES (EXECUTIVE-GRADE)
# ============================================================================

class NarrativeTemplate:
    """Base template for generating narratives"""
    
    @staticmethod
    def trend_increase(
        metric: str,
        percent_change: float,
        entity: str = None,
        period: str = None,
        confidence: float = 1.0
    ) -> Narrative:
        """
        Positive trend template.
        
        Example:
            metric="Revenue", percent_change=15, entity="EMEA", period="Q4 2024"
        """
        entity_phrase = f"in {entity}" if entity else "overall"
        period_phrase = f"during {period}" if period else "this period"
        
        metric_lower = metric.lower()
        pct_str = f"{abs(percent_change):.1f}%" if isinstance(percent_change, (int, float)) else str(percent_change)
        
        return Narrative(
            headline=f"{metric} increased {pct_str} {entity_phrase}",
            summary=f"{metric} showed positive momentum {entity_phrase} {period_phrase}, with {pct_str} growth. This aligns with expected seasonal patterns and operational improvements.",
            next_step=f"Review drivers of growth in {entity or metric_lower}",
            insight_type="trend_increase",
            tone=ToneStyle.EXECUTIVE,
            confidence=confidence,
            keywords=[metric_lower, "growth", "increase", (entity or "").lower()],
        )
    
    @staticmethod
    def trend_decline(
        metric: str,
        percent_change: float,
        entity: str = None,
        period: str = None,
        severity: str = "moderate",
        confidence: float = 1.0
    ) -> Narrative:
        """
        Negative trend template with severity awareness.
        
        Example:
            metric="Revenue", percent_change=-12, entity="APAC", period="Q4 2024", severity="moderate"
        """
        entity_phrase = f"in {entity}" if entity else "overall"
        period_phrase = f"during {period}" if period else "this period"
        metric_lower = metric.lower()
        pct_str = f"{abs(percent_change):.1f}%" if isinstance(percent_change, (int, float)) else str(percent_change)
        
        # Severity-aware wording
        severity_map = {
            "low": ("slight decline", "monitoring recommended"),
            "moderate": ("notable decline", "investigation recommended"),
            "high": ("significant decline", "requires immediate action"),
        }
        
        decline_verb, next_action = severity_map.get(severity.lower(), ("decline", "review"))
        
        return Narrative(
            headline=f"{metric} declined {pct_str} {entity_phrase}",
            summary=f"{metric} showed a {decline_verb} {entity_phrase} {period_phrase}. Contributing factors should be analyzed to determine if this is temporary or part of a larger trend.",
            next_step=f"{next_action} — drill into factors affecting {entity or metric_lower}",
            insight_type="trend_decline",
            tone=ToneStyle.OPERATIONAL,
            confidence=confidence,
            keywords=[metric_lower, "decline", "decrease", (entity or "").lower()],
        )
    
    @staticmethod
    def top_performer(
        metric: str,
        entity: str,
        value: Any = None,
        rank: Optional[int] = None,
        confidence: float = 1.0
    ) -> Narrative:
        """
        Top performer template for winners and leaders.
        
        Example:
            metric="Revenue", entity="North America", value=2100000, rank=1
        """
        rank_phrase = f"(Rank #{rank})" if rank else ""
        value_phrase = f"at ${value:,.0f}" if isinstance(value, (int, float)) else f"at {value}" if value else ""
        metric_lower = metric.lower()
        entity_lower = entity.lower()
        
        return Narrative(
            headline=f"{entity} leads in {metric} {rank_phrase}",
            summary=f"{entity} generated the highest {metric_lower} {value_phrase}. This segment demonstrates strong market position and operational effectiveness. Performance is worth replicating across other regions.",
            next_step=f"Analyze success factors in {entity_lower} for broader application",
            insight_type="top_performer",
            tone=ToneStyle.EXECUTIVE,
            confidence=confidence,
            keywords=[metric_lower, "leader", "top", entity_lower, "best"],
        )
    
    @staticmethod
    def root_cause(
        cause: str,
        entity: str = None,
        impact_metric: str = None,
        impact_percent: float = None,
        recommendation: str = None,
        confidence: float = 0.8
    ) -> Narrative:
        """
        Root cause analysis template.
        
        Example:
            cause="Customer churn increased post-outage", entity="EMEA", 
            impact_metric="Revenue", impact_percent=-8, 
            recommendation="Implement SLA improvements"
        """
        entity_phrase = f" impacting {entity}" if entity else ""
        impact_phrase = f" contributing to {impact_percent:.1f}% of the change in {impact_metric.lower()}" if impact_metric and impact_percent else ""
        
        # Build recommendation phrasing
        rec_phrase = f"Recommended action: {recommendation}." if recommendation else "Recommended action: Address identified factor."
        
        return Narrative(
            headline=f"Root cause identified: {cause}",
            summary=f"{cause}{entity_phrase}{impact_phrase}. This factor appears to be the primary driver of the observed change and should be addressed to restore normal performance.",
            next_step=f"{rec_phrase} Implement mitigation and monitor improvement.",
            insight_type="root_cause",
            tone=ToneStyle.OPERATIONAL,
            confidence=confidence,
            keywords=["root_cause", "analysis", "cause", cause.lower()],
        )
    
    @staticmethod
    def explain_data_summary(
        table_name: str,
        row_count: int,
        key_metrics: List[str] = None,
        time_range: str = None,
        confidence: float = 1.0
    ) -> Narrative:
        """
        Data discovery/explain template.
        
        Example:
            table_name="Sales", row_count=245000, 
            key_metrics=["Revenue", "Orders", "Customer Count"],
            time_range="36 months rolling"
        """
        key_metrics = key_metrics or []
        table_lower = table_name.lower()
        
        metrics_phrase = f"Track {', '.join(key_metrics)}." if key_metrics else ""
        time_phrase = f"Data spans {time_range}." if time_range else ""
        
        return Narrative(
            headline=f"Dataset overview: {table_name} table",
            summary=f"This dataset contains {row_count:,} records covering transactional and organizational data. {metrics_phrase} {time_phrase} All data has been validated and is ready for analysis.",
            next_step=f"Begin exploration — start with total {key_metrics[0].lower()} by region or product",
            insight_type="explain_data_summary",
            tone=ToneStyle.ANALYTICAL,
            confidence=confidence,
            keywords=["dataset", "overview", table_lower, "discovery"],
        )
    
    @staticmethod
    def exploration_suggestion(
        current_metric: str,
        suggested_dimension: str,
        reason: str = None,
        confidence: float = 0.85
    ) -> Narrative:
        """
        Exploration path suggestion template.
        
        Example:
            current_metric="Revenue", suggested_dimension="Product Category",
            reason="To identify category-level performance drivers"
        """
        metric_lower = current_metric.lower()
        dim_lower = suggested_dimension.lower()
        
        reason_phrase = f"This provides visibility into {reason.lower()}." if reason else "This provides deeper visibility."
        
        return Narrative(
            headline=f"Explore {metric_lower} by {suggested_dimension}",
            summary=f"Breaking down {metric_lower} by {dim_lower} will reveal concentration and distribution patterns. {reason_phrase}",
            next_step=f"Run analysis: {current_metric} grouped by {suggested_dimension}",
            insight_type="exploration_suggestion",
            tone=ToneStyle.ANALYTICAL,
            confidence=confidence,
            keywords=[metric_lower, "explore", "breakdown", dim_lower],
        )
    
    @staticmethod
    def comparison_insight(
        metric: str,
        group_a: str,
        group_b: str,
        difference_percent: float,
        winner: str = None,
        confidence: float = 1.0
    ) -> Narrative:
        """
        Comparison/benchmark template.
        
        Example:
            metric="Margin", group_a="Product A", group_b="Product B",
            difference_percent=18, winner="Product A"
        """
        metric_lower = metric.lower()
        diff_str = f"{abs(difference_percent):.1f}%" if isinstance(difference_percent, (int, float)) else str(difference_percent)
        
        winner_phrase = f"{winner} outperforms" if winner else "First group outperforms"
        
        return Narrative(
            headline=f"{metric} gap: {diff_str} between {group_a} and {group_b}",
            summary=f"{winner_phrase} {group_b} in {metric_lower} by {diff_str}. This variance warrants investigation to determine if it reflects pricing, efficiency, or market conditions.",
            next_step=f"Deep dive into operational differences between {group_a} and {group_b}",
            insight_type="comparison_insight",
            tone=ToneStyle.OPERATIONAL,
            confidence=confidence,
            keywords=[metric_lower, "comparison", "gap", group_a.lower(), group_b.lower()],
        )


# ============================================================================
# INSIGHT NARRATIVE ENGINE
# ============================================================================

class InsightNarrativeEngine:
    """
    Generates executive-grade narratives from structured insights.
    
    Transforms technical insight data into clear, actionable narratives.
    Output is always a structured Narrative object, never a flat string.
    """
    
    def generate(self, insight: Dict[str, Any]) -> Narrative:
        """
        Generate narrative from insight data.
        
        Args:
            insight: Dict with 'type', 'metric', 'entity', etc.
        
        Returns:
            Narrative object with headline, summary, next_step
        """
        
        insight_type = insight.get("type", "unknown")
        confidence = insight.get("confidence", 1.0)
        
        # Route to appropriate template
        if insight_type == "trend_increase":
            return NarrativeTemplate.trend_increase(
                metric=insight.get("metric", "Metric"),
                percent_change=insight.get("percent_change", 0),
                entity=insight.get("entity"),
                period=insight.get("period"),
                confidence=confidence,
            )
        
        elif insight_type == "trend_decline":
            return NarrativeTemplate.trend_decline(
                metric=insight.get("metric", "Metric"),
                percent_change=insight.get("percent_change", 0),
                entity=insight.get("entity"),
                period=insight.get("period"),
                severity=insight.get("severity", "moderate"),
                confidence=confidence,
            )
        
        elif insight_type == "top_performer":
            return NarrativeTemplate.top_performer(
                metric=insight.get("metric", "Metric"),
                entity=insight.get("entity", "Entity"),
                value=insight.get("value"),
                rank=insight.get("rank"),
                confidence=confidence,
            )
        
        elif insight_type == "root_cause":
            return NarrativeTemplate.root_cause(
                cause=insight.get("cause", "Unknown factor"),
                entity=insight.get("entity"),
                impact_metric=insight.get("impact_metric"),
                impact_percent=insight.get("impact_percent"),
                recommendation=insight.get("recommendation"),
                confidence=confidence,
            )
        
        elif insight_type == "explain_data_summary":
            return NarrativeTemplate.explain_data_summary(
                table_name=insight.get("table_name", "Dataset"),
                row_count=insight.get("row_count", 0),
                key_metrics=insight.get("key_metrics"),
                time_range=insight.get("time_range"),
                confidence=confidence,
            )
        
        elif insight_type == "exploration_suggestion":
            return NarrativeTemplate.exploration_suggestion(
                current_metric=insight.get("metric", "Metric"),
                suggested_dimension=insight.get("dimension", "Dimension"),
                reason=insight.get("reason"),
                confidence=confidence,
            )
        
        elif insight_type == "comparison_insight":
            return NarrativeTemplate.comparison_insight(
                metric=insight.get("metric", "Metric"),
                group_a=insight.get("group_a", "Group A"),
                group_b=insight.get("group_b", "Group B"),
                difference_percent=insight.get("difference_percent", 0),
                winner=insight.get("winner"),
                confidence=confidence,
            )
        
        else:
            # Fallback for unknown types
            return Narrative(
                headline="Insight detected",
                summary="Analysis complete. Review the data above for patterns and opportunities.",
                next_step="Consider drilling deeper into specific dimensions or time periods",
                insight_type="unknown",
                tone=ToneStyle.ANALYTICAL,
                confidence=0.5,
            )
    
    @staticmethod
    def generate_headline_only(insight: Dict[str, Any]) -> str:
        """
        Quick helper to get just the headline string (for backward compat).
        
        Example:
            headline = engine.generate_headline_only({"type": "trend_decline", ...})
            # Returns: "Revenue declined 12% in APAC"
        """
        narrative = InsightNarrativeEngine().generate(insight)
        return narrative.headline
