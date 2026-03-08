import os
import json
from groq import Groq


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def ai_risk_classification(query: str):

    prompt = f"""
You are a SQL security engine.

Analyze this SQL query and return JSON with:
risk_score (0-100)
status (SAFE, WARNING, BLOCKED)
reason

SQL Query:
{query}
"""

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