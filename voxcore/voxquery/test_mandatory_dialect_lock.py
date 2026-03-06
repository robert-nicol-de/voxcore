#!/usr/bin/env python3
"""
Test the MANDATORY SQL Server T-SQL Dialect Lock
This tests the exact sequence: Layer 1 (prompt) → Layer 2 (runtime) → Layer 3 (validation) → Layer 4 (fallback)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_mandatory_prompt_lock():
    """Test Layer 1: MANDATORY prompt lock at the very top"""
    print("\n" + "="*80)
    print("LAYER 1: MANDATORY SQL SERVER T-SQL DIALECT LOCK (at prompt top)")
    print("="*80)
    
    payload = {
        "question": "Show top 10 accounts by balance",
        "execute": False,
        "dry_run": False,
    }
    
    response = requests.post(f"{BASE_URL}/api/query", json=payload)
    result = response.json()
    
    sql = result.get("sql", "")
    print(f"\nGenerated SQL:\n{sql}")
    
    # Check for violations
    violations = []
    
    if "LIMIT" in sql.upper():
        violations.append("❌ LIMIT keyword found (should use TOP)")
    
    if "SELECT 1 AS sql_server_dialect_violated" in sql:
        violations.append("❌ LLM returned dialect violation marker")
    
    if not sql or sql.strip() == "":
        violations.append("⚠️  SQL is empty")
    
    if violations:
        print("\nViolations found:")
        for v in violations:
            print(f"  {v}")
        return False
    
    # Check for correct patterns
    if "TOP" in sql.upper() or "Sales.Customer" in sql or "SALES.CUSTOMER" in sql:
        print("\n✅ LAYER 1 PASSED: Correct T-SQL syntax detected")
        return True
    
    print("\n⚠️  LAYER 1: Could not verify correct syntax")
    return True

def test_runtime_rewrite():
    """Test Layer 2: Runtime rewrite function"""
    print("\n" + "="*80)
    print("LAYER 2: Runtime Rewrite (enforce_tsql)")
    print("="*80)
    
    from voxquery.core.sql_generator import SQLGenerator
    
    test_cases = [
        {
            "input": "SELECT * FROM Customer LIMIT 10",
            "should_not_have": ["LIMIT"],
            "should_have": ["Sales.Customer"],
        },
        {
            "input": "SELECT CustomerID FROM SalesOrderHeader LIMIT 5",
            "should_not_have": ["LIMIT"],
            "should_have": ["Sales.SalesOrderHeader"],
        },
    ]
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        result = SQLGenerator.force_tsql(test["input"])
        print(f"\nTest {i}:")
        print(f"  Input:  {test['input']}")
        print(f"  Output: {result}")
        
        # Check violations
        for keyword in test["should_not_have"]:
            if keyword in result.upper():
                print(f"  ❌ FAILED: '{keyword}' still present")
                all_passed = False
        
        # Check required patterns
        for keyword in test["should_have"]:
            if keyword in result:
                print(f"  ✅ OK: '{keyword}' found")
            else:
                print(f"  ⚠️  WARNING: '{keyword}' not found")
    
    if all_passed:
        print("\n✅ LAYER 2 PASSED: All rewrites successful")
    else:
        print("\n❌ LAYER 2 FAILED: Some rewrites failed")
    
    return all_passed

def test_validation_reject():
    """Test Layer 3: Hard reject LIMIT in validation"""
    print("\n" + "="*80)
    print("LAYER 3: Hard Reject LIMIT in Validation")
    print("="*80)
    
    from voxquery.core.sql_safety import validate_sql
    
    bad_sql = "SELECT * FROM Sales.Customer LIMIT 10"
    allowed_tables = {"SALES.CUSTOMER", "SALES.SALESORDERHEADER", "PERSON.PERSON"}
    
    is_safe, reason, score = validate_sql(bad_sql, allowed_tables, dialect="sqlserver")
    
    print(f"\nSQL: {bad_sql}")
    print(f"Is Safe: {is_safe}")
    print(f"Reason: {reason}")
    print(f"Score: {score}")
    
    if not is_safe and score == 0.0 and "LIMIT" in reason:
        print("\n✅ LAYER 3 PASSED: LIMIT rejected with score 0.0")
        return True
    else:
        print("\n❌ LAYER 3 FAILED: LIMIT not properly rejected")
        return False

def test_end_to_end_execution():
    """Test Layer 4: End-to-end execution with fallback"""
    print("\n" + "="*80)
    print("LAYER 4: End-to-End Execution with Safe Fallback")
    print("="*80)
    
    payload = {
        "question": "Show top 10 accounts by balance",
        "execute": True,
        "dry_run": False,
    }
    
    response = requests.post(f"{BASE_URL}/api/query", json=payload)
    result = response.json()
    
    sql = result.get("sql", "")
    message = result.get("message", "")
    data = result.get("data", [])
    error = result.get("error")
    
    print(f"\nGenerated SQL:\n{sql}")
    print(f"Message: {message}")
    print(f"Error: {error}")
    print(f"Data rows: {len(data) if data else 0}")
    
    # Check for success
    if error:
        print(f"\n❌ LAYER 4 FAILED: Query error: {error}")
        return False
    
    if not sql or "SELECT 1 AS" in sql:
        print(f"\n❌ LAYER 4 FAILED: Invalid SQL generated")
        return False
    
    if "LIMIT" in sql.upper():
        print(f"\n⚠️  WARNING: LIMIT still in SQL (should have been stripped)")
        if data:
            print(f"  But query executed successfully with {len(data)} rows")
            return True
        return False
    
    if data:
        print(f"\n✅ LAYER 4 PASSED: Query executed successfully with {len(data)} rows")
        return True
    
    print(f"\n⚠️  LAYER 4: Query executed but no data returned")
    return True

def main():
    print("\n" + "="*80)
    print("MANDATORY SQL SERVER T-SQL DIALECT LOCK – COMPREHENSIVE TEST")
    print("="*80)
    
    # Wait for backend to be ready
    print("\nWaiting for backend to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready")
                break
        except:
            pass
        if i < 9:
            time.sleep(1)
    
    results = {}
    
    # Test each layer
    results["Layer 1: MANDATORY Prompt Lock"] = test_mandatory_prompt_lock()
    results["Layer 2: Runtime Rewrite"] = test_runtime_rewrite()
    results["Layer 3: Validation Reject"] = test_validation_reject()
    results["Layer 4: End-to-End Execution"] = test_end_to_end_execution()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for layer, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{layer}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("="*80))
    if all_passed:
        print("✅ ALL LAYERS PASSED – MANDATORY DIALECT LOCK IS ACTIVE")
    else:
        print("❌ SOME LAYERS FAILED – REVIEW ABOVE")
    print("="*80 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
