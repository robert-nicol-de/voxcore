class DecisionEngine:
    def evaluate(self, insight):
        """
        Takes enriched EMD insight and decides what action to take
        """
        actions = []
        # 🔴 High-risk decline
        if insight.get("prediction", {}).get("risk") == "HIGH":
            actions.append({
                "type": "alert",
                "priority": "critical",
                "message": insight["narrative"]
            })
            actions.append({
                "type": "email",
                "target": "admin",
                "template": "high_risk_alert"
            })
        # 📉 Revenue decline
        if insight.get("type") == "decline":
            actions.append({
                "type": "report",
                "report_type": "decline_summary"
            })
        # 🧠 Strong root cause
        for rc in insight.get("root_causes", []):
            if rc.get("contribution", 0) > 40:
                actions.append({
                    "type": "alert",
                    "priority": "medium",
                    "message": f"Dominant factor: {rc['value']}"
                })
        return actions
