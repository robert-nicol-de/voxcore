#!/usr/bin/env python3
"""
Test script to verify accuracy hardening (96-98% target)

Tests the 4 exact questions from the user:
1. "What is our total balance?"
2. "Top 10 accounts by balance"
3. "Give me YTD revenue summary"
4. "Monthly transaction count"

Captures full prompt and raw Groq response if hallucination occurs.
"""

import sys
import os
import logging
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from voxquery.core.engine import VoxQueryEngine
from voxquery.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test questions
TEST_QUESTIONS = [
    "What is our total balance?",
    "Top 10 accounts by balance",
    "Give me YTD revenue summary",
    "Monthly transaction count",
]

def test_accuracy_hardening():
    """Test accuracy hardening with 4 exact questions"""
    
    print("\n" + "="*100)
    print("ACCURACY HARDENING TEST - 96-98% TARGET")
    print("="*100)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Dialect: {settings.warehouse_type}")
    print("="*100 + "\n")
    
    # Initialize engine
    try:
        engine = VoxQueryEngine()
        logger.info("✅ VoxQueryEngine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize VoxQueryEngine: {e}")
        return False
    
    # Test each question
    results = []
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'='*100}")
        print(f"TEST {i}/4: {question}")
        print(f"{'='*100}\n")
        
        try:
            # Generate SQL
            logger.info(f"Generating SQL for question: {question}")
            result = engine.ask(question)
            
            # Extract SQL
            sql = result.get("sql", "")
            
            # Check for hallucinations
            hallucinated = False
            hallucination_reason = None
            
            # Check for forbidden table names
            forbidden_tables = [
                "FACT_REVENUE", "CUSTOMERS", "SALES", "BUDGET", 
                "ORDERS", "PAYMENTS", "INVOICES", "TRANSACTION_DATE"
            ]
            
            for forbidden in forbidden_tables:
                if forbidden in sql.upper():
                    hallucinated = True
                    hallucination_reason = f"Hallucinated table: {forbidden}"
                    break
            
            # Check for valid SELECT
            if not sql.upper().startswith("SELECT"):
                hallucinated = True
                hallucination_reason = "SQL doesn't start with SELECT"
            
            # Check for SELECT 1 (fallback)
            if sql.strip().upper() == "SELECT 1":
                hallucinated = True
                hallucination_reason = "Fallback query (SELECT 1)"
            
            # Print results
            print(f"Question: {question}")
            print(f"Generated SQL: {sql}")
            print(f"Hallucinated: {'❌ YES' if hallucinated else '✅ NO'}")
            if hallucination_reason:
                print(f"Reason: {hallucination_reason}")
            print()
            
            results.append({
                "question": question,
                "sql": sql,
                "hallucinated": hallucinated,
                "reason": hallucination_reason,
            })
            
        except Exception as e:
            logger.error(f"❌ Error testing question: {e}", exc_info=True)
            results.append({
                "question": question,
                "sql": None,
                "hallucinated": True,
                "reason": str(e),
            })
    
    # Summary
    print("\n" + "="*100)
    print("TEST SUMMARY")
    print("="*100 + "\n")
    
    total = len(results)
    hallucinated_count = sum(1 for r in results if r["hallucinated"])
    accuracy = ((total - hallucinated_count) / total) * 100
    
    print(f"Total Questions: {total}")
    print(f"Hallucinations: {hallucinated_count}")
    print(f"Accuracy: {accuracy:.1f}%")
    print()
    
    for i, result in enumerate(results, 1):
        status = "❌ HALLUCINATED" if result["hallucinated"] else "✅ PASSED"
        print(f"{i}. {status}: {result['question']}")
        if result["reason"]:
            print(f"   Reason: {result['reason']}")
        print(f"   SQL: {result['sql'][:80]}..." if result['sql'] and len(result['sql']) > 80 else f"   SQL: {result['sql']}")
        print()
    
    print("="*100)
    print(f"FINAL ACCURACY: {accuracy:.1f}%")
    print(f"TARGET: 96-98%")
    print(f"STATUS: {'✅ PASSED' if accuracy >= 96 else '❌ FAILED'}")
    print("="*100 + "\n")
    
    return accuracy >= 96

if __name__ == "__main__":
    success = test_accuracy_hardening()
    sys.exit(0 if success else 1)
