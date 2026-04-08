"""
Integration tests for ConversationManagerV3 - LLM-powered orchestrator.

Tests the full flow with real AI understanding.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from voxcore.services.conversation_manager_v3 import ConversationManagerV3, get_conversation_manager_v3


class TestConversationManagerV3:
    """Test ConversationManagerV3 - LLM-powered orchestrator."""
    
    @pytest.fixture
    def manager(self):
        """Create manager without VoxCoreEngine."""
        return ConversationManagerV3(voxcore_engine=None)
    
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
    
    @pytest.fixture
    def mock_intent(self):
        """Mock LLM intent response."""
        return {
            "intent_type": "aggregate",
            "confidence": 0.95,
            "metrics": ["revenue"],
            "dimensions": ["region"],
            "timeframe": None,
            "filters": {},
            "ambiguous": False,
            "clarification_needed": False,
            "clarification_text": None,
            "raw_input": "Show revenue by region",
            "source": "llm"
        }
    
    @pytest.fixture
    def mock_parsed_state(self):
        """Mock LLM parsed state."""
        return {
            "filters": {},
            "timeframe": None,
            "aggregation": "SUM",
            "sorting": "DESC",
            "limit": 10,
            "context_updates": {},
            "confidence": 0.95,
            "source": "llm"
        }
    
    def test_manager_initialization(self, manager):
        """Test manager initializes with LLM services."""
        assert manager.llm_intent_service is not None
        assert manager.llm_state_parser is not None
        assert manager.state_service is not None
        assert manager.query_service is not None
        assert manager.response_service is not None
    
    def test_handle_message_complete_flow(self, manager, mock_connection, mock_intent, mock_parsed_state):
        """Test complete message handling flow."""
        
        with patch.object(manager.llm_intent_service, 'analyze_intent', return_value=mock_intent), \
             patch.object(manager.llm_state_parser, 'parse_state', return_value=mock_parsed_state):
            
            response = manager.handle_message(
                session_id="test_session",
                user_input="Show revenue by region",
                db_connection=mock_connection,
                user_id="test_user",
                timeout=30
            )
            
            assert response["session_id"] == "test_session"
            assert "success" in response
            assert "message" in response
            assert "ai_confidence" in response
            assert response["source"] == "llm"
    
    def test_ai_confidence_in_response(self, manager, mock_connection, mock_intent, mock_parsed_state):
        """Test AI confidence is included in response."""
        mock_intent["confidence"] = 0.92
        mock_parsed_state["confidence"] = 0.88
        
        with patch.object(manager.llm_intent_service, 'analyze_intent', return_value=mock_intent), \
             patch.object(manager.llm_state_parser, 'parse_state', return_value=mock_parsed_state):
            
            response = manager.handle_message(
                session_id="test_session",
                user_input="Query",
                db_connection=mock_connection,
                user_id="test_user"
            )
            
            # Should be minimum of both confidences
            assert response["ai_confidence"] == min(0.92, 0.88)
    
    def test_clarification_request(self, manager, mock_connection):
        """Test clarification when intent unclear."""
        unclear_intent = {
            "intent_type": "aggregate",
            "confidence": 0.3,
            "metrics": [],
            "dimensions": [],
            "ambiguous": True,
            "clarification_needed": True,
            "clarification_text": "What metric do you want?",
            "source": "llm"
        }
        
        with patch.object(manager.llm_intent_service, 'analyze_intent', return_value=unclear_intent):
            
            response = manager.handle_message(
                session_id="test_session",
                user_input="xyz abc",
                db_connection=mock_connection,
                user_id="test_user"
            )
            
            assert response["ambiguous"] == True
            assert "What metric" in response["message"]
    
    def test_fallback_source_tracking(self, manager, mock_connection):
        """Test response tracks fallback when LLM fails."""
        fallback_intent = {
            "intent_type": "aggregate",
            "confidence": 0.7,
            "metrics": [],
            "dimensions": [],
            "source": "fallback_error",
            "llm_error": "Rate limited",
            "clarification_needed": False
        }
        
        with patch.object(manager.llm_intent_service, 'analyze_intent', return_value=fallback_intent):
            
            response = manager.handle_message(
                session_id="test_session",
                user_input="Show data",
                db_connection=mock_connection,
                user_id="test_user"
            )
            
            # Source should track where intent came from
            assert response["source"] == "fallback_error"
    
    def test_multi_turn_conversation(self, manager, mock_connection, mock_intent, mock_parsed_state):
        """Test multi-turn conversation with LLM."""
        
        with patch.object(manager.llm_intent_service, 'analyze_intent', return_value=mock_intent), \
             patch.object(manager.llm_state_parser, 'parse_state', return_value=mock_parsed_state):
            
            # Turn 1
            response1 = manager.handle_message(
                session_id="test_session",
                user_input="Show revenue",
                db_connection=mock_connection,
                user_id="test_user"
            )
            
            # Turn 2
            response2 = manager.handle_message(
                session_id="test_session",
                user_input="By region?",
                db_connection=mock_connection,
                user_id="test_user"
            )
            
            # Both should succeed
            assert "message" in response1
            assert "message" in response2
            
            # Session should have history
            context = manager.get_session_context("test_session")
            assert len(context["messages"]) >= 2
    
    def test_error_handling(self, manager, mock_connection, mock_intent, mock_parsed_state):
        """Test error handling in V3."""
        
        with patch.object(manager.llm_intent_service, 'analyze_intent', return_value=mock_intent), \
             patch.object(manager.llm_state_parser, 'parse_state', side_effect=Exception("Parse error")):
            
            response = manager.handle_message(
                session_id="test_session",
                user_input="Query",
                db_connection=mock_connection,
                user_id="test_user"
            )
            
            # Should handle error gracefully
            assert "error" in response or response["success"] == False
    
    def test_ai_stats(self, manager):
        """Test AI statistics collection."""
        stats = manager.get_ai_stats()
        
        assert "intent_service" in stats
        assert "state_parser" in stats
        assert "llm_failures" in stats["intent_service"]
    
    def test_session_isolation_with_llm(self, manager, mock_connection, mock_intent, mock_parsed_state):
        """Test session isolation with LLM services."""
        
        with patch.object(manager.llm_intent_service, 'analyze_intent', return_value=mock_intent), \
             patch.object(manager.llm_state_parser, 'parse_state', return_value=mock_parsed_state):
            
            # Two different sessions
            manager.handle_message("session1", "Show revenue", mock_connection, "user1")
            manager.handle_message("session2", "Show profit", mock_connection, "user2")
            
            context1 = manager.get_session_context("session1")
            context2 = manager.get_session_context("session2")
            
            # Different metric tracking
            assert context1.get("metrics", []) != context2.get("metrics", [])
    
    def test_clear_session(self, manager, mock_connection, mock_intent, mock_parsed_state):
        """Test clearing session with LLM services."""
        
        with patch.object(manager.llm_intent_service, 'analyze_intent', return_value=mock_intent), \
             patch.object(manager.llm_state_parser, 'parse_state', return_value=mock_parsed_state):
            
            manager.handle_message("session", "query", mock_connection)
            manager.clear_session("session")
            
            context = manager.get_session_context("session")
            assert len(context.get("messages", [])) == 0
    
    def test_get_conversation_history(self, manager, mock_connection, mock_intent, mock_parsed_state):
        """Test retrieving conversation history."""
        
        with patch.object(manager.llm_intent_service, 'analyze_intent', return_value=mock_intent), \
             patch.object(manager.llm_state_parser, 'parse_state', return_value=mock_parsed_state):
            
            manager.handle_message("session", "Show revenue", mock_connection)
            history = manager.get_conversation_history("session")
            
            assert isinstance(history, str)
            assert len(history) > 0


class TestConversationManagerV3Singleton:
    """Test V3 singleton factory."""
    
    def test_returns_same_instance(self):
        """Test get_conversation_manager_v3 returns singleton."""
        manager1 = get_conversation_manager_v3()
        manager2 = get_conversation_manager_v3()
        assert manager1 is manager2
    
    def test_singleton_with_engine(self):
        """Test singleton with VoxCoreEngine."""
        mock_engine = Mock()
        manager = get_conversation_manager_v3(voxcore_engine=mock_engine)
        assert manager.voxcore_engine == mock_engine
