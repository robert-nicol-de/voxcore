"""
LLM-Powered Conversation Manager - V3

STEP 5: Real Intelligence

Orchestrator that chains:
1. LLMIntentService (real NLP instead of pattern matching)
2. LLMStateParser (semantic extraction)
3. StateService (context management)
4. QueryService (SQL + governance)
5. ResponseService (formatting)

Flow:
  User Input
      ↓
  LLMIntentService (🧠 REAL AI understanding)
      ↓
  LLMStateParser (🧠 REAL extraction)
      ↓
  StateService (remember context)
      ↓
  QueryService (build query + apply governance)
      ↓
  ResponseService (format response + insights)
      ↓
  User Response

Benefits over V2:
  ✅ Real NLP instead of regex
  ✅ Semantic understanding of constraints
  ✅ Context-aware interpretations
  ✅ Automatic graceful fallback to pattern matching
  ✅ 100% backward compatible with V2
"""
import logging
from typing import Dict, Any, Optional

from voxcore.services.intent_service_llm import get_llm_intent_service
from voxcore.services.state_parser_llm import get_llm_state_parser
from voxcore.services.state_service import get_state_service
from voxcore.services.query_service import get_query_service
from voxcore.services.response_service import get_response_service

logger = logging.getLogger(__name__)


class ConversationManagerV3:
    """
    STEP 5: LLM-powered conversation manager.
    
    Replaces pattern matching with real AI understanding.
    Maintains full backward compatibility with V2.
    Automatic fallback to pattern matching on LLM failures.
    """
    
    def __init__(self, voxcore_engine=None):
        """
        Initialize V3 manager with LLM services.
        
        Args:
            voxcore_engine: Optional VoxCoreEngine for governance
        """
        # LLM-powered services (new in V3)
        self.llm_intent_service = get_llm_intent_service()
        self.llm_state_parser = get_llm_state_parser()
        
        # Standard services (from V2)
        self.state_service = get_state_service()
        self.query_service = get_query_service(voxcore_engine=voxcore_engine)
        self.response_service = get_response_service()
        
        self.voxcore_engine = voxcore_engine
    
    def handle_message(
        self,
        session_id: str,
        user_input: str,
        db_connection: Any,
        user_id: str = "user_default",
        workspace_id: Optional[str] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Process a user message end-to-end with LLM intelligence.
        
        Flow:
          1. LLM Intent Analysis (🧠 real NLP)
          2. LLM State Parsing (🧠 semantic extraction)
          3. State Management (remember context)
          4. Build & Execute Query (SQL + governance)
          5. Format Response (insights + recommendations)
        
        Args:
            session_id: Session identifier
            user_input: User's natural language query
            db_connection: Database connection
            user_id: User identifier (for RBAC)
            workspace_id: Optional workspace identifier
            timeout: Query timeout in seconds
            
        Returns:
            {
                "session_id": str,
                "success": bool,
                "message": str,
                "data": list or None,
                "insights": dict,
                "recommendations": list,
                "visualization": dict,
                "cost_feedback": str,
                "ai_confidence": float,
                "error": str or None,
                "source": "llm" or "fallback"
            }
        """
        logger.info(f"[V3] [{session_id}] Processing: {user_input}")
        
        try:
            # ─────────────────────────────────────────────────────────────
            # STEP 1: LLM Intent Analysis (🧠 Real NLP)
            # ─────────────────────────────────────────────────────────────
            intent = self.llm_intent_service.analyze_intent(user_input)
            logger.info(
                f"[V3] [{session_id}] Intent: {intent['intent_type']} "
                f"(confidence: {intent['confidence']:.2f}, source: {intent.get('source', 'unknown')})"
            )
            
            # Check if clarification needed
            if intent.get("clarification_needed"):
                self.state_service.add_message(
                    session_id, "user", user_input,
                    metadata={"intent": intent, "ai_source": intent.get("source")}
                )
                
                return {
                    "session_id": session_id,
                    "success": True,
                    "message": intent.get("clarification_text", "I need clarification."),
                    "data": None,
                    "insights": {},
                    "recommendations": [],
                    "visualization": {},
                    "ambiguous": True,
                    "ai_confidence": intent.get("confidence", 0),
                    "source": intent.get("source", "unknown"),
                    "error": None
                }
            
            # ─────────────────────────────────────────────────────────────
            # STEP 2: LLM State Parsing (🧠 Semantic Extraction)
            # ─────────────────────────────────────────────────────────────
            current_context = self.state_service.get_context(session_id)
            parsed_state = self.llm_state_parser.parse_state(
                user_input=user_input,
                conversation_history=current_context.get("messages", []),
                current_context=current_context
            )
            logger.info(
                f"[V3] [{session_id}] Parsed state: "
                f"filters={parsed_state['filters']}, "
                f"confidence={parsed_state['confidence']:.2f}"
            )
            
            # ─────────────────────────────────────────────────────────────
            # STEP 3: Update Conversation State
            # ─────────────────────────────────────────────────────────────
            self.state_service.add_message(
                session_id, "user", user_input,
                metadata={
                    "intent": intent,
                    "parsed_state": parsed_state,
                    "ai_source": intent.get("source")
                }
            )
            
            # Update state with LLM-extracted metrics/dimensions
            if intent.get("metrics"):
                self.state_service.set_metrics(session_id, intent["metrics"])
            if intent.get("dimensions"):
                self.state_service.set_dimensions(session_id, intent["dimensions"])
            
            # Apply LLM-parsed filters
            for filter_key, filter_value in parsed_state.get("filters", {}).items():
                self.state_service.add_filter(session_id, filter_key, filter_value)
            
            # Get updated context
            context = self.state_service.get_context(session_id)
            logger.info(
                f"[V3] [{session_id}] Context: "
                f"metrics={context.get('metrics')}, "
                f"dimensions={context.get('dimensions')}, "
                f"filters={context.get('filters')}"
            )
            
            # ─────────────────────────────────────────────────────────────
            # STEP 4: Build and Execute Query
            # ─────────────────────────────────────────────────────────────
            query_result = self.query_service.build_and_execute_query(
                intent=intent,
                context=context,
                session_id=session_id,
                db_connection=db_connection,
                user_id=user_id,
                workspace_id=workspace_id,
                timeout=timeout
            )
            
            logger.info(
                f"[V3] [{session_id}] Query: "
                f"success={query_result['success']}, "
                f"rows={query_result.get('row_count', 0)}, "
                f"cost={query_result.get('cost_score', 0)}/100"
            )
            
            # ─────────────────────────────────────────────────────────────
            # STEP 5: Format Response with Insights
            # ─────────────────────────────────────────────────────────────
            response_data = self.response_service.generate_response(
                query_result=query_result,
                intent=intent,
                context=context
            )
            
            # Store assistant response
            self.state_service.add_message(
                session_id, "assistant", response_data.get("message", ""),
                metadata={
                    "intent": intent,
                    "cost_score": query_result.get("cost_score"),
                    "execution_time_ms": query_result.get("execution_time_ms"),
                    "ai_source": intent.get("source")
                }
            )
            
            # Return complete response with AI metadata
            return {
                "session_id": session_id,
                "success": response_data.get("success", False),
                "message": response_data.get("message", ""),
                "data": response_data.get("data"),
                "row_count": response_data.get("row_count", 0),
                "insights": response_data.get("insights", {}),
                "recommendations": response_data.get("recommendations", []),
                "visualization": response_data.get("visualization", {}),
                "cost_feedback": response_data.get("cost_feedback", ""),
                "execution_time_ms": response_data.get("execution_time_ms", 0),
                "ai_confidence": min(intent.get("confidence", 0.5), parsed_state.get("confidence", 0.5)),
                "source": intent.get("source", "unknown"),
                "error": response_data.get("error")
            }
        
        except Exception as e:
            logger.error(f"[V3] [{session_id}] Error: {e}", exc_info=True)
            
            self.state_service.add_message(
                session_id, "system", f"Error: {str(e)}"
            )
            
            return {
                "session_id": session_id,
                "success": False,
                "message": "An error occurred while processing your request.",
                "data": None,
                "insights": {},
                "recommendations": [],
                "visualization": {},
                "error": str(e),
                "ai_confidence": 0.0,
                "source": "error"
            }
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get current session context."""
        return self.state_service.get_context(session_id)
    
    def get_conversation_history(self, session_id: str, max_messages: int = 20) -> str:
        """Get conversation history for context."""
        return self.state_service.get_conversation_summary(session_id, max_messages)
    
    def clear_session(self, session_id: str) -> None:
        """Clear session state."""
        self.state_service.clear_session(session_id)
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get full session state for debugging."""
        return self.state_service.get_state_dict(session_id)
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """Get AI service statistics."""
        return {
            "intent_service": self.llm_intent_service.get_stats(),
            "state_parser": {
                "llm_failures": self.llm_state_parser.llm_failures
            }
        }


# Singleton instance
_conversation_manager_v3 = None

def get_conversation_manager_v3(voxcore_engine=None) -> ConversationManagerV3:
    """Get or create conversation manager V3 singleton."""
    global _conversation_manager_v3
    if _conversation_manager_v3 is None:
        _conversation_manager_v3 = ConversationManagerV3(voxcore_engine=voxcore_engine)
    return _conversation_manager_v3
