"""
VoxCore Playground Insights Engine.

Provides the Explain My Data feature, a ranked VIIS-style business insight
report, and an Ask Why investigation endpoint over the demo dataset.
"""
from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

# ---------------------------------------------------------------------------
# Demo dataset — Northwind Retail Group sandbox data
# Extended to support trend analysis across three calendar months.
# ---------------------------------------------------------------------------

_DEMO_ORDERS = [
    # January
    {"order_id": 1,  "customer_id": 5, "product": "Headphones",  "country": "Canada", "amount": 850,  "month": "January",  "month_order": 1, "weekday": "Friday",    "salesperson": "Maya"},
    {"order_id": 2,  "customer_id": 2, "product": "Headphones",  "country": "Canada", "amount": 420,  "month": "January",  "month_order": 1, "weekday": "Tuesday",   "salesperson": "Elena"},
    {"order_id": 3,  "customer_id": 6, "product": "Keyboard",    "country": "USA",    "amount": 300,  "month": "January",  "month_order": 1, "weekday": "Friday",    "salesperson": "Maya"},
    # February
    {"order_id": 4,  "customer_id": 3, "product": "Keyboard",    "country": "USA",    "amount": 1200, "month": "February", "month_order": 2, "weekday": "Wednesday", "salesperson": "Jordan"},
    {"order_id": 5,  "customer_id": 6, "product": "Monitor",     "country": "USA",    "amount": 800,  "month": "February", "month_order": 2, "weekday": "Friday",    "salesperson": "Jordan"},
    {"order_id": 6,  "customer_id": 1, "product": "Keyboard",    "country": "USA",    "amount": 650,  "month": "February", "month_order": 2, "weekday": "Monday",    "salesperson": "Elena"},
    # March
    {"order_id": 7,  "customer_id": 1, "product": "Laptop",      "country": "USA",    "amount": 2000, "month": "March",    "month_order": 3, "weekday": "Friday",    "salesperson": "Jordan"},
    {"order_id": 8,  "customer_id": 2, "product": "Monitor",     "country": "Canada", "amount": 1500, "month": "March",    "month_order": 3, "weekday": "Thursday",  "salesperson": "Maya"},
    {"order_id": 9,  "customer_id": 4, "product": "Laptop",      "country": "UK",     "amount": 900,  "month": "March",    "month_order": 3, "weekday": "Friday",    "salesperson": "Jordan"},
    {"order_id": 10, "customer_id": 3, "product": "Headphones",  "country": "USA",    "amount": 380,  "month": "March",    "month_order": 3, "weekday": "Tuesday",   "salesperson": "Elena"},
]

_DEMO_CUSTOMERS = {
    1: {"name": "John",  "country": "USA"},
    2: {"name": "Sarah", "country": "Canada"},
    3: {"name": "Mike",  "country": "USA"},
    4: {"name": "Ava",   "country": "UK"},
    5: {"name": "Liam",  "country": "Canada"},
    6: {"name": "Noah",  "country": "USA"},
}

_MONTH_ORDER = ["January", "February", "March"]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _pct_change(old: float, new: float) -> int:
    if old == 0:
        return 100
    return round((new - old) / old * 100)


def _total_revenue() -> int:
    return sum(o["amount"] for o in _DEMO_ORDERS)


def _average_order_value() -> float:
    return _total_revenue() / len(_DEMO_ORDERS)


def _aggregate_by(key: str) -> dict[str, int]:
    values: dict[str, int] = {}
    for order in _DEMO_ORDERS:
        values[str(order[key])] = values.get(str(order[key]), 0) + int(order["amount"])
    return values


def _monthly_revenue() -> dict[str, int]:
    return _aggregate_by("month")


def _product_country_revenue() -> dict[tuple[str, str], int]:
    values: dict[tuple[str, str], int] = {}
    for order in _DEMO_ORDERS:
        key = (str(order["product"]), str(order["country"]))
        values[key] = values.get(key, 0) + int(order["amount"])
    return values


# ---------------------------------------------------------------------------
# Insight categories
# ---------------------------------------------------------------------------

def _dataset_summary() -> list[str]:
    total = _total_revenue()
    order_count = len(_DEMO_ORDERS)
    customer_count = len({o["customer_id"] for o in _DEMO_ORDERS})
    product_count = len({o["product"] for o in _DEMO_ORDERS})
    avg = round(_average_order_value())

    return [
        f"Total revenue is ${total:,} across {order_count} orders",
        f"Average order value is ${avg:,} across {customer_count} active customers",
        f"The sandbox dataset currently spans {product_count} products across 3 countries",
    ]


def _top_performers() -> list[str]:
    total = _total_revenue()
    product_rev = _aggregate_by("product")
    country_rev = _aggregate_by("country")
    salesperson_rev = _aggregate_by("salesperson")

    top_product = max(product_rev, key=lambda p: product_rev[p])
    top_country = max(country_rev, key=lambda c: country_rev[c])
    top_salesperson = max(salesperson_rev, key=lambda s: salesperson_rev[s])
    top_customer = max(
        _DEMO_CUSTOMERS,
        key=lambda customer_id: sum(
            o["amount"] for o in _DEMO_ORDERS if o["customer_id"] == customer_id
        ),
    )
    top_customer_spend = sum(
        o["amount"] for o in _DEMO_ORDERS if o["customer_id"] == top_customer
    )

    return [
        f"{top_product} is the top selling product generating {round(product_rev[top_product] / total * 100)}% of revenue",
        f"{top_country} generates the highest sales at ${country_rev[top_country]:,}",
        f"{top_salesperson} leads the sales team with ${salesperson_rev[top_salesperson]:,} booked",
        f"{_DEMO_CUSTOMERS[top_customer]['name']} is the top customer with ${top_customer_spend:,} in spend",
    ]


def _trend_detection() -> list[str]:
    month_rev: dict[str, int] = {}
    month_count: dict[str, int] = {}
    for o in _DEMO_ORDERS:
        m = o["month"]
        month_rev[m] = month_rev.get(m, 0) + o["amount"]
        month_count[m] = month_count.get(m, 0) + 1

    months = [m for m in _MONTH_ORDER if m in month_rev]
    trends: list[str] = []

    for i in range(1, len(months)):
        prev, curr = months[i - 1], months[i]
        pct = _pct_change(month_rev[prev], month_rev[curr])
        direction = "increased" if pct >= 0 else "declined"
        abs_pct = abs(pct)
        trends.append(
            f"Revenue {direction} {abs_pct}% from {prev} (${month_rev[prev]:,}) to {curr} (${month_rev[curr]:,})"
        )

    if len(months) >= 2:
        last_two = months[-2:]
        order_pct = _pct_change(month_count[last_two[0]], month_count[last_two[1]])
        direction = "up" if order_pct >= 0 else "down"
        trends.append(
            f"Order volume is {direction} {abs(order_pct)}% in {last_two[1]} compared to {last_two[0]}"
        )

    return trends


def _distribution_analysis() -> list[str]:
    total = _total_revenue()
    product_rev = sorted(_aggregate_by("product").items(), key=lambda item: item[1], reverse=True)
    top_three = product_rev[:3]
    top_three_value = sum(value for _, value in top_three)
    top_three_share = round(top_three_value / total * 100)

    high_value_orders = sum(1 for order in _DEMO_ORDERS if order["amount"] >= _average_order_value())
    high_value_share = round(high_value_orders / len(_DEMO_ORDERS) * 100)

    return [
        f"Top 3 products contribute {top_three_share}% of total revenue",
        f"{high_value_share}% of orders are at or above the average order value, showing a concentrated revenue mix",
        f"Revenue concentration is highest in {top_three[0][0]} and {top_three[1][0]}, which together generate ${top_three[0][1] + top_three[1][1]:,}",
    ]


def _outlier_detection() -> list[str]:
    amounts = [o["amount"] for o in _DEMO_ORDERS]
    avg = sum(amounts) / len(amounts)
    outliers: list[str] = []

    for o in _DEMO_ORDERS:
        ratio = o["amount"] / avg
        if ratio >= 1.8:
            multiplier = round(ratio, 1)
            outliers.append(
                f"Order #{o['order_id']} ({o['product']}, ${o['amount']:,}) is {multiplier}× the average order value"
            )

    if not outliers:
        outliers.append("No significant outliers detected — order values are within a normal range")

    min_amt = min(amounts)
    max_amt = max(amounts)
    spread = round((max_amt - min_amt) / avg * 100)
    outliers.append(
        f"Order value spread is {spread}% of average (min ${min_amt:,} → max ${max_amt:,})"
    )

    return outliers


def _correlation_signals() -> list[str]:
    product_country: dict[tuple[str, str], int] = {}
    weekday_rev = _aggregate_by("weekday")
    for order in _DEMO_ORDERS:
        key = (str(order["product"]), str(order["country"]))
        product_country[key] = product_country.get(key, 0) + int(order["amount"])

    strongest_pair = max(product_country, key=lambda item: product_country[item])
    strongest_weekday = max(weekday_rev, key=lambda day: weekday_rev[day])

    return [
        f"{strongest_pair[0]} sales are strongest in {strongest_pair[1]}, contributing ${product_country[strongest_pair]:,}",
        f"{strongest_weekday} is the strongest sales day, indicating demand clusters late in the week",
        "Higher-value orders tend to align with Laptop and Monitor deals rather than accessory purchases",
    ]


def _natural_language_insight_generator() -> list[str]:
    total = _total_revenue()
    avg = round(_average_order_value())
    product_rev = _aggregate_by("product")
    country_rev = _aggregate_by("country")
    month_rev = _aggregate_by("month")

    top_product = max(product_rev, key=lambda p: product_rev[p])
    top_country = max(country_rev, key=lambda c: country_rev[c])
    top_month = max(month_rev, key=lambda m: month_rev[m])

    return [
        f"Total revenue is ${total:,}",
        f"{top_product} is the top-selling product",
        f"{top_country} generates the highest sales",
        f"Average order value is ${avg:,}",
        f"{top_month} has the highest sales activity",
    ]


def _build_viis_insights() -> list[dict[str, Any]]:
    total_revenue = _total_revenue()
    avg_order = round(_average_order_value())
    monthly_revenue = _monthly_revenue()
    product_revenue = _aggregate_by("product")
    country_revenue = _aggregate_by("country")
    weekday_revenue = _aggregate_by("weekday")
    salesperson_revenue = _aggregate_by("salesperson")
    product_country_revenue = _product_country_revenue()

    feb_revenue = monthly_revenue.get("February", 0)
    march_revenue = monthly_revenue.get("March", 0)
    march_pct = abs(_pct_change(feb_revenue, march_revenue))
    strongest_pair = max(product_country_revenue, key=lambda item: product_country_revenue[item])
    strongest_weekday = max(weekday_revenue, key=lambda day: weekday_revenue[day])
    top_product = max(product_revenue, key=lambda item: product_revenue[item])
    top_country = max(country_revenue, key=lambda item: country_revenue[item])
    top_salesperson = max(salesperson_revenue, key=lambda item: salesperson_revenue[item])
    outlier_order = max(_DEMO_ORDERS, key=lambda order: order["amount"])
    outlier_ratio = round(outlier_order["amount"] / _average_order_value(), 1)

    insights = [
        {
            "id": "revenue-momentum",
            "rank": 1,
            "category": "Trend Detection Engine",
            "title": "Revenue momentum accelerated in March",
            "insight": f"Revenue increased {march_pct}% in March versus February.",
            "driver": f"Laptop and Monitor sales drove the step-up, led by {strongest_pair[1]} demand and larger enterprise-sized orders.",
            "impact": f"March contributed ${march_revenue:,}, or {round(march_revenue / total_revenue * 100)}% of total revenue.",
            "suggested_action": "Review the March demand spike and identify which campaigns or accounts can be replicated next month.",
            "confidence": 94,
            "source": "Northwind Retail Group (demo)",
        },
        {
            "id": "product-leader",
            "rank": 2,
            "category": "Top Performers Engine",
            "title": "Laptop is the primary growth engine",
            "insight": f"Laptop is the top-selling product and generates {round(product_revenue[top_product] / total_revenue * 100)}% of revenue.",
            "driver": f"Laptop demand is concentrated in {strongest_pair[1]} and supported by high-value orders rather than low-ticket accessory volume.",
            "impact": f"Laptop revenue totals ${product_revenue[top_product]:,}, making it the largest single product contribution in the dataset.",
            "suggested_action": "Protect laptop inventory and verify pricing, fulfillment, and promotion coverage in top-performing regions.",
            "confidence": 92,
            "source": "Northwind Retail Group (demo)",
        },
        {
            "id": "regional-concentration",
            "rank": 3,
            "category": "Correlation Engine",
            "title": "Revenue is concentrated in a few demand pockets",
            "insight": f"{top_country} is the highest-sales region and {strongest_pair[0]} is strongest in {strongest_pair[1]}.",
            "driver": f"The {strongest_pair[0]} x {strongest_pair[1]} combination contributes ${product_country_revenue[strongest_pair]:,}, while {strongest_weekday} produces the strongest sales day pattern.",
            "impact": f"Regional concentration increases risk if demand softens in {top_country} because it currently anchors ${country_revenue[top_country]:,} in revenue.",
            "suggested_action": f"Investigate whether {top_product} demand can be diversified outside {strongest_pair[1]} without diluting margin.",
            "confidence": 89,
            "source": "Northwind Retail Group (demo)",
        },
        {
            "id": "order-outlier",
            "rank": 4,
            "category": "Outlier Detection Engine",
            "title": "A single large order materially influences results",
            "insight": f"Order #{outlier_order['order_id']} is {outlier_ratio}x larger than the average order value.",
            "driver": f"That order is a {outlier_order['product']} purchase in {outlier_order['country']} worth ${outlier_order['amount']:,}.",
            "impact": f"This one transaction represents {round(outlier_order['amount'] / total_revenue * 100)}% of total revenue, so trend interpretation should account for deal concentration.",
            "suggested_action": "Validate whether this is repeatable enterprise demand, a one-off deal, or a data-quality edge case.",
            "confidence": 87,
            "source": "Northwind Retail Group (demo)",
        },
        {
            "id": "operating-focus",
            "rank": 5,
            "category": "Dataset Summary Engine",
            "title": "Commercial execution is efficient but concentrated",
            "insight": f"Average order value is ${avg_order:,}, and {top_salesperson} currently leads the team.",
            "driver": f"A small set of high-value transactions and concentrated product demand are driving above-average order values.",
            "impact": f"Current efficiency is strong, but dependence on a narrow revenue base can amplify volatility across only {len(_DEMO_ORDERS)} orders.",
            "suggested_action": "Scale the winning playbook to a broader customer base so growth does not depend on a handful of large deals.",
            "confidence": 84,
            "source": "Northwind Retail Group (demo)",
        },
    ]

    return sorted(insights, key=lambda item: (item["rank"], -item["confidence"]))


def _build_ask_why_payload(insight_id: str) -> dict[str, Any]:
    insights = {item["id"]: item for item in _build_viis_insights()}
    insight = insights.get(insight_id)
    if insight is None:
        raise HTTPException(status_code=404, detail="Insight not found")

    product_country_revenue = _product_country_revenue()
    strongest_pair = max(product_country_revenue, key=lambda item: product_country_revenue[item])
    weekday_revenue = _aggregate_by("weekday")
    strongest_weekday = max(weekday_revenue, key=lambda day: weekday_revenue[day])
    monthly_revenue = _monthly_revenue()

    why_map: dict[str, dict[str, Any]] = {
        "revenue-momentum": {
            "root_cause": f"March growth is primarily explained by Laptop and Monitor demand, especially in {strongest_pair[1]}, where larger deal sizes lifted revenue.",
            "dimensions": [
                {"dimension": "Product", "finding": "Laptop and Monitor contributed the majority of incremental March revenue."},
                {"dimension": "Region", "finding": f"{strongest_pair[1]} showed the strongest high-value demand cluster."},
                {"dimension": "Time", "finding": f"March revenue reached ${monthly_revenue['March']:,} after a lower February baseline of ${monthly_revenue['February']:,}."},
            ],
            "recommended_investigation": "Check which campaigns, pipeline events, or inventory availability drove March hardware demand.",
        },
        "product-leader": {
            "root_cause": f"Laptop leadership comes from a small number of large, high-margin orders rather than broad low-ticket volume.",
            "dimensions": [
                {"dimension": "Product", "finding": "Laptop revenue is concentrated in fewer but larger deals."},
                {"dimension": "Region", "finding": f"{strongest_pair[1]} is the strongest Laptop geography in the dataset."},
                {"dimension": "Customer", "finding": "High-spend accounts are responsible for the bulk of hardware growth."},
            ],
            "recommended_investigation": "Review account-level demand and confirm whether the top hardware buyers are repeatable or one-time wins.",
        },
        "regional-concentration": {
            "root_cause": f"Revenue clusters around the {strongest_pair[0]} x {strongest_pair[1]} combination and peaks on {strongest_weekday}, showing demand concentration instead of uniform performance.",
            "dimensions": [
                {"dimension": "Region", "finding": f"{strongest_pair[1]} has the strongest product-region revenue combination."},
                {"dimension": "Product", "finding": f"{strongest_pair[0]} is the leading product in that concentration pocket."},
                {"dimension": "Day of Week", "finding": f"{strongest_weekday} is the most productive sales day."},
            ],
            "recommended_investigation": "Test whether adjacent regions or alternate weekdays can absorb the same offer without eroding conversion.",
        },
        "order-outlier": {
            "root_cause": "One exceptional order materially lifts the average order value and can overstate underlying demand stability.",
            "dimensions": [
                {"dimension": "Order Size", "finding": "The top transaction is materially larger than the average order."},
                {"dimension": "Product", "finding": "The outlier is tied to a high-ticket hardware purchase."},
                {"dimension": "Risk", "finding": "Removing a single outlier would noticeably lower average order value and revenue concentration."},
            ],
            "recommended_investigation": "Validate the customer, margin profile, and repeatability of the large order before extrapolating trend signals.",
        },
        "operating-focus": {
            "root_cause": "Commercial efficiency is strong because a narrow set of products, deals, and sellers are outperforming the rest of the dataset.",
            "dimensions": [
                {"dimension": "Sales Team", "finding": "One seller currently leads booked revenue."},
                {"dimension": "Order Mix", "finding": "High-value orders are lifting average order value above what broad-based volume would suggest."},
                {"dimension": "Coverage", "finding": "Revenue is spread across only a small number of transactions and customers."},
            ],
            "recommended_investigation": "Document the top seller playbook and determine how much of it can be standardized across the team.",
        },
    }

    payload = why_map[insight_id]
    return {
        "status": "success",
        "insight_id": insight_id,
        "title": insight["title"],
        "root_cause": payload["root_cause"],
        "dimensions": payload["dimensions"],
        "recommended_investigation": payload["recommended_investigation"],
        "confidence": min(insight["confidence"] + 2, 98),
        "source": insight["source"],
    }


def _build_business_drivers() -> list[dict[str, Any]]:
    total_revenue = _total_revenue()
    product_revenue = _aggregate_by("product")
    country_revenue = _aggregate_by("country")
    salesperson_revenue = _aggregate_by("salesperson")

    drivers = [
        {
            "label": max(product_revenue, key=product_revenue.get),
            "type": "Product",
            "share": round(max(product_revenue.values()) / total_revenue * 100),
        },
        {
            "label": max(country_revenue, key=country_revenue.get),
            "type": "Region",
            "share": round(max(country_revenue.values()) / total_revenue * 100),
        },
        {
            "label": max(salesperson_revenue, key=salesperson_revenue.get),
            "type": "Sales Owner",
            "share": round(max(salesperson_revenue.values()) / total_revenue * 100),
        },
    ]
    return drivers


def _build_anomaly_summary() -> list[dict[str, Any]]:
    avg_order_value = _average_order_value()
    largest_order = max(_DEMO_ORDERS, key=lambda order: order["amount"])
    canada_orders = [order for order in _DEMO_ORDERS if order["country"] == "Canada"]
    canada_average = round(sum(order["amount"] for order in canada_orders) / len(canada_orders))

    return [
        {
            "title": "Large order anomaly",
            "detail": f"Order #{largest_order['order_id']} is {round(largest_order['amount'] / avg_order_value, 1)}x larger than the average order value.",
            "severity": "medium",
        },
        {
            "title": "Regional variance",
            "detail": f"Canada orders average ${canada_average:,}, materially above accessory-only transactions and worth monitoring for demand mix shifts.",
            "severity": "low",
        },
    ]


def _build_engine_overview() -> dict[str, Any]:
    top_insight = _build_viis_insights()[0]
    return {
        "what_happened": top_insight["insight"],
        "why_it_happened": top_insight["driver"],
        "should_the_business_care": top_insight["impact"],
        "monitoring_mode": "continuous",
    }


def _build_daily_report() -> dict[str, Any]:
    top_insight = _build_viis_insights()[0]
    return {
        "title": "Today's VoxCore Insight",
        "report_date": str(date.today()),
        "headline": top_insight["insight"],
        "driver": top_insight["driver"],
        "confidence": top_insight["confidence"],
        "source": top_insight["source"],
    }


def _build_executive_briefing() -> dict[str, Any]:
    top_insight = _build_viis_insights()[0]
    monthly_revenue = _monthly_revenue()
    briefing_lines = [
        top_insight["insight"],
        top_insight["driver"],
        f"Customer orders reached {len(_DEMO_ORDERS)} with March revenue at ${monthly_revenue.get('March', 0):,}.",
    ]
    return {
        "title": "VoxCore Executive Briefing",
        "report_date": str(date.today()),
        "summary_lines": briefing_lines,
        "priority": "high",
        "confidence": top_insight["confidence"],
        "source": top_insight["source"],
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _build_report() -> list[dict]:
    return [
        {
            "category": "Dataset Summary Engine",
            "icon": "summary",
            "insights": _dataset_summary(),
        },
        {
            "category": "Top Performers Engine",
            "icon": "performers",
            "insights": _top_performers(),
        },
        {
            "category": "Trend Detection Engine",
            "icon": "trend",
            "insights": _trend_detection(),
        },
        {
            "category": "Distribution Analysis Engine",
            "icon": "distribution",
            "insights": _distribution_analysis(),
        },
        {
            "category": "Outlier Detection Engine",
            "icon": "outlier",
            "insights": _outlier_detection(),
        },
        {
            "category": "Correlation Engine",
            "icon": "correlation",
            "insights": _correlation_signals(),
        },
        {
            "category": "Natural Language Insight Generator",
            "icon": "narrative",
            "insights": _natural_language_insight_generator(),
        },
    ]


# kept for internal smoke-testing
def _compute_insights() -> list[str]:
    flat: list[str] = []
    for section in _build_report():
        flat.extend(section["insights"])
    return flat


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.get("/api/v1/playground/insights")
def playground_insights():
    """
    Automatically analyse the Northwind demo dataset and return categorised
    business insights.  Auth-exempt — designed for unauthenticated visitors.
    """
    report = _build_report()
    total_insights = sum(len(s["insights"]) for s in report)
    return {
        "status": "success",
        "dataset": "Northwind Retail Group (demo)",
        "standard": "VIIS v1",
        "engine_overview": _build_engine_overview(),
        "total_insights": total_insights,
        "categories": report,
        "structured_insights": _build_viis_insights(),
        "business_drivers": _build_business_drivers(),
        "anomalies": _build_anomaly_summary(),
        "daily_report": _build_daily_report(),
        "executive_briefing": _build_executive_briefing(),
    }


@router.get("/api/v1/playground/insights/ask-why")
def playground_ask_why(insight_id: str = Query(..., description="VIIS insight identifier")):
    return _build_ask_why_payload(insight_id)
