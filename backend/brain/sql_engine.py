def generate(plan: dict):
    metric = plan["metric"]
    if plan["time_range"] == "last_3_months":
        interval = "3 months"
    elif plan["time_range"] == "last_6_months":
        interval = "6 months"
    else:
        interval = "3 months"
    return (
        f"SELECT {plan['time_col']}, SUM({metric}) as value "
        f"FROM {plan['table']} "
        f"WHERE {plan['time_col']} >= CURRENT_DATE - INTERVAL '{interval}' "
        f"GROUP BY {plan['time_col']} "
        f"ORDER BY {plan['time_col']} ASC"
    )
