#!/usr/bin/env python
"""Check available ODBC drivers"""

import pyodbc

print("Available ODBC drivers:")
print("=" * 60)

drivers = sorted(pyodbc.drivers())

if not drivers:
    print("No ODBC drivers found!")
else:
    for i, driver in enumerate(drivers, 1):
        print(f"{i}. {driver}")

print("=" * 60)
print(f"Total: {len(drivers)} driver(s)")

# Check for SQL Server drivers specifically
print("\nSQL Server drivers:")
sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
if sql_server_drivers:
    for driver in sql_server_drivers:
        print(f"  ✓ {driver}")
else:
    print("  ✗ No SQL Server drivers found!")
    print("  Install: ODBC Driver 17 for SQL Server")
