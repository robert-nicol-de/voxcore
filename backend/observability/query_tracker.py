"""
STEP 10 — Observability: Query Tracker

Tracks individual query lifecycle and metadata for debugging and auditing.
Each query gets a unique ID and tracked through all stages: submission → execution → completion.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class QueryStatus(str, Enum):
    """Query execution status"""
    SUBMITTED = "submitted"
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


@dataclass
class QueryMetadata:
    """Complete metadata for a query execution"""
    
    # Identification
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Context
    org_id: str = ""
    user_id: str = ""
    user_role: str = ""
    session_id: str = ""
    
    # Query details
    sql: str = ""
    sql_hash: str = ""  # For caching
    query_type: str = ""  # SELECT, INSERT, UPDATE, DELETE, etc.
    
    # Status
    status: QueryStatus = QueryStatus.SUBMITTED
    
    # Timing
    submitted_at: str = ""
    queued_at: Optional[str] = None
    execution_started_at: Optional[str] = None
    execution_completed_at: Optional[str] = None
    
    # Performance
    queue_wait_ms: float = 0
    execution_time_ms: float = 0
    total_time_ms: float = 0
    
    # Results
    rows_returned: int = 0
    result_size_bytes: int = 0
    
    # Resources
    cost_score: float = 0
    llm_tokens_used: int = 0
    
    # Policies applied
    policies_applied: List[str] = field(default_factory=list)
    policy_effects: List[str] = field(default_factory=list)
    
    # Cache
    cache_hit: bool = False
    cache_key: str = ""
    cache_age_seconds: int = 0
    
    # Errors
    error: bool = False
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    # Source
    source: str = "api"  # api, conversation, batch, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        data = asdict(self)
        data["status"] = self.status.value
        return data


class QueryTracker:
    """
    Tracks individual queries through their lifecycle.
    
    Provides:
    - Query creation and ID generation
    - Status tracking (submitted → queued → executing → completed/failed)
    - Metadata collection at each stage
    - Query history/replay for debugging
    """
    
    def __init__(self, max_queries: int = 100000):
        """
        Initialize query tracker.
        
        Args:
            max_queries: Maximum number of queries to keep in memory
        """
        self.max_queries = max_queries
        self.queries: Dict[str, QueryMetadata] = {}  # query_id -> metadata
        self._lock = __import__('threading').RLock()
    
    def create_query(
        self,
        sql: str,
        org_id: str,
        user_id: str,
        user_role: str,
        session_id: str = "",
        source: str = "api"
    ) -> str:
        """
        Create new query and return query_id.
        
        Args:
            sql: SQL query string
            org_id: Organization ID
            user_id: User ID
            user_role: User's role
            session_id: Session/conversation ID
            source: Where query came from (api, conversation, batch)
        
        Returns:
            query_id: Unique query identifier
        """
        query_id = str(uuid.uuid4())
        
        # Calculate query hash for caching
        import hashlib
        sql_hash = hashlib.sha256(sql.encode()).hexdigest()
        
        # Detect query type
        query_type = sql.strip().split()[0].upper() if sql.strip() else "UNKNOWN"
        
        metadata = QueryMetadata(
            query_id=query_id,
            org_id=org_id,
            user_id=user_id,
            user_role=user_role,
            session_id=session_id,
            sql=sql,
            sql_hash=sql_hash,
            query_type=query_type,
            status=QueryStatus.SUBMITTED,
            submitted_at=datetime.utcnow().isoformat(),
            source=source
        )
        
        with self._lock:
            self.queries[query_id] = metadata
            
            # Cleanup old queries if we exceed max
            if len(self.queries) > self.max_queries:
                # Remove oldest 10% by submission time
                oldest = sorted(
                    self.queries.values(),
                    key=lambda q: q.submitted_at
                )[:int(self.max_queries * 0.1)]
                
                for query in oldest:
                    self.queries.pop(query.query_id, None)
        
        return query_id
    
    def mark_queued(self, query_id: str):
        """Mark query as queued"""
        with self._lock:
            if query_id in self.queries:
                self.queries[query_id].status = QueryStatus.QUEUED
                self.queries[query_id].queued_at = datetime.utcnow().isoformat()
                
                # Calculate queue wait
                submitted = datetime.fromisoformat(self.queries[query_id].submitted_at)
                queued = datetime.fromisoformat(self.queries[query_id].queued_at)
                self.queries[query_id].queue_wait_ms = (queued - submitted).total_seconds() * 1000
    
    def mark_executing(self, query_id: str):
        """Mark query as executing"""
        with self._lock:
            if query_id in self.queries:
                self.queries[query_id].status = QueryStatus.EXECUTING
                self.queries[query_id].execution_started_at = datetime.utcnow().isoformat()
    
    def mark_completed(
        self,
        query_id: str,
        rows_returned: int,
        result_size_bytes: int = 0,
        cost_score: float = 0,
        llm_tokens: int = 0,
        policies: Optional[List[str]] = None,
        policy_effects: Optional[List[str]] = None
    ):
        """Mark query as completed successfully"""
        with self._lock:
            if query_id in self.queries:
                q = self.queries[query_id]
                q.status = QueryStatus.COMPLETED
                q.execution_completed_at = datetime.utcnow().isoformat()
                q.rows_returned = rows_returned
                q.result_size_bytes = result_size_bytes
                q.cost_score = cost_score
                q.llm_tokens_used = llm_tokens
                
                if policies:
                    q.policies_applied = policies
                if policy_effects:
                    q.policy_effects = policy_effects
                
                # Calculate execution time
                started = datetime.fromisoformat(q.execution_started_at)
                completed = datetime.fromisoformat(q.execution_completed_at)
                q.execution_time_ms = (completed - started).total_seconds() * 1000
                
                # Calculate total time
                submitted = datetime.fromisoformat(q.submitted_at)
                q.total_time_ms = (completed - submitted).total_seconds() * 1000
    
    def mark_cached(
        self,
        query_id: str,
        cache_key: str,
        cache_age_seconds: int,
        rows_returned: int,
        result_size_bytes: int = 0
    ):
        """Mark query as served from cache"""
        with self._lock:
            if query_id in self.queries:
                q = self.queries[query_id]
                q.status = QueryStatus.CACHED
                q.cache_hit = True
                q.cache_key = cache_key
                q.cache_age_seconds = cache_age_seconds
                q.execution_completed_at = datetime.utcnow().isoformat()
                q.rows_returned = rows_returned
                q.result_size_bytes = result_size_bytes
                
                # Calculate execution time (cache lookup)
                submitted = datetime.fromisoformat(q.submitted_at)
                completed = datetime.fromisoformat(q.execution_completed_at)
                q.execution_time_ms = (completed - submitted).total_seconds() * 1000
                q.total_time_ms = q.execution_time_ms
    
    def mark_failed(
        self,
        query_id: str,
        error_message: str,
        error_type: str = "QueryExecutionError"
    ):
        """Mark query as failed"""
        with self._lock:
            if query_id in self.queries:
                q = self.queries[query_id]
                q.status = QueryStatus.FAILED
                q.error = True
                q.error_message = error_message
                q.error_type = error_type
                q.execution_completed_at = datetime.utcnow().isoformat()
                
                # Calculate execution time
                submitted = datetime.fromisoformat(q.submitted_at)
                completed = datetime.fromisoformat(q.execution_completed_at)
                q.execution_time_ms = (completed - submitted).total_seconds() * 1000
                q.total_time_ms = q.execution_time_ms
    
    def get_query(self, query_id: str) -> Optional[QueryMetadata]:
        """Get query metadata"""
        with self._lock:
            return self.queries.get(query_id)
    
    def get_queries_by_org(self, org_id: str, limit: int = 100) -> List[QueryMetadata]:
        """Get queries for organization"""
        with self._lock:
            queries = [
                q for q in self.queries.values()
                if q.org_id == org_id
            ]
            return sorted(
                queries,
                key=lambda q: q.submitted_at,
                reverse=True
            )[:limit]
    
    def get_queries_by_user(self, user_id: str, limit: int = 100) -> List[QueryMetadata]:
        """Get queries for user"""
        with self._lock:
            queries = [
                q for q in self.queries.values()
                if q.user_id == user_id
            ]
            return sorted(
                queries,
                key=lambda q: q.submitted_at,
                reverse=True
            )[:limit]
    
    def get_recent_queries(self, limit: int = 100) -> List[QueryMetadata]:
        """Get most recent queries"""
        with self._lock:
            queries = sorted(
                self.queries.values(),
                key=lambda q: q.submitted_at,
                reverse=True
            )
            return queries[:limit]
    
    def get_failed_queries(self, limit: int = 100) -> List[QueryMetadata]:
        """Get failed queries"""
        with self._lock:
            queries = [
                q for q in self.queries.values()
                if q.status == QueryStatus.FAILED
            ]
            return sorted(
                queries,
                key=lambda q: q.submitted_at,
                reverse=True
            )[:limit]
    
    def get_slow_queries(self, threshold_ms: float = 1000, limit: int = 100) -> List[QueryMetadata]:
        """Get slow queries"""
        with self._lock:
            queries = [
                q for q in self.queries.values()
                if q.execution_time_ms > threshold_ms and q.status == QueryStatus.COMPLETED
            ]
            return sorted(
                queries,
                key=lambda q: q.execution_time_ms,
                reverse=True
            )[:limit]
    
    def get_high_cost_queries(self, threshold: float = 10.0, limit: int = 100) -> List[QueryMetadata]:
        """Get high-cost queries"""
        with self._lock:
            queries = [
                q for q in self.queries.values()
                if q.cost_score > threshold and q.status == QueryStatus.COMPLETED
            ]
            return sorted(
                queries,
                key=lambda q: q.cost_score,
                reverse=True
            )[:limit]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total = len(self.queries)
            cached = sum(1 for q in self.queries.values() if q.cache_hit)
            
            return {
                "total_queries": total,
                "cache_hits": cached,
                "cache_misses": total - cached,
                "cache_hit_rate": (cached / total * 100) if total > 0 else 0
            }
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self._lock:
            total = len(self.queries)
            failed = sum(1 for q in self.queries.values() if q.status == QueryStatus.FAILED)
            
            # Count errors by type
            errors_by_type = {}
            for q in self.queries.values():
                if q.error_type:
                    errors_by_type[q.error_type] = errors_by_type.get(q.error_type, 0) + 1
            
            return {
                "total_queries": total,
                "failed_queries": failed,
                "error_rate": (failed / total * 100) if total > 0 else 0,
                "errors_by_type": errors_by_type
            }
    
    def clear_old_queries(self, older_than_hours: int = 24):
        """Clear queries older than specified hours"""
        from datetime import timezone, timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
        
        with self._lock:
            to_delete = []
            for query_id, q in self.queries.items():
                submitted = datetime.fromisoformat(q.submitted_at)
                if submitted < cutoff:
                    to_delete.append(query_id)
            
            for query_id in to_delete:
                self.queries.pop(query_id)
            
            return len(to_delete)


# Global query tracker instance
_query_tracker: Optional[QueryTracker] = None


def get_query_tracker() -> QueryTracker:
    """Get or create global query tracker"""
    global _query_tracker
    if _query_tracker is None:
        _query_tracker = QueryTracker()
    return _query_tracker
