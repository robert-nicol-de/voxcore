#!/usr/bin/env python3
"""Test column hallucination prevention - all 3 layers"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voxquery.core.sql_safety import fix_invented_columns, validate_sql

print("=" * 80)
print("COLUMN HALLUCINATION PREVENTION - 3 LAYER TEST")
print("=" * 80)

# Test 1: Layer 3 - fix_invented_columns (pre-execution rewrite)
print("\n1. Testing fix_invented_columns() - Layer 3 (Pre-execution Rewrite):")
test_cases = [
    {
        "name": "Invented c.Name column",
        "input": "SELECT TOP 10 c.CustomerID, c.Name FROM Sales.Customer c",
        "expected_contains": ["Person.Person", "FirstName", "LastName"]
    },
    {
        "name": "Invented c.Balance column",
        "input": "SELECT TOP 10 c.CustomerID, c.Balance FROM Sales.Customer c",
        "expected_contains": ["Sales.SalesOrderHeader", "SUM(soh.TotalDue)"]
    },
    {
        "name": "Invented TotalBalance column",
        "input": "SELECT TOP 10 c.CustomerID, TotalBalance FROM Sales.Customer c",
        "expected_contains": ["SUM(soh.TotalDue)"]
    },
]

for test in test_cases:
    fixed = fix_invented_columns(test["input"])
    all_found = all(exp in fixed for exp in test["expected_contains"])
    status = "PASS" if all_found else "FAIL"
    print(f"  [{status}] {test['name']}")
    if not all_found:
        print(f"    Input: {test['input']}")
        print(f"    Output: {fixed}")
        print(f"    Expected to contain: {test['expected_contains']}")

# Test 2: Layer 2 - Column validation in validate_sql
print("\n2. Testing validate_sql() - Layer 2 (Column Validation):")
allowed_tables = {
    'SALES.CUSTOMER',
    'SALES.SALESORDERHEADER',
    'PERSON.PERSON',
}

test_sqls = [
    {
        "name": "Valid SQL with correct columns",
        "sql": "SELECT TOP 10 c.CustomerID, p.FirstName FROM Sales.Customer c JOIN Person.Person p ON c.PersonID = p.BusinessEntityID",
        "should_pass": True
    },
    {
        "name": "Invalid SQL with invented c.Name",
        "sql": "SELECT TOP 10 c.CustomerID, c.Name FROM Sales.Customer c",
        "should_pass": False
    },
    {
        "name": "Invalid SQL with invented c.Balance",
        "sql": "SELECT TOP 10 c.CustomerID, c.Balance FROM Sales.Customer c",
        "should_pass": False
    },
]

for test in test_sqls:
    is_safe, reason, score = validate_sql(
        test["sql"],
        allowed_tables=allowed_tables,
        dialect='sqlserver'
    )
    
    passed = is_safe == test["should_pass"]
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {test['name']}")
    print(f"    Safe: {is_safe}, Score: {score:.2f}")
    if not passed:
        print(f"    Reason: {reason}")

# Test 3: Layer 1 - Prompt includes COLUMN HALLUCINATION RULE
print("\n3. Testing COLUMN HALLUCINATION RULE in prompt - Layer 1:")
from voxquery.core.sql_generator import SQLGenerator

if hasattr(SQLGenerator, 'PRIORITY_RULES'):
    priority_rules = SQLGenerator.PRIORITY_RULES
    checks = [
        ("COLUMN HALLUCINATION RULE" in priority_rules, "COLUMN HALLUCINATION RULE defined"),
        ("c.Name" in priority_rules, "c.Name hallucination mentioned"),
        ("c.Balance" in priority_rules, "c.Balance hallucination mentioned"),
        ("Person.Person.FirstName" in priority_rules, "Correct join mentioned"),
        ("SalesOrderHeader.TotalDue" in priority_rules, "Correct balance column mentioned"),
    ]
    
    for check, desc in checks:
        status = "PASS" if check else "FAIL"
        print(f"  [{status}] {desc}")
else:
    print("  [FAIL] PRIORITY_RULES not found in SQLGenerator")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETE")
print("=" * 80)
