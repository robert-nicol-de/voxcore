from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ControlPlaneContext:
    operation: str
    company_id: str
    workspace_id: str
    user_id: int | None = None
    role: str | None = None
    datasource_id: str | None = None
    schema_name: str | None = None
    actor_type: str = "user"
    entrypoint: str = "api"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QueryRoutePlan:
    mode: str = "sync"
    semantic_brain: bool = True
    data_guardian: bool = True
    policy_engine: bool = True
    risk_engine: bool = True
    execution_guard: bool = True
    query_queue: bool = False
    agent_system: bool = False
    telemetry: bool = True

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
