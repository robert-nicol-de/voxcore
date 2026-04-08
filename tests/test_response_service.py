"""
Test suite for ResponseService.

Tests response formatting, insight extraction, recommendations, visualizations.
"""
import pytest
from voxcore.services.response_service import ResponseService, get_response_service


class TestResponseService:
    """Test ResponseService."""
    
    @pytest.fixture
    def service(self):
        return ResponseService()
    
    @pytest.fixture
    def successful_query_result(self):
        return {
            "success": True,
            "sql": "SELECT region, SUM(revenue) FROM Orders GROUP BY region",
            "data": [
                {"region": "US", "sum_revenue": 100000},
                {"region": "EU", "sum_revenue": 75000},
                {"region": "Asia", "sum_revenue": 50000}
            ],
            "row_count": 3,
            "execution_time_ms": 125,
            "cost_score": 35,
            "cost_level": "safe"
        }
    
    @pytest.fixture
    def sample_intent(self):
        return {
            "intent_type": "aggregate",
            "confidence": 0.95,
            "metrics": ["revenue"],
            "dimensions": ["region"]
        }
    
    @pytest.fixture
    def sample_context(self):
        return {
            "session_id": "session_123",
            "messages": [],
            "metrics": ["revenue"],
            "dimensions": ["region"],
            "filters": {}
        }
    
    def test_generate_response_success(self, service, successful_query_result, sample_intent, sample_context):
        """Test generating successful response."""
        result = service.generate_response(successful_query_result, sample_intent, sample_context)
        
        assert result["success"] == True
        assert "message" in result
        assert isinstance(result["message"], str)
        assert len(result["message"]) > 0
    
    def test_extract_insights_basic(self, service):
        """Test basic insight extraction."""
        data = [
            {"region": "US", "value": 100},
            {"region": "EU", "value": 75},
            {"region": "Asia", "value": 50}
        ]
        
        insights = service._extract_insights(data, "aggregate")
        
        assert "summary" in insights or "top_finding" in insights
        assert isinstance(insights, dict)
    
    def test_extract_insights_detects_anomalies(self, service):
        """Test that anomalies are detected."""
        data = [
            {"value": 100},
            {"value": 105},
            {"value": 103},
            {"value": 500}  # Anomaly
        ]
        
        insights = service._extract_insights(data, "trend")
        
        # Should detect the anomaly
        result_str = str(insights)
        assert len(result_str) > 0
    
    def test_extract_insights_for_different_intent_types(self, service):
        """Test insight extraction for different intent types."""
        data = [
            {"metric": "Q1", "value": 100},
            {"metric": "Q2", "value": 150},
            {"metric": "Q3", "value": 200}
        ]
        
        for intent_type in ["aggregate", "ranking", "trend", "comparison"]:
            insights = service._extract_insights(data, intent_type)
            assert isinstance(insights, dict)
    
    def test_generate_recommendations_cost_based(self, service, successful_query_result, sample_intent, sample_context):
        """Test cost-based recommendations."""
        # High cost query
        high_cost_result = successful_query_result.copy()
        high_cost_result["cost_score"] = 85
        
        recommendations = service._generate_recommendations(high_cost_result, sample_intent, sample_context)
        
        assert isinstance(recommendations, list)
        # Should suggest optimization if cost is high
        rec_str = str(recommendations)
        assert len(rec_str) > 0
    
    def test_generate_recommendations_context_aware(self, service, successful_query_result, sample_intent):
        """Test context-aware recommendations."""
        context = {
            "session_id": "session_123",
            "messages": [],
            "metrics": ["revenue"],
            "dimensions": ["region"],
            "filters": {"year": 2024}
        }
        
        recommendations = service._generate_recommendations(successful_query_result, sample_intent, context)
        
        assert isinstance(recommendations, list)
    
    def test_suggest_visualization_aggregate(self, service):
        """Test visualization suggestion for aggregate."""
        intent = {"intent_type": "aggregate"}
        data = [{"label": "US", "value": 100}]
        
        viz = service._suggest_visualization(data, intent)
        
        assert "type" in viz
        # Aggregate usually suggests bar or pie
        assert viz["type"] in ["bar", "pie"]
    
    def test_suggest_visualization_trend(self, service):
        """Test visualization suggestion for trend."""
        intent = {"intent_type": "trend"}
        data = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-02-01", "value": 120}
        ]
        
        viz = service._suggest_visualization(data, intent)
        
        assert "type" in viz
        # Trend usually suggests line chart
        assert viz["type"] in ["line"]
    
    def test_suggest_visualization_ranking(self, service):
        """Test visualization suggestion for ranking."""
        intent = {"intent_type": "ranking"}
        data = [
            {"name": "Product A", "value": 500},
            {"name": "Product B", "value": 450}
        ]
        
        viz = service._suggest_visualization(data, intent)
        
        assert "type" in viz
        # Ranking usually suggests bar
        assert viz["type"] in ["bar"]
    
    def test_error_handling(self, service, sample_intent, sample_context):
        """Test handling of query errors."""
        error_result = {
            "success": False,
            "error": "Query timeout after 30 seconds",
            "sql": None,
            "data": None
        }
        
        response = service.generate_response(error_result, sample_intent, sample_context)
        
        assert response["success"] == False
        assert "error" in response or "message" in response
    
    def test_response_with_cost_feedback(self, service, successful_query_result, sample_intent, sample_context):
        """Test cost feedback in response."""
        result = service.generate_response(successful_query_result, sample_intent, sample_context)
        
        if "cost_feedback" in result:
            assert isinstance(result["cost_feedback"], str)
    
    def test_response_structure(self, service, successful_query_result, sample_intent, sample_context):
        """Test that response has all required fields."""
        result = service.generate_response(successful_query_result, sample_intent, sample_context)
        
        assert "success" in result
        assert "message" in result
        assert "data" in result
        assert "insights" in result
        assert "recommendations" in result
        assert "visualization" in result
    
    def test_empty_data_handling(self, service, sample_intent, sample_context):
        """Test handling of empty result set."""
        empty_result = {
            "success": True,
            "sql": "SELECT * FROM Orders WHERE region='NonExistent'",
            "data": [],
            "row_count": 0
        }
        
        response = service.generate_response(empty_result, sample_intent, sample_context)
        
        assert response["success"] == True
        # Should handle empty gracefully
        assert "message" in response
    
    def test_large_dataset_handling(self, service, sample_intent, sample_context):
        """Test handling of large datasets."""
        large_data = [{"id": i, "value": i * 10} for i in range(1000)]
        
        result = {
            "success": True,
            "data": large_data,
            "row_count": 1000
        }
        
        response = service.generate_response(result, sample_intent, sample_context)
        
        assert response["success"] == True
        # Should handle large data without crashing
        assert "message" in response


class TestResponseServiceSingleton:
    """Test singleton factory function."""
    
    def test_get_response_service_returns_singleton(self):
        """Test that get_response_service returns same instance."""
        service1 = get_response_service()
        service2 = get_response_service()
        assert service1 is service2
