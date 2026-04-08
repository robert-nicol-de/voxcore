import uuid
import json
from voxcore.audit.models import AuditLog

class AuditService:
    def log(self, db, **kwargs):
        log = AuditLog(
            id=str(uuid.uuid4()),
            tenant_id=kwargs.get("tenant_id"),
            user_id=kwargs.get("user_id"),
            action=kwargs.get("action"),
            resource_type=kwargs.get("resource_type"),
            resource_id=kwargs.get("resource_id"),
            query=kwargs.get("query"),
            status=kwargs.get("status"),
            risk_score=kwargs.get("risk_score"),
            execution_time_ms=kwargs.get("execution_time_ms"),
            rows_returned=kwargs.get("rows_returned"),
            metadata=json.dumps(kwargs.get("metadata", {}))
        )
        db.add(log)
        db.commit()
