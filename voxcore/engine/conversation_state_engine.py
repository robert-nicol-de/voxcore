"""
VoxCore Conversational State Engine (CSE)

Step 12: Clean session state management for Playground.

Guarantees:
- State remains clean: only Playground-relevant fields
- Sessions expire automatically after MAX_AGE
- No unbounded growth: cleanup runs before each access
- State reset is explicit: user clicked reset or session timed out

This prevents drift over long demo sessions.
The QueryState dataclass (from conversation_manager.py) defines what's relevant:
- metric, dimension, time_filter, entity_focus (user analysis context)
- intent, confidence (intent detection)
- message_count (session activity)
"""
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class PlaygroundSessionState:
    """
    Clean session state - only Playground-relevant fields.
    
    Think of this as "what the user is currently analyzing" not "everything".
    """
    # Session identity (set once, immutable)
    session_id: str
    org_id: str
    user_id: str
    
    # Current analysis state (updated as user explores)
    metric: Optional[str] = None  # revenue, orders, customers, etc.
    dimension: Optional[str] = None  # region, product, category, etc.
    time_filter: Optional[str] = None  # ytd, last_quarter, month_over_month, etc.
    entity_focus: Optional[str] = None  # specific region/product if mentioned
    intent: Optional[str] = None  # current intent from StateExtractor
    confidence: float = 0.0  # confidence of intent detection
    
    # Session tracking (managed internally)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    message_count: int = 0
    
    # Expiration (configured at engine level)
    max_age_seconds: int = 3600  # 1 hour default
    
    def is_expired(self) -> bool:
        """Has this session timed out?"""
        age = time.time() - self.created_at
        return age > self.max_age_seconds
    
    def touch(self):
        """Update last activity timestamp (called on each message)"""
        self.last_activity = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export state as dict (for serialization or client response)"""
        return {
            "session_id": self.session_id,
            "org_id": self.org_id,
            "user_id": self.user_id,
            "metric": self.metric,
            "dimension": self.dimension,
            "time_filter": self.time_filter,
            "entity_focus": self.entity_focus,
            "intent": self.intent,
            "confidence": self.confidence,
            "message_count": self.message_count,
            "created_at": self.created_at,
            "is_expired": self.is_expired(),
        }


class ConversationStateEngine:
    """
    Manages session state for Playground demo conversations.
    
    Design principles:
    1. Clean state: only store fields that Playground needs
    2. Bounded growth: expire sessions automatically
    3. Explicit reset: user asks to reset or session times out
    4. No surprises: predictable state throughout demo
    """
    
    def __init__(self, max_session_age_seconds: int = 3600):
        """
        Args:
            max_session_age_seconds: How long before session expires (default 1 hour)
        """
        self.states: Dict[str, PlaygroundSessionState] = {}
        self.max_session_age_seconds = max_session_age_seconds
    
    def create_state(self, session_id: str, org_id: str, user_id: str) -> PlaygroundSessionState:
        """
        Create new session state.
        
        Called when user starts a Playground session.
        Initializes with clean defaults (all analysis fields = None).
        """
        state = PlaygroundSessionState(
            session_id=session_id,
            org_id=org_id,
            user_id=user_id,
            max_age_seconds=self.max_session_age_seconds,
        )
        self.states[session_id] = state
        return state
    
    def get_state(self, session_id: str) -> Optional[PlaygroundSessionState]:
        """
        Get session state.
        
        Automatically cleans up expired sessions before returning.
        Returns None if session not found or has expired.
        """
        self._cleanup_expired_sessions()
        
        state = self.states.get(session_id)
        if state and state.is_expired():
            # Double-check expiration
            del self.states[session_id]
            return None
        return state
    
    def update_state(self, session_id: str, **updates) -> Optional[PlaygroundSessionState]:
        """
        Update specific state fields.
        
        Only allows Playground-relevant fields (metric, dimension, intent, etc.).
        Rejects any other field names to keep state clean.
        Updates last_activity and increments message_count.
        
        Args:
            session_id: Which session to update
            **updates: Field updates (e.g., metric="revenue", intent="explain")
        
        Returns:
            Updated state, or None if session not found/expired
        """
        state = self.get_state(session_id)
        if not state:
            return None
        
        # Whitelist: only these fields can be set
        allowed_fields = {
            "metric", "dimension", "time_filter", "entity_focus",
            "intent", "confidence", "message_count"
        }
        
        # Filter out any disallowed fields
        valid_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        # Update allowed fields
        for key, value in valid_updates.items():
            setattr(state, key, value)
        
        # Increment activity
        state.touch()
        if "message_count" not in valid_updates:
            state.message_count += 1
        
        return state
    
    def reset_state(self, session_id: str) -> bool:
        """
        Explicitly reset session state (user clicked reset button).
        
        Clears analysis fields but keeps session alive:
        - metric, dimension, time_filter, entity_focus → None
        - intent, confidence → reset
        - message_count → preserved (for audit)
        - created_at, session_id → unchanged
        
        Args:
            session_id: Which session to reset
        
        Returns:
            True if reset successful, False if session not found
        """
        state = self.get_state(session_id)
        if not state:
            return False
        
        # Reset analysis fields only
        state.metric = None
        state.dimension = None
        state.time_filter = None
        state.entity_focus = None
        state.intent = None
        state.confidence = 0.0
        
        state.touch()
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Explicitly delete a session (e.g., user logged out).
        
        Completely removes all state for this session.
        
        Args:
            session_id: Which session to delete
        
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.states:
            del self.states[session_id]
            return True
        return False
    
    def _cleanup_expired_sessions(self):
        """
        Remove all expired sessions.
        
        Called automatically before each get_state() to prevent unbounded growth.
        """
        expired_ids = [
            sid for sid, state in self.states.items()
            if state.is_expired()
        ]
        for sid in expired_ids:
            del self.states[sid]
    
    def get_active_session_count(self) -> int:
        """
        Number of active (non-expired) sessions.
        
        Useful for monitoring/debugging Playground load.
        Triggers cleanup operation.
        """
        self._cleanup_expired_sessions()
        return len(self.states)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full session state as dict.
        
        Includes timing info (created_at, is_expired) for debugging.
        """
        state = self.get_state(session_id)
        if not state:
            return None
        return state.to_dict()


# Singleton instance for convenience
_state_engine: Optional[ConversationStateEngine] = None


def get_conversation_state_engine() -> ConversationStateEngine:
    """
    Get or create the singleton state engine.
    
    Used by Playground routes to access session state.
    """
    global _state_engine
    if _state_engine is None:
        _state_engine = ConversationStateEngine()
    return _state_engine
