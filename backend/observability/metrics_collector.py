"""
STEP 10 — Observability: Metrics Collector

Collects and aggregates metrics: latency, error rate, cache hits, queue wait time.
Provides real-time and historical metrics for dashboards and alerting.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import threading
import statistics


@dataclass
class LatencyMetrics:
    """Query latency metrics"""
    min_ms: float = 0
    max_ms: float = 0
    mean_ms: float = 0
    median_ms: float = 0
    p95_ms: float = 0
    p99_ms: float = 0
    count: int = 0


@dataclass
class ErrorMetrics:
    """Error metrics"""
    total_errors: int = 0
    error_rate_percent: float = 0.0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    last_error: Optional[str] = None
    last_error_time: Optional[str] = None


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    hit_rate_percent: float = 0.0
    avg_hit_time_ms: float = 0
    avg_miss_time_ms: float = 0


@dataclass
class QueueMetrics:
    """Job queue metrics"""
    waiting_count: int = 0
    avg_wait_time_ms: float = 0
    max_wait_time_ms: float = 0
    processed_count: int = 0
    processing_count: int = 0


@dataclass
class CostMetrics:
    """Cost/resource usage metrics"""
    total_cost: float = 0.0
    avg_cost_per_query: float = 0.0
    max_cost: float = 0.0
    cost_by_role: Dict[str, float] = field(default_factory=dict)
    cost_by_org: Dict[str, float] = field(default_factory=dict)


@dataclass
class SystemHealthMetrics:
    """Overall system health"""
    status: str = "healthy"  # healthy, degraded, critical
    uptime_seconds: int = 0
    memory_percent: float = 0.0
    cpu_percent: float = 0.0
    active_connections: int = 0
    pending_jobs: int = 0
    last_error: Optional[str] = None


class MetricsCollector:
    """
    Collects and aggregates system metrics for observability.
    
    Tracks:
    - Query latency (min, max, mean, median, p95, p99)
    - Error rate and error types
    - Cache hit rate and performance
    - Queue wait times
    - Cost metrics (total, by role, by org)
    """
    
    def __init__(self, window_size: int = 10000):
        """
        Initialize metrics collector.
        
        Args:
            window_size: Number of queries to keep in rolling window
        """
        self.window_size = window_size
        
        # Rolling windows for metrics
        self.latencies: deque = deque(maxlen=window_size)  # Query latencies in ms
        self.errors: deque = deque(maxlen=window_size)  # Error events
        self.cache_hits: deque = deque(maxlen=window_size)  # Cache hit times in ms
        self.cache_misses: deque = deque(maxlen=window_size)  # Cache miss times in ms
        self.queue_waits: deque = deque(maxlen=window_size)  # Queue wait times in ms
        self.costs: deque = deque(maxlen=window_size)  # Cost scores
        
        # Aggregated by dimension
        self.by_org: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "query_count": 0,
            "total_latency_ms": 0,
            "total_cost": 0,
            "error_count": 0
        })
        
        self.by_role: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "query_count": 0,
            "total_latency_ms": 0,
            "total_cost": 0,
            "error_count": 0
        })
        
        self.by_user: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "query_count": 0,
            "total_latency_ms": 0,
            "total_cost": 0,
            "error_count": 0
        })
        
        # System metrics
        self.active_jobs: Dict[str, Dict[str, Any]] = {}  # job_id -> job metadata
        self.failed_queries: deque = deque(maxlen=1000)  # Failed query details
        
        self._lock = threading.RLock()
    
    def record_query(
        self,
        query_id: str,
        org_id: str,
        user_id: str,
        user_role: str,
        execution_time_ms: float,
        cost_score: float,
        rows_returned: int,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Record a query execution"""
        with self._lock:
            # Record latency
            self.latencies.append(execution_time_ms)
            
            # Record cost
            self.costs.append(cost_score)
            
            # Update by-org metrics
            self.by_org[org_id]["query_count"] += 1
            self.by_org[org_id]["total_latency_ms"] += execution_time_ms
            self.by_org[org_id]["total_cost"] += cost_score
            
            # Update by-role metrics
            self.by_role[user_role]["query_count"] += 1
            self.by_role[user_role]["total_latency_ms"] += execution_time_ms
            self.by_role[user_role]["total_cost"] += cost_score
            
            # Update by-user metrics
            self.by_user[user_id]["query_count"] += 1
            self.by_user[user_id]["total_latency_ms"] += execution_time_ms
            self.by_user[user_id]["total_cost"] += cost_score
            
            # Record error if failed
            if not success:
                error_event = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "query_id": query_id,
                    "org_id": org_id,
                    "user_id": user_id,
                    "error_message": error_message
                }
                self.errors.append(error_event)
                self.failed_queries.append(error_event)
                
                self.by_org[org_id]["error_count"] += 1
                self.by_role[user_role]["error_count"] += 1
                self.by_user[user_id]["error_count"] += 1
    
    def record_cache_hit(
        self,
        query_id: str,
        hit_time_ms: float,
        rows_returned: int,
        cache_key: str
    ):
        """Record cache hit"""
        with self._lock:
            self.cache_hits.append(hit_time_ms)
    
    def record_cache_miss(
        self,
        query_id: str,
        miss_time_ms: float,
        cache_key: str
    ):
        """Record cache miss"""
        with self._lock:
            self.cache_misses.append(miss_time_ms)
    
    def record_queue_wait(
        self,
        job_id: str,
        wait_time_ms: float
    ):
        """Record queue wait time"""
        with self._lock:
            self.queue_waits.append(wait_time_ms)
    
    def add_active_job(
        self,
        job_id: str,
        query_id: str,
        org_id: str,
        user_id: str,
        status: str,
        created_at: str
    ):
        """Add job to active jobs tracking"""
        with self._lock:
            self.active_jobs[job_id] = {
                "job_id": job_id,
                "query_id": query_id,
                "org_id": org_id,
                "user_id": user_id,
                "status": status,
                "created_at": created_at,
                "started_at": None,
                "completed_at": None
            }
    
    def update_job_status(self, job_id: str, status: str, started_at: Optional[str] = None):
        """Update job status"""
        with self._lock:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["status"] = status
                if started_at:
                    self.active_jobs[job_id]["started_at"] = started_at
    
    def complete_job(self, job_id: str, completed_at: str):
        """Mark job as completed"""
        with self._lock:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["status"] = "completed"
                self.active_jobs[job_id]["completed_at"] = completed_at
                # Keep in history briefly, then remove
                # (in production, move to persistent storage)
    
    # Metrics calculation methods
    
    def get_latency_metrics(self) -> LatencyMetrics:
        """Calculate latency metrics"""
        with self._lock:
            if not self.latencies:
                return LatencyMetrics()
            
            latencies = sorted(self.latencies)
            count = len(latencies)
            
            return LatencyMetrics(
                min_ms=min(latencies),
                max_ms=max(latencies),
                mean_ms=statistics.mean(latencies),
                median_ms=statistics.median(latencies),
                p95_ms=latencies[int(count * 0.95)] if count > 0 else 0,
                p99_ms=latencies[int(count * 0.99)] if count > 19 else latencies[-1],
                count=count
            )
    
    def get_error_metrics(self) -> ErrorMetrics:
        """Calculate error metrics"""
        with self._lock:
            total_queries = len(self.latencies) + len(self.errors)
            total_errors = len(self.errors)
            
            error_rate = (total_errors / total_queries * 100) if total_queries > 0 else 0
            
            # Count errors by type
            errors_by_type = defaultdict(int)
            last_error = None
            last_error_time = None
            
            for error_event in self.errors:
                error_msg = error_event.get("error_message", "unknown")
                error_type = error_msg.split(":")[0] if error_msg else "unknown"
                errors_by_type[error_type] += 1
                
                if last_error is None:
                    last_error = error_msg
                    last_error_time = error_event.get("timestamp")
            
            return ErrorMetrics(
                total_errors=total_errors,
                error_rate_percent=error_rate,
                errors_by_type=dict(errors_by_type),
                last_error=last_error,
                last_error_time=last_error_time
            )
    
    def get_cache_metrics(self) -> CacheMetrics:
        """Calculate cache metrics"""
        with self._lock:
            hits = len(self.cache_hits)
            misses = len(self.cache_misses)
            total = hits + misses
            
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            avg_hit_time = statistics.mean(self.cache_hits) if self.cache_hits else 0
            avg_miss_time = statistics.mean(self.cache_misses) if self.cache_misses else 0
            
            return CacheMetrics(
                hits=hits,
                misses=misses,
                hit_rate_percent=hit_rate,
                avg_hit_time_ms=avg_hit_time,
                avg_miss_time_ms=avg_miss_time
            )
    
    def get_queue_metrics(self) -> QueueMetrics:
        """Calculate queue metrics"""
        with self._lock:
            waiting_count = sum(
                1 for job in self.active_jobs.values()
                if job["status"] == "queued"
            )
            
            processing_count = sum(
                1 for job in self.active_jobs.values()
                if job["status"] == "processing"
            )
            
            wait_times = list(self.queue_waits)
            avg_wait = statistics.mean(wait_times) if wait_times else 0
            max_wait = max(wait_times) if wait_times else 0
            processed_count = sum(
                1 for job in self.active_jobs.values()
                if job["status"] == "completed"
            )
            
            return QueueMetrics(
                waiting_count=waiting_count,
                avg_wait_time_ms=avg_wait,
                max_wait_time_ms=max_wait,
                processed_count=processed_count,
                processing_count=processing_count
            )
    
    def get_cost_metrics(self) -> CostMetrics:
        """Calculate cost metrics"""
        with self._lock:
            total_cost = sum(self.costs) if self.costs else 0
            avg_cost = (total_cost / len(self.costs)) if self.costs else 0
            max_cost = max(self.costs) if self.costs else 0
            
            # Cost by role
            cost_by_role = {}
            for role, metrics in self.by_role.items():
                cost_by_role[role] = metrics["total_cost"]
            
            # Cost by org
            cost_by_org = {}
            for org, metrics in self.by_org.items():
                cost_by_org[org] = metrics["total_cost"]
            
            return CostMetrics(
                total_cost=total_cost,
                avg_cost_per_query=avg_cost,
                max_cost=max_cost,
                cost_by_role=cost_by_role,
                cost_by_org=cost_by_org
            )
    
    def get_system_health(self) -> SystemHealthMetrics:
        """Calculate system health"""
        latency = self.get_latency_metrics()
        errors = self.get_error_metrics()
        cache = self.get_cache_metrics()
        queue = self.get_queue_metrics()
        
        # Determine health status
        status = "healthy"
        
        if errors.error_rate_percent > 5:
            status = "critical"
        elif errors.error_rate_percent > 1 or latency.p99_ms > 5000:
            status = "degraded"
        
        active_queue = sum(
            1 for job in self.active_jobs.values()
            if job["status"] in ["queued", "processing"]
        )
        
        return SystemHealthMetrics(
            status=status,
            uptime_seconds=0,  # Calculate based on startup time
            memory_percent=0,  # Get from system
            cpu_percent=0,  # Get from system
            active_connections=len(self.active_jobs),
            pending_jobs=queue.waiting_count,
            last_error=errors.last_error
        )
    
    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get list of active jobs"""
        with self._lock:
            jobs = [
                job for job in self.active_jobs.values()
                if job["status"] in ["queued", "processing"]
            ]
            return sorted(jobs, key=lambda j: j["created_at"], reverse=True)
    
    def get_failed_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent failed queries"""
        with self._lock:
            return list(self.failed_queries)[-limit:]
    
    def get_slow_queries(self, threshold_ms: float = 1000, limit: int = 50) -> List[Dict[str, Any]]:
        """Get slow queries from latency history"""
        with self._lock:
            slow = [
                {"latency_ms": lat} for lat in self.latencies
                if lat > threshold_ms
            ]
            return sorted(slow, key=lambda x: x["latency_ms"], reverse=True)[:limit]
    
    def get_metrics_by_org(self, org_id: str) -> Dict[str, Any]:
        """Get metrics for specific organization"""
        with self._lock:
            if org_id not in self.by_org:
                return {}
            
            org_metrics = self.by_org[org_id]
            query_count = org_metrics["query_count"]
            
            return {
                "org_id": org_id,
                "query_count": query_count,
                "avg_latency_ms": (
                    org_metrics["total_latency_ms"] / query_count
                    if query_count > 0 else 0
                ),
                "total_cost": org_metrics["total_cost"],
                "error_count": org_metrics["error_count"],
                "error_rate": (
                    org_metrics["error_count"] / query_count * 100
                    if query_count > 0 else 0
                )
            }
    
    def reset_metrics(self):
        """Reset all metrics (for testing)"""
        with self._lock:
            self.latencies.clear()
            self.errors.clear()
            self.cache_hits.clear()
            self.cache_misses.clear()
            self.queue_waits.clear()
            self.costs.clear()
            self.by_org.clear()
            self.by_role.clear()
            self.by_user.clear()
            self.active_jobs.clear()
            self.failed_queries.clear()


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
