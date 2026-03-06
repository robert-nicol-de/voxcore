#!/usr/bin/env python3
"""Test the full flow with AdventureWorks2022"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from voxquery.core.engine import VoxQueryEngine
from voxquery.core.connection_manager import ConnectionManager
import json

def test_adventureworks():
    """Test with AdventureWorks2022"""
    print("\n" + "="*80)
    print("TESTING ADVENTUREWORKS2022 FLOW")
    print("="*80 + "\n")
    
    # Create connection manager
    conn_mgr = ConnectionManager()
    
    # Connect to SQL Server with AdventureWorks2022
    print("1. Connecting to SQL Server (AdventureWorks2022)...")
    try:
        conn_mgr.connect(
            warehouse_type="sqlserver",
            server="localhost",
            database="AdventureWorks2022",
            username="sa",
            password="YourPassword123!"
        )
        print("✓ Connected successfully\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}\n")
        return
    
    # Create engine
    print("2. Creating VoxQueryEngine...")
    try:
        engine = VoxQueryEngine(connection_manager=conn_mgr)
        print("✓ Engine created\n")
    except Exception as e:
        print(f"✗ Engine creation failed: {e}\n")
        return
    
    # Get schema
    print("3. Fetching schema...")
    try:
        schema = engine.get_schema()
        print(f"✓ Schema fetched: {len(schema)} tables")
        print(f"   Tables: {list(schema.keys())[:5]}...\n")
    except Exception as e:
        print(f"✗ Schema fetch failed: {e}\n")
        return
    
    # Generate questions
    print("4. Generating schema-based questions...")
    try:
        questions = engine.generate_questions_from_schema(schema, limit=4)
        print(f"✓ Generated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q}")
        print()
    except Exception as e:
        print(f"✗ Question generation failed: {e}\n")
    
    # Ask a simple question
    print("5. Testing query execution...")
    try:
        result = engine.ask(
            question="How many products are in the database?",
            execute=True,
            dry_run=False
        )
        print(f"✓ Query executed")
        print(f"   SQL: {result.get('sql', 'N/A')[:100]}...")
        print(f"   Data rows: {len(result.get('data') or [])}")
        if result.get('data'):
            print(f"   First row: {result.get('data')[0]}")
        if result.get('error'):
            print(f"   Error: {result.get('error')}")
        print()
    except Exception as e:
        print(f"✗ Query execution failed: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_adventureworks()
