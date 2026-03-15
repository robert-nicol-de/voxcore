# PermissionEngine integration test (skeleton)
from voxcore.security.permission_engine import PermissionEngine
from voxcore.security.sqlite_adapter import SQLiteAdapter
from pathlib import Path

# Example usage for local dev/test
def test_permission_engine():
    db_path = Path(__file__).resolve().parents[3] / "data" / "voxcloud.db"
    db = SQLiteAdapter(db_path)
    engine = PermissionEngine(db)
    # Example: user 12, viewer, dashboard 21
    assert engine.relationship_exists(("user", 12), "member", ("workspace", 5))
    assert engine.relationship_exists(("workspace", 5), "viewer", ("dashboard", 21))
    # Add more tests as needed

if __name__ == "__main__":
    test_permission_engine()
    print("[OK] PermissionEngine basic checks passed.")
