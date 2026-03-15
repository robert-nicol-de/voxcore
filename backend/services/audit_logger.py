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

# --- Compliance Log Retention and Export Utilities ---
def rotate_audit_log(max_size_mb: int = 50) -> None:
    """
    Rotate the audit log file if it exceeds max_size_mb (default 50MB).
    Archives the current log with a timestamp and starts a new one.
    """
    path = _audit_file()
    if not path.exists():
        return
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb < max_size_mb:
        return
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_path = path.parent / f"ai_query_audit_{timestamp}.jsonl"
    path.rename(archive_path)
    # Create a new empty log file
    path.touch()

def purge_old_audit_logs(retain_days: int = 90) -> None:
    """
    Delete audit log archives older than retain_days (default 90 days).
    """
    now = datetime.now(timezone.utc)
    log_dir = _audit_file().parent
    for file in log_dir.glob("ai_query_audit_*.jsonl"):
        try:
            # Extract timestamp from filename
            ts_str = file.stem.replace("ai_query_audit_", "")
            ts = datetime.strptime(ts_str, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            if (now - ts).days > retain_days:
                file.unlink()
        except Exception:
            continue

def export_audit_log(destination: str) -> None:
    """
    Export the current audit log to a specified destination (path).
    """
    path = _audit_file()
    dest = Path(destination)
    if path.exists():
        dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
