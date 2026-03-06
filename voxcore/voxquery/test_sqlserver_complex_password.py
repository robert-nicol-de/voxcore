#!/usr/bin/env python3
"""Test SQL Server connection with complex password"""

import pyodbc

def test_connection():
    """Test SQL Server connection"""
    print("\nTesting SQL Server connection with complex password...")
    
    # Connection string with complex password
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost;"
        "Database=AdventureWorks2022;"
        "UID=sa;"
        "PWD=P@ssw0rd123!;"
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
