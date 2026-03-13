"""
backend/agents — AI Data Agents package.

Persistent analytical services that continuously monitor data and surface
insights, anomalies, and risks automatically.
"""
from .insight_agent import run as run_insight
from .anomaly_agent import run as run_anomaly
from .risk_agent import run as run_risk
from .schema_agent import run as run_schema

__all__ = ["run_insight", "run_anomaly", "run_risk", "run_schema"]
