import os
from groq import Groq

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def refine_query_with_ai(question: str) -> str:
    prompt = f"""
    You are a senior data analyst.

    Improve this query so it is:
    - clearer
    - more specific
    - analytically useful

    Query:
    {question}

    Return only the improved query.
    """

    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
