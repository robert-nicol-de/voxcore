# Week 1: Syntactic & Semantic Validation Layer Implementation

**Status**: Ready to implement  
**Timeline**: 3-5 days  
**Expected Accuracy Gain**: 75-85% → 80-85% (catch broken SQL + dangerous queries)  
**Effort**: ~8-12 hours engineering  

---

## CURRENT STATE (Layer 1 Only)

✅ **Layer 1: Prompt + Few-Shot** (DEPLOYED)
- Aggressive finance domain rules
- Explicit table forbidding
- Expected accuracy: 75-85% on revenue queries

❌ **Layers 2-7**: Not implemented yet

---

## WEEK 1 GOAL: Implement Layers 3 & 4

### Layer 3: Syntactic Validation
**Purpose**: Catch broken SQL before execution  
**Tool**: sqlglot parser  
**Expected catch rate**: 60-70% of broken SQL  

### Layer 4: Semantic Validation
**Purpose**: Catch dangerous/wrong intent  
**Tool**: Custom risk scoring  
**Expected catch rate**: 40-50% of dangerous queries  

---

## IMPLEMENTATION PLAN

### Step 1: Create SQL Validator Module (1-2 hours)

**File**: `voxcore/voxquery/voxquery/core/sql_validator.py`

```python
import sqlglot
from typing import Tuple, Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class SQLValidator:
    """Validates SQL for syntax, safety, and semantic correctness"""
    
    def __init__(self, dialect: str = "sqlserver"):
        self.dialect = dialect
        self.max_rows = 1000
        self.forbidden_tables = {
            "PersonPhone", "PhoneNumberType", "AWBuildVersion",
            "ProductPhoto", "Document", "Department", "ScrapReason"
        }
    
    def validate(self, sql: str, question: str) -> Tuple[bool, Optional[str], Dict]:
        """
        Validate SQL query
        
        Returns:
            (is_valid, error_message, metadata)
        """
        metadata = {
            "syntax_valid": False,
            "semantic_valid": False,
            "risk_score": 0.0,
            "issues": []
        }
        
        # Step 1: Syntactic validation
        syntax_valid, syntax_error = self._validate_syntax(sql)
        metadata["syntax_valid"] = syntax_valid
        if not syntax_valid:
            metadata["issues"].append(f"Syntax error: {syntax_error}")
            return False, syntax_error, metadata
        
        # Step 2: Semantic validation
        semantic_valid, semantic_error, risk_score = self._validate_semantic(sql, question)
        metadata["semantic_valid"] = semantic_valid
        metadata["risk_score"] = risk_score
        if not semantic_valid:
            metadata["issues"].append(f"Semantic error: {semantic_error}")
            return False, semantic_error, metadata
        
        return True, None, metadata
    
    def _validate_syntax(self, sql: str) -> Tuple[bool, Optional[str]]:
        """Check if SQL is syntactically valid"""
        try:
            parsed = sqlglot.parse_one(sql, read=self.dialect)
            if parsed is None:
                return False, "Failed to parse SQL"
            return True, None
        except Exception as e:
            return False, str(e)
    
    def _validate_semantic(self, sql: str, question: str) -> Tuple[bool, Optional[str], float]:
        """Check for dangerous/wrong intent"""
        try:
            parsed = sqlglot.parse_one(sql, read=self.dialect)
            
            # Check 1: Forbidden tables
            tables = self._extract_tables(parsed)
            forbidden_found = [t for t in tables if any(f in t for f in self.forbidden_tables)]
            if forbidden_found and "revenue" in question.lower():
                return False, f"Forbidden tables for revenue query: {forbidden_found}", 0.1
            
            # Check 2: Row count estimation
            has_limit = self._has_limit(parsed)
            if not has_limit:
                return False, "Query missing TOP/LIMIT clause", 0.2
            
            # Check 3: JOIN explosion detection
            join_count = self._count_joins(parsed)
            if join_count > 5:
                return False, f"Too many JOINs ({join_count}), risk of explosion", 0.3
            
            # Check 4: Aggregation for revenue questions
            if "revenue" in question.lower() or "sales" in question.lower():
                has_aggregation = self._has_aggregation(parsed)
                if not has_aggregation:
                    return False, "Revenue query missing aggregation (SUM/COUNT/AVG)", 0.4
            
            # All checks passed
            risk_score = 0.0
            return True, None, risk_score
            
        except Exception as e:
            logger.error(f"Semantic validation error: {e}")
            return False, f"Validation error: {str(e)}", 0.5
    
    def _extract_tables(self, parsed) -> List[str]:
        """Extract table names from parsed SQL"""
        tables = []
        for table in parsed.find_all(sqlglot.exp.Table):
            tables.append(table.name)
        return tables
    
    def _has_limit(self, parsed) -> bool:
        """Check if query has TOP or LIMIT"""
        limit = parsed.find(sqlglot.exp.Limit)
        return limit is not None
    
    def _count_joins(self, parsed) -> int:
        """Count number of JOINs"""
        joins = list(parsed.find_all(sqlglot.exp.Join))
        return len(joins)
    
    def _has_aggregation(self, parsed) -> bool:
        """Check if query has aggregation functions"""
        agg_functions = {"SUM", "COUNT", "AVG", "MAX", "MIN"}
        for func in parsed.find_all(sqlglot.exp.Func):
            if func.name.upper() in agg_functions:
                return True
        return False
```

### Step 2: Integrate Validator into Query Endpoint (1-2 hours)

**File**: `voxcore/voxquery/voxquery/api/v1/query.py`

Add validation before SQL execution:

```python
from voxquery.core.sql_validator import SQLValidator

validator = SQLValidator(dialect="sqlserver")

@router.post("/query")
async def execute_query(request: QueryRequest):
    """Execute query with validation"""
    
    # Generate SQL
    sql = await sql_generator.generate(request.question)
    
    # Validate SQL (NEW)
    is_valid, error_msg, metadata = validator.validate(sql, request.question)
    
    if not is_valid:
        logger.warning(f"Validation failed: {error_msg}")
        logger.warning(f"Metadata: {metadata}")
        
        # Return error response
        return {
            "error": error_msg,
            "validation_metadata": metadata,
            "fallback_query": "SELECT 1 AS validation_failed"
        }
    
    # Execute validated SQL
    results = await execute_sql(sql)
    return results
```

### Step 3: Add Test Cases (1-2 hours)

**File**: `voxcore/voxquery/tests/test_sql_validator.py`

```python
import pytest
from voxquery.core.sql_validator import SQLValidator

@pytest.fixture
def validator():
    return SQLValidator(dialect="sqlserver")

class TestSyntacticValidation:
    def test_valid_sql(self, validator):
        sql = "SELECT TOP 10 * FROM Sales.Customer"
        is_valid, error, metadata = validator.validate(sql, "show customers")
        assert is_valid
        assert metadata["syntax_valid"]
    
    def test_broken_sql(self, validator):
        sql = "SELECT * FORM Sales.Customer"  # FORM instead of FROM
        is_valid, error, metadata = validator.validate(sql, "show customers")
        assert not is_valid
        assert not metadata["syntax_valid"]

class TestSemanticValidation:
    def test_forbidden_table_revenue_query(self, validator):
        sql = "SELECT * FROM Person.PersonPhone"
        is_valid, error, metadata = validator.validate(sql, "top customers by revenue")
        assert not is_valid
        assert "Forbidden tables" in error
    
    def test_missing_limit(self, validator):
        sql = "SELECT * FROM Sales.Customer"  # No TOP
        is_valid, error, metadata = validator.validate(sql, "show customers")
        assert not is_valid
        assert "TOP/LIMIT" in error
    
    def test_revenue_query_missing_aggregation(self, validator):
        sql = "SELECT TOP 10 CustomerID FROM Sales.SalesOrderHeader"
        is_valid, error, metadata = validator.validate(sql, "top customers by revenue")
        assert not is_valid
        assert "aggregation" in error.lower()
    
    def test_valid_revenue_query(self, validator):
        sql = """
        SELECT TOP 10
            CustomerID,
            SUM(TotalDue) AS total_revenue
        FROM Sales.SalesOrderHeader
        GROUP BY CustomerID
        ORDER BY total_revenue DESC
        """
        is_valid, error, metadata = validator.validate(sql, "top customers by revenue")
        assert is_valid
        assert metadata["semantic_valid"]
```

---

## INTEGRATION CHECKLIST

- [ ] Create `sql_validator.py` with SQLValidator class
- [ ] Add sqlglot to requirements.txt
- [ ] Integrate validator into query endpoint
- [ ] Add validation logging
- [ ] Create test cases
- [ ] Test with broken SQL examples
- [ ] Test with dangerous queries
- [ ] Test with valid queries
- [ ] Restart backend
- [ ] Verify validation catches errors

---

## EXPECTED RESULTS

### Before Validation Layer
```
Query: "Show top 10 customers by revenue"
Generated SQL: SELECT * FROM Person.PersonPhone  ❌ WRONG TABLE
Result: Empty chart, no data
```

### After Validation Layer
```
Query: "Show top 10 customers by revenue"
Generated SQL: SELECT * FROM Person.PersonPhone  ❌ WRONG TABLE
Validation: ❌ CAUGHT - Forbidden table for revenue query
Result: Error message + fallback query
```

---

## NEXT STEPS (Week 2)

### Layer 5: Rewrite Engine
- Fix dialect issues (LIMIT → TOP)
- Inject row limits
- Qualify schemas
- Normalize column names

### Layer 6: Policy Enforcement
- RBAC checks
- Row-level security
- PII masking

---

## QUICK REFERENCE

**Files to Create**:
1. `voxcore/voxquery/voxquery/core/sql_validator.py` (150 lines)
2. `voxcore/voxquery/tests/test_sql_validator.py` (100 lines)

**Files to Modify**:
1. `voxcore/voxquery/voxquery/api/v1/query.py` (add 10 lines)
2. `requirements.txt` (add sqlglot)

**Time Estimate**: 3-5 hours  
**Accuracy Gain**: +5-10% (catch broken SQL + dangerous queries)

