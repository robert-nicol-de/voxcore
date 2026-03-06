#!/usr/bin/env python3
"""Quick test to verify backend is running and responding"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

def test_connection():
    """Test connection endpoint"""
    print("\n2. Testing connection endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/connection/test")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

def test_connect():
    """Test connect endpoint"""
    print("\n3. Testing connect endpoint...")
    try:
        payload = {
            "database": "sqlserver",
            "credentials": {
                "host": "localhost",
                "database": "AdventureWorks2022",
                "auth_type": "windows"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/connect",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

def test_query():
    """Test query endpoint"""
    print("\n4. Testing query endpoint...")
    try:
        payload = {
            "question": "How many products are in the database?",
            "warehouse": "sqlserver",
            "execute": True,
            "dry_run": False
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   SQL: {data.get('sql', 'N/A')[:100] if data.get('sql') else 'N/A'}...")
        print(f"   Data rows: {len(data.get('data') or [])}")
        print(f"   Error: {data.get('error', 'None')}")
        print(f"   Message: {data.get('message', 'None')}")
        print(f"   Charts: {list(data.get('charts', {}).keys()) if data.get('charts') else 'None'}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*80)
    print("BACKEND HEALTH CHECK")
    print("="*80)
    test_health()
    test_connection()
    test_connect()
    test_query()
    print("\n" + "="*80)
