"""
UsageTracker - Session-level metering and billing foundation

Tracks per-session usage metrics for monetization:
- queries_count: Number of queries executed
- rows_scanned: Total rows queried across all executions
- execution_time_total: Cumulative query execution time
- cost_spent: Calculated cost based on governance policies

Schema (SQLite):
  sessions:
    - session_id (PK, TEXT)
    - user_id (TEXT, nullable)
    - workspace_id (TEXT, nullable)
    - created_at (TIMESTAMP)
    - queries_count (INTEGER)
    - rows_scanned_total (INTEGER)
    - execution_time_total (INTEGER, ms)
    - cost_spent (FLOAT)

Usage:
  tracker = UsageTracker()
  tracker.record_query(session_id, rows=1000, time_ms=250, cost=5.0)
  usage = tracker.get_session_usage(session_id)
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Default SQLite database path
DEFAULT_DB_PATH = os.getenv(
    "USAGE_TRACKER_DB",
    os.path.join(os.path.dirname(__file__), "../data/usage_tracker.db")
)


class UsageTracker:
    """Session-level usage tracking for metering and billing"""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """Create database and schema if not exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                workspace_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                queries_count INTEGER DEFAULT 0,
                rows_scanned_total INTEGER DEFAULT 0,
                execution_time_total INTEGER DEFAULT 0,
                cost_spent REAL DEFAULT 0.0
            )
        """)

        # Create queries table (detailed log)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                query_hash TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rows_scanned INTEGER DEFAULT 0,
                execution_time_ms INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                status TEXT DEFAULT 'success',
                sql TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON sessions(session_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_query_session ON query_executions(session_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_query_executed_at ON query_executions(executed_at)"
        )

        conn.commit()
        conn.close()

    def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create or reset a session.
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
            workspace_id: Optional workspace identifier
            
        Returns:
            Session metadata
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO sessions 
            (session_id, user_id, workspace_id, created_at, queries_count, rows_scanned_total, execution_time_total, cost_spent)
            VALUES (?, ?, ?, ?, 0, 0, 0, 0.0)
            """,
            (session_id, user_id, workspace_id, datetime.utcnow().isoformat()),
        )
        conn.commit()

        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else {}

    def record_query(
        self,
        session_id: str,
        rows_scanned: int = 0,
        execution_time_ms: int = 0,
        cost: float = 0.0,
        status: str = "success",
        sql: Optional[str] = None,
        query_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a query execution and update session totals.
        
        Args:
            session_id: Session identifier
            rows_scanned: Number of rows affected
            execution_time_ms: Execution time in milliseconds
            cost: Calculated cost (based on governance policies)
            status: Query status (success, error, blocked)
            sql: Original SQL query (optional)
            query_hash: Hash of query for deduplication (optional)
            
        Returns:
            Updated session usage
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Record individual query
            cursor.execute(
                """
                INSERT INTO query_executions 
                (session_id, query_hash, rows_scanned, execution_time_ms, cost, status, sql)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    query_hash,
                    rows_scanned,
                    execution_time_ms,
                    cost,
                    status,
                    sql,
                ),
            )

            # Update session totals (only on success)
            if status == "success":
                cursor.execute(
                    """
                    UPDATE sessions
                    SET 
                        queries_count = queries_count + 1,
                        rows_scanned_total = rows_scanned_total + ?,
                        execution_time_total = execution_time_total + ?,
                        cost_spent = cost_spent + ?
                    WHERE session_id = ?
                    """,
                    (rows_scanned, execution_time_ms, cost, session_id),
                )
            else:
                # Still increment query count even on error
                cursor.execute(
                    "UPDATE sessions SET queries_count = queries_count + 1 WHERE session_id = ?",
                    (session_id,),
                )

            conn.commit()

            # Return updated session
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()

            return dict(row) if row else {}

        finally:
            conn.close()

    def get_session_usage(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current usage metrics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session usage dict or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_session_queries(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> list:
        """
        Get detailed query execution log for a session.
        
        Args:
            session_id: Session identifier
            limit: Max results
            offset: Pagination offset
            
        Returns:
            List of query execution records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM query_executions 
            WHERE session_id = ? 
            ORDER BY executed_at DESC 
            LIMIT ? OFFSET ?
            """,
            (session_id, limit, offset),
        )
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get aggregated usage summary for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Summary with usage metrics and estimates
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get session totals
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        session = cursor.fetchone()

        if not session:
            conn.close()
            return {}

        session_dict = dict(session)

        # Get average execution time
        cursor.execute(
            """
            SELECT 
                AVG(execution_time_ms) as avg_time,
                MIN(execution_time_ms) as min_time,
                MAX(execution_time_ms) as max_time,
                COUNT(*) as total_executions
            FROM query_executions 
            WHERE session_id = ? AND status = 'success'
            """,
            (session_id,),
        )
        stats = cursor.fetchone()
        conn.close()

        if stats:
            stats_dict = dict(stats)
            session_dict.update(
                {
                    "avg_execution_time_ms": stats_dict.get("avg_time") or 0,
                    "min_execution_time_ms": stats_dict.get("min_time") or 0,
                    "max_execution_time_ms": stats_dict.get("max_time") or 0,
                    "total_executions": stats_dict.get("total_executions") or 0,
                }
            )

        return session_dict

    def get_cost_estimate(self, session_id: str) -> Dict[str, Any]:
        """
        Calculate cost estimate for session (for billing).
        
        Cost calculation:
        - Base: $0.01 per query
        - Rows: $0.001 per 10,000 rows
        - Time: $0.01 per 100ms
        
        Args:
            session_id: Session identifier
            
        Returns:
            Cost breakdown
        """
        usage = self.get_session_summary(session_id)

        if not usage:
            return {}

        queries_count = usage.get("queries_count", 0)
        rows_scanned = usage.get("rows_scanned_total", 0)
        execution_time = usage.get("execution_time_total", 0)
        cost_spent = usage.get("cost_spent", 0)

        # Simple cost model
        estimated_query_cost = queries_count * 0.01
        estimated_row_cost = (rows_scanned / 10000) * 0.001
        estimated_time_cost = (execution_time / 100) * 0.01

        total_estimated = estimated_query_cost + estimated_row_cost + estimated_time_cost

        return {
            "queries_count": queries_count,
            "rows_scanned_total": rows_scanned,
            "execution_time_total": execution_time,
            "cost_from_governance": cost_spent,
            "estimated_query_cost": round(estimated_query_cost, 4),
            "estimated_row_cost": round(estimated_row_cost, 4),
            "estimated_time_cost": round(estimated_time_cost, 4),
            "total_estimated_cost": round(total_estimated, 4),
        }

    def reset_session(self, session_id: str) -> Dict[str, Any]:
        """Reset usage metrics for a session (for new analytics)"""
        return self.create_session(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its query logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM query_executions WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Delete sessions older than N days. Returns count deleted."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM session WHERE 
            created_at < datetime('now', '-' || ? || ' days')
            """,
            (days,),
        )
        conn.commit()
        deleted = cursor.rowcount
        conn.close()

        return deleted


# Singleton instance
_tracker: Optional[UsageTracker] = None


def get_usage_tracker() -> UsageTracker:
    """Get or create global UsageTracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker
