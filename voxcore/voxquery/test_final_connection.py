#!/usr/bin/env python3
"""Test final connection with correct credentials"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("TESTING NEW SNOWFLAKE INSTANCE - FINAL")
print("="*80)

# Test connection
print("\nStep 1: Testing Snowflake Connection")
print("-" * 80)

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

print(f"Connecting to:")
print(f"  Account: ko05278.af-south-1.aws")
print(f"  Username: QUERY")
print(f"  Database: FINANCIAL_TEST")
print(f"  Schema: PUBLIC")

response = requests.post(f"{BASE_URL}/api/v1/auth/connect", json=payload)
print(f"\nStatus: {response.status_code}")

if response.status_code == 200:
    print("✅ Connection successful!")
    
    # Test query execution
    print("\nStep 2: Testing Query Execution")
    print("-" * 80)
    
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
    else:
        print(f"\n⚠️  Query executed but returned no data")
else:
    print(f"❌ Connection failed!")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
