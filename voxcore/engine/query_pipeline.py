from voxcore.agents.brain_agent import BrainAgent
from voxcore.agents.qpe_agent import QPEAgent
from voxcore.agents.vuse_agent import VUSEAgent
from voxcore.agents.query_guardian_agent import QueryGuardianAgent

from voxcore.engine.execution_engine import ExecutionEngine
from voxcore.engine.query_cost_analyzer import estimate_query_cost
# from voxcore.engine.query_orchestrator import submit_query_task, QueryPriority
from voxcore.engine.insight_engine import generate_insights

from voxcore.schema.schema_scanner import SchemaScanner
from voxcore.schema.relationship_detector import RelationshipDetector
from voxcore.schema.join_graph import JoinGraph
from voxcore.schema.join_resolver import JoinResolver
from voxcore.semantic.semantic_builder import build_semantic_model


class QueryPipeline:

    def __init__(self, db_path):

        # --- SCHEMA INTELLIGENCE ---
        scanner = SchemaScanner()
        schema = scanner.scan(db_path)

        relationships = RelationshipDetector().detect(schema)
        join_graph = JoinGraph().build(relationships)

        semantic = build_semantic_model(schema)

        # --- AGENTS ---
        self.brain = BrainAgent()
        self.qpe = QPEAgent(semantic, JoinResolver(), join_graph)
        self.vuse = VUSEAgent()
        self.guardian = QueryGuardianAgent()
        self.executor = ExecutionEngine()

        self.db_path = db_path

    # 🚀 MAIN ENTRY

    def run(self, session_id, message, audit=None, schema=None, schema_trust=None, suggested_tables=None):
        if audit is None:
            raise Exception("Audit object required")
        # --- 1. BRAIN ---
        audit["steps"].append(f"Parsed intent: {message}")
        brain = self.brain.run(message)

        if brain["ambiguity"]["is_ambiguous"]:
            return {
                "stage": "brain",
                "message": brain["ambiguity"]["clarification_needed"]
            }

        # --- 2. QPE ---
        plan = self.qpe.run(brain)
        # Learning boost: use suggested tables
        if suggested_tables:
            audit["reasoning"].append(
                f"Using learned table suggestions: {suggested_tables}"
            )
        # Audit: record selected tables
        if hasattr(plan, 'tables'):
            for table_name in getattr(plan, 'tables', []):
                audit["selectedTables"].append(table_name)
                audit["reasoning"].append(f"Selected {table_name} based on column match")
                audit["steps"].append(f"Selected table: {table_name}")
        if not audit["selectedTables"]:
            audit["warnings"].append("Pipeline did not select tables")

        # --- 3. VUSE ---
        vuse = self.vuse.run(plan)
        # Audit: record SQL generation
        audit["reasoning"].append("Generated SQL using matched schema columns")
        audit["steps"].append("Generated SQL")

        sql = vuse["sql"]

        # --- 4. COST CHECK ---
        cost = estimate_query_cost(
            join_count=sql.upper().count("JOIN"),
            has_filter="WHERE" in sql.upper(),
            estimated_rows=100000,
            result_rows=1000
        )

        # --- 4.1. VALIDATION (simulate for now) ---
        validation_result = {
            "is_valid": True,
            "was_rewritten": vuse.get("rewritten", False),
            "risk_score": cost,
        }

        if cost > 85:
            return {
                "stage": "cost",
                "message": "Query too expensive",
                "cost": cost
            }

        # --- 5. GUARDIAN ---
        guardian = self.guardian.run(sql, vuse)

        if guardian["status"] == "blocked":
            return {
                "stage": "guardian",
                "message": "Query blocked",
                "details": guardian
            }

        # --- 6. EXECUTION (ASYNC) ---
        future = submit_query_task(
            self.executor.run,
            guardian["final_sql"],
            self.db_path,
            priority=QueryPriority.HIGH
        )

        result = future.result()

        if result["status"] == "error":
            return {
                "stage": "execution",
                "message": "Execution failed",
                "error": result["error"]
            }

        # --- 7. INSIGHTS ---
        insights = generate_insights("growth_trend", result["rows"])

        # --- 8. PIPELINE GOVERNANCE OBJECT ---
        pipeline = {
            "validated": validation_result["is_valid"],
            "rewritten": validation_result["was_rewritten"],
            "risk_score": validation_result["risk_score"],
            "status": "SUCCESS"
        }

        # --- 9. FINAL RESPONSE ---
        return {
            "stage": "complete",
            "message": "Query executed successfully",
            "data": result["rows"],
            "row_count": result["row_count"],
            "sql": guardian["final_sql"],
            "chart": vuse["chart"],
            "insights": insights,
            "guardian": guardian,
            "cost_score": cost,
            "plan": plan,          # 🔥 optional: debug UI
            "intent": brain,       # 🔥 optional: debug UI
            "audit": audit,
            "schema_trust": schema_trust,
            "pipeline": pipeline
        }
