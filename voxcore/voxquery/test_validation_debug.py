#!/usr/bin/env python3
"""
Test script to validate the debug output from the validation layer.
This tests the complete flow: SQL generation -> validation -> debug output.
"""

import requests
import json
import sys

# Backend URL
BACKEND_URL = "http://localhost:8000"

def connect_to_database():
    """Connect to a test database"""
    print(f"\n{'='*80}")
    print(f"CONNECTING TO DATABASE")
    print(f"{'='*80}\n")
    
    # Try to load credentials from INI file
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/auth/load-ini-credentials/snowflake",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            credentials = data.get("credentials", {})
            print(f"[OK] Loaded credentials from INI file")
            print(f"  Host: {credentials.get('host')}")
            print(f"  Database: {credentials.get('database')}")
        else:
            print(f"[WARN] Could not load INI credentials: {response.text}")
            print(f"Using fallback credentials...")
            credentials = {
                "host": "localhost",
                "username": "test",
                "password": "test",
                "database": "voxquery",
            }
    except Exception as e:
        print(f"[WARN] Could not load INI credentials: {e}")
        print(f"Using fallback credentials...")
        credentials = {
            "host": "localhost",
            "username": "test",
            "password": "test",
            "database": "voxquery",
        }
    
    # Connect to database
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/connect",
            json={
                "database": "snowflake",
                "credentials": credentials
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"[OK] Connected to database")
            return True
        else:
            print(f"[FAIL] Connection failed: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        return False

def test_query(question: str):
    """Test a query and capture the response"""
    print(f"\n{'='*80}")
    print(f"TESTING QUESTION: {question}")
    print(f"{'='*80}\n")
    
    # Make request to backend
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/query",
            json={"question": question},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n[OK] SUCCESS")
            print(f"SQL: {data.get('sql', 'N/A')}")
            print(f"Confidence: {data.get('confidence', 'N/A')}")
            print(f"Query Type: {data.get('query_type', 'N/A')}")
            print(f"Tables Used: {data.get('tables_used', [])}")
            
            # Check for validation issues
            if data.get('confidence', 1.0) < 0.6:
                print(f"\n[WARN] LOW CONFIDENCE: {data.get('confidence', 'N/A')}")
            
            return True
        else:
            print(f"\n[FAIL] ERROR")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"\n[FAIL] EXCEPTION: {e}")
        return False

def main():
    """Run validation tests"""
    print("\n" + "="*80)
    print("VOXQUERY VALIDATION DEBUG TEST")
    print("="*80)
    
    # First, connect to database
    if not connect_to_database():
        print("\n[FAIL] Could not connect to database. Exiting.")
        return 1
    
    # Test queries
    test_queries = [
        "Show me sales trends",
        "What is our YTD revenue?",
        "Show top 10 customers by revenue",
        "Monthly transaction count",
    ]
    
    results = []
    for question in test_queries:
        success = test_query(question)
        results.append((question, success))
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for question, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status}: {question}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n[OK] ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
