"""
VoxCore Conversation Memory
Stores and retrieves per-session conversational context.
"""
class ConversationMemory:
    def __init__(self):
        self.sessions = {}

    def store_message(self, session_id, user_msg, response):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"user": user_msg, "assistant": response})

    def get_history(self, session_id):
        return self.sessions.get(session_id, [])
