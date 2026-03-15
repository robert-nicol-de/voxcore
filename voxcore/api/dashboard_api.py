"""
VoxCore Data Intelligence Dashboard API (VID)
Provides endpoints for live insights, anomalies, trends, root cause chains, and exploration suggestions.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import List

from voxcore.engine.insight_engine import generate_insights
from voxcore.engine.insight_memory import InsightMemory
from voxcore.engine.exploration_engine import generate_related_queries
# from voxcore.engine.proactive_insight_system import get_proactive_anomalies, get_proactive_trends

app = FastAPI()
insight_memory = InsightMemory()

@app.get("/api/insights/latest")
def get_latest_insights():
    """Return the most recent insights from Explain My Data, Proactive Insight System, and user queries."""
    # Example: Pull last 10 insights from memory
    latest = insight_memory.insights[-10:]
    return {"insights": latest[::-1]}

@app.get("/api/insights/anomalies")
def get_anomalies():
    """Return detected anomalies (from Proactive Insight System or memory)."""
    # Placeholder: filter for type == 'anomaly_detection'
    anomalies = [i for i in insight_memory.insights if i.get("type") == "anomaly_detection"]
    return {"anomalies": anomalies[::-1]}

@app.get("/api/insights/trends")
def get_trends():
    """Return detected trends (from Insight Engine or memory)."""
    trends = [i for i in insight_memory.insights if "trend" in (i.get("type") or "")]
    return {"trends": trends[::-1]}

@app.get("/api/insights/root_causes")
def get_root_causes():
    """Return root cause chains from Insight Memory relationships."""
    # Return as a list of edges for graph visualization
    return {"root_causes": insight_memory.relationships}

@app.get("/api/exploration/suggestions")
def get_exploration_suggestions():
    """Return exploration suggestions from the Exploration Engine."""
    # Example: Use a default query plan for demo
    query_plan = {"metric": "revenue"}
    suggestions = generate_related_queries(query_plan)
    return {"suggestions": suggestions}

# Example: To run with uvicorn
# uvicorn voxcore.api.dashboard_api:app --reload
