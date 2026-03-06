#!/usr/bin/env python3
"""
Test script to verify Snowflake connection with USE statements
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test credentials
credentials = {
    "database": "snowflake",
    "credentials": {
        "host": "VOXQUERYTRAININGFIN2025",  # Account identifier
        "username": "VOXQUERY_USER",
        "password": "VoxQuery@2025",
        "database": "VOXQUERYTRAININGFIN2025",
        "schema": "PUBLIC",
        "warehouse": "COMPUTE_WH",
        "role": "ACCOUNTADMIN"
    }
}

print("\n" + "="*80)
print("TESTING SNOWFLAKE CONNECTION WITH USE STATEMENTS")
print("="*80 + "\n")

# Test 1: Test connection endpoint
print("1. Testing /auth/test-connection endpoint...")
try:
    response = requests.post(f"{BASE_URL}/auth/test-connection", json=credentials)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "-"*80 + "\n")

# Test 2: Connect endpoint
print("2. Testing /auth/connect endpoint...")
try:
    response = requests.post(f"{BASE_URL}/auth/connect", json=credentials)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "="*80 + "\n")
