# --- Router must be defined first ---
from fastapi import APIRouter, HTTPException
router = APIRouter()
from backend.engine.action_engine import generate_actions, generate_ai_actions
# 🧠 SUGGESTED ACTIONS API
@router.get("/api/insights/actions/{insight_id}")
async def get_insight_actions(insight_id: str):
    # For demo: find insight by id using InsightMemory (replace with real DB)
    from voxcore.engine.insight_memory import InsightMemory
    insight_memory = InsightMemory()
    try:
        insight = next(i for i in insight_memory.get_all_insights() if i["id"] == insight_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Insight not found")

    # Static rule-based actions
    actions = generate_actions(insight)

    # AI actions (stub: replace with real LLM call)
    def fake_llm(prompt):
        return [
            {"title": "Check inventory", "priority": "high", "impact": "high", "description": "Ensure stock levels are sufficient."},
            {"title": "Review campaign", "priority": "medium", "impact": "medium", "description": "Analyze recent marketing efforts."}
        ]
    ai_actions = generate_ai_actions(insight, context={}, llm=fake_llm)

    return {
        "summary": f"Suggested actions for: {insight['insight']}",
        "actions": actions + ai_actions
    }

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from voxcore.engine.main_query_engine import process_user_question

router = APIRouter()

@router.post("/api/user/event")
async def track_event(event: dict):
    user_id = event.get("user_id", "anonymous")
    from backend.engine.user_behavior import user_behavior
    user_behavior.store(user_id, event)
    return {"status": "tracked"}

@router.post("/api/pr/drilldown")
async def drilldown(insight: dict):
    from backend.engine.drilldown_generator import generate_drilldown_query
    query = generate_drilldown_query(insight["insight"])
    return {
        "query": query
    }

from backend.engine.architect_router import ArchitectRouter, sort_by_pipeline
from backend.engine.ai_router import route_with_ai


from backend.engine.pipeline_memory import pipeline_memory
from backend.engine.semantic_memory import semantic_memory
from backend.engine.query_refiner import refine_query_with_ai
from backend.engine.alert_engine import alert_engine

router = APIRouter()

# TEMP in-memory store (upgrade later to DB)
PR_STORE: List[dict] = []

class PRRequest(BaseModel):
    title: str
    type: str
    domain: str
    problem: str
    approach: str

router_engine = ArchitectRouter()

@router.post("/api/pr/create")
async def create_pr(pr: PRRequest):
    pr_data = pr.dict()
    pr_data["status"] = "draft"

    PR_STORE.append(pr_data)

    return {
        "status": "created",
        "pr": pr_data
    }

@router.get("/api/pr/list")
async def list_prs():
    return {"prs": PR_STORE}

@router.post("/api/pr/execute")
async def execute_pr(pr: PRRequest):

        # 🟡 STEP 2 — AI REFINEMENT (GROQ)
        # (Legacy refine_query removed; now using Groq LLM)
    """
    Execute PR as a real system task with pipeline context
    """

    # 🟠 Get user_id for personalization
    user_id = getattr(pr, "metadata", {}).get("user_id", "anonymous") if hasattr(pr, "metadata") else "anonymous"
    # 🧠 1. AI Multi-domain routing (Groq)
    ai_route = route_with_ai(pr.problem)
    routes = [
        {
            "domain": d["name"],
            "confidence": d["confidence"]
        }
        for d in ai_route["domains"]
    ]
    pipeline_context["logs"].append(f"AI routing applied: {ai_route['reason']}")
    pipeline_context["routing_reason"] = ai_route["reason"]
    # 🟡 Hybrid fallback for safety
    if not routes:
        routes = router_engine.route_multi(pr.problem)
        pipeline_context["logs"].append("Fallback to rule-based routing")
        pipeline_context["routing_reason"] = "Fallback to rule-based routing"
    # 🟢 Store routing memory
    pipeline_memory.store({
        "question": pr.problem,
        "route": routes,
        "type": "routing"
    })
    # 🧠 2. Order by pipeline
    ordered_routes = sort_by_pipeline(routes)

    # 🚀 STEP 1 — INTRODUCE PIPELINE CONTEXT
    pipeline_context = {
        "question": pr.problem,
        "data": None,
        "validated": False,
        "insights": None,
        "logs": []
    }


    # 🚀 STEP 1 — DEFINE CONDITIONS (RULE ENGINE)
    CONDITIONS = {
        "Query Intelligence": lambda ctx: True,
        "Governance & Safety": lambda ctx: ctx.get("data") is not None,
        "Insight Engine": lambda ctx: ctx.get("validated") is True,
        "Frontend UI/UX": lambda ctx: ctx.get("insights") is not None,
    }

    # 🟠 STEP 2 — APPLY CONDITIONS IN PIPELINE LOOP

    results = []
    for step in ordered_routes:
        domain = step["domain"]

        # 🧠 CHECK CONDITION FIRST
        condition = CONDITIONS.get(domain, lambda ctx: True)
        if not condition(pipeline_context):
            results.append({
                "domain": domain,
                "confidence": step["confidence"],
                "result": {"message": "Skipped (condition not met)"}
            })
            pipeline_context["logs"].append(f"{domain} skipped")
            continue

        # ⚡ EXECUTION
        if domain == "Query Intelligence":
            original_question = pipeline_context["question"]
            match, score = semantic_memory.find_best_match(original_question, threshold=0.8)
            if match:
                pipeline_context["question"] = match["refined"]
                pipeline_context["logs"].append(
                    f"Semantic memory applied (score={score})"
                )

            MAX_RETRIES = 2
            success = False
            for attempt in range(MAX_RETRIES):
                try:
                    result = process_user_question(
                        question=pipeline_context["question"],
                        db_connection=None
                    )
                    if result:
                        pipeline_context["data"] = result
                        pipeline_context["logs"].append(f"Query success (attempt {attempt+1})")
                        success = True
                        break
                except Exception as e:
                    pipeline_context["logs"].append(f"Query failed (attempt {attempt+1})")
                    # 🧠 SELF-HEALING ACTION (AI REFINEMENT WITH FALLBACK)
                    try:
                        refined = refine_query_with_ai(pipeline_context["question"])
                    except Exception:
                        refined = pipeline_context["question"]  # fallback
                    pipeline_context["question"] = refined
                    pipeline_context["logs"].append("AI refinement applied (Groq)")
            if not success:
                pipeline_context["logs"].append("Query failed after retries")
                results.append({
                    "domain": domain,
                    "confidence": step["confidence"],
                    "result": {"message": "No data, pipeline stopped"}
                })
                break
            else:
                result = pipeline_context["data"]
                # 🟡 STEP 3 — STORE LEARNING SEMANTICALLY
                semantic_memory.store(
                    question=original_question,
                    refined=pipeline_context["question"]
                )
                pipeline_context["logs"].append(
                    "Stored semantic learning"
                )

        elif domain == "Governance & Safety":
            if pipeline_context["data"] is None:
                result = {"message": "No data to validate"}
            else:
                pipeline_context["validated"] = True
                result = {"message": "Validation passed"}

            if not pipeline_context["validated"]:
                pipeline_context["logs"].append("Validation failed → stopping pipeline")
                results.append({
                    "domain": domain,
                    "confidence": step["confidence"],
                    "result": {"message": "Validation failed, pipeline stopped"}
                })
                break
            pipeline_context["logs"].append("Validation complete")

        elif domain == "Insight Engine":
            if not pipeline_context["validated"]:
                result = {"message": "Skipped (not validated)"}
            else:
                if not pipeline_context["data"]:
                    result = {"message": "No data → cannot generate insights"}
                else:
                    from backend.engine.insight_generator import generate_ranked_insights_with_ai
                    try:
                        insights = generate_ranked_insights_with_ai(
                            pipeline_context["data"],
                            pipeline_context["question"]
                        )
                        # Personalize ranking using user behavior (per user)
                        from backend.engine.user_behavior import user_behavior
                        prefs = user_behavior.get_preferences(user_id)
                        def score_insight(insight):
                            base = insight["confidence"]
                            if insight["type"] in prefs:
                                base += 0.1 * prefs[insight["type"]]
                            return base
                        insights = sorted(
                            insights,
                            key=score_insight,
                            reverse=True
                        )
                        pipeline_context["insights"] = insights
                        result = {"message": "AI ranked insights generated"}
                        pipeline_context["logs"].append("AI ranked insights generated")
                        pipeline_context["logs"].append("Insights personalized based on user behavior")
                        # STEP 2 — ALERT ENGINE
                        alerts = alert_engine.evaluate(
                            pipeline_context["insights"],
                            prefs,
                            user_id
                        )
                        pipeline_context["alerts"] = alerts
                        if alerts:
                            pipeline_context["logs"].append("Alerts triggered")
                    except Exception:
                        pipeline_context["insights"] = [
                            {
                                "insight": "Fallback insight",
                                "type": "trend",
                                "confidence": 0.5
                            }
                        ]
                        result = {"message": "Insights generated (fallback)"}
                        pipeline_context["logs"].append("Insight fallback used")
            pipeline_context["logs"].append("Insight step completed")

        else:
            result = {"message": f"Handled by {domain}"}

        results.append({
            "domain": domain,
            "confidence": step["confidence"],
            "result": result
        })

    # 🟡 STEP 3 — RETURN FULL CONTEXT
    return {
        "status": "executed",
        "pipeline": ordered_routes,
        "results": results,
        "context": pipeline_context
    }
