#!/usr/bin/env python3
"""Test VoxCore + VoxQuery integration"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_query(question, platform="sqlserver"):
    """Test a query through the API"""
    print(f"\n{'='*80}")
    print(f"Testing: {question}")
    print(f"Platform: {platform}")
    print(f"{'='*80}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "question": question,
                "platform": platform,
                "execute": False,  # Don't execute, just generate
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success")
            print(f"  Generated SQL: {result.get('sql', 'N/A')[:80]}...")
            print(f"  Status: {result.get('status', 'N/A')}")
            print(f"  Risk Score: {result.get('risk_score', 'N/A')}")
            print(f"  Error: {result.get('error', 'None')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"  {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_blocking():
    """Test that destructive operations are blocked"""
    print(f"\n{'='*80}")
    print("Testing: Destructive Operation Blocking")
    print(f"{'='*80}")
    
    dangerous_queries = [
        "DROP TABLE ACCOUNTS",
        "DELETE FROM CUSTOMERS",
        "TRUNCATE TABLE ORDERS",
        "ALTER TABLE PRODUCTS ADD COLUMN test INT",
    ]
    
    for query in dangerous_queries:
        print(f"\nTesting: {query}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/query",
                json={
                    "question": query,
                    "platform": "sqlserver",
                    "execute": False,
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'blocked':
                    print(f"  ✅ BLOCKED (as expected)")
                    print(f"     Error: {result.get('error', 'N/A')}")
                else:
                    print(f"  ⚠️  NOT BLOCKED (unexpected)")
                    print(f"     Status: {result.get('status')}")
            else:
                print(f"  ❌ Error: {response.status_code}")
        
        except Exception as e:
            print(f"  ❌ Exception: {e}")


def main():
    print("\n" + "="*80)
    print("VoxCore + VoxQuery Integration Test")
    print("="*80)
    
    # Wait for backend to be ready
    print("\nWaiting for backend to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready")
                break
        except:
            pass
        
        if i < 9:
            time.sleep(1)
    else:
        print("❌ Backend not responding")
        return
    
    # Test normal queries
    print("\n" + "="*80)
    print("PART 1: Normal Queries")
    print("="*80)
    
    test_query("Show me top 10 accounts by balance")
    test_query("What is the total revenue?")
    
    # Test blocking
    print("\n" + "="*80)
    print("PART 2: Destructive Operation Blocking")
    print("="*80)
    
    test_blocking()
    
    print("\n" + "="*80)
    print("Test Complete")
    print("="*80)


if __name__ == "__main__":
    main()
