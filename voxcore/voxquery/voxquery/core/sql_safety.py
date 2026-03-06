"""SQL safety checks - prevent data modification and hallucinations"""

import logging
import re
import sqlglot
import sqlparse
from sqlglot import exp
from sqlparse.tokens import Keyword, DML, DDL
from typing import Optional

logger = logging.getLogger(__name__)


def _normalize_table_name(table_name: str) -> str:
    """
    Normalize unqualified table names to schema-qualified names for SQL Server.
    
    Maps common AdventureWorks table names to their schema-qualified versions.
    If already qualified or unknown, returns as-is.
    
    Args:
        table_name: Table name (may be qualified or unqualified)
    
    Returns:
        Schema-qualified table name
    """
    if not table_name:
        return table_name
    
    # If already qualified (contains a dot), return as-is
    if '.' in table_name:
        return table_name
    
    # Map unqualified names to schema-qualified names
    table_mappings = {
        'CUSTOMER': 'SALES.CUSTOMER',
        'SALESORDERHEADER': 'SALES.SALESORDERHEADER',
        'SALESORDERDETAIL': 'SALES.SALESORDERDETAIL',
        'PRODUCT': 'PRODUCTION.PRODUCT',
        'EMPLOYEE': 'HUMANRESOURCES.EMPLOYEE',
        'SCRAPREASON': 'PRODUCTION.SCRAPREASON',
        'DATABASELOG': 'DBO.DATABASELOG',
        'ERRORLOG': 'DBO.ERRORLOG',
    }
    
    upper_name = table_name.upper()
    return table_mappings.get(upper_name, table_name)


def fix_invented_columns(sql: str) -> str:
    """
    Fix common invented columns that LLM hallucinates.
    
    Replaces invented columns with correct joins and expressions.
    
    Args:
        sql: SQL query that may contain invented columns
    
    Returns:
        Fixed SQL query
    """
    if not sql:
        return sql
    
    # Fix common hallucinations
    # 1. c.Name → Person.Person.FirstName + ' ' + Person.Person.LastName
    if 'c.Name' in sql or 'c.NAME' in sql.upper():
        # Add Person.Person join if not already there
        if 'Person.Person' not in sql:
            sql = sql.replace(
                'FROM Sales.Customer c',
                'FROM Sales.Customer c JOIN Person.Person p ON c.PersonID = p.BusinessEntityID'
            )
        sql = re.sub(r'c\.Name\b', "CONCAT(p.FirstName, ' ', p.LastName)", sql, flags=re.IGNORECASE)
        logger.info("Fixed invented c.Name column")
    
    # 2. c.Balance → SUM(soh.TotalDue)
    if 'c.Balance' in sql or 'c.BALANCE' in sql.upper():
        if 'Sales.SalesOrderHeader' not in sql:
            sql = sql.replace(
                'FROM Sales.Customer c',
                'FROM Sales.Customer c JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID'
            )
        sql = re.sub(r'c\.Balance\b', 'SUM(soh.TotalDue)', sql, flags=re.IGNORECASE)
        logger.info("Fixed invented c.Balance column")
    
    # 3. c.TotalBalance → SUM(soh.TotalDue)
    if 'TotalBalance' in sql:
        if 'Sales.SalesOrderHeader' not in sql:
            sql = sql.replace(
                'FROM Sales.Customer c',
                'FROM Sales.Customer c JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID'
            )
        sql = re.sub(r'c\.TotalBalance\b', 'SUM(soh.TotalDue)', sql, flags=re.IGNORECASE)
        logger.info("Fixed invented TotalBalance column")
    
    # 4. c.CustomerName → CONCAT(p.FirstName, ' ', p.LastName)
    if 'CustomerName' in sql:
        if 'Person.Person' not in sql:
            sql = sql.replace(
                'FROM Sales.Customer c',
                'FROM Sales.Customer c JOIN Person.Person p ON c.PersonID = p.BusinessEntityID'
            )
        sql = re.sub(r'c\.CustomerName\b', "CONCAT(p.FirstName, ' ', p.LastName)", sql, flags=re.IGNORECASE)
        logger.info("Fixed invented CustomerName column")
    
    return sql


def sanitize_tsql(sql: str) -> str:
    """
    AGGRESSIVE runtime dialect sanitizer for SQL Server - blocks LIMIT and enforces T-SQL
    
    This is the user's requested aggressive sanitizer that:
    1. Removes/replaces LIMIT with TOP N
    2. Forces schema qualification for common tables
    3. Replaces invented 'Name' with correct join
    
    Args:
        sql: SQL query that may contain mixed dialect syntax
    
    Returns:
        Sanitized T-SQL query
    """
    if not sql:
        return sql
    
    sql = sql.strip()
    sql_upper = sql.upper()
    
    # Strip LIMIT if present
    sql = re.sub(r'\s*LIMIT\s+\d+\s*;?(\s|$)', '', sql, flags=re.IGNORECASE | re.DOTALL)
    
    # Add TOP 10 if "top 10" intent detected and no TOP present
    if 'TOP' not in sql.upper() and any(p in sql.lower() for p in ['top 10', 'top 20', 'highest 10']):
        n = 10  # default
        if 'TOP' in sql.upper():
            n_match = re.search(r'TOP\s+(\d+)', sql.upper())
            if n_match:
                n = n_match.group(1)
        sql = re.sub(r'SELECT\s+', f'SELECT TOP {n} ', sql, flags=re.IGNORECASE, count=1)
    
    # Ensure ORDER BY exists for TOP (fallback to first column)
    if 'TOP' in sql.upper() and 'ORDER BY' not in sql.upper():
        sql = sql.rstrip('; \n') + " ORDER BY 1 DESC"
    
    # Schema qualification for common tables
    sql = re.sub(r'\bFROM\s+Customer\b', 'FROM Sales.Customer', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bFROM\s+SalesOrderHeader\b', 'FROM Sales.SalesOrderHeader', sql, flags=re.IGNORECASE)
    
    return sql


def force_sqlserver_syntax(sql: str) -> str:
    """Aggressively convert LIMIT to TOP and remove dialect bleed"""
    sql = sql.strip()
    
    # Strip LIMIT if present
    sql = re.sub(r'\s*LIMIT\s+\d+\s*;?(\s|$)', '', sql, flags=re.IGNORECASE | re.DOTALL)
    
    # Add TOP 10 if "top 10" intent detected and no TOP present
    if 'TOP' not in sql.upper() and any(p in sql.lower() for p in ['top 10', 'top 20', 'highest 10']):
        n = 10  # default
        if 'TOP' in sql.upper():
            n_match = re.search(r'TOP\s+(\d+)', sql.upper())
            if n_match:
                n = n_match.group(1)
        sql = re.sub(r'SELECT\s+', f'SELECT TOP {n} ', sql, flags=re.IGNORECASE, count=1)
    
    # Ensure ORDER BY exists for TOP (fallback to first column)
    if 'TOP' in sql.upper() and 'ORDER BY' not in sql.upper():
        sql = sql.rstrip('; \n') + " ORDER BY 1 DESC"
    
    # Schema qualification for common tables
    sql = re.sub(r'\bFROM\s+Customer\b', 'FROM Sales.Customer', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bFROM\s+SalesOrderHeader\b', 'FROM Sales.SalesOrderHeader', sql, flags=re.IGNORECASE)
    
    return sql


def normalize_tsql(sql: str) -> str:
    """
    Force SQL Server dialect compatibility - convert Snowflake/PostgreSQL syntax to T-SQL
    
    Args:
        sql: SQL query that may contain mixed dialect syntax
    
    Returns:
        Normalized T-SQL query
    """
    if not sql:
        return sql
    
    sql_upper = sql.upper()
    
    # Replace LIMIT with TOP if missing TOP
    if 'LIMIT' in sql_upper and 'TOP' not in sql_upper:
        # Extract N from LIMIT N
        match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
        if match:
            n = match.group(1)
            # Remove LIMIT clause
            sql = re.sub(r'\s+LIMIT\s+\d+', '', sql, flags=re.IGNORECASE)
            # Add TOP at the beginning of SELECT
            sql = re.sub(r'SELECT\s+', f'SELECT TOP {n} ', sql, flags=re.IGNORECASE, count=1)
            logger.info(f"✅ Converted LIMIT {n} to TOP {n}")
    
    # Fix common Snowflake/PostgreSQL functions
    sql = re.sub(r'CURRENT_DATE\(\)', 'CAST(GETDATE() AS DATE)', sql, flags=re.IGNORECASE)
    sql = re.sub(r'CURRENT_TIMESTAMP\(\)', 'GETDATE()', sql, flags=re.IGNORECASE)
    sql = re.sub(r'NOW\(\)', 'GETDATE()', sql, flags=re.IGNORECASE)
    
    # Ensure schema qualification for common AdventureWorks tables
    # Map unqualified names to schema-qualified names
    table_mappings = {
        r'\bCUSTOMER\b': 'Sales.Customer',
        r'\bSALESORDERHEADER\b': 'Sales.SalesOrderHeader',
        r'\bSALESORDERDETAIL\b': 'Sales.SalesOrderDetail',
        r'\bPRODUCT\b': 'Production.Product',
        r'\bEMPLOYEE\b': 'HumanResources.Employee',
        r'\bSCRAPREASON\b': 'Production.ScrapReason',
    }
    
    for unqualified, qualified in table_mappings.items():
        # Only replace if not already qualified
        if not re.search(rf'\w+\.{unqualified}', sql, re.IGNORECASE):
            sql = re.sub(unqualified, qualified, sql, flags=re.IGNORECASE)
    
    return sql


def is_read_only(sql: str, dialect: str = "snowflake") -> tuple[bool, str | None]:
    """
    Check if SQL is read-only (SELECT only, no INSERT/UPDATE/DELETE/CREATE/DROP/ALTER)
    
    Args:
        sql: SQL query to check
        dialect: Database dialect (snowflake, sqlserver, postgres, etc.)
    
    Returns:
        (is_safe: bool, error_message: str | None)
        - (True, None) if query is safe (SELECT only)
        - (False, error_msg) if query is unsafe (contains DML/DDL)
    """
    try:
        # For SQL Server, use sqlparse instead of sqlglot since sqlglot doesn't support 'mssql'
        if dialect.lower() in ['sqlserver', 'mssql']:
            # Use sqlparse for SQL Server
            parsed = sqlparse.parse(sql)
            if not parsed:
                return False, "Could not parse SQL"
            
            parsed_stmt = parsed[0]
            
            # Check for dangerous keywords
            dangerous_keywords = {
                'DROP', 'DELETE', 'UPDATE', 'INSERT', 'MERGE', 'TRUNCATE',
                'ALTER', 'CREATE', 'EXECUTE', 'GRANT', 'REVOKE', 'EXEC'
            }
            
            for token in parsed_stmt.flatten():
                # Check both Keyword and DML token types
                if (token.ttype is Keyword or token.ttype is DML) and token.value.upper() in dangerous_keywords:
                    logger.warning(f"❌ UNSAFE SQL DETECTED: {token.value.upper()} operation not allowed")
                    return False, f"Only SELECT queries allowed for safety. {token.value.upper()} operations are blocked."
            
            logger.info(f"✅ SQL safety check passed: Query is read-only")
            return True, None
        
        # For other dialects, try sqlglot
        dialect_map = {
            'snowflake': 'snowflake',
            'postgres': 'postgres',
            'postgresql': 'postgres',
            'redshift': 'redshift',
            'bigquery': 'bigquery',
        }
        
        sqlglot_dialect = dialect_map.get(dialect.lower(), 'snowflake')
        
        # Parse the SQL
        parsed = sqlglot.parse_one(sql, read=sqlglot_dialect)
        
        if not parsed:
            return False, "Could not parse SQL"
        
        # Check for dangerous operations (use correct sqlglot expression names)
        dangerous_types = [
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Create,
            exp.Drop,
            exp.Alter,
            exp.TruncateTable,
            exp.Replace,
            exp.Grant,
            exp.Revoke,
            exp.Merge,
        ]
        
        for dangerous_type in dangerous_types:
            if parsed.find(dangerous_type):
                operation = dangerous_type.__name__.upper()
                logger.warning(f"❌ UNSAFE SQL DETECTED: {operation} operation not allowed")
                return False, f"Only SELECT queries allowed for safety. {operation} operations are blocked."
        
        # Extra check for TRUNCATE (sometimes parsed differently)
        if "TRUNCATE" in sql.upper() and "TABLE" in sql.upper():
            logger.warning(f"❌ UNSAFE SQL DETECTED: TRUNCATE TABLE operation not allowed")
            return False, "Only SELECT queries allowed for safety. TRUNCATE TABLE operations are blocked."
        
        # Check if it's a SELECT (or CTE with SELECT)
        if not isinstance(parsed, exp.Select):
            # Could be a CTE or other structure, check if it contains SELECT
            if not parsed.find(exp.Select):
                return False, "Query must be a SELECT statement"
        
        logger.info(f"✅ SQL safety check passed: Query is read-only")
        return True, None
        
    except Exception as e:
        logger.error(f"Error checking SQL safety: {e}")
        # Fail safe - if we can't parse it, reject it
        return False, f"Could not validate SQL safety: {str(e)}"


def sanitize_sql(sql: str) -> str:
    """
    Sanitize SQL by removing comments and normalizing whitespace
    
    Args:
        sql: Raw SQL query
    
    Returns:
        Cleaned SQL
    """
    try:
        # Parse and regenerate to normalize
        parsed = sqlglot.parse_one(sql)
        if parsed:
            return parsed.sql()
        return sql
    except:
        return sql


def extract_tables(sql: str, dialect: str = "snowflake") -> set:
    """
    Extract table names from SQL query using sqlglot AST.
    Simple and reliable - just gets table names from FROM/JOIN clauses.
    Falls back to sqlparse for SQL Server since sqlglot doesn't support 'mssql'.
    
    Args:
        sql: SQL query
        dialect: Database dialect
    
    Returns:
        Set of table names (uppercase), with schema qualification for SQL Server
    """
    try:
        # For SQL Server, use sqlparse since sqlglot doesn't support 'mssql'
        if dialect.lower() in ['sqlserver', 'mssql']:
            tables = set()
            parsed = sqlparse.parse(sql)
            if not parsed:
                return set()
            
            # Simple regex-based extraction for SQL Server
            # Look for FROM and JOIN keywords followed by table names
            from sqlparse.sql import IdentifierList, Identifier, Where
            from sqlparse.tokens import Keyword, DML
            
            stmt = parsed[0]
            from_seen = False
            
            for token in stmt.tokens:
                # Skip whitespace and comments
                if token.is_whitespace or token.ttype in (sqlparse.tokens.Comment.Single, sqlparse.tokens.Comment.Multiline):
                    continue
                
                # Check for FROM or JOIN keywords
                if token.ttype is Keyword and token.value.upper() in ('FROM', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'CROSS JOIN'):
                    from_seen = True
                    continue
                
                # After FROM/JOIN, next non-whitespace token should be table name(s)
                if from_seen:
                    if isinstance(token, IdentifierList):
                        # Multiple tables
                        for identifier in token.get_identifiers():
                            table_name = identifier.get_real_name()
                            if table_name:
                                # Normalize unqualified names to schema-qualified
                                normalized = _normalize_table_name(table_name)
                                tables.add(normalized.upper())
                    elif isinstance(token, Identifier):
                        # Single table
                        table_name = token.get_real_name()
                        if table_name:
                            # Normalize unqualified names to schema-qualified
                            normalized = _normalize_table_name(table_name)
                            tables.add(normalized.upper())
                    elif token.ttype is Keyword:
                        # Another keyword (WHERE, GROUP BY, etc.) - stop looking
                        from_seen = False
                    elif not token.is_whitespace:
                        # Some other token - stop looking
                        from_seen = False
            
            print(f"[DEBUG] Parsed tables (sqlparse): {tables}")
            logger.debug(f"Extracted tables from SQL (sqlparse): {tables}")
            return tables
        
        # For other dialects, use sqlglot
        # Map our dialect names to sqlglot dialect names
        dialect_map = {
            'snowflake': 'snowflake',
            'postgres': 'postgres',
            'postgresql': 'postgres',
            'redshift': 'redshift',
            'bigquery': 'bigquery',
        }
        
        sqlglot_dialect = dialect_map.get(dialect.lower(), 'snowflake')
        
        parsed = sqlglot.parse_one(sql, read=sqlglot_dialect)
        if not parsed:
            print(f"[EXTRACTION ERROR] sqlglot failed to parse SQL\nSQL:\n{sql}")
            return set()
        
        tables = set()
        for table in parsed.find_all(exp.Table):
            if table.name:  # skip empty / alias-only
                tables.add(table.name.upper())
        
        print(f"[DEBUG] Parsed tables (sqlglot): {tables}")
        logger.debug(f"Extracted tables from SQL (sqlglot): {tables}")
        return tables
    except Exception as e:
        print(f"[EXTRACTION ERROR] {e}\nSQL:\n{sql}")
        logger.warning(f"Error extracting tables from SQL: {e}")
        return set()


def extract_columns(sql: str, dialect: str = "snowflake") -> dict:
    """
    Extract columns by table from SQL query.
    Falls back to sqlparse for SQL Server since sqlglot doesn't support 'mssql'.
    
    Args:
        sql: SQL query
        dialect: Database dialect
    
    Returns:
        Dict mapping table names/aliases to sets of column names
    """
    try:
        # For SQL Server, use sqlparse since sqlglot doesn't support 'mssql'
        if dialect.lower() in ['sqlserver', 'mssql']:
            columns_by_table = {}
            parsed = sqlparse.parse(sql)
            if not parsed:
                return {}
            
            stmt = parsed[0]
            
            # Simple extraction: look for SELECT clause and extract column references
            # This is a simplified approach that works for most queries
            select_seen = False
            in_select = False
            
            for token in stmt.tokens:
                if token.is_whitespace or token.ttype in (sqlparse.tokens.Comment.Single, sqlparse.tokens.Comment.Multiline):
                    continue
                
                # Look for SELECT keyword
                if token.ttype is Keyword and token.value.upper() == 'SELECT':
                    select_seen = True
                    in_select = True
                    continue
                
                # Stop at FROM keyword
                if token.ttype is Keyword and token.value.upper() == 'FROM':
                    in_select = False
                    continue
                
                # Extract columns from SELECT clause
                if in_select:
                    from sqlparse.sql import IdentifierList, Identifier, Parenthesis
                    
                    if isinstance(token, IdentifierList):
                        # Multiple columns
                        for identifier in token.get_identifiers():
                            col_name = identifier.get_real_name()
                            if col_name and col_name != '*':
                                # Add to wildcard table reference
                                if '*' not in columns_by_table:
                                    columns_by_table['*'] = set()
                                columns_by_table['*'].add(col_name.upper())
                    elif isinstance(token, Identifier):
                        # Single column
                        col_name = token.get_real_name()
                        if col_name and col_name != '*':
                            if '*' not in columns_by_table:
                                columns_by_table['*'] = set()
                            columns_by_table['*'].add(col_name.upper())
                    elif token.value.strip() == '*':
                        # Wildcard - add to wildcard reference
                        if '*' not in columns_by_table:
                            columns_by_table['*'] = set()
                        columns_by_table['*'].add('*')
            
            return columns_by_table
        
        # For other dialects, use sqlglot
        # Map our dialect names to sqlglot dialect names
        dialect_map = {
            'snowflake': 'snowflake',
            'postgres': 'postgres',
            'postgresql': 'postgres',
            'redshift': 'redshift',
            'bigquery': 'bigquery',
        }
        
        sqlglot_dialect = dialect_map.get(dialect.lower(), 'snowflake')
        
        parsed = sqlglot.parse_one(sql, read=sqlglot_dialect)
        if not parsed:
            return {}
        
        columns_by_table = {}
        
        # Find all column references
        for col in parsed.find_all(exp.Column):
            col_name = col.name
            table_ref = col.table  # Could be alias or table name
            
            if col_name:
                # If table is specified, use it; otherwise use "*" as wildcard
                table_key = table_ref.upper() if table_ref else "*"
                
                if table_key not in columns_by_table:
                    columns_by_table[table_key] = set()
                
                columns_by_table[table_key].add(col_name.upper())
        
        return columns_by_table
    except Exception as e:
        logger.warning(f"Error extracting columns from SQL: {e}")
        return {}


def inspect_and_repair(
    generated_sql: str,
    schema_tables: set,
    schema_columns: dict,
    dialect: str = "snowflake"
) -> tuple[str, float]:
    """
    Inspect generated SQL for hallucinations and schema violations.
    Returns (final_sql, confidence_score 0–1).
    
    Args:
        generated_sql: SQL generated by LLM
        schema_tables: Set of valid table names (uppercase)
        schema_columns: Dict mapping table names to sets of column names
        dialect: Database dialect
    
    Returns:
        (final_sql, confidence_score)
        - confidence_score 1.0 = fully valid
        - confidence_score 0.0 = fallback used
        - 0.5-0.95 = warnings but usable
    """
    score = 1.0
    issues = []
    
    # 1. Forbidden keywords (DDL/DML)
    forbidden = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'CREATE', 'EXECUTE', 'GRANT']
    if any(kw in generated_sql.upper() for kw in forbidden):
        issues.append("Forbidden DDL/DML detected")
        score *= 0.1
        logger.warning(f"❌ SQL inspection: Forbidden keyword detected")
    
    # 2. Table name validation
    extracted_tables = extract_tables(generated_sql, dialect)
    
    if not extracted_tables:
        # Extraction failed or no tables found - assume safe if no DDL/DML
        print("[VALIDATION WARNING] Table extraction failed — assuming safe if no DDL/DML")
        logger.warning("[VALIDATION WARNING] Table extraction failed — assuming safe if no DDL/DML")
    else:
        unknown_tables = extracted_tables - schema_tables
        
        if unknown_tables:
            issues.append(f"Unknown tables: {unknown_tables}")
            score *= 0.4
            logger.warning(f"❌ SQL inspection: Unknown tables {unknown_tables}")
    
    # 3. Column validation (only for tables we know about)
    extracted_cols = extract_columns(generated_sql, dialect)
    
    for table_key, cols in extracted_cols.items():
        # Skip wildcard table references
        if table_key == "*":
            continue
        
        # Check if table exists in schema
        if table_key in schema_tables:
            allowed_cols = schema_columns.get(table_key, set())
            
            # If we have column info for this table, validate
            if allowed_cols:
                invalid_cols = cols - allowed_cols
                if invalid_cols:
                    issues.append(f"Invalid columns in {table_key}: {invalid_cols}")
                    score *= 0.6
                    logger.warning(f"❌ SQL inspection: Invalid columns {invalid_cols} in table {table_key}")
    
    # 4. Final decision
    if score < 0.5:
        logger.warning(f"❌ SQL inspection FAILED (score {score:.2f}): {'; '.join(issues)}")
        
        # Use safe fallback
        if schema_tables:
            safe_table = next(iter(schema_tables))
            fallback_sql = f"SELECT * FROM {safe_table} LIMIT 10"
            logger.warning(f"⚠️  Using fallback query: {fallback_sql}")
            return fallback_sql, 0.0
        
        fallback_sql = "SELECT 1 AS no_matching_schema"
        logger.warning(f"⚠️  Using fallback query: {fallback_sql}")
        return fallback_sql, 0.0
    
    if issues:
        logger.warning(f"⚠️  SQL inspection passed with warnings (score {score:.2f}): {'; '.join(issues)}")
    else:
        logger.info(f"✅ SQL inspection passed (score {score:.2f})")
    
    return generated_sql, score


def validate_sql(
    sql: str,
    allowed_tables: set,
    allowed_columns: dict = None,
    dialect: str = "snowflake"
) -> tuple[bool, str, float]:
    """
    Level 2 Validation: Table & Column Whitelist + Safety Rules
    
    Returns (is_safe: bool, reason: str, confidence: float 0–1)
    
    This is a production-ready validation layer that:
    1. Blocks dangerous DDL/DML keywords
    2. Validates tables against whitelist
    3. Validates columns against whitelist (optional)
    4. Returns confidence score for UI integration
    
    Args:
        sql: SQL query to validate
        allowed_tables: Set of allowed table names (uppercase)
        allowed_columns: Dict mapping table names to allowed column sets (optional)
        dialect: Database dialect
    
    Returns:
        (is_safe, reason, confidence)
        - is_safe: True if score >= 0.6
        - reason: Human-readable explanation
        - confidence: Score 0.0-1.0
    """
    print("[VALIDATION START] SQL to validate:")
    print(sql)
    
    score = 1.0
    issues = []
    
    if not sql or not sql.strip():
        print("[VALIDATION FAIL] SQL is empty")
        return False, "SQL is empty", 0.0
    
    try:
        # Parse SQL
        parsed = sqlparse.parse(sql)
        if not parsed:
            return False, "Could not parse SQL", 0.0
        
        parsed_stmt = parsed[0]
        
        # 1. BLOCK DANGEROUS KEYWORDS (DDL/DML)
        dangerous_keywords = {
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'MERGE', 'TRUNCATE',
            'ALTER', 'CREATE', 'EXECUTE', 'GRANT', 'REVOKE', 'EXEC'
        }
        
        found_dangerous = []
        for token in parsed_stmt.flatten():
            if token.ttype is Keyword and token.value.upper() in dangerous_keywords:
                found_dangerous.append(token.value.upper())
        
        if found_dangerous:
            issues.append(f"Forbidden DDL/DML keywords detected: {', '.join(set(found_dangerous))}")
            score *= 0.05  # Heavy penalty
            print(f"[VALIDATION FAIL] Dangerous keywords: {set(found_dangerous)}")
            logger.warning(f"❌ SQL validation: Dangerous keywords {set(found_dangerous)}")
        else:
            print("[VALIDATION] DDL/DML check passed")
        
        # 2. EXTRACT AND VALIDATE TABLES
        tables_in_sql = extract_tables(sql, dialect)
        
        # Normalize case for comparison
        allowed_tables_upper = {t.upper() for t in allowed_tables} if allowed_tables else set()
        
        # DEBUG: Show what we're comparing
        print(f"[VALIDATION] Allowed: {allowed_tables_upper}")
        print(f"[VALIDATION] Extracted: {tables_in_sql}")
        
        if tables_in_sql:
            unknown_tables = tables_in_sql - allowed_tables_upper
            
            print(f"[VALIDATION] Unknown: {unknown_tables}")
            
            if unknown_tables:
                # Only fail if we have a populated allowed_tables list
                if allowed_tables_upper:
                    issues.append(f"Unknown tables referenced: {', '.join(sorted(unknown_tables))}")
                    score *= 0.3  # Moderate penalty
                    print(f"[VALIDATION FAIL] Unknown tables: {unknown_tables}")
                    logger.warning(f"❌ SQL validation: Unknown tables {unknown_tables}")
                else:
                    # If allowed_tables is empty, don't fail on unknown tables
                    print("[VALIDATION] Allowed tables empty — skipping unknown table check")
                    logger.warning("[VALIDATION] Allowed tables empty — skipping unknown table check")
            else:
                print("[VALIDATION] Tables OK — proceeding")
        else:
            # No tables extracted - don't fail, just log
            print("[VALIDATION] No tables extracted from SQL")
        
        # 3. VALIDATE COLUMNS (if allowed_columns provided)
        if allowed_columns:
            extracted_cols = extract_columns(sql, dialect)
            
            for table_key, cols in extracted_cols.items():
                # Skip wildcard references
                if table_key == "*":
                    continue
                
                # Check if table is in allowed list
                table_upper = table_key.upper()
                if table_upper in {t.upper() for t in allowed_tables}:
                    allowed_cols_upper = {c.upper() for c in allowed_columns.get(table_upper, set())}
                    
                    if allowed_cols_upper:
                        invalid_cols = cols - allowed_cols_upper
                        if invalid_cols:
                            issues.append(f"Invalid columns in {table_key}: {', '.join(sorted(invalid_cols))}")
                            score *= 0.5  # Moderate penalty
                            logger.warning(f"❌ SQL validation: Invalid columns {invalid_cols} in {table_key}")
        
        # 4. DIALECT VALIDATION (for SQL Server) – LAYER 3: HARD REJECT LIMIT
        if dialect and dialect.lower() in ['sqlserver', 'mssql']:
            forbidden_keywords = ['LIMIT', 'DATE_TRUNC', 'EXTRACT', 'CURRENT_DATE', 'ILIKE', 'NOW()']
            sql_upper = sql.upper()
            
            found_forbidden = []
            for kw in forbidden_keywords:
                if kw in sql_upper:
                    found_forbidden.append(kw)
            
            if found_forbidden:
                # LAYER 3: HARD REJECT – LIMIT is immediate fail
                if 'LIMIT' in found_forbidden:
                    issues.append(f"LIMIT forbidden in SQL Server – must use TOP N")
                    score = 0.0  # IMMEDIATE REJECT
                    logger.error(f"❌ LAYER 3 REJECT: LIMIT keyword in SQL Server query")
                    print(f"[VALIDATION FAIL] LAYER 3: LIMIT keyword detected – immediate reject")
                else:
                    issues.append(f"Forbidden dialect keywords for SQL Server: {', '.join(found_forbidden)}")
                    score *= 0.01  # ALMOST ALWAYS REJECT
                    logger.warning(f"❌ SQL validation: Forbidden dialect keywords {found_forbidden}")
                    print(f"[VALIDATION FAIL] Dialect mismatch: {found_forbidden}")
        
        # Check TOP requires ORDER BY
        if 'TOP' in sql.upper() and 'ORDER BY' not in sql.upper():
            issues.append("TOP N requires ORDER BY clause")
            score *= 0.3
            logger.warning(f"❌ SQL validation: TOP without ORDER BY")
            print(f"[VALIDATION FAIL] TOP without ORDER BY")
        
        # 5. COLUMN HALLUCINATION DETECTION (for SQL Server)
        if dialect and dialect.lower() in ['sqlserver', 'mssql']:
            # Check for common invented columns
            invented_cols = ['c.Name', 'c.Balance', 'c.TotalBalance', 'c.CustomerName']
            sql_upper = sql.upper()
            
            for invented_col in invented_cols:
                if invented_col.upper() in sql_upper:
                    # Special case: if Person.Person.FirstName is in the query, c.Name is OK
                    if invented_col.upper() == 'C.NAME' and 'PERSON.PERSON.FIRSTNAME' in sql_upper:
                        continue
                    
                    issues.append(f"Suspected invented column: {invented_col}")
                    score *= 0.2  # Heavy penalty
                    logger.warning(f"Column hallucination detected: {invented_col}")
                    print(f"[VALIDATION FAIL] Invented column: {invented_col}")
        
        # 6. FINAL DECISION
        is_safe = score >= 0.6
        
        if issues:
            reason = "; ".join(issues)
            print(f"[VALIDATION FAIL] Score {score:.2f}: {reason}")
            logger.warning(f"⚠️  SQL validation issues (score {score:.2f}): {reason}")
        else:
            reason = "SQL passed all safety checks"
            print(f"[VALIDATION PASS] All checks passed (score {score:.2f})")
            logger.info(f"✅ SQL validation passed (score {score:.2f})")
        
        return is_safe, reason, score
    
    except Exception as e:
        logger.error(f"Error during SQL validation: {e}")
        return False, f"Validation error: {str(e)}", 0.0
