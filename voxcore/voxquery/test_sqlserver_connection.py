#!/usr/bin/env python3
"""
Comprehensive SQL Server connection test suite
Run this to validate SQL Server connectivity before starting VoxQuery
"""

import sys
import pyodbc
import logging
from typing import Tuple, Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_odbc_drivers() -> bool:
    """Test 1: Check if ODBC drivers are available"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Checking ODBC Drivers")
    logger.info("="*80)
    
    drivers = pyodbc.drivers()
    logger.info(f"Found {len(drivers)} ODBC drivers:")
    
    required_drivers = [
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 18 for SQL Server",
        "SQL Server",
    ]
    
    found_drivers = []
    for driver in drivers:
        logger.info(f"  - {driver}")
        if any(req in driver for req in required_drivers):
            found_drivers.append(driver)
    
    if found_drivers:
        logger.info(f"✓ Found compatible driver: {found_drivers[0]}")
        return True
    else:
        logger.error("✗ No compatible SQL Server ODBC drivers found!")
        logger.error("  Install: ODBC Driver 17 for SQL Server or later")
        return False


def test_direct_pyodbc(server: str, database: str, auth_type: str = "windows") -> Tuple[bool, Optional[str]]:
    """Test 2: Direct pyodbc connection"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Direct pyodbc Connection")
    logger.info("="*80)
    
    # Normalize server name
    if server == ".":
        server = "(local)"
    
    conn_str = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Trusted_Connection=yes"
    )
    
    logger.info(f"Connection String: {conn_str}")
    
    try:
        conn = pyodbc.connect(conn_str, autocommit=True, unicode_results=True)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        conn.close()
        
        logger.info(f"✓ Direct pyodbc connection succeeded")
        logger.info(f"  SQL Server Version: {version[:60]}...")
        return True, version
    except Exception as e:
        logger.error(f"✗ Direct pyodbc connection failed: {e}")
        return False, str(e)


def test_sqlalchemy_connection(server: str, database: str, auth_type: str = "windows") -> bool:
    """Test 3: SQLAlchemy mssql+pyodbc connection"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: SQLAlchemy mssql+pyodbc Connection")
    logger.info("="*80)
    
    try:
        from sqlalchemy import create_engine, text
        
        # Normalize server name
        if server == ".":
            server = "(local)"
        
        if auth_type == "windows":
            connection_url = (
                f"mssql+pyodbc:///?odbc_connect="
                f"Driver={{ODBC Driver 17 for SQL Server}};"
                f"Server={server};"
                f"Database={database};"
                f"Trusted_Connection=yes"
            )
        else:
            logger.error("SQL authentication test not implemented")
            return False
        
        logger.info(f"SQLAlchemy URL: {connection_url[:80]}...")
        
        engine = create_engine(connection_url, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.scalar()
            logger.info(f"✓ SQLAlchemy connection succeeded")
            logger.info(f"  SQL Server Version: {version[:60]}...")
        
        engine.dispose()
        return True
    
    except Exception as e:
        logger.error(f"✗ SQLAlchemy connection failed: {e}")
        return False


def test_schema_access(server: str, database: str) -> bool:
    """Test 4: Schema access and table enumeration"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Schema Access")
    logger.info("="*80)
    
    try:
        from sqlalchemy import create_engine, text, inspect
        
        # Normalize server name
        if server == ".":
            server = "(local)"
        
        connection_url = (
            f"mssql+pyodbc:///?odbc_connect="
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server={server};"
            f"Database={database};"
            f"Trusted_Connection=yes"
        )
        
        engine = create_engine(connection_url, echo=False)
        inspector = inspect(engine)
        
        tables = inspector.get_table_names()
        logger.info(f"✓ Schema access succeeded")
        logger.info(f"  Found {len(tables)} tables")
        
        if tables:
            logger.info(f"  Sample tables: {', '.join(tables[:5])}")
        
        engine.dispose()
        return True
    
    except Exception as e:
        logger.error(f"✗ Schema access failed: {e}")
        return False


def run_all_tests(server: str = "(local)", database: str = "VoxQueryTrainingFin2025") -> bool:
    """Run all connection tests"""
    logger.info("\n" + "="*80)
    logger.info("SQL SERVER CONNECTION TEST SUITE")
    logger.info("="*80)
    logger.info(f"Server: {server}")
    logger.info(f"Database: {database}")
    
    results = []
    
    # Test 1: ODBC Drivers
    results.append(("ODBC Drivers", test_odbc_drivers()))
    
    # Test 2: Direct pyodbc
    success, version = test_direct_pyodbc(server, database)
    results.append(("Direct pyodbc", success))
    
    # Test 3: SQLAlchemy
    results.append(("SQLAlchemy mssql+pyodbc", test_sqlalchemy_connection(server, database)))
    
    # Test 4: Schema Access
    results.append(("Schema Access", test_schema_access(server, database)))
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✓ All tests passed! SQL Server connection is ready.")
        return True
    else:
        logger.error("\n✗ Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    server = sys.argv[1] if len(sys.argv) > 1 else "(local)"
    database = sys.argv[2] if len(sys.argv) > 2 else "VoxQueryTrainingFin2025"
    
    success = run_all_tests(server, database)
    sys.exit(0 if success else 1)
