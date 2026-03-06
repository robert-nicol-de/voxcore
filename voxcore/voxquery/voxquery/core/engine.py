"""Main VoxQuery Engine - orchestrates SQL generation and execution"""

# Apply Python 3.14+ compatibility patches FIRST
import sys
sys.path.insert(0, '/'.join(__file__.split('/')[:-2]))  # Add backend to path
try:
    import snowflake_compat
except ImportError:
    pass

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
import pyodbc

from .sql_generator import SQLGenerator, GeneratedSQL
from .schema_analyzer import SchemaAnalyzer
from .conversation import ConversationManager
from .sql_safety import inspect_and_repair, validate_sql
from ..settings import settings

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
        sqlalchemy_engine = None,  # NEW: Accept pre-created engine
    ):
        self.warehouse_type = warehouse_type or settings.warehouse_type
        self.warehouse_host = warehouse_host or settings.warehouse_host
        self.warehouse_user = warehouse_user or settings.warehouse_user
        self.warehouse_password = warehouse_password or settings.warehouse_password
        self.warehouse_database = warehouse_database or settings.warehouse_database
        self.auth_type = auth_type
        
        # Initialize engine - use provided engine or create new one
        if sqlalchemy_engine:
            self.engine = sqlalchemy_engine
            logger.info("✓ Using provided SQLAlchemy engine")
        else:
            self.engine = self._create_engine()
        
        # LAZY INITIALIZATION: Don't create SchemaAnalyzer here
        # It will be created on first access via the property
        self._schema_analyzer = None
        
        # Initialize other components
        self.sql_generator = SQLGenerator(
            self.engine,
            dialect=self.warehouse_type,
        )
        self.conversation = ConversationManager()
        
        logger.info(f"✓ VoxQueryEngine initialized")
        logger.info(f"  Warehouse: {self.warehouse_type}")
        logger.info(f"  Host: {self.warehouse_host}")
        logger.info(f"  Database: {self.warehouse_database}")
    
    @property
    def schema_analyzer(self) -> SchemaAnalyzer:
        """Lazy-initialize SchemaAnalyzer on first access"""
        if self._schema_analyzer is None:
            print(f"\n{'='*80}")
            print(f"LAZY-INITIALIZING SCHEMA ANALYZER")
            print(f"  warehouse_type={self.warehouse_type}")
            print(f"  warehouse_host={self.warehouse_host}")
            print(f"  warehouse_user={self.warehouse_user}")
            print(f"  warehouse_database={self.warehouse_database}")
            print(f"{'='*80}\n")
            
            logger.info("Lazy-initializing SchemaAnalyzer with current engine params")
            logger.info(f"  warehouse_type={self.warehouse_type}")
            logger.info(f"  warehouse_host={self.warehouse_host}")
            logger.info(f"  warehouse_user={self.warehouse_user}")
            logger.info(f"  warehouse_database={self.warehouse_database}")
            
            if not self.warehouse_host or not self.warehouse_user or not self.warehouse_database:
                logger.error(f"❌ CRITICAL: Missing connection parameters!")
                logger.error(f"  warehouse_host={self.warehouse_host}")
                logger.error(f"  warehouse_user={self.warehouse_user}")
                logger.error(f"  warehouse_database={self.warehouse_database}")
            
            self._schema_analyzer = SchemaAnalyzer(
                self.engine,
                warehouse_type=self.warehouse_type,
                warehouse_host=self.warehouse_host,
                warehouse_user=self.warehouse_user,
                warehouse_password=self.warehouse_password,
                warehouse_database=self.warehouse_database,
            )
        return self._schema_analyzer
    
    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine based on warehouse type"""
        from urllib.parse import quote
        
        # For SQL Server: Use raw pyodbc.connect() with unicode_results=True
        # This is the PROVEN approach that actually works
        if self.warehouse_type == "sqlserver":
            return self._create_sqlserver_engine()
        
        # For other warehouses, use standard SQLAlchemy connection strings
        # Handle SQL Server with Windows Auth
        if self.warehouse_type == "sqlserver" and self.auth_type == "windows":
            # For Windows Auth, use trusted_connection
            # Handle localhost/. specially
            host = self.warehouse_host if self.warehouse_host and self.warehouse_host != "." else "localhost"
            connection_string = (
                f"mssql+pyodbc://@{host}/{self.warehouse_database}?"
                f"driver=ODBC+Driver+17+for+SQL+Server&"
                f"trusted_connection=yes&"
                f"CHARSET=UTF8&"
                f"MARS_Connection=Yes"
            )
        else:
            # For Snowflake, extract account identifier properly
            snowflake_account = self.warehouse_host
            if self.warehouse_type == "snowflake" and self.warehouse_host:
                # Remove .snowflakecomputing.com suffix if present
                if ".snowflakecomputing.com" in self.warehouse_host:
                    snowflake_account = self.warehouse_host.replace(".snowflakecomputing.com", "")
                # Keep region-specific format like we08391.af-south-1.aws
                # Don't strip it - Snowflake needs the full account identifier with region
            
            # For Snowflake, handle DATABASE.SCHEMA format
            snowflake_db = self.warehouse_database
            snowflake_schema = "PUBLIC"
            if self.warehouse_type == "snowflake" and self.warehouse_database and "." in self.warehouse_database:
                parts = self.warehouse_database.split(".", 1)
                snowflake_db = parts[0]
                snowflake_schema = parts[1]
            elif self.warehouse_type == "snowflake":
                # If no dot, assume it's just the database name, use PUBLIC schema
                snowflake_db = self.warehouse_database or "VOXQUERYTRAININGFIN2025"
                snowflake_schema = "PUBLIC"
            
            # URL-encode credentials for Snowflake (passwords may contain special chars like !@#$)
            encoded_user = quote(self.warehouse_user, safe='') if self.warehouse_user else ""
            encoded_password = quote(self.warehouse_password, safe='') if self.warehouse_password else ""
            
            connection_strings = {
                "snowflake": (
                    f"snowflake://{encoded_user}:{encoded_password}"
                    f"@{snowflake_account}/{snowflake_db}/{snowflake_schema}"
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
            }
            
            connection_string = connection_strings.get(self.warehouse_type)
            if not connection_string:
                raise ValueError(f"Unsupported warehouse type: {self.warehouse_type}")
        
        logger.info(f"Creating engine for {self.warehouse_type}")
        
        # For Snowflake, we need to pass database/schema as connect_args
        # because SQLAlchemy's Snowflake dialect doesn't read them from the URL
        if self.warehouse_type == "snowflake":
            print(f"\n{'='*80}")
            print(f"SNOWFLAKE CONNECTION STRING PARAMS:")
            print(f"  Database: {snowflake_db}")
            print(f"  Schema: {snowflake_schema}")
            print(f"{'='*80}\n")
            
            engine = create_engine(
                connection_string,
                echo=settings.debug,
                connect_args={
                    "database": snowflake_db,
                    "schema": snowflake_schema,
                }
            )
        else:
            engine = create_engine(connection_string, echo=settings.debug)
        
        return engine
    
    def _create_sqlserver_engine(self) -> Engine:
        """Create SQL Server engine using SQLAlchemy's standard mssql+pyodbc format
        
        Features:
        - Automatic retry with exponential backoff
        - Connection pooling with health checks
        - Comprehensive logging
        - UTF-8 encoding support
        """
        from sqlalchemy import pool
        import time
        
        logger.info(f"\n{'='*80}")
        logger.info(f"CREATING SQL SERVER ENGINE")
        logger.info(f"{'='*80}")
        logger.info(f"Auth Type: {repr(self.auth_type)}")
        logger.info(f"Host: {repr(self.warehouse_host)}")
        logger.info(f"Database: {repr(self.warehouse_database)}")
        logger.info(f"{'='*80}\n")
        
        # Validate inputs
        if not self.warehouse_host:
            raise ValueError("warehouse_host is required")
        if not self.warehouse_database:
            raise ValueError("warehouse_database is required")
        
        # Normalize server name
        server = self.warehouse_host
        if server == ".":
            server = "(local)"  # SQL Server convention for local connections
            logger.info(f"Converted server '.' to '(local)'")
        
        # Build connection URL
        if self.auth_type == "windows":
            connection_url = (
                f"mssql+pyodbc:///?odbc_connect="
                f"Driver={{ODBC Driver 17 for SQL Server}};"
                f"Server={server};"
                f"Database={self.warehouse_database};"
                f"Trusted_Connection=yes"
            )
        else:
            if not self.warehouse_user:
                raise ValueError("warehouse_user is required for SQL authentication")
            if not self.warehouse_password:
                raise ValueError("warehouse_password is required for SQL authentication")
            
            connection_url = (
                f"mssql+pyodbc://{self.warehouse_user}:{self.warehouse_password}"
                f"@{server}/{self.warehouse_database}"
            )
        
        logger.info(f"SQLAlchemy URL: {connection_url[:80]}...")
        
        # Retry logic with exponential backoff
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connection attempt {attempt + 1}/{max_retries}...")
                
                engine = create_engine(
                    connection_url,
                    echo=settings.debug,
                    poolclass=pool.QueuePool,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True,  # Test connections before using them
                    pool_recycle=3600,  # Recycle connections after 1 hour
                    connect_args={
                        "timeout": 10,
                    }
                )
                
                # Test the connection
                logger.info("Testing connection...")
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT @@VERSION"))
                    version = result.scalar()
                    logger.info(f"✓ Connection test succeeded")
                    logger.info(f"  SQL Server Version: {version[:60]}...")
                    
                    # Debug: Show current database context
                    db_result = conn.execute(text("SELECT DB_NAME()"))
                    current_db = db_result.scalar()
                    print(f"\n{'='*80}")
                    print(f"CONNECTED TO: Database={current_db}")
                    print(f"{'='*80}\n")
                
                logger.info(f"{'='*80}\n")
                return engine
            
            except Exception as e:
                logger.error(f"✗ Connection attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"✗ All {max_retries} connection attempts failed")
                    logger.error(f"Exception Type: {type(e).__name__}")
                    logger.error(f"Exception Args: {e.args}")
                    logger.info(f"{'='*80}\n")
                    raise
    
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
            # Add to conversation for audit trail only
            self.conversation.add_user_message(question)
            
            # DO NOT pass conversation context to SQL generator
            # This prevents token bloat and Groq degradation
            context = None
            
            # Generate SQL
            logger.info(f"Generating SQL for: {question}")
            generated_sql = self.sql_generator.generate(question, context)
            
            # LAYER 2: PLATFORM DIALECT ENGINE – REWRITE & VALIDATE IMMEDIATELY AFTER LLM
            # This is the critical interception point for all platforms
            final_sql = generated_sql.sql
            if self.warehouse_type:
                logger.info(f"[LAYER 2] Applying platform dialect engine for {self.warehouse_type}")
                from voxquery.core import platform_dialect_engine
                
                dialect_result = platform_dialect_engine.process_sql(final_sql, self.warehouse_type)
                final_sql = dialect_result["final_sql"]
                
                if dialect_result["fallback_used"]:
                    logger.warning(f"[LAYER 2] Fallback query used due to validation failure")
                    logger.warning(f"[LAYER 2] Issues: {dialect_result['issues']}")
                    generated_sql.confidence = 0.0
                else:
                    logger.info(f"[LAYER 2] SQL rewritten and validated successfully")
                    logger.info(f"[LAYER 2] Validation score: {dialect_result['score']}")
                
                logger.info(f"[LAYER 2] Final SQL: {final_sql[:100]}...")
            
            # LEVEL 2 VALIDATION: Table & Column Whitelist + Safety Rules
            # This is the production-ready safety gate
            confidence = generated_sql.confidence
            validation_reason = None
            
            if final_sql:
                # FORCE SCHEMA ANALYSIS BEFORE VALIDATION
                # Ensure schema_cache is populated
                if not self.schema_analyzer.schema_cache:
                    logger.info("[SCHEMA FORCE LOAD] Cache empty — analyzing tables now")
                    self.schema_analyzer.analyze_all_tables()
                
                # Get schema for validation
                schema_tables = set(self.schema_analyzer.schema_cache.keys()) if self.schema_analyzer.schema_cache else set()
                schema_columns = {}
                
                for table_name, table_schema in (self.schema_analyzer.schema_cache or {}).items():
                    schema_columns[table_name] = set(table_schema.columns.keys()) if table_schema.columns else set()
                
                # Run Level 2 validation (table & column whitelist + safety rules)
                is_safe, reason, validation_score = validate_sql(
                    final_sql,
                    schema_tables,
                    schema_columns,
                    dialect=self.warehouse_type
                )
                
                validation_reason = reason
                
                # If validation fails, use fallback
                if not is_safe:
                    logger.warning(f"⚠️  Level 2 validation FAILED: {reason}")
                    if schema_tables:
                        safe_table = next(iter(schema_tables))
                        # Use TOP for SQL Server, LIMIT for others
                        if self.warehouse_type and self.warehouse_type.lower() == 'sqlserver':
                            final_sql = f"SELECT TOP 10 * FROM {safe_table}"
                        else:
                            final_sql = f"SELECT * FROM {safe_table} LIMIT 10"
                        confidence = 0.0
                        logger.warning(f"⚠️  Using fallback query: {final_sql}")
                    else:
                        final_sql = "SELECT 1 AS no_matching_schema"
                        confidence = 0.0
                else:
                    # Validation passed, but adjust confidence if score is low
                    if validation_score < 0.95:
                        confidence = min(confidence, validation_score)
                        logger.warning(f"⚠️  Confidence reduced to {confidence:.2f} due to validation warnings")
            
            result = {
                "question": question,
                "sql": final_sql,
                "query_type": generated_sql.query_type.value,
                "confidence": confidence,
                "explanation": generated_sql.explanation,
                "tables_used": generated_sql.tables_used,
                "validation_reason": validation_reason,
                "data": None,
                "execution_time_ms": 0.0,
                "error": None,
                "model_fingerprint": f"Groq / llama-3.3-70b-versatile | Dialect: {self.warehouse_type}",
            }
            
            # Execute if requested
            if execute:
                logger.info("Executing query")
                
                # Dry run first if enabled
                if dry_run and self._supports_dry_run():
                    self._dry_run_query(final_sql)
                
                # Execute actual query
                query_result = self._execute_query(final_sql)
                result.update({
                    "data": query_result.data,
                    "execution_time_ms": query_result.execution_time_ms,
                    "error": query_result.error,
                    "row_count": query_result.row_count,
                })
            
            # Update conversation context for audit only
            self.conversation.update_context("last_query", final_sql)
            self.conversation.update_context("tables_accessed", generated_sql.tables_used)
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            import traceback
            traceback.print_exc()
            return {
                "question": question,
                "error": str(e),
                "sql": "",
                "data": None,
                "query_type": "unknown",
                "confidence": 0.0,
                "explanation": f"Error: {str(e)}",
                "tables_used": [],
                "validation_reason": None,
                "execution_time_ms": 0.0,
                "row_count": 0,
                "model_fingerprint": f"Groq / llama-3.3-70b-versatile | Dialect: {self.warehouse_type}",
            }
    async def ask_async(self, question: str, context: str = None):
        """Execute a natural language question (async version)

        Args:
            question: Natural language question
            context: Optional context for the question

        Returns:
            Dictionary with results or error
        """
        try:
            # Generate SQL
            generated_sql = self.sql_generator.generate(question, context)

            # Validate + rewrite with dialect engine
            validation = self.dialect_engine.process_sql(
                generated_sql,
                self.current_platform
            )

            # Execute
            cursor = self.connection.cursor()
            cursor.execute(validation.final_sql)

            # Get results
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            cursor.close()

            return {
                "success": True,
                "question": question,
                "generated_sql": generated_sql,
                "final_sql": validation.final_sql,
                "was_rewritten": validation.was_rewritten,
                "results": [dict(zip(columns, row)) for row in rows],
                "row_count": len(rows),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
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
        from sqlalchemy import text
        try:
            explain_sql = f"EXPLAIN {sql}"
            with self.engine.connect() as conn:
                conn.execute(text(explain_sql))
            logger.info("Dry-run successful")
        except Exception as e:
            logger.warning(f"Dry-run failed: {e}")
    
    def _execute_query(self, sql: str) -> QueryResult:
        """Execute a SQL query"""
        import time
        from sqlalchemy import text
        
        try:
            # Validate SQL is not None
            if not sql:
                logger.error("SQL is None or empty")
                return QueryResult(
                    success=False,
                    error="SQL is None or empty",
                    execution_time_ms=0.0,
                )
            
            logger.debug("Executing SQL: %s", sql)
            start_time = time.time()
            
            logger.info(f"\n{'='*80}")
            logger.info(f"QUERY EXECUTION - CONNECTION DETAILS")
            logger.info(f"{'='*80}")
            logger.info(f"Warehouse Type: {self.warehouse_type}")
            logger.info(f"Warehouse Host: {self.warehouse_host}")
            logger.info(f"Warehouse Database: {self.warehouse_database}")
            logger.info(f"Auth Type: {self.auth_type}")
            logger.info(f"Engine URL: {self.engine.url}")
            logger.info(f"Engine Dialect: {self.engine.dialect.name}")
            logger.info(f"SQL: {sql[:200]}...")
            logger.info(f"{'='*80}\n")
            
            # For Snowflake, use raw connector to bypass SQLAlchemy issues
            if self.warehouse_type == "snowflake":
                logger.info("Using raw Snowflake connector (bypassing SQLAlchemy)")
                return self._execute_query_snowflake_raw(sql, start_time)
            
            # For other databases, use SQLAlchemy
            logger.debug("Acquiring connection from engine...")
            with self.engine.connect() as conn:
                logger.debug("Connection acquired: %s", conn)
                
                logger.debug("Creating text() object from SQL...")
                sql_text = text(sql)
                logger.debug("text() object created: %s", sql_text)
                
                logger.debug("Executing SQL via connection.execute()...")
                result = conn.execute(sql_text)
                logger.debug("execute() returned: %s", result)
                logger.debug("execute() type: %s", type(result))
                
                if result is None:
                    logger.warning("connection.execute() returned None - likely DDL")
                    return QueryResult(
                        success=True,
                        data=[],
                        execution_time_ms=(time.time() - start_time) * 1000,
                        row_count=0,
                    )
                
                logger.debug("Fetching all rows...")
                rows = result.fetchall()
                logger.debug("fetchall() returned %d rows", len(rows) if rows else 0)
                
                logger.debug("Getting column names...")
                columns = list(result.keys()) if result.keys() else []
                logger.debug("Columns: %s", columns)
                
                # Convert to list of dicts with native Python types
                data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Convert to native Python types
                        if value is None:
                            row_dict[col] = None
                        elif isinstance(value, (int, float, str, bool)):
                            row_dict[col] = value
                        else:
                            # Convert other types to string safely
                            try:
                                row_dict[col] = str(value)
                            except:
                                row_dict[col] = repr(value)
                    data.append(row_dict)
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                logger.info(f"✓ Query executed successfully in {execution_time_ms:.2f}ms")
                logger.info(f"  Rows returned: {len(rows)}")
                logger.info(f"  Columns: {columns}")
                
                return QueryResult(
                    success=True,
                    data=data[:settings.max_result_rows],
                    execution_time_ms=execution_time_ms,
                    row_count=len(rows),
                )
        except Exception as e:
            # Log raw exception args for debugging (before stringifying)
            try:
                logger.error("Raw exception args: %s", e.args)
                logger.error("Exception repr: %r", e)
            except:
                pass
            
            # For pyodbc errors, try to extract the message safely
            safe_msg = None
            if hasattr(e, 'args') and len(e.args) > 1:
                try:
                    # pyodbc.Error has (state, msg_bytes) tuple
                    if isinstance(e.args[1], bytes):
                        safe_msg = e.args[1].decode('utf-8', errors='replace')
                    else:
                        safe_msg = str(e.args[1])
                except:
                    pass
            
            # Nuclear-proof exception handling to prevent encoding bombs
            if not safe_msg:
                try:
                    # Try standard string conversion first
                    safe_msg = str(e)
                except:
                    try:
                        # Fallback to repr() which escapes problematic bytes
                        safe_msg = repr(e)
                    except:
                        try:
                            # Last resort: encode/decode with replacement
                            safe_msg = str(e).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                        except:
                            # If all else fails, use a generic message
                            safe_msg = "Unknown database error (encoding issue)"
            
            # Log safely without triggering encoding bomb
            try:
                logger.error(f"Query execution failed: {safe_msg}", exc_info=True)
            except:
                logger.error("Query execution failed (error message encoding issue)", exc_info=True)
            
            return QueryResult(
                success=False,
                error=safe_msg[:500],  # Truncate to prevent huge error messages
                execution_time_ms=0.0,
            )
    
    def _execute_query_snowflake_raw(self, sql: str, start_time: float) -> QueryResult:
        """Execute query using raw Snowflake connector (bypasses SQLAlchemy)"""
        import time
        import snowflake.connector
        
        try:
            logger.info("Connecting to Snowflake with raw connector...")
            
            # Create fresh connection with context
            conn_params = {
                'account': self.warehouse_host,
                'user': self.warehouse_user,
                'password': self.warehouse_password,
                'warehouse': 'COMPUTE_WH',
                'role': 'ACCOUNTADMIN',
            }
            
            conn = snowflake.connector.connect(**conn_params)
            cursor = conn.cursor()
            
            try:
                # Set context - use FINANCE schema where the tables are
                logger.info("Setting Snowflake context...")
                cursor.execute(f'USE DATABASE "{self.warehouse_database}"')
                cursor.execute('USE SCHEMA "FINANCE"')
                logger.info("✓ Context set to FINANCE schema")
                
                # Execute query
                logger.info("Executing query...")
                cursor.execute(sql)
                
                # Fetch results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                logger.info(f"✓ Query executed: {len(rows)} rows, {len(columns)} columns")
                
                # Convert to list of dicts
                data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        if value is None:
                            row_dict[col] = None
                        elif isinstance(value, (int, float, str, bool)):
                            row_dict[col] = value
                        else:
                            try:
                                row_dict[col] = str(value)
                            except:
                                row_dict[col] = repr(value)
                    data.append(row_dict)
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Log success with row count and execution time
                logger.info(f"[SUCCESS] Executed in {execution_time_ms/1000:.2f}s, {len(rows)} rows returned")
                
                return QueryResult(
                    success=True,
                    data=data[:settings.max_result_rows],
                    execution_time_ms=execution_time_ms,
                    row_count=len(rows),
                )
            
            finally:
                cursor.close()
                conn.close()
        
        except Exception as e:
            logger.error(f"Raw Snowflake query execution failed: {e}", exc_info=True)
            safe_msg = str(e)
            return QueryResult(
                success=False,
                error=safe_msg[:500],
                execution_time_ms=(time.time() - start_time) * 1000,
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
            # Build schema summary
            schema_summary = self._build_schema_summary(schema)
            
            # Create prompt that generates SPECIFIC, BUSINESS-FOCUSED questions
            prompt_text = f"""You are a business analyst. Generate {limit} SPECIFIC, ACTIONABLE questions for this database.

Schema:
{schema_summary}

RULES:
1. Questions must be SPECIFIC to the actual tables and columns
2. Ask about REAL business metrics (revenue, count, average, top items, trends)
3. Use actual column names from the schema
4. Avoid generic questions like "How many records?"
5. Focus on insights, not just data retrieval
6. Make questions that would help a business user understand their data

Generate ONLY a JSON array of questions, no other text.
Example: ["Which product has the highest sales?", "What is the average order value?"]"""
            
            # Generate questions using Groq LLM
            try:
                from langchain_groq import ChatGroq
                import os
                from dotenv import load_dotenv
                
                load_dotenv()
                groq_api_key = os.getenv("GROQ_API_KEY")
                if not groq_api_key:
                    raise ValueError("GROQ_API_KEY not set")
                
                llm = ChatGroq(
                    model=settings.llm_model,  # llama-3.1-70b-versatile
                    temperature=0.5,  # Slightly higher for variety in questions
                    max_tokens=500,
                    api_key=groq_api_key,
                )
                logger.info("✓ Using Groq for question generation")
            except Exception as e:
                logger.error(f"✗ Groq initialization failed: {e}")
                return self._get_default_questions(schema, limit)
            
            response = llm.invoke(prompt_text)
            
            # Parse response
            import json
            import re
            
            # Extract JSON from response
            response_text = response.content if hasattr(response, 'content') else str(response)
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if json_match:
                questions = json.loads(json_match.group())
                # Filter out generic questions
                questions = [q for q in questions if not self._is_generic_question(q)]
                return questions[:limit]
            else:
                logger.warning("Could not parse LLM response for questions")
                return self._get_default_questions(schema, limit)
        
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self._get_default_questions(schema, limit)
    
    def _is_generic_question(self, question: str) -> bool:
        """Check if a question is too generic"""
        generic_patterns = [
            "how many records",
            "how many rows",
            "what columns",
            "show me the data",
            "list all",
            "get all",
            "show all records",
        ]
        question_lower = question.lower()
        return any(pattern in question_lower for pattern in generic_patterns)
    
    def _build_schema_summary(self, schema: Dict[str, Any]) -> str:
        """Build a concise schema summary for LLM"""
        if not schema:
            return "No tables available in the schema."
        
        summary_lines = []
        
        for table_name, table_info in list(schema.items())[:10]:  # Limit to 10 tables
            columns = table_info.get("columns", {})
            col_names = ", ".join(list(columns.keys())[:8])  # Limit columns shown
            row_count = table_info.get("row_count", "?")
            summary_lines.append(f"- {table_name} ({row_count} rows): {col_names}")
        
        if not summary_lines:
            return "No tables available in the schema."
        
        return "\n".join(summary_lines)
        
        return "\n".join(summary_lines)
    
    def _get_default_questions(self, schema: Dict[str, Any], limit: int) -> List[str]:
        """Fallback: Generate smart questions from schema"""
        questions = []
        
        # Get table and column names
        table_names = list(schema.keys())[:3]
        
        if table_names:
            # Generate specific questions based on actual tables
            for table in table_names:
                table_info = schema.get(table, {})
                columns = list(table_info.get("columns", {}).keys())
                
                # Generate questions based on column types
                if columns:
                    # Question 1: Count by first column
                    if len(columns) > 1:
                        questions.append(f"How many records are in the {table} table?")
                    
                    # Question 2: Top values
                    if len(columns) > 1:
                        questions.append(f"What are the top 10 values in {columns[0]} from {table}?")
                    
                    # Question 3: Aggregation
                    if len(columns) > 2:
                        questions.append(f"Show me {columns[0]} grouped by {columns[1]} from {table}")
        
        # Add generic but useful questions
        if not questions:
            questions.extend([
                "Show me the first 10 records",
                "What tables are available?",
                "Show me a summary of the data",
            ])
        
        # Add more specific questions
        questions.extend([
            "What is the most common value in the first column?",
            "Show me records sorted by the most recent date",
            "What are the unique values in the first column?",
        ])
        
        return questions[:limit]
    
    def close(self) -> None:
        """Close database connection"""
        self.engine.dispose()
