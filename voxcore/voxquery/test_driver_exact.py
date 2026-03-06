#!/usr/bin/env python3
"""Test exact ODBC driver name"""

import pyodbc

# Get the exact driver name
drivers = pyodbc.drivers()
print("Available drivers:")
for d in drivers:
    print(f"  '{d}' (repr: {repr(d)})")

driver_17 = [d for d in drivers if 'ODBC Driver 17' in d]
if driver_17:
    driver_17 = driver_17[0]
    print(f"\nExact driver name: '{driver_17}'")
    print(f"Driver name repr: {repr(driver_17)}")
    
    # Try connection with exact driver name
    conn_str = f"Driver={{{driver_17}}};Server=.;Database=VoxQueryTrainingFin2025;Trusted_Connection=yes"
    print(f"\nConnection string: {conn_str}")
    
    try:
        conn = pyodbc.connect(conn_str, autocommit=True, unicode_results=True)
        print("✓ Connection succeeded!")
        conn.close()
    except Exception as e:
        print(f"✗ Connection failed: {e}")
else:
    print("ODBC Driver 17 not found!")
