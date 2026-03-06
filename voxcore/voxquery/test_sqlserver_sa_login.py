#!/usr/bin/env python3
"""Test SQL Server 'sa' account login"""

import pyodbc
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("SQL SERVER 'SA' ACCOUNT LOGIN TEST")
logger.info("=" * 60)

# Test credentials
host = "localhost"
database = "AdventureWorks2022"
user = "sa"
password = input("Enter 'sa' password: ").strip()

if not password:
    logger.error("Password required")
    exit(1)

logger.info(f"\nTesting login with:")
logger.info(f"  Host: {host}")
logger.info(f"  Database: {database}")
logger.info(f"  User: {user}")
logger.info(f"  Password: {'*' * len(password)}")

# Try connection
try:
    logger.info("\nAttempting connection...")
    conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={host};"
        f"Database={database};"
        f"UID={user};"
        f"PWD={password};"
        f"TrustServerCertificate=yes"
    )
    
    conn = pyodbc.connect(conn_str, timeout=5)
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()
    
    logger.info(f"✓ LOGIN SUCCESSFUL!")
    logger.info(f"  SQL Server version: {version[0][:80]}...")
    
    # Check if 'sa' is enabled
    cursor.execute("SELECT name, is_disabled FROM sys.sql_logins WHERE name = 'sa'")
    result = cursor.fetchone()
    if result:
        name, is_disabled = result
        logger.info(f"\n'sa' Account Status:")
        logger.info(f"  Name: {name}")
        logger.info(f"  Disabled: {is_disabled}")
        if is_disabled:
            logger.warning("  ⚠️  'sa' account is DISABLED!")
        else:
            logger.info("  ✓ 'sa' account is ENABLED")
    
    conn.close()

except pyodbc.Error as e:
    logger.error(f"✗ LOGIN FAILED!")
    logger.error(f"  Error: {e}")
    logger.error(f"\nPossible causes:")
    logger.error(f"  1. Wrong password")
    logger.error(f"  2. 'sa' account is disabled")
    logger.error(f"  3. SQL authentication not enabled")
    logger.error(f"  4. SQL Server not running")

logger.info("\n" + "=" * 60)
