"""Conversation manager for maintaining context across follow-ups"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 10):
        self.messages: List[Message] = []
        self.max_history = max_history
        self.context: Dict[str, Any] = {
            "tables_accessed": [],
            "last_query": None,
            "filters_applied": [],
        }
    
    def add_user_message(self, content: str, metadata: Optional[Dict] = None) -> Message:
        """Add a user message to the conversation"""
        msg = Message(
            role="user",
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )
        self.messages.append(msg)
        self._trim_history()
        return msg
    
    def add_assistant_message(self, content: str, metadata: Optional[Dict] = None) -> Message:
        """Add an assistant message to the conversation"""
        msg = Message(
            role="assistant",
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )
        self.messages.append(msg)
        self._trim_history()
        return msg
    
    def get_conversation_context(self) -> str:
        """Get the conversation history as a formatted string"""
        context = "Conversation History:\n"
        for msg in self.messages[-10:]:  # Last 10 messages
            context += f"{msg.role.upper()}: {msg.content}\n"
        return context
    
    def get_last_query(self) -> Optional[str]:
        """Get the last user query"""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None
    
    def update_context(self, key: str, value: Any) -> None:
        """Update conversation context"""
        self.context[key] = value
    
    def _trim_history(self) -> None:
        """Trim conversation history to max_history messages"""
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in self.messages
            ],
            "context": self.context,
        }
    
    def clear(self) -> None:
        """Clear conversation history"""
        self.messages = []
        self.context = {
            "tables_accessed": [],
            "last_query": None,
            "filters_applied": [],
        }
