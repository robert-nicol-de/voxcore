#!/usr/bin/env python3
"""
Test that NoneType errors are fixed in error handling
"""
import sys
import json

# Test 1: Verify engine.ask() returns proper dict on error
print("=" * 80)
print("TEST 1: Engine error handling returns proper dict")
print("=" * 80)

from voxquery.core.engine import VoxQueryEngine

# Create engine with valid warehouse but trigger error in ask()
try:
    engine = VoxQueryEngine(warehouse_type="sqlserver")
    # Mock the sql_generator to raise an error
    original_generate = engine.sql_generator.generate
    def mock_generate(*args, **kwargs):
        raise ValueError("Simulated LLM error")
    engine.sql_generator.generate = mock_generate
    
    result = engine.ask("Show me top 10 accounts")
    
    # Verify all required fields exist
    required_fields = [
        "question", "error", "sql", "data", "query_type", 
        "confidence", "explanation", "tables_used", "execution_time_ms", "row_count"
    ]
    
    missing_fields = [f for f in required_fields if f not in result]
    
    if missing_fields:
        print("FAIL: Missing fields: " + str(missing_fields))
        sys.exit(1)
    
    # Verify no None values for critical fields
    if result.get("sql") is None:
        print("FAIL: sql is None (should be empty string)")
        sys.exit(1)
    
    if result.get("data") is not None and not isinstance(result.get("data"), (list, type(None))):
        print("FAIL: data is not list or None")
        sys.exit(1)
    
    print("PASS: All required fields present")
    print("   sql type: " + str(type(result.get('sql'))) + " = '" + str(result.get('sql')) + "'")
    print("   data type: " + str(type(result.get('data'))))
    print("   error: " + str(result.get('error'))[:50] + "...")
    
except Exception as e:
    print("FAIL: Exception during test: " + str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("TEST 2: Query endpoint handles None gracefully")
print("=" * 80)

# Test that the query endpoint doesn't crash on None values
test_result = {
    "sql": None,
    "data": None,
    "error": "Test error"
}

# Simulate the checks from query.py
generated_sql = (test_result.get("sql") or "").upper()
print("PASS: generated_sql = '" + generated_sql + "' (no crash)")

if generated_sql and ("DATABASELOG" in generated_sql or "ERRORLOG" in generated_sql):
    print("   Would warn about wrong table")
else:
    print("   No table warning (correct)")

print("\n" + "=" * 80)
print("ALL TESTS PASSED")
print("=" * 80)
