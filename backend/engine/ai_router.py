from groq import Groq
import os
import json

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def route_with_ai(question: str):
    prompt = f"""
    You are the VoxCore Master Architect.

    Your job:
    - Determine which system domains should handle this request
    - Return a JSON response

    Available domains:
    - Query Intelligence
    - Governance & Safety
    - Insight Engine
    - Frontend UI/UX
    - Security & Permissions

    Rules:
    - You can select MULTIPLE domains
    - Order them in execution order
    - Provide confidence (0–1)
    - Provide reasoning

    Question:
    {question}

    Output JSON format:
    {{
      "domains": [
        {{"name": "...", "confidence": 0.0}}
      ],
      "reason": "..."
    }}
    """

    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except:
        return {
            "domains": [{"name": "Query Intelligence", "confidence": 0.5}],
            "reason": "Fallback routing"
        }
