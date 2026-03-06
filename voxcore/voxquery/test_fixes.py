#!/usr/bin/env python3
"""Test the three immediate fixes"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_sales_trends():
    """Test the sales trends query that was failing"""
    print("\n" + "="*80)
    print("TEST: Sales Trends Query")
    print("="*80)
    
    payload = {
        "question": "Show me sales trends",
        "dialect": "snowflake"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nGenerated SQL:")
            print(data.get("sql", "NO SQL"))
            print(f"\nConfidence: {data.get('confidence', 'N/A')}")
            print(f"Query Type: {data.get('query_type', 'N/A')}")
            
            # Check if it's the fallback
            if "no_matching_schema" in data.get("sql", "").lower():
                print("\n❌ FAILED: Got fallback SQL (no_matching_schema)")
                return False
            else:
                print("\n✅ SUCCESS: Got real SQL (not fallback)")
                return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_ytd_sales():
    """Test YTD sales query"""
    print("\n" + "="*80)
    print("TEST: YTD Sales Query")
    print("="*80)
    
    payload = {
        "question": "What is our YTD sales?",
        "dialect": "snowflake"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nGenerated SQL:")
            print(data.get("sql", "NO SQL"))
            print(f"\nConfidence: {data.get('confidence', 'N/A')}")
            
            # Check if it's the fallback
            if "no_matching_schema" in data.get("sql", "").lower():
                print("\n❌ FAILED: Got fallback SQL")
                return False
            else:
                print("\n✅ SUCCESS: Got real SQL")
                return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_monthly_transactions():
    """Test monthly transaction count"""
    print("\n" + "="*80)
    print("TEST: Monthly Transaction Count")
    print("="*80)
    
    payload = {
        "question": "Monthly transaction count",
        "dialect": "snowflake"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nGenerated SQL:")
            print(data.get("sql", "NO SQL"))
            print(f"\nConfidence: {data.get('confidence', 'N/A')}")
            
            # Check if it's the fallback
            if "no_matching_schema" in data.get("sql", "").lower():
                print("\n❌ FAILED: Got fallback SQL")
                return False
            else:
                print("\n✅ SUCCESS: Got real SQL")
                return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING IMMEDIATE FIXES")
    print("="*80)
    print("\nFix 1: sqlglot-based table extraction with logging")
    print("Fix 2: Disabled restrictive validation checks")
    print("Fix 3: Emergency logging before validation")
    
    # Wait for backend to be ready
    print("\nWaiting for backend to be ready...")
    time.sleep(2)
    
    results = []
    results.append(("Sales Trends", test_sales_trends()))
    results.append(("YTD Sales", test_ytd_sales()))
    results.append(("Monthly Transactions", test_monthly_transactions()))
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("="*80))
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED - Check logs above")
    print("="*80)
