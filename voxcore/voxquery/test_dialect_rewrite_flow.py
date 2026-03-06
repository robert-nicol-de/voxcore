#!/usr/bin/env python3
"""Test the dialect rewrite flow for SQL Server LIMIT → TOP conversion"""

from voxquery.core.platform_dialect_engine import process_sql

print("=" * 80)
print("TEST 1: SQL Server with LIMIT (should be rewritten to TOP)")
print("=" * 80)
test_sql = "SELECT * FROM Production.Document LIMIT 10"
result = process_sql(test_sql, "sqlserver")
print(f"Original:  {result['original_sql']}")
print(f"Rewritten: {result['rewritten_sql']}")
print(f"Final:     {result['final_sql']}")
print(f"Valid:     {result['is_valid']}")
print(f"Score:     {result['score']}")
print(f"Issues:    {result['issues']}")
print(f"Fallback:  {result['fallback_used']}")
print()

print("=" * 80)
print("TEST 2: SQL Server with TOP (should pass)")
print("=" * 80)
test_sql2 = "SELECT TOP 10 * FROM Sales.Customer ORDER BY CustomerID DESC"
result2 = process_sql(test_sql2, "sqlserver")
print(f"Original:  {result2['original_sql']}")
print(f"Rewritten: {result2['rewritten_sql']}")
print(f"Final:     {result2['final_sql']}")
print(f"Valid:     {result2['is_valid']}")
print(f"Score:     {result2['score']}")
print(f"Issues:    {result2['issues']}")
print(f"Fallback:  {result2['fallback_used']}")
print()

print("=" * 80)
print("TEST 3: Snowflake with LIMIT (should NOT be rewritten)")
print("=" * 80)
test_sql3 = "SELECT * FROM ACCOUNTS LIMIT 10"
result3 = process_sql(test_sql3, "snowflake")
print(f"Original:  {result3['original_sql']}")
print(f"Rewritten: {result3['rewritten_sql']}")
print(f"Final:     {result3['final_sql']}")
print(f"Valid:     {result3['is_valid']}")
print(f"Score:     {result3['score']}")
print(f"Issues:    {result3['issues']}")
print(f"Fallback:  {result3['fallback_used']}")
