"""
VoxCore Insight Engine (VIE)
Converts SQL result sets into clear, actionable business insights.
"""

from typing import List, Dict, Any
import numpy as np
from voxcore.engine.insight_memory import InsightMemory

# Initialize global insight memory instance
insight_memory = InsightMemory()

def detect_growth(data: List[Dict[str, Any]], value_key: str) -> bool:
    values = [row[value_key] for row in data]
    return all(earlier <= later for earlier, later in zip(values, values[1:]))

def detect_decline(data: List[Dict[str, Any]], value_key: str) -> bool:
    values = [row[value_key] for row in data]
    return all(earlier >= later for earlier, later in zip(values, values[1:]))

def detect_spike(data: List[Dict[str, Any]], value_key: str, threshold: float = 2.0) -> List[int]:
    values = np.array([row[value_key] for row in data])
    avg = np.mean(values)
    spikes = [i for i, v in enumerate(values) if v > threshold * avg]
    return spikes

def detect_top_performer(data: List[Dict[str, Any]], value_key: str, top_n: int = 1) -> List[Dict[str, Any]]:
    return sorted(data, key=lambda x: x[value_key], reverse=True)[:top_n]

def detect_outlier(data: List[Dict[str, Any]], value_key: str, z_thresh: float = 2.5) -> List[int]:
    values = np.array([row[value_key] for row in data])
    mean = np.mean(values)
    std = np.std(values)
    return [i for i, v in enumerate(values) if abs(v - mean) > z_thresh * std]


# --- Insight Templates ---
INSIGHT_TEMPLATES = {
    "growth_trend": "{metric} increased {growth_percent}% over the last {period}.",
    "decline_trend": "{metric} declined {decline_percent}% in {region} during {period}.",
    "top_performers": "{entity} generated the highest {metric}, contributing {share}% of total.",
    "anomaly_detection": "Spike detected for {label} ({metric} = {value}).",
    "churn_risk": "{count} customers have not purchased in the past {window} days.",
    "seasonality": "{metric} shows seasonality with peaks in {period}.",
    "regional_comparison": "{region} generated the highest {metric}.",
    "product_ranking": "{entity} is a top product by {metric}.",
    "revenue_distribution": "{segment} accounts for {share}% of {metric}.",
    "emerging_segment": "{segment} is an emerging growth area for {metric}.",
}

# --- Chart Suggestions ---
CHART_SUGGESTIONS = {
    "growth_trend": {"chart": "line", "x_axis": "period", "y_axis": "metric"},
    "decline_trend": {"chart": "line", "x_axis": "period", "y_axis": "metric"},
    "top_performers": {"chart": "bar", "x_axis": "entity", "y_axis": "metric"},
    "anomaly_detection": {"chart": "line+marker", "x_axis": "period", "y_axis": "metric"},
    "churn_risk": {"chart": "bar", "x_axis": "customer", "y_axis": "last_active"},
    "seasonality": {"chart": "line", "x_axis": "period", "y_axis": "metric"},
    "regional_comparison": {"chart": "grouped_bar", "x_axis": "region", "y_axis": "metric"},
    "product_ranking": {"chart": "bar", "x_axis": "product", "y_axis": "metric"},
    "revenue_distribution": {"chart": "histogram", "x_axis": "segment", "y_axis": "metric"},
    "emerging_segment": {"chart": "line", "x_axis": "period", "y_axis": "metric"},
}

def score_insight(insight: dict) -> float:
    # Default weights: impact 0.4, trend_strength 0.3, rarity 0.2, confidence 0.1
    return (
        insight.get("impact", 0) * 0.4 +
        insight.get("trend_strength", 0) * 0.3 +
        insight.get("rarity", 0) * 0.2 +
        insight.get("confidence", 0) * 0.1
    )

def generate_insights(insight_type: str, data: List[Dict[str, Any]], *args) -> List[dict]:
    """
    Returns a list of structured insight dicts with narrative, score, and chart suggestion.
    """
    insights = []
    # Heuristic: try to infer keys
    value_key = None  # Ensure all metric names come from semantic registry only
    label_key = None  # Ensure all dimension names come from semantic registry only

    # Example: growth trend
    if insight_type == "growth_trend" and value_key:
        values = [row[value_key] for row in data]
        if len(values) > 1:
            growth = (values[-1] - values[0]) / max(values[0], 1e-6) * 100
            trend_strength = np.polyfit(range(len(values)), values, 1)[0]
            impact = abs(growth)
            rarity = 0.0
            confidence = 1.0 if trend_strength > 0 else 0.7
            narrative = INSIGHT_TEMPLATES[insight_type].format(
                metric=value_key.capitalize(),
                growth_percent=round(growth, 1),
                period=f"{len(values)} periods"
            )
            chart = CHART_SUGGESTIONS[insight_type]
            insight_obj = {
                "insight": narrative,
                "type": insight_type,
                "score": score_insight({"impact": impact, "trend_strength": trend_strength, "rarity": rarity, "confidence": confidence}),
                "impact": impact,
                "trend_strength": trend_strength,
                "rarity": rarity,
                "confidence": confidence,
                "chart": chart,
                "x_axis": chart["x_axis"],
                "y_axis": chart["y_axis"],
                "metric": value_key,
                "entity": None
            }
            insights.append(insight_obj)
            # Store in insight memory
            insight_memory.store_insight(insight_obj)
    # Example: decline trend
    elif insight_type == "decline_trend" and value_key:
        values = [row[value_key] for row in data]
        if len(values) > 1:
            decline = (values[0] - values[-1]) / max(values[0], 1e-6) * 100
            trend_strength = np.polyfit(range(len(values)), values, 1)[0]
            impact = abs(decline)
            rarity = 0.0
            confidence = 1.0 if trend_strength < 0 else 0.7
            narrative = INSIGHT_TEMPLATES[insight_type].format(
                metric=value_key.capitalize(),
                decline_percent=round(decline, 1),
                region="All",
                period=f"{len(values)} periods"
            )
            chart = CHART_SUGGESTIONS[insight_type]
            insight_obj = {
                "insight": narrative,
                "type": insight_type,
                "score": score_insight({"impact": impact, "trend_strength": trend_strength, "rarity": rarity, "confidence": confidence}),
                "impact": impact,
                "trend_strength": trend_strength,
                "rarity": rarity,
                "confidence": confidence,
                "chart": chart,
                "x_axis": chart["x_axis"],
                "y_axis": chart["y_axis"],
                "metric": value_key,
                "entity": None
            }
            insights.append(insight_obj)
            # Store in insight memory
            insight_memory.store_insight(insight_obj)
    # Example: top performers
    elif insight_type == "top_performers" and value_key and label_key:
        top = detect_top_performer(data, value_key, top_n=1)
        if top:
            entity = top[0][label_key]
            metric = value_key.capitalize()
            total = sum([row[value_key] for row in data])
            share = round(top[0][value_key] / max(total, 1e-6) * 100, 1)
            impact = share
            trend_strength = 0.0
            rarity = 0.0
            confidence = 1.0
            narrative = INSIGHT_TEMPLATES[insight_type].format(
                entity=entity,
                metric=metric,
                share=share
            )
            chart = CHART_SUGGESTIONS[insight_type]
            insight_obj = {
                "insight": narrative,
                "type": insight_type,
                "score": score_insight({"impact": impact, "trend_strength": trend_strength, "rarity": rarity, "confidence": confidence}),
                "impact": impact,
                "trend_strength": trend_strength,
                "rarity": rarity,
                "confidence": confidence,
                "chart": chart,
                "x_axis": chart["x_axis"],
                "y_axis": chart["y_axis"],
                "metric": value_key,
                "entity": entity
            }
            insights.append(insight_obj)
            # Store in insight memory
            insight_memory.store_insight(insight_obj)
            # Link to previous related insights (root cause chain)
            related = insight_memory.find_related_insights(metric=value_key)
            for prev in related:
                if prev is not insight_obj and prev.get("entity") != entity:
                    insight_memory.link_insights(parent=prev.get("insight"), child=insight_obj.get("insight"), relationship="related")
    # Example: anomaly detection
    elif insight_type == "anomaly_detection" and value_key and label_key:
        spikes = detect_spike(data, value_key)
        for i in spikes:
            label = data[i][label_key]
            value = data[i][value_key]
            impact = value
            trend_strength = 0.0
            rarity = 1.0
            confidence = 0.9
            narrative = INSIGHT_TEMPLATES[insight_type].format(
                label=label,
                metric=value_key.capitalize(),
                value=value
            )
            chart = CHART_SUGGESTIONS[insight_type]
            insights.append({
                "insight": narrative,
                "type": insight_type,
                "score": score_insight({"impact": impact, "trend_strength": trend_strength, "rarity": rarity, "confidence": confidence}),
                "impact": impact,
                "trend_strength": trend_strength,
                "rarity": rarity,
                "confidence": confidence,
                "chart": chart,
                "x_axis": chart["x_axis"],
                "y_axis": chart["y_axis"]
            })
    # Add more types as needed...
    return insights

if __name__ == "__main__":
    # Example: Trend detection
    data = [
        {"Month": "Jan", "Revenue": 900000},
        {"Month": "Feb", "Revenue": 950000},
        {"Month": "Mar", "Revenue": 1100000},
        {"Month": "Apr", "Revenue": 1250000},
    ]
    print(generate_insights(data, value_key="Revenue", label_key="Month"))
    # Example: Anomaly detection
    data2 = [
        {"Day": "Mon", "Revenue": 45000},
        {"Day": "Tue", "Revenue": 48000},
        {"Day": "Wed", "Revenue": 51000},
        {"Day": "Thu", "Revenue": 210000},
        {"Day": "Fri", "Revenue": 49000},
    ]
    print(generate_insights(data2, value_key="Revenue", label_key="Day"))
