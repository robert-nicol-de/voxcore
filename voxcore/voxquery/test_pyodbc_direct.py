#!/usr/bin/env python3
"""Test SQL Server connection directly with pyodbc"""

import pyodbc

def test_connection():
    """Test SQL Server connection with pyodbc"""
    print("\n" + "="*80)
    print("Testing SQL Server Connection with pyodbc")
    print("="*80 + "\n")
    
    # Test parameters
    server = "localhost"
    database = "AdventureWorks2022"
    username = "sa"
    password = "Stayout1234"
    
    print(f"Connection Parameters:")
    print(f"  Server: {server}")
    print(f"  Database: {database}")
    print(f"  Username: {username}")
    print(f"  Password: {'*' * len(password)}")
    
    # Try different connection strings
    connection_strings = [
        # Standard SQL auth
        f"Driver={{ODBC Driver 18 for SQL Server}};Server={server};Database={database};UID={username};PWD={password};",
        # With TrustServerCertificate
        f"Driver={{ODBC Driver 18 for SQL Server}};Server={server};Database={database};UID={username};PWD={password};TrustServerCertificate=yes;",
        # With Encrypt=no
        f"Driver={{ODBC Driver 18 for SQL Server}};Server={server};Database={database};UID={username};PWD={password};Encrypt=no;",
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\n[Attempt {i}] Testing connection string...")
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS test")
            result = cursor.fetchone()
            print(f"✓ Connection successful! Result: {result}")
            conn.close()
            return True
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
    
    print("\n" + "="*80)
    print("✗ All connection attempts failed")
    print("="*80 + "\n")
    return False

if __name__ == "__main__":
    test_connection()
