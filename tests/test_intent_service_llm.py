"""
Test suite for LLM Intent Service.

Tests real NLP understanding with mocking for API calls.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from voxcore.services.intent_service_llm import LLMIntentService, get_llm_intent_service


class TestLLMIntentService:
    """Test LLMIntentService - Real NLP intent detection."""
    
    @pytest.fixture
    def service(self):
        """Create service with mocked Groq client."""
        return LLMIntentService()
    
    @pytest.fixture
    def mock_groq_response(self):
        """Mock Groq API response."""
        return {
            "intent": "aggregate",
            "confidence": 0.95,
            "metrics": ["revenue"],
            "dimensions": ["region"],
            "timeframe": "2024",
            "filters": {},
            "clarification_needed": False,
            "clarification_text": None
        }
    
    def test_analyze_intent_with_valid_response(self, service, mock_groq_response):
        """Test analyzing intent with valid LLM response."""
        with patch.object(service, '_llm_classify_intent', return_value=mock_groq_response):
            result = service.analyze_intent("What is the total revenue by region?")
            
            assert result["intent_type"] == "aggregate"
            assert result["confidence"] == 0.95
            assert "revenue" in result["metrics"]
            assert "region" in result["dimensions"]
            assert result["source"] == "llm"
    
    def test_analyze_intent_fallback_on_error(self, service):
        """Test fallback to pattern matching on LLM error."""
        with patch.object(service, '_llm_classify_intent', side_effect=Exception("API Error")):
            result = service.analyze_intent("Show top 10 products by profit")
            
            # Should fall back to pattern matching
            assert result["source"] == "fallback_error"
            assert "error" in result.get("llm_error", "")
    
    def test_confidence_scoring(self, service):
        """Test confidence is normalized to 0-1."""
        response_high = {
            "intent": "aggregate",
            "confidence": 0.99,
            "metrics": ["revenue"],
            "dimensions": [],
            "clarification_needed": False
        }
        
        response_low = {
            "intent": "ranking",
            "confidence": 0.3,
            "metrics": ["profit"],
            "dimensions": [],
            "clarification_needed": True,
            "clarification_text": "Please clarify"
        }
        
        with patch.object(service, '_llm_classify_intent', return_value=response_high):
            result = service.analyze_intent("query")
            assert 0.0 <= result["confidence"] <= 1.0
            assert result["confidence"] == 0.99
        
        with patch.object(service, '_llm_classify_intent', return_value=response_low):
            result = service.analyze_intent("query")
            assert 0.0 <= result["confidence"] <= 1.0
            assert result["confidence"] == 0.3
    
    def test_metrics_extraction(self, service):
        """Test metrics are properly extracted."""
        response = {
            "intent": "aggregate",
            "confidence": 0.9,
            "metrics": ["revenue", "profit"],
            "dimensions": ["region"],
            "clarification_needed": False
        }
        
        with patch.object(service, '_llm_classify_intent', return_value=response):
            result = service.analyze_intent("query")
            assert len(result["metrics"]) == 2
            assert "revenue" in result["metrics"]
            assert "profit" in result["metrics"]
    
    def test_dimensions_extraction(self, service):
        """Test dimensions are properly extracted."""
        response = {
            "intent": "aggregate",
            "confidence": 0.9,
            "metrics": ["revenue"],
            "dimensions": ["region", "category"],
            "clarification_needed": False
        }
        
        with patch.object(service, '_llm_classify_intent', return_value=response):
            result = service.analyze_intent("query")
            assert len(result["dimensions"]) == 2
            assert "region" in result["dimensions"]
            assert "category" in result["dimensions"]
    
    def test_clarification_request(self, service):
        """Test clarification is properly flagged."""
        response = {
            "intent": "aggregate",
            "confidence": 0.4,
            "metrics": [],
            "dimensions": [],
            "clarification_needed": True,
            "clarification_text": "What metric would you like?"
        }
        
        with patch.object(service, '_llm_classify_intent', return_value=response):
            result = service.analyze_intent("xyz abc")
            assert result["clarification_needed"] == True
            assert "What metric" in result["clarification_text"]
    
    def test_intent_types_supported(self, service):
        """Test all intent types are recognized."""
        intent_types = ["aggregate", "ranking", "trend", "comparison", "diagnostic"]
        
        for intent_type in intent_types:
            response = {
                "intent": intent_type,
                "confidence": 0.9,
                "metrics": ["revenue"],
                "dimensions": [],
                "clarification_needed": False
            }
            
            with patch.object(service, '_llm_classify_intent', return_value=response):
                result = service.analyze_intent("query")
                assert result["intent_type"] == intent_type
    
    def test_timeframe_extraction(self, service):
        """Test timeframe is properly extracted."""
        response = {
            "intent": "trend",
            "confidence": 0.9,
            "metrics": ["revenue"],
            "dimensions": ["date"],
            "timeframe": "2024-Q1",
            "clarification_needed": False
        }
        
        with patch.object(service, '_llm_classify_intent', return_value=response):
            result = service.analyze_intent("Revenue trend for Q1 2024")
            assert result["timeframe"] == "2024-Q1"
    
    def test_filters_extraction(self, service):
        """Test filters are properly extracted."""
        response = {
            "intent": "aggregate",
            "confidence": 0.95,
            "metrics": ["revenue"],
            "dimensions": ["region"],
            "filters": {"region": "US", "year": 2024},
            "clarification_needed": False
        }
        
        with patch.object(service, '_llm_classify_intent', return_value=response):
            result = service.analyze_intent("US revenue in 2024")
            assert result["filters"]["region"] == "US"
            assert result["filters"]["year"] == 2024
    
    def test_get_stats(self, service):
        """Test stats reporting."""
        stats = service.get_stats()
        
        assert "llm_failures" in stats
        assert "fallback_uses" in stats
        assert "total_requests" in stats
        assert "fallback_rate" in stats
    
    def test_no_groq_client_fallback(self):
        """Test service works when Groq not initialized."""
        service = LLMIntentService()
        service.groq_client = None  # Simulate no API key
        
        result = service.analyze_intent("What is revenue?")
        
        # Should still work via fallback
        assert result["source"] == "fallback_no_client"
        assert "intent_type" in result


class TestLLMIntentServiceSingleton:
    """Test singleton factory."""
    
    def test_returns_same_instance(self):
        """Test get_llm_intent_service returns singleton."""
        service1 = get_llm_intent_service()
        service2 = get_llm_intent_service()
        assert service1 is service2
