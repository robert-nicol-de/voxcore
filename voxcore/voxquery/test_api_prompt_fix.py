#!/usr/bin/env python
"""Test the prompt fix via HTTP API"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def connect_to_database():
    """Connect to SQL Server database"""
    print("Connecting to SQL Server...")
    
    response = requests.post(
        f"{BASE_URL}/auth/connect",
        json={
            "database": "sqlserver",
            "credentials": {
                "host": ".",
                "username": "sa",
                "password": "YourPassword123!",
                "database": "AdventureWorks2022",
                "auth_type": "sql"
            }
        },
        timeout=30
    )
    
    if response.status_code == 200:
        print("✓ Connected to SQL Server")
        return True
    else:
        print(f"✗ Connection failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_different_questions():
    """Test that different questions generate different SQL"""
    
    print("\n" + "="*80)
    print("TEST: Different Questions Generate Different SQL (via API)")
    print("="*80 + "\n")
    
    # Connect first
    if not connect_to_database():
        print("Cannot proceed without database connection")
        return False
    
    # Test questions
    questions = [
        "What is the average MarginTargetPct for products in the Dim_Product table with a CategoryKey of 1?",
        "What is the top-selling ProductName by LineTotal in the Fact_Sales table?",
        "Give me YTD sales",
    ]
    
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'─'*80}")
        print(f"Question {i}: {question}")
        print(f"{'─'*80}")
        
        try:
            # Call the API
            response = requests.post(
                f"{BASE_URL}/query",
                json={"question": question},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                sql = data.get("sql", "")
                print(f"\nGenerated SQL:\n{sql}\n")
                
                results.append({
                    "question": question,
                    "sql": sql,
                    "success": True,
                })
            else:
                print(f"ERROR: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                results.append({
                    "question": question,
                    "sql": None,
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                })
            
            # Small delay between questions
            time.sleep(2)
            
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "question": question,
                "sql": None,
                "success": False,
                "error": str(e),
            })
    
    # Analyze results
    print(f"\n{'='*80}")
    print("ANALYSIS")
    print(f"{'='*80}\n")
    
    sqls = [r["sql"] for r in results if r["success"] and r["sql"]]
    
    print(f"Total questions: {len(questions)}")
    print(f"Successful: {len([r for r in results if r['success']])}")
    print(f"Unique SQL queries: {len(set(sqls))}")
    
    # Check for duplicates
    duplicates = []
    for i, sql1 in enumerate(sqls):
        for j, sql2 in enumerate(sqls):
            if i < j and sql1 == sql2:
                duplicates.append((i, j))
    
    if duplicates:
        print(f"\n⚠️  DUPLICATE SQL DETECTED:")
        for i, j in duplicates:
            print(f"  Question {i+1} and Question {j+1} generated identical SQL")
            print(f"  SQL: {sqls[i][:100]}...")
    else:
        print(f"\n✓ All questions generated DIFFERENT SQL")
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    for i, result in enumerate(results, 1):
        status = "✓" if result["success"] else "✗"
        print(f"{status} Question {i}: {result['question'][:60]}...")
        if result["success"]:
            print(f"  SQL: {result['sql'][:80]}...")
        else:
            print(f"  Error: {result.get('error', 'Unknown')}")
    
    return len(duplicates) == 0

if __name__ == "__main__":
    import sys
    success = test_different_questions()
    sys.exit(0 if success else 1)
