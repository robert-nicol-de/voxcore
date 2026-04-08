def generate(data: list, plan: dict):
    values = [row[plan["value_col"]] for row in data]
    start = values[0]
    end = values[-1]
    change = end - start
    pct_change = (change / start) if start != 0 else 0
    direction = "up" if change > 0 else "down" if change < 0 else "flat"
    strength = round(abs(pct_change), 2)
    avg = sum(values) / len(values)
    anomalies = []
    for i, v in enumerate(values):
        if abs(v - avg) / avg > 0.3:
            anomalies.append({
                "index": i,
                "value": v,
                "type": "spike" if v > avg else "drop"
            })
        metric = get_metric_from_semantic_registry(plan["metric"])
    if direction == "up":
        takeaway = f"{metric} increased by {round(pct_change*100,1)}% over the period"
    elif direction == "down":
        takeaway = f"{metric} decreased by {round(abs(pct_change)*100,1)}% over the period"
    else:
        takeaway = f"{metric} remained stable over the period"
    return {
        "trend": {
            "direction": direction,
            "strength": strength
        },
        "anomalies": anomalies,
        "summary": {
            "key_takeaway": takeaway,
            "confidence": 0.75
        }
    }
