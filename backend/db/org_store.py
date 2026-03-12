"""
backend/db/org_store.py

SQLite-backed store for organizations, workspaces, and users.
Database file: data/voxcloud.db (at project root).

Bootstraps a default org/workspace on first run so the platform works
out-of-the-box without any setup.
"""

import hashlib
import json
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
                environment TEXT NOT NULL DEFAULT 'dev',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(org_id, slug)
            );

            CREATE TABLE IF NOT EXISTS org_users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT 'viewer',
                org_id        INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                workspace_id  INTEGER REFERENCES workspaces(id) ON DELETE SET NULL,
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS workspace_users (
                user_id       INTEGER NOT NULL REFERENCES org_users(id) ON DELETE CASCADE,
                workspace_id  INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
                role          TEXT NOT NULL DEFAULT 'viewer',
                created_at    TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, workspace_id)
            );

            CREATE TABLE IF NOT EXISTS data_sources (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id          INTEGER,
                workspace_id    INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
                type            TEXT,
                platform        TEXT NOT NULL,
                name            TEXT NOT NULL,
                status          TEXT DEFAULT 'active',
                config          TEXT,
                credentials     TEXT NOT NULL,
                schema_cache    TEXT,
                schema_cache_at TEXT,
                is_active       INTEGER DEFAULT 1,
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS semantic_models (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id    INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
                datasource_id   INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
                name            TEXT NOT NULL,
                description     TEXT,
                definition      TEXT NOT NULL,
                is_active       INTEGER DEFAULT 1,
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS schema_tables (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                datasource_id   INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
                schema_name     TEXT NOT NULL,
                table_name      TEXT NOT NULL,
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS schema_columns (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                datasource_id   INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
                schema_name     TEXT NOT NULL,
                table_name      TEXT NOT NULL,
                column_name     TEXT NOT NULL,
                data_type       TEXT,
                nullable        INTEGER,
                primary_key     INTEGER,
                sensitive       TEXT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS api_keys (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id        INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                name          TEXT NOT NULL,
                key_prefix    TEXT NOT NULL,
                key_hash      TEXT NOT NULL,
                created_by    INTEGER,
                is_active     INTEGER NOT NULL DEFAULT 1,
                created_at    TEXT NOT NULL DEFAULT (datetime('now')),
                last_used_at  TEXT
            );
        """)

        # Lightweight forward-only schema compatibility for already-created DBs
        existing_ds_cols = {
            r["name"]
            for r in conn.execute("PRAGMA table_info(data_sources)").fetchall()
        }
        if "org_id" not in existing_ds_cols:
            conn.execute("ALTER TABLE data_sources ADD COLUMN org_id INTEGER")
        if "type" not in existing_ds_cols:
            conn.execute("ALTER TABLE data_sources ADD COLUMN type TEXT")
        if "status" not in existing_ds_cols:
            conn.execute("ALTER TABLE data_sources ADD COLUMN status TEXT DEFAULT 'active'")
        if "config" not in existing_ds_cols:
            conn.execute("ALTER TABLE data_sources ADD COLUMN config TEXT")

        existing_ws_cols = {
            r["name"]
            for r in conn.execute("PRAGMA table_info(workspaces)").fetchall()
        }
        if "environment" not in existing_ws_cols:
            conn.execute("ALTER TABLE workspaces ADD COLUMN environment TEXT DEFAULT 'dev'")

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


def create_workspace(org_id: int, name: str, environment: str = "dev") -> Dict:
    slug = name.lower().replace(" ", "-").replace("_", "-")
    env = (environment or "dev").strip().lower()
    if env not in {"dev", "test", "prod"}:
        env = "dev"
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO workspaces (name, slug, org_id, environment) VALUES (?, ?, ?, ?)",
            (name, slug, org_id, env),
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
        effective_workspace_id = workspace_id
        if effective_workspace_id is None:
            row = conn.execute(
                "SELECT id FROM workspaces WHERE org_id = ? ORDER BY id LIMIT 1",
                (org_id,),
            ).fetchone()
            effective_workspace_id = row[0] if row else None

        if effective_workspace_id is not None:
            conn.execute(
                """
                INSERT OR REPLACE INTO workspace_users (user_id, workspace_id, role)
                VALUES (?, ?, ?)
                """,
                (user_id, effective_workspace_id, role),
            )
    return {
        "id": user_id,
        "email": email,
        "role": role,
        "org_id": org_id,
        "workspace_id": effective_workspace_id,
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


def user_has_workspace_access(user_id: int, workspace_id: int) -> bool:
    with _get_conn() as conn:
        direct = conn.execute(
            """
            SELECT 1
            FROM workspace_users
            WHERE user_id = ? AND workspace_id = ?
            LIMIT 1
            """,
            (user_id, workspace_id),
        ).fetchone()
        if direct:
            return True

        fallback = conn.execute(
            """
            SELECT 1
            FROM org_users u
            JOIN workspaces w ON w.org_id = u.org_id
            WHERE u.id = ? AND w.id = ?
            LIMIT 1
            """,
            (user_id, workspace_id),
        ).fetchone()
    return bool(fallback)


def list_user_workspaces(user_id: int, org_id: int) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT w.id, w.name, w.slug, w.org_id, w.created_at,
                   COALESCE(wu.role, u.role, 'viewer') AS role
            FROM workspaces w
            LEFT JOIN workspace_users wu ON wu.workspace_id = w.id AND wu.user_id = ?
            LEFT JOIN org_users u ON u.id = ?
            WHERE w.org_id = ?
            ORDER BY w.created_at
            """,
            (user_id, user_id, org_id),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Data Sources ───────────────────────────────────────────────────────────────

def list_data_sources(workspace_id: int) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, org_id, workspace_id, name, platform, type, status,
                   config, schema_cache_at, is_active, created_at, updated_at
            FROM data_sources
            WHERE workspace_id = ?
            ORDER BY created_at DESC
            """,
            (workspace_id,),
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        if d.get("config"):
            try:
                d["config"] = json.loads(d["config"])
            except Exception:
                d["config"] = {}
        out.append(d)
    return out


def list_data_sources_scoped(org_id: int, workspace_id: int) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, org_id, workspace_id, name, platform, type, status,
                   config, schema_cache_at, is_active, created_at, updated_at
            FROM data_sources
            WHERE org_id = ? AND workspace_id = ?
            ORDER BY created_at DESC
            """,
            (org_id, workspace_id),
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        if d.get("config"):
            try:
                d["config"] = json.loads(d["config"])
            except Exception:
                d["config"] = {}
        out.append(d)
    return out


def get_data_source(datasource_id: int) -> Optional[Dict]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM data_sources WHERE id = ?",
            (datasource_id,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    for key in ("config", "credentials", "schema_cache"):
        if d.get(key):
            try:
                d[key] = json.loads(d[key])
            except Exception:
                d[key] = {}
    return d


def get_data_source_scoped(datasource_id: int, org_id: int, workspace_id: int) -> Optional[Dict]:
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT * FROM data_sources
            WHERE id = ? AND org_id = ? AND workspace_id = ?
            """,
            (datasource_id, org_id, workspace_id),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    for key in ("config", "credentials", "schema_cache"):
        if d.get(key):
            try:
                d[key] = json.loads(d[key])
            except Exception:
                d[key] = {}
    return d


def create_data_source(
    org_id: int,
    workspace_id: int,
    name: str,
    platform: str,
    status: str,
    config: Dict,
    credentials: Optional[Dict] = None,
) -> Dict:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO data_sources (org_id, workspace_id, name, type, platform, status, config, credentials)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                org_id,
                workspace_id,
                name,
                platform,
                platform,
                status,
                json.dumps(config or {}),
                json.dumps(credentials or config or {}),
            ),
        )
        ds_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return get_data_source(ds_id) or {}


def delete_data_source(datasource_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM data_sources WHERE id = ?",
            (datasource_id,),
        )
    return cur.rowcount > 0


def delete_data_source_scoped(datasource_id: int, org_id: int, workspace_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM data_sources WHERE id = ? AND org_id = ? AND workspace_id = ?",
            (datasource_id, org_id, workspace_id),
        )
    return cur.rowcount > 0


def create_api_key(org_id: int, name: str, created_by: Optional[int] = None) -> Dict:
    raw_key = f"vxc_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    prefix = raw_key[:14]
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO api_keys (org_id, name, key_prefix, key_hash, created_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (org_id, name, prefix, key_hash, created_by),
        )
        api_key_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {
        "id": api_key_id,
        "org_id": org_id,
        "name": name,
        "key_prefix": prefix,
        "api_key": raw_key,
    }


def list_api_keys(org_id: int) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, org_id, name, key_prefix, is_active, created_by, created_at, last_used_at
            FROM api_keys
            WHERE org_id = ?
            ORDER BY created_at DESC
            """,
            (org_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def revoke_api_key(org_id: int, api_key_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "UPDATE api_keys SET is_active = 0 WHERE id = ? AND org_id = ?",
            (api_key_id, org_id),
        )
    return cur.rowcount > 0


def update_data_source_schema_cache(datasource_id: int, schema_cache: Dict) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            """
            UPDATE data_sources
            SET schema_cache = ?, schema_cache_at = datetime('now'), updated_at = datetime('now')
            WHERE id = ?
            """,
            (json.dumps(schema_cache or {}), datasource_id),
        )
    return cur.rowcount > 0


def cache_schema_snapshot(datasource_id: int, schema_cache: Dict) -> None:
    """Persist schema_cache into flat schema_tables/schema_columns for fast explorer reads."""
    tables = (schema_cache or {}).get("tables", [])
    with _get_conn() as conn:
        conn.execute("DELETE FROM schema_columns WHERE datasource_id = ?", (datasource_id,))
        conn.execute("DELETE FROM schema_tables WHERE datasource_id = ?", (datasource_id,))

        for t in tables:
            schema_name = t.get("schema") or "public"
            table_name = t.get("name") or ""
            if not table_name:
                continue
            conn.execute(
                """
                INSERT INTO schema_tables (datasource_id, schema_name, table_name)
                VALUES (?, ?, ?)
                """,
                (datasource_id, schema_name, table_name),
            )

            for c in t.get("columns", [])[:500]:
                conn.execute(
                    """
                    INSERT INTO schema_columns (
                        datasource_id, schema_name, table_name, column_name,
                        data_type, nullable, primary_key, sensitive
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        datasource_id,
                        schema_name,
                        table_name,
                        c.get("name", ""),
                        c.get("type", ""),
                        1 if c.get("nullable") else 0,
                        1 if c.get("primary_key") else 0,
                        c.get("sensitive"),
                    ),
                )


def list_workspace_schema_snapshot(
    workspace_id: int,
    max_tables: int = 30,
    max_columns_per_table: int = 20,
) -> List[Dict]:
    with _get_conn() as conn:
        table_rows = conn.execute(
            """
            SELECT st.datasource_id, ds.name AS datasource_name, ds.platform,
                   st.schema_name, st.table_name
            FROM schema_tables st
            JOIN data_sources ds ON ds.id = st.datasource_id
            WHERE ds.workspace_id = ?
            ORDER BY ds.name ASC, st.schema_name ASC, st.table_name ASC
            LIMIT ?
            """,
            (workspace_id, max_tables),
        ).fetchall()

        out: List[Dict] = []
        for row in table_rows:
            columns = conn.execute(
                """
                SELECT column_name, data_type, nullable, primary_key, sensitive
                FROM schema_columns
                WHERE datasource_id = ? AND schema_name = ? AND table_name = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (
                    row["datasource_id"],
                    row["schema_name"],
                    row["table_name"],
                    max_columns_per_table,
                ),
            ).fetchall()
            out.append(
                {
                    "datasource_id": row["datasource_id"],
                    "datasource_name": row["datasource_name"],
                    "platform": row["platform"],
                    "schema_name": row["schema_name"],
                    "table_name": row["table_name"],
                    "columns": [dict(c) for c in columns],
                }
            )

    return out


# ── Semantic Models ───────────────────────────────────────────────────────────

def list_semantic_models(workspace_id: int, datasource_id: Optional[int] = None) -> List[Dict]:
    with _get_conn() as conn:
        if datasource_id:
            rows = conn.execute(
                """
                SELECT id, workspace_id, datasource_id, name, description, definition, is_active, created_at, updated_at
                FROM semantic_models
                WHERE workspace_id = ? AND datasource_id = ?
                ORDER BY created_at DESC
                """,
                (workspace_id, datasource_id),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, workspace_id, datasource_id, name, description, definition, is_active, created_at, updated_at
                FROM semantic_models
                WHERE workspace_id = ?
                ORDER BY created_at DESC
                """,
                (workspace_id,),
            ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        if d.get("definition"):
            try:
                d["definition"] = json.loads(d["definition"])
            except Exception:
                d["definition"] = {}
        out.append(d)
    return out


def get_semantic_model(model_id: int) -> Optional[Dict]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM semantic_models WHERE id = ?",
            (model_id,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    if d.get("definition"):
        try:
            d["definition"] = json.loads(d["definition"])
        except Exception:
            d["definition"] = {}
    return d


def create_semantic_model(
    workspace_id: int,
    datasource_id: int,
    name: str,
    description: str,
    definition: Dict,
) -> Dict:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO semantic_models (workspace_id, datasource_id, name, description, definition)
            VALUES (?, ?, ?, ?, ?)
            """,
            (workspace_id, datasource_id, name, description, json.dumps(definition or {})),
        )
        model_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return get_semantic_model(model_id) or {}


def update_semantic_model(
    model_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    definition: Optional[Dict] = None,
) -> Optional[Dict]:
    current = get_semantic_model(model_id)
    if not current:
        return None
    next_name = name if name is not None else current.get("name", "")
    next_desc = description if description is not None else current.get("description", "")
    next_def = definition if definition is not None else current.get("definition", {})
    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE semantic_models
            SET name = ?, description = ?, definition = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (next_name, next_desc, json.dumps(next_def or {}), model_id),
        )
    return get_semantic_model(model_id)


def delete_semantic_model(model_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM semantic_models WHERE id = ?",
            (model_id,),
        )
    return cur.rowcount > 0
