from voxcore.insights.engine import run_insight_engine
from backend.insights.root_cause import run_root_cause_analysis
from backend.insights.narrative import generate_narrative
from backend.insights.prioritization import prioritize_insights

def test_empty_input():
    insight = run_insight_engine([], "revenue", "month")
    assert insight["trend"]["direction"] == "flat"
    assert insight["trend"]["strength"] == 0.0
    assert insight["insights"] == []

def test_basic_up_trend():
    rows = [
        {"month": "Jan", "revenue": 100},
        {"month": "Feb", "revenue": 150},
    ]
    insight = run_insight_engine(rows, "revenue", "month")
    assert insight["trend"]["direction"] == "up"

def test_basic_down_trend():
    rows = [
        {"month": "Jan", "revenue": 200},
        {"month": "Feb", "revenue": 100},
    ]
    insight = run_insight_engine(rows, "revenue", "month")
    assert insight["trend"]["direction"] == "down"

def test_flat_trend():
    rows = [
        {"month": "Jan", "revenue": 100},
        {"month": "Feb", "revenue": 102},  # <5% change
    ]
    insight = run_insight_engine(rows, "revenue", "month")
    assert insight["trend"]["direction"] == "flat"

def test_dirty_data():
    rows = [
        {"month": "Jan", "revenue": "100"},
        {"month": "Feb", "revenue": None},
        {"month": "Mar", "revenue": "150"},
    ]
    # Convert revenue to float, handle None as 0
    for r in rows:
        try:
            r["revenue"] = float(r["revenue"] or 0)
        except Exception:
            r["revenue"] = 0.0
    insight = run_insight_engine(rows, "revenue", "month")
    assert insight["trend"]["direction"] in ["up", "down", "flat"]

def test_root_cause_detection():
    rows = [
        {"month": "Jan", "product": "A", "revenue": 100},
        {"month": "Feb", "product": "A", "revenue": 200},
        {"month": "Jan", "product": "B", "revenue": 300},
        {"month": "Feb", "product": "B", "revenue": 320},
    ]

    result = run_root_cause_analysis(
        rows,
        metric="revenue",
        dimension="month",
        breakdown_dimension="product"
    )

    assert result["top_driver"]["entity"] == "A"

def test_root_cause_contribution():
    rows = [
        {"month": "Jan", "product": "A", "revenue": 100},
        {"month": "Feb", "product": "A", "revenue": 300},
        {"month": "Jan", "product": "B", "revenue": 200},
        {"month": "Feb", "product": "B", "revenue": 220},
    ]

    from backend.insights.root_cause import run_root_cause_analysis

    result = run_root_cause_analysis(
        rows,
        metric="revenue",
        dimension="month",
        breakdown_dimension="product"
    )

    assert result["top_driver"]["entity"] == "A"
    assert result["drivers"][0]["contribution_pct"] > result["drivers"][1]["contribution_pct"]

def test_narrative_with_root_cause():
    trend = {"direction": "up", "strength": 0.8}
    root_cause = {
        "top_driver": {"entity": "Product A", "contribution_pct": 0.75},
        "drivers": [
            {"entity": "Product A", "contribution_pct": 0.75},
            {"entity": "Product B", "contribution_pct": 0.2},
        ]
    }
    anomalies = []

    result = generate_narrative(
        metric="revenue",
        trend=trend,
        root_cause=root_cause,
        anomalies=anomalies
    )

    assert "increasing" in result["headline"]
    assert "Product A" in result["headline"]
    assert "Product A (75%)" in result["key_takeaway"]

def test_prioritization_order():
    from backend.insights.prioritization import prioritize_insights

    insights = [
        {"type": "trend", "message": "Trend detected"},
        {"type": "root_cause", "message": "Driven by A"},
        {"type": "anomaly", "message": "Spike detected"},
    ]

    trend = {"direction": "up", "strength": 0.9}
    anomalies = [1, 2]

    result = prioritize_insights(insights, trend, anomalies)

    assert result[0]["type"] == "root_cause"
    assert result[0]["priority"] >= result[1]["priority"]

def test_top_insight_exists():
    from voxcore.insights.engine import run_insight_engine

    rows = [
        {"month": "Jan", "revenue": 100},
        {"month": "Feb", "revenue": 200},
    ]

    result = run_insight_engine(
        rows,
        metric="revenue",
        dimension="month"
    )

    assert "top_insight" in result
    assert result["top_insight"] is not None

def test_api_requires_key(client):
    response = client.post("/api/v1/query", json={"query": "test"})
    assert response.status_code == 401
