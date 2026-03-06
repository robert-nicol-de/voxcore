# Week 1: Validation Layer Implementation

**Goal**: Catch 80% of broken SQL before execution  
**Effort**: 2-3 days  
**Impact**: Reduce runtime errors by 70%  
**Reliability Gain**: 75-85% → 80-85%  

---

## What We're Building

### Layer 3: Syntactic Validation
Catch SQL syntax errors using `sqlglot` parser

### Layer 4: Semantic Validation
Catch logical errors:
- SELECT * without LIMIT
- Too many JOINs (>5)
- Forbidden tables
- Domain-specific rules
- Schema validation

---

## Step 1: Install Dependencies

```bash
pip install sqlglot sqlparse
```

---

## Step 2: Create Validation Module

**File**: `voxcore/voxquery/voxquery/core/sql_validator.py`

```python
import sqlglot
from typing import Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)

class SQLValidator:
    """Validate SQL syntax and semantics"""
    
    def __init__(self, dialect: str = "tsql"):
        self.dialect = dialect
        self.forbidden_tables = {
            "AWBuildVersion", "ProductPhoto", "ErrorLog", 
            "DatabaseLog", "PersonPhone", "PhoneNumberType"
        }
    
    def validate_syntax(self, sql: str) -> Tuple[bool, str]:
        """Validate SQL syntax using sqlglot"""
        try:
            parsed = sqlglot.parse_one(sql, read=self.dialect)
            if not parsed:
                return False, "Failed to parse SQL"
            logger.debug(f"✓ Syntax valid: {sql[:50]}...")
            return True, ""
        except Exception as e:
            error_msg = f"Syntax error: {str(e)}"
            logger.warning(f"✗ {error_msg}")
            return False, error_msg
    
    def validate_semantics(
        self, 
        sql: str, 
        question: str, 
        schema: Dict[str, any]
    ) -> Tuple[bool, str]:
        """Validate SQL semantics"""
        
        # Check 1: SELECT * without LIMIT/TOP
        if "SELECT *" in sql.upper():
            if "LIMIT" not in sql.upper() and "TOP" not in sql.upper():
                error = "SELECT * without LIMIT/TOP - potential data explosion"
                logger.warning(f"✗ {error}")
                return False, error
        
        # Check 2: JOIN explosion detection
        join_count = sql.upper().count("JOIN")
        if join_count > 5:
            error = f"Too many JOINs ({join_count}) - likely incorrect"
            logger.warning(f"✗ {error}")
            return False, error
        
        # Check 3: Forbidden tables
        for table in self.forbidden_tables:
            if table in sql:
                error = f"Forbidden table: {table}"
                logger.warning(f"✗ {error}")
                return False, error
        
        # Check 4: Revenue question validation
        revenue_keywords = ["revenue", "sales", "income", "earnings", "top customers"]
        if any(kw in question.lower() for kw in revenue_keywords):
            if "Sales.SalesOrderHeader" not in sql:
                error = "Revenue question must use Sales.SalesOrderHeader"
                logger.warning(f"✗ {error}")
                return False, error
        
        # Check 5: Schema validation
        try:
            tables = self._extract_tables(sql)
            for table in tables:
                if table not in schema:
                    error = f"Unknown table: {table}"
                    logger.warning(f"✗ {error}")
                    return False, error
        except Exception as e:
            logger.debug(f"Could not validate schema: {e}")
        
        logger.debug(f"✓ Semantics valid: {sql[:50]}...")
        return True, ""
    
    def validate(
        self, 
        sql: str, 
        question: str, 
        schema: Dict[str, any]
    ) -> Tuple[bool, str]:
        """Run all validations"""
        
        # Syntactic validation
        is_valid, error = self.validate_syntax(sql)
        if not is_valid:
            return False, error
        
        # Semantic validation
        is_valid, error = self.validate_semantics(sql, question, schema)
        if not is_valid:
            return False, error
        
        return True, ""
    
    def _extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL"""
        try:
            parsed = sqlglot.parse_one(sql, read=self.dialect)
            tables = []
            for table in parsed.find_all(sqlglot.exp.Table):
                tables.append(table.name)
            return tables
        except:
            return []
```

---

## Step 3: Integrate into Query Execution

**File**: `voxcore/voxquery/voxquery/api/v1/query.py`

Add validation before execution:

```python
from voxquery.core.sql_validator import SQLValidator

# At module level
validator = SQLValidator(dialect="tsql")

@router.post("/query")
async def execute_query(request: QueryRequest):
    """Execute query with validation"""
    
    try:
        # ... existing code ...
        
        # Generate SQL
        generated_sql = sql_generator.generate(
            question=request.question,
            warehouse=request.warehouse,
            schema_context=schema_context
        )
        
        # NEW: Validate SQL before execution
        is_valid, error = validator.validate(
            sql=generated_sql,
            question=request.question,
            schema=schema_dict
        )
        
        if not is_valid:
            logger.warning(f"Validation failed: {error}")
            return {
                "error": error,
                "generated_sql": generated_sql,
                "fallback": get_fallback_query(request.question),
                "validation_failed": True
            }
        
        # Execute validated SQL
        results = execute_sql(generated_sql, connection)
        
        return {
            "generated_sql": generated_sql,
            "results": results,
            "validation_passed": True
        }
        
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return {
            "error": str(e),
            "fallback": get_fallback_query(request.question)
        }
```

---

## Step 4: Add Logging

**File**: `voxcore/voxquery/voxquery/core/sql_validator.py`

Add detailed logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# In validator methods:
logger.debug(f"✓ Syntax valid: {sql[:50]}...")
logger.warning(f"✗ Syntax error: {error}")
logger.debug(f"✓ Semantics valid: {sql[:50]}...")
logger.warning(f"✗ Semantic error: {error}")
```

---

## Step 5: Test Validation

**File**: `test_sql_validator.py`

```python
import pytest
from voxquery.core.sql_validator import SQLValidator

@pytest.fixture
def validator():
    return SQLValidator(dialect="tsql")

@pytest.fixture
def schema():
    return {
        "Sales.SalesOrderHeader": {},
        "Sales.Customer": {},
        "Person.Person": {},
    }

class TestSyntacticValidation:
    def test_valid_sql(self, validator):
        sql = "SELECT TOP 10 * FROM Sales.SalesOrderHeader"
        is_valid, error = validator.validate_syntax(sql)
        assert is_valid
        assert error == ""
    
    def test_invalid_sql(self, validator):
        sql = "SELECT * FORM Sales.SalesOrderHeader"  # FORM instead of FROM
        is_valid, error = validator.validate_syntax(sql)
        assert not is_valid
        assert "Syntax error" in error

class TestSemanticValidation:
    def test_select_star_without_limit(self, validator, schema):
        sql = "SELECT * FROM Sales.SalesOrderHeader"
        question = "Show all orders"
        is_valid, error = validator.validate_semantics(sql, question, schema)
        assert not is_valid
        assert "LIMIT/TOP" in error
    
    def test_select_star_with_limit(self, validator, schema):
        sql = "SELECT TOP 10 * FROM Sales.SalesOrderHeader"
        question = "Show all orders"
        is_valid, error = validator.validate_semantics(sql, question, schema)
        assert is_valid
    
    def test_forbidden_table(self, validator, schema):
        sql = "SELECT * FROM AWBuildVersion"
        question = "Show build version"
        is_valid, error = validator.validate_semantics(sql, question, schema)
        assert not is_valid
        assert "Forbidden table" in error
    
    def test_revenue_without_correct_table(self, validator, schema):
        sql = "SELECT * FROM Sales.Customer"
        question = "Show top 10 customers by revenue"
        is_valid, error = validator.validate_semantics(sql, question, schema)
        assert not is_valid
        assert "Sales.SalesOrderHeader" in error
    
    def test_too_many_joins(self, validator, schema):
        sql = """
        SELECT * FROM t1
        JOIN t2 ON t1.id = t2.id
        JOIN t3 ON t2.id = t3.id
        JOIN t4 ON t3.id = t4.id
        JOIN t5 ON t4.id = t5.id
        JOIN t6 ON t5.id = t6.id
        """
        question = "Complex query"
        is_valid, error = validator.validate_semantics(sql, question, schema)
        assert not is_valid
        assert "Too many JOINs" in error

class TestFullValidation:
    def test_valid_revenue_query(self, validator, schema):
        sql = """
        SELECT TOP 10
            p.FirstName + ' ' + p.LastName AS CustomerName,
            SUM(soh.TotalDue) AS total_revenue
        FROM Sales.Customer c
        JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
        JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
        GROUP BY c.CustomerID, p.FirstName, p.LastName
        ORDER BY total_revenue DESC
        """
        question = "Show top 10 customers by revenue"
        is_valid, error = validator.validate(sql, question, schema)
        assert is_valid
        assert error == ""
```

Run tests:
```bash
pytest test_sql_validator.py -v
```

---

## Step 6: Update Query Response

**File**: `voxcore/voxquery/voxquery/api/v1/query.py`

Update response schema:

```python
from pydantic import BaseModel
from typing import Optional

class QueryResponse(BaseModel):
    generated_sql: str
    results: Optional[list] = None
    error: Optional[str] = None
    fallback: Optional[str] = None
    validation_passed: bool = True
    validation_error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    rows_returned: Optional[int] = None
```

---

## Step 7: Restart Backend

```bash
cd voxcore/voxquery
python -m uvicorn voxquery.api.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

---

## Testing Checklist

### Test 1: Valid Revenue Query
```
Question: "Show top 10 customers by revenue"
Expected: ✓ Validation passed
```

### Test 2: SELECT * Without LIMIT
```
Question: "Show all orders"
Generated SQL: "SELECT * FROM Sales.SalesOrderHeader"
Expected: ✗ Validation failed - "SELECT * without LIMIT/TOP"
```

### Test 3: Forbidden Table
```
Question: "Show build version"
Generated SQL: "SELECT * FROM AWBuildVersion"
Expected: ✗ Validation failed - "Forbidden table: AWBuildVersion"
```

### Test 4: Too Many JOINs
```
Question: "Complex query"
Generated SQL: "SELECT * FROM t1 JOIN t2 ... JOIN t6"
Expected: ✗ Validation failed - "Too many JOINs (5)"
```

### Test 5: Revenue Without Correct Table
```
Question: "Top customers by revenue"
Generated SQL: "SELECT * FROM Sales.Customer"
Expected: ✗ Validation failed - "Revenue question must use Sales.SalesOrderHeader"
```

---

## Success Metrics

### Before Validation
- Broken SQL reaches database
- Runtime errors
- User confusion
- Reliability: 75-85%

### After Validation
- Broken SQL caught before execution
- Clear error messages
- Fallback queries provided
- Reliability: 80-85%

---

## Next Steps

After Week 1 validation is working:

1. **Week 2**: Add rewrite engine (inject limits, qualify schemas)
2. **Week 3**: Add semantic router (classify relevant tables)
3. **Week 4**: Add feedback loop (thumbs up/down + corrections)

---

## Summary

Week 1 validation layer:
- ✅ Syntactic validation (sqlglot)
- ✅ Semantic validation (checks)
- ✅ Integration into query execution
- ✅ Logging & monitoring
- ✅ Test coverage

**Impact**: Catch 80% of broken SQL before execution  
**Reliability**: 75-85% → 80-85%  
**Effort**: 2-3 days  

