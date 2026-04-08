"""
Intent Service - User input analysis and intent detection.

Responsibility: Understand what the user is trying to do
- Parse user message
- Detect query intent (aggregate, ranking, trend, comparison, diagnostic)
- Extract entities (metrics, dimensions, timeframes)
- Analyze ambiguity
- Generate clarification questions if needed

Does NOT: Execute queries, manage state, format responses
"""
from typing import Dict, Any, Optional, List
import re


class IntentService:
    """Analyzes user input to understand query intent."""
    
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
        """Initialize intent service."""
        self.ambiguity_threshold = 0.65
        self.confidence_threshold = 0.65
    
    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user intent from natural language input.
        
        Args:
            user_input: User's natural language query
            
        Returns:
            {
                "intent_type": "aggregate|ranking|trend|comparison|diagnostic",
                "confidence": 0.0-1.0,
                "metrics": ["revenue", ...],
                "dimensions": ["region", ...],
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
            clarification_text = self._generate_clarification(
                intent_type, metrics, dimensions, ambiguous
            )
        
        return {
            "intent_type": intent_type,
            "confidence": intent_confidence,
            "metrics": metrics,
            "dimensions": dimensions,
            "ambiguous": ambiguous,
            "clarification_needed": clarification_needed,
            "clarification_text": clarification_text,
            "raw_input": text,
        }
    
    def _detect_intent(self, text: str) -> tuple:
        """
        Detect primary intent type from text.
        
        Returns:
            (intent_type: str, confidence: float)
        """
        scores = {}
        
        # Match patterns
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            for pattern, score in patterns:
                if re.search(pattern, text):
                    scores[intent_type] = max(scores.get(intent_type, 0), score)
        
        # Default to aggregate if no match
        if not scores:
            return "aggregate", 0.60
        
        # Return highest scoring intent
        primary = max(scores, key=scores.get)
        return primary, scores[primary]
    
    def _extract_metrics(self, text: str) -> List[str]:
        """
        Extract metric entities from text.
        
        Returns:
            List of detected metrics (e.g., ["revenue", "profit"])
        """
        metrics = []
        for metric_name, keywords in self.METRIC_VOCAB.items():
            for keyword in keywords:
                if keyword in text:
                    metrics.append(metric_name)
                    break
        
        # Default if nothing found
        return metrics or ["sales"]
    
    def _extract_dimensions(self, text: str) -> List[str]:
        """
        Extract dimension entities from text.
        
        Returns:
            List of detected dimensions (e.g., ["region", "time"])
        """
        dimensions = []
        for dim_name, keywords in self.DIMENSION_VOCAB.items():
            for keyword in keywords:
                if keyword in text:
                    dimensions.append(dim_name)
                    break
        
        return dimensions
    
    def _generate_clarification(
        self,
        intent_type: str,
        metrics: List[str],
        dimensions: List[str],
        ambiguous: bool
    ) -> Optional[str]:
        """
        Generate clarification question if needed.
        
        Returns:
            Clarification question or None
        """
        if ambiguous and len(set(metrics)) > 1:
            return f"I found multiple metrics: {', '.join(set(metrics))}. Which would you like to analyze?"
        
        if not metrics:
            return "I couldn't identify a metric. What would you like to measure?"
        
        if not dimensions and intent_type in ["ranking", "comparison"]:
            return f"I can show {metrics[0]}, but what dimension would you like? (e.g., region, category)"
        
        return None
    
    def is_ambiguous(self, analysis: Dict[str, Any]) -> bool:
        """Check if intent analysis is ambiguous."""
        return analysis.get("ambiguous", False)
    
    def requires_clarification(self, analysis: Dict[str, Any]) -> bool:
        """Check if clarification is needed."""
        return analysis.get("clarification_needed", False)


# Singleton instance
_intent_service = None

def get_intent_service() -> IntentService:
    """Get or create intent service singleton."""
    global _intent_service
    if _intent_service is None:
        _intent_service = IntentService()
    return _intent_service
