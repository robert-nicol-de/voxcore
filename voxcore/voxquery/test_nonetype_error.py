#!/usr/bin/env python3
"""Test script to reproduce the NoneType subscripting error"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from voxquery.core.engine import VoxQueryEngine
from voxquery.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)
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
    logger.info(f"Schema cache size: {len(engine.schema_analyzer.schema_cache)}")
    
    # Try to ask a question
    logger.info("\nAsking question: 'Show me top 10 accounts by balance'")
    result = engine.ask(
        question="Show me top 10 accounts by balance",
        execute=False,
        dry_run=False,
    )
    
    logger.info(f"Result: {result}")
    
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    import traceback
    traceback.print_exc()
