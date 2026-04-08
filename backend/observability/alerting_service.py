"""
AlertingService — Production Alert System

Detects anomalies and routes alerts to appropriate channels.
Starts simple, can be enhanced to Slack/Email/PagerDuty.
"""

from typing import Callable, List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts"""
    HIGH_LATENCY = "high_latency"
    HIGH_ERROR_RATE = "high_error_rate"
    HIGH_COST = "high_cost"
    QUERY_BLOCKED = "query_blocked"
    POLICY_VIOLATION = "policy_violation"
    CACHE_MISS_SPIKE = "cache_miss_spike"
    QUEUE_BUILDUP = "queue_buildup"
    CUSTOM = "custom"


@dataclass
class Alert:
    """Single alert"""
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    metric_value: Optional[Any] = None
    threshold: Optional[Any] = None
    timestamp: Optional[float] = None
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp,
            "context": self.context,
        }


class AlertHandler:
    """Base class for alert routing"""
    
    def handle_alert(self, alert: Alert) -> bool:
        """
        Handle an alert.
        
        Args:
            alert: Alert to handle
        
        Returns:
            True if handled successfully
        """
        raise NotImplementedError


class LoggerAlertHandler(AlertHandler):
    """Route alerts to logger"""
    
    def handle_alert(self, alert: Alert) -> bool:
        """Log alert"""
        if alert.severity == AlertSeverity.CRITICAL:
            logger.critical(f"[{alert.type.value}] {alert.title}: {alert.message}")
        elif alert.severity == AlertSeverity.WARNING:
            logger.warning(f"[{alert.type.value}] {alert.title}: {alert.message}")
        else:
            logger.info(f"[{alert.type.value}] {alert.title}: {alert.message}")
        return True


class ConsoleAlertHandler(AlertHandler):
    """Print alerts to console"""
    
    def handle_alert(self, alert: Alert) -> bool:
        """Print alert"""
        severity_symbol = {
            AlertSeverity.CRITICAL: "🔴",
            AlertSeverity.WARNING: "🟡",
            AlertSeverity.INFO: "🟢"
        }
        
        symbol = severity_symbol.get(alert.severity, "•")
        print(
            f"{symbol} {alert.severity.value.upper()} | "
            f"{alert.type.value} | "
            f"{alert.title}: {alert.message}"
        )
        return True


class SlackAlertHandler(AlertHandler):
    """Route alerts to Slack (stub - implement with webhook)"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def handle_alert(self, alert: Alert) -> bool:
        """Send to Slack"""
        # Stub implementation
        logger.info(f"[SLACK] Would send to {self.webhook_url}: {alert.title}")
        return True


class AlertingService:
    """
    Monitors metrics and generates alerts.
    
    Usage:
        alerting = AlertingService()
        alerting.check_query_metrics(latency_ms, cost_score, status)
    """
    
    def __init__(self):
        self.handlers: List[AlertHandler] = []
        self.alert_history: List[Alert] = []
        self.max_history = 10000
        
        # Default handlers
        self.add_handler(LoggerAlertHandler())
        self.add_handler(ConsoleAlertHandler())
    
    def add_handler(self, handler: AlertHandler) -> None:
        """Register alert handler"""
        self.handlers.append(handler)
    
    def _emit_alert(self, alert: Alert) -> None:
        """Emit alert to all handlers"""
        alert.timestamp = alert.timestamp or datetime.utcnow().timestamp()
        
        # Store in history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        # Route to handlers
        for handler in self.handlers:
            try:
                handler.handle_alert(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {str(e)}")
    
    def check_query_metrics(
        self,
        query_id: str,
        execution_time_ms: float,
        cost_score: int,
        status: str,
        user_id: str = "",
        org_id: str = ""
    ) -> None:
        """
        Check query metrics for anomalies.
        
        Args:
            query_id: Query identifier
            execution_time_ms: Execution time in milliseconds
            cost_score: Governance cost (0-100)
            status: Query status (success/error/blocked)
            user_id: User who ran query
            org_id: Organization
        """
        
        # Check latency
        if execution_time_ms > 5000:  # 5 seconds
            self._emit_alert(Alert(
                type=AlertType.HIGH_LATENCY,
                severity=AlertSeverity.WARNING,
                title="High Query Latency",
                message=f"Query took {execution_time_ms}ms (threshold: 5000ms)",
                metric_value=execution_time_ms,
                threshold=5000,
                context={"query_id": query_id, "user_id": user_id}
            ))
        
        # Check cost
        if cost_score > 80:
            self._emit_alert(Alert(
                type=AlertType.HIGH_COST,
                severity=AlertSeverity.WARNING,
                title="High Cost Query",
                message=f"Query cost score: {cost_score}/100 (threshold: 80)",
                metric_value=cost_score,
                threshold=80,
                context={"query_id": query_id, "user_id": user_id, "org_id": org_id}
            ))
        
        # Check status
        if status == "blocked":
            self._emit_alert(Alert(
                type=AlertType.QUERY_BLOCKED,
                severity=AlertSeverity.WARNING,
                title="Query Blocked by Governance",
                message=f"Query blocked for user {user_id} in {org_id}",
                context={"query_id": query_id, "user_id": user_id, "org_id": org_id}
            ))
        elif status == "error":
            self._emit_alert(Alert(
                type=AlertType.HIGH_ERROR_RATE,
                severity=AlertSeverity.WARNING,
                title="Query Execution Error",
                message=f"Query {query_id} failed",
                context={"query_id": query_id, "user_id": user_id}
            ))
    
    def check_system_metrics(
        self,
        avg_latency_ms: float,
        error_rate: float,
        queue_depth: int
    ) -> None:
        """
        Check system-level metrics.
        
        Args:
            avg_latency_ms: Average query latency
            error_rate: Error percentage (0-100)
            queue_depth: Jobs waiting in queue
        """
        
        # Check average latency
        if avg_latency_ms > 2000:
            self._emit_alert(Alert(
                type=AlertType.HIGH_LATENCY,
                severity=AlertSeverity.CRITICAL if avg_latency_ms > 5000 else AlertSeverity.WARNING,
                title="High Average Latency",
                message=f"System avg latency: {avg_latency_ms}ms",
                metric_value=avg_latency_ms,
                threshold=2000
            ))
        
        # Check error rate
        if error_rate > 5:
            self._emit_alert(Alert(
                type=AlertType.HIGH_ERROR_RATE,
                severity=AlertSeverity.CRITICAL if error_rate > 10 else AlertSeverity.WARNING,
                title="High Error Rate",
                message=f"Error rate: {error_rate}% (threshold: 5%)",
                metric_value=error_rate,
                threshold=5
            ))
        
        # Check queue buildup
        if queue_depth > 100:
            self._emit_alert(Alert(
                type=AlertType.QUEUE_BUILDUP,
                severity=AlertSeverity.WARNING,
                title="Queue Buildup",
                message=f"Queue depth: {queue_depth} jobs (threshold: 100)",
                metric_value=queue_depth,
                threshold=100
            ))
    
    def custom_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit custom alert.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Severity level
            context: Additional context
        """
        self._emit_alert(Alert(
            type=AlertType.CUSTOM,
            severity=severity,
            title=title,
            message=message,
            context=context
        ))
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return [a.to_dict() for a in self.alert_history[-limit:]]
    
    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get all critical alerts"""
        critical = [
            a for a in self.alert_history
            if a.severity == AlertSeverity.CRITICAL
        ]
        return [a.to_dict() for a in critical[-20:]]


# Global instance
_alerting_service: Optional[AlertingService] = None


def get_alerting_service() -> AlertingService:
    """Get or create global alerting service"""
    global _alerting_service
    if _alerting_service is None:
        _alerting_service = AlertingService()
    return _alerting_service


def set_alerting_service(service: AlertingService) -> None:
    """Set custom alerting service"""
    global _alerting_service
    _alerting_service = service
