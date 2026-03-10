"""
Query Approval Queue — database layer.

Provides:
  submit()         — insert a pending query into the queue
  list_pending()   — return all rows with status='pending'
  approve()        — mark a row approved
  reject()         — mark a row rejected
  get_by_id()      — fetch a single row
"""

import json
import os
from typing import Any

import psycopg2
import psycopg2.extras

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME", "voxcore")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")


def _conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def ensure_table() -> None:
    sql = """
    CREATE TABLE IF NOT EXISTS pending_queries (
        id SERIAL PRIMARY KEY,
        query_text TEXT NOT NULL,
        risk_score INT NOT NULL,
        risk_level TEXT NOT NULL,
        reasons TEXT,
        ai_agent TEXT NOT NULL DEFAULT 'anonymous',
        database_name TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        company_id INT,
        user_id INT,
        created_at TIMESTAMP DEFAULT NOW(),
        reviewed_by TEXT,
        reviewed_at TIMESTAMP
    )
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def submit(
    query_text: str,
    risk_score: int,
    risk_level: str,
    reasons: list[str],
    ai_agent: str = "anonymous",
    database_name: str | None = None,
    company_id: int = 1,
    user_id: int = 1,
) -> dict[str, Any]:
    ensure_table()
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pending_queries
                    (query_text, risk_score, risk_level, reasons,
                     ai_agent, database_name, company_id, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    query_text,
                    risk_score,
                    risk_level,
                    json.dumps(reasons),
                    ai_agent,
                    database_name,
                    company_id,
                    user_id,
                ),
            )
            row = dict(cur.fetchone())
    return row


def list_pending(company_id: int | None = None) -> list[dict[str, Any]]:
    ensure_table()
    with _conn() as conn:
        with conn.cursor() as cur:
            if company_id:
                cur.execute(
                    "SELECT * FROM pending_queries WHERE status='pending' AND company_id=%s ORDER BY created_at DESC",
                    (company_id,),
                )
            else:
                cur.execute(
                    "SELECT * FROM pending_queries WHERE status='pending' ORDER BY created_at DESC"
                )
            return [dict(r) for r in cur.fetchall()]


def get_by_id(query_id: int) -> dict[str, Any] | None:
    ensure_table()
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pending_queries WHERE id=%s", (query_id,))
            row = cur.fetchone()
            return dict(row) if row else None


def _update_status(query_id: int, status: str, reviewed_by: str) -> dict[str, Any]:
    ensure_table()
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pending_queries
                SET status=%s, reviewed_by=%s, reviewed_at=NOW()
                WHERE id=%s
                RETURNING *
                """,
                (status, reviewed_by, query_id),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"No pending query with id={query_id}")
            return dict(row)


def approve(query_id: int, reviewed_by: str = "admin") -> dict[str, Any]:
    return _update_status(query_id, "approved", reviewed_by)


def reject(query_id: int, reviewed_by: str = "admin") -> dict[str, Any]:
    return _update_status(query_id, "rejected", reviewed_by)
