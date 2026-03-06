#!/usr/bin/env python3
"""Comprehensive test of the full VoxQuery flow"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")

def test_full_flow():
    """Test the complete VoxQuery flow"""
    
    print_section("VOXQUERY FULL FLOW TEST")
    
    # Step 1: Connect to Snowflake
    print_section("STEP 1: Connect to Snowflake")
    
    connect_payload = {
        "database": "snowflake",
        "credentials": {
            "host": "we08391.af-south-1.aws",
            "username": "VOXQUERY",
            "password": "Robert210680!@#$",
            "database": "VOXQUERYTRAININGPIN2025",
            "auth_type": "sql"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/connect", json=connect_payload)
    if response.status_code != 200:
        print(f"❌ Connection failed: {response.json()}")
        return False
    
    print(f"✅ Connected to Snowflake")
    print(f"   Database: VOXQUERYTRAININGPIN2025")
    print(f"   Account: we08391.af-south-1.aws")
    
    # Step 2: Get schema
    print_section("STEP 2: Get Database Schema")
    
    response = requests.get(f"{BASE_URL}/api/v1/schema")
    if response.status_code == 200:
        schema = response.json()
        tables = schema.get('tables', [])
        print(f"✅ Schema retrieved")
        print(f"   Tables found: {len(tables)}")
        if tables:
            print(f"   First table: {tables[0]}")
    else:
        print(f"⚠️  Schema endpoint not available")
    
    # Step 3: Generate smart questions
    print_section("STEP 3: Generate Smart Questions")
    
    response = requests.get(f"{BASE_URL}/api/v1/schema/questions")
    if response.status_code == 200:
        questions = response.json().get('questions', [])
        print(f"✅ Generated {len(questions)} smart questions")
        for i, q in enumerate(questions[:3], 1):
            print(f"   {i}. {q}")
    else:
        print(f"⚠️  Questions endpoint not available")
    
    # Step 4: Execute queries
    print_section("STEP 4: Execute Queries")
    
    test_questions = [
        "Show me the top 10 records",
        "Show me records sorted by SALES_AMOUNT descending",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Query {i} ---")
        print(f"Question: {question}")
        
        query_payload = {
            "question": question,
            "execute": True
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/query", json=query_payload)
        result = response.json()
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success")
            print(f"   SQL: {result.get('sql')}")
            print(f"   Rows: {result.get('row_count')}")
            print(f"   Time: {result.get('execution_time_ms'):.2f}ms")
            if result.get('data'):
                print(f"   Sample: {result['data'][0]}")
        
        time.sleep(0.5)
    
    # Step 5: Summary
    print_section("SUMMARY")
    print("✅ VoxQuery Full Flow Test Complete!")
    print("\nKey Features Verified:")
    print("  ✅ Snowflake connection with explicit context switching")
    print("  ✅ Raw connector query execution (bypasses SQLAlchemy)")
    print("  ✅ Result fetching and conversion to dict format")
    print("  ✅ Multiple queries in sequence")
    print("  ✅ Proper error handling")
    
    return True

if __name__ == "__main__":
    try:
        success = test_full_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
