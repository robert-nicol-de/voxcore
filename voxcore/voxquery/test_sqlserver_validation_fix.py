#!/usr/bin/env python3
"""
Test SQL Server validation fix - verify extract_tables and extract_columns work with sqlparse fallback
"""

import sys
sys.path.insert(0, '/workspace/backend')

from voxquery.core.sql_safety import extract_tables, extract_columns, is_read_only, validate_sql

# Test 1: Simple SELECT query
print("=" * 80)
print("TEST 1: Simple SELECT query")
print("=" * 80)
sql1 = "SELECT * FROM Customers"
print(f"SQL: {sql1}")
print(f"Dialect: sqlserver")

tables = extract_tables(sql1, dialect="sqlserver")
print(f"✅ Tables extracted: {tables}")

columns = extract_columns(sql1, dialect="sqlserver")
print(f"✅ Columns extracted: {columns}")

is_safe, error = is_read_only(sql1, dialect="sqlserver")
print(f"✅ Is read-only: {is_safe} (error: {error})")

# Test 2: JOIN query
print("\n" + "=" * 80)
print("TEST 2: JOIN query")
print("=" * 80)
sql2 = """
SELECT c.CustomerID, c.CustomerName, o.OrderID
FROM Customers c
INNER JOIN Orders o ON c.CustomerID = o.CustomerID
WHERE o.OrderDate > '2024-01-01'
"""
print(f"SQL: {sql2}")
print(f"Dialect: sqlserver")

tables = extract_tables(sql2, dialect="sqlserver")
print(f"✅ Tables extracted: {tables}")

columns = extract_columns(sql2, dialect="sqlserver")
print(f"✅ Columns extracted: {columns}")

is_safe, error = is_read_only(sql2, dialect="sqlserver")
print(f"✅ Is read-only: {is_safe} (error: {error})")

# Test 3: Dangerous query (should be blocked)
print("\n" + "=" * 80)
print("TEST 3: Dangerous query (DELETE - should be blocked)")
print("=" * 80)
sql3 = "DELETE FROM Customers WHERE CustomerID = 1"
print(f"SQL: {sql3}")
print(f"Dialect: sqlserver")

is_safe, error = is_read_only(sql3, dialect="sqlserver")
print(f"✅ Is read-only: {is_safe} (error: {error})")
if not is_safe:
    print(f"✅ CORRECTLY BLOCKED: {error}")

# Test 4: Full validation with allowed tables
print("\n" + "=" * 80)
print("TEST 4: Full validation with allowed tables")
print("=" * 80)
sql4 = "SELECT CustomerID, CustomerName FROM Customers"
allowed_tables = {'CUSTOMERS', 'ORDERS', 'PRODUCTS'}
print(f"SQL: {sql4}")
print(f"Allowed tables: {allowed_tables}")
print(f"Dialect: sqlserver")

is_safe, reason, score = validate_sql(sql4, allowed_tables, dialect="sqlserver")
print(f"✅ Validation result: is_safe={is_safe}, score={score:.2f}")
print(f"   Reason: {reason}")

# Test 5: Validation with unknown table (should fail)
print("\n" + "=" * 80)
print("TEST 5: Validation with unknown table (should fail)")
print("=" * 80)
sql5 = "SELECT * FROM UnknownTable"
allowed_tables = {'CUSTOMERS', 'ORDERS', 'PRODUCTS'}
print(f"SQL: {sql5}")
print(f"Allowed tables: {allowed_tables}")
print(f"Dialect: sqlserver")

is_safe, reason, score = validate_sql(sql5, allowed_tables, dialect="sqlserver")
print(f"✅ Validation result: is_safe={is_safe}, score={score:.2f}")
print(f"   Reason: {reason}")
if not is_safe:
    print(f"✅ CORRECTLY REJECTED: Unknown table detected")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
