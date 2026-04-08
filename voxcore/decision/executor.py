class ActionExecutor:
    def execute(self, actions, context):
        results = []
        for action in actions:
            if action["type"] == "alert":
                results.append(self._trigger_alert(action, context))
            elif action["type"] == "email":
                results.append(self._send_email(action, context))
            elif action["type"] == "report":
                results.append(self._generate_report(action, context))
        return results
    def _trigger_alert(self, action, context):
        print("🚨 Alert:", action["message"])
        return {"status": "alert_sent"}
    def _send_email(self, action, context):
        print("📧 Email sent to", action["target"])
        return {"status": "email_sent"}
    def _generate_report(self, action, context):
        print("📊 Report generated:", action["report_type"])
        return {"status": "report_created"}
