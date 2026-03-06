#!/usr/bin/env python3
"""Test SQL validation and auto-fix logic"""

import sys
import logging
from voxquery.core.sql_generator import SQLGenerator
from sqlalchemy import create_engine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test cases for SQL validation
TEST_CASES = [
    {
        "name": "Bare FROM in subquery (CRITICAL)",
        "input": """SELECT COUNT(DISTINCT Object) AS unique_objects,
        AVG(modification_count) AS average_modifications
FROM (
    FROM DatabaseLog
    (Object, COUNT(*) AS modification_count)
    FROM DatabaseLog
    GROUP BY Object
    WHERE Object IS NOT NULL
) AS modifications""",
        "expected_pattern": "SELECT.*FROM.*SELECT.*FROM.*DatabaseLog",
        "description": "Should fix bare FROM and floating column list"
    },
    {
        "name": "Leading UNION ALL",
        "input": "UNION ALL SELECT * FROM table1",
        "expected_pattern": "^SELECT",
        "description": "Should remove leading UNION ALL"
    },
    {
        "name": "Floating column list",
        "input": "SELECT * FROM (col1, col2) FROM table1 WHERE col1 > 10",
        "expected_pattern": "SELECT.*col1.*col2.*FROM.*table1",
        "description": "Should fix floating column list"
    },
    {
        "name": "Incomplete UNION ALL",
        "input": "SELECT col1 FROM table1 UNION ALL",
        "expected_pattern": "SELECT.*FROM.*table1",
        "description": "Should remove incomplete UNION ALL"
    },
    {
        "name": "Valid SQL (no changes)",
        "input": "SELECT col1, COUNT(*) FROM table1 GROUP BY col1",
        "expected_pattern": "SELECT.*col1.*COUNT.*FROM.*table1.*GROUP BY",
        "description": "Should not modify valid SQL"
    },
    {
        "name": "Correct subquery structure",
        "input": """SELECT COUNT(DISTINCT Object) AS unique_objects,
        AVG(1.0 * modification_count) AS average_modifications
FROM (
    SELECT Object, COUNT(*) AS modification_count
    FROM DatabaseLog
    WHERE Object IS NOT NULL
    GROUP BY Object
) t""",
        "expected_pattern": "SELECT.*COUNT.*DISTINCT.*FROM.*SELECT.*Object.*COUNT.*FROM.*DatabaseLog",
        "description": "Should not modify correct subquery"
    },
]

def test_sql_validation():
    """Test SQL validation fixes"""
    
    # Create a dummy engine (won't be used for validation tests)
    engine = create_engine("sqlite:///:memory:")
    generator = SQLGenerator(engine, dialect="sqlserver")
    
    logger.info("=" * 80)
    logger.info("SQL VALIDATION TEST SUITE")
    logger.info("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(TEST_CASES, 1):
        logger.info(f"\nTest {i}: {test['name']}")
        logger.info(f"Description: {test['description']}")
        logger.info(f"Input:\n{test['input'][:100]}...")
        
        try:
            # Run validation
            result = generator._validate_sql(test['input'])
            
            logger.info(f"Output:\n{result[:100]}...")
            
            # Check if result matches expected pattern
            import re
            if re.search(test['expected_pattern'], result, re.IGNORECASE | re.DOTALL):
                logger.info("✓ PASSED")
                passed += 1
            else:
                logger.error(f"✗ FAILED - Output doesn't match expected pattern")
                logger.error(f"Expected pattern: {test['expected_pattern']}")
                logger.error(f"Got: {result}")
                failed += 1
        except Exception as e:
            logger.error(f"✗ FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    logger.info("\n" + "=" * 80)
    logger.info(f"RESULTS: {passed} passed, {failed} failed out of {len(TEST_CASES)} tests")
    logger.info("=" * 80)
    
    return failed == 0

if __name__ == "__main__":
    success = test_sql_validation()
    sys.exit(0 if success else 1)
