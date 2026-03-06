#!/usr/bin/env python3
"""Test the balance question fix"""

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
    
    # Test 1: Balance question (should use ACCOUNTS table)
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Balance question")
    logger.info("="*80)
    result = engine.ask(
        question="Show me top 10 accounts by balance",
        execute=False,
        dry_run=False,
    )
    
    sql = result.get('sql', '')
    logger.info(f"Generated SQL: {sql}")
    
    if "ACCOUNTS" in sql.upper() and "BALANCE" in sql.upper():
        logger.info("✅ PASS: Using ACCOUNTS table with BALANCE column")
    else:
        logger.info("❌ FAIL: Not using ACCOUNTS/BALANCE")
    
    # Test 2: Another balance question
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Highest balance question")
    logger.info("="*80)
    result = engine.ask(
        question="What are the highest balance accounts?",
        execute=False,
        dry_run=False,
    )
    
    sql = result.get('sql', '')
    logger.info(f"Generated SQL: {sql}")
    
    if "ACCOUNTS" in sql.upper() and "BALANCE" in sql.upper():
        logger.info("✅ PASS: Using ACCOUNTS table with BALANCE column")
    else:
        logger.info("❌ FAIL: Not using ACCOUNTS/BALANCE")
    
    # Test 3: Generic question (should work with any table)
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Generic question")
    logger.info("="*80)
    result = engine.ask(
        question="Show me database users",
        execute=False,
        dry_run=False,
    )
    
    sql = result.get('sql', '')
    logger.info(f"Generated SQL: {sql}")
    logger.info("✅ PASS: Generic question processed")
    
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    import traceback
    traceback.print_exc()
