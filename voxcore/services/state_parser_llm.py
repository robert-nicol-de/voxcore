"""
LLM-Powered State Parser - Using Groq Llama for semantic state extraction.

STEP 5: Real Intelligence - Part 2

Replaces manual state extraction with LLM-driven semantic parsing.
- Extracts meaning from user input
- Identifies filters, timeframes, and constraints
- Updates conversation context intelligently
- Graceful fallback to simple extraction on LLM failure
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
    logger.warning("[LLM] GROQ_API_KEY not set - will use fallback parsing")
    groq_client = None
else:
    groq_client = Groq(api_key=groq_api_key)


class LLMStateParser:
    """
    LLM-powered state and context parsing.
    
    Extracts semantic meaning from user input and conversation history.
    Features:
    - Interactive constraint extraction
    - Implicit filter inference
    - Contextual understanding
    - Automatic fallback to simple parsing
    """
    
    SYSTEM_PROMPT = """You are an expert at understanding database queries and analytical requirements from natural language.

Given a user's question and conversation history, extract:

1. **filters** - WHERE clause constraints
   - Explicit: "in the US", "for 2024", "premium customers"
   - Implicit: "best products" might imply high-performers

2. **timeframe** - Specific period referenced
   - Explicit: "2024", "last quarter", "Q1 2024"
   - Implicit: "recent" = last month/quarter

3. **aggregation** - How to combine data
   - "total" = SUM
   - "average" = AVG
   - "count" = COUNT
   - "breakdown" = GROUP BY

4. **sorting** - Order preference
   - "top" = DESC
   - "bottom" = ASC

5. **limit** - Number of items
   - "top 10", "bottom 5", etc.

6. **context_updates** - What should be remembered?
   - Which metrics are we tracking?
   - Which dimensions matter?
   - Any standing filters?

Return JSON with structured data. For ambiguous inputs, make reasonable assumptions and include confidence scores.

CRITICAL: Always return valid JSON."""

    def __init__(self):
        """Initialize LLM state parser."""
        self.groq_client = groq_client
        self.llm_failures = 0
    
    def parse_state(
        self,
        user_input: str,
        conversation_history: list = None,
        current_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Parse semantic state from user input and history.
        
        Args:
            user_input: Current user message
            conversation_history: Previous messages
            current_context: Current session context
            
        Returns:
            {
                "filters": {"region": "US", "year": 2024},
                "timeframe": "2024-Q1",
                "aggregation": "SUM",
                "sorting": "DESC",
                "limit": 10,
                "context_updates": {
                    "active_filters": [...],
                    "tracking_metrics": [...],
                    "focused_dimensions": [...]
                },
                "source": "llm" or "fallback",
                "confidence": 0.0-1.0
            }
        """
        logger.info(f"[LLM Parser] Parsing state from: {user_input[:100]}")
        
        if not self.groq_client:
            logger.warning("[LLM Parser] Groq not available, using fallback")
            return self._fallback_parse_state(user_input, current_context)
        
        try:
            result = self._llm_parse_state(
                user_input,
                conversation_history or [],
                current_context or {}
            )
            result["source"] = "llm"
            logger.info(f"[LLM Parser] ✅ Success: {len(result.get('filters', {}))} filters, {result.get('confidence', 0):.2f} confidence")
            return result
            
        except Exception as e:
            logger.error(f"[LLM Parser] ❌ LLM failed: {str(e)[:100]}")
            self.llm_failures += 1
            return self._fallback_parse_state(user_input, current_context)
    
    def _llm_parse_state(
        self,
        user_input: str,
        conversation_history: list,
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call LLM to parse state."""
        
        # Build context messages for LLM
        history_text = ""
        if conversation_history:
            history_text = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
        
        context_text = ""
        if current_context:
            context_text = f"""
Current Context:
- Metrics being tracked: {current_context.get('metrics', [])}
- Dimensions in use: {current_context.get('dimensions', [])}
- Current filters: {current_context.get('filters', {})}
- Recent tables: {current_context.get('tables_accessed', [])}
"""
        
        user_message = f"""
User's Question: {user_input}

{context_text}

{f'Recent conversation:' + history_text if history_text else ''}
"""
        
        # Call LLM
        try:
            logger.debug("[LLM Parser] Calling Groq with primary model (70B)")
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2,  # Low for consistent parsing
                max_tokens=600,
                response_format={"type": "json_object"}
            )
            
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                logger.warning("[LLM Parser] Rate limited, trying 8B fallback")
                response = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.2,
                    max_tokens=600,
                    response_format={"type": "json_object"}
                )
            else:
                raise
        
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        
        return self._normalize_parse_response(data)
    
    def _normalize_parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize LLM parse response."""
        
        filters = data.get("filters", {})
        if not isinstance(filters, dict):
            filters = {}
        
        timeframe = data.get("timeframe", None)
        aggregation = data.get("aggregation", "SUM").upper()
        sorting = data.get("sorting", "DESC").upper()
        limit = data.get("limit", None)
        
        context_updates = data.get("context_updates", {})
        if not isinstance(context_updates, dict):
            context_updates = {}
        
        confidence = float(data.get("confidence", 0.7))
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            "filters": filters,
            "timeframe": timeframe,
            "aggregation": aggregation,
            "sorting": sorting,
            "limit": limit,
            "context_updates": context_updates,
            "confidence": confidence
        }
    
    def _fallback_parse_state(
        self,
        user_input: str,
        current_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fallback simple state parsing.
        """
        logger.info("[LLM Parser] Using fallback parsing")
        
        text = user_input.lower()
        filters = {}
        timeframe = None
        limit = None
        
        # Simple filter extraction
        if " in " in text:
            parts = text.split(" in ")
            if len(parts) > 1:
                location = parts[-1].split()[0]
                filters["region"] = location.title()
        
        if "2024" in text:
            timeframe = "2024"
        elif "2023" in text:
            timeframe = "2023"
        
        if "top " in text:
            import re
            match = re.search(r"top (\d+)", text)
            if match:
                limit = int(match.group(1))
        
        return {
            "filters": filters,
            "timeframe": timeframe,
            "aggregation": "SUM",
            "sorting": "DESC",
            "limit": limit or 10,
            "context_updates": {},
            "confidence": 0.4,
            "source": "fallback"
        }


# Singleton
_llm_state_parser = None

def get_llm_state_parser() -> LLMStateParser:
    """Get or create LLM state parser singleton."""
    global _llm_state_parser
    if _llm_state_parser is None:
        _llm_state_parser = LLMStateParser()
    return _llm_state_parser
