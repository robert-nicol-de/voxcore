"""Core engine tests"""

import pytest
from voxquery.core.engine import VoxQueryEngine
from voxquery.core.schema_analyzer import SchemaAnalyzer


def test_schema_analyzer_initialization():
    """Test schema analyzer initialization"""
    # Would need a test database for this
    pass


def test_sql_generator():
    """Test SQL generation"""
    # Would need a test database for this
    pass


def test_conversation_manager():
    """Test conversation context management"""
    from voxquery.core.conversation import ConversationManager
    
    manager = ConversationManager()
    
    # Add messages
    manager.add_user_message("What are top clients?")
    manager.add_assistant_message("Here's the SQL...")
    manager.add_user_message("Filter by region")
    
    # Check history
    assert len(manager.messages) == 3
    assert manager.messages[0].role == "user"
    assert manager.get_last_query() == "Filter by region"


def test_conversation_context_updates():
    """Test context updates"""
    from voxquery.core.conversation import ConversationManager
    
    manager = ConversationManager()
    manager.update_context("tables_accessed", ["customers", "orders"])
    manager.update_context("last_query", "SELECT * FROM customers")
    
    assert manager.context["tables_accessed"] == ["customers", "orders"]
    assert manager.context["last_query"] == "SELECT * FROM customers"


def test_conversation_serialization():
    """Test conversation serialization to dict"""
    from voxquery.core.conversation import ConversationManager
    
    manager = ConversationManager()
    manager.add_user_message("Test")
    manager.add_assistant_message("Response")
    
    data = manager.to_dict()
    assert "messages" in data
    assert len(data["messages"]) == 2
    assert "context" in data


def test_conversation_clear():
    """Test clearing conversation"""
    from voxquery.core.conversation import ConversationManager
    
    manager = ConversationManager()
    manager.add_user_message("Test")
    assert len(manager.messages) == 1
    
    manager.clear()
    assert len(manager.messages) == 0
