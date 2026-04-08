def build(intent: dict):
    return {
        "table": "sales",
        "metric": intent["metric"],
        "trend": intent["trend"],
        "time_range": intent["time_range"],
        "time_col": "month",
        "value_col": "value"
    }
