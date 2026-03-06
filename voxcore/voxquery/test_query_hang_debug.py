#!/usr/bin/env python3
"""
Debug query hang issue - test the full flow
"""
import sys
import time

print("=" * 80)
print("TEST: Query Hang Debug")
print("=" * 80)

# Test 1: Check if backend can start
print("\n1. Testing backend startup...")
try:
    from voxquery.api.engine_manager import engine_manager
    print("   OK: engine_manager imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

# Test 2: Check if we can get an engine
print("\n2. Testing engine retrieval...")
try:
    engine = engine_manager.get_engine()
    if engine:
        print(f"   OK: Engine retrieved: {engine.warehouse_type}")
    else:
        print("   INFO: No engine connected (expected)")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

# Test 3: Check if schema analyzer works
print("\n3. Testing schema analyzer...")
try:
    from voxquery.core.schema_analyzer import SchemaAnalyzer
    analyzer = SchemaAnalyzer()
    print("   OK: SchemaAnalyzer created")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

# Test 4: Check if SQL generator works
print("\n4. Testing SQL generator...")
try:
    from voxquery.core.sql_generator import SQLGenerator
    gen = SQLGenerator()
    print("   OK: SQLGenerator created")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

# Test 5: Check if platform dialect engine works
print("\n5. Testing platform dialect engine...")
try:
    from voxquery.core import platform_dialect_engine
    result = platform_dialect_engine.process_sql("SELECT * FROM test", "sqlserver")
    print(f"   OK: Platform dialect engine works")
    print(f"      Result keys: {list(result.keys())}")
except Exception as e:
    print(f"   FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("All diagnostic tests passed")
print("=" * 80)
print("\nIf query still hangs, the issue is likely:")
print("1. Groq API call is slow/timing out")
print("2. Database connection is hanging")
print("3. Schema analysis is taking too long")
print("\nCheck backend logs for more details")
