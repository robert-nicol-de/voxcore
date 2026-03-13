from __future__ import annotations

from typing import Literal

EventType = Literal[
    "query_executed",
    "query_blocked",
    "policy_violation",
    "schema_change",
    "metric_anomaly",
    "insight_generated",
    "agent_alert",
]

QUERY_EXECUTED: EventType = "query_executed"
QUERY_BLOCKED: EventType = "query_blocked"
POLICY_VIOLATION: EventType = "policy_violation"
SCHEMA_CHANGE: EventType = "schema_change"
METRIC_ANOMALY: EventType = "metric_anomaly"
INSIGHT_GENERATED: EventType = "insight_generated"
AGENT_ALERT: EventType = "agent_alert"

ALL_EVENT_TYPES: tuple[EventType, ...] = (
    QUERY_EXECUTED,
    QUERY_BLOCKED,
    POLICY_VIOLATION,
    SCHEMA_CHANGE,
    METRIC_ANOMALY,
    INSIGHT_GENERATED,
    AGENT_ALERT,
)
