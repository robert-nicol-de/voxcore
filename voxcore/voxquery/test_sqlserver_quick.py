#!/usr/bin/env python3
"""Quick SQL Server diagnostic - non-interactive"""

import socket
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_port_open(host, port, timeout=2):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

logger.info("=" * 60)
logger.info("SQL SERVER QUICK DIAGNOSTIC")
logger.info("=" * 60)

# Check port
logger.info("\nChecking if SQL Server port (1433) is open...")
if check_port_open("localhost", 1433, timeout=3):
    logger.info("✓ Port 1433 is OPEN - SQL Server is likely running")
else:
    logger.info("✗ Port 1433 is CLOSED - SQL Server is NOT running")
    logger.info("\nTo fix:")
    logger.info("  1. Open Services (services.msc)")
    logger.info("  2. Find 'SQL Server (MSSQLSERVER)'")
    logger.info("  3. Right-click and select 'Start'")

# Check ODBC driver
logger.info("\nChecking ODBC Driver 18...")
try:
    import pyodbc
    drivers = pyodbc.drivers()
    if any('ODBC Driver 18 for SQL Server' in d for d in drivers):
        logger.info("✓ ODBC Driver 18 is installed")
    else:
        logger.info("✗ ODBC Driver 18 NOT found")
        logger.info(f"  Available: {drivers}")
except Exception as e:
    logger.error(f"✗ Error: {e}")

logger.info("\n" + "=" * 60)
