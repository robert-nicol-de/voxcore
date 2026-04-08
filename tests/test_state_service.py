"""
Test suite for StateService.

Tests conversation context tracking, history management, filters, tables.
"""
import pytest
from voxcore.services.state_service import StateService, get_state_service, ConversationState


class TestConversationState:
    """Test ConversationState dataclass."""
    
    def test_state_creation(self):
        """Test creating conversation state."""
        state = ConversationState(
            session_id="session_123",
            messages=[],
            context={},
            metrics=["revenue"],
            dimensions=["region"],
            filters={},
            tables_accessed=[],
            timestamps={}
        )
        assert state.session_id == "session_123"
        assert state.metrics == ["revenue"]
        assert state.dimensions == ["region"]
    
    def test_state_with_messages(self):
        """Test state tracking messages."""
        state = ConversationState(
            session_id="session_123",
            messages=[
                {"role": "user", "content": "Show revenue"},
                {"role": "assistant", "content": "Here is revenue"}
            ],
            context={},
            metrics=[],
            dimensions=[],
            filters={},
            tables_accessed=[],
            timestamps={}
        )
        assert len(state.messages) == 2
        assert state.messages[0]["role"] == "user"


class TestStateService:
    """Test StateService."""
    
    @pytest.fixture
    def service(self):
        return StateService()
    
    @pytest.fixture
    def session_id(self):
        return "test_session_123"
    
    def test_add_message(self, service, session_id):
        """Test adding messages to conversation."""
        service.add_message(session_id, "user", "Show revenue by region")
        context = service.get_context(session_id)
        assert len(context["messages"]) == 1
        assert context["messages"][0]["role"] == "user"
    
    def test_add_multiple_messages(self, service, session_id):
        """Test adding multiple messages."""
        service.add_message(session_id, "user", "Show revenue")
        service.add_message(session_id, "assistant", "Here is revenue")
        service.add_message(session_id, "user", "By region?")
        
        context = service.get_context(session_id)
        assert len(context["messages"]) == 3
    
    def test_message_history_trimming(self, service, session_id):
        """Test that history is trimmed to max 50 messages."""
        # Add 60 messages
        for i in range(60):
            service.add_message(session_id, "user", f"Message {i}")
        
        context = service.get_context(session_id)
        # Should be trimmed to 40 (keeps recent, removes oldest)
        assert len(context["messages"]) <= 50
    
    def test_set_metrics(self, service, session_id):
        """Test setting metrics."""
        service.set_metrics(session_id, ["revenue", "profit"])
        context = service.get_context(session_id)
        assert "revenue" in context["metrics"]
        assert "profit" in context["metrics"]
    
    def test_set_dimensions(self, service, session_id):
        """Test setting dimensions."""
        service.set_dimensions(session_id, ["region", "category"])
        context = service.get_context(session_id)
        assert "region" in context["dimensions"]
        assert "category" in context["dimensions"]
    
    def test_add_filter(self, service, session_id):
        """Test adding filter."""
        service.add_filter(session_id, "region", "US")
        filters = service.get_filters(session_id)
        assert filters.get("region") == "US"
    
    def test_multiple_filters(self, service, session_id):
        """Test adding multiple filters."""
        service.add_filter(session_id, "region", "US")
        service.add_filter(session_id, "year", 2024)
        filters = service.get_filters(session_id)
        assert filters.get("region") == "US"
        assert filters.get("year") == 2024
    
    def test_get_filters(self, service, session_id):
        """Test retrieving filters."""
        service.add_filter(session_id, "category", "Premium")
        filters = service.get_filters(session_id)
        assert isinstance(filters, dict)
        assert filters.get("category") == "Premium"
    
    def test_add_table_access(self, service, session_id):
        """Test tracking table access."""
        service.add_table_access(session_id, "Orders")
        tables = service.get_tables_accessed(session_id)
        assert "Orders" in tables
    
    def test_multiple_table_access(self, service, session_id):
        """Test tracking multiple table accesses."""
        service.add_table_access(session_id, "Orders")
        service.add_table_access(session_id, "Customers")
        service.add_table_access(session_id, "Products")
        tables = service.get_tables_accessed(session_id)
        assert len(tables) == 3
        assert "Orders" in tables
    
    def test_get_context_returns_full_dict(self, service, session_id):
        """Test that context returns complete state."""
        service.add_message(session_id, "user", "Show revenue")
        service.set_metrics(session_id, ["revenue"])
        service.set_dimensions(session_id, ["region"])
        service.add_filter(session_id, "region", "US")
        
        context = service.get_context(session_id)
        assert "messages" in context
        assert "metrics" in context
        assert "dimensions" in context
        assert "filters" in context
        assert "tables_accessed" in context
        assert "session_id" in context
    
    def test_conversation_summary(self, service, session_id):
        """Test getting conversation summary."""
        service.add_message(session_id, "user", "Show revenue")
        service.add_message(session_id, "assistant", "Revenue is $100K")
        service.add_message(session_id, "user", "By region?")
        
        summary = service.get_conversation_summary(session_id)
        assert isinstance(summary, str)
        assert "revenue" in summary.lower()
    
    def test_context_isolation_between_sessions(self, service):
        """Test that different sessions don't interfere."""
        service.add_message("session1", "user", "Show revenue")
        service.set_metrics("session1", ["revenue"])
        
        service.add_message("session2", "user", "Show profit")
        service.set_metrics("session2", ["profit"])
        
        context1 = service.get_context("session1")
        context2 = service.get_context("session2")
        
        assert context1["metrics"] == ["revenue"]
        assert context2["metrics"] == ["profit"]
    
    def test_message_with_metadata(self, service, session_id):
        """Test adding message with metadata."""
        service.add_message(
            session_id, "user", "Show revenue",
            metadata={"intent": "aggregate"}
        )
        context = service.get_context(session_id)
        assert "intent" in context["messages"][0].get("metadata", {})
    
    def test_clear_session(self, service, session_id):
        """Test clearing session state."""
        service.add_message(session_id, "user", "Show revenue")
        service.set_metrics(session_id, ["revenue"])
        
        service.clear_session(session_id)
        context = service.get_context(session_id)
        assert len(context["messages"]) == 0
        assert len(context["metrics"]) == 0


class TestStateServiceSingleton:
    """Test singleton factory function."""
    
    def test_get_state_service_returns_singleton(self):
        """Test that get_state_service returns same instance."""
        service1 = get_state_service()
        service2 = get_state_service()
        assert service1 is service2
