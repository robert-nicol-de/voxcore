from groq import Groq
import os

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_drilldown_query(insight: str):
    prompt = f"""
    You are a data analyst.

    Based on this insight:
    "{insight}"

    Generate a follow-up query that would help investigate it further.

    Rules:
    - Be specific
    - Focus on root cause
    - Keep it short

    Output:
    Only return the query text.
    """

    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
