"""
backend/db/org_store.py

SQLite-backed store for organizations, workspaces, and users.
Database file: data/voxcloud.db (at project root).

Bootstraps a default org/workspace on first run so the platform works
out-of-the-box without any setup.
"""

import hashlib
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional


# ── Database setup ─────────────────────────────────────────────────────────────

def _db_path() -> Path:
    # backend/db/org_store.py -> backend/db -> backend -> project root
    root = Path(__file__).resolve().parents[2]
    db_dir = root / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "voxcloud.db"


@contextmanager
def _get_conn():
    conn = sqlite3.connect(str(_db_path()), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables and seed default org + workspace if empty."""
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS organizations (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                slug       TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS workspaces (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                slug       TEXT NOT NULL,
                org_id     INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(org_id, slug)
            );

            CREATE TABLE IF NOT EXISTS org_users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT 'analyst',
                org_id        INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                workspace_id  INTEGER REFERENCES workspaces(id) ON DELETE SET NULL,
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)

        # Seed default org and workspace on first run only
        existing = conn.execute("SELECT COUNT(*) FROM organizations").fetchone()[0]
        if existing == 0:
            conn.execute(
                "INSERT INTO organizations (name, slug) VALUES (?, ?)",
                ("VoxCore Demo", "voxcore-demo"),
            )
            org_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.execute(
                "INSERT INTO workspaces (name, slug, org_id) VALUES (?, ?, ?)",
                ("Default", "default", org_id),
            )
            print("[OK] Seeded default organization and workspace in voxcloud.db")


# ── Password helpers ───────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def _check_password(password: str, stored: str) -> bool:
    if ":" not in stored:
        # Legacy plaintext comparison (for migrated dummy users)
        return password == stored
    salt, h = stored.split(":", 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == h


# ── Organizations ──────────────────────────────────────────────────────────────

def list_orgs() -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM organizations ORDER BY created_at"
        ).fetchall()
    return [dict(r) for r in rows]


def get_org(org_id: int) -> Optional[Dict]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM organizations WHERE id = ?", (org_id,)
        ).fetchone()
    return dict(row) if row else None


def create_org(name: str) -> Dict:
    slug = name.lower().replace(" ", "-").replace("_", "-")
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO organizations (name, slug) VALUES (?, ?)", (name, slug)
        )
        org_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Auto-create a Default workspace for every new org
        conn.execute(
            "INSERT INTO workspaces (name, slug, org_id) VALUES (?, ?, ?)",
            ("Default", "default", org_id),
        )
    return get_org(org_id)


# ── Workspaces ─────────────────────────────────────────────────────────────────

def list_workspaces(org_id: int) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM workspaces WHERE org_id = ? ORDER BY created_at",
            (org_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_workspace(workspace_id: int) -> Optional[Dict]:
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT w.*, o.name AS org_name, o.slug AS org_slug
            FROM workspaces w
            JOIN organizations o ON o.id = w.org_id
            WHERE w.id = ?
            """,
            (workspace_id,),
        ).fetchone()
    return dict(row) if row else None


def get_default_workspace(org_id: int) -> Optional[Dict]:
    """Return the first (oldest) workspace for an org — used as fallback."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM workspaces WHERE org_id = ? ORDER BY id LIMIT 1",
            (org_id,),
        ).fetchone()
    return dict(row) if row else None


def create_workspace(org_id: int, name: str) -> Dict:
    slug = name.lower().replace(" ", "-").replace("_", "-")
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO workspaces (name, slug, org_id) VALUES (?, ?, ?)",
            (name, slug, org_id),
        )
        ws_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return get_workspace(ws_id)


def delete_workspace(workspace_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM workspaces WHERE id = ?", (workspace_id,)
        )
    return cur.rowcount > 0


def rename_workspace(workspace_id: int, name: str) -> Optional[Dict]:
    slug = name.lower().replace(" ", "-").replace("_", "-")
    with _get_conn() as conn:
        cur = conn.execute(
            "UPDATE workspaces SET name = ?, slug = ? WHERE id = ?",
            (name, slug, workspace_id),
        )
    return get_workspace(workspace_id) if cur.rowcount > 0 else None


# ── Users ──────────────────────────────────────────────────────────────────────

def list_users(org_id: int) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, email, role, org_id, workspace_id, created_at "
            "FROM org_users WHERE org_id = ? ORDER BY created_at",
            (org_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_user_by_email(email: str) -> Optional[Dict]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, role, org_id, workspace_id "
            "FROM org_users WHERE email = ?",
            (email.lower(),),
        ).fetchone()
    return dict(row) if row else None


def create_user(
    email: str,
    password: str,
    role: str,
    org_id: int,
    workspace_id: Optional[int] = None,
) -> Dict:
    pw_hash = _hash_password(password)
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO org_users (email, password_hash, role, org_id, workspace_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (email.lower(), pw_hash, role, org_id, workspace_id),
        )
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {
        "id": user_id,
        "email": email,
        "role": role,
        "org_id": org_id,
        "workspace_id": workspace_id,
    }


def verify_user(email: str, password: str) -> Optional[Dict]:
    """Return user dict if credentials match, else None."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not _check_password(password, user["password_hash"]):
        return None
    return user


def update_user_role(user_id: int, role: str) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "UPDATE org_users SET role = ? WHERE id = ?", (role, user_id)
        )
    return cur.rowcount > 0
