#!/usr/bin/env python3
"""Direct test of SQL Server connection without SQLAlchemy"""

import pyodbc
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test 1: Check available ODBC drivers
print("\n" + "="*80)
print("AVAILABLE ODBC DRIVERS")
print("="*80)
drivers = pyodbc.drivers()
for driver in drivers:
    print(f"  - {driver}")

# Test 2: Try to connect with minimal connection string
print("\n" + "="*80)
print("TEST 1: Windows Auth (Trusted Connection)")
print("="*80)

conn_str_windows = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=VoxQueryTrainingFin2025;"
    "Trusted_Connection=yes;"
)

print(f"Connection String: {conn_str_windows}")
try:
    conn = pyodbc.connect(conn_str_windows, autocommit=True, unicode_results=True)
    print("✓ Connection succeeded!")
    
    # Try a simple query
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    result = cursor.fetchone()
    print(f"✓ Query result: {result[0][:50]}...")
    
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print(f"  Exception type: {type(e).__name__}")
    print(f"  Exception args: {e.args}")

# Test 3: Try with different server names
print("\n" + "="*80)
print("TEST 2: Try different server names")
print("="*80)

server_variants = [
    "localhost",
    ".",
    "127.0.0.1",
    "localhost\\SQLEXPRESS",
    "(local)",
]

for server in server_variants:
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        f"Server={server};"
        "Database=VoxQueryTrainingFin2025;"
        "Trusted_Connection=yes;"
    )
    print(f"\nTrying: Server={server}")
    try:
        conn = pyodbc.connect(conn_str, autocommit=True, unicode_results=True, timeout=3)
        print(f"  ✓ Connected!")
        conn.close()
        break
    except Exception as e:
        print(f"  ✗ Failed: {str(e)[:80]}")

print("\n" + "="*80)
print("DONE")
print("="*80)
