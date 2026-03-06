#!/usr/bin/env python3
"""Test real query execution with schema analysis"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("TESTING REAL QUERY EXECUTION")
print("="*80)

# Step 1: Connect
print("\nStep 1: Connecting to Snowflake...")
payload = {
    "database": "snowflake",
    "credentials": {
        "host": "ko05278.af-south-1.aws",
        "username": "QUERY",
        "password": "Robert210680!@#$",
        "database": "FINANCIAL_TEST",
        "auth_type": "sql"
    }
}

response = requests.post(f"{BASE_URL}/api/v1/auth/connect", json=payload)
if response.status_code != 200:
    print(f"❌ Connection failed: {response.json()}")
    exit(1)

print("✅ Connected!")

# Step 2: Check schema
print("\nStep 2: Checking schema...")
response = requests.get(f"{BASE_URL}/api/v1/debug-schema")
result = response.json()
print(f"Tables found: {result.get('tables_found', 0)}")
print(f"Tables: {result.get('tables', [])[:5]}")  # Show first 5

# Step 3: Ask a question
print("\nStep 3: Asking a question...")
query_payload = {
    "question": "Show me the first 5 records",
    "execute": True
}

response = requests.post(f"{BASE_URL}/api/v1/query", json=query_payload)
result = response.json()

print(f"SQL: {result.get('sql')}")
print(f"Error: {result.get('error')}")
print(f"Rows: {result.get('row_count')}")
print(f"Time: {result.get('execution_time_ms'):.2f}ms")

if result.get('data'):
    print(f"\n✅ Query executed successfully!")
    print(f"First row: {result['data'][0]}")
    print(f"Columns: {list(result['data'][0].keys())}")
else:
    print(f"\n⚠️  Query executed but returned no data")
    if result.get('error'):
        print(f"Error: {result['error']}")
