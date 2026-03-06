#!/usr/bin/env python
"""Test API query endpoint"""

import sys
import io
import json
import requests

# Force UTF-8 encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("\n" + "="*80)
print("API QUERY TEST")
print("="*80 + "\n")

# Test 1: Connect to Snowflake
print("TEST 1: Connecting to Snowflake...")
connect_payload = {
    "database": "snowflake",
    "credentials": {
        "host": "ko05278.af-south-1.aws",
        "username": "QUERY",
        "password": "Robert210680!@#$",
        "database": "FINANCIAL_TEST",
    }
}

try:
    response = requests.post("http://localhost:8000/api/v1/auth/connect", json=connect_payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Get schema
print("\nTEST 2: Getting schema...")
try:
    response = requests.get("http://localhost:8000/api/v1/debug-schema")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Tables found: {data.get('tables_found', 0)}")
    print(f"Tables: {data.get('tables', [])}")
    print(f"Schema context length: {data.get('schema_length', 0)}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Generate SQL
print("\nTEST 3: Generating SQL for a question...")
query_payload = {
    "question": "Show me the top 10 accounts by total holdings value",
    "execute": False,
}

try:
    response = requests.post("http://localhost:8000/api/v1/query", json=query_payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"SQL: {data.get('sql')}")
    print(f"Confidence: {data.get('confidence')}")
    print(f"Explanation: {data.get('explanation')}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Execute query
print("\nTEST 4: Executing query...")
query_payload = {
    "question": "Show me the top 10 accounts by total holdings value",
    "execute": True,
}

try:
    response = requests.post("http://localhost:8000/api/v1/query", json=query_payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"SQL: {data.get('sql')}")
    print(f"Rows returned: {data.get('row_count', 0)}")
    if data.get('data'):
        print(f"First row: {data['data'][0]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
