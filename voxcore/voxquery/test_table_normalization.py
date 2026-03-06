#!/usr/bin/env python3
"""Test table name normalization in extract_tables"""

import sys
sys.path.insert(0, '/Users/USER/Documents/trae_projects/VoxQuery/backend')

from voxquery.core.sql_safety import extract_tables, _normalize_table_name

print("=" * 80)
print("TEST: Table Name Normalization")
print("=" * 80)

# Test 1: Normalize individual table names
print("\n1. Testing _normalize_table_name():")
test_names = [
    'CUSTOMER',
    'SALESORDERHEADER',
    'PRODUCT',
    'EMPLOYEE',
    'Sales.Customer',  # Already qualified
    'UNKNOWN_TABLE',   # Unknown table
]

for name in test_names:
    normalized = _normalize_table_name(name)
    print(f"  {name:30} → {normalized}")

# Test 2: Extract tables from SQL with unqualified names
print("\n2. Testing extract_tables() with unqualified names:")
sql_unqualified = """
SELECT TOP 10 c.CustomerID, c.Name, SUM(soh.TotalDue) as total_balance
FROM CUSTOMER c
JOIN SALESORDERHEADER soh ON c.CustomerID = soh.CustomerID
GROUP BY c.CustomerID, c.Name
ORDER BY total_balance DESC
"""

tables = extract_tables(sql_unqualified, dialect='sqlserver')
print(f"  Extracted tables: {tables}")
print(f"  Expected: {{'SALES.CUSTOMER', 'SALES.SALESORDERHEADER'}}")
print(f"  Match: {tables == {'SALES.CUSTOMER', 'SALES.SALESORDERHEADER'}}")

# Test 3: Extract tables from SQL with qualified names
print("\n3. Testing extract_tables() with qualified names:")
sql_qualified = """
SELECT TOP 10 c.CustomerID, c.Name, SUM(soh.TotalDue) as total_balance
FROM Sales.Customer c
JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
GROUP BY c.CustomerID, c.Name
ORDER BY total_balance DESC
"""

tables = extract_tables(sql_qualified, dialect='sqlserver')
print(f"  Extracted tables: {tables}")
print(f"  Expected: {{'SALES.CUSTOMER', 'SALES.SALESORDERHEADER'}}")
print(f"  Match: {tables == {'SALES.CUSTOMER', 'SALES.SALESORDERHEADER'}}")

# Test 4: Extract tables from SQL with mixed names
print("\n4. Testing extract_tables() with mixed names:")
sql_mixed = """
SELECT TOP 10 c.CustomerID, c.Name, SUM(soh.TotalDue) as total_balance
FROM CUSTOMER c
JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
GROUP BY c.CustomerID, c.Name
ORDER BY total_balance DESC
"""

tables = extract_tables(sql_mixed, dialect='sqlserver')
print(f"  Extracted tables: {tables}")
print(f"  Expected: {{'SALES.CUSTOMER', 'SALES.SALESORDERHEADER'}}")
print(f"  Match: {tables == {'SALES.CUSTOMER', 'SALES.SALESORDERHEADER'}}")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETE")
print("=" * 80)
