"""
Refactored ConversationManager - Orchestrator pattern.

STEP 4: Clean Architecture

This is the orchestrator that chains the four services:
  1. IntentService: Understand what user wants
  2. StateService: Track conversation context
  3. QueryService: Build and execute SQL
  4. ResponseService: Format response

Flow:
  User Input
      ↓
  IntentService (What does user want?)
      ↓
  StateService (Remember what we're tracking)
      ↓
  QueryService (Build SQL + Governance + Execute)
      ↓
  ResponseService (Format results)
      ↓
  User Response

Benefits:
  ✅ Each service has one responsibility
  ✅ Easy to test in isolation
  ✅ Easy to swap implementations
  ✅ Easy to add new features
  ✅ Clear data flow
"""
from typing import Dict, Any, Optional
import logging

from voxcore.services.intent_service import get_intent_service
from voxcore.services.state_service import get_state_service
from voxcore.services.query_service import get_query_service
from voxcore.services.response_service import get_response_service

logger = logging.getLogger(__name__)


class ConversationManagerV2:
    """
    Refactored conversation manager using service orchestration.
    
    No longer a "God Object" - now an orchestrator that chains services.
    """
    
    def __init__(self, voxcore_engine=None):
        """
        Initialize conversation manager with services.
        
        Args:
            voxcore_engine: Optional VoxCoreEngine for governance
        """
        self.intent_service = get_intent_service()
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
        Process a user message end-to-end.
        
        Flow:
          1. Analyze intent (IntentService)
          2. Update state (StateService)
          3. Build & execute query (QueryService)
          4. Format response (ResponseService)
        
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
                "error": str or None
            }
        """
        logger.info(f"[{session_id}] Processing: {user_input}")
        
        try:
            # ─────────────────────────────────────────────────────────────
            # STEP 1: Analyze Intent
            # ─────────────────────────────────────────────────────────────
            intent = self.intent_service.analyze_intent(user_input)
            logger.info(f"[{session_id}] Intent: {intent['intent_type']} (confidence: {intent['confidence']:.2f})")
            
            # Check if clarification needed
            if intent.get("clarification_needed"):
                # Store ambiguous input in history and ask for clarification
                self.state_service.add_message(
                    session_id, "user", user_input,
                    metadata={"intent": intent}
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
                    "error": None
                }
            
            # ─────────────────────────────────────────────────────────────
            # STEP 2: Update Conversation State
            # ─────────────────────────────────────────────────────────────
            self.state_service.add_message(
                session_id, "user", user_input,
                metadata={"intent": intent}
            )
            
            # Update state with new metrics/dimensions
            if intent.get("metrics"):
                self.state_service.set_metrics(session_id, intent["metrics"])
            if intent.get("dimensions"):
                self.state_service.set_dimensions(session_id, intent["dimensions"])
            
            # Get context for query building
            context = self.state_service.get_context(session_id)
            logger.info(f"[{session_id}] Context: metrics={context.get('metrics')}, "
                       f"dimensions={context.get('dimensions')}")
            
            # ─────────────────────────────────────────────────────────────
            # STEP 3: Build and Execute Query
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
            
            logger.info(f"[{session_id}] Query: success={query_result['success']}, "
                       f"rows={query_result.get('row_count', 0)}, "
                       f"cost={query_result.get('cost_score', 0)}/100")
            
            # ─────────────────────────────────────────────────────────────
            # STEP 4: Format Response
            # ─────────────────────────────────────────────────────────────
            response_data = self.response_service.generate_response(
                query_result=query_result,
                intent=intent,
                context=context
            )
            
            # Store assistant response in history
            self.state_service.add_message(
                session_id, "assistant", response_data.get("message", ""),
                metadata={
                    "intent": intent,
                    "cost_score": query_result.get("cost_score"),
                    "execution_time_ms": query_result.get("execution_time_ms")
                }
            )
            
            # Record table access if query succeeded
            if query_result["success"]:
                # This would normally extract table names from SQL
                # For now, just track that query was executed
                self.state_service.add_message(session_id, "system", "Query executed")
            
            # Return complete response
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
                "error": response_data.get("error")
            }
        
        except Exception as e:
            logger.error(f"[{session_id}] Error: {e}", exc_info=True)
            
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
                "error": str(e)
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


# Singleton instance
_conversation_manager = None

def get_conversation_manager(voxcore_engine=None) -> ConversationManagerV2:
    """Get or create conversation manager singleton."""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManagerV2(voxcore_engine=voxcore_engine)
    return _conversation_manager
