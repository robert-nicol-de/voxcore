"""
Firewall Event Logging Models
Stores firewall inspection events for audit and analytics
"""

from datetime import datetime
from typing import Optional, List, Dict, Any


class FirewallEvent:
    """
    Represents a firewall inspection event
    Used for logging and analytics
    """
    
    def __init__(
        self,
        query: str,
        generated_sql: str,
        risk_score: int,
        risk_level: str,
        violations: List[str],
        action: str,
        user: Optional[str] = None,
        database: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        self.timestamp = datetime.utcnow()
        self.query = query
        self.generated_sql = generated_sql
        self.risk_score = risk_score
        self.risk_level = risk_level
        self.violations = violations
        self.action = action
        self.user = user or "unknown"
        self.database = database or "unknown"
        self.session_id = session_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "query": self.query,
            "generated_sql": self.generated_sql,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "violations": self.violations,
            "action": self.action,
            "user": self.user,
            "database": self.database,
            "session_id": self.session_id
        }


class FirewallEventLog:
    """In-memory firewall event log"""
    
    def __init__(self, max_events: int = 1000):
        self.events: List[FirewallEvent] = []
        self.max_events = max_events
        self.action_counts = {"allow": 0, "rewrite": 0, "block": 0}  # Track all actions
    
    def log_event(self, event: FirewallEvent) -> None:
        """Log a firewall event - ALL queries are logged, not just blocked ones"""
        self.events.append(event)
        self.action_counts[event.action] = self.action_counts.get(event.action, 0) + 1
        
        # Keep only recent events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
    
    def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent firewall events"""
        return [e.to_dict() for e in self.events[-limit:]]
    
    def get_blocked_events(self) -> List[Dict[str, Any]]:
        """Get only blocked queries"""
        blocked = [e for e in self.events if e.action == "block"]
        return [e.to_dict() for e in blocked[-100:]]
    
    def get_high_risk_events(self) -> List[Dict[str, Any]]:
        """Get high-risk queries"""
        high_risk = [e for e in self.events if e.risk_level == "HIGH"]
        return [e.to_dict() for e in high_risk[-100:]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get firewall statistics"""
        if not self.events:
            return {
                "total_inspected": 0,
                "blocked_count": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "block_rate": 0.0
            }
        
        total = len(self.events)
        blocked = sum(1 for e in self.events if e.action == "block")
        high_risk = sum(1 for e in self.events if e.risk_level == "HIGH")
        medium_risk = sum(1 for e in self.events if e.risk_level == "MEDIUM")
        low_risk = sum(1 for e in self.events if e.risk_level == "LOW")
        
        return {
            "total_inspected": total,
            "blocked_count": blocked,
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "block_rate": (blocked / total * 100) if total > 0 else 0.0
        }


# Global event log
firewall_event_log = FirewallEventLog()
