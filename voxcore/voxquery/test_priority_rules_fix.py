#!/usr/bin/env python3
"""Test the updated PRIORITY_RULES for balance questions"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from voxquery.core.engine import VoxQueryEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create engine with SQL Server
try:
    logger.info("Creating VoxQueryEngine for SQL Server...")
    engine = VoxQueryEngine(
        warehouse_type="sqlserver",
        warehouse_host="localhost",
        warehouse_user=None,
        warehouse_password=None,
        warehouse_database="AdventureWorks2022",
        auth_type="windows",
    )
    
    logger.info("Engine created successfully")
    
    # Test 1: Balance question (should use CUSTOMER + SALESORDERHEADER)
    logger.info("\n" + "="*80)
    logger.info("TEST 1: 'Show top 10 accounts by balance'")
    logger.info("="*80)
    result = engine.ask(
        question="Show top 10 accounts by balance",
        execute=False,
        dry_run=False,
    )
    
    sql = result.get('sql', '')
    logger.info(f"Generated SQL:\n{sql}\n")
    
    if "CUSTOMER" in sql.upper() and "SALESORDERHEADER" in sql.upper():
        logger.info("✅ PASS: Using CUSTOMER + SALESORDERHEADER tables")
    else:
        logger.info("❌ FAIL: Not using correct tables")
    
    if "DATABASELOG" not in sql.upper() and "ERRORLOG" not in sql.upper():
        logger.info("✅ PASS: Not using wrong tables (DatabaseLog/ErrorLog)")
    else:
        logger.info("❌ FAIL: Using wrong tables")
    
    # Test 2: Highest balance question
    logger.info("\n" + "="*80)
    logger.info("TEST 2: 'What are the highest balance accounts?'")
    logger.info("="*80)
    result = engine.ask(
        question="What are the highest balance accounts?",
        execute=False,
        dry_run=False,
    )
    
    sql = result.get('sql', '')
    logger.info(f"Generated SQL:\n{sql}\n")
    
    if "CUSTOMER" in sql.upper() and "SALESORDERHEADER" in sql.upper():
        logger.info("✅ PASS: Using CUSTOMER + SALESORDERHEADER tables")
    else:
        logger.info("❌ FAIL: Not using correct tables")
    
    # Test 3: Top customers by balance
    logger.info("\n" + "="*80)
    logger.info("TEST 3: 'Top customers by balance'")
    logger.info("="*80)
    result = engine.ask(
        question="Top customers by balance",
        execute=False,
        dry_run=False,
    )
    
    sql = result.get('sql', '')
    logger.info(f"Generated SQL:\n{sql}\n")
    
    if "CUSTOMER" in sql.upper() and "SALESORDERHEADER" in sql.upper():
        logger.info("✅ PASS: Using CUSTOMER + SALESORDERHEADER tables")
    else:
        logger.info("❌ FAIL: Not using correct tables")
    
    # Test 4: Generic question (should work with any table)
    logger.info("\n" + "="*80)
    logger.info("TEST 4: 'Show me all products'")
    logger.info("="*80)
    result = engine.ask(
        question="Show me all products",
        execute=False,
        dry_run=False,
    )
    
    sql = result.get('sql', '')
    logger.info(f"Generated SQL:\n{sql}\n")
    logger.info("✅ PASS: Generic question processed")
    
    logger.info("\n" + "="*80)
    logger.info("ALL TESTS COMPLETE")
    logger.info("="*80)
    
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    import traceback
    traceback.print_exc()
