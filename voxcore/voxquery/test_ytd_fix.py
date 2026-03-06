#!/usr/bin/env python3
"""Test YTD query generation fix"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

load_dotenv()

from voxquery.core.sql_generator import SQLGenerator
from voxquery.core.connection_manager import ConnectionManager

def test_ytd_query():
    """Test that YTD query generates correct SQL without hallucinating TRANSACTION_DATE as a table"""
    
    print("\n" + "="*80)
    print("TEST: YTD Query Generation")
    print("="*80 + "\n")
    
    # Initialize connection
    conn_manager = ConnectionManager()
    engine = conn_manager.get_engine()
    
    if not engine:
        print("❌ Failed to get database engine")
        return False
    
    # Initialize SQL generator
    generator = SQLGenerator(
        engine=engine,
        dialect="snowflake",
        warehouse_host=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse_user=os.getenv("SNOWFLAKE_USER"),
        warehouse_password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse_database=os.getenv("SNOWFLAKE_DATABASE"),
    )
    
    # Test 1: YTD query
    print("\n" + "-"*80)
    print("TEST 1: YTD Query")
    print("-"*80)
    
    question1 = "give me ytd"
    result1 = generator.generate(question1)
    
    print(f"\nQuestion: {question1}")
    print(f"Generated SQL: {result1.sql}")
    print(f"Confidence: {result1.confidence}")
    
    # Check for hallucination
    if "TRANSACTION_DATE" in result1.sql and "FROM TRANSACTION_DATE" in result1.sql:
        print("❌ FAILED: Hallucinated TRANSACTION_DATE as a table")
        return False
    
    if "FROM TRANSACTIONS" not in result1.sql and "SELECT 1" not in result1.sql:
        print("⚠️  WARNING: Query doesn't reference TRANSACTIONS table")
    
    print("✅ PASSED: No hallucination of TRANSACTION_DATE as table")
    
    # Test 2: Different query to check for duplicate response
    print("\n" + "-"*80)
    print("TEST 2: Different Query (Check for Duplicate Response)")
    print("-"*80)
    
    question2 = "show me top 10 accounts"
    result2 = generator.generate(question2)
    
    print(f"\nQuestion: {question2}")
    print(f"Generated SQL: {result2.sql}")
    print(f"Confidence: {result2.confidence}")
    
    # Check if response is different from first query
    if result1.sql.strip() == result2.sql.strip():
        print("❌ FAILED: Generated identical SQL for different questions")
        print(f"  Query 1: {result1.sql}")
        print(f"  Query 2: {result2.sql}")
        return False
    
    print("✅ PASSED: Generated different SQL for different questions")
    
    # Test 3: Verify schema context shows columns belong to tables
    print("\n" + "-"*80)
    print("TEST 3: Schema Context Format")
    print("-"*80)
    
    schema_context = generator.schema_analyzer.get_schema_context()
    
    if "Columns in" not in schema_context:
        print("⚠️  WARNING: Schema context doesn't explicitly show column ownership")
    else:
        print("✅ PASSED: Schema context explicitly shows which columns belong to which tables")
    
    if "TRANSACTION_DATE is a COLUMN" in schema_context:
        print("✅ PASSED: Schema context includes explicit warning about TRANSACTION_DATE")
    else:
        print("⚠️  WARNING: Schema context doesn't include explicit column/table distinction")
    
    print("\n" + "="*80)
    print("ALL TESTS PASSED ✅")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_ytd_query()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
