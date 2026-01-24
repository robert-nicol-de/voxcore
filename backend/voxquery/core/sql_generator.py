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

from voxquery.core.schema_analyzer import SchemaAnalyzer
from voxquery.config import settings

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
    
    # Few-shot examples for financial queries
    FEW_SHOT_EXAMPLES = [
        {
            "question": "Show top 10 clients by YTD revenue",
            "sql": """
SELECT 
    client_id,
    client_name,
    SUM(amount) as ytd_revenue
FROM transactions
WHERE YEAR(transaction_date) = YEAR(GETDATE())
GROUP BY client_id, client_name
ORDER BY ytd_revenue DESC
LIMIT 10
            """
        },
        {
            "question": "Compare Q4 actuals vs budget",
            "sql": """
SELECT 
    account_code,
    account_name,
    SUM(CASE WHEN type = 'ACTUAL' THEN amount ELSE 0 END) as actual_amount,
    SUM(CASE WHEN type = 'BUDGET' THEN amount ELSE 0 END) as budget_amount,
    SUM(CASE WHEN type = 'ACTUAL' THEN amount ELSE 0 END) - 
    SUM(CASE WHEN type = 'BUDGET' THEN amount ELSE 0 END) as variance
FROM gl_transactions
WHERE QUARTER(transaction_date) = 4
    AND YEAR(transaction_date) = YEAR(GETDATE())
GROUP BY account_code, account_name
            """
        },
        {
            "question": "List overdue invoices >60 days grouped by region",
            "sql": """
SELECT 
    c.region,
    COUNT(*) as overdue_count,
    SUM(i.amount) as total_overdue,
    AVG(DATEDIFF(DAY, i.due_date, GETDATE())) as avg_days_overdue
FROM invoices i
JOIN customers c ON i.customer_id = c.customer_id
WHERE i.status = 'UNPAID'
    AND DATEDIFF(DAY, i.due_date, GETDATE()) > 60
GROUP BY c.region
ORDER BY total_overdue DESC
            """
        },
    ]
    
    def __init__(self, engine: Engine, dialect: str = "snowflake"):
        self.engine = engine
        self.dialect = dialect
        self.schema_analyzer = SchemaAnalyzer(engine)
        
        # Initialize LLM based on provider
        if settings.llm_provider == "ollama":
            from langchain_community.llms import Ollama
            self.llm = Ollama(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
            )
        else:
            # Default to OpenAI
            self.llm = ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                api_key=settings.llm_api_key,
            )
    
    def generate(self, question: str, context: Optional[str] = None) -> GeneratedSQL:
        """Generate SQL from a natural language question"""
        try:
            # Get schema context
            schema_context = self.schema_analyzer.get_schema_context()
            
            # Build prompt with examples and schema
            prompt_text = self._build_prompt(
                question=question,
                schema_context=schema_context,
                context=context,
            )
            
            # Generate SQL
            response = self.llm.invoke(prompt_text)
            sql = self._extract_sql(response.content)
            
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
    ) -> str:
        """Build the prompt for SQL generation"""
        dialect_features = "\n".join(
            self.DIALECT_FEATURES.get(self.dialect, [])
        )
        
        examples_text = "\n".join([
            f"Question: {ex['question']}\nSQL:\n{ex['sql']}"
            for ex in self.FEW_SHOT_EXAMPLES
        ])
        
        template = f"""You are a SQL expert for {self.dialect.upper()} databases.

{schema_context}

Dialect-specific features to use:
{dialect_features}

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
