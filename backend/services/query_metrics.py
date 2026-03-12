import os
import logging
from typing import Any, Dict

from psycopg2.pool import SimpleConnectionPool


logger = logging.getLogger(__name__)


DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME", "voxcore")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_POOL_MIN = int(os.environ.get("DB_POOL_MIN", "1"))
DB_POOL_MAX = int(os.environ.get("DB_POOL_MAX", "10"))
DB_STATEMENT_TIMEOUT_MS = int(os.environ.get("DB_STATEMENT_TIMEOUT_MS", "15000"))


_POOL: SimpleConnectionPool | None = None


def _get_pool() -> SimpleConnectionPool:
    global _POOL
    if _POOL is None:
        _POOL = SimpleConnectionPool(
            minconn=DB_POOL_MIN,
            maxconn=DB_POOL_MAX,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5,
        )
    return _POOL


def _get_connection():
    pool = _get_pool()
    conn = pool.getconn()
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout = %s", (DB_STATEMENT_TIMEOUT_MS,))
    return conn


def _put_connection(conn) -> None:
    if conn is None:
        return
    pool = _get_pool()
    pool.putconn(conn)


def ensure_query_logs_table() -> None:
    conn = _get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS query_logs (
                        id SERIAL PRIMARY KEY,
                        company_id INT,
                        user_id INT,
                        query TEXT,
                        execution_time FLOAT,
                        risk_level TEXT,
                        blocked BOOLEAN,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
    finally:
        _put_connection(conn)


def log_query(
    company_id: int,
    user_id: int,
    query: str,
    execution_time: float,
    risk_level: str,
    blocked: bool,
) -> bool:
    try:
        ensure_query_logs_table()
        conn = _get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO query_logs
                        (company_id, user_id, query, execution_time, risk_level, blocked, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                        """,
                        (company_id, user_id, query, execution_time, risk_level, blocked),
                    )
        finally:
            _put_connection(conn)
        return True
    except Exception as exc:
        logger.warning("Failed to log query metrics: %s", exc)
        return False


def get_metrics() -> Dict[str, Any]:
    ensure_query_logs_table()
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM query_logs
                WHERE created_at > NOW() - interval '1 minute'
                """
            )
            queries_per_minute = cur.fetchone()[0]

            cur.execute(
                """
                SELECT COUNT(*)
                FROM query_logs
                WHERE blocked = true
                """
            )
            blocked_queries = cur.fetchone()[0]

            cur.execute(
                """
                SELECT AVG(execution_time)
                FROM query_logs
                """
            )
            avg_latency = cur.fetchone()[0]
    finally:
        _put_connection(conn)

    return {
        "queries_per_minute": queries_per_minute,
        "blocked_queries": blocked_queries,
        "average_latency": float(avg_latency) if avg_latency is not None else 0.0,
    }


def get_recent_queries(limit: int = 50) -> list:
    """Return the most recent query_log rows for the inspector table."""
    ensure_query_logs_table()
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, company_id, user_id, query, execution_time,
                       risk_level, blocked, created_at
                FROM query_logs
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        _put_connection(conn)


def get_risk_distribution() -> Dict[str, Any]:
    """Return count & percentage breakdown by risk level for charts."""
    ensure_query_logs_table()
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM query_logs")
            total = cur.fetchone()[0] or 1  # avoid /0

            cur.execute(
                """
                SELECT risk_level, COUNT(*) AS cnt
                FROM query_logs
                GROUP BY risk_level
                """
            )
            rows = cur.fetchall()
    finally:
        _put_connection(conn)

    distribution = {}
    for risk_level, cnt in rows:
        distribution[risk_level] = {
            "count": cnt,
            "percentage": round(cnt / total * 100, 1),
        }

    return {"total": total, "distribution": distribution}


def get_system_metrics() -> Dict[str, Any]:
    """Aggregated system-wide stats for the inspector header cards."""
    ensure_query_logs_table()
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM query_logs WHERE created_at > NOW() - interval '1 day'"
            )
            queries_today = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM query_logs WHERE blocked = true")
            blocked_total = cur.fetchone()[0]

            cur.execute("SELECT AVG(execution_time) FROM query_logs")
            avg_latency = cur.fetchone()[0]
    finally:
        _put_connection(conn)

    # pending approvals count (best-effort)
    pending = 0
    try:
        from backend.services.approval_queue import list_pending
        pending = len(list_pending())
    except Exception:
        pass

    return {
        "queries_today": queries_today,
        "blocked_total": blocked_total,
        "avg_latency_ms": round(float(avg_latency or 0) * 1000, 1),
        "pending_approvals": pending,
    }
