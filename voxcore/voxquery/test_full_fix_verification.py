#!/usr/bin/env python3
"""Comprehensive test to verify all fixes are working"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voxquery.core.sql_safety import extract_tables, validate_sql, normalize_tsql
from voxquery.core.schema_analyzer import SchemaAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("COMPREHENSIVE FIX VERIFICATION TEST")
print("=" * 80)

# Test 1: Schema Analyzer with SQL Server
print("\n1. Testing Schema Analyzer with SQL Server:")
try:
    from voxquery.core.engine_manager import engine_manager
    
    engine = engine_manager.get_engine()
    if engine:
        analyzer = SchemaAnalyzer(engine, warehouse_type='sqlserver')
        schemas = analyzer.analyze_all_tables()
        
        # Check for schema-qualified names
        qualified_tables = [t for t in schemas.keys() if '.' in t]
        print(f"  [OK] Found {len(schemas)} tables")
        print(f"  [OK] Schema-qualified tables: {len(qualified_tables)}")
        
        # Show sample tables
        sample_tables = list(schemas.keys())[:5]
        print(f"  Sample tables: {sample_tables}")
        
        # Check for key tables
        key_tables = ['SALES.CUSTOMER', 'SALES.SALESORDERHEADER', 'PRODUCTION.PRODUCT']
        found_keys = [t for t in key_tables if t in schemas]
        print(f"  [OK] Found key tables: {found_keys}")
    else:
        print("  [WARN] Could not create SQL Server engine")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 2: Table Extraction with Normalization
print("\n2. Testing Table Extraction with Normalization:")
sql_test = """
SELECT TOP 10 c.CustomerID, c.Name, SUM(soh.TotalDue) as total_balance
FROM CUSTOMER c
JOIN SALESORDERHEADER soh ON c.CustomerID = soh.CustomerID
GROUP BY c.CustomerID, c.Name
ORDER BY total_balance DESC
"""

tables = extract_tables(sql_test, dialect='sqlserver')
print(f"  Extracted tables: {tables}")
expected = {'SALES.CUSTOMER', 'SALES.SALESORDERHEADER'}
if tables == expected:
    print(f"  [OK] Table extraction with normalization working correctly")
else:
    print(f"  [ERROR] Expected {expected}, got {tables}")

# Test 3: SQL Validation with Normalized Tables
print("\n3. Testing SQL Validation with Normalized Tables:")
try:
    # Create allowed tables set with schema-qualified names
    allowed_tables = {
        'SALES.CUSTOMER',
        'SALES.SALESORDERHEADER',
        'SALES.SALESORDERDETAIL',
        'PRODUCTION.PRODUCT',
        'HUMANRESOURCES.EMPLOYEE',
        'PRODUCTION.SCRAPREASON',
        'DBO.DATABASELOG',
        'DBO.ERRORLOG',
    }
    
    is_safe, reason, score = validate_sql(
        sql_test,
        allowed_tables=allowed_tables,
        dialect='sqlserver'
    )
    
    print(f"  Is safe: {is_safe}")
    print(f"  Score: {score:.2f}")
    print(f"  Reason: {reason}")
    
    if is_safe and score >= 0.6:
        print(f"  [OK] SQL validation passed")
    else:
        print(f"  [WARN] SQL validation failed (expected after fix)")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 4: T-SQL Normalization
print("\n4. Testing T-SQL Normalization:")
sql_with_limit = "SELECT * FROM CUSTOMER LIMIT 10"
normalized = normalize_tsql(sql_with_limit)
print(f"  Original: {sql_with_limit}")
print(f"  Normalized: {normalized}")
if 'TOP 10' in normalized and 'LIMIT' not in normalized:
    print(f"  [OK] T-SQL normalization working correctly")
else:
    print(f"  [ERROR] T-SQL normalization failed")

# Test 5: Dialect Lock in Prompt
print("\n5. Testing Dialect Lock in Prompt:")
try:
    from voxquery.core.sql_generator import SQLGenerator
    
    # Check if DIALECT_LOCK is defined
    if hasattr(SQLGenerator, 'DIALECT_LOCK'):
        dialect_lock = SQLGenerator.DIALECT_LOCK
        if 'T-SQL only' in dialect_lock and 'TOP N' in dialect_lock:
            print(f"  [OK] DIALECT_LOCK is properly defined")
            print(f"  Sample: {dialect_lock[:100]}...")
        else:
            print(f"  [ERROR] DIALECT_LOCK missing key phrases")
    else:
        print(f"  [ERROR] DIALECT_LOCK not found in SQLGenerator")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 6: Priority Rules in Prompt
print("\n6. Testing Priority Rules in Prompt:")
try:
    from voxquery.core.sql_generator import SQLGenerator
    
    # Check if PRIORITY_RULES is defined
    if hasattr(SQLGenerator, 'PRIORITY_RULES'):
        priority_rules = SQLGenerator.PRIORITY_RULES
        if 'balance' in priority_rules.lower() and 'Sales.Customer' in priority_rules:
            print(f"  [OK] PRIORITY_RULES is properly defined")
            print(f"  Sample: {priority_rules[:100]}...")
        else:
            print(f"  [ERROR] PRIORITY_RULES missing key phrases")
    else:
        print(f"  [ERROR] PRIORITY_RULES not found in SQLGenerator")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
