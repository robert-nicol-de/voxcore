"""
VoxCore Conversation Manager
Handles user messages, intent detection, routing, and dashboard synchronization.
"""
from voxcore.engine.conversation_memory import ConversationMemory
from voxcore.engine.conversation_state_engine import ConversationStateEngine
from voxcore.engine.insight_narrative_engine import InsightNarrativeEngine

from voxcore.engine.exploration_engine import generate_related_queries


class ConversationManager:
    def __init__(self, state_engine=None, memory=None, query_router=None, narrative_engine=None, exploration_engine=None, demo_mode=False):
        self.state_engine = state_engine or ConversationStateEngine()
        self.memory = memory or ConversationMemory()
        self.query_router = query_router or self
        self.narrative_engine = narrative_engine or InsightNarrativeEngine()
        from voxcore.engine.exploration_engine import generate_related_queries
        self.exploration_engine = exploration_engine or type('ExplorationEngine', (), {"generate_related_queries": staticmethod(generate_related_queries)})()
        self.demo_mode = demo_mode

    def handle_message(self, session_id, message, max_rows=1000, timeout=10, demo_db=False):
        # 1. Retrieve current state
        state = self.state_engine.get_state(session_id)
        # 2. Detect intent
        intent = self.detect_intent(message)
        # 3. Extract and update state
        updates = self.extract_state_updates(message)
        updated_state = self.state_engine.update_state(session_id, updates)
        # 4. Route query (could be replaced by a real QueryRouter)
        # Playground/demo DB routing
        db_path = None
        if self.demo_mode or demo_db:
            import os
            db_path = os.path.join(os.path.dirname(__file__), '../playground/demo_database.db')
        # Pass db_path, max_rows, timeout to query_router if supported
        if hasattr(self.query_router, 'route'):
            result = self.query_router.route(message, updated_state, intent, db_path=db_path, max_rows=max_rows, timeout=timeout)
        else:
            result = self.route_query(message, updated_state, intent)
        # 5. Generate narrative
        narrative = self.narrative_engine.generate(result)
        # 6. Generate exploration suggestions
        suggestions = self.exploration_engine.generate_related_queries(updated_state)
        # 7. Store chat history
        self.memory.store_message(session_id, message, narrative)
        # 8. Return structured response for dashboard sync
        return {
            "message": narrative,
            "data": result.get("data"),
            "chart": result.get("chart"),
            "suggestions": [f"{s['metric']} by {s['dimension']}" for s in suggestions]
        }

    def detect_intent(self, message):
        m = message.lower()
        if "why" in m:
            return "root_cause"
        if "trend" in m:
            return "trend_analysis"
        if "compare" in m:
            return "comparison"
        if "explore" in m:
            return "exploration"
        if "explain" in m:
            return "explain_dataset"
        return "data_query"

    def extract_state_updates(self, message):
        updates = {}
        m = message.lower()
        if "revenue" in m:
            updates["metric"] = "revenue"
        if "sales" in m:
            updates["metric"] = "sales"
        if "region" in m:
            updates["dimension"] = "region"
        if "product" in m:
            updates["dimension"] = "product"
        if "category" in m:
            updates["dimension"] = "category"
        if "customer" in m:
            updates["dimension"] = "customer"
        if "last quarter" in m:
            updates["time_filter"] = "last_quarter"
        if "last month" in m:
            updates["time_filter"] = "last_month"
        if "last week" in m:
            updates["time_filter"] = "last_week"
        if "this year" in m:
            updates["time_filter"] = "this_year"
        # Add more extraction rules as needed
        return updates

    def route_query(self, message, state, intent):
        # Placeholder: integrate with query planner, SQL pipeline, insight engine, etc.
        # Example: return a technical insight dict
        if intent == "data_query":
            return {"type": "trend_decline", "metric": state.get("metric", "revenue"), "percent_change": 18, "entity": state.get("entity_focus", "South region"), "period": state.get("time_filter", "last month"), "chart": {"type": "bar", "dimension": state.get("dimension", "region"), "metric": state.get("metric", "revenue")}}
        if intent == "root_cause":
            return {"type": "root_cause", "metric": state.get("metric", "revenue"), "entity": state.get("entity_focus", "South region"), "cause": "Outdoor category drop", "chart": {"type": "graph"}}
        if intent == "explore":
            return {"type": "exploration", "metric": state.get("metric", "revenue"), "dimension": state.get("dimension", "product"), "chart": {"type": "bar"}}
        return {"type": "generic", "chart": {}}

    def handle_follow_up(self, message, context, state):
        # Use context and state to resolve follow-up
        return {"type": "follow_up", "chart": {}}

    def run_exploration(self, message, state):
        # Use Exploration Engine
        return {"type": "exploration", "chart": {}}

    def handle_root_cause(self, message, state):
        # Use Insight Memory and Narrative Engine
        return {"type": "root_cause", "chart": {}}

    def handle_explain_data(self, message, state):
        # Use Explain My Data
        return {"type": "explain_data", "chart": {}}
