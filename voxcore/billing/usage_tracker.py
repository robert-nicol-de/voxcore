class UsageTracker:
    def track(self, tenant_id, usage_type):
        print(f"Tracking {usage_type} for {tenant_id}")

USAGE_COST = {
    "insight": 1,
    "prediction": 2,
    "alert": 1,
    "report": 3
}

def enforce_limits(tenant):
    if tenant.usage > tenant.plan_limit:
        raise Exception("Upgrade required")
