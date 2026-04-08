class UserBehaviorMemory:
    def __init__(self):
        self.user_events = {}

    def store(self, user_id: str, event: dict):
        if user_id not in self.user_events:
            self.user_events[user_id] = []
        self.user_events[user_id].append(event)

    def get_preferences(self, user_id: str):
        prefs = {}
        for e in self.user_events.get(user_id, []):
            key = e.get("insight_type")
            if key:
                prefs[key] = prefs.get(key, 0) + 1
        return prefs

user_behavior = UserBehaviorMemory()
