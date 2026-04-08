class AlertEngine:
    def __init__(self):
        self.alerts = []

    def evaluate(self, insights, user_prefs, user_id):
        triggered = []
        for insight in insights:
            score = insight["confidence"]
            insight_type = insight["type"]
            # 🎯 RULE 1: high confidence
            if score > 0.85:
                triggered.append(insight)
            # 🎯 RULE 2: user preference match
            elif insight_type in user_prefs:
                if user_prefs[insight_type] >= 2:
                    triggered.append(insight)
        for alert in triggered:
            self.alerts.append({
                "user_id": user_id,
                "insight": alert,
                "status": "new"
            })
        return triggered


alert_engine = AlertEngine()
