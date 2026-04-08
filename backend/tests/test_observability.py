"""
Comprehensive tests for STEP 10 — Observability System

Tests cover:
- Structured logging
- Metrics collection
- Query tracking
- Dashboard API
"""

import pytest
from datetime import datetime, timedelta
import uuid

from backend.observability.structured_logger import (
    StructuredLogger, QueryLogger, PolicyLogger, PerformanceLogger, ErrorLogger,
    set_correlation_id, set_request_context, correlation_id, org_id_ctx, user_id_ctx
)
from backend.observability.metrics_collector import (
    MetricsCollector, get_metrics_collector,
    LatencyMetrics, ErrorMetrics, CacheMetrics, QueueMetrics, CostMetrics
)
from backend.observability.query_tracker import (
    QueryTracker, QueryMetadata, QueryStatus, get_query_tracker
)


class TestStructuredLogger:
    """Test structured logging"""
    
    def test_structured_logger_creation(self):
        """Test creating structured logger"""
        logger = StructuredLogger("test_logger")
        assert logger.name == "test_logger"
    
    def test_correlation_id_context(self):
        """Test correlation ID in context"""
        corr_id = str(uuid.uuid4())
        set_correlation_id(corr_id)
        
        assert correlation_id.get() == corr_id
    
    def test_request_context(self):
        """Test request context (org, user, session)"""
        org_id = "acme_corp"
        user_id = "user_123"
        session_id = "session_456"
        
        set_request_context(org_id, user_id, session_id)
        
        assert org_id_ctx.get() == org_id
        assert user_id_ctx.get() == user_id
    
    def test_query_logger_submission(self):
        """Test query logger submission event"""
        logger = QueryLogger()
        
        logger.query_submitted(
            query_id="q1",
            sql="SELECT * FROM employees",
            org_id="acme",
            user_id="user_123",
            user_role="analyst"
        )
        # Should not raise
    
    def test_query_logger_completion(self):
        """Test query logger completion event"""
        logger = QueryLogger()
        
        logger.query_completed(
            query_id="q1",
            execution_time_ms=123.45,
            rows_returned=100,
            cost_score=5.5
        )
        # Should not raise
    
    def test_query_logger_failure(self):
        """Test query logger failure event"""
        logger = QueryLogger()
        error = Exception("Database connection failed")
        
        logger.query_failed(
            query_id="q1",
            execution_time_ms=45.0,
            error=error,
            error_message="Database connection failed"
        )
        # Should not raise


class TestMetricsCollector:
    """Test metrics collection"""
    
    def test_metrics_collector_creation(self):
        """Test creating metrics collector"""
        collector = MetricsCollector()
        assert collector is not None
    
    def test_record_query(self):
        """Test recording query metrics"""
        collector = MetricsCollector()
        
        collector.record_query(
            query_id="q1",
            org_id="acme",
            user_id="user_123",
            user_role="analyst",
            execution_time_ms=150.5,
            cost_score=5.0,
            rows_returned=100,
            success=True
        )
        
        latency = collector.get_latency_metrics()
        assert latency.count == 1
        assert latency.mean_ms == 150.5
    
    def test_latency_metrics(self):
        """Test latency metric calculation"""
        collector = MetricsCollector()
        
        # Record multiple queries
        for i in range(10):
            collector.record_query(
                query_id=f"q{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst",
                execution_time_ms=float(100 + i * 10),
                cost_score=5.0,
                rows_returned=100,
                success=True
            )
        
        latency = collector.get_latency_metrics()
        
        assert latency.count == 10
        assert latency.min_ms == 100
        assert latency.max_ms == 190
        assert 100 <= latency.mean_ms <= 190
        assert latency.p95_ms > latency.mean_ms
        assert latency.p99_ms >= latency.p95_ms
    
    def test_error_metrics(self):
        """Test error metric calculation"""
        collector = MetricsCollector()
        
        # Record successful queries
        for i in range(95):
            collector.record_query(
                query_id=f"q{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst",
                execution_time_ms=100,
                cost_score=5.0,
                rows_returned=100,
                success=True
            )
        
        # Record failed queries
        for i in range(5):
            collector.record_query(
                query_id=f"q_fail_{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst",
                execution_time_ms=50,
                cost_score=0,
                rows_returned=0,
                success=False,
                error_message="Query execution failed"
            )
        
        errors = collector.get_error_metrics()
        
        assert errors.total_errors == 5
        assert abs(errors.error_rate_percent - 5.0) < 0.1
    
    def test_cache_metrics(self):
        """Test cache metrics"""
        collector = MetricsCollector()
        
        # Record cache hits
        for i in range(80):
            collector.record_cache_hit(
                query_id=f"q_hit_{i}",
                hit_time_ms=10.0,
                rows_returned=100,
                cache_key=f"cache_{i % 10}"
            )
        
        # Record cache misses
        for i in range(20):
            collector.record_cache_miss(
                query_id=f"q_miss_{i}",
                miss_time_ms=100.0,
                cache_key=f"cache_{i % 5}"
            )
        
        cache = collector.get_cache_metrics()
        
        assert cache.hits == 80
        assert cache.misses == 20
        assert cache.hit_rate_percent == 80.0
    
    def test_queue_metrics(self):
        """Test queue metrics"""
        collector = MetricsCollector()
        
        # Add active jobs
        for i in range(15):
            collector.add_active_job(
                job_id=f"job_{i}",
                query_id=f"q{i}",
                org_id="acme",
                user_id="user_123",
                status="queued" if i < 10 else "processing",
                created_at=datetime.utcnow().isoformat()
            )
        
        # Record queue wait times
        for i in range(5):
            collector.record_queue_wait(
                job_id=f"job_{i}",
                wait_time_ms=100.0 + i * 10
            )
        
        queue = collector.get_queue_metrics()
        
        assert queue.waiting_count == 10
        assert queue.processing_count == 5
    
    def test_cost_metrics(self):
        """Test cost metrics"""
        collector = MetricsCollector()
        
        # Record queries with costs
        for i in range(5):
            collector.record_query(
                query_id=f"q{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst",
                execution_time_ms=100,
                cost_score=float(10 + i),
                rows_returned=100,
                success=True
            )
        
        cost = collector.get_cost_metrics()
        
        assert cost.total_cost == 60.0  # 10+11+12+13+14
        assert cost.avg_cost_per_query == 12.0
    
    def test_system_health_healthy(self):
        """Test system health status"""
        collector = MetricsCollector()
        
        # Add successful queries
        for i in range(100):
            collector.record_query(
                query_id=f"q{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst",
                execution_time_ms=100,
                cost_score=5.0,
                rows_returned=100,
                success=True
            )
        
        health = collector.get_system_health()
        
        assert health.status == "healthy"
    
    def test_get_active_jobs(self):
        """Test getting active jobs"""
        collector = MetricsCollector()
        
        collector.add_active_job(
            job_id="job_1",
            query_id="q1",
            org_id="acme",
            user_id="user_123",
            status="processing",
            created_at=datetime.utcnow().isoformat()
        )
        
        jobs = collector.get_active_jobs()
        
        assert len(jobs) == 1
        assert jobs[0]["job_id"] == "job_1"


class TestQueryTracker:
    """Test query tracking"""
    
    def test_create_query(self):
        """Test creating new query"""
        tracker = QueryTracker()
        
        query_id = tracker.create_query(
            sql="SELECT * FROM employees",
            org_id="acme",
            user_id="user_123",
            user_role="analyst"
        )
        
        assert query_id is not None
        assert len(query_id) > 0
    
    def test_query_status_progression(self):
        """Test query status progression"""
        tracker = QueryTracker()
        
        query_id = tracker.create_query(
            sql="SELECT * FROM employees",
            org_id="acme",
            user_id="user_123",
            user_role="analyst"
        )
        
        # Check initial status
        query = tracker.get_query(query_id)
        assert query.status == QueryStatus.SUBMITTED
        
        # Mark queued
        tracker.mark_queued(query_id)
        query = tracker.get_query(query_id)
        assert query.status == QueryStatus.QUEUED
        
        # Mark executing
        tracker.mark_executing(query_id)
        query = tracker.get_query(query_id)
        assert query.status == QueryStatus.EXECUTING
        
        # Mark completed
        tracker.mark_completed(
            query_id,
            rows_returned=100,
            cost_score=5.0
        )
        query = tracker.get_query(query_id)
        assert query.status == QueryStatus.COMPLETED
    
    def test_query_timing(self):
        """Test query timing calculation"""
        tracker = QueryTracker()
        
        query_id = tracker.create_query(
            sql="SELECT * FROM employees",
            org_id="acme",
            user_id="user_123",
            user_role="analyst"
        )
        
        tracker.mark_queued(query_id)
        tracker.mark_executing(query_id)
        tracker.mark_completed(query_id, rows_returned=100, cost_score=5.0)
        
        query = tracker.get_query(query_id)
        
        # Times should be recorded
        assert query.submitted_at is not None
        assert query.queued_at is not None
        assert query.execution_started_at is not None
        assert query.execution_completed_at is not None
        assert query.queue_wait_ms >= 0
        assert query.execution_time_ms >= 0
        assert query.total_time_ms >= 0
    
    def test_mark_cached(self):
        """Test marking query as cached"""
        tracker = QueryTracker()
        
        query_id = tracker.create_query(
            sql="SELECT * FROM employees",
            org_id="acme",
            user_id="user_123",
            user_role="analyst"
        )
        
        tracker.mark_cached(
            query_id,
            cache_key="cache_key_123",
            cache_age_seconds=3600,
            rows_returned=100
        )
        
        query = tracker.get_query(query_id)
        
        assert query.status == QueryStatus.CACHED
        assert query.cache_hit is True
        assert query.cache_key == "cache_key_123"
        assert query.cache_age_seconds == 3600
    
    def test_mark_failed(self):
        """Test marking query as failed"""
        tracker = QueryTracker()
        
        query_id = tracker.create_query(
            sql="SELECT * FROM employees",
            org_id="acme",
            user_id="user_123",
            user_role="analyst"
        )
        
        tracker.mark_failed(
            query_id,
            error_message="Database connection timeout",
            error_type="DatabaseError"
        )
        
        query = tracker.get_query(query_id)
        
        assert query.status == QueryStatus.FAILED
        assert query.error is True
        assert query.error_message == "Database connection timeout"
        assert query.error_type == "DatabaseError"
    
    def test_get_queries_by_org(self):
        """Test getting queries by organization"""
        tracker = QueryTracker()
        
        # Create queries for different orgs
        for i in range(5):
            tracker.create_query(
                sql=f"SELECT * FROM table{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst"
            )
        
        for i in range(3):
            tracker.create_query(
                sql=f"SELECT * FROM table{i}",
                org_id="techcorp",
                user_id="user_456",
                user_role="admin"
            )
        
        acme_queries = tracker.get_queries_by_org("acme")
        assert len(acme_queries) == 5
        
        techcorp_queries = tracker.get_queries_by_org("techcorp")
        assert len(techcorp_queries) == 3
    
    def test_get_failed_queries(self):
        """Test getting failed queries"""
        tracker = QueryTracker()
        
        # Create successful queries
        for i in range(7):
            query_id = tracker.create_query(
                sql=f"SELECT * FROM table{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst"
            )
            tracker.mark_completed(query_id, rows_returned=100)
        
        # Create failed queries
        for i in range(3):
            query_id = tracker.create_query(
                sql=f"SELECT * FROM table{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst"
            )
            tracker.mark_failed(query_id, error_message="Error")
        
        failed = tracker.get_failed_queries()
        assert len(failed) == 3
    
    def test_get_slow_queries(self):
        """Test getting slow queries"""
        tracker = QueryTracker()
        
        # Create queries with different execution times
        execution_times = [100, 200, 500, 1000, 1500, 2000, 2500]
        for i, exec_time in enumerate(execution_times):
            # Simulate slow execution by setting timestamps manually
            query_id = tracker.create_query(
                sql=f"SELECT * FROM table{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst"
            )
            tracker.mark_executing(query_id)
            tracker.mark_completed(query_id, rows_returned=100)
            
            # Manually set execution time for testing
            query = tracker.get_query(query_id)
            if query:
                query.execution_time_ms = float(exec_time)
        
        slow = tracker.get_slow_queries(threshold_ms=1000)
        
        # Should get queries slower than 1000ms
        assert len(slow) >= 4  # 1000, 1500, 2000, 2500
    
    def test_cache_statistics(self):
        """Test cache statistics"""
        tracker = QueryTracker()
        
        # Create cached queries
        for i in range(80):
            query_id = tracker.create_query(
                sql=f"SELECT * FROM table{i % 10}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst"
            )
            tracker.mark_cached(
                query_id,
                cache_key=f"cache_{i % 10}",
                cache_age_seconds=3600,
                rows_returned=100
            )
        
        # Create non-cached queries
        for i in range(20):
            query_id = tracker.create_query(
                sql=f"SELECT * FROM new_table{i}",
                org_id="acme",
                user_id="user_123",
                user_role="analyst"
            )
            tracker.mark_completed(query_id, rows_returned=100)
        
        stats = tracker.get_cache_stats()
        
        assert stats["cache_hits"] == 80
        assert stats["cache_misses"] == 20


class TestObservabilityIntegration:
    """End-to-end observability integration tests"""
    
    def test_full_query_lifecycle(self):
        """Test full query lifecycle with all components"""
        tracker = get_query_tracker()
        collector = get_metrics_collector()
        
        # Clear any previous data
        collector.reset_metrics()
        tracker.queries.clear()
        
        # Create query
        query_id = tracker.create_query(
            sql="SELECT * FROM employees",
            org_id="acme",
            user_id="user_123",
            user_role="analyst"
        )
        
        # Record in metrics
        collector.record_query(
            query_id=query_id,
            org_id="acme",
            user_id="user_123",
            user_role="analyst",
            execution_time_ms=150.0,
            cost_score=5.5,
            rows_returned=100,
            success=True
        )
        
        # Update tracker
        tracker.mark_queued(query_id)
        tracker.mark_executing(query_id)
        tracker.mark_completed(query_id, rows_returned=100, cost_score=5.5)
        
        # Verify tracking
        query = tracker.get_query(query_id)
        assert query.status == QueryStatus.COMPLETED
        
        # Verify metrics collected
        latency = collector.get_latency_metrics()
        assert latency.count >= 1
        assert latency.mean_ms >= 150.0
        
        cost = collector.get_cost_metrics()
        assert cost.total_cost >= 5.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
