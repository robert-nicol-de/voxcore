"""
VoxCore Insight Engine (VIE)
Converts SQL result sets into clear, actionable business insights.

PLAYGROUND SCOPE: Exposes only 4 stable insight types.
- growth_trend: Positive trend detection
- decline_trend: Negative trend detection
- top_performers: Leader identification
- anomaly_detection: Spike/outlier detection

All other insight types are reserved for future implementation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np
from voxcore.engine.insight_memory import InsightMemory

# Initialize global insight memory instance
insight_memory = InsightMemory()

# ============================================================================
# DETECTION HELPERS
# ============================================================================

def detect_growth(data: List[Dict[str, Any]], value_key: str) -> bool:
    """Check if all values are monotonically increasing"""
    if not data or len(data) < 2:
        return False
    values = [row[value_key] for row in data]
    return all(earlier <= later for earlier, later in zip(values, values[1:]))


def detect_decline(data: List[Dict[str, Any]], value_key: str) -> bool:
    """Check if all values are monotonically decreasing"""
    if not data or len(data) < 2:
        return False
    values = [row[value_key] for row in data]
    return all(earlier >= later for earlier, later in zip(values, values[1:]))


def detect_spike(data: List[Dict[str, Any]], value_key: str, threshold: float = 2.0) -> List[int]:
    """Detect values that exceed mean by threshold multiplier"""
    if not data:
        return []
    values = np.array([row[value_key] for row in data])
    avg = np.mean(values)
    if avg == 0:
        return []
    spikes = [i for i, v in enumerate(values) if v > threshold * avg]
    return spikes


def detect_top_performer(data: List[Dict[str, Any]], value_key: str, top_n: int = 1) -> List[Dict[str, Any]]:
    """Return top N rows sorted by value_key"""
    if not data:
        return []
    return sorted(data, key=lambda x: x.get(value_key, 0), reverse=True)[:top_n]


def detect_outlier(data: List[Dict[str, Any]], value_key: str, z_thresh: float = 2.5) -> List[int]:
    """Detect statistical outliers using z-score"""
    if not data or len(data) < 2:
        return []
    values = np.array([row[value_key] for row in data])
    mean = np.mean(values)
    std = np.std(values)
    if std == 0:
        return []
    return [i for i, v in enumerate(values) if abs(v - mean) > z_thresh * std]


# ============================================================================
# STABLE INSIGHT TEMPLATES (EXPOSED TO PLAYGROUND)
# ============================================================================

INSIGHT_TEMPLATES = {
    "growth_trend": "{metric} increased {growth_percent}% over {period}.",
    "decline_trend": "{metric} declined {decline_percent}% in {region} during {period}.",
    "top_performers": "{entity} generated the highest {metric}, contributing {share}% of total.",
    "anomaly_detection": "Spike detected for {label} ({metric} = {value}).",
}

# ============================================================================
# STANDARDIZED CHART METADATA (FOR FRONTEND)
# ============================================================================

CHART_SUGGESTIONS = {
    "growth_trend": {
        "type": "line",
        "x_axis_key": "period",
        "y_axis_key": "metric",
        "title": "Growth Trend",
    },
    "decline_trend": {
        "type": "line",
        "x_axis_key": "period",
        "y_axis_key": "metric",
        "title": "Decline Trend",
    },
    "top_performers": {
        "type": "bar",
        "x_axis_key": "entity",
        "y_axis_key": "metric",
        "title": "Top Performers",
    },
    "anomaly_detection": {
        "type": "line+marker",
        "x_axis_key": "period",
        "y_axis_key": "metric",
        "title": "Anomaly Detection",
    },
}


# ============================================================================
# INSIGHT DATACLASSES
# ============================================================================

@dataclass
class InsightData:
    """Structured insight with all scoring and metadata"""
    insight_type: str  # "growth_trend" | "decline_trend" | "top_performers" | "anomaly_detection"
    narrative: str  # Human-readable insight description
    score: float  # 0.0-100.0 overall insight quality score
    confidence: float  # 0.0-1.0 confidence in this insight
    impact: float  # 0.0-100.0 business impact (contribution, growth %, etc.)
    trend_strength: float  # -1.0 to 1.0 linear trend coefficient (for trend insights)
    rarity: float  # 0.0-1.0 how unusual this insight is (0=common, 1=rare)
    chart: Dict[str, Any]  # Chart metadata: type, x_axis_key, y_axis_key, title
    metric: str  # The metric name (e.g., "Revenue")
    entity: Optional[str] = None  # The entity if multi-dimensional (e.g., "EMEA", "Product A")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-safe dictionary"""
        return {
            "type": self.insight_type,
            "insight": self.narrative,
            "score": round(self.score, 2),
            "confidence": round(self.confidence, 2),
            "impact": round(self.impact, 2),
            "trend_strength": round(self.trend_strength, 2),
            "rarity": round(self.rarity, 2),
            "chart": self.chart,
            "metric": self.metric,
            "entity": self.entity,
        }


@dataclass
class EMDCard:
    """Lightweight preview card for Playground EMD display"""
    title: str  # Short title (e.g., "Revenue Growth")
    insight: str  # One-liner narrative
    score: float  # 0.0-100.0 overall insight quality
    confidence: float  # 0.0-1.0 confidence
    chart: Dict[str, Any]  # Standardized chart metadata (type, x_axis_key, y_axis_key, title)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            "title": self.title,
            "insight": self.insight,
            "score": round(self.score, 2),
            "confidence": round(self.confidence, 2),
            "chart": self.chart,
        }


# ============================================================================
# SCORING ENGINE
# ============================================================================

def score_insight(
    impact: float,
    trend_strength: float,
    confidence: float,
    rarity: float = 0.0,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate overall insight score (0-100).
    
    Weights (default):
    - impact: 0.4 (business value)
    - confidence: 0.3 (statistical confidence)
    - trend_strength: 0.2 (trend clarity)
    - rarity: 0.1 (uniqueness)
    
    Args:
        impact: 0-100 (business impact percentage)
        trend_strength: -1.0 to 1.0 (linear trend)
        confidence: 0-1.0 (statistical confidence)
        rarity: 0-1.0 (how unusual)
        weights: Custom weight dict
    
    Returns:
        score: 0-100
    """
    if weights is None:
        weights = {
            "impact": 0.4,
            "confidence": 0.3,
            "trend_strength": 0.2,
            "rarity": 0.1,
        }
    
    # Normalize inputs
    impact_norm = min(abs(impact) / 100.0, 1.0)  # Cap at 1.0
    trend_norm = abs(trend_strength)  # Already -1 to 1
    confidence_norm = min(confidence, 1.0)  # Already 0-1
    rarity_norm = min(rarity, 1.0)  # Already 0-1
    
    # Weighted score
    score = (
        impact_norm * weights["impact"] +
        confidence_norm * weights["confidence"] +
        trend_norm * weights["trend_strength"] +
        rarity_norm * weights["rarity"]
    )
    
    # Scale to 0-100
    return score * 100.0


# ============================================================================
# INSIGHT GENERATION (STABLE TYPES ONLY)
# ============================================================================

def generate_insights(
    insight_type: str,
    data: List[Dict[str, Any]],
    value_key: str,
    label_key: Optional[str] = None,
    period_label: str = "period"
) -> List[InsightData]:
    """
    Generate high-quality insights from query result data.
    
    Exposed types:
    - growth_trend: Monotonic increase detection
    - decline_trend: Monotonic decrease detection
    - top_performers: Top N by metric
    - anomaly_detection: Statistical spikes
    
    Args:
        insight_type: Type of insight to generate
        data: List of dicts (query result rows)
        value_key: The numeric metric column name
        label_key: The dimension/category column name (required for top_performers, anomaly_detection)
        period_label: Label for time axis (default "period")
    
    Returns:
        List of InsightData objects (structured, scored, ready for Playground)
    """
    
    if not data or insight_type not in INSIGHT_TEMPLATES:
        return []
    
    insights = []
    
    # ---- GROWTH TREND ----
    if insight_type == "growth_trend":
        values = [row.get(value_key, 0) for row in data]
        if len(values) > 1 and min(values) >= 0:
            growth_pct = ((values[-1] - values[0]) / max(abs(values[0]), 1e-6)) * 100
            trend_strength = float(np.polyfit(range(len(values)), values, 1)[0]) / max(abs(values[-1]), 1)
            
            # Only return if actually positive
            if growth_pct > 0:
                narrative = INSIGHT_TEMPLATES["growth_trend"].format(
                    metric=value_key.capitalize(),
                    growth_percent=round(growth_pct, 1),
                    period=f"{len(values)} {period_label}s"
                )
                
                impact = min(abs(growth_pct), 100.0)
                confidence = 0.95 if trend_strength > 0.01 else 0.7
                score = score_insight(impact, trend_strength, confidence, rarity=0.0)
                
                insight = InsightData(
                    insight_type="growth_trend",
                    narrative=narrative,
                    score=score,
                    confidence=confidence,
                    impact=impact,
                    trend_strength=trend_strength,
                    rarity=0.0,
                    chart=CHART_SUGGESTIONS["growth_trend"].copy(),
                    metric=value_key,
                    entity=None
                )
                insights.append(insight)
                insight_memory.store_insight(insight.to_dict(), score)
    
    # ---- DECLINE TREND ----
    elif insight_type == "decline_trend":
        values = [row.get(value_key, 0) for row in data]
        if len(values) > 1 and min(values) >= 0:
            decline_pct = ((values[0] - values[-1]) / max(abs(values[0]), 1e-6)) * 100
            trend_strength = float(np.polyfit(range(len(values)), values, 1)[0]) / max(abs(values[0]), 1)
            
            # Only return if actually negative
            if decline_pct > 0:
                narrative = INSIGHT_TEMPLATES["decline_trend"].format(
                    metric=value_key.capitalize(),
                    decline_percent=round(decline_pct, 1),
                    region="overall",
                    period=f"{len(values)} {period_label}s"
                )
                
                impact = min(abs(decline_pct), 100.0)
                confidence = 0.95 if trend_strength < -0.01 else 0.7
                score = score_insight(impact, abs(trend_strength), confidence, rarity=0.0)
                
                insight = InsightData(
                    insight_type="decline_trend",
                    narrative=narrative,
                    score=score,
                    confidence=confidence,
                    impact=impact,
                    trend_strength=trend_strength,
                    rarity=0.0,
                    chart=CHART_SUGGESTIONS["decline_trend"].copy(),
                    metric=value_key,
                    entity=None
                )
                insights.append(insight)
                insight_memory.store_insight(insight.to_dict(), score)
    
    # ---- TOP PERFORMERS ----
    elif insight_type == "top_performers":
        if not label_key:
            return []
        
        top = detect_top_performer(data, value_key, top_n=1)
        if top:
            entity = str(top[0].get(label_key, "Unknown"))
            total = sum([row.get(value_key, 0) for row in data])
            if total > 0:
                share_pct = (top[0].get(value_key, 0) / total) * 100
                
                narrative = INSIGHT_TEMPLATES["top_performers"].format(
                    entity=entity,
                    metric=value_key.capitalize(),
                    share=round(share_pct, 1)
                )
                
                impact = min(share_pct, 100.0)
                confidence = 1.0
                score = score_insight(impact, 0.0, confidence, rarity=0.1)
                
                insight = InsightData(
                    insight_type="top_performers",
                    narrative=narrative,
                    score=score,
                    confidence=confidence,
                    impact=impact,
                    trend_strength=0.0,
                    rarity=0.1,
                    chart=CHART_SUGGESTIONS["top_performers"].copy(),
                    metric=value_key,
                    entity=entity
                )
                insights.append(insight)
                insight_memory.store_insight(insight.to_dict(), score)
    
    # ---- ANOMALY DETECTION ----
    elif insight_type == "anomaly_detection":
        if not label_key:
            return []
        
        spikes = detect_spike(data, value_key, threshold=2.0)
        for idx in spikes[:3]:  # Limit to top 3 anomalies
            label = str(data[idx].get(label_key, "Unknown"))
            value = data[idx].get(value_key, 0)
            
            narrative = INSIGHT_TEMPLATES["anomaly_detection"].format(
                label=label,
                metric=value_key.capitalize(),
                value=round(value, 2) if isinstance(value, float) else value
            )
            
            impact = min(abs(value) / max([row.get(value_key, 1) for row in data], 1), 100.0) * 50
            confidence = 0.9
            rarity = 0.8
            score = score_insight(impact, 0.0, confidence, rarity=rarity)
            
            insight = InsightData(
                insight_type="anomaly_detection",
                narrative=narrative,
                score=score,
                confidence=confidence,
                impact=impact,
                trend_strength=0.0,
                rarity=rarity,
                chart=CHART_SUGGESTIONS["anomaly_detection"].copy(),
                metric=value_key,
                entity=label
            )
            insights.append(insight)
            insight_memory.store_insight(insight.to_dict(), score)
    
    return insights


# ============================================================================
# PLAYGROUND EMD PREVIEW HELPER
# ============================================================================

def convert_insights_to_emd_cards(insights: List[InsightData]) -> List[EMDCard]:
    """
    Convert full insight objects to lightweight EMD preview cards.
    
    EMD = Executive Metrics Dashboard
    Cards are ready for Playground rendering (2-4 per dashboard).
    
    Args:
        insights: List of InsightData objects (from generate_insights)
    
    Returns:
        List of EMDCard objects (title, insight, score, confidence, chart)
    """
    cards = []
    
    for insight in insights:
        # Generate title based on type
        if insight.insight_type == "growth_trend":
            title = f"{insight.metric} Growth"
        elif insight.insight_type == "decline_trend":
            title = f"{insight.metric} Decline"
        elif insight.insight_type == "top_performers":
            title = f"Leader: {insight.entity}"
        elif insight.insight_type == "anomaly_detection":
            title = f"Anomaly: {insight.entity}"
        else:
            title = f"{insight.insight_type}"
        
        card = EMDCard(
            title=title,
            insight=insight.narrative,
            score=insight.score,
            confidence=insight.confidence,
            chart=insight.chart
        )
        cards.append(card)
    
    return cards


def generate_emd_preview(
    insight_type: str,
    data: List[Dict[str, Any]],
    value_key: str,
    label_key: Optional[str] = None,
    period_label: str = "period"
) -> List[EMDCard]:
    """
    All-in-one helper: Generate insights and convert to EMD cards.
    
    Perfect for Playground dashboard rendering.
    Returns 0-4 lightweight cards ready for UI consumption.
    
    Args:
        insight_type: Type of insight (growth_trend, decline_trend, top_performers, anomaly_detection)
        data: Query result rows
        value_key: Metric column name
        label_key: Dimension column name (optional)
        period_label: Label for time axis
    
    Returns:
        List of EMDCard objects (0-4 cards)
    """
    insights = generate_insights(insight_type, data, value_key, label_key, period_label)
    cards = convert_insights_to_emd_cards(insights)
    return cards[:4]  # Cap at 4 cards for Playground


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example 1: Growth Trend Detection
    print("=" * 60)
    print("EXAMPLE 1: Growth Trend")
    print("=" * 60)
    data_growth = [
        {"Month": "Jan", "Revenue": 900000},
        {"Month": "Feb", "Revenue": 950000},
        {"Month": "Mar", "Revenue": 1100000},
        {"Month": "Apr", "Revenue": 1250000},
    ]
    insights = generate_insights(
        insight_type="growth_trend",
        data=data_growth,
        value_key="Revenue",
        label_key="Month",
        period_label="month"
    )
    for insight in insights:
        print(f"Narrative: {insight.narrative}")
        print(f"Score: {insight.score:.2f}")
        print(f"Confidence: {insight.confidence:.2f}")
        print(f"Impact: {insight.impact:.2f}%")
        print(f"Chart Type: {insight.chart['type']}")
    
    # Example 2: EMD Preview Cards (Playground)
    print("\n" + "=" * 60)
    print("EXAMPLE 2: EMD Preview Cards")
    print("=" * 60)
    cards = generate_emd_preview(
        insight_type="growth_trend",
        data=data_growth,
        value_key="Revenue",
        period_label="month"
    )
    for card in cards:
        print(f"Title: {card.title}")
        print(f"Insight: {card.insight}")
        print(f"Score: {card.score:.2f}")
        print(f"Confidence: {card.confidence:.2f}")
        print()
    
    # Example 3: Anomaly Detection
    print("=" * 60)
    print("EXAMPLE 3: Anomaly Detection")
    print("=" * 60)
    data_anomaly = [
        {"Day": "Mon", "Revenue": 45000},
        {"Day": "Tue", "Revenue": 48000},
        {"Day": "Wed", "Revenue": 51000},
        {"Day": "Thu", "Revenue": 210000},  # SPIKE
        {"Day": "Fri", "Revenue": 49000},
    ]
    insights = generate_insights(
        insight_type="anomaly_detection",
        data=data_anomaly,
        value_key="Revenue",
        label_key="Day",
        period_label="day"
    )
    for insight in insights:
        print(f"Narrative: {insight.narrative}")
        print(f"Score: {insight.score:.2f}")
        print()

