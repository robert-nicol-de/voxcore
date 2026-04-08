"""
Test suite for IntentService.

Tests intent detection, entity extraction, clarification logic.
"""
import pytest
from voxcore.services.intent_service import IntentService, get_intent_service


class TestIntentService:
    """Test IntentService.analyze_intent()"""
    
    @pytest.fixture
    def service(self):
        return IntentService()
    
    def test_aggregate_intent_detection(self, service):
        """Test detection of aggregation intent."""
        result = service.analyze_intent("What is the total revenue by region?")
        assert result["intent_type"] == "aggregate"
        assert result["confidence"] > 0.65
        assert "revenue" in result.get("metrics", [])
        assert "region" in result.get("dimensions", [])
    
    def test_ranking_intent_detection(self, service):
        """Test detection of ranking intent."""
        result = service.analyze_intent("Show me the top 5 products by profit")
        assert result["intent_type"] == "ranking"
        assert result["confidence"] > 0.65
        assert "profit" in result.get("metrics", [])
    
    def test_trend_intent_detection(self, service):
        """Test detection of trend intent."""
        result = service.analyze_intent("What is the revenue trend over time?")
        assert result["intent_type"] == "trend"
        assert "revenue" in result.get("metrics", [])
    
    def test_comparison_intent_detection(self, service):
        """Test detection of comparison intent."""
        result = service.analyze_intent("Compare profit between regions")
        assert result["intent_type"] == "comparison"
        assert "profit" in result.get("metrics", [])
        assert "region" in result.get("dimensions", [])
    
    def test_diagnostic_intent_detection(self, service):
        """Test detection of diagnostic intent."""
        result = service.analyze_intent("Why is revenue declining?")
        assert result["intent_type"] == "diagnostic"
    
    def test_ambiguous_intent_clarification(self, service):
        """Test clarification when intent is ambiguous."""
        result = service.analyze_intent("Show me something")
        assert result.get("ambiguous") or result["confidence"] < 0.65
    
    def test_low_confidence_triggers_clarification(self, service):
        """Test clarification request for low confidence."""
        result = service.analyze_intent("xyz abc qwerty")
        if result["confidence"] < 0.65:
            assert result.get("clarification_needed")
    
    def test_metrics_extraction(self, service):
        """Test metric vocabulary extraction."""
        result = service.analyze_intent("Total revenue and profit by category")
        assert "revenue" in result.get("metrics", [])
        assert "profit" in result.get("metrics", [])
    
    def test_dimensions_extraction(self, service):
        """Test dimension vocabulary extraction."""
        result = service.analyze_intent("Sales by region, segment, and time")
        dimensions = result.get("dimensions", [])
        assert "region" in dimensions or "segment" in dimensions
    
    def test_multiple_metrics(self, service):
        """Test extraction of multiple metrics."""
        result = service.analyze_intent("Revenue, gross margin, and customer count")
        metrics = result.get("metrics", [])
        assert len(metrics) >= 2
    
    def test_pattern_matching_precision(self, service):
        """Test that patterns match correctly."""
        # Test with clear aggregate pattern
        result1 = service.analyze_intent("aggregate revenue by region")
        assert result1["intent_type"] == "aggregate"
        
        # Test with clear ranking pattern
        result2 = service.analyze_intent("ranking products by profit")
        assert result2["intent_type"] == "ranking"
    
    def test_case_insensitivity(self, service):
        """Test that intent detection is case-insensitive."""
        result1 = service.analyze_intent("WHAT IS THE TOTAL REVENUE?")
        result2 = service.analyze_intent("what is the total revenue?")
        assert result1["intent_type"] == result2["intent_type"]
    
    def test_output_structure(self, service):
        """Test that output has required fields."""
        result = service.analyze_intent("Show revenue by region")
        assert "intent_type" in result
        assert "confidence" in result
        assert "metrics" in result
        assert "dimensions" in result
        assert "ambiguous" in result
        assert "clarification_needed" in result


class TestIntentServiceSingleton:
    """Test singleton factory function."""
    
    def test_get_intent_service_returns_singleton(self):
        """Test that get_intent_service returns same instance."""
        service1 = get_intent_service()
        service2 = get_intent_service()
        assert service1 is service2
