import logging
from typing import Any, Dict

logger = logging.getLogger("voxcore.query_service")
logger.setLevel(logging.INFO)

class QueryService:
    def __init__(self):
        pass

    def execute(self, query_request, request_id=None) -> Dict[str, Any]:
        """
        Legacy query pipeline (pre-VoxCore). This method is deprecated and should not be used.
        """
        raise NotImplementedError("Legacy query pipeline is removed. Use VoxCore main_query_engine for all queries.")

    def _validate(self, query_request, request_id):
        if not hasattr(query_request, "query") or not query_request.query or not query_request.query.strip():
            logger.error(f"[request_id={request_id}] Validation failed: query is empty", extra={"request_id": request_id})
            raise ValueError("Query cannot be empty.")
        logger.info(f"[request_id={request_id}] Validation passed", extra={"request_id": request_id})

    # Legacy parse_intent method removed. Use VoxCore pipeline for all new logic.

    def build_plan(self, intent: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        logger.info(f"[request_id={request_id}] Building plan", extra={"request_id": request_id})
        return {
            "table": "sales",
            "metric": intent["metric"],
            "trend": intent["trend"],
            "time_col": "month",
            "value_col": "revenue"
        }

    def generate_sql(self, plan: Dict[str, Any], request_id: str) -> str:
        logger.info(f"[request_id={request_id}] Generating SQL", extra={"request_id": request_id})
        sql = (
            f"SELECT {plan['time_col']}, SUM({plan['value_col']}) as {plan['value_col']} "
            f"FROM {plan['table']} "
            f"GROUP BY {plan['time_col']} "
            f"ORDER BY {plan['time_col']} ASC"
        )
        logger.info(f"[request_id={request_id}] SQL generated: {sql}", extra={"request_id": request_id})
        return sql

    def run_query(self, sql: str, request_id: str):
        logger.info(f"[request_id={request_id}] Running query (mocked)", extra={"request_id": request_id})
        # Mocked data for growth/decline
        if "decline" in sql:
            data = [
                {"month": "Jan", "revenue": 1000},
                {"month": "Feb", "revenue": 900},
                {"month": "Mar", "revenue": 800},
            ]
        else:
            data = [
                {"month": "Jan", "revenue": 1000},
                {"month": "Feb", "revenue": 1200},
                {"month": "Mar", "revenue": 1400},
            ]
        logger.info(f"[request_id={request_id}] Query returned {len(data)} rows", extra={"request_id": request_id})
        return data

    def generate_insights(self, data, plan, request_id: str):
        logger.info(f"[request_id={request_id}] Generating insights", extra={"request_id": request_id})
        values = [row[plan["value_col"]] for row in data]

        # Trend detection
        start = values[0]
        end = values[-1]
        change = end - start
        pct_change = (change / start) if start != 0 else 0

        direction = "up" if change > 0 else "down" if change < 0 else "flat"
        strength = round(abs(pct_change), 2)

        # Simple anomaly detection
        avg = sum(values) / len(values)
        anomalies = []
        for i, v in enumerate(values):
            if abs(v - avg) / avg > 0.3:  # 30% deviation
                anomalies.append({
                    "index": i,
                    "value": v,
                    "type": "spike" if v > avg else "drop"
                })

        # Narrative
        if direction == "up":
            takeaway = f"Revenue increased by {round(pct_change*100,1)}% over the period"
        elif direction == "down":
            takeaway = f"Revenue decreased by {round(abs(pct_change)*100,1)}% over the period"
        else:
            takeaway = "Revenue remained stable over the period"

        result = {
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
        logger.info(f"[request_id={request_id}] Insights generated", extra={"request_id": request_id})
        return result
