#!/usr/bin/env python3
"""Simple test of SQL Server connection"""

import pyodbc

def test_connection():
    """Test SQL Server connection"""
    print("\nTesting SQL Server connection...")
    
    # Connection string with all necessary options
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost;"
        "Database=AdventureWorks2022;"
        "UID=sa;"
        "PWD=Stayout1234;"
        "TrustServerCertificate=yes;"
        "Encrypt=no;"
    )
    
    try:
        print(f"Connecting to SQL Server...")
        conn = pyodbc.connect(conn_str)
        print("✓ Connection successful!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION AS Version")
        version = cursor.fetchone()
        print(f"✓ SQL Server Version: {version[0][:50]}...")
        
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES")
        table_count = cursor.fetchone()
        print(f"✓ Table count: {table_count[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
