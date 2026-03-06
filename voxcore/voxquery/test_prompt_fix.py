#!/usr/bin/env python
"""Test script to verify the prompt fix for different questions"""

import sys
import os
import json
import time
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

from voxquery.core.engine import VoxQueryEngine

def test_different_questions():
    """Test that different questions generate different SQL"""
    
    print("\n" + "="*80)
    print("TEST: Different Questions Generate Different SQL")
    print("="*80 + "\n")
    
    # Initialize engine
    engine = VoxQueryEngine(
        warehouse_type="sqlserver",
        warehouse_host=".",
        warehouse_user="sa",
        warehouse_password="YourPassword123!",
        warehouse_database="AdventureWorks2022",
        auth_type="sql",
    )
    
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
            result = engine.ask(question, execute=False)
            
            sql = result.get("sql", "")
            print(f"\nGenerated SQL:\n{sql}\n")
            
            results.append({
                "question": question,
                "sql": sql,
                "success": True,
            })
            
            # Small delay between questions
            time.sleep(1)
            
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
    success = test_different_questions()
    sys.exit(0 if success else 1)
