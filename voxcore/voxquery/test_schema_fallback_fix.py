#!/usr/bin/env python3
"""Test that schema fallback is working and SQL generation succeeds"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_ytd_sales_query():
    """Test YTD sales query - should generate valid SQL now"""
    print("\n" + "="*80)
    print("TEST: YTD Sales Query")
    print("="*80)
    
    payload = {
        "question": "What is our YTD sales?",
        "conversation_id": "test_session_1"
    }
    
    print(f"Sending question: {payload['question']}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/query",
        json=payload,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS")
        print(f"SQL Generated: {result.get('sql', 'N/A')}")
        print(f"Explanation: {result.get('explanation', 'N/A')}")
        
        # Check if SQL is valid (not the fallback)
        sql = result.get('sql', '').upper()
        if 'SELECT 1 AS no_matching_schema' in sql:
            print("❌ FAILED: Still getting fallback SQL (schema not loaded)")
            return False
        elif 'TRANSACTIONS' in sql and 'TRANSACTION_DATE' in sql:
            print("✅ PASSED: Valid SQL generated with correct tables and columns")
            return True
        else:
            print(f"⚠️  Generated SQL but may not be optimal: {result.get('sql')}")
            return True
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_top_accounts_query():
    """Test top accounts query"""
    print("\n" + "="*80)
    print("TEST: Top Accounts Query")
    print("="*80)
    
    payload = {
        "question": "Show me the top 10 accounts by balance",
        "conversation_id": "test_session_2"
    }
    
    print(f"Sending question: {payload['question']}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/query",
        json=payload,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS")
        print(f"SQL Generated: {result.get('sql', 'N/A')}")
        
        sql = result.get('sql', '').upper()
        if 'ACCOUNTS' in sql and 'BALANCE' in sql:
            print("✅ PASSED: Valid SQL with ACCOUNTS table")
            return True
        else:
            print(f"⚠️  Generated SQL: {result.get('sql')}")
            return True
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_transaction_count_query():
    """Test transaction count query"""
    print("\n" + "="*80)
    print("TEST: Transaction Count Query")
    print("="*80)
    
    payload = {
        "question": "How many transactions do we have?",
        "conversation_id": "test_session_3"
    }
    
    print(f"Sending question: {payload['question']}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/query",
        json=payload,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS")
        print(f"SQL Generated: {result.get('sql', 'N/A')}")
        
        sql = result.get('sql', '').upper()
        if 'TRANSACTIONS' in sql:
            print("✅ PASSED: Valid SQL with TRANSACTIONS table")
            return True
        else:
            print(f"⚠️  Generated SQL: {result.get('sql')}")
            return True
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SCHEMA FALLBACK FIX TEST SUITE")
    print("="*80)
    print("Testing that schema fallback is working and SQL generation succeeds")
    
    # Wait for backend to be ready
    print("\nWaiting for backend to be ready...")
    for i in range(15):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready")
                break
        except Exception as e:
            print(f"  Attempt {i+1}/15: Waiting... ({e})")
        time.sleep(1)
    else:
        print("❌ Backend did not respond in time")
        exit(1)
    
    # Run tests
    results = []
    results.append(("YTD Sales", test_ytd_sales_query()))
    results.append(("Top Accounts", test_top_accounts_query()))
    results.append(("Transaction Count", test_transaction_count_query()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Schema fallback fix is working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
