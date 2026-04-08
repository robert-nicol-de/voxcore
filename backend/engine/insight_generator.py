from groq import Groq
import os

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_ranked_insights_with_ai(data, question: str):
    prompt = f"""
    You are a senior data analyst.

    Analyze the data and generate the TOP 3 most important insights.

    Question:
    {question}

    Data:
    {data}

    Rules:
    - Return 3 insights max
    - Rank by importance
    - Be specific (numbers, trends, comparisons)
    - Include a confidence score (0–1)

    Output JSON:
    [
      {{
        "insight": "...",
        "type": "trend|anomaly|comparison",
        "confidence": 0.0
      }}
    ]
    """

    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    import json

    try:
        return json.loads(response.choices[0].message.content)
    except:
        return [
            {
                "insight": "Basic insight fallback",
                "type": "trend",
                "confidence": 0.5
            }
        ]

def fallback_insight(data):
    return "Basic insight: Data processed successfully"
