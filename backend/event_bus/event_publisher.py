from __future__ import annotations

import json
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from .event_consumer import registry
from .event_types import ALL_EVENT_TYPES, EventType

_MAX_EVENTS = 500
_recent_events: deque[dict[str, Any]] = deque(maxlen=_MAX_EVENTS)
_lock = Lock()


def _events_file() -> Path:
    path = Path("backend") / "logs" / "intelligence_bus_events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def publish_event(
    event_type: EventType,
    payload: dict[str, Any],
    org_id: int | str | None = None,
    workspace_id: int | str | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    """Publish an event to the in-process intelligence bus and append to JSONL log."""
    if event_type not in ALL_EVENT_TYPES:
        raise ValueError(f"Unsupported event_type: {event_type}")

    event = {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "org_id": str(org_id) if org_id is not None else None,
        "workspace_id": str(workspace_id) if workspace_id is not None else None,
        "source": source or "voxcore",
        "payload": payload or {},
    }

    with _lock:
        _recent_events.appendleft(event)
        with _events_file().open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    registry.dispatch(event)
    return event


def recent_events(
    limit: int = 50,
    org_id: int | str | None = None,
    workspace_id: int | str | None = None,
    event_type: str | None = None,
) -> list[dict[str, Any]]:
    """Return recent events from the in-memory stream, newest first."""
    safe_limit = max(1, min(500, int(limit or 50)))
    with _lock:
        events = list(_recent_events)

    if len(events) < safe_limit:
        try:
            lines = _events_file().read_text(encoding="utf-8").splitlines()
            file_events: list[dict[str, Any]] = []
            for line in reversed(lines[-1000:]):
                line = line.strip()
                if not line:
                    continue
                try:
                    file_events.append(json.loads(line))
                except Exception:
                    continue
            seen = {str(e.get("id")) for e in events}
            for evt in file_events:
                evt_id = str(evt.get("id"))
                if evt_id not in seen:
                    events.append(evt)
                    seen.add(evt_id)
        except Exception:
            pass

    if org_id is not None:
        events = [e for e in events if e.get("org_id") in {None, str(org_id)}]
    if workspace_id is not None:
        events = [e for e in events if e.get("workspace_id") in {None, str(workspace_id)}]
    if event_type:
        events = [e for e in events if e.get("event_type") == event_type]

    return events[:safe_limit]
