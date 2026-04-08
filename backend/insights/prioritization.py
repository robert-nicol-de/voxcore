def score_insight(insight, trend, anomalies):
    base = 0.5

    # --- TYPE WEIGHT ---
    if insight["type"] == "root_cause":
        base += 0.3
    elif insight["type"] == "trend":
        base += 0.2
    elif insight["type"] == "anomaly":
        base += 0.25

    # --- TREND IMPACT ---
    strength = trend.get("strength", 0)

    if strength > 0.7:
        base += 0.2
    elif strength < 0.3:
        base -= 0.1

    # --- ANOMALY BOOST ---
    if insight["type"] == "anomaly":
        base += min(0.2, 0.05 * len(anomalies))

    # Clamp
    return max(0, min(1, round(base, 3)))

def prioritize_insights(insights, trend, anomalies):
    for i in insights:
        i["priority"] = score_insight(i, trend, anomalies)

    return sorted(insights, key=lambda x: x["priority"], reverse=True)
