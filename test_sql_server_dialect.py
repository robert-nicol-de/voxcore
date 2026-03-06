#!/usr/bin/env python3
"""Test SQL Server dialect conversion"""

import re

def translate_to_sqlserver(sql: str) -> str:
    """Translate generic SQL to SQL Server dialect"""
    # Replace SELECT ... LIMIT N with SELECT TOP N ...
    sql = re.sub(
        r'SELECT\s+(.*?)\s+FROM\s+(.+?)\s+LIMIT\s+(\d+)(?:\s|$)',
        r'SELECT TOP \3 \1 FROM \2 ',
        sql,
        flags=re.IGNORECASE
    )
    return sql

# Test cases
test_cases = [
    ("SELECT * FROM AWBuildVersion LIMIT 10", "SELECT TOP 10 * FROM AWBuildVersion"),
    ("SELECT col1, col2 FROM table1 LIMIT 5", "SELECT TOP 5 col1, col2 FROM table1"),
    ("SELECT COUNT(*) FROM users LIMIT 1", "SELECT TOP 1 COUNT(*) FROM users"),
]

print("Testing SQL Server dialect conversion:\n")
for input_sql, expected in test_cases:
    result = translate_to_sqlserver(input_sql)
    status = "✅" if result.strip() == expected.strip() else "❌"
    print(f"{status} Input:    {input_sql}")
    print(f"   Expected: {expected}")
    print(f"   Got:      {result}")
    print()
