#!/usr/bin/env python3
"""Test SQL Server connection directly"""

import pyodbc

print("\n" + "="*80)
print("TESTING SQL SERVER CONNECTION DIRECTLY")
print("="*80 + "\n")

# List available drivers
print("Available ODBC drivers:")
for driver in pyodbc.drivers():
    if 'SQL' in driver or 'sql' in driver:
        print(f"  - {driver}")
print()

# Try different connection methods
methods = [
    {
        "name": "SQL Auth with ODBC 18",
        "connection_string": "Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=AdventureWorks2022;UID=sa;PWD=Stayout1234;TrustServerCertificate=yes"
    },
    {
        "name": "SQL Auth with ODBC 17",
        "connection_string": "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=AdventureWorks2022;UID=sa;PWD=Stayout1234;TrustServerCertificate=yes"
    },
    {
        "name": "Windows Auth with ODBC 18",
        "connection_string": "Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=AdventureWorks2022;Trusted_Connection=yes;TrustServerCertificate=yes"
    },
    {
        "name": "Windows Auth with ODBC 17",
        "connection_string": "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=AdventureWorks2022;Trusted_Connection=yes;TrustServerCertificate=yes"
    },
    {
        "name": "SQL Auth with (local)",
        "connection_string": "Driver={ODBC Driver 18 for SQL Server};Server=(local);Database=AdventureWorks2022;UID=sa;PWD=Stayout1234;TrustServerCertificate=yes"
    },
]

for method in methods:
    print(f"Trying: {method['name']}")
    try:
        conn = pyodbc.connect(method['connection_string'])
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"  ✓ SUCCESS!")
        print(f"    Version: {version[:50]}...")
        cursor.close()
        conn.close()
        break
    except Exception as e:
        print(f"  ✗ Failed: {str(e)[:100]}")
    print()

print("="*80)
