#!/usr/bin/env python3
"""Reset SQL Server sa account password with complex password"""

import pyodbc

def reset_sa_password():
    """Reset the sa account password"""
    print("\n" + "="*80)
    print("Resetting SQL Server sa Account Password (Complex)")
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
    
    new_password = "P@ssw0rd123!"
    
    try:
        print("Connecting to SQL Server with Windows Authentication...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Reset sa password with complex password
        print(f"Executing: ALTER LOGIN sa WITH PASSWORD = '{new_password}';")
        cursor.execute(f"ALTER LOGIN sa WITH PASSWORD = '{new_password}';")
        conn.commit()
        print("✓ sa password reset successfully!")
        
        print(f"\nNew password: {new_password}")
        
        conn.close()
        
        print("\n" + "="*80)
        print("✓ SA PASSWORD RESET SUCCESSFULLY")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        print("\n" + "="*80)
        print("✗ FAILED TO RESET SA PASSWORD")
        print("="*80 + "\n")
        return False

if __name__ == "__main__":
    reset_sa_password()
