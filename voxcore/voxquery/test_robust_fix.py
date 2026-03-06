#!/usr/bin/env python3
"""
Test the 3 immediate robust fixes
"""

import requests
import json
import time

API_URL = "http://localhost:8000/api/v1/query"

# Test questions
TEST_QUESTIONS = [
    "What is our total balance?",
    "Top 10 accounts by balance",
    "Which accounts have negative balance AND have had transactions in the last 30 days?",
    "Monthly transaction count",
]

def test_robust_fix():
    """Test the 3 robust fixes"""
    
    print("\n" + "="*80)
    print("TESTING 3 IMMEDIATE ROBUST FIXES")
    print("="*80)
    print("Fix 1: Strengthen prompt to ban dangerous constructs")
    print("Fix 2: Add column-count check in validation")
    print("Fix 3: Force simplest possible fallback")
    print("="*80 + "\n")
    
    results = []
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print("TEST {}/4: {}".format(i, question))
        
        try:
            response = requests.post(
                API_URL,
                json={"question": question},
                timeout=30
            )
            
            if response.status_code != 200:
                print("  API Error: {}".format(response.status_code))
                results.append({
                    "question": question,
                    "status": "ERROR",
                    "sql": None,
                })
                continue
            
            data = response.json()
            sql = data.get("sql", "")
            
            # Check for dangerous constructs
            has_cte = "WITH" in sql.upper()
            has_union = "UNION" in sql.upper()
            has_multiple_select = sql.upper().count("SELECT") > 1
            has_subquery = "FROM (" in sql.upper() or "WHERE (" in sql.upper()
            
            is_safe = not (has_cte or has_union or has_multiple_select or has_subquery)
            
            print("  SQL: {}".format(sql[:80]))
            print("  Safe: {}".format("YES" if is_safe else "NO"))
            
            if has_cte:
                print("    - Contains CTE (WITH)")
            if has_union:
                print("    - Contains UNION")
            if has_multiple_select:
                print("    - Multiple SELECT statements")
            if has_subquery:
                print("    - Contains subquery")
            
            results.append({
                "question": question,
                "status": "PASS" if is_safe else "FAIL",
                "sql": sql,
                "has_cte": has_cte,
                "has_union": has_union,
                "has_multiple_select": has_multiple_select,
                "has_subquery": has_subquery,
            })
            
        except Exception as e:
            print("  Error: {}".format(str(e)))
            results.append({
                "question": question,
                "status": "ERROR",
                "sql": None,
            })
        
        print()
        time.sleep(1)
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    
    print("Total: {}".format(total))
    print("Passed: {}".format(passed))
    print("Failed: {}".format(failed))
    print("Errors: {}".format(errors))
    print()
    
    for i, result in enumerate(results, 1):
        status = result["status"]
        print("{}: {} - {}".format(i, status, result["question"]))
        if result["sql"]:
            print("   SQL: {}".format(result["sql"][:80]))
    
    print()
    print("="*80)
    print("RESULT: {} / {} PASSED".format(passed, total))
    print("="*80 + "\n")
    
    return passed == total

if __name__ == "__main__":
    import sys
    success = test_robust_fix()
    sys.exit(0 if success else 1)
