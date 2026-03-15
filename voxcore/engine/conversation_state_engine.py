"""
VoxCore Conversational State Engine (CSE)
Tracks and updates evolving state for each session.
"""
class ConversationStateEngine:
    def __init__(self):
        self.states = {}

    def get_state(self, session_id):
        return self.states.get(session_id, {})

    def update_state(self, session_id, updates):
        state = self.states.get(session_id, {})
        state.update(updates)
        self.states[session_id] = state
        return state
