#!/usr/bin/env python3
"""Test the validation fix with proper debug output"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from voxquery.core.sql_safety import validate_sql, extract_tables

def test_validation_with_schema():
    """Test validation with proper schema cache"""
    print("\n" + "="*80)
    print("TEST: Validation with Schema Cache")
    print("="*80)
    
    # Simulate schema cache from database
    allowed_tables = {'ACCOUNTS', 'TRANSACTIONS', 'HOLDINGS', 'SECURITIES', 'SECURITY_PRICES'}
    allowed_columns = {
        'ACCOUNTS': {'ACCOUNT_ID', 'ACCOUNT_NAME', 'BALANCE', 'OPEN_DATE', 'STATUS'},
        'TRANSACTIONS': {'TRANSACTION_ID', 'ACCOUNT_ID', 'TRANSACTION_DATE', 'AMOUNT', 'TRANSACTION_TYPE'},
        'HOLDINGS': {'HOLDING_ID', 'ACCOUNT_ID', 'SECURITY_ID', 'QUANTITY'},
        'SECURITIES': {'SECURITY_ID', 'SECURITY_NAME', 'TICKER'},
        'SECURITY_PRICES': {'SECURITY_ID', 'PRICE_DATE', 'PRICE'},
    }
    
    test_queries = [
        ("Sales query", "SELECT SUM(AMOUNT) AS sales FROM TRANSACTIONS WHERE AMOUNT > 0"),
        ("Sales trends", "SELECT DATE_TRUNC('MONTH', TRANSACTION_DATE) AS month, SUM(AMOUNT) AS sales FROM TRANSACTIONS WHERE AMOUNT > 0 GROUP BY month ORDER BY month DESC"),
        ("YTD revenue", "SELECT SUM(AMOUNT) AS ytd_revenue FROM TRANSACTIONS WHERE EXTRACT(YEAR FROM TRANSACTION_DATE) = EXTRACT(YEAR FROM CURRENT_DATE()) AND AMOUNT > 0"),
        ("Join query", "SELECT A.ACCOUNT_ID, SUM(CASE WHEN T.AMOUNT > 0 THEN T.AMOUNT ELSE 0 END) AS revenue FROM ACCOUNTS A JOIN TRANSACTIONS T ON A.ACCOUNT_ID = T.ACCOUNT_ID GROUP BY A.ACCOUNT_ID ORDER BY revenue DESC LIMIT 10"),
    ]
    
    results = []
    for name, sql in test_queries:
        print(f"\n{name}:")
        print(f"SQL: {sql[:80]}...")
        
        # Extract tables
        extracted = extract_tables(sql, "snowflake")
        print(f"Extracted tables: {extracted}")
        
        # Validate
        is_safe, reason, confidence = validate_sql(sql, allowed_tables, allowed_columns, "snowflake")
        
        print(f"Validation result: is_safe={is_safe}, confidence={confidence:.2f}")
        if reason:
            print(f"Reason: {reason}")
        
        if is_safe:
            print("✅ PASSED")
            results.append((name, True))
        else:
            print("❌ FAILED")
            results.append((name, False))
    
    return results

def main():
    print("\n" + "="*80)
    print("VALIDATION FIX TEST")
    print("="*80)
    print("\nTesting validation with proper schema cache and debug output")
    
    results = test_validation_with_schema()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("="*80))
    if all_passed:
        print("✅ ALL VALIDATION TESTS PASSED!")
        print("\nExpected debug output when running via API:")
        print("[VALIDATION DEBUG] Allowed tables: {'ACCOUNTS', 'TRANSACTIONS', 'HOLDINGS', 'SECURITIES', 'SECURITY_PRICES'}")
        print("[VALIDATION DEBUG] Extracted: {'TRANSACTIONS'}")
        print("[VALIDATION DEBUG] Unknown: set()")
    else:
        print("❌ SOME VALIDATION TESTS FAILED")
    print("="*80)

if __name__ == "__main__":
    main()
