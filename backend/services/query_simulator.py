import psycopg2
import os

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME", "voxcore")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")

RISK_KEYWORDS = ["Seq Scan", "Hash Join", "Nested Loop", "cost="]


def simulate_query(sql: str) -> dict:
    """
    Run EXPLAIN ANALYZE on the SQL and return impact analysis.
    Does NOT execute the query — safe for destructive statements too.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cur = conn.cursor()

        # Wrap in a transaction we always roll back so nothing mutates
        cur.execute("BEGIN")
        try:
            cur.execute(f"EXPLAIN ANALYZE {sql}")
            plan_rows = cur.fetchall()
        finally:
            cur.execute("ROLLBACK")

        plan_text = "\n".join(row[0] for row in plan_rows)

        warnings = []
        if "Seq Scan" in plan_text:
            warnings.append("Full table scan detected — consider adding an index")
        if "Nested Loop" in plan_text:
            warnings.append("Nested loop join detected — may be slow on large tables")
        if "Hash Join" in plan_text:
            warnings.append("Hash join detected — ensure adequate work_mem")

        # Extract estimated cost from the plan header line
        cost_estimate = None
        for line in plan_text.splitlines():
            if "cost=" in line:
                try:
                    cost_part = line.split("cost=")[1].split(" ")[0]
                    cost_estimate = cost_part  # e.g. "0.00..431.00"
                except Exception:
                    pass
                break

        cur.close()
        conn.close()

        return {
            "safe_to_run": len(warnings) == 0,
            "warnings": warnings,
            "cost_estimate": cost_estimate,
            "plan": plan_text,
        }

    except Exception as exc:
        return {
            "safe_to_run": None,
            "warnings": [],
            "cost_estimate": None,
            "plan": None,
            "error": str(exc),
        }
