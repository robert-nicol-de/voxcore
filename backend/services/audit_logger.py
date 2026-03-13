import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _audit_file() -> Path:
    path = Path("backend") / "logs" / "ai_query_audit.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def create_audit_query_id(prefix: str = "VCX") -> str:
    return f"{prefix}-{secrets.token_hex(4).upper()}"


def log_audit_event(event: Dict[str, Any]) -> None:
    payload = {
        "event_id": event.get("event_id") or secrets.token_hex(8),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    with _audit_file().open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def get_recent_audit_events(limit: int = 100) -> List[Dict[str, Any]]:
    path = _audit_file()
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    recent = lines[-limit:]
    events: List[Dict[str, Any]] = []
    for line in reversed(recent):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    return events
