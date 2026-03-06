#!/usr/bin/env python3
"""
Test the aggressive dialect lock with a balance question
This tests the complete flow: LLM generation → sanitize_tsql → validate_sql
"""

import sys
import json
sys.path.insert(0, '/workspace/backend')

import requests
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("TESTING AGGRESSIVE DIALECT LOCK WITH BALANCE QUESTION")
print("="*80)

# First, connect to SQL Server
print("\n1. Connecting to SQL Server...")
connect_payload = {
    "warehouse": "sqlserver",
    "database": "AdventureWorks2022",
    "server": "localhost",
    "username": "",
    "password": "",
    "use_windows_auth": True
}

try:
    response = requests.post(f"{BASE_URL}/api/connect", json=connect_payload, timeout=10)
    if response.status_code == 200:
        print("✅ Connected to SQL Server")
    else:
        print(f"⚠️  Connection response: {response.status_code}")
        print(response.text[:200])
except Exception as e:
    print(f"⚠️  Connection error: {e}")

time.sleep(1)

# Now ask a balance question
print("\n2. Asking balance question: 'Show top 10 accounts by balance'")
question_payload = {
    "question": "Show top 10 accounts by balance",
    "warehouse": "sqlserver",
    "execute": False,  # Dry run first
    "dry_run": True
}

try:
    response = requests.post(f"{BASE_URL}/api/ask", json=question_payload, timeout=30)
    if response.status_code == 200:
        result = response.json()
        sql = result.get('sql', '')
        print(f"\n✅ Generated SQL:")
        print(f"   {sql}")
        
        # Check for aggressive lock compliance
        checks = {
            "Uses TOP (not LIMIT)": "TOP" in sql and "LIMIT" not in sql,
            "Uses schema-qualified tables": "Sales.Customer" in sql or "Sales.SalesOrderHeader" in sql,
            "Joins to Person.Person for names": "Person.Person" in sql,
            "Uses TotalDue for balance": "TotalDue" in sql,
            "No invented columns": "c.Name" not in sql and "c.Balance" not in sql,
            "No production/log tables": "DatabaseLog" not in sql and "ErrorLog" not in sql,
        }
        
        print(f"\n   Compliance checks:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        all_passed = all(checks.values())
        if all_passed:
            print(f"\n✅ SQL FULLY COMPLIANT with aggressive dialect lock!")
        else:
            print(f"\n⚠️  Some compliance checks failed")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:500])
except Exception as e:
    print(f"❌ Request error: {e}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
