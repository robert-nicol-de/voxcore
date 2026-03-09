import os
import json
from groq import Groq


# Initialize Groq client only if API key is available
groq_api_key = os.environ.get("GROQ_API_KEY")
client = None
if groq_api_key:
    try:
        client = Groq(api_key=groq_api_key)
        print("[✓] Groq AI client initialized successfully")
    except Exception as e:
        print(f"[⚠] Failed to initialize Groq client: {e}")
        client = None
else:
    print("[⚠] GROQ_API_KEY not set - AI risk classification disabled")


def ai_risk_classification(query: str):
    # If Groq client is not available, return safe defaults
    if not client:
        return {
            "risk_score": 50,
            "status": "WARNING",
            "reason": "AI analysis unavailable - using fallback heuristics"
        }

    prompt = f"""
You are a SQL security engine.

Analyze this SQL query and return JSON with:
risk_score (0-100)
status (SAFE, WARNING, BLOCKED)
reason

SQL Query:
{query}
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except Exception:
            return {
                "risk_score": 50,
                "status": "WARNING",
                "reason": "AI parsing failed"
            }
    except Exception as e:
        print(f"[⚠] AI risk classification error: {e}")
        return {
            "risk_score": 50,
            "status": "WARNING",
            "reason": f"AI error: {str(e)}"
        }


def calculate_risk(query: str):

    query_lower = query.lower()

    if "drop table" in query_lower:
        return {
            "risk_score": 95,
            "status": "BLOCKED",
            "reason": "Destructive SQL operation detected"
        }

    if "delete from" in query_lower:
        return {
            "risk_score": 85,
            "status": "WARNING",
            "reason": "Delete operation detected"
        }

    return ai_risk_classification(query)