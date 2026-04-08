"""
Test suite for LLM State Parser.

Tests semantic state extraction with mocking.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from voxcore.services.state_parser_llm import LLMStateParser, get_llm_state_parser


class TestLLMStateParser:
    """Test LLMStateParser - Semantic state extraction."""
    
    @pytest.fixture
    def service(self):
        return LLMStateParser()
    
    @pytest.fixture
    def mock_parse_response(self):
        """Mock LLM parse response."""
        return {
            "filters": {"region": "US", "year": 2024},
            "timeframe": "2024",
            "aggregation": "SUM",
            "sorting": "DESC",
            "limit": 10,
            "context_updates": {
                "active_filters": ["region", "year"],
                "tracking_metrics": ["revenue"],
                "focused_dimensions": ["region"]
            },
            "confidence": 0.95
        }
    
    def test_parse_state_basic(self, service, mock_parse_response):
        """Test basic state parsing."""
        with patch.object(service, '_llm_parse_state', return_value=mock_parse_response):
            result = service.parse_state("Show US revenue in 2024")
            
            assert result["filters"]["region"] == "US"
            assert result["filters"]["year"] == 2024
            assert result["timeframe"] == "2024"
            assert result["source"] == "llm"
    
    def test_parse_state_fallback_on_error(self, service):
        """Test fallback to simple parsing on error."""
        with patch.object(service, '_llm_parse_state', side_effect=Exception("API Error")):
            result = service.parse_state("Show top 10 products")
            
            assert result["source"] == "fallback"
            assert "confidence" in result
    
    def test_filters_normalization(self, service):
        """Test filters are properly normalized."""
        response = {
            "filters": {"region": "US", "year": 2024},
            "timeframe": None,
            "aggregation": "SUM",
            "sorting": "DESC",
            "limit": None,
            "context_updates": {},
            "confidence": 0.9
        }
        
        with patch.object(service, '_llm_parse_state', return_value=response):
            result = service.parse_state("query")
            
            assert isinstance(result["filters"], dict)
            assert result["filters"]["region"] == "US"
    
    def test_aggregation_normalization(self, service):
        """Test aggregation is uppercased."""
        response = {
            "filters": {},
            "timeframe": None,
            "aggregation": "sum",  # lowercase
            "sorting": "desc",
            "limit": 10,
            "context_updates": {},
            "confidence": 0.9
        }
        
        with patch.object(service, '_llm_parse_state', return_value=response):
            result = service.parse_state("query")
            
            assert result["aggregation"] == "SUM"
            assert result["sorting"] == "DESC"
    
    def test_timeframe_extraction(self, service):
        """Test timeframe is extracted."""
        response = {
            "filters": {},
            "timeframe": "2024-Q1",
            "aggregation": "AVG",
            "sorting": "ASC",
            "limit": 5,
            "context_updates": {},
            "confidence": 0.85
        }
        
        with patch.object(service, '_llm_parse_state', return_value=response):
            result = service.parse_state("Q1 2024 data")
            
            assert result["timeframe"] == "2024-Q1"
    
    def test_limit_extraction(self, service):
        """Test limit/top-N is extracted."""
        response = {
            "filters": {},
            "timeframe": None,
            "aggregation": "SUM",
            "sorting": "DESC",
            "limit": 20,
            "context_updates": {},
            "confidence": 0.9
        }
        
        with patch.object(service, '_llm_parse_state', return_value=response):
            result = service.parse_state("top 20 products")
            
            assert result["limit"] == 20
    
    def test_context_updates(self, service):
        """Test context_updates are tracked."""
        response = {
            "filters": {"region": "EU"},
            "timeframe": None,
            "aggregation": "SUM",
            "sorting": "DESC",
            "limit": 10,
            "context_updates": {
                "active_filters": ["region"],
                "tracking_metrics": ["revenue", "profit"],
                "focused_dimensions": ["region", "category"]
            },
            "confidence": 0.9
        }
        
        with patch.object(service, '_llm_parse_state', return_value=response):
            result = service.parse_state("query")
            
            updates = result["context_updates"]
            assert "region" in updates["active_filters"]
            assert "revenue" in updates["tracking_metrics"]
            assert "region" in updates["focused_dimensions"]
    
    def test_confidence_clamping(self, service):
        """Test confidence is clamped to 0-1."""
        response_high = {
            "filters": {},
            "timeframe": None,
            "aggregation": "SUM",
            "sorting": "DESC",
            "limit": 10,
            "context_updates": {},
            "confidence": 1.5  # > 1.0
        }
        
        response_low = {
            "filters": {},
            "timeframe": None,
            "aggregation": "SUM",
            "sorting": "DESC",
            "limit": 10,
            "context_updates": {},
            "confidence": -0.5  # < 0.0
        }
        
        with patch.object(service, '_llm_parse_state', return_value=response_high):
            result = service.parse_state("query")
            assert result["confidence"] == 1.0
        
        with patch.object(service, '_llm_parse_state', return_value=response_low):
            result = service.parse_state("query")
            assert result["confidence"] == 0.0
    
    def test_parse_with_history(self, service, mock_parse_response):
        """Test parsing with conversation history."""
        history = [
            {"role": "user", "content": "Show revenue"},
            {"role": "assistant", "content": "Here is revenue"}
        ]
        context = {
            "metrics": ["revenue"],
            "dimensions": ["region"],
            "filters": {}
        }
        
        with patch.object(service, '_llm_parse_state', return_value=mock_parse_response):
            result = service.parse_state(
                "By region?",
                conversation_history=history,
                current_context=context
            )
            
            assert result["source"] == "llm"
    
    def test_fallback_parse_simple(self, service):
        """Test fallback parser."""
        service.groq_client = None
        
        result = service.parse_state("Show US data for 2024")
        
        assert result["source"] == "fallback"
        assert result["filters"].get("region") == "US"
        assert result["timeframe"] == "2024"
        assert result["confidence"] == 0.4  # Fallback confidence
    
    def test_fallback_parse_top_n(self, service):
        """Test fallback parser detects top-N."""
        service.groq_client = None
        
        result = service.parse_state("Top 15 products")
        
        assert result["limit"] == 15


class TestLLMStateParserSingleton:
    """Test singleton factory."""
    
    def test_returns_same_instance(self):
        """Test get_llm_state_parser returns singleton."""
        parser1 = get_llm_state_parser()
        parser2 = get_llm_state_parser()
        assert parser1 is parser2
