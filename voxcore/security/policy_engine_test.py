from voxcore.security.policy_engine import DataPolicyEngine

engine = DataPolicyEngine()

decision, reasons = engine.evaluate(
    sql="SELECT * FROM sales",
    risk_score=60,
    user_role="analyst",
    metadata={}
)

print(decision, reasons)
