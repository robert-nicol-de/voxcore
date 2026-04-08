"""
MetricsService — Core Metrics Collection Interface

This is the abstraction layer. Storage (in-memory, Redis, etc.)
can be swapped without changing the interface.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from collections import defaultdict
import time
from enum import Enum


class MetricType(str, Enum):
    """Metric categories"""
    QUERY = "query"
    SYSTEM = "system"
    BUSINESS = "business"
    GOVERNANCE = "governance"


@dataclass
class QueryMetric:
    """Single query execution metric"""
    query_id: str
    execution_time_ms: float
    cost_score: int
    rows_returned: int
    cache_hit: bool
    status: str  # "success", "error", "blocked"
    user_id: str
    org_id: str
    policies_applied_count: int
    columns_masked_count: int
    timestamp: float


@dataclass
class SystemMetric:
    """System-level metric snapshot"""
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_rate: float  # 0-100
    throughput_qps: float  # queries per second
    active_jobs: int
    queue_depth: int
    cache_hit_rate: float  # 0-100
    timestamp: float


@dataclass
class BusinessMetric:
    """Business-level metric"""
    org_id: str
    user_id: Optional[str]
    total_queries: int
    avg_cost: float
    total_cost: float
    timestamp: float


@dataclass
class GovernanceMetric:
    """Governance activity metric"""
    policies_triggered: int
    policies_blocked: int
    columns_masked: int
    rbac_denials: int
    cost_limit_hits: int
    timestamp: float


class MetricsService:
    """
    Abstract metrics service interface.
    
    Implementations: InMemoryMetricsService, RedisMetricsService
    """
    
    def __init__(self):
        """Initialize metrics service"""
        pass
    
    def track_query(self, metadata: Dict[str, Any]) -> None:
        """
        Record a query execution metric.
        
        Args:
            metadata: ExecutionMetadata as dict
        """
        raise NotImplementedError
    
    def get_query_metrics(self, limit: int = 100) -> List[QueryMetric]:
        """Get recent query metrics"""
        raise NotImplementedError
    
    def get_system_metrics(self) -> SystemMetric:
        """Get current system metrics"""
        raise NotImplementedError
    
    def get_business_metrics(self, org_id: Optional[str] = None) -> List[BusinessMetric]:
        """Get business metrics for org or all orgs"""
        raise NotImplementedError
    
    def get_governance_metrics(self) -> GovernanceMetric:
        """Get governance activity snapshot"""
        raise NotImplementedError
    
    def get_top_cost_queries(self, limit: int = 10) -> List[QueryMetric]:
        """Get most expensive queries"""
        raise NotImplementedError
    
    def get_top_slow_queries(self, limit: int = 10) -> List[QueryMetric]:
        """Get slowest queries"""
        raise NotImplementedError
    
    def get_failed_queries(self, limit: int = 20) -> List[QueryMetric]:
        """Get recent failed queries"""
        raise NotImplementedError
    
    def get_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get metrics for specific user"""
        raise NotImplementedError
    
    def get_org_metrics(self, org_id: str) -> Dict[str, Any]:
        """Get metrics for specific organization"""
        raise NotImplementedError
    
    def clear_metrics(self) -> None:
        """Clear all metrics (for testing)"""
        raise NotImplementedError


class InMemoryMetricsService(MetricsService):
    """In-memory metrics storage (for dev/testing)"""
    
    def __init__(self, max_queries: int = 10000):
        super().__init__()
        self.query_metrics: List[QueryMetric] = []
        self.max_queries = max_queries
        self.start_time = time.time()
    
    def track_query(self, metadata: Dict[str, Any]) -> None:
        """Record query metric"""
        metric = QueryMetric(
            query_id=metadata.get("query_id", ""),
            execution_time_ms=metadata.get("execution_time_ms", 0),
            cost_score=metadata.get("cost_score", 0),
            rows_returned=metadata.get("rows_returned", 0),
            cache_hit="cache_hit" in metadata.get("execution_flags", []),
            status=metadata.get("validation_status", "unknown"),
            user_id=metadata.get("user_id", ""),
            org_id=metadata.get("org_id", ""),
            policies_applied_count=len(metadata.get("policies_applied", [])),
            columns_masked_count=len(metadata.get("columns_masked", [])),
            timestamp=metadata.get("timestamp", time.time())
        )
        
        self.query_metrics.append(metric)
        
        # Trim if over limit
        if len(self.query_metrics) > self.max_queries:
            self.query_metrics = self.query_metrics[-self.max_queries:]
    
    def get_query_metrics(self, limit: int = 100) -> List[QueryMetric]:
        """Get recent query metrics"""
        return self.query_metrics[-limit:]
    
    def get_system_metrics(self) -> SystemMetric:
        """Calculate system metrics from queries"""
        if not self.query_metrics:
            return SystemMetric(
                avg_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                error_rate=0,
                throughput_qps=0,
                active_jobs=0,
                queue_depth=0,
                cache_hit_rate=0,
                timestamp=time.time()
            )
        
        recent = self.query_metrics[-1000:]  # Last 1000 queries
        latencies = [m.execution_time_ms for m in recent]
        errors = [m for m in recent if m.status != "success"]
        cache_hits = [m for m in recent if m.cache_hit]
        
        latencies_sorted = sorted(latencies)
        
        # Calculate uptime in seconds
        uptime = time.time() - self.start_time
        throughput = len(recent) / max(uptime, 1)
        
        return SystemMetric(
            avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
            p95_latency_ms=latencies_sorted[int(len(latencies_sorted) * 0.95)] if latencies else 0,
            p99_latency_ms=latencies_sorted[int(len(latencies_sorted) * 0.99)] if latencies else 0,
            error_rate=(len(errors) / len(recent) * 100) if recent else 0,
            throughput_qps=throughput,
            active_jobs=0,  # Would need real tracking
            queue_depth=0,  # Would need real tracking
            cache_hit_rate=(len(cache_hits) / len(recent) * 100) if recent else 0,
            timestamp=time.time()
        )
    
    def get_business_metrics(self, org_id: Optional[str] = None) -> List[BusinessMetric]:
        """Get business metrics by org"""
        metrics_by_org = defaultdict(lambda: {
            "total": 0,
            "cost": 0,
            "users": set()
        })
        
        for metric in self.query_metrics:
            if org_id and metric.org_id != org_id:
                continue
            
            m = metrics_by_org[metric.org_id]
            m["total"] += 1
            m["cost"] += metric.cost_score
            m["users"].add(metric.user_id)
        
        result = []
        for org, data in metrics_by_org.items():
            result.append(BusinessMetric(
                org_id=org,
                user_id=None,
                total_queries=data["total"],
                avg_cost=data["cost"] / data["total"] if data["total"] > 0 else 0,
                total_cost=data["cost"],
                timestamp=time.time()
            ))
        
        return result
    
    def get_governance_metrics(self) -> GovernanceMetric:
        """Get governance activity"""
        policies_triggered = 0
        blocked = sum(1 for m in self.query_metrics if m.status == "blocked")
        columns_masked = sum(m.columns_masked_count for m in self.query_metrics)
        
        for metric in self.query_metrics:
            policies_triggered += metric.policies_applied_count
        
        return GovernanceMetric(
            policies_triggered=policies_triggered,
            policies_blocked=blocked,
            columns_masked=columns_masked,
            rbac_denials=0,
            cost_limit_hits=sum(1 for m in self.query_metrics if m.cost_score > 80),
            timestamp=time.time()
        )
    
    def get_top_cost_queries(self, limit: int = 10) -> List[QueryMetric]:
        """Get most expensive queries"""
        return sorted(self.query_metrics, key=lambda m: m.cost_score, reverse=True)[:limit]
    
    def get_top_slow_queries(self, limit: int = 10) -> List[QueryMetric]:
        """Get slowest queries"""
        return sorted(self.query_metrics, key=lambda m: m.execution_time_ms, reverse=True)[:limit]
    
    def get_failed_queries(self, limit: int = 20) -> List[QueryMetric]:
        """Get recent failed queries"""
        failed = [m for m in self.query_metrics if m.status != "success"]
        return failed[-limit:]
    
    def get_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get metrics for user"""
        user_metrics = [m for m in self.query_metrics if m.user_id == user_id]
        if not user_metrics:
            return {}
        
        return {
            "total_queries": len(user_metrics),
            "avg_cost": sum(m.cost_score for m in user_metrics) / len(user_metrics),
            "avg_latency_ms": sum(m.execution_time_ms for m in user_metrics) / len(user_metrics),
            "error_count": sum(1 for m in user_metrics if m.status != "success"),
            "last_query_time": user_metrics[-1].timestamp if user_metrics else 0,
        }
    
    def get_org_metrics(self, org_id: str) -> Dict[str, Any]:
        """Get metrics for organization"""
        org_metrics = [m for m in self.query_metrics if m.org_id == org_id]
        if not org_metrics:
            return {}
        
        return {
            "total_queries": len(org_metrics),
            "avg_cost": sum(m.cost_score for m in org_metrics) / len(org_metrics),
            "total_cost": sum(m.cost_score for m in org_metrics),
            "avg_latency_ms": sum(m.execution_time_ms for m in org_metrics) / len(org_metrics),
            "unique_users": len(set(m.user_id for m in org_metrics)),
            "error_count": sum(1 for m in org_metrics if m.status != "success"),
            "columns_masked": sum(m.columns_masked_count for m in org_metrics),
        }
    
    def clear_metrics(self) -> None:
        """Clear all metrics"""
        self.query_metrics = []


# Global instance (will be used by default)
_metrics_service: Optional[MetricsService] = None


def get_metrics_service() -> MetricsService:
    """Get or create global metrics service"""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = InMemoryMetricsService()
    return _metrics_service


def set_metrics_service(service: MetricsService) -> None:
    """Set custom metrics service"""
    global _metrics_service
    _metrics_service = service
