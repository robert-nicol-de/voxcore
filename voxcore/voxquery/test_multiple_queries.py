#!/usr/bin/env python3
"""Test multiple queries to verify stability"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_query(question, execute=True):
    """Test a single query"""
    payload = {
        "question": question,
        "execute": execute
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/query", json=payload)
    result = response.json()
    
    print(f"\n{'='*80}")
    print(f"Question: {question}")
    print(f"SQL: {result.get('sql')}")
    print(f"Status: {'✅ SUCCESS' if not result.get('error') else '❌ ERROR'}")
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    else:
        print(f"Rows: {result.get('row_count')}")
        print(f"Time: {result.get('execution_time_ms'):.2f}ms")
        if result.get('data'):
            print(f"First row: {result['data'][0]}")
    
    return not result.get('error')


if __name__ == "__main__":
    print("Testing multiple queries with Snowflake raw connector...")
    
    # First, connect
    print("\nConnecting to Snowflake...")
    payload = {
        "database": "snowflake",
        "credentials": {
            "host": "we08391.af-south-1.aws",
            "username": "VOXQUERY",
            "password": "Robert210680!@#$",
            "database": "VOXQUERYTRAININGPIN2025",
            "auth_type": "sql"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/connect", json=payload)
    if response.status_code != 200:
        print(f"❌ Connection failed: {response.json()}")
        exit(1)
    
    print("✅ Connected!")
    
    # Test multiple queries
    queries = [
        "Show me the top 10 records",
        "How many records are in the FACT_REVENUE table?",
        "Show me records sorted by SALES_AMOUNT descending",
        "What are the unique STORE_ID values?",
    ]
    
    results = []
    for query in queries:
        success = test_query(query)
        results.append((query, success))
        time.sleep(0.5)  # Small delay between queries
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for query, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {query[:60]}")
