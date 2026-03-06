#!/usr/bin/env python3
"""Test to diagnose why UI goes blank after asking a question"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import asyncio
from voxquery.api.query import QueryRequest, ask_question
from voxquery.api.auth import ConnectRequest, DatabaseCredentials, connect
from voxquery.api import engine_manager

async def test_full_flow():
    """Test the full flow: connect -> ask question -> check response"""
    print("\n" + "="*80)
    print("TESTING FULL FLOW: CONNECT -> QUESTION -> RESPONSE")
    print("="*80 + "\n")
    
    # Step 1: Connect to SQL Server
    print("STEP 1: Connecting to SQL Server (AdventureWorks2022)...")
    try:
        connect_req = ConnectRequest(
            database="sqlserver",
            credentials=DatabaseCredentials(
                host="localhost",
                database="AdventureWorks2022",
                username="sa",
                password="YourPassword123!",
                auth_type="sql"
            )
        )
        
        response = await connect(connect_req)
        print(f"✓ Connected: {response.message}\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}\n")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Ask a question
    print("STEP 2: Asking a question...")
    try:
        query_req = QueryRequest(
            question="How many products are in the database?",
            warehouse="sqlserver",
            execute=True,
            dry_run=False
        )
        
        response = await ask_question(query_req)
        
        print(f"✓ Query executed")
        print(f"  Question: {response.question}")
        print(f"  SQL: {response.sql[:100] if response.sql else 'N/A'}...")
        print(f"  Data rows: {len(response.data) if response.data else 0}")
        print(f"  Error: {response.error if response.error else 'None'}")
        print(f"  Message: {response.message if response.message else 'None'}")
        print(f"  Chart: {'Yes' if response.chart else 'No'}")
        print(f"  Charts: {list(response.charts.keys()) if response.charts else 'None'}\n")
        
        # Step 3: Check response serialization
        print("STEP 3: Checking response serialization...")
        try:
            # Try to serialize the response to JSON (like FastAPI would)
            response_dict = response.model_dump()
            json_str = json.dumps(response_dict, default=str)
            print(f"✓ Response serializes to JSON successfully")
            print(f"  JSON length: {len(json_str)} bytes\n")
            
            # Print first 500 chars of JSON
            print("  First 500 chars of JSON response:")
            print(f"  {json_str[:500]}...\n")
        except Exception as e:
            print(f"✗ Response serialization failed: {e}\n")
            import traceback
            traceback.print_exc()
        
        # Step 4: Check data content
        if response.data:
            print("STEP 4: Checking data content...")
            print(f"  First row: {response.data[0]}\n")
        
    except Exception as e:
        print(f"✗ Query execution failed: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_flow())
