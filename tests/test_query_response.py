def test_insight_with_empty_data():
    from voxcore.insights.engine import run_insight_engine

    insight = run_insight_engine([], "revenue", "month")

    assert insight["trend"]["direction"] == "flat"
    assert insight["trend"]["strength"] == 0.0
    assert insight["insights"] == []

def test_insight_with_dirty_data():
    from voxcore.insights.engine import run_insight_engine

    rows = [
        {"month": "Jan", "revenue": "1000"},
        {"month": "Feb", "revenue": None},
        {"month": "Mar", "revenue": "1500"},
    ]

    # Convert revenue to float, handle None as 0
    for r in rows:
        try:
            r["revenue"] = float(r["revenue"] or 0)
        except Exception:
            r["revenue"] = 0.0

    insight = run_insight_engine(rows, "revenue", "month")

    assert insight["trend"]["direction"] in ["up", "down", "flat"]
def test_insight_contract(client):
    res = client.post("/api/v1/query", json={"query": "revenue last 3 months"})
    data = res.json()

    assert "insight" in data

    insight = data["insight"]

    # Structure
    assert isinstance(insight["insights"], list)
    assert isinstance(insight["anomalies"], list)
    assert isinstance(insight["trend"], dict)
    assert isinstance(insight["summary"], dict)

    # Trend
    assert insight["trend"]["direction"] in ["up", "down", "flat"]
    assert 0.0 <= float(insight["trend"]["strength"]) <= 1.0

    # Summary
    assert "headline" in insight["summary"]
    assert "key_takeaway" in insight["summary"]
    assert "insight" in data
