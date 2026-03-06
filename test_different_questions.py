#!/usr/bin/env python3
"""Test that different questions return different data"""

import requests
import json

BASE_URL = "http://localhost:5000"

# First, connect to SQL Server
print("=" * 60)
print("STEP 1: Connecting to SQL Server")
print("=" * 60)

connect_response = requests.post(
    f"{BASE_URL}/api/v1/auth/connect",
    json={
        "database": "sqlserver",
        "credentials": {
            "host": "localhost",
            "database": "AdventureWorks2022",
            "auth_type": "windows"
        }
    }
)

print(f"Connect response: {connect_response.status_code}")
print(json.dumps(connect_response.json(), indent=2))

# Now test different questions
questions = [
    "Show top 10 customers",
    "Show top 10 products",
    "What are the best selling items?",
    "Monthly recurring revenue analysis"
]

print("\n" + "=" * 60)
print("STEP 2: Testing Different Questions")
print("=" * 60)

for i, question in enumerate(questions, 1):
    print(f"\n--- Question {i}: {question} ---")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/query",
        json={
            "question": question,
            "warehouse": "sqlserver",
            "session_id": "test-session"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get("success"):
        print(f"✓ Query succeeded")
        print(f"  Generated SQL: {data.get('generated_sql', '')[:100]}...")
        print(f"  Rows returned: {data.get('rows_returned', 0)}")
        if data.get('results'):
            print(f"  First result: {data['results'][0]}")
    else:
        print(f"✗ Query failed: {data.get('error')}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
