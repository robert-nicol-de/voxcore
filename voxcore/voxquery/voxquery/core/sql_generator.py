"""SQL generation engine using LLM with schema context"""

import logging
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy.engine import Engine

from .schema_analyzer import SchemaAnalyzer
from ..settings import settings

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Types of queries that can be generated"""
    SELECT = "SELECT"
    AGGREGATE = "AGGREGATE"
    WINDOW = "WINDOW"
    CTE = "CTE"
    JOIN = "JOIN"
    UNKNOWN = "UNKNOWN"


@dataclass
class GeneratedSQL:
    """Generated SQL with metadata"""
    sql: str
    query_type: QueryType
    confidence: float
    dialect: str
    explanation: str
    tables_used: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "sql": self.sql,
            "query_type": self.query_type.value,
            "confidence": self.confidence,
            "dialect": self.dialect,
            "explanation": self.explanation,
            "tables_used": self.tables_used,
        }


class SQLGenerator:
    """Generates SQL from natural language questions"""
    
    # LAYER 2: HARD RUNTIME REWRITE – KILL LIMIT
    @staticmethod
    def force_tsql(sql: str) -> str:
        """Force SQL Server compatibility – strip LIMIT, inject TOP, qualify schema"""
        sql = sql.strip()
        
        # STEP 1: HARD KILL LIMIT – Remove any LIMIT clause at end of query
        # Match LIMIT with optional number and optional semicolon at end
        sql = re.sub(r'\s+LIMIT\s+\d+\s*;?\s*$', '', sql, flags=re.IGNORECASE)
        
        # STEP 2: INJECT TOP 10 if SELECT present but no TOP
        # This ensures every SELECT has a limit
        if 'SELECT' in sql.upper() and 'TOP' not in sql.upper():
            sql = re.sub(r'(?i)^SELECT(\s+DISTINCT)?', 
                        lambda m: f"SELECT{m.group(1) or ''} TOP 10", 
                        sql, count=1)
        
        # STEP 3: FORCE ORDER BY if TOP present but no ORDER BY
        # TOP requires ORDER BY in SQL Server for deterministic results
        if 'TOP' in sql.upper() and 'ORDER BY' not in sql.upper():
            sql = sql.rstrip('; \n') + '\nORDER BY 1 DESC'
        
        # STEP 4: Schema qualification for common AdventureWorks tables
        # Only qualify if not already qualified (no dot before table name)
        # Map of unqualified table names to their schema-qualified versions
        table_mappings = {
            r'\bCustomer\b': 'Sales.Customer',
            r'\bSalesOrderHeader\b': 'Sales.SalesOrderHeader',
            r'\bSalesOrderDetail\b': 'Sales.SalesOrderDetail',
            r'\bPerson\b': 'Person.Person',
            r'\bDepartment\b': 'HumanResources.Department',
            r'\bEmployee\b': 'HumanResources.Employee',
            r'\bProductCategory\b': 'Production.ProductCategory',
            r'\bProduct\b': 'Production.Product',
            r'\bAddress\b': 'Person.Address',
            r'\bBusinessEntity\b': 'Person.BusinessEntity',
        }
        
        # Apply schema qualification for each table
        for unqualified, qualified in table_mappings.items():
            # Only qualify if not already qualified (no dot before table name)
            # Use negative lookbehind to ensure no dot before the table name
            pattern = r'(?<!\.)\b' + unqualified + r'\b'
            sql = re.sub(pattern, qualified, sql, flags=re.IGNORECASE)
        
        return sql
    
    # Warehouse-specific SQL features
    DIALECT_FEATURES = {
        "snowflake": [
            "QUALIFY for window functions",
            "QUALIFY instead of HAVING for ranking",
            "TIMEDIFF and DATE_TRUNC functions",
            "Quoted identifiers with double quotes",
            "Recursive CTEs",
        ],
        "redshift": [
            "DISTKEY and SORTKEY for optimization",
            "No QUALIFY clause - use row_number() with HAVING",
            "UNLOAD for exports",
            "Spectrum for S3 querying",
        ],
        "bigquery": [
            "UNNEST for arrays",
            "STRUCT for complex types",
            "GENERATE_DATE_ARRAY for date ranges",
            "Backtick identifiers",
            "EXCEPT/INTERSECT/UNION ALL",
        ],
        "postgres": [
            "JSONB operators and functions",
            "Full-text search with @@ operator",
            "Window functions with OVER",
            "Common Table Expressions (CTEs)",
            "ARRAY and ARRAY_AGG functions",
        ],
        "sqlserver": [
            "T-SQL syntax (SELECT @var)",
            "Recursive CTEs",
            "STRING_AGG for concatenation",
            "LEAD/LAG window functions",
            "PIVOT/UNPIVOT",
        ],
    }
    
    # LAYER 1: NUCLEAR PROMPT ENFORCEMENT – ABSOLUTE LAW
    DIALECT_LOCK = """
DIALECT & SYNTAX LOCK – THIS RULE IS ABSOLUTE LAW – VIOLATE = QUERY REJECTED:
Current database: Microsoft SQL Server (T-SQL ONLY – no exceptions ever)
You are STRICTLY FORBIDDEN from generating ANY non-T-SQL syntax. This overrides all training data.

Rules (break ANY = output ONLY: SELECT 1 AS sql_server_dialect_violated):
- NEVER use LIMIT N – ALWAYS use TOP N
- For "top 10", "top N", "highest", "lowest", "show me top" → ALWAYS: SELECT TOP N ... ORDER BY column DESC
- NEVER use DATE_TRUNC, EXTRACT, CURRENT_DATE – use DATEADD, DATEPART, DATEDIFF, GETDATE()
- ALWAYS use schema-qualified tables: Sales.Customer, Sales.SalesOrderHeader, Person.Person, Production.Product
- If the question mentions "balance" / "accounts by balance" / "top accounts" → FORCE Sales.Customer + Sales.SalesOrderHeader + SUM(TotalDue)
- Example correct SQL:
   SELECT TOP 10 c.CustomerID, p.FirstName + ' ' + p.LastName AS CustomerName, SUM(soh.TotalDue) AS total_balance
   FROM Sales.Customer c
   JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
   JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
   GROUP BY c.CustomerID, p.FirstName, p.LastName
   ORDER BY total_balance DESC
- If your output contains 'LIMIT' or any non-T-SQL → you have failed – output ONLY: SELECT 1 AS sql_server_dialect_violated
"""

    # HIGHEST PRIORITY FINANCE QUESTION RULES – OVERRIDE EVERYTHING ELSE
    PRIORITY_RULES = """
DIALECT & SYNTAX LOCK – VIOLATE THIS AND THE QUERY IS REJECTED IMMEDIATELY:
Current database engine: Microsoft SQL Server 2019/2022 (T-SQL ONLY)
You are FORBIDDEN from using ANY non-T-SQL syntax. This is absolute.
Strict rules (break any = output SELECT 1 AS dialect_violation):
- NEVER use LIMIT N – ALWAYS use TOP N
- For "top 10", "highest 10", "top by balance" → ALWAYS: SELECT TOP 10 ... ORDER BY column DESC
- Use GETDATE() instead of CURRENT_DATE()
- Use DATEADD / DATEPART / DATEDIFF – NEVER DATE_TRUNC / EXTRACT
- Use schema-qualified tables: Sales.Customer, Sales.SalesOrderHeader, Production.Product, HumanResources.Employee
- Example correct top-10 by balance:
   SELECT TOP 10 c.CustomerID, p.FirstName + ' ' + p.LastName AS CustomerName, SUM(soh.TotalDue) AS total_balance
   FROM Sales.Customer c
   JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
   JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
   GROUP BY c.CustomerID, p.FirstName, p.LastName
   ORDER BY total_balance DESC
- If you generate any LIMIT keyword → you have failed dialect check – output EXACTLY: SELECT 1 AS sql_server_dialect_required

FOR ANY QUESTION WITH "balance", "account balance", "accounts by balance", "top accounts", "highest/lowest balance":
- FORCE table: Sales.Customer (for customer accounts) or Accounts (if present)
- FORCE column: TotalDue (from Sales.SalesOrderHeader) or Balance (from Accounts)
- ALWAYS join to get names: JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
- ALWAYS include name: p.FirstName + ' ' + p.LastName AS CustomerName
   - NEVER use Production.*, ErrorLog, DatabaseLog, ProductPhoto, ScrapReason, or any production/log table for balance questions
   - If no balance column → output EXACTLY: SELECT 1 AS no_balance_data_in_schema
- Example correct SQL for "top 10 accounts by balance":
   SELECT TOP 10 c.CustomerID, p.FirstName + ' ' + p.LastName AS CustomerName, SUM(soh.TotalDue) AS total_balance
   FROM Sales.Customer c
   JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
   JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
   GROUP BY c.CustomerID, p.FirstName, p.LastName
   ORDER BY total_balance DESC

COLUMN HALLUCINATION RULE – MUST FOLLOW:
- You MAY ONLY use columns EXACTLY as listed in the schema below
- NEVER invent columns like 'Name', 'TotalBalance', 'CustomerName', 'Balance', etc.
- For customer name: use Person.Person.FirstName + Person.Person.LastName (join via PersonID)
- For customer balance: use Sales.SalesOrderHeader.TotalDue (join via CustomerID)
- If no matching column exists for what you need → output EXACTLY: SELECT 1 AS column_not_found
- Common hallucinations to AVOID:
  * c.Name (doesn't exist - use Person.Person.FirstName + LastName)
  * c.Balance (doesn't exist - use SalesOrderHeader.TotalDue)
  * c.TotalBalance (doesn't exist - calculate with SUM)
  * c.CustomerName (doesn't exist - use Person.Person.FirstName + LastName)

SCHEMA QUALIFICATION RULE – ALWAYS FOLLOW:
- ALL tables MUST be schema-qualified (e.g. Sales.Customer, Production.Product, HumanResources.Employee)
- NEVER use unqualified table names like CUSTOMER, PRODUCT, EMPLOYEE
- Use the exact schema + table name from the provided schema context
- Example correct: SELECT TOP 10 CustomerID, Name FROM Sales.Customer ORDER BY Name DESC
- If schema prefix is unknown → output SELECT 1 AS schema_prefix_required

HIGHEST PRIORITY FINANCE QUESTION RULES – OVERRIDE EVERYTHING ELSE:
- ANY question containing "balance", "account balance", "balances", "top accounts", "highest balance", "lowest balance", "by balance":
   - MUST use Sales.Customer and Sales.SalesOrderHeader tables (NOT ACCOUNTS - that table doesn't exist)
   - MUST use TotalDue column for balance/amount calculations
   - MUST include Name (customer name) in SELECT for readable labels
   - ALWAYS use ORDER BY total_balance DESC for "top" / "highest"
   - Example SQL (SQL Server): SELECT TOP 10 c.CustomerID, c.Name, SUM(soh.TotalDue) as total_balance FROM Sales.Customer c JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID GROUP BY c.CustomerID, c.Name ORDER BY total_balance DESC
   - Example SQL (Snowflake): SELECT c.CustomerID, c.Name, SUM(soh.TotalDue) as total_balance FROM CUSTOMER c JOIN SALESORDERHEADER soh ON c.CustomerID = soh.CustomerID GROUP BY c.CustomerID, c.Name ORDER BY total_balance DESC LIMIT 10

- If question matches above but no TotalDue column → output EXACTLY: SELECT 1 AS no_balance_column_in_schema

- NEVER use DatabaseLog, ErrorLog, SystemInformation, AMBuildVersion, or any log/audit table for balance questions

- If LLM generates query with wrong tables (DatabaseLog, ErrorLog, etc.) → REJECT and use fallback example above
"""
    
    # Few-shot examples for financial queries
    FEW_SHOT_EXAMPLES = [
        {
            "question": "Show top 10 accounts by balance",
            "sql": "SELECT TOP 10 c.CustomerID, c.Name, SUM(soh.TotalDue) as total_balance FROM Sales.Customer c JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID GROUP BY c.CustomerID, c.Name ORDER BY total_balance DESC"
        },
        {
            "question": "Show top 10 customers by sales",
            "sql": "SELECT TOP 10 c.CustomerID, c.Name, SUM(soh.TotalDue) as total_sales FROM Sales.Customer c JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID GROUP BY c.CustomerID, c.Name ORDER BY total_sales DESC"
        },
        {
            "question": "Highest balance accounts",
            "sql": "SELECT TOP 10 c.CustomerID, c.Name, SUM(soh.TotalDue) as total_balance FROM Sales.Customer c JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID GROUP BY c.CustomerID, c.Name ORDER BY total_balance DESC"
        },
        {
            "question": "List top customers by total order amount",
            "sql": "SELECT TOP 10 c.CustomerID, c.Name, COUNT(soh.SalesOrderID) as order_count, SUM(soh.TotalDue) as total_amount FROM Sales.Customer c JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID GROUP BY c.CustomerID, c.Name ORDER BY total_amount DESC"
        },
    ]
    
    def __init__(self, engine: Engine, dialect: str = None):
        self.engine = engine
        
        # Determine dialect from engine if not explicitly provided
        if dialect is None:
            if hasattr(engine, 'warehouse_type') and engine.warehouse_type:
                self.dialect = engine.warehouse_type.lower()
            else:
                self.dialect = "snowflake"  # fallback default
        else:
            self.dialect = dialect.lower()
        
        self.schema_analyzer = SchemaAnalyzer(engine)
        
        # Initialize LLM based on provider
        if settings.llm_provider == "ollama":
            from langchain_community.llms import Ollama
            self.llm = Ollama(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
            )
        else:
            # Default to Groq
            from langchain_groq import ChatGroq
            self.llm = ChatGroq(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                api_key=settings.groq_api_key,
            )
    
    def _score_table_for_question(self, table: str, question: str) -> float:
        """Score how relevant a table is for the given question (0.0 to 1.0)"""
        question_lower = question.lower()
        table_upper = table.upper()
        
        # Revenue/sales questions MUST use Sales.SalesOrderHeader
        if any(kw in question_lower for kw in ["revenue", "sales", "customers by revenue", "top customers", "customer spending", "total sales"]):
            if "SALESORDERHEADER" in table_upper or "SALES.SALESORDERHEADER" in table_upper:
                return 1.0  # Perfect match
            if "CUSTOMER" in table_upper or "SALES.CUSTOMER" in table_upper:
                return 0.9  # Good for joining
            if "PERSON" in table_upper or "PERSON.PERSON" in table_upper:
                return 0.8  # Good for names
            if "AWBUILDVERSION" in table_upper or "ERRORLOG" in table_upper or "DATABASELOG" in table_upper:
                return 0.0  # Force avoid metadata tables
            return 0.3  # Generic tables
        
        # Customer questions
        if any(kw in question_lower for kw in ["customer", "client", "account"]):
            if "CUSTOMER" in table_upper:
                return 1.0
            if "PERSON" in table_upper:
                return 0.9
            if "SALESORDERHEADER" in table_upper:
                return 0.7
            if "AWBUILDVERSION" in table_upper:
                return 0.0
            return 0.3
        
        # Block metadata tables for all business questions
        if "AWBUILDVERSION" in table_upper or "ERRORLOG" in table_upper or "DATABASELOG" in table_upper:
            return 0.0
        
        return 0.5  # Default neutral score
    
    def _validate_sql_for_question(self, sql: str, question: str) -> tuple:
        """Validate if SQL is semantically correct for the question. Returns (is_valid, reason)"""
        question_lower = question.lower()
        sql_upper = sql.upper()
        
        # Revenue/sales questions validation
        if any(kw in question_lower for kw in ["revenue", "sales", "customers by revenue", "top customers", "customer spending", "total sales"]):
            # Must have SUM or aggregation
            if "SUM(" not in sql_upper and "COUNT(" not in sql_upper and "AVG(" not in sql_upper:
                return False, "Revenue query missing aggregation (SUM/COUNT/AVG)"
            
            # Must use SalesOrderHeader
            if "SALESORDERHEADER" not in sql_upper:
                return False, "Revenue query must use Sales.SalesOrderHeader table"
            
            # Must have GROUP BY
            if "GROUP BY" not in sql_upper:
                return False, "Revenue query must have GROUP BY for aggregation"
            
            # Block metadata tables
            if "AWBUILDVERSION" in sql_upper or "ERRORLOG" in sql_upper or "DATABASELOG" in sql_upper:
                return False, "Query uses irrelevant metadata table"
            
            return True, "Valid revenue query"
        
        # Customer questions validation
        if any(kw in question_lower for kw in ["customer", "client", "account"]):
            if "AWBUILDVERSION" in sql_upper or "ERRORLOG" in sql_upper or "DATABASELOG" in sql_upper:
                return False, "Query uses irrelevant metadata table for customer question"
            return True, "Valid customer query"
        
        return True, "Query passed basic validation"
    
    def generate(self, question: str, context: Optional[str] = None) -> GeneratedSQL:
        """Generate SQL from a natural language question"""
        try:
            # Get schema context
            schema_context = self.schema_analyzer.get_schema_context()
            
            # LINE 1: Build platform-specific system prompt BEFORE LLM call
            system_prompt = None
            try:
                from voxquery.core import platform_dialect_engine
                
                platform = self.dialect or "snowflake"
                system_prompt = platform_dialect_engine.build_system_prompt(
                    platform,
                    schema_context
                )
            except Exception as e:
                logger.warning(f"Failed to build platform-specific prompt: {e}. Using fallback.")
                system_prompt = None
            
            # Build prompt with platform-specific rules
            prompt_text = self._build_prompt(
                question=question,
                schema_context=schema_context,
                context=context,
                system_prompt=system_prompt,  # Pass platform-specific prompt
            )
            
            # Generate SQL with automatic fallback on rate limit
            from voxquery.core.llm_fallback import generate_sql_with_fallback
            
            messages = [
                {"role": "user", "content": prompt_text}
            ]
            
            sql_content = generate_sql_with_fallback(
                messages=messages,
                temperature=0.1,
                max_tokens=1024,
            )
            sql = self._extract_sql(sql_content)
            
            # LAYER 2: Hard runtime rewrite – kill LIMIT
            if self.dialect and self.dialect.lower() == 'sqlserver':
                sql = self.force_tsql(sql)
            
            # VALIDATION: Check if SQL is semantically correct for the question
            is_valid, validation_reason = self._validate_sql_for_question(sql, question)
            
            if not is_valid:
                logger.warning(f"❌ SQL VALIDATION FAILED: {validation_reason}")
                logger.warning(f"Generated SQL: {sql}")
                
                # Apply fallback for revenue queries
                question_lower = question.lower()
                if any(kw in question_lower for kw in ["revenue", "sales", "customers by revenue", "top customers", "customer spending", "total sales"]):
                    logger.info("📋 Applying safe fallback for revenue query")
                    sql = """SELECT TOP 10 
                        c.CustomerID,
                        p.FirstName + ' ' + p.LastName AS CustomerName,
                        SUM(soh.TotalDue) AS total_revenue
                    FROM Sales.Customer c
                    INNER JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
                    INNER JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
                    GROUP BY c.CustomerID, p.FirstName, p.LastName
                    ORDER BY total_revenue DESC"""
            
            # Analyze generated SQL
            query_type = self._determine_query_type(sql)
            tables = self._extract_tables(sql)
            
            return GeneratedSQL(
                sql=sql,
                query_type=query_type,
                confidence=self._calculate_confidence(sql),
                dialect=self.dialect,
                explanation=self._generate_explanation(question, sql),
                tables_used=tables,
            )
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise
    
    def _build_prompt(
        self,
        question: str,
        schema_context: str,
        context: Optional[str] = None,
        system_prompt: str = None,
    ) -> str:
        """Build the prompt for SQL generation"""
        from voxquery.config.dialects.dialect_config import get_dialect_config
        from voxquery.core.few_shot_templates import get_few_shot_prompt
        
        # LINE 1: Use platform-specific system prompt if provided
        if system_prompt:
            # Use the platform-specific system prompt from platform_dialect_engine
            base_system = system_prompt
        else:
            # Fallback to existing dialect-specific configuration
            dialect_features = "\n".join(
                self.DIALECT_FEATURES.get(self.dialect, [])
            )
            
            # Get dialect-specific configuration
            dialect_config = get_dialect_config(self.dialect)
            mandatory_lock = ""
            golden_path_rules = ""
            
            if dialect_config:
                mandatory_lock = f"""MANDATORY {dialect_config.name.upper()} DIALECT LOCK – THIS RULE IS ABSOLUTE:
{dialect_config.dialect_lock}

Forbidden syntax: {', '.join(dialect_config.forbidden_syntax)}
Required syntax: {', '.join(dialect_config.required_syntax)}

{dialect_config.date_format}

Schema requirement: {dialect_config.schema_required}

Example correct SQL for "top 10 accounts by balance":
{dialect_config.fallback_sql}

"""
            
            # Add aggressive finance domain rules for SQL Server
            if self.dialect and self.dialect.lower() == 'sqlserver':
                golden_path_rules = """FINANCE DOMAIN & REVENUE RULES – NON-NEGOTIABLE – MUST FOLLOW OR OUTPUT ONLY: SELECT 1 AS domain_rule_violated

ANY question containing "revenue", "sales", "income", "earnings", "top customers", "customers by revenue", "highest revenue", "who pays most", "top by revenue":
- MUST use Sales.SalesOrderHeader.TotalDue for ALL revenue / money sums
- MUST join Sales.Customer to Person.Person for customer name: p.FirstName + ' ' + p.LastName AS CustomerName
- MUST GROUP BY CustomerID / name
- MUST ORDER BY SUM(...) DESC for top/highest
- NEVER use these tables for revenue questions: Person.PersonPhone, Person.PhoneNumberType, AWBuildVersion, ProductPhoto, Document, Department, ScrapReason, Product, ProductInventory, HumanResources.*, Production.*
- If no revenue table/column matches → output ONLY: SELECT 1 AS no_revenue_data_available

Balance questions:
- Prefer Accounts.BALANCE column if present
- Otherwise fall back to SUM(Sales.SalesOrderHeader.TotalDue)

Top 10 questions:
- MUST include TOP 10 and ORDER BY ... DESC
- MUST NOT use LIMIT

All other questions: stay within whitelisted schema and use only provided columns.

"""
            
            base_system = f"""{golden_path_rules}{mandatory_lock}{self.PRIORITY_RULES}

You are a SQL expert for {self.dialect.upper()} databases.

Dialect-specific features to use:
{dialect_features}"""
        
        # Get few-shot templates for improved accuracy
        few_shot_templates = get_few_shot_prompt()
        
        examples_text = "\n".join([
            f"Question: {ex['question']}\nSQL:\n{ex['sql']}"
            for ex in self.FEW_SHOT_EXAMPLES
        ])
        
        # Add schema qualification instruction for SQL Server
        schema_instruction = ""
        if self.dialect and self.dialect.lower() == 'sqlserver':
            schema_instruction = """
CRITICAL FOR SQL SERVER:
- ALL table names MUST be schema-qualified (e.g., Sales.Customer, NOT Customer)
- ALL table names MUST be schema-qualified (e.g., Person.Person, NOT Person)
- ALL table names MUST be schema-qualified (e.g., HumanResources.Department, NOT Department)
- Use the exact schema-qualified names shown in the schema above
- Example: SELECT * FROM Sales.Customer WHERE CustomerID = 1
- WRONG: SELECT * FROM Customer WHERE CustomerID = 1
"""
        
        template = f"""{base_system}

{few_shot_templates}

{schema_context}
{schema_instruction}

Few-shot examples:
{examples_text}

Additional context: {context or "None"}

Generate ONLY valid {self.dialect.upper()} SQL for this question:
{question}

Return ONLY the SQL query wrapped in ```sql``` tags, with no explanation."""
        
        return template
    
    def _extract_sql(self, text: str) -> str:
        """Extract SQL from LLM response"""
        # Try to extract from ```sql blocks
        sql_pattern = r"```sql\s*(.*?)\s*```"
        matches = re.findall(sql_pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[0].strip()
        
        # Otherwise, assume the entire response is SQL
        return text.strip()
    
    def _determine_query_type(self, sql: str) -> QueryType:
        """Determine the type of SQL query"""
        sql_upper = sql.upper()
        
        if "WITH" in sql_upper:
            return QueryType.CTE
        elif "OVER" in sql_upper or "WINDOW" in sql_upper:
            return QueryType.WINDOW
        elif "GROUP BY" in sql_upper:
            return QueryType.AGGREGATE
        elif "JOIN" in sql_upper:
            return QueryType.JOIN
        elif "SELECT" in sql_upper:
            return QueryType.SELECT
        else:
            return QueryType.UNKNOWN
    
    def _extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL"""
        tables = []
        # Simple regex to find FROM/JOIN table references
        from_pattern = r"(?:FROM|JOIN)\s+(\w+)"
        matches = re.findall(from_pattern, sql, re.IGNORECASE)
        return list(set(matches))
    
    def _calculate_confidence(self, sql: str) -> float:
        """Estimate confidence in generated SQL"""
        confidence = 1.0
        
        # Deduct points for potential issues
        if "???" in sql:
            confidence -= 0.5
        if "TODO" in sql:
            confidence -= 0.3
        if not sql.upper().startswith("SELECT"):
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_explanation(self, question: str, sql: str) -> str:
        """Generate a human-readable explanation of the SQL"""
        return f"This query selects data from {self._extract_tables(sql)} to answer: {question}"
