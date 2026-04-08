MONTH_ORDER = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def safe_sort(rows, dimension):
    try:
        sample = rows[0].get(dimension) if rows else None
        # Month sorting
        if isinstance(sample, str) and sample in MONTH_ORDER:
            return sorted(rows, key=lambda x: MONTH_ORDER.get(x.get(dimension), 0))
        # Default sorting
        return sorted(rows, key=lambda x: x.get(dimension))
    except Exception:
        return rows

def run_insight_engine(rows, metric, dimension=None):
    from backend.insights.root_cause import run_root_cause_analysis
    from backend.insights.narrative import generate_narrative
    from backend.insights.prioritization import prioritize_insights
    def build_empty_insight():
        return {
            "insights": [],
            "trend": {"direction": "flat", "strength": 0.0},
            "anomalies": [],
            "summary": {"headline": "", "key_takeaway": ""}
        }

    try:
        if not rows:
            return build_empty_insight()

        # CRITICAL FIX: sort rows by dimension
        if dimension:
            rows = safe_sort(rows, dimension)

        values = [float(r.get(metric, 0) or 0) for r in rows]
        if len(values) < 2:
            return build_empty_insight()

        first, last = values[0], values[-1]
        delta = last - first
        pct_change = 0.0
        if abs(first) > 1e-6:
            pct_change = delta / abs(first)

        # Flat if <5% change
        if abs(pct_change) < 0.05:
            direction = "flat"
        elif delta > 0:
            direction = "up"
        else:
            direction = "down"

        strength = min(1.0, max(0.0, abs(pct_change)))
        insight_msg = f"{metric} changed {round(delta, 2)} ({direction})"

        insights_list = [
            {"type": "trend", "message": insight_msg}
        ]

        # v1: use dimension as breakdown_dimension
        breakdown_dimension = dimension if dimension else None
        root_cause = None
        if breakdown_dimension:
            root_cause = run_root_cause_analysis(
                rows,
                metric,
                dimension,
                breakdown_dimension
            )
        if root_cause:
            top = root_cause["top_driver"]
            drivers = root_cause["drivers"]

            driver_msgs = [
                f"{d['entity']} ({int(d['contribution_pct'] * 100)}%)"
                for d in drivers
            ]

            insights_list.append({
                "type": "root_cause",
                "message": f"{metric} change was primarily driven by {', '.join(driver_msgs)}"
            })

        trend = {
            "direction": direction,
            "strength": round(strength, 4)
        }
        anomalies = []  # placeholder for future anomaly logic
        summary = generate_narrative(
            metric=metric,
            trend=trend,
            root_cause=root_cause,
            anomalies=anomalies
        )

        insights_list = prioritize_insights(
            insights_list,
            trend,
            anomalies
        )
        if insights_list:
            top_insight = insights_list[0]
        else:
            top_insight = {
                "type": "none",
                "message": "No significant insights detected",
                "priority": 0.0
            }
        return {
            "insights": insights_list,
            "top_insight": top_insight,
            "trend": trend,
            "anomalies": anomalies,
            "summary": summary
        }
    except Exception:
        return build_empty_insight()
