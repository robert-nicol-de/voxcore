#!/usr/bin/env python3
"""Test the top 10 by balance fix"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_top_10_balance():
    """Test: Show me top 10 accounts by balance"""
    
    print("\n" + "="*80)
    print("TEST: Top 10 Accounts by Balance")
    print("="*80)
    
    payload = {
        "question": "Show me top 10 accounts by balance",
        "database": "snowflake"
    }
    
    print(f"\nQuestion: {payload['question']}")
    print(f"Database: {payload['database']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query/generate-sql",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            sql = result.get("sql", "")
            
            print(f"\n✓ Generated SQL:")
            print(f"  {sql}")
            
            # Validate the SQL
            checks = {
                "Uses ACCOUNTS table": "ACCOUNTS" in sql.upper(),
                "Uses BALANCE column": "BALANCE" in sql.upper(),
                "Uses ORDER BY DESC": "ORDER BY" in sql.upper() and "DESC" in sql.upper(),
                "Uses LIMIT 10": "LIMIT 10" in sql.upper(),
                "No hallucinated tables": not any(t in sql.upper() for t in ["AMBUILDVERSION", "DATABASELOG", "ERRORLOG"]),
            }
            
            print(f"\n✓ Validation Checks:")
            all_pass = True
            for check, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check}")
                if not passed:
                    all_pass = False
            
            if all_pass:
                print(f"\n✓✓✓ ALL CHECKS PASSED ✓✓✓")
            else:
                print(f"\n✗ SOME CHECKS FAILED")
            
            return all_pass
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(f"  {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("Waiting for backend to be ready...")
    time.sleep(2)
    
    success = test_top_10_balance()
    
    print("\n" + "="*80)
    if success:
        print("✓ TEST PASSED - LLM is generating correct SQL for top 10 by balance")
    else:
        print("✗ TEST FAILED - LLM is still hallucinating or using wrong columns")
    print("="*80 + "\n")
