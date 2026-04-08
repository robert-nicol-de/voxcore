"""
VoxCore Conversation Memory
Stores and retrieves per-session conversational context using Redis.
"""
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

class ConversationMemory:
    def store_message(self, session_id, user_msg, response):
        key = f"session:{session_id}"
        history = self.get_history(session_id)
        history.append({"user": user_msg, "assistant": response})
        r.set(key, json.dumps(history), ex=1800)

    def get_history(self, session_id):
        key = f"session:{session_id}"
        data = r.get(key)
        return json.loads(data) if data else []
