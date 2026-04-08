"""
Insights persistence layer.

Stores insights and learning signals in SQLite.
Replaces YAML file-based storage with proper relational schema.

Tables:
  - insights: Discovered patterns/anomalies
  - learning_signals: User interaction tracking
  - insight_cache: Cached insight metadata

Usage:
    create_tables()  # Initialize schema (idempotent)
    store_insight(insight_text, insight_type, metric, score)
    insights = get_all_insights()
"""
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_PATH = 'voxcore_insights.db'


def get_db() -> sqlite3.Connection:
    """Get SQLite connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables() -> None:
    """Create or verify insights schema (idempotent)."""
    conn = get_db()
    c = conn.cursor()
    
    # Enhanced insights table with type and metric columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insight TEXT NOT NULL,
            insight_type TEXT,
            metric TEXT,
            score FLOAT DEFAULT 0.0,
            workspace_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Learning signals for user behavior tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT,
            query TEXT,
            workspace_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insight cache metadata (for tracking stale insights)
    c.execute('''
        CREATE TABLE IF NOT EXISTS insight_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insight_id INTEGER,
            cache_key TEXT UNIQUE,
            cache_value TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (insight_id) REFERENCES insights(id)
        )
    ''')
    
    # Create indexes for common queries
    try:
        c.execute('CREATE INDEX IF NOT EXISTS idx_insights_created ON insights(created_at)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(insight_type)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_insights_workspace ON insights(workspace_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_signals_user ON learning_signals(user_id)')
    except sqlite3.OperationalError:
        pass  # Index may already exist
    
    conn.commit()
    conn.close()


def store_insight(
    insight: str,
    insight_type: Optional[str] = None,
    metric: Optional[str] = None,
    score: float = 0.0,
    workspace_id: Optional[str] = None
) -> int:
    """
    Store a new insight in the database.
    
    Args:
        insight: Insight text/description
        insight_type: Type of insight (e.g., "revenue_decline", "anomaly")
        metric: Associated metric (e.g., "revenue", "user_count")
        score: Relevance/importance score (0.0-1.0)
        workspace_id: Optional workspace identifier
    
    Returns:
        Insight ID (for later reference)
    """
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO insights (insight, insight_type, metric, score, workspace_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (insight, insight_type, metric, score, workspace_id))
    conn.commit()
    insight_id = c.lastrowid
    conn.close()
    return insight_id


def get_all_insights(workspace_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieve all insights, optionally filtered by workspace.
    
    Args:
        workspace_id: Optional filter to workspace
        limit: Maximum number of results
    
    Returns:
        List of insight dictionaries
    """
    conn = get_db()
    c = conn.cursor()
    
    if workspace_id:
        c.execute('''
            SELECT * FROM insights
            WHERE workspace_id IS NULL OR workspace_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (workspace_id, limit))
    else:
        c.execute('''
            SELECT * FROM insights
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_insights_by_type(
    insight_type: str,
    workspace_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Retrieve insights filtered by type.
    
    Args:
        insight_type: Type to filter by
        workspace_id: Optional workspace filter
        limit: Maximum results
    
    Returns:
        List of matching insights
    """
    conn = get_db()
    c = conn.cursor()
    
    if workspace_id:
        c.execute('''
            SELECT * FROM insights
            WHERE insight_type = ? AND (workspace_id IS NULL OR workspace_id = ?)
            ORDER BY created_at DESC
            LIMIT ?
        ''', (insight_type, workspace_id, limit))
    else:
        c.execute('''
            SELECT * FROM insights
            WHERE insight_type = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (insight_type, limit))
    
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_insights_by_metric(
    metric: str,
    workspace_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Retrieve insights for a specific metric.
    
    Args:
        metric: Metric to filter by (e.g., "revenue")
        workspace_id: Optional workspace filter
        limit: Maximum results
    
    Returns:
        List of insights for this metric
    """
    conn = get_db()
    c = conn.cursor()
    
    if workspace_id:
        c.execute('''
            SELECT * FROM insights
            WHERE metric = ? AND (workspace_id IS NULL OR workspace_id = ?)
            ORDER BY created_at DESC
            LIMIT ?
        ''', (metric, workspace_id, limit))
    else:
        c.execute('''
            SELECT * FROM insights
            WHERE metric = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (metric, limit))
    
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_insight(insight_id: int) -> bool:
    """
    Delete an insight by ID.
    
    Args:
        insight_id: ID to delete
    
    Returns:
        True if deleted, False if not found
    """
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM insights WHERE id = ?', (insight_id,))
    conn.commit()
    success = c.rowcount > 0
    conn.close()
    return success


def store_learning_signal(
    user_id: str,
    action: str,
    query: str,
    workspace_id: Optional[str] = None
) -> int:
    """
    Store a learning signal (user interaction).
    
    Args:
        user_id: User identifier
        action: Action type (e.g., "approved", "rejected", "modified")
        query: Associated query or content
        workspace_id: Optional workspace identifier
    
    Returns:
        Learning signal ID
    """
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO learning_signals (user_id, action, query, workspace_id)
        VALUES (?, ?, ?, ?)
    ''', (user_id, action, query, workspace_id))
    conn.commit()
    signal_id = c.lastrowid
    conn.close()
    return signal_id


def get_learning_signals(
    user_id: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Retrieve learning signals, optionally filtered by user.
    
    Args:
        user_id: Optional user filter
        limit: Maximum results
    
    Returns:
        List of learning signal dictionaries
    """
    conn = get_db()
    c = conn.cursor()
    
    if user_id:
        c.execute('''
            SELECT * FROM learning_signals
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
    else:
        c.execute('''
            SELECT * FROM learning_signals
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_insights_stats(workspace_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics about stored insights.
    
    Args:
        workspace_id: Optional workspace filter
    
    Returns:
        Dictionary with counts and timestamps
    """
    conn = get_db()
    c = conn.cursor()
    
    if workspace_id:
        c.execute('''
            SELECT COUNT(*) as total, COUNT(DISTINCT insight_type) as type_count
            FROM insights
            WHERE workspace_id IS NULL OR workspace_id = ?
        ''', (workspace_id,))
    else:
        c.execute('''
            SELECT COUNT(*) as total, COUNT(DISTINCT insight_type) as type_count
            FROM insights
        ''')
    
    stats = dict(c.fetchone())
    conn.close()
    return stats

