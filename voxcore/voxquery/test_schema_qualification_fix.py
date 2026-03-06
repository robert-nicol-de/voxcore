#!/usr/bin/env python3
"""
Test schema qualification fix for SQL Server
Verifies that:
1. force_tsql properly qualifies table names
2. Schema context includes qualified names
3. LLM prompt includes schema qualification instruction
"""

import sys
sys.path.insert(0, '/workspace/backend')

from voxquery.core.sql_generator import SQLGenerator

def test_force_tsql_qualification():
    """Test that force_tsql properly qualifies table names"""
    print("\n" + "="*80)
    print("TEST 1: force_tsql Schema Qualification")
    print("="*80)
    
    test_cases = [
        {
            "input": "SELECT * FROM Customer WHERE CustomerID = 1",
            "expected": "SELECT TOP 10 * FROM Sales.Customer WHERE CustomerID = 1\nORDER BY 1 DESC",
            "description": "Unqualified Customer table"
        },
        {
            "input": "SELECT * FROM SalesOrderHeader",
            "expected": "SELECT TOP 10 * FROM Sales.SalesOrderHeader\nORDER BY 1 DESC",
            "description": "Unqualified SalesOrderHeader table"
        },
        {
            "input": "SELECT * FROM Person",
            "expected": "SELECT TOP 10 * FROM Person.Person\nORDER BY 1 DESC",
            "description": "Unqualified Person table"
        },
        {
            "input": "SELECT * FROM Sales.Customer",
            "expected": "SELECT TOP 10 * FROM Sales.Customer\nORDER BY 1 DESC",
            "description": "Already qualified Customer table (should not double-qualify)"
        },
        {
            "input": "SELECT * FROM Customer c JOIN SalesOrderHeader s ON c.CustomerID = s.CustomerID",
            "expected": "SELECT TOP 10 * FROM Sales.Customer c JOIN Sales.SalesOrderHeader s ON c.CustomerID = s.CustomerID\nORDER BY 1 DESC",
            "description": "Multiple unqualified tables"
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        result = SQLGenerator.force_tsql(test["input"])
        
        # Normalize whitespace for comparison
        result_normalized = " ".join(result.split())
        expected_normalized = " ".join(test["expected"].split())
        
        if result_normalized == expected_normalized:
            print(f"✅ Test {i} PASSED: {test['description']}")
            print(f"   Input:    {test['input']}")
            print(f"   Output:   {result}")
            passed += 1
        else:
            print(f"❌ Test {i} FAILED: {test['description']}")
            print(f"   Input:    {test['input']}")
            print(f"   Expected: {test['expected']}")
            print(f"   Got:      {result}")
            failed += 1
        print()
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

def test_schema_instruction_in_prompt():
    """Test that schema instruction is included in prompt for SQL Server"""
    print("\n" + "="*80)
    print("TEST 2: Schema Instruction in Prompt")
    print("="*80)
    
    # Create a SQL generator for SQL Server
    generator = SQLGenerator(dialect="sqlserver")
    
    # Build a test prompt
    schema_context = """
TABLE: dbo.Customer
  Columns in dbo.Customer:
    - CustomerID: INT (NOT NULL)
    - Name: VARCHAR (NOT NULL)
"""
    
    prompt = generator._build_prompt(
        question="Show top 10 customers",
        schema_context=schema_context,
        context=None,
        system_prompt=None
    )
    
    # Check if schema qualification instruction is present
    if "CRITICAL FOR SQL SERVER" in prompt and "schema-qualified" in prompt:
        print("✅ Schema qualification instruction found in prompt")
        print(f"\nPrompt excerpt:")
        lines = prompt.split('\n')
        for i, line in enumerate(lines):
            if "CRITICAL FOR SQL SERVER" in line:
                # Print 10 lines starting from this line
                for j in range(i, min(i+10, len(lines))):
                    print(f"  {lines[j]}")
                break
        return True
    else:
        print("❌ Schema qualification instruction NOT found in prompt")
        print(f"\nFull prompt:\n{prompt}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SCHEMA QUALIFICATION FIX TEST SUITE")
    print("="*80)
    
    test1_passed = test_force_tsql_qualification()
    test2_passed = test_schema_instruction_in_prompt()
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
