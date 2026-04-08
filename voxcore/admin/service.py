from voxcore.admin.models import Tenant
from voxcore.security.models import User
from voxcore.audit.models import AuditLog

class AdminService:
    def get_tenants(self, db):
        return db.query(Tenant).all()

    def get_users(self, db, tenant_id):
        return db.query(User).filter_by(tenant_id=tenant_id).all()

    def get_usage(self, db, tenant_id):
        logs = db.query(AuditLog).filter_by(tenant_id=tenant_id).all()
        return {
            "queries": len(logs),
            "avg_risk": sum(l.risk_score for l in logs if l.risk_score) / max(len(logs), 1)
        }
