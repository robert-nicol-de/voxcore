"""
LLM-Powered Intent Service - Using Groq Llama for real NLP understanding.

STEP 5: Real Intelligence

Replaces pattern matching with actual natural language understanding.
- Uses Groq Llama 3 (70B) for intent classification
- Fallback to Llama 3.1 (8B) on rate limits
- Structured JSON output
- Confidence scoring
- Graceful fallback to pattern matching on LLM failure
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from groq import Groq

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logger.warning("[LLM] GROQ_API_KEY not set - will use fallback pattern matching")
    groq_client = None
else:
    groq_client = Groq(api_key=groq_api_key)

# Fallback pattern matching (for when LLM is unavailable)
from voxcore.services.intent_service_fallback import IntentServiceFallback


class LLMIntentService:
    """
    LLM-powered intent detection using Groq Llama.
    
    Features:
    - Real NLP understanding (no pattern matching)
    - Structured JSON output
    - Confidence scoring
    - Automatic fallback to pattern matching on LLM failure
    - Graceful degradation
    """
    
    # System prompt for intent classification
    SYSTEM_PROMPT = """You are an expert SQL query analyst. Your job is to understand what the user wants to do with their database.

Analyze user questions and classify them into one of these intent types:

1. **aggregate** - Sum, average, count, or total values
   - Examples: "total revenue", "average profit", "how many customers"
   - Keywords: sum, total, average, count, overall, cumulative

2. **ranking** - Find top/bottom items, sorted lists
   - Examples: "top 10 products", "lowest cost suppliers", "ranking"
   - Keywords: top, bottom, highest, lowest, ranking, best, worst

3. **trend** - Track changes over time
   - Examples: "revenue trend", "sales over time", "quarterly growth"
   - Keywords: trend, growth, decline, over time, history, timeline

4. **comparison** - Compare A vs B
   - Examples: "US vs EU revenue", "YoY comparison", "profit difference"
   - Keywords: vs, versus, compare, yoy, mom, qoq, difference

5. **diagnostic** - Investigate why something happened
   - Examples: "why is revenue down?", "what caused the drop?"
   - Keywords: why, what drove, root cause, explain, reason

For each input, extract:
- **intent**: Primary intent type (aggregate|ranking|trend|comparison|diagnostic)
- **confidence**: How confident you are (0.0-1.0)
- **metrics**: What to measure (e.g., "revenue", "profit", "count")
- **dimensions**: How to group/breakdown (e.g., "region", "category", "time")
- **timeframe**: Time period if relevant (e.g., "2024", "last quarter")
- **filters**: Any conditions mentioned (e.g., "US only", "2024")
- **clarification_needed**: Whether the user's intent is unclear

Return a JSON object. For ambiguous inputs, set clarification_needed=true and clarification_text with a question.

CRITICAL: Always return valid JSON. Never break out of JSON format."""

    def __init__(self):
        """Initialize LLM intent service with fallback."""
        self.groq_client = groq_client
        self.fallback_service = IntentServiceFallback()  # Fallback for LLM failures
        self.llm_failures = 0
        self.fallback_uses = 0
    
    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user intent using LLM, with automatic fallback to pattern matching.
        
        Args:
            user_input: User's natural language query
            
        Returns:
            {
                "intent_type": str,
                "confidence": float,
                "metrics": list,
                "dimensions": list,
                "timeframe": str or None,
                "filters": dict,
                "ambiguous": bool,
                "clarification_needed": bool,
                "clarification_text": str or None,
                "source": "llm" or "fallback",
                "raw_input": str
            }
        """
        logger.info(f"[LLM Intent] Analyzing: {user_input[:100]}")
        
        if not self.groq_client:
            logger.warning("[LLM Intent] Groq client not initialized, using fallback")
            result = self.fallback_service.analyze_intent(user_input)
            result["source"] = "fallback_no_client"
            self.fallback_uses += 1
            return result
        
        try:
            # Call LLM for intent classification
            result = self._llm_classify_intent(user_input)
            result["source"] = "llm"
            logger.info(f"[LLM Intent] ✅ Success: {result['intent_type']} (confidence: {result['confidence']:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"[LLM Intent] ❌ LLM failed: {str(e)[:100]}")
            logger.info(f"[LLM Intent] 🔄 Falling back to pattern matching")
            
            self.llm_failures += 1
            self.fallback_uses += 1
            
            # Fall back to pattern matching
            result = self.fallback_service.analyze_intent(user_input)
            result["source"] = "fallback_error"
            result["llm_error"] = str(e)[:100]
            return result
    
    def _llm_classify_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Call Groq LLM to classify intent.
        
        Args:
            user_input: User query
            
        Returns:
            Parsed intent result
        """
        # Build prompt
        user_message = f"User question: {user_input}"
        
        # Call Groq LLM (primary: 70B, fallback: 8B)
        try:
            logger.debug("[LLM Intent] Calling Groq with primary model (70B)")
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Low temperature for consistent classifications
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                logger.warning("[LLM Intent] Rate limited on 70B, trying fallback 8B")
                response = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
            else:
                raise
        
        # Parse response
        content = response.choices[0].message.content.strip()
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            logger.error(f"[LLM Intent] Invalid JSON from LLM: {content[:100]}")
            raise ValueError(f"LLM returned invalid JSON")
        
        # Validate and normalize response
        result = self._normalize_llm_response(data, user_input)
        return result
    
    def _normalize_llm_response(self, data: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """
        Normalize LLM response to standard format.
        
        Args:
            data: Raw LLM response
            user_input: Original user input
            
        Returns:
            Normalized intent dict
        """
        # Extract and validate intent type
        intent_type = data.get("intent", "aggregate").lower()
        if intent_type not in ["aggregate", "ranking", "trend", "comparison", "diagnostic"]:
            intent_type = "aggregate"
        
        # Extract confidence (0-1)
        confidence = float(data.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
        
        # Extract metrics (list of strings)
        metrics = data.get("metrics", [])
        if isinstance(metrics, str):
            metrics = [metrics]
        metrics = [m.lower().strip() for m in metrics if m]
        
        # Extract dimensions (list of strings)
        dimensions = data.get("dimensions", [])
        if isinstance(dimensions, str):
            dimensions = [dimensions]
        dimensions = [d.lower().strip() for d in dimensions if d]
        
        # Extract other fields
        timeframe = data.get("timeframe", None)
        filters = data.get("filters", {})
        if not isinstance(filters, dict):
            filters = {}
        
        clarification_needed = data.get("clarification_needed", False)
        clarification_text = data.get("clarification_text", None)
        
        return {
            "intent_type": intent_type,
            "confidence": confidence,
            "metrics": metrics,
            "dimensions": dimensions,
            "timeframe": timeframe,
            "filters": filters,
            "ambiguous": clarification_needed,
            "clarification_needed": clarification_needed,
            "clarification_text": clarification_text,
            "raw_input": user_input
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get LLM service statistics."""
        return {
            "llm_failures": self.llm_failures,
            "fallback_uses": self.fallback_uses,
            "total_requests": self.llm_failures + self.fallback_uses,
            "fallback_rate": self.fallback_uses / max(1, self.llm_failures + self.fallback_uses)
        }


# Singleton
_llm_intent_service = None

def get_llm_intent_service() -> LLMIntentService:
    """Get or create LLM intent service singleton."""
    global _llm_intent_service
    if _llm_intent_service is None:
        _llm_intent_service = LLMIntentService()
    return _llm_intent_service
