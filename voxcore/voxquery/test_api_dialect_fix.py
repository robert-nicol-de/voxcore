#!/usr/bin/env python3
"""Test the dialect fix via API"""

import requests
import json

BASE_URL = "http://localhost:8000"

# First, connect to SQL Server
print("=" * 80)
print("STEP 1: Connect to SQL Server")
print("=" * 80)

connect_payload = {
    "platform": "sqlserver",
    "host": "localhost",
    "port": 1433,
    "database": "AdventureWorks2022",
    "username": "sa",
    "password": "YourPassword123!",
    "trusted_connection": False
}

response = requests.post(f"{BASE_URL}/api/connect", json=connect_payload)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()

# Now ask a question that should trigger LIMIT → TOP conversion
print("=" * 80)
print("STEP 2: Ask question that would generate LIMIT (should be rewritten to TOP)")
print("=" * 80)

query_payload = {
    "question": "Show me top 10 accounts by balance",
    "execute": False
}

response = requests.post(f"{BASE_URL}/api/query", json=query_payload)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Generated SQL: {result.get('sql', 'N/A')}")
print(f"Confidence: {result.get('confidence', 'N/A')}")
print(f"Error: {result.get('error', 'N/A')}")
print()

# Check if LIMIT is in the SQL
if "LIMIT" in (result.get('sql', '') or '').upper():
    print("❌ FAIL: LIMIT still present in generated SQL")
elif "TOP" in (result.get('sql', '') or '').upper():
    print("✅ PASS: LIMIT was rewritten to TOP")
else:
    print("⚠️  WARNING: Neither LIMIT nor TOP found in SQL")
