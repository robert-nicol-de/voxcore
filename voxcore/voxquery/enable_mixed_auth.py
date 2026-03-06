#!/usr/bin/env python3
"""Enable Mixed Authentication Mode in SQL Server"""

import pyodbc
import subprocess
import time

def enable_mixed_auth():
    """Enable Mixed Authentication Mode"""
    print("\n" + "="*80)
    print("Enabling Mixed Authentication Mode in SQL Server")
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
        
        # Check current login mode
        cursor.execute("""
            SELECT SERVERPROPERTY('LoginMode') AS LoginMode
        """)
        
        login_mode = cursor.fetchone()[0]
        print(f"Current Login Mode: {login_mode}")
        if login_mode == 1:
            print("  Mode: Windows Authentication only")
        elif login_mode == 2:
            print("  Mode: SQL Server and Windows Authentication (Mixed)")
        
        # Enable Mixed Authentication Mode using registry
        print("\nEnabling Mixed Authentication Mode...")
        
        # Use PowerShell to modify registry
        ps_command = """
        $regPath = 'HKLM:\\Software\\Microsoft\\MSSQLServer\\MSSQLServer'
        $regValue = 'LoginMode'
        
        # 1 = Windows Auth only, 2 = Mixed Auth
        Set-ItemProperty -Path $regPath -Name $regValue -Value 2
        
        Write-Host "✓ Registry updated to enable Mixed Authentication"
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print("\n⚠️  SQL Server needs to be restarted for changes to take effect")
            print("Restarting SQL Server...")
            
            # Restart SQL Server
            subprocess.run(
                ["powershell", "-Command", "Restart-Service -Name MSSQLSERVER -Force"],
                capture_output=True
            )
            
            print("✓ SQL Server restarted")
            time.sleep(3)  # Wait for service to restart
            
            print("\n" + "="*80)
            print("✓ MIXED AUTHENTICATION MODE ENABLED")
            print("="*80 + "\n")
            return True
        else:
            print(f"✗ Failed to update registry: {result.stderr}")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

if __name__ == "__main__":
    enable_mixed_auth()
