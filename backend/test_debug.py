#!/usr/bin/env python
"""Quick test of the debug endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Testing Debug Endpoints")
print("=" * 60)

# Test 1: Check schema
print("\n1. Checking database schema...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/debug/schema")
    data = response.json()
    print("Response:")
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")

# Test 2: Test SQL generation for a simple query
print("\n2. Testing SQL generation for 'Show top 10 records'...")
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/debug/test-sql",
        json={"question": "Show top 10 records", "warehouse": "sqlserver"}
    )
    data = response.json()
    print("Response:")
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")

# Test 3: Check connection status
print("\n3. Checking connection status...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/connection-status")
    data = response.json()
    print("Response:")
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
