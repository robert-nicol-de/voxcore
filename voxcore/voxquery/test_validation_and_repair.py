#!/usr/bin/env python3
"""Test SQL validation and auto-repair logic"""

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

# Test cases for validation and repair
TEST_CASES = [
    {
        "name": "Pattern 1: Multiple FROM clauses",
        "sql": """SELECT COUNT(DISTINCT Object) AS unique_objects,
                 AVG(modification_count) AS average_modifications
          FROM (
              FROM DatabaseLog
              (Object, COUNT(*) AS modification_count)
              FROM DatabaseLog
              GROUP BY Object
              WHERE Object IS NOT NULL
          ) AS modifications""",
        "should_fail_validation": True,
        "should_repair": True,
        "description": "Bare FROM and floating column list - should trigger Pattern A repair"
    },
    {
        "name": "Pattern 2: Floating column list",
        "sql": """SELECT col1, col2
          FROM (col1, col2) FROM table1
          WHERE col1 > 10""",
        "should_fail_validation": True,
        "should_repair": False,
        "description": "Floating column list - should fail validation"
    },
    {
        "name": "Pattern 3: GROUP BY after subquery alias",
        "sql": """SELECT col1, COUNT(*) FROM (
              SELECT col1 FROM table1
          ) AS t GROUP BY col1""",
        "should_fail_validation": True,
        "should_repair": False,
        "description": "GROUP BY after alias - should fail validation"
    },
    {
        "name": "Pattern B: UNION ALL with aggregates",
        "sql": """SELECT COUNT(DISTINCT Object) AS unique_objects
          FROM DatabaseLog
          UNION ALL
          SELECT AVG(modification_count) AS average_modifications
          FROM DatabaseLog""",
        "should_fail_validation": True,
        "should_repair": True,
        "description": "UNION ALL with aggregates - should trigger Pattern B repair"
    },
    {
        "name": "Valid SQL (no changes)",
        "sql": """SELECT col1, COUNT(*) as cnt
          FROM table1
          WHERE col1 > 10
          GROUP BY col1""",
        "should_fail_validation": False,
        "should_repair": False,
        "description": "Valid SQL - should pass validation"
    },
    {
        "name": "Correct CTE structure",
        "sql": """WITH per_group AS (
              SELECT Object, COUNT(*) AS modification_count
              FROM DatabaseLog
              WHERE Object IS NOT NULL
              GROUP BY Object
          )
          SELECT
              COUNT(*) AS unique_objects,
              AVG(1.0 * modification_count) AS average_modifications
          FROM per_group""",
        "should_fail_validation": False,
        "should_repair": False,
        "description": "Correct CTE structure - should pass validation"
    },
]

def test_validation_and_repair():
    """Test validation and repair logic"""
    
    # Create a dummy engine (won't be used for validation tests)
    engine = create_engine("sqlite:///:memory:")
    generator = SQLGenerator(engine, dialect="sqlserver")
    
    logger.info("=" * 80)
    logger.info("SQL VALIDATION AND REPAIR TEST SUITE")
    logger.info("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(TEST_CASES, 1):
        logger.info(f"\n{'─' * 80}")
        logger.info(f"Test {i}: {test['name']}")
        logger.info(f"Description: {test['description']}")
        logger.info(f"Input SQL:\n{test['sql'][:100]}...")
        
        try:
            # Step 1: Validate
            is_valid, error_reason = generator._validate_sql(test['sql'], "sqlserver")
            
            logger.info(f"Validation result: {'✓ PASS' if is_valid else '✗ FAIL'}")
            if error_reason:
                logger.info(f"Error reason: {error_reason}")
            
            # Check if validation result matches expectation
            if is_valid == (not test['should_fail_validation']):
                logger.info("✓ Validation result matches expectation")
            else:
                logger.error(f"✗ Validation result mismatch!")
                logger.error(f"  Expected: {'FAIL' if test['should_fail_validation'] else 'PASS'}")
                logger.error(f"  Got: {'FAIL' if not is_valid else 'PASS'}")
                failed += 1
                continue
            
            # Step 2: Try repair if validation failed
            if not is_valid and test['should_repair']:
                logger.info("Attempting auto-repair...")
                repaired = generator._attempt_auto_repair(test['sql'], "test question")
                
                if repaired:
                    logger.info(f"✓ Auto-repair succeeded")
                    logger.info(f"Repaired SQL:\n{repaired[:100]}...")
                    
                    # Re-validate
                    is_valid_after, error_after = generator._validate_sql(repaired, "sqlserver")
                    logger.info(f"Re-validation after repair: {'✓ PASS' if is_valid_after else '✗ FAIL'}")
                    
                    if is_valid_after:
                        logger.info("✓ PASSED - Repair successful")
                        passed += 1
                    else:
                        logger.error(f"✗ FAILED - Repaired SQL still invalid: {error_after}")
                        failed += 1
                else:
                    logger.error("✗ Auto-repair returned None")
                    if test['should_repair']:
                        logger.error("✗ FAILED - Expected repair to succeed")
                        failed += 1
                    else:
                        logger.info("✓ PASSED - Repair correctly returned None")
                        passed += 1
            elif not is_valid and not test['should_repair']:
                logger.info("✓ PASSED - Validation correctly failed (no repair expected)")
                passed += 1
            elif is_valid and not test['should_fail_validation']:
                logger.info("✓ PASSED - Validation correctly passed")
                passed += 1
            else:
                logger.error("✗ FAILED - Unexpected state")
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
    success = test_validation_and_repair()
    sys.exit(0 if success else 1)
