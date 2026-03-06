#!/usr/bin/env python
"""Test simple query"""

import sys
import io
import requests

# Force UTF-8 encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("\n" + "="*80)
print("SIMPLE QUERY TEST")
print("="*80 + "\n")

# Connect first
print("Connecting to Snowflake...")
connect_payload = {
    "database": "snowflake",
    "credentials": {
        "host": "ko05278.af-south-1.aws",
        "username": "QUERY",
        "password": "Robert210680!@#$",
        "database": "FINANCIAL_TEST",
    }
}

response = requests.post("http://localhost:8000/api/v1/auth/connect", json=connect_payload)
print(f"Connection status: {response.status_code}")

# Test different questions
questions = [
    "List all accounts",
    "Show me accounts",
    "What accounts are in the database?",
    "SELECT * FROM ACCOUNTS",
]

for question in questions:
    print(f"\nQuestion: {question}")
    query_payload = {
        "question": question,
        "execute": False,
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/query", json=query_payload)
        data = response.json()
        print(f"  SQL: {data.get('sql')}")
        print(f"  Confidence: {data.get('confidence')}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "="*80)
