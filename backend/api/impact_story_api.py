from fastapi import APIRouter
from voxcore.engine.insight_memory import InsightMemory

router = APIRouter()
from .action_api import ACTION_EXECUTIONS



insight_memory = InsightMemory()

def generate_impact_story(data):
    insight = data.get("insight", "")
    actions = data.get("actions", [])
    results = data.get("results", [])
    story = f"{insight}. "
    if actions:
        story += f"{actions[0]} was executed. "
    if results:
        impact = results[0]["impact"] * 100
        story += f"This resulted in a {impact:.1f}% improvement. "
    if len(results) > 1:
        extra = results[1]["impact"] * 100
        story += f"Further actions contributed an additional {extra:.1f}% growth."
    return story

@router.get("/api/insights/impact-story/{insight_id}")
def api_impact_story(insight_id: str):
    # Find the insight
    insight = next((i for i in insight_memory.get_all_insights() if i.get("id") == insight_id), None)
    if not insight:
        return {"story": "No insight found."}
    # Gather actions and results
    actions = [e["action_id"] for e in ACTION_EXECUTIONS if e.get("insight_id") == insight_id]
    results = [e for e in ACTION_EXECUTIONS if e.get("insight_id") == insight_id and e.get("impact") is not None]
    # Timeline events (optional)
    # timeline = get_timeline_events(insight_id)
    data = {
        "insight": insight.get("insight"),
        "actions": actions,
        "results": results,
    }
    story = generate_impact_story(data)
    return {"story": story}
