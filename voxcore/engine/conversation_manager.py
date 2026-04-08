"""
VoxCore Conversation Manager
Handles user messages, intent detection, routing, and dashboard synchronization.
"""

from voxcore.engine.conversation_memory import ConversationMemory
from voxcore.engine.conversation_state_engine import ConversationStateEngine
from voxcore.engine.insight_narrative_engine import InsightNarrativeEngine
from voxcore.engine.exploration_engine import generate_related_queries
from voxcore.agents.brain_agent import BrainAgent
from voxcore.agents.qpe_agent import QPEAgent
from voxcore.agents.query_guardian_agent import QueryGuardianAgent
from voxcore.agents.vuse_agent import VUSEAgent



from voxcore.engine.execution_engine import ExecutionEngine
from voxcore.engine.insight_engine import generate_insights

"""
DEPRECATED: ConversationManager is no longer used. Please use QueryPipeline instead.
This file is retained for reference only and will be removed in a future cleanup.
"""

class ConversationManager:
    def __init__(self, state_engine=None, memory=None, query_router=None, narrative_engine=None, exploration_engine=None, demo_mode=False):
        self.state_engine = state_engine or ConversationStateEngine()
        self.memory = memory or ConversationMemory()
        self.narrative_engine = narrative_engine or InsightNarrativeEngine()
        from voxcore.engine.exploration_engine import generate_related_queries
        self.exploration_engine = exploration_engine or type('ExplorationEngine', (), {"generate_related_queries": staticmethod(generate_related_queries)})()
        self.demo_mode = demo_mode
        self.brain = BrainAgent()
        self.qpe = QPEAgent()
        self.vuse = VUSEAgent()
        self.guardian = QueryGuardianAgent()
        self.executor = ExecutionEngine()

    def handle_message(self, session_id, message, db_path, max_rows=1000, timeout=10, demo_db=False):
        print("STEP 1: API received message")
        # 1. BRAIN
        brain_output = self.brain.run(message)

        if brain_output["ambiguity"]["is_ambiguous"]:
            return {
                "message": brain_output["ambiguity"]["clarification_needed"]
            }
        print("STEP 2: Context built:", brain_output)

        # 2. QPE
        plan = self.qpe.run(brain_output)

        # 3. VUSE
        vuse_output = self.vuse.run(plan)

        # 4. GUARDIAN
        print("STEP 3: RBAC check for user:", session_id)
        guardian = self.guardian.run(
            sql=vuse_output["sql"],
            metadata=vuse_output
        )
        print("STEP 5: Inspector issues:", guardian.get("risk_flags"))
        print("STEP 6: Risk score:", guardian.get("risk_score"))
        print("STEP 7: Policy decision:", guardian.get("status"))

        if guardian["status"] == "blocked":
            return {
                "message": "Query blocked for safety",
                "guardian": guardian
            }

        # 5. EXECUTION
        print("STEP 4: Generated SQL:", guardian.get("final_sql"))
        print("STEP 9: Executing query")
        result = self.executor.run(
            sql=guardian["final_sql"],
            db_path=db_path
        )

        if result["status"] == "error":
            print("STEP 13: Redacted error:", result["error"])
            return {
                "message": "Execution failed",
                "error": result["error"]
            }

        # 6. INSIGHTS
        print("STEP 10: Masked result:", result["rows"])
        insights = generate_insights("growth_trend", result["rows"])
        print("STEP 11: Insight generated:", insights)

        # 7. RESPONSE
        response = {
            "message": "Query executed successfully",
            "data": result["rows"],
            "row_count": result["row_count"],
            "insights": insights,
            "guardian": guardian,
            "sql": guardian["final_sql"]
        }
        print("STEP 14: Final response:", response)



    def run_exploration(self, message, state):
        # Use Exploration Engine
        return {"type": "exploration", "chart": {}}

    def handle_root_cause(self, message, state):
        # Use Insight Memory and Narrative Engine
        return {"type": "root_cause", "chart": {}}

    def handle_explain_data(self, message, state):
        # Use Explain My Data
        return {"type": "explain_data", "chart": {}}

    def vuse(self):
        return self.vuse_agent
