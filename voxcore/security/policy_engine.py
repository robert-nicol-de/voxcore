
class PolicyDecision:
    ALLOW = "allow"
    BLOCK = "block"
    REQUIRE_APPROVAL = "require_approval"
    REWRITE = "rewrite"


class PolicyExplain:
    def __init__(self, decision, reason, rule):
        self.decision = decision
        self.reason = reason
        self.rule = rule
    def as_dict(self):
        return {"decision": self.decision, "reason": self.reason, "rule": self.rule}


class DataPolicyEngine:
    def evaluate(self, sql, risk_score, user_role, metadata):
        # Rule 1: Block destructive
        if sql.strip().upper().startswith(("DROP", "DELETE", "TRUNCATE", "ALTER")):
            return PolicyExplain(PolicyDecision.BLOCK, "Destructive query", "RULE_BLOCK_DESTRUCTIVE")

        # Rule 2: Sensitive data
        if metadata.get("contains_sensitive") and user_role != "admin":
            return PolicyExplain(PolicyDecision.BLOCK, "Sensitive data access denied", "RULE_BLOCK_SENSITIVE")

        # Rule 3: High risk
        if risk_score > 80:
            return PolicyExplain(PolicyDecision.REQUIRE_APPROVAL, "High risk query", "RULE_REQUIRE_APPROVAL_RISK")

        # Rule 4: Medium risk → rewrite
        if risk_score > 50:
            return PolicyExplain(PolicyDecision.REWRITE, "Query needs optimization", "RULE_REWRITE_MEDIUM_RISK")

        return PolicyExplain(PolicyDecision.ALLOW, "Allowed", "RULE_ALLOW_DEFAULT")
