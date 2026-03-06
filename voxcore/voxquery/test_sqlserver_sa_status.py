#!/usr/bin/env python3
"""Check SQL Server sa account status"""

import pyodbc

def check_sa_status():
    """Check if sa account is enabled"""
    print("\n" + "="*80)
    print("Checking SQL Server sa Account Status")
    print("="*80 + "\n")
    
    # First, try to connect with Windows Auth to check sa status
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost;"
        "Database=master;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
        "Encrypt=no;"
    )
    
    try:
        print("Connecting with Windows Authentication to check sa status...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Check if sa account exists and is enabled
        cursor.execute("""
            SELECT name, is_disabled 
            FROM sys.sql_logins 
            WHERE name = 'sa'
        """)
        
        result = cursor.fetchone()
        if result:
            name, is_disabled = result
            print(f"\n✓ Found sa account:")
            print(f"  Name: {name}")
            print(f"  Is Disabled: {is_disabled}")
            
            if is_disabled:
                print("\n⚠️  WARNING: sa account is DISABLED!")
                print("You need to enable it with:")
                print("  ALTER LOGIN sa ENABLE;")
            else:
                print("\n✓ sa account is ENABLED")
        else:
            print("\n✗ sa account not found!")
        
        # Check SQL Server authentication mode
        cursor.execute("""
            SELECT SERVERPROPERTY('LoginMode') AS LoginMode
        """)
        
        login_mode = cursor.fetchone()[0]
        print(f"\nSQL Server Login Mode: {login_mode}")
        if login_mode == 1:
            print("  Mode: Windows Authentication only")
        elif login_mode == 2:
            print("  Mode: SQL Server and Windows Authentication")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Failed to connect: {e}")

if __name__ == "__main__":
    check_sa_status()
