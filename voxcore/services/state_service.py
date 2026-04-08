"""
State Service - Conversation state and context management.

Responsibility: Track conversation context and state
- Manage conversation history
- Track tables accessed, queries run, filters applied
- Update state from user input and query results
- Provide context for downstream services
- Handle session state

Does NOT: Detect intent, execute queries, generate responses
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ConversationState:
    """Represents the current conversation state."""
    session_id: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metrics: List[str] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    tables_accessed: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "messages": self.messages,
            "context": self.context,
            "metrics": self.metrics,
            "dimensions": self.dimensions,
            "filters": self.filters,
            "tables_accessed": self.tables_accessed,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class StateService:
    """Manages conversation state and context."""
    
    def __init__(self, max_history: int = 50):
        """
        Initialize state service.
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.max_history = max_history
        self.states: Dict[str, ConversationState] = {}
    
    def get_or_create_state(self, session_id: str) -> ConversationState:
        """
        Get existing state or create new one.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationState for this session
        """
        if session_id not in self.states:
            self.states[session_id] = ConversationState(session_id=session_id)
        return self.states[session_id]
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add message to conversation history.
        
        Args:
            session_id: Session identifier
            role: "user" or "assistant"
            content: Message content
            metadata: Optional metadata (intent, execution_time, etc.)
        """
        state = self.get_or_create_state(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        state.messages.append(message)
        state.last_updated = datetime.now()
        
        # Trim history if too long
        if len(state.messages) > self.max_history:
            state.messages = state.messages[-self.max_history:]
    
    def update_context(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update conversation context.
        
        Args:
            session_id: Session identifier
            updates: Dictionary of updates to apply
            
        Returns:
            Updated context
        """
        state = self.get_or_create_state(session_id)
        state.context.update(updates)
        state.last_updated = datetime.now()
        return state.context
    
    def set_metrics(self, session_id: str, metrics: List[str]) -> None:
        """Set active metrics for session."""
        state = self.get_or_create_state(session_id)
        state.metrics = metrics
        state.last_updated = datetime.now()
    
    def set_dimensions(self, session_id: str, dimensions: List[str]) -> None:
        """Set active dimensions for session."""
        state = self.get_or_create_state(session_id)
        state.dimensions = dimensions
        state.last_updated = datetime.now()
    
    def add_filter(self, session_id: str, filter_key: str, filter_value: Any) -> None:
        """
        Add a filter to the current state.
        
        Args:
            session_id: Session identifier
            filter_key: Filter key (e.g., "region")
            filter_value: Filter value
        """
        state = self.get_or_create_state(session_id)
        state.filters[filter_key] = filter_value
        state.last_updated = datetime.now()
    
    def get_filters(self, session_id: str) -> Dict[str, Any]:
        """Get current filters for session."""
        state = self.get_or_create_state(session_id)
        return state.filters.copy()
    
    def clear_filters(self, session_id: str) -> None:
        """Clear all filters for session."""
        state = self.get_or_create_state(session_id)
        state.filters = {}
        state.last_updated = datetime.now()
    
    def add_table_access(self, session_id: str, table_name: str) -> None:
        """
        Record that a table was accessed.
        
        Args:
            session_id: Session identifier
            table_name: Name of accessed table
        """
        state = self.get_or_create_state(session_id)
        if table_name not in state.tables_accessed:
            state.tables_accessed.append(table_name)
        state.last_updated = datetime.now()
    
    def get_table_history(self, session_id: str) -> List[str]:
        """Get list of tables accessed in session."""
        state = self.get_or_create_state(session_id)
        return state.tables_accessed.copy()
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get full session context for downstream services.
        
        Returns:
            {
                "metrics": [...],
                "dimensions": [...],
                "filters": {...},
                "tables": [...],
                "recent_queries": [...],
                "context": {...}
            }
        """
        state = self.get_or_create_state(session_id)
        
        # Get last 10 queries from history
        recent_queries = [
            m["content"] for m in state.messages[-20:]
            if m["role"] == "user"
        ][-10:]
        
        return {
            "metrics": state.metrics,
            "dimensions": state.dimensions,
            "filters": state.filters,
            "tables": state.tables_accessed,
            "recent_queries": recent_queries,
            "context": state.context,
        }
    
    def get_state_dict(self, session_id: str) -> Dict[str, Any]:
        """Get full state as dictionary."""
        state = self.get_or_create_state(session_id)
        return state.to_dict()
    
    def clear_session(self, session_id: str) -> None:
        """Clear all state for a session."""
        if session_id in self.states:
            del self.states[session_id]
    
    def get_conversation_summary(self, session_id: str, max_messages: int = 10) -> str:
        """
        Get formatted conversation summary for LLM context.
        
        Args:
            session_id: Session identifier
            max_messages: Maximum messages to include
            
        Returns:
            Formatted conversation string
        """
        state = self.get_or_create_state(session_id)
        
        summary = "Conversation History:\n"
        for msg in state.messages[-max_messages:]:
            role = msg["role"].upper()
            content = msg["content"]
            summary += f"{role}: {content}\n"
        
        return summary
    
    def get_last_user_query(self, session_id: str) -> Optional[str]:
        """Get the last user query in the conversation."""
        state = self.get_or_create_state(session_id)
        
        for msg in reversed(state.messages):
            if msg["role"] == "user":
                return msg["content"]
        
        return None


# Singleton instance
_state_service = None

def get_state_service() -> StateService:
    """Get or create state service singleton."""
    global _state_service
    if _state_service is None:
        _state_service = StateService()
    return _state_service
