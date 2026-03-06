"""Repair metrics tracking for monitoring and analytics"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class RepairEvent:
    """Single repair event"""
    timestamp: datetime
    pattern: str  # e.g., "broken_derived_table", "union_all_abuse", etc.
    question_snippet: str
    original_sql_hash: int
    success: bool  # Did repair pass re-validation?
    execution_success: Optional[bool] = None  # Did query execute without error?


@dataclass
class RepairMetrics:
    """Aggregated repair metrics"""
    total_queries: int = 0
    queries_needing_repair: int = 0
    repair_attempts: int = 0
    repair_successes: int = 0
    repair_failures: int = 0
    execution_successes: int = 0
    execution_failures: int = 0
    
    # Pattern breakdown
    pattern_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    pattern_success_rates: Dict[str, float] = field(default_factory=dict)
    
    # Time window
    window_start: datetime = field(default_factory=datetime.now)
    window_end: datetime = field(default_factory=datetime.now)
    
    @property
    def repair_rate(self) -> float:
        """% of queries that needed repair"""
        if self.total_queries == 0:
            return 0.0
        return (self.queries_needing_repair / self.total_queries) * 100
    
    @property
    def repair_success_rate(self) -> float:
        """% of repair attempts that succeeded"""
        if self.repair_attempts == 0:
            return 0.0
        return (self.repair_successes / self.repair_attempts) * 100
    
    @property
    def execution_success_rate(self) -> float:
        """% of repaired queries that executed successfully"""
        total_executed = self.execution_successes + self.execution_failures
        if total_executed == 0:
            return 0.0
        return (self.execution_successes / total_executed) * 100
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "total_queries": self.total_queries,
            "queries_needing_repair": self.queries_needing_repair,
            "repair_rate_percent": round(self.repair_rate, 2),
            "repair_attempts": self.repair_attempts,
            "repair_successes": self.repair_successes,
            "repair_failures": self.repair_failures,
            "repair_success_rate_percent": round(self.repair_success_rate, 2),
            "execution_successes": self.execution_successes,
            "execution_failures": self.execution_failures,
            "execution_success_rate_percent": round(self.execution_success_rate, 2),
            "pattern_counts": dict(self.pattern_counts),
            "pattern_success_rates": {k: round(v, 2) for k, v in self.pattern_success_rates.items()},
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
        }


class RepairMetricsTracker:
    """Track repair metrics over time"""
    
    def __init__(self, window_hours: int = 24):
        self.window_hours = window_hours
        self.events: List[RepairEvent] = []
        self.logger = logging.getLogger(__name__)
    
    def record_query(self, total_queries: int):
        """Record that a query was processed"""
        pass  # Tracked implicitly through repair events
    
    def record_repair_attempt(
        self,
        pattern: str,
        question_snippet: str,
        original_sql_hash: int,
        success: bool
    ):
        """Record a repair attempt"""
        event = RepairEvent(
            timestamp=datetime.now(),
            pattern=pattern,
            question_snippet=question_snippet,
            original_sql_hash=original_sql_hash,
            success=success
        )
        self.events.append(event)
        
        self.logger.info(
            f"Repair event recorded: pattern={pattern}, success={success}",
            extra={
                "pattern": pattern,
                "success": success,
                "question_snippet": question_snippet[:80]
            }
        )
    
    def record_execution_result(self, pattern: str, success: bool):
        """Record execution result for a repaired query"""
        # Find most recent event with this pattern
        for event in reversed(self.events):
            if event.pattern == pattern and event.execution_success is None:
                event.execution_success = success
                break
    
    def get_metrics(self, hours: Optional[int] = None) -> RepairMetrics:
        """Get aggregated metrics for time window"""
        if hours is None:
            hours = self.window_hours
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [e for e in self.events if e.timestamp >= cutoff_time]
        
        metrics = RepairMetrics(
            window_start=cutoff_time,
            window_end=datetime.now()
        )
        
        # Count events
        metrics.repair_attempts = len(recent_events)
        metrics.repair_successes = sum(1 for e in recent_events if e.success)
        metrics.repair_failures = metrics.repair_attempts - metrics.repair_successes
        
        # Execution results
        metrics.execution_successes = sum(1 for e in recent_events if e.execution_success is True)
        metrics.execution_failures = sum(1 for e in recent_events if e.execution_success is False)
        
        # Pattern breakdown
        for event in recent_events:
            metrics.pattern_counts[event.pattern] += 1
        
        # Pattern success rates
        for pattern, count in metrics.pattern_counts.items():
            successes = sum(1 for e in recent_events if e.pattern == pattern and e.success)
            metrics.pattern_success_rates[pattern] = (successes / count * 100) if count > 0 else 0.0
        
        return metrics
    
    def get_top_patterns(self, limit: int = 3, hours: Optional[int] = None) -> List[tuple]:
        """Get top N patterns by frequency"""
        metrics = self.get_metrics(hours)
        sorted_patterns = sorted(
            metrics.pattern_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_patterns[:limit]
    
    def clear_old_events(self, hours: int = 72):
        """Clear events older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        original_count = len(self.events)
        self.events = [e for e in self.events if e.timestamp >= cutoff_time]
        removed = original_count - len(self.events)
        
        if removed > 0:
            self.logger.info(f"Cleared {removed} old repair events")


# Global metrics tracker instance
_metrics_tracker: Optional[RepairMetricsTracker] = None


def get_metrics_tracker() -> RepairMetricsTracker:
    """Get or create global metrics tracker"""
    global _metrics_tracker
    if _metrics_tracker is None:
        _metrics_tracker = RepairMetricsTracker(window_hours=24)
    return _metrics_tracker


def record_repair_attempt(
    pattern: str,
    question_snippet: str,
    original_sql_hash: int,
    success: bool
):
    """Record a repair attempt to global tracker"""
    tracker = get_metrics_tracker()
    tracker.record_repair_attempt(pattern, question_snippet, original_sql_hash, success)


def record_execution_result(pattern: str, success: bool):
    """Record execution result to global tracker"""
    tracker = get_metrics_tracker()
    tracker.record_execution_result(pattern, success)


def get_metrics(hours: Optional[int] = None) -> RepairMetrics:
    """Get current metrics"""
    tracker = get_metrics_tracker()
    return tracker.get_metrics(hours)


def get_top_patterns(limit: int = 3, hours: Optional[int] = None) -> List[tuple]:
    """Get top patterns"""
    tracker = get_metrics_tracker()
    return tracker.get_top_patterns(limit, hours)
