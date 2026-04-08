"""
Fallback Intent Service - Pattern matching based.

Used when LLM is unavailable or fails.
This is the original STEP 4 approach kept as fallback.
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class IntentServiceFallback:
    """
    Pattern-matching intent detection.
    Used as fallback when LLM is unavailable.
    """
    
    # Intent patterns mapping
    INTENT_PATTERNS = {
        "aggregate": [
            (r"total|sum|overall|cumulative", 0.90),
            (r"how much|how many|what is the", 0.85),
        ],
        "ranking": [
            (r"top|bottom|highest|lowest|ranking|best|worst", 0.95),
        ],
        "trend": [
            (r"trend|growth|decline|overtime|over time|timeline|history", 0.90),
        ],
        "comparison": [
            (r"yoy|year.over.year|mom|month.over.month|qoq|quarter.over.quarter|compare", 0.95),
            (r"vs\.|versus|compared to|difference", 0.85),
        ],
        "diagnostic": [
            (r"why|what.drove|driver|explain|caused|reason|root cause", 0.90),
        ],
    }
    
    # Metric vocabulary
    METRIC_VOCAB = {
        "revenue": ["revenue", "sales", "turnover"],
        "profit": ["profit", "margin", "earnings"],
        "count": ["count", "volume", "quantity"],
        "growth": ["growth", "increase", "decrease"],
        "cost": ["cost", "expense", "spending"],
    }
    
    # Dimension vocabulary
    DIMENSION_VOCAB = {
        "region": ["region", "regions", "country"],
        "category": ["category", "categories", "product category"],
        "time": ["month", "quarter", "year", "date", "week"],
        "segment": ["segment", "segments", "customer segment"],
    }
    
    def __init__(self):
        """Initialize fallback intent service."""
        self.ambiguity_threshold = 0.65
        self.confidence_threshold = 0.65
    
    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user intent from natural language input (pattern matching).
        
        Args:
            user_input: User's natural language query
            
        Returns:
            {
                "intent_type": "aggregate|ranking|trend|comparison|diagnostic",
                "confidence": 0.0-1.0,
                "metrics": ["revenue", ...],
                "dimensions": ["region", ...],
                "timeframe": None,
                "filters": {},
                "ambiguous": bool,
                "clarification_needed": bool,
                "clarification_text": str or None,
                "raw_input": str
            }
        """
        text = user_input.strip()
        lowered = text.lower()
        
        # 1. Detect intent type
        intent_type, intent_confidence = self._detect_intent(lowered)
        
        # 2. Extract entities (metrics, dimensions)
        metrics = self._extract_metrics(lowered)
        dimensions = self._extract_dimensions(lowered)
        
        # 3. Check for ambiguity
        ambiguous = len(set(metrics)) > 1
        
        # 4. Determine if clarification needed
        clarification_needed = (
            intent_confidence < self.confidence_threshold or
            (not metrics and not dimensions) or
            ambiguous
        )
        
        clarification_text = None
        if clarification_needed:
            if not metrics:
                clarification_text = "What metric would you like to analyze? (e.g., revenue, profit, count)"
            elif not dimensions:
                clarification_text = "How would you like to break down the data? (e.g., by region, category, time)"
            else:
                clarification_text = "Your query is ambiguous. Could you clarify what you're looking for?"
        
        return {
            "intent_type": intent_type,
            "confidence": intent_confidence,
            "metrics": metrics,
            "dimensions": dimensions,
            "timeframe": None,
            "filters": {},
            "ambiguous": ambiguous,
            "clarification_needed": clarification_needed,
            "clarification_text": clarification_text,
            "raw_input": text
        }
    
    def _detect_intent(self, lowered: str) -> tuple:
        """
        Detect intent type using pattern matching.
        
        Returns: (intent_type, confidence)
        """
        max_confidence = 0.0
        detected_intent = "aggregate"  # Default
        
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            for pattern, pattern_confidence in patterns:
                if self._matches_pattern(pattern, lowered):
                    if pattern_confidence > max_confidence:
                        max_confidence = pattern_confidence
                        detected_intent = intent_type
        
        return detected_intent, max_confidence
    
    def _matches_pattern(self, pattern: str, text: str) -> bool:
        """Check if pattern matches text."""
        import re
        try:
            return bool(re.search(pattern, text))
        except:
            return False
    
    def _extract_metrics(self, lowered: str) -> List[str]:
        """Extract mentioned metrics."""
        metrics = []
        for metric_name, keywords in self.METRIC_VOCAB.items():
            for keyword in keywords:
                if keyword in lowered:
                    metrics.append(metric_name)
                    break
        return list(set(metrics))  # Remove duplicates
    
    def _extract_dimensions(self, lowered: str) -> List[str]:
        """Extract mentioned dimensions."""
        dimensions = []
        for dim_name, keywords in self.DIMENSION_VOCAB.items():
            for keyword in keywords:
                if keyword in lowered:
                    dimensions.append(dim_name)
                    break
        return list(set(dimensions))  # Remove duplicates
