#!/usr/bin/env python3
"""Check available Groq models"""

import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from groq import Groq

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY not set")
    exit(1)

print(f"Using API key: {api_key[:20]}...")

client = Groq(api_key=api_key)

try:
    models = client.models.list()
    print("\nAvailable Groq models:")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"Error listing models: {e}")
    import traceback
    traceback.print_exc()
