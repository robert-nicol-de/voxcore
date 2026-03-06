#!/usr/bin/env python3
"""Test SQL Server connection with Windows Authentication"""

import pyodbc

def test_connection():
    """Test SQL Server connection with Windows Auth"""
    print("\n" + "="*80)
    print("Testing SQL Server Connection with Windows Authentication")
    print("="*80 + "\n")
    
    # Connection string with Windows Authentication
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost;"
        "Database=AdventureWorks2022;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
        "Encrypt=no;"
    )
    
    try:
        print(f"Connecting to SQL Server with Windows Authentication...")
        conn = pyodbc.connect(conn_str)
        print("✓ Connection successful!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION AS Version")
        version = cursor.fetchone()
        print(f"✓ SQL Server Version: {version[0][:50]}...")
        
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES")
        table_count = cursor.fetchone()
        print(f"✓ Table count: {table_count[0]}")
        
        cursor.execute("SELECT DB_NAME() AS CurrentDatabase")
        db_name = cursor.fetchone()
        print(f"✓ Current Database: {db_name[0]}")
        
        conn.close()
        
        print("\n" + "="*80)
        print("✓ SQL SERVER WINDOWS AUTH CONNECTION TEST PASSED")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\n" + "="*80)
        print("✗ SQL SERVER WINDOWS AUTH CONNECTION TEST FAILED")
        print("="*80 + "\n")
        return False

if __name__ == "__main__":
    test_connection()
