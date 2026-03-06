#!/usr/bin/env python3
"""
Diagnostic script to check if SQL Server is running and accessible.
This helps identify the root cause of connection hangs.
"""

import sys
import socket
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_port_open(host, port, timeout=2):
    """Check if a port is open on the given host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"Error checking port: {e}")
        return False

def check_sqlserver_service():
    """Check if SQL Server service is running on Windows"""
    try:
        # Try to get SQL Server service status
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Service -Name "MSSQL*" | Select-Object Name, Status'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("SQL Server Services:")
            logger.info(result.stdout)
            return True
        else:
            logger.warning("Could not query SQL Server services")
            return False
    except Exception as e:
        logger.error(f"Error checking SQL Server service: {e}")
        return False

def test_pyodbc_connection(host, database, user, password):
    """Test connection using pyodbc directly"""
    try:
        import pyodbc
        
        # Normalize server name
        server = host
        if server == ".":
            server = "(local)"
        
        logger.info(f"\nTesting pyodbc connection to {server}\\{database}...")
        
        # Try Windows auth first
        try:
            logger.info("  Attempting Windows authentication...")
            conn_str = (
                f"Driver={{ODBC Driver 18 for SQL Server}};"
                f"Server={server};"
                f"Database={database};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes"
            )
            conn = pyodbc.connect(conn_str, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            logger.info(f"  ✓ Windows auth successful! SQL Server version: {version[0][:50]}...")
            conn.close()
            return True
        except Exception as e:
            logger.warning(f"  ✗ Windows auth failed: {e}")
        
        # Try SQL auth
        if user and password:
            try:
                logger.info("  Attempting SQL authentication...")
                conn_str = (
                    f"Driver={{ODBC Driver 18 for SQL Server}};"
                    f"Server={server};"
                    f"Database={database};"
                    f"UID={user};"
                    f"PWD={password};"
                    f"TrustServerCertificate=yes"
                )
                conn = pyodbc.connect(conn_str, timeout=5)
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()
                logger.info(f"  ✓ SQL auth successful! SQL Server version: {version[0][:50]}...")
                conn.close()
                return True
            except Exception as e:
                logger.warning(f"  ✗ SQL auth failed: {e}")
        
        return False
    
    except ImportError:
        logger.error("pyodbc not installed. Install with: pip install pyodbc")
        return False
    except Exception as e:
        logger.error(f"Error testing pyodbc connection: {e}")
        return False

def main():
    logger.info("=" * 80)
    logger.info("SQL SERVER DIAGNOSTIC CHECK")
    logger.info("=" * 80)
    
    # Check if ODBC driver is installed
    logger.info("\n1. Checking ODBC Driver 18 for SQL Server...")
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        odbc_driver = [d for d in drivers if 'ODBC Driver 18 for SQL Server' in d]
        if odbc_driver:
            logger.info(f"  ✓ Found: {odbc_driver[0]}")
        else:
            logger.warning(f"  ✗ ODBC Driver 18 not found. Available drivers: {drivers}")
    except Exception as e:
        logger.error(f"  ✗ Error checking ODBC drivers: {e}")
    
    # Check if port 1433 is open
    logger.info("\n2. Checking if SQL Server port (1433) is open...")
    if check_port_open("localhost", 1433, timeout=3):
        logger.info("  ✓ Port 1433 is open")
    else:
        logger.warning("  ✗ Port 1433 is NOT open (SQL Server may not be running)")
    
    # Check SQL Server service status
    logger.info("\n3. Checking SQL Server service status...")
    check_sqlserver_service()
    
    # Test connection
    logger.info("\n4. Testing database connection...")
    host = "localhost"
    database = "AdventureWorks2022"
    user = "sa"
    password = input("Enter SQL Server 'sa' password (or press Enter to skip): ").strip()
    
    if password:
        test_pyodbc_connection(host, database, user, password)
    else:
        logger.info("  Skipping connection test (no password provided)")
    
    logger.info("\n" + "=" * 80)
    logger.info("DIAGNOSTIC CHECK COMPLETE")
    logger.info("=" * 80)
    logger.info("\nIf SQL Server is not running:")
    logger.info("  1. Open Services (services.msc)")
    logger.info("  2. Find 'SQL Server (MSSQLSERVER)' or similar")
    logger.info("  3. Right-click and select 'Start'")
    logger.info("\nIf port 1433 is not open:")
    logger.info("  1. Check Windows Firewall settings")
    logger.info("  2. Allow SQL Server through the firewall")
    logger.info("  3. Restart SQL Server service")

if __name__ == "__main__":
    main()
