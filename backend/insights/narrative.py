def generate_narrative(metric, trend, root_cause, anomalies):
    direction = trend.get("direction")
    strength = trend.get("strength", 0)

    # --- HEADLINE ---
    if direction == "up":
        headline = f"{metric} is increasing"
    elif direction == "down":
        headline = f"{metric} is declining"
    else:
        headline = f"{metric} is stable"

    # Add strength qualifier
    if strength > 0.7:
        headline = headline.replace("is", "is strongly")
    elif strength < 0.3:
        headline = headline.replace("is", "is slightly")

    # --- ROOT CAUSE ---
    if root_cause:
        top = root_cause.get("top_driver", {})
        entity = top.get("entity")
        pct = int(top.get("contribution_pct", 0) * 100)

        if entity:
            headline += f", driven by {entity}"

    # --- KEY TAKEAWAY ---
    takeaway_parts = []

    if root_cause:
        drivers = root_cause.get("drivers", [])
        if drivers:
            driver_msgs = [
                f"{d['entity']} ({int(d['contribution_pct'] * 100)}%)"
                for d in drivers[:3]
            ]
            takeaway_parts.append(
                f"Top contributors: {', '.join(driver_msgs)}"
            )

    if anomalies:
        takeaway_parts.append(
            f"{len(anomalies)} anomaly detected"
            if len(anomalies) == 1
            else f"{len(anomalies)} anomalies detected"
        )

    if not takeaway_parts:
        takeaway_parts.append("No significant drivers or anomalies detected")

    key_takeaway = ". ".join(takeaway_parts)

    return {
        "headline": headline,
        "key_takeaway": key_takeaway
    }
