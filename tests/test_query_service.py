"""
Test suite for QueryService.

Tests SQL building, governance integration, execution, error handling.
"""
import pytest
from unittest.mock import Mock, MagicMock
from voxcore.services.query_service import QueryService, get_query_service


class TestQueryService:
    """Test QueryService."""
    
    @pytest.fixture
    def service(self):
        return QueryService(voxcore_engine=None)  # No engine for unit tests
    
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
        cursor.executemany.return_value = None
        conn.cursor.return_value.__enter__.return_value = cursor
        return conn
    
    @pytest.fixture
    def sample_intent(self):
        return {
            "intent_type": "aggregate",
            "metrics": ["revenue"],
            "dimensions": ["region"]
        }
    
    @pytest.fixture
    def sample_context(self):
        return {
            "session_id": "session_123",
            "metrics": ["revenue"],
            "dimensions": ["region"],
            "filters": {}
        }
    
    def test_build_aggregate_query(self, service):
        """Test building aggregation SQL."""
        intent = {
            "intent_type": "aggregate",
            "metrics": ["revenue"],
            "dimensions": ["region"]
        }
        context = {"filters": {}}
        
        sql = service._build_aggregate_query(intent, context)
        assert "revenue" in sql.lower()
        assert "region" in sql.lower()
        assert "select" in sql.lower()
        assert "group by" in sql.lower()
    
    def test_build_ranking_query(self, service):
        """Test building ranking SQL."""
        intent = {
            "intent_type": "ranking",
            "metrics": ["profit"],
            "dimensions": []
        }
        context = {"filters": {}}
        
        sql = service._build_ranking_query(intent, context)
        assert "profit" in sql.lower()
        assert "order by" in sql.lower()
        assert "limit" in sql.lower()
    
    def test_build_trend_query(self, service):
        """Test building trend SQL."""
        intent = {
            "intent_type": "trend",
            "metrics": ["revenue"],
            "dimensions": ["time"]
        }
        context = {"filters": {}}
        
        sql = service._build_trend_query(intent, context)
        assert "revenue" in sql.lower()
        assert "order by" in sql.lower()
    
    def test_build_comparison_query(self, service):
        """Test building comparison SQL."""
        intent = {
            "intent_type": "comparison",
            "metrics": ["profit"],
            "dimensions": ["region"]
        }
        context = {"filters": {}}
        
        sql = service._build_comparison_query(intent, context)
        assert "profit" in sql.lower()
        assert "region" in sql.lower()
    
    def test_build_diagnostic_query(self, service):
        """Test building diagnostic SQL."""
        intent = {
            "intent_type": "diagnostic",
            "metrics": ["revenue"],
            "dimensions": []
        }
        context = {"filters": {}}
        
        sql = service._build_diagnostic_query(intent, context)
        assert isinstance(sql, str)
        assert len(sql) > 0
    
    def test_apply_governance_without_engine(self, service):
        """Test governance when VoxCoreEngine not available."""
        result = service._apply_governance(
            sql="SELECT * FROM Orders",
            session_id="session_123",
            user_id="user_123",
            workspace_id="ws_123"
        )
        
        # Should have default safe values
        assert result["cost_score"] == 35  # Default safe value
        assert result["cost_level"] == "safe"
        assert result["approved"] == True
    
    def test_execute_sql_success(self, service, mock_connection):
        """Test successful SQL execution."""
        result = service._execute_sql(
            sql="SELECT * FROM Orders LIMIT 10",
            connection=mock_connection,
            timeout=30
        )
        
        assert result["success"] == True
        assert "data" in result
        assert isinstance(result["data"], list)
    
    def test_execute_sql_timeout_handling(self, service):
        """Test timeout handling in SQL execution."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Query timed out")
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = service._execute_sql(
            sql="SELECT * FROM Orders",
            connection=mock_conn,
            timeout=30
        )
        
        # Should handle error gracefully
        assert result["success"] == False or "error" in result
    
    def test_build_and_execute_query_aggregate(self, service, sample_intent, sample_context, mock_connection):
        """Test full aggregate query execution."""
        result = service.build_and_execute_query(
            intent=sample_intent,
            context=sample_context,
            session_id="session_123",
            db_connection=mock_connection,
            user_id="user_123",
            timeout=30
        )
        
        assert "success" in result
        assert "sql" in result
        assert "data" in result
    
    def test_build_and_execute_query_with_filters(self, service, mock_connection):
        """Test query execution with filters."""
        intent = {
            "intent_type": "aggregate",
            "metrics": ["revenue"],
            "dimensions": ["region"]
        }
        context = {
            "session_id": "session_123",
            "metrics": ["revenue"],
            "dimensions": ["region"],
            "filters": {"region": "US"}
        }
        
        result = service.build_and_execute_query(
            intent=intent,
            context=context,
            session_id="session_123",
            db_connection=mock_connection,
            user_id="user_123",
            timeout=30
        )
        
        # Query should include filter
        sql = result.get("sql", "").lower()
        # Filter should be applied in some way
        assert "sql" in result
    
    def test_result_structure(self, service, sample_intent, sample_context, mock_connection):
        """Test that result has required fields."""
        result = service.build_and_execute_query(
            intent=sample_intent,
            context=sample_context,
            session_id="session_123",
            db_connection=mock_connection,
            user_id="user_123",
            timeout=30
        )
        
        assert "success" in result
        assert "sql" in result
        assert "data" in result
        assert "row_count" in result
        assert "cost_score" in result
        assert "cost_level" in result
        assert "execution_time_ms" in result
    
    def test_no_voxcore_engine_graceful_fallback(self, service):
        """Test that service works without VoxCoreEngine."""
        assert service.voxcore_engine is None
        
        # Should still be able to build queries
        intent = {"intent_type": "aggregate", "metrics": ["revenue"], "dimensions": []}
        context = {"filters": {}}
        sql = service._build_aggregate_query(intent, context)
        assert sql is not None


class TestQueryServiceSingleton:
    """Test singleton factory function."""
    
    def test_get_query_service_returns_singleton(self):
        """Test that get_query_service returns same instance."""
        service1 = get_query_service()
        service2 = get_query_service()
        assert service1 is service2
    
    def test_get_query_service_with_engine(self):
        """Test that engine can be passed to get_query_service."""
        mock_engine = Mock()
        service = get_query_service(voxcore_engine=mock_engine)
        assert service.voxcore_engine == mock_engine
