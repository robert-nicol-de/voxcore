#!/usr/bin/env python3
"""Enable SQL Server sa account"""

import pyodbc

def enable_sa_account():
    """Enable the sa account"""
    print("\n" + "="*80)
    print("Enabling SQL Server sa Account")
    print("="*80 + "\n")
    
    # Connect with Windows Auth
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost;"
        "Database=master;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
        "Encrypt=no;"
    )
    
    try:
        print("Connecting to SQL Server with Windows Authentication...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Enable sa account
        print("Executing: ALTER LOGIN sa ENABLE;")
        cursor.execute("ALTER LOGIN sa ENABLE;")
        conn.commit()
        print("✓ sa account enabled successfully!")
        
        # Verify it's enabled
        cursor.execute("""
            SELECT name, is_disabled 
            FROM sys.sql_logins 
            WHERE name = 'sa'
        """)
        
        result = cursor.fetchone()
        if result:
            name, is_disabled = result
            print(f"\n✓ Verification:")
            print(f"  Name: {name}")
            print(f"  Is Disabled: {is_disabled}")
            
            if not is_disabled:
                print("\n✓ sa account is now ENABLED!")
            else:
                print("\n✗ sa account is still disabled")
        
        conn.close()
        
        print("\n" + "="*80)
        print("✓ SA ACCOUNT ENABLED SUCCESSFULLY")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        print("\n" + "="*80)
        print("✗ FAILED TO ENABLE SA ACCOUNT")
        print("="*80 + "\n")
        return False

if __name__ == "__main__":
    enable_sa_account()
