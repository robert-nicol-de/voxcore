import uuid
from voxcore.alerts.models import Alert

class AlertEngine:
    def evaluate_insight(self, db, insight, tenant_id):
        alert = None
        # 🚨 Decline detection
        if insight["type"] == "decline_trend" and insight["impact"] > 15:
            alert = self._create_alert(
                tenant_id,
                "decline",
                "high",
                insight
            )
        # 🚨 Spike detection
        if insight["type"] == "anomaly_detection":
            alert = self._create_alert(
                tenant_id,
                "spike",
                "high",
                insight
            )
        if alert:
            db.add(alert)
            db.commit()
        return alert

    def _create_alert(self, tenant_id, alert_type, severity, insight):
        return Alert(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            type=alert_type,
            severity=severity,
            message=insight["insight"],
            metric=insight.get("metric"),
            entity=insight.get("entity"),
            confidence=insight.get("confidence", 0.9)
        )
