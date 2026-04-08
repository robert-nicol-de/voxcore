import uuid

class BrainAgent:
    def run(self, user_query: str) -> dict:
        """
        Convert natural language into structured analytical intent
        """
        query = user_query.lower()

        # --- Intent classification ---
        if "trend" in query or "growth" in query:
            intent_type = "trend_analysis"
        elif "compare" in query:
            intent_type = "comparison"
        elif "top" in query or "best" in query:
            intent_type = "ranking"
        else:
            intent_type = "aggregation"

        # --- Entity extraction ---
        metrics = []
        dimensions = []
        filters = []

        if "revenue" in query:
            metrics.append("revenue")

        if "sales" in query:
            metrics.append("sales")

        if "region" in query:
            dimensions.append("region")

        if "product" in query:
            dimensions.append("product")

        # --- Time understanding ---
        time_range = {"type": None, "value": None}

        if "last 30 days" in query:
            time_range = {"type": "relative", "value": "30_days"}

        if "ytd" in query:
            time_range = {"type": "relative", "value": "ytd"}

        # --- Ambiguity detection ---
        is_ambiguous = False
        clarification = None

        if not metrics:
            is_ambiguous = True
            clarification = "What metric do you want to analyze?"

        # --- Build output ---
        output = {
            "intent_id": str(uuid.uuid4()),
            "user_query": user_query,
            "intent_type": intent_type,
            "confidence": 0.85,
            "entities": {
                "metrics": metrics,
                "dimensions": dimensions,
                "filters": filters,
                "time_range": time_range,
                "comparison": None
            },
            "ambiguity": {
                "is_ambiguous": is_ambiguous,
                "clarification_needed": clarification
            }
        }
        print("STEP 2: Context built:", output)
        return output
