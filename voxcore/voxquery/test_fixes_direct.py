#!/usr/bin/env python3
"""Direct test of the three immediate fixes without needing database connection"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from voxquery.core.sql_generator import SQLGenerator
from voxquery.core.schema_analyzer import SchemaAnalyzer
from sqlalchemy import create_engine

def test_table_extraction():
    """Test Fix 1: sqlglot-based table extraction"""
    print("\n" + "="*80)
    print("FIX 1: sqlglot-based table extraction with logging")
    print("="*80)
    
    from voxquery.core.sql_safety import extract_tables
    
    test_sqls = [
        "SELECT SUM(AMOUNT) AS sales FROM TRANSACTIONS WHERE AMOUNT > 0",
        "SELECT DATE_TRUNC('MONTH', TRANSACTION_DATE) AS month, SUM(AMOUNT) AS sales FROM TRANSACTIONS WHERE AMOUNT > 0 GROUP BY month ORDER BY month DESC",
        "SELECT * FROM ACCOUNTS JOIN TRANSACTIONS ON ACCOUNTS.ACCOUNT_ID = TRANSACTIONS.ACCOUNT_ID",
    ]
    
    print("\nTesting table extraction:")
    for sql in test_sqls:
        print(f"\nSQL: {sql[:80]}...")
        tables = extract_tables(sql, "snowflake")
        print(f"Extracted tables: {tables}")
        
        # Verify we got the right tables
        if "TRANSACTIONS" in tables or "ACCOUNTS" in tables:
            print("✅ Correct tables extracted")
        else:
            print("❌ Failed to extract tables")
            return False
    
    return True

def test_validation_disabled():
    """Test Fix 2: Restrictive validation checks disabled"""
    print("\n" + "="*80)
    print("FIX 2: Disabled restrictive validation checks")
    print("="*80)
    
    from voxquery.core.sql_generator import SQLGenerator
    
    # Create a generator with fallback schema
    gen = SQLGenerator(
        engine=None,  # No database needed
        dialect="snowflake"
    )
    
    # Test queries that should now pass
    test_queries = [
        "SELECT DATE_TRUNC('MONTH', TRANSACTION_DATE) AS month, SUM(AMOUNT) AS sales FROM TRANSACTIONS WHERE AMOUNT > 0 GROUP BY month ORDER BY month DESC",
        "SELECT SUM(AMOUNT) AS ytd_sales FROM TRANSACTIONS WHERE EXTRACT(YEAR FROM TRANSACTION_DATE) = EXTRACT(YEAR FROM CURRENT_DATE())",
    ]
    
    print("\nTesting validation (should allow GROUP BY, ORDER BY, etc.):")
    for sql in test_queries:
        print(f"\nSQL: {sql[:80]}...")
        is_valid, error = gen._validate_sql(sql, "snowflake")
        
        if is_valid:
            print(f"✅ Validation PASSED")
        else:
            print(f"❌ Validation FAILED: {error}")
            return False
    
    return True

def test_emergency_logging():
    """Test Fix 3: Emergency logging is in place"""
    print("\n" + "="*80)
    print("FIX 3: Emergency logging before validation")
    print("="*80)
    
    print("\nChecking that emergency logging code is present...")
    
    # Read the sql_generator.py file with proper encoding
    try:
        with open("backend/voxquery/core/sql_generator.py", "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except:
        with open("backend/voxquery/core/sql_generator.py", "r", errors="ignore") as f:
            content = f.read()
    
    # Check for the emergency logging markers
    if 'print("="*80)' in content and 'print("SQL ABOUT TO BE VALIDATED:")' in content:
        print("✅ Emergency logging code found in sql_generator.py")
        return True
    else:
        print("❌ Emergency logging code NOT found")
        return False

def main():
    print("\n" + "="*80)
    print("DIRECT TEST OF IMMEDIATE FIXES")
    print("="*80)
    print("\nFix 1: sqlglot-based table extraction with logging")
    print("Fix 2: Disabled restrictive validation checks")
    print("Fix 3: Emergency logging before validation")
    
    results = []
    
    try:
        results.append(("Fix 1: Table Extraction", test_table_extraction()))
    except Exception as e:
        print(f"❌ Fix 1 test failed with exception: {e}")
        results.append(("Fix 1: Table Extraction", False))
    
    try:
        results.append(("Fix 2: Validation Disabled", test_validation_disabled()))
    except Exception as e:
        print(f"❌ Fix 2 test failed with exception: {e}")
        results.append(("Fix 2: Validation Disabled", False))
    
    try:
        results.append(("Fix 3: Emergency Logging", test_emergency_logging()))
    except Exception as e:
        print(f"❌ Fix 3 test failed with exception: {e}")
        results.append(("Fix 3: Emergency Logging", False))
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("="*80))
    if all_passed:
        print("✅ ALL FIXES VERIFIED!")
        print("\nNext steps:")
        print("1. Connect to a Snowflake database via the UI")
        print("2. Ask 'Show me sales trends'")
        print("3. Check backend logs for:")
        print("   - [DEBUG] Parsed tables from SQL: {'TRANSACTIONS'}")
        print("   - SQL ABOUT TO BE VALIDATED:")
        print("   - Extracted tables BEFORE validation: {'TRANSACTIONS'}")
        print("4. Verify SQL executes without fallback")
    else:
        print("❌ SOME FIXES FAILED - Check logs above")
    print("="*80)

if __name__ == "__main__":
    main()
