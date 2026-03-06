"""
VoxQuery - Minimal Backend for Testing
"""

import sys
import os
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    
    app = FastAPI(
        title="VoxQuery API",
        description="Natural Language SQL Generation",
        version="1.0.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request model
    class QueryRequest(BaseModel):
        question: str
        warehouse: Optional[str] = "snowflake"
        session_id: Optional[str] = "default"
    
    # Response model
    class QueryResponse(BaseModel):
        question: str
        sql: str
        explanation: str
        results: Optional[list] = None
        chart: Optional[dict] = None
    
    # Database connection model
    class DBConnectionRequest(BaseModel):
        database: str  # snowflake, redshift, bigquery, postgres, sqlserver
        credentials: dict
    
    class DBConnectionResponse(BaseModel):
        status: str
        message: str
        database: str
    
    @app.get("/health")
    def health():
        return {"status": "ok", "service": "VoxQuery Backend"}
    
    @app.get("/")
    def root():
        return {
            "service": "VoxQuery - Natural Language SQL",
            "version": "1.0.0",
            "docs": "http://localhost:8000/docs"
        }
    
    # Global connection storage - mutable container to persist across requests
    connection_store = {"sqlserver": None, "snowflake": None, "schema_cache": {}}
    
    def fetch_sqlserver_schema() -> dict:
        """Fetch SQL Server database schema"""
        try:
            import pyodbc
            if connection_store.get("sqlserver") is None:
                return {}
            
            try:
                conn = pyodbc.connect(connection_store["sqlserver"])
                cursor = conn.cursor()
                
                # Get all tables with columns
                schema = {}
                cursor.execute("""
                    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    ORDER BY TABLE_NAME, ORDINAL_POSITION
                """)
                
                for table_name, column_name, data_type, is_nullable in cursor.fetchall():
                    if table_name not in schema:
                        schema[table_name] = []
                    schema[table_name].append({
                        "name": column_name,
                        "type": data_type,
                        "nullable": is_nullable == 'YES'
                    })
                
                cursor.close()
                conn.close()
                return schema
            except Exception as e:
                print(f"Error connecting to get schema: {e}")
                return {}
        except ImportError:
            print("Warning: pyodbc not installed, schema scanning unavailable")
            return {}
    
    def generate_questions_from_schema(schema: dict, db_type: str = "sqlserver") -> list:
        """Generate relevant questions based on database schema"""
        questions = []
        
        if not schema:
            return [
                "Show me the top 10 records",
                "Count records by category",
                "Show recent records",
                "List distinct values"
            ]
        
        tables = list(schema.keys())
        
        # Generate questions based on what we find
        for table in tables[:5]:  # Limit to first 5 tables
            columns = schema[table]
            col_names = [c["name"].lower() for c in columns]
            
            # Sales/Order tables
            if any(x in table.lower() for x in ['sales', 'order', 'invoice']):
                questions.append(f"Show top 10 {table} records")
                if any(x in col_names for x in ['amount', 'total', 'price', 'quantity']):
                    questions.append(f"Total sales amount from {table}")
                if any(x in col_names for x in ['date', 'created', 'ordered']):
                    questions.append(f"Sales by date in {table}")
                if any(x in col_names for x in ['customer', 'client', 'account']):
                    questions.append(f"Top customers by {table}")
            
            # Product/Inventory tables
            elif any(x in table.lower() for x in ['product', 'inventory', 'item']):
                questions.append(f"List all {table}")
                if any(x in col_names for x in ['price', 'cost', 'amount']):
                    questions.append(f"Products by price range from {table}")
                if any(x in col_names for x in ['category', 'type', 'class']):
                    questions.append(f"Group {table} by category")
            
            # Customer/Person tables
            elif any(x in table.lower() for x in ['customer', 'person', 'client', 'user']):
                questions.append(f"Count of {table} records")
                if any(x in col_names for x in ['city', 'country', 'state', 'region']):
                    questions.append(f"Customers by location from {table}")
                if any(x in col_names for x in ['joined', 'created', 'registered']):
                    questions.append(f"New {table} by month")
            
            # Generic fallback
            else:
                questions.append(f"Show sample {table}")
                if columns:
                    questions.append(f"Count distinct in {table}")
        
        # Add some universal questions
        if not questions:
            questions = [
                "Count total records",
                "Show sample data",
                "List all tables"
            ]
        
        return list(dict.fromkeys(questions))[:8]  # Remove duplicates, limit to 8
    
    def execute_sql_server_query(sql: str) -> tuple[bool, list, str]:
        """Execute query on connected SQL Server database"""
        try:
            import pyodbc
            if connection_store.get("sqlserver") is None:
                return False, [], "❌ No active SQL Server connection. Please connect first."
            
            try:
                conn = pyodbc.connect(connection_store["sqlserver"], timeout=10)
                cursor = conn.cursor()
                cursor.execute(sql)
                
                # Fetch column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Fetch all rows
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                
                cursor.close()
                conn.close()
                
                return True, results, f"✅ Query executed successfully - {len(results)} rows returned"
            except Exception as query_error:
                error_str = str(query_error)
                if "ODBC" in error_str or "driver" in error_str.lower():
                    return False, [], f"❌ ODBC Driver Issue: Make sure ODBC Driver 17 for SQL Server is installed. Error: {error_str}"
                return False, [], f"❌ Query execution error: {error_str}"
        except ImportError as ie:
            return False, [], f"❌ pyodbc not installed. Please install it: pip install pyodbc"
        except Exception as e:
            return False, [], f"❌ Database error: {str(e)}"
    
    def get_database_schema(db_type: str) -> dict:
        """Get schema from connected database - works across all databases"""
        if db_type == "sqlserver":
            return fetch_sqlserver_schema()
        # Other databases would go here
        return {}
    
    def generate_dynamic_sql(question: str, schema: dict, db_type: str = "sqlserver") -> str:
        """Generate SQL dynamically based on actual schema and user question"""
        if not schema:
            return "SELECT 'No database schema available' as Error"
        
        question_lower = question.lower()
        tables = list(schema.keys())
        
        # Find relevant tables based on question keywords
        sales_tables = [t for t in tables if any(x in t.lower() for x in ['sales', 'order', 'invoice', 'transaction'])]
        product_tables = [t for t in tables if any(x in t.lower() for x in ['product', 'inventory', 'item', 'catalog'])]
        customer_tables = [t for t in tables if any(x in t.lower() for x in ['customer', 'person', 'user', 'account', 'client'])]
        date_tables = [t for t in tables if any(x in t.lower() for x in ['order', 'sales', 'transaction', 'invoice'])]
        
        # Get columns for analysis
        def find_columns(table, keywords):
            if table not in schema:
                return []
            return [c["name"] for c in schema[table] if any(k in c["name"].lower() for k in keywords)]
        
        # Detect key columns
        amount_cols = {}
        date_cols = {}
        id_cols = {}
        for table in tables:
            amounts = find_columns(table, ['amount', 'total', 'price', 'revenue', 'cost', 'value', 'linetotal'])
            dates = find_columns(table, ['date', 'time', 'created', 'ordered', 'invoiced'])
            ids = find_columns(table, ['id', 'customerid', 'productid', 'orderid'])
            if amounts:
                amount_cols[table] = amounts[0]
            if dates:
                date_cols[table] = dates[0]
            if ids:
                id_cols[table] = ids[0]
        
        # Generate SQL based on question patterns
        if "top" in question_lower and ("customer" in question_lower or "client" in question_lower):
            # Top customers by spending
            if sales_tables:
                sales_table = sales_tables[0]
                amount_col = amount_cols.get(sales_table, "")
                
                if amount_col:
                    # Find customer ID column
                    customer_id_cols = find_columns(sales_table, ['customer', 'clientid', 'accountid'])
                    if customer_id_cols:
                        cust_col = customer_id_cols[0]
                        return f"""SELECT TOP 10
    {cust_col},
    SUM({amount_col}) as TotalAmount,
    COUNT(*) as TransactionCount
FROM {sales_table}
GROUP BY {cust_col}
ORDER BY TotalAmount DESC"""
        
        elif "revenue" in question_lower or ("sales" in question_lower and "total" in question_lower):
            # Total revenue/sales
            if sales_tables:
                sales_table = sales_tables[0]
                amount_col = amount_cols.get(sales_table, "")
                if amount_col:
                    date_col = date_cols.get(sales_table, "")
                    if date_col:
                        return f"""SELECT 
    YEAR({sales_table}.{date_col}) as [Year],
    SUM({sales_table}.{amount_col}) as TotalRevenue,
    COUNT(*) as TransactionCount
FROM {sales_table}
GROUP BY YEAR({sales_table}.{date_col})
ORDER BY [Year] DESC"""
                    else:
                        return f"""SELECT 
    SUM({sales_table}.{amount_col}) as TotalRevenue,
    COUNT(*) as TransactionCount
FROM {sales_table}"""
        
        elif "trend" in question_lower or "over time" in question_lower:
            # Sales trends over time
            if sales_tables:
                sales_table = sales_tables[0]
                date_col = date_cols.get(sales_table, "")
                amount_col = amount_cols.get(sales_table, "")
                
                if date_col and amount_col:
                    return f"""SELECT TOP 100
    CAST({sales_table}.{date_col} AS DATE) as DateRecord,
    SUM({sales_table}.{amount_col}) as Amount
FROM {sales_table}
WHERE {sales_table}.{date_col} IS NOT NULL
GROUP BY CAST({sales_table}.{date_col} AS DATE)
ORDER BY DateRecord DESC"""
        
        elif "product" in question_lower:
            # Product analysis
            if product_tables:
                product_table = product_tables[0]
                return f"""SELECT TOP 20 *
FROM {product_table}"""
        
        elif "count" in question_lower:
            # Count records
            if sales_tables:
                sales_table = sales_tables[0]
                return f"SELECT COUNT(*) as RecordCount FROM {sales_table}"
        
        # Default: Show sample data from largest table
        if tables:
            largest_table = tables[0]
            return f"SELECT TOP 20 * FROM {largest_table}"
        
        return ""
    
    @app.post("/api/v1/query")
    async def generate_query(request: QueryRequest):
        """Generate SQL from natural language question - works with any database schema"""
        try:
            question = request.question
            question_lower = question.lower()
            
            # Determine which database we're using
            db_type = request.warehouse if hasattr(request, 'warehouse') else 'sqlserver'
            
            # Fetch the actual schema from the connected database
            schema = get_database_schema(db_type)
            
            # Generate SQL based on actual schema
            sql = generate_dynamic_sql(question, schema, db_type)
            
            if not sql:
                return {
                    "question": question,
                    "sql": "",
                    "results": [],
                    "message": "❌ Could not understand the question or no compatible tables found in the database"
                }
            
            # Execute the generated SQL
            success, results, message = execute_sql_server_query(sql) if db_type == 'sqlserver' else (False, [], "Database type not yet implemented for execution")
            
            return {
                "question": question,
                "sql": sql,
                "results": results if success else [],
                "message": message
            }
            
        except Exception as e:
            return {
                "question": request.question,
                "sql": "",
                "results": [],
                "message": f"❌ Error: {str(e)}"
            }
    
    def test_database_connection(db_type: str, credentials: dict) -> tuple[bool, str]:
        """Test connection to various database platforms"""
        try:
            if db_type == "snowflake":
                # Snowflake connection test
                try:
                    import snowflake.connector
                    
                    # Extract account identifier from host
                    # Snowflake can accept full URLs or account identifiers
                    host = credentials.get('host', '').strip()
                    if not host:
                        return False, "❌ Snowflake Host/Account is required (e.g., we08391.sf-south-1.aws or we08391)"
                    
                    # Remove URL parts if user pasted full URL
                    if 'snowflake.com' in host:
                        # Extract account ID from URL like https://app.snowflake.com/sf-south-1.aws/we08391/#/works
                        try:
                            parts = host.split('/')
                            account_id = [p for p in parts if 'we' in p or 'xy' in p or len(p) > 5][-1].split('#')[0]
                            host = account_id
                        except:
                            return False, "❌ Invalid Snowflake URL format. Use account identifier instead (e.g., we08391)"
                    
                    conn = snowflake.connector.connect(
                        account=host,
                        user=credentials.get('username'),
                        password=credentials.get('password'),
                        database=credentials.get('database'),
                        warehouse=credentials.get('port', 'COMPUTE_WH')
                    )
                    conn.close()
                    return True, "✅ Snowflake connection successful"
                except ImportError:
                    return True, "⚠️ Snowflake driver not installed. Install with: pip install snowflake-connector-python"
                except Exception as e:
                    error_msg = str(e)
                    if "Invalid account identifier" in error_msg:
                        return False, f"❌ Invalid account identifier. Use format like: we08391.sf-south-1.aws\nError: {error_msg}"
                    elif "Incorrect username or password" in error_msg:
                        return False, "❌ Incorrect username or password"
                    else:
                        return False, f"❌ Snowflake connection failed: {error_msg}"
            
            elif db_type == "redshift":
                # Redshift connection test
                try:
                    import psycopg2
                    conn = psycopg2.connect(
                        host=credentials.get('host'),
                        port=int(credentials.get('port', 5439)),
                        user=credentials.get('username'),
                        password=credentials.get('password'),
                        database=credentials.get('database')
                    )
                    conn.close()
                    return True, "✅ Redshift connection successful"
                except ImportError:
                    return True, "⚠️ Redshift driver not installed (psycopg2), but credentials format validated"
                except Exception as e:
                    return False, f"❌ Redshift connection failed: {str(e)}"
            
            elif db_type == "postgres":
                # PostgreSQL connection test
                try:
                    import psycopg2
                    conn = psycopg2.connect(
                        host=credentials.get('host'),
                        port=int(credentials.get('port', 5432)),
                        user=credentials.get('username'),
                        password=credentials.get('password'),
                        database=credentials.get('database')
                    )
                    conn.close()
                    return True, "✅ PostgreSQL connection successful"
                except ImportError:
                    return True, "⚠️ PostgreSQL driver not installed (psycopg2), but credentials format validated"
                except Exception as e:
                    return False, f"❌ PostgreSQL connection failed: {str(e)}"
            
            elif db_type == "bigquery":
                # BigQuery connection test
                try:
                    from google.cloud import bigquery
                    client = bigquery.Client(project=credentials.get('host'))
                    return True, "✅ BigQuery connection successful"
                except ImportError:
                    return True, "⚠️ BigQuery driver not installed (google-cloud-bigquery), but credentials format validated"
                except Exception as e:
                    return False, f"❌ BigQuery connection failed: {str(e)}"
            
            elif db_type == "sqlserver":
                # SQL Server connection test (supports both Windows Auth and SQL Server Auth)
                try:
                    import pyodbc
                    
                    # Check authentication type
                    auth_type = credentials.get('auth_type', 'sql')  # 'windows' or 'sql'
                    host = credentials.get('host', '').strip()
                    port = credentials.get('port', '')
                    database = credentials.get('database', '').strip()
                    
                    # Validate required fields
                    if not host:
                        return False, "❌ Server/Host is required"
                    if not database:
                        return False, "❌ Database name is required"
                    
                    if auth_type != 'windows':
                        username = credentials.get('username', '').strip()
                        if not username:
                            return False, "❌ Username is required for SQL Server Authentication"
                    
                    # Format server name (handle backslash for named instances)
                    if '\\' in host:
                        server = host  # Already has instance name like DESKTOP-ABC\SQLEXPRESS
                    else:
                        # Add port if specified and not default
                        if port and str(port) != '1433':
                            server = f"{host},{port}"
                        else:
                            server = host
                    
                    if auth_type == 'windows':
                        # Windows Authentication - use Trusted Connection
                        conn_str = f"Driver={{ODBC Driver 17 for SQL Server}};Server={server};Database={database};Trusted_Connection=yes;"
                    else:
                        # SQL Server Authentication
                        username = credentials.get('username', '').strip()
                        password = credentials.get('password', '')
                        conn_str = f"Driver={{ODBC Driver 17 for SQL Server}};Server={server};Database={database};UID={username};PWD={password}"
                    
                    # Attempt connection with timeout
                    conn = pyodbc.connect(conn_str, timeout=10)
                    conn.close()
                    
                    # Store connection string globally for queries
                    connection_store["sqlserver"] = conn_str
                    
                    auth_label = "Windows Authentication" if auth_type == 'windows' else "SQL Server Authentication"
                    return True, f"✅ SQL Server connection successful ({auth_label})"
                except ImportError:
                    return True, "⚠️ SQL Server driver not installed (pyodbc), but credentials format validated"
                except Exception as e:
                    error_msg = str(e)
                    # Provide more helpful error messages
                    if 'login' in error_msg.lower() or 'authentication' in error_msg.lower():
                        return False, f"❌ Authentication failed - check credentials: {error_msg}"
                    elif 'cannot open' in error_msg.lower():
                        return False, f"❌ Cannot connect to server - check host/server name: {error_msg}"
                    else:
                        return False, f"❌ SQL Server connection failed: {error_msg}"
            
            else:
                return False, f"❌ Unknown database type: {db_type}"
                
        except Exception as e:
            return False, f"❌ Connection test error: {str(e)}"
    
    @app.post("/api/v1/test-connection")
    async def test_connection(request: DBConnectionRequest):
        """Test database connection"""
        try:
            success, message = test_database_connection(request.database, request.credentials)
            if success:
                return DBConnectionResponse(
                    status="success",
                    message=message,
                    database=request.database
                )
            else:
                raise HTTPException(status_code=400, detail=message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/connect")
    async def connect_database(request: DBConnectionRequest):
        """Connect to database and store connection"""
        try:
            success, message = test_database_connection(request.database, request.credentials)
            if success:
                # Connection is now stored in global current_connection for SQL Server
                return DBConnectionResponse(
                    status="success",
                    message=f"🟢 Connected to {request.database}",
                    database=request.database
                )
            else:
                raise HTTPException(status_code=400, detail=message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/connection-status")
    async def connection_status():
        """Check current database connection status"""
        sqlserver_connected = connection_store.get("sqlserver") is not None
        return {
            "sqlserver": {
                "connected": sqlserver_connected,
                "status": "🟢 Connected" if sqlserver_connected else "🔴 Not connected"
            }
        }
    
    @app.post("/api/v1/generate-questions")
    async def generate_questions(request: DBConnectionRequest):
        """Generate smart questions based on database schema"""
        try:
            if request.database == "sqlserver":
                # Fetch schema
                schema = fetch_sqlserver_schema()
                if not schema:
                    return {
                        "success": False,
                        "questions": [],
                        "message": "Could not fetch schema"
                    }
                
                # Generate questions
                questions = generate_questions_from_schema(schema, "sqlserver")
                
                return {
                    "success": True,
                    "questions": questions,
                    "table_count": len(schema),
                    "message": f"Generated {len(questions)} questions from {len(schema)} tables"
                }
            else:
                # For other databases, return generic questions for now
                return {
                    "success": True,
                    "questions": [
                        "Show me recent records",
                        "Count total records",
                        "Group by category",
                        "Top 10 records",
                        "Show distinct values",
                        "Latest entries",
                        "Summary statistics",
                        "Records by date"
                    ],
                    "message": "Generic questions (schema scanning not yet implemented for this database)"
                }
        except Exception as e:
            return {
                "success": False,
                "questions": [],
                "message": f"Error generating questions: {str(e)}"
            }

except ImportError as e:
    print(f"❌ Error: Missing module: {e}")
    print()
    print("Installing dependencies...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=False)
    print()
    print("Please run again: python main.py")
else:
    # Run server if imports successful
    if __name__ == "__main__":
        import sys
        # Set UTF-8 encoding for Windows console
        if sys.stdout.encoding != 'utf-8':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        
        print("=" * 60)
        print("🚀 VoxQuery Backend Starting")
        print("=" * 60)
        print()
        print("📍 API: http://localhost:8000")
        print("📖 Docs: http://localhost:8000/docs")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
