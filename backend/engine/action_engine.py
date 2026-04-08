def generate_actions(insight):
    actions = []

    if insight["type"] == "decline_trend":
        actions.append({
            "title": "Investigate recent changes",
            "description": "Check pricing, promotions, or supply issues",
            "priority": "high"
        })

    if insight["type"] == "anomaly_detection":
        actions.append({
            "title": "Validate anomaly source",
            "description": "Check if spike is due to campaign or data issue",
            "priority": "high"
        })

    return actions

# AI Layer (LLM-powered)
def generate_ai_actions(insight, context, llm):
    prompt = f"""
    Insight: {insight['insight']}
    Type: {insight['type']}

    Suggest 3-5 business actions with priority and reasoning.
    """
    return llm(prompt)
