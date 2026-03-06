#!/usr/bin/env python3
"""Test full flow with SQL Server"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_connect():
    """Test database connection"""
    print("\n" + "="*80)
    print("TEST 1: Connect to SQL Server")
    print("="*80)
    
    payload = {
        "warehouse": "sqlserver",
        "host": "localhost",
        "database": "AdventureWorks2022",
        "auth_type": "windows",
        "username": None,
        "password": None,
    }
    
    response = requests.post(f"{BASE_URL}/api/connect", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_schema():
    """Test schema loading"""
    print("\n" + "="*80)
    print("TEST 2: Get Schema")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/schema")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Tables found: {len(data.get('tables', []))}")
    if data.get('tables'):
        print(f"First 5 tables: {data['tables'][:5]}")
    
    return response.status_code == 200

def test_query():
    """Test query execution"""
    print("\n" + "="*80)
    print("TEST 3: Ask Question")
    print("="*80)
    
    payload = {
        "question": "Show me top 10 database users by log count",
        "execute": True,
        "dry_run": False,
    }
    
    response = requests.post(f"{BASE_URL}/api/query/ask", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    print(f"Question: {data.get('question')}")
    print(f"SQL: {data.get('sql')}")
    print(f"Confidence: {data.get('confidence')}")
    print(f"Error: {data.get('error')}")
    print(f"Data rows: {len(data.get('data', []))}")
    if data.get('data'):
        print(f"First row: {data['data'][0]}")
    
    return response.status_code == 200 and not data.get('error')

if __name__ == "__main__":
    try:
        print("\n🚀 FULL FLOW TEST - SQL SERVER")
        
        if test_connect():
            print("✅ Connection test passed")
        else:
            print("❌ Connection test failed")
            sys.exit(1)
        
        time.sleep(1)
        
        if test_schema():
            print("✅ Schema test passed")
        else:
            print("❌ Schema test failed")
            sys.exit(1)
        
        time.sleep(1)
        
        if test_query():
            print("✅ Query test passed")
        else:
            print("❌ Query test failed")
            sys.exit(1)
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
