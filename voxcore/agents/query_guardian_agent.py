import uuid

class QueryGuardianAgent:
    def run(self, sql: str, metadata: dict) -> dict:
        risk_score = 0
        flags = []
        recommendations = []
        final_sql = sql

        sql_upper = sql.upper()

        # --- P0: DESTRUCTIVE (BLOCK) ---
        destructive = ["DROP", "DELETE", "TRUNCATE", "ALTER"]

        for keyword in destructive:
            if keyword in sql_upper:
                return {
                    "query_id": str(uuid.uuid4()),
                    "status": "blocked",
                    "risk_score": 100,
                    "risk_flags": ["DESTRUCTIVE_OPERATION"],
                    "recommendations": ["Remove destructive SQL operations"],
                    "final_sql": None
                }

        # --- P1: SELECT * ---
        # Only flag SELECT * if not in a CTE layer (e.g., not in 'final_select')
        if "SELECT *" in sql_upper and "final_select" not in sql:
            risk_score += 30
            flags.append("SELECT_ALL")
            # Auto-fix (basic)
            final_sql = final_sql.replace("SELECT *", "SELECT /* explicit columns required */")
            recommendations.append("Explicit column selection enforced")

        # --- P1: MISSING LIMIT ---
        if "LIMIT" not in sql_upper:
            risk_score += 10
            flags.append("MISSING_LIMIT")
            recommendations.append("Add LIMIT to control output size")

        # --- P1: LARGE TIME RANGE ---
        if "INTERVAL '1 YEAR'" in sql_upper or "INTERVAL '12 MONTH'" in sql_upper:
            risk_score += 25
            flags.append("LARGE_TIME_RANGE")

        # --- P1: FULL SCAN ---
        if "WHERE" not in sql_upper:
            risk_score += 30
            flags.append("FULL_TABLE_SCAN")

        # --- P1: WINDOW FUNCTION SAFETY ---
        if "LAG(" in sql_upper or "LEAD(" in sql_upper:
            if "ORDER BY" not in sql_upper:
                risk_score += 20
                flags.append("WINDOW_NO_ORDER")
                recommendations.append("Ensure ORDER BY in window function")

        # --- P2: TRUSTED PATTERN ---
        pattern = metadata.get("pattern")
        if pattern in ["rolling_growth", "simple"]:
            risk_score -= 10
            flags.append("TRUSTED_PATTERN")

        # --- FINAL DECISION ---
        if risk_score >= 80:
            status = "blocked"
        elif risk_score >= 40:
            status = "warning"
        else:
            status = "approved"

        print("STEP 5: Inspector issues:", flags)
        print("STEP 6: Risk score:", risk_score)
        print("STEP 7: Policy decision:", status)
        return {
            "query_id": str(uuid.uuid4()),
            "status": status,
            "risk_score": max(risk_score, 0),
            "risk_flags": flags,
            "recommendations": recommendations,
            "final_sql": final_sql
        }
