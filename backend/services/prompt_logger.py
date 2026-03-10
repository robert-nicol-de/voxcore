import psycopg2
import os

# Example: load DB connection info from env
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME", "voxcore")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")


def log_prompt(user, prompt, sql, risk):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO ai_prompts
            (user_id, company_id, prompt, generated_sql, risk_level, approved, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,NOW())
            """,
            (user.id, user.company_id, prompt, sql, risk, False)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[⚠] Failed to log prompt: {e}")
        return False
