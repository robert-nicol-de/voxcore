import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _audit_file() -> Path:
    path = Path("backend") / "logs" / "ai_query_audit.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def log_audit_event(event: Dict[str, Any]) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    with _audit_file().open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
