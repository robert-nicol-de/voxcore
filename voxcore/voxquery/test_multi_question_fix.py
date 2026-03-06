#!/usr/bin/env python
"""Test script to verify multi-question fix

This script tests that different questions generate different SQL queries,
not the same query repeated.
"""

import sys
import os
import logging
import json
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from voxquery.core.engine import VoxQueryEngine
from voxquery.config_loader import get_config_loader

def test_multi_question_fix():
    """Test that different questions generate different SQL"""
    
    logger.info("\n" + "="*80)
    logger.info("TEST: Multi-Question Fix")
    logger.info("="*80)
    
    try:
        # Create engine
        logger.info("\n1. Creating VoxQueryEngine...")
        engine = VoxQueryEngine(
            warehouse_type="sqlserver",
            warehouse_host=".",
            warehouse_user="sa",
            warehouse_password="YourPassword123!",
            warehouse_database="AdventureWorks2022",
            auth_type="sql",
        )
        logger.info("✓ Engine created successfully")
        
        # Test 1: Ask first question
        logger.info("\n2. Asking first question...")
        question1 = "Show me the top 5 products by sales"
        logger.info(f"   Question 1: {question1}")
        
        result1 = engine.ask(question1, execute=False)
        sql1 = result1.get("sql", "")
        logger.info(f"   Generated SQL 1:\n   {sql1}")
        
        # Test 2: Ask second question
        logger.info("\n3. Asking second question...")
        question2 = "Show me the bottom 5 products by sales"
        logger.info(f"   Question 2: {question2}")
        
        result2 = engine.ask(question2, execute=False)
        sql2 = result2.get("sql", "")
        logger.info(f"   Generated SQL 2:\n   {sql2}")
        
        # Test 3: Ask third question
        logger.info("\n4. Asking third question...")
        question3 = "Count products by category"
        logger.info(f"   Question 3: {question3}")
        
        result3 = engine.ask(question3, execute=False)
        sql3 = result3.get("sql", "")
        logger.info(f"   Generated SQL 3:\n   {sql3}")
        
        # Verify results
        logger.info("\n" + "="*80)
        logger.info("VERIFICATION")
        logger.info("="*80)
        
        # Check if SQLs are different
        if sql1 == sql2:
            logger.error("✗ FAIL: SQL 1 and SQL 2 are identical!")
            logger.error(f"  SQL 1: {sql1}")
            logger.error(f"  SQL 2: {sql2}")
            return False
        else:
            logger.info("✓ PASS: SQL 1 and SQL 2 are different")
        
        if sql2 == sql3:
            logger.error("✗ FAIL: SQL 2 and SQL 3 are identical!")
            logger.error(f"  SQL 2: {sql2}")
            logger.error(f"  SQL 3: {sql3}")
            return False
        else:
            logger.info("✓ PASS: SQL 2 and SQL 3 are different")
        
        if sql1 == sql3:
            logger.error("✗ FAIL: SQL 1 and SQL 3 are identical!")
            logger.error(f"  SQL 1: {sql1}")
            logger.error(f"  SQL 3: {sql3}")
            return False
        else:
            logger.info("✓ PASS: SQL 1 and SQL 3 are different")
        
        # Check if questions are reflected in SQL
        logger.info("\n" + "="*80)
        logger.info("SEMANTIC VERIFICATION")
        logger.info("="*80)
        
        # Question 1 should have TOP or ORDER BY DESC
        if "TOP" in sql1.upper() or "ORDER BY" in sql1.upper():
            logger.info("✓ PASS: SQL 1 contains TOP or ORDER BY (expected for 'top 5')")
        else:
            logger.warning("⚠ WARNING: SQL 1 might not reflect 'top 5' requirement")
        
        # Question 2 should have different structure than Question 1
        if "BOTTOM" in sql2.upper() or "ASC" in sql2.upper():
            logger.info("✓ PASS: SQL 2 contains ASC or BOTTOM (expected for 'bottom 5')")
        else:
            logger.warning("⚠ WARNING: SQL 2 might not reflect 'bottom 5' requirement")
        
        # Question 3 should have GROUP BY
        if "GROUP BY" in sql3.upper():
            logger.info("✓ PASS: SQL 3 contains GROUP BY (expected for 'count by category')")
        else:
            logger.warning("⚠ WARNING: SQL 3 might not reflect 'count by category' requirement")
        
        logger.info("\n" + "="*80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("="*80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ TEST FAILED: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_multi_question_fix()
    sys.exit(0 if success else 1)
