"""Main VoxQuery Engine - orchestrates SQL generation and execution"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from voxquery.core.sql_generator import SQLGenerator, GeneratedSQL
from voxquery.core.schema_analyzer import SchemaAnalyzer
from voxquery.core.conversation import ConversationManager
from voxquery.config import settings

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of a query execution"""
    success: bool
    data: Optional[List[Dict]] = None
    error: Optional[str] = None
    sql: Optional[str] = None
    execution_time_ms: float = 0.0
    row_count: int = 0


class VoxQueryEngine:
    """Main engine for VoxQuery functionality"""
    
    def __init__(
        self,
        warehouse_type: str = "snowflake",
        warehouse_host: str = None,
        warehouse_user: str = None,
        warehouse_password: str = None,
        warehouse_database: str = None,
        auth_type: str = "sql",
    ):
        self.warehouse_type = warehouse_type or settings.warehouse_type
        self.warehouse_host = warehouse_host or settings.warehouse_host
        self.warehouse_user = warehouse_user or settings.warehouse_user
        self.warehouse_password = warehouse_password or settings.warehouse_password
        self.warehouse_database = warehouse_database or settings.warehouse_database
        self.auth_type = auth_type
        
        # Initialize engine
        self.engine = self._create_engine()
        
        # Initialize components
        self.schema_analyzer = SchemaAnalyzer(self.engine)
        self.sql_generator = SQLGenerator(self.engine, dialect=self.warehouse_type)
        self.conversation = ConversationManager()
    
    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine based on warehouse type"""
        
        # Handle SQL Server with Windows Auth
        if self.warehouse_type == "sqlserver" and self.auth_type == "windows":
            # For Windows Auth, use trusted_connection
            # Handle localhost/. specially
            host = self.warehouse_host if self.warehouse_host and self.warehouse_host != "." else "localhost"
            connection_string = (
                f"mssql+pyodbc://@{host}/{self.warehouse_database}?"
                f"driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
            )
        else:
            connection_strings = {
                "snowflake": (
                    f"snowflake://{self.warehouse_user}:{self.warehouse_password}"
                    f"@{self.warehouse_host}/{self.warehouse_database}"
                ),
                "redshift": (
                    f"redshift+psycopg2://{self.warehouse_user}:{self.warehouse_password}"
                    f"@{self.warehouse_host}:5439/{self.warehouse_database}"
                ),
                "bigquery": (
                    f"bigquery://{self.warehouse_database}"
                ),
                "postgres": (
                    f"postgresql://{self.warehouse_user}:{self.warehouse_password}"
                    f"@{self.warehouse_host}:5432/{self.warehouse_database}"
                ),
                "sqlserver": (
                    f"mssql+pyodbc://{self.warehouse_user}:{self.warehouse_password}"
                    f"@{self.warehouse_host}/{self.warehouse_database}?"
                    f"driver=ODBC+Driver+17+for+SQL+Server"
                ),
            }
            
            connection_string = connection_strings.get(self.warehouse_type)
            if not connection_string:
                raise ValueError(f"Unsupported warehouse type: {self.warehouse_type}")
        
        logger.info(f"Creating engine for {self.warehouse_type}")
        return create_engine(connection_string, echo=settings.debug)
    
    def ask(
        self,
        question: str,
        execute: bool = False,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Ask a question and optionally execute the generated SQL
        
        Args:
            question: Natural language question
            execute: Whether to execute the generated SQL
            dry_run: Run EXPLAIN/dry-run before execution
        
        Returns:
            Dictionary with generated SQL and optionally results
        """
        try:
            # Add to conversation
            self.conversation.add_user_message(question)
            
            # Get conversation context for follow-ups
            context = self.conversation.get_conversation_context()
            
            # Generate SQL
            logger.info(f"Generating SQL for: {question}")
            generated_sql = self.sql_generator.generate(question, context)
            
            result = {
                "question": question,
                "sql": generated_sql.sql,
                "query_type": generated_sql.query_type.value,
                "confidence": generated_sql.confidence,
                "explanation": generated_sql.explanation,
                "tables_used": generated_sql.tables_used,
                "data": None,
                "execution_time_ms": 0.0,
                "error": None,
            }
            
            # Execute if requested
            if execute:
                logger.info("Executing query")
                
                # Dry run first if enabled
                if dry_run and self._supports_dry_run():
                    self._dry_run_query(generated_sql.sql)
                
                # Execute actual query
                query_result = self._execute_query(generated_sql.sql)
                result.update({
                    "data": query_result.data,
                    "execution_time_ms": query_result.execution_time_ms,
                    "error": query_result.error,
                    "row_count": query_result.row_count,
                })
            
            # Update conversation context
            self.conversation.update_context("last_query", generated_sql.sql)
            self.conversation.update_context("tables_accessed", generated_sql.tables_used)
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                "question": question,
                "error": str(e),
                "sql": None,
                "data": None,
            }
    
    def _supports_dry_run(self) -> bool:
        """Check if warehouse supports dry-run"""
        dry_run_supported = {
            "snowflake": False,  # Snowflake doesn't have EXPLAIN directly
            "redshift": True,
            "bigquery": True,
            "postgres": True,
            "sqlserver": True,
        }
        return dry_run_supported.get(self.warehouse_type, False)
    
    def _dry_run_query(self, sql: str) -> None:
        """Run dry-run/explain query"""
        try:
            explain_sql = f"EXPLAIN {sql}"
            with self.engine.connect() as conn:
                conn.execute(explain_sql)
            logger.info("Dry-run successful")
        except Exception as e:
            logger.warning(f"Dry-run failed: {e}")
    
    def _execute_query(self, sql: str) -> QueryResult:
        """Execute a SQL query"""
        import time
        
        try:
            start_time = time.time()
            
            with self.engine.connect() as conn:
                result = conn.execute(sql)
                
                # Fetch results
                rows = result.fetchall()
                columns = result.keys()
                
                # Convert to list of dicts
                data = [
                    {col: row[i] for i, col in enumerate(columns)}
                    for row in rows
                ]
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                return QueryResult(
                    success=True,
                    data=data[:settings.max_result_rows],
                    execution_time_ms=execution_time_ms,
                    row_count=len(rows),
                )
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return QueryResult(
                success=False,
                error=str(e),
                execution_time_ms=0.0,
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema"""
        schemas = self.schema_analyzer.analyze_all_tables()
        return {
            table_name: schema.to_dict()
            for table_name, schema in schemas.items()
        }
    
    def generate_questions_from_schema(self, schema: Dict[str, Any], limit: int = 8) -> List[str]:
        """Generate smart questions based on database schema"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate
            
            # Build schema summary
            schema_summary = self._build_schema_summary(schema)
            
            # Create prompt for question generation
            prompt = ChatPromptTemplate.from_template("""
You are a business analyst helping users explore their data warehouse.

Based on the following database schema, generate {limit} practical, business-focused questions that users might ask.

Database Schema:
{schema_summary}

Generate questions that:
1. Are specific to the tables and columns available
2. Represent common business queries (revenue, trends, rankings, comparisons)
3. Are phrased in natural, conversational English
4. Don't require joins across too many tables
5. Are answerable with the available data

Return ONLY a JSON array of question strings, no other text.
Example format: ["Question 1?", "Question 2?", "Question 3?"]
""")
            
            # Generate questions using LLM
            if settings.llm_provider == "ollama":
                from langchain_community.llms import Ollama
                llm = Ollama(
                    model=settings.llm_model,
                    temperature=0.7,
                )
            else:
                llm = ChatOpenAI(
                    model=settings.llm_model,
                    temperature=0.7,
                    api_key=settings.llm_api_key,
                )
            
            chain = prompt | llm
            response = chain.invoke({
                "limit": limit,
                "schema_summary": schema_summary,
            })
            
            # Parse response
            import json
            import re
            
            # Extract JSON from response
            response_text = response.content
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if json_match:
                questions = json.loads(json_match.group())
                return questions[:limit]
            else:
                logger.warning("Could not parse LLM response for questions")
                return self._get_default_questions(schema, limit)
        
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self._get_default_questions(schema, limit)
    
    def _build_schema_summary(self, schema: Dict[str, Any]) -> str:
        """Build a concise schema summary for LLM"""
        summary_lines = []
        
        for table_name, table_info in list(schema.items())[:10]:  # Limit to 10 tables
            columns = table_info.get("columns", {})
            col_names = ", ".join(list(columns.keys())[:8])  # Limit columns shown
            row_count = table_info.get("row_count", "?")
            summary_lines.append(f"- {table_name} ({row_count} rows): {col_names}")
        
        return "\n".join(summary_lines)
    
    def _get_default_questions(self, schema: Dict[str, Any], limit: int) -> List[str]:
        """Fallback: Generate basic questions from schema"""
        questions = []
        
        # Get table names
        table_names = list(schema.keys())[:3]
        
        if table_names:
            # Generate basic questions
            for table in table_names:
                questions.append(f"Show me the top 10 records from {table}")
                questions.append(f"How many rows are in {table}?")
                questions.append(f"What columns are in {table}?")
        
        # Add generic questions
        questions.extend([
            "Show me a summary of the data",
            "What are the most recent records?",
            "Show me data grouped by date",
        ])
        
        return questions[:limit]
    
    def close(self) -> None:
        """Close database connection"""
        self.engine.dispose()
