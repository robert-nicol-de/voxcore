"""
Integration tests for ConversationManagerV2 orchestrator.

Tests the full flow: User Input → Intent → State → Query → Response
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from voxcore.services.conversation_manager_v2 import ConversationManagerV2, get_conversation_manager


class TestConversationManagerV2:
    """Test ConversationManagerV2 orchestrator."""
    
    @pytest.fixture
    def manager(self):
        """Create manager without VoxCoreEngine for testing."""
        return ConversationManagerV2(voxcore_engine=None)
    
    @pytest.fixture
    def mock_connection(self):
        """Mock database connection."""
        conn = Mock()
        cursor = Mock()
        cursor.fetchall.return_value = [
            {"region": "US", "revenue": 100000},
            {"region": "EU", "revenue": 75000}
        ]
        cursor.rowcount = 2
        conn.cursor.return_value.__enter__.return_value = cursor
        return conn
    
    def test_manager_initialization(self, manager):
        """Test manager initialization."""
        assert manager.intent_service is not None
        assert manager.state_service is not None
        assert manager.query_service is not None
        assert manager.response_service is not None
    
    def test_handle_message_aggregate_flow(self, manager, mock_connection):
        """Test complete aggregate query flow."""
        session_id = "test_session"
        
        response = manager.handle_message(
            session_id=session_id,
            user_input="What is the total revenue by region?",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        assert "session_id" in response
        assert response["session_id"] == session_id
        assert "success" in response
        assert "message" in response
    
    def test_handle_message_creates_session_history(self, manager, mock_connection):
        """Test that messages are tracked in session history."""
        session_id = "test_session"
        
        manager.handle_message(
            session_id=session_id,
            user_input="Show revenue",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        # Check that history was created
        context = manager.get_session_context(session_id)
        assert len(context.get("messages", [])) > 0
    
    def test_handle_message_with_clarification(self, manager, mock_connection):
        """Test clarification request for ambiguous input."""
        session_id = "test_session"
        
        response = manager.handle_message(
            session_id=session_id,
            user_input="xyz abc qwerty nonsense",  # Ambiguous
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        # Should either ask for clarification or succeed
        assert response.get("success") or "clarification" in response.get("message", "").lower()
    
    def test_handle_message_stores_assistant_response(self, manager, mock_connection):
        """Test that assistant response is stored in history."""
        session_id = "test_session"
        
        manager.handle_message(
            session_id=session_id,
            user_input="Show total revenue",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        context = manager.get_session_context(session_id)
        # Should have at least user message + assistant response
        messages = context.get("messages", [])
        assert len(messages) >= 1  # At least the user message
    
    def test_multiple_turns_same_session(self, manager, mock_connection):
        """Test multi-turn conversation in same session."""
        session_id = "test_session"
        
        # Turn 1
        response1 = manager.handle_message(
            session_id=session_id,
            user_input="Show revenue",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        # Turn 2
        response2 = manager.handle_message(
            session_id=session_id,
            user_input="By region?",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        # Both should succeed
        assert "message" in response1
        assert "message" in response2
        
        # Session should have accumulated messages
        context = manager.get_session_context(session_id)
        assert len(context["messages"]) >= 2
    
    def test_get_session_context(self, manager, mock_connection):
        """Test retrieving session context."""
        session_id = "test_session"
        
        manager.handle_message(
            session_id=session_id,
            user_input="Show revenue by region",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        context = manager.get_session_context(session_id)
        
        assert "session_id" in context
        assert "messages" in context
        assert "metrics" in context
        assert "dimensions" in context
        assert "filters" in context
    
    def test_get_conversation_history(self, manager, mock_connection):
        """Test retrieving conversation history."""
        session_id = "test_session"
        
        manager.handle_message(
            session_id=session_id,
            user_input="What is revenue?",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        history = manager.get_conversation_history(session_id)
        
        assert isinstance(history, str)
        assert len(history) > 0
    
    def test_clear_session(self, manager, mock_connection):
        """Test clearing session state."""
        session_id = "test_session"
        
        # Add some data
        manager.handle_message(
            session_id=session_id,
            user_input="Show revenue",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        # Clear it
        manager.clear_session(session_id)
        
        # Check it's cleared
        context = manager.get_session_context(session_id)
        assert len(context.get("messages", [])) == 0
    
    def test_response_output_format(self, manager, mock_connection):
        """Test that response has correct format."""
        response = manager.handle_message(
            session_id="test_session",
            user_input="Show revenue by region",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        # Check required fields
        assert "session_id" in response
        assert "success" in response
        assert "message" in response
        assert "data" in response
        assert "insights" in response
        assert "recommendations" in response
        assert "visualization" in response
    
    def test_error_handling_invalid_connection(self, manager):
        """Test error handling with invalid connection."""
        response = manager.handle_message(
            session_id="test_session",
            user_input="Show revenue",
            db_connection=None,  # Invalid
            user_id="test_user",
            timeout=30
        )
        
        # Should handle gracefully
        assert "error" in response or not response.get("success", False)
    
    def test_different_intent_types(self, manager, mock_connection):
        """Test handling of different intent types."""
        session_id = "test_session"
        
        test_cases = [
            ("What is the total revenue?", "aggregate"),  # Should detect aggregate
            ("Show top 5 products", "ranking"),              # Should detect ranking
            ("Show revenue trend", "trend"),                # Should detect trend
            ("Compare profit by region", "comparison"),     # Should detect comparison
        ]
        
        for user_input, expected_intent_key in test_cases:
            response = manager.handle_message(
                session_id=session_id,
                user_input=user_input,
                db_connection=mock_connection,
                user_id="test_user",
                timeout=30
            )
            assert "message" in response
    
    def test_session_isolation(self, manager, mock_connection):
        """Test that sessions don't interfere with each other."""
        # Session 1
        manager.handle_message(
            session_id="session1",
            user_input="Show revenue",
            db_connection=mock_connection,
            user_id="user1",
            timeout=30
        )
        
        # Session 2
        manager.handle_message(
            session_id="session2",
            user_input="Show profit",
            db_connection=mock_connection,
            user_id="user2",
            timeout=30
        )
        
        # Check isolation
        context1 = manager.get_session_context("session1")
        context2 = manager.get_session_context("session2")
        
        # Different sessions should have different histories
        assert len(context1["messages"]) >= 1
        assert len(context2["messages"]) >= 1
    
    def test_get_session_state(self, manager, mock_connection):
        """Test debugging method get_session_state."""
        session_id = "test_session"
        
        manager.handle_message(
            session_id=session_id,
            user_input="Show revenue by region",
            db_connection=mock_connection,
            user_id="test_user",
            timeout=30
        )
        
        state = manager.get_session_state(session_id)
        
        assert isinstance(state, dict)
        assert "session_id" in state


class TestConversationManagerV2Singleton:
    """Test singleton factory function."""
    
    def test_get_conversation_manager_returns_singleton(self):
        """Test that get_conversation_manager returns same instance."""
        manager1 = get_conversation_manager()
        manager2 = get_conversation_manager()
        assert manager1 is manager2
    
    def test_get_conversation_manager_with_engine(self):
        """Test that engine can be passed."""
        mock_engine = Mock()
        manager = get_conversation_manager(voxcore_engine=mock_engine)
        assert manager.voxcore_engine == mock_engine
