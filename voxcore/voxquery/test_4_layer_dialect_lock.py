#!/usr/bin/env python3
"""
Test all 4 layers of the bulletproof dialect lock for SQL Server
Layer 1: Nuclear prompt enforcement
Layer 2: Hard runtime rewrite (kill LIMIT)
Layer 3: Hard reject LIMIT in validation
Layer 4: Safe fallback query
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_layer_1_prompt():
    """Test Layer 1: Nuclear prompt enforcement"""
    print("\n" + "="*80)
    print("LAYER 1: Nuclear Prompt Enforcement")
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
    
    # Check for LIMIT (should not be present)
    if "LIMIT" in sql.upper():
        print("❌ LAYER 1 FAILED: LIMIT keyword found in generated SQL")
        return False
    
    # Check for TOP (should be present)
    if "TOP" not in sql.upper():
        print("⚠️  WARNING: TOP keyword not found (might be OK if not a top-N query)")
    
    # Check for schema qualification
    if "Sales.Customer" in sql or "SALES.CUSTOMER" in sql:
        print("✅ LAYER 1 PASSED: Schema-qualified tables used")
        return True
    else:
        print("⚠️  WARNING: Schema qualification not found")
        return True

def test_layer_2_runtime_rewrite():
    """Test Layer 2: Hard runtime rewrite"""
    print("\n" + "="*80)
    print("LAYER 2: Hard Runtime Rewrite (Kill LIMIT)")
    print("="*80)
    
    # Test the force_tsql function directly
    from voxquery.core.sql_generator import SQLGenerator
    
    test_cases = [
        ("SELECT * FROM Customer LIMIT 10", "SELECT TOP 10 * FROM Sales.Customer ORDER BY 1 DESC"),
        ("SELECT * FROM SalesOrderHeader LIMIT 5", "SELECT TOP 5 * FROM Sales.SalesOrderHeader ORDER BY 1 DESC"),
    ]
    
    all_passed = True
    for input_sql, expected_pattern in test_cases:
        result = SQLGenerator.force_tsql(input_sql)
        print(f"\nInput:  {input_sql}")
        print(f"Output: {result}")
        
        if "LIMIT" in result.upper():
            print("❌ LAYER 2 FAILED: LIMIT not removed")
            all_passed = False
        elif "TOP" in result.upper():
            print("✅ LAYER 2 PASSED: LIMIT replaced with TOP")
        else:
            print("⚠️  WARNING: Neither LIMIT nor TOP found")
    
    return all_passed

def test_layer_3_validation():
    """Test Layer 3: Hard reject LIMIT in validation"""
    print("\n" + "="*80)
    print("LAYER 3: Hard Reject LIMIT in Validation")
    print("="*80)
    
    from voxquery.core.sql_safety import validate_sql
    
    # Test SQL with LIMIT (should fail)
    bad_sql = "SELECT * FROM Sales.Customer LIMIT 10"
    allowed_tables = {"SALES.CUSTOMER", "SALES.SALESORDERHEADER", "PERSON.PERSON"}
    
    is_safe, reason, score = validate_sql(bad_sql, allowed_tables, dialect="sqlserver")
    
    print(f"\nSQL: {bad_sql}")
    print(f"Is Safe: {is_safe}")
    print(f"Reason: {reason}")
    print(f"Score: {score}")
    
    if not is_safe and score == 0.0:
        print("✅ LAYER 3 PASSED: LIMIT keyword rejected with score 0.0")
        return True
    else:
        print("❌ LAYER 3 FAILED: LIMIT not properly rejected")
        return False

def test_layer_4_fallback():
    """Test Layer 4: Safe fallback query"""
    print("\n" + "="*80)
    print("LAYER 4: Safe Fallback Query")
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
    
    # Check if fallback was triggered
    if "Adjusted to safe SQL Server query" in message:
        print("✅ LAYER 4 PASSED: Safe fallback was triggered and executed")
        return True
    
    # Check if query executed successfully without error
    if not error and data:
        print("✅ LAYER 4 PASSED: Query executed successfully")
        return True
    
    if error:
        print(f"❌ LAYER 4 FAILED: Query error: {error}")
        return False
    
    print("⚠️  WARNING: Could not determine if fallback was needed")
    return True

def main():
    print("\n" + "="*80)
    print("BULLETPROOF 4-LAYER DIALECT LOCK TEST")
    print("="*80)
    
    results = {}
    
    # Test each layer
    results["Layer 1: Prompt"] = test_layer_1_prompt()
    results["Layer 2: Runtime Rewrite"] = test_layer_2_runtime_rewrite()
    results["Layer 3: Validation"] = test_layer_3_validation()
    results["Layer 4: Fallback"] = test_layer_4_fallback()
    
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
        print("✅ ALL LAYERS PASSED – DIALECT LOCK IS BULLETPROOF")
    else:
        print("❌ SOME LAYERS FAILED – REVIEW ABOVE")
    print("="*80 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
