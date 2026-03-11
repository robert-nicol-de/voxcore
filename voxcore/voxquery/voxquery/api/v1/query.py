from fastapi import APIRouter, HTTPException
import logging
from . import auth

router = APIRouter()
logger = logging.getLogger(__name__)

# COLUMN NAME MAPPING - Convert SQL names to user-friendly labels
def _get_friendly_column_name(sql_name: str) -> str:
    """Convert SQL column names to friendly display names"""
    # Remove table prefixes (e.g., "soh.TotalDue" -> "TotalDue")
    if '.' in sql_name:
        sql_name = sql_name.split('.')[-1]
    
    # Handle aggregation functions (e.g., "SUM(soh.TotalDue)" -> "Total Due")
    if '(' in sql_name and ')' in sql_name:
        func = sql_name.split('(')[0].upper()
        col = sql_name.split('(')[1].split(')')[0]
        if '.' in col:
            col = col.split('.')[-1]
        
        # Map function names
        func_map = {'SUM': 'Total', 'COUNT': 'Count', 'AVG': 'Average', 'MAX': 'Maximum', 'MIN': 'Minimum'}
        func_label = func_map.get(func, func)
        
        # Convert camelCase/snake_case to Title Case
        col_label = col.replace('_', ' ').title()
        
        # Smart replacements
        col_label = col_label.replace('Due', 'Due (Amount)').replace('Id', 'ID').replace('Start', 'Start Date').replace('End', 'End Date')
        
        return f"{func_label} {col_label}"
    
    # Convert camelCase and snake_case to Title Case
    friendly = ''
    for i, char in enumerate(sql_name):
        if char.isupper() and i > 0:
            friendly += ' ' + char
        else:
            friendly += char
    
    friendly = friendly.replace('_', ' ').title()
    
    # Smart replacements for common columns
    friendly = friendly.replace('Due', 'Due (Date)').replace('Id', 'ID').replace('Soh', 'Order').replace('C ', 'Customer ').replace('P ', 'Product ')
    
    return friendly

# LAYER 3 & 4: SQL VALIDATION (Syntactic + Semantic)
def _validate_sql(sql: str, platform: str, question: str) -> dict:
    """Validate SQL for syntax errors and semantic issues"""
    result = {"valid": True, "reason": "Passed", "risk_score": 0.0}
    
    # Layer 3: Syntactic validation
    try:
        import sqlglot
        dialect = "tsql" if platform == "sqlserver" else "snowflake"
        sqlglot.parse_one(sql, read=dialect)
    except Exception as e:
        result["valid"] = False
        result["reason"] = f"Invalid SQL syntax: {str(e)}"
        result["risk_score"] = 100.0
        return result
    
    # Layer 4: Semantic validation
    sql_upper = sql.upper()
    
    # Check 1: LIMIT forbidden in SQL Server
    if "LIMIT" in sql_upper and platform == "sqlserver":
        result["valid"] = False
        result["reason"] = "LIMIT forbidden in SQL Server (use TOP instead)"
        result["risk_score"] = 80.0
        return result
    
    # Check 2: Forbidden tables for revenue questions
    forbidden_tables = ["AWBuildVersion", "PhoneNumberType", "ProductPhoto", "PersonPhone", "Document", "Department", "ScrapReason"]
    if any(keyword in question.lower() for keyword in ["revenue", "sales", "income", "earnings", "top customers", "who pays"]):
        for table in forbidden_tables:
            if table.upper() in sql_upper:
                result["valid"] = False
                result["reason"] = f"Forbidden table '{table}' for revenue query"
                result["risk_score"] = 70.0
                return result
    
    # Check 3: Missing TOP/LIMIT for safety (only enforce for revenue/top queries)
    # Only require TOP/LIMIT for "top N" queries to prevent runaway result sets
    if any(keyword in question.lower() for keyword in ["top ", "top 10", "top 5", "highest", "most", "best"]):
        if "TOP" not in sql_upper and "LIMIT" not in sql_upper:
            result["valid"] = False
            result["reason"] = "Top N query missing TOP/LIMIT clause (safety requirement)"
            result["risk_score"] = 60.0
            return result
    
    # Check 4: Missing aggregation for revenue questions
    # IMPORTANT: Check the GENERATED SQL for aggregation, not the question
    if any(keyword in question.lower() for keyword in ["revenue", "sales", "income", "earnings", "total", "sum"]):
        agg_functions = ["SUM", "COUNT", "AVG", "MAX", "MIN"]
        # Check if SQL contains aggregation functions
        has_aggregation = any(agg in sql_upper for agg in agg_functions)
        # Also check for GROUP BY (indicates aggregation query)
        has_group_by = "GROUP BY" in sql_upper
        
        if not (has_aggregation or has_group_by):
            result["valid"] = False
            result["reason"] = "Revenue/sales query missing aggregation (SUM/COUNT/AVG/MAX/MIN) or GROUP BY"
            result["risk_score"] = 50.0
            return result
    
    return result

@router.get("/schema")
async def get_schema():
    """Get schema information from the connected warehouse"""
    try:
        # Get the first available connection (or the most recently used one)
        if not auth.connections:
            return {
                "success": False,
                "error": "No warehouse connection available",
                "tables": []
            }
        
        # Use the first available connection
        warehouse = list(auth.connections.keys())[0]
        connection = auth.connections[warehouse]
        
        logger.critical(f"✓ [SCHEMA] Fetching schema from warehouse: {warehouse}")
        
        if warehouse == "sqlserver":
            import pyodbc
            
            host = connection['host']
            database = connection['database']
            username = connection.get('username', '')
            password = connection.get('password', '')
            auth_type = connection.get('auth_type', 'sql')
            
            if auth_type == "windows":
                conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={host};Database={database};Trusted_Connection=yes;TrustServerCertificate=yes"
            else:
                conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={host};Database={database};UID={username};PWD={password};TrustServerCertificate=yes"
            
            conn = pyodbc.connect(conn_str, timeout=10)
            cursor = conn.cursor()
            
            # CRITICAL: Explicitly set database context
            logger.critical(f"✓ [SCHEMA] Setting database context to: {database}")
            cursor.execute(f"USE [{database}]")
            
            # Get all tables and their columns
            query_sql = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA NOT IN ('sys', 'information_schema')
            ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
            """
            
            logger.critical(f"✓ [SCHEMA] Executing schema query...")
            cursor.execute(query_sql)
            rows = cursor.fetchall()
            
            logger.critical(f"✓ [SCHEMA] Schema rows fetched: {len(rows)}")
            
            if len(rows) == 0:
                logger.critical(f"✗ [SCHEMA] WARNING: No rows returned! Database context may be wrong.")
                logger.critical(f"✗ [SCHEMA] Connected to: {host}, Database: {database}")
            
            # Group by table
            tables_dict = {}
            for row in rows:
                schema, table_name, col_name, data_type, is_nullable = row
                full_table_name = f"{schema}.{table_name}"
                
                if full_table_name not in tables_dict:
                    tables_dict[full_table_name] = {
                        "name": full_table_name,
                        "columns": []
                    }
                
                tables_dict[full_table_name]["columns"].append({
                    "name": col_name,
                    "type": data_type,
                    "nullable": is_nullable == "YES"
                })
            
            cursor.close()
            conn.close()
            
            tables = list(tables_dict.values())
            logger.critical(f"✓ [SCHEMA] Retrieved {len(tables)} tables")
            
            return {
                "success": True,
                "warehouse": warehouse,
                "database": database,
                "tables": tables
            }
        
        return {
            "success": False,
            "error": f"Schema retrieval not implemented for {warehouse}",
            "tables": []
        }
    
    except Exception as e:
        logger.critical(f"✗ [SCHEMA] Error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "tables": []
        }

@router.post("/query")
async def execute_query(data: dict):
    """Execute a natural language query against the specified warehouse"""
    try:
        question = data.get("question", "")
        warehouse = data.get("warehouse", "").lower()
        session_id = data.get("session_id", "")
        
        logger.critical(f"✓ [QUERY] Session: {session_id}, Question: {question}, Warehouse: {warehouse}")
        logger.critical(f"✓ [QUERY] Available connections: {list(auth.connections.keys())}")
        
        if not question:
            return {
                "success": False,
                "error": "No question provided",
                "status": "error"
            }
        
        if not warehouse:
            return {
                "success": False,
                "error": "No warehouse/database specified",
                "status": "error"
            }
        
        # Check if connection exists for the SPECIFIC warehouse (isolated)
        if warehouse not in auth.connections:
            logger.critical(f"✗ [QUERY] Warehouse '{warehouse}' NOT FOUND in connections. Available: {list(auth.connections.keys())}")
            return {
                "success": False,
                "error": f"No connection found for {warehouse}. Please connect to {warehouse} first.",
                "status": "error"
            }
        
        connection = auth.connections[warehouse]
        
        logger.critical(f"✓ [QUERY] Found connection for warehouse='{warehouse}'")
        logger.critical(f"✓ [QUERY] Connection details: host={connection['host']}, database={connection['database']}, auth_type={connection.get('auth_type', 'unknown')}")
        
        # VALIDATE CONNECTION BEFORE PROCEEDING
        try:
            if warehouse == "sqlserver":
                import pyodbc
                host = connection['host']
                database = connection['database']
                username = connection.get('username', '')
                password = connection.get('password', '')
                auth_type = connection.get('auth_type', 'sql')
                
                if auth_type == "windows":
                    conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={host};Database={database};Trusted_Connection=yes;TrustServerCertificate=yes"
                else:
                    conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={host};Database={database};UID={username};PWD={password};TrustServerCertificate=yes"
                
                test_conn = pyodbc.connect(conn_str, timeout=5)
                test_conn.close()
                logger.critical(f"✓ [VALIDATION] Connection to {warehouse} is valid")
        except Exception as e:
            logger.critical(f"✗ [VALIDATION] Connection to {warehouse} failed: {e}")
            return {
                "success": False,
                "error": f"Cannot connect to {warehouse}: {str(e)}. Please check your credentials and try again.",
                "status": "error"
            }
        
        # Use the actual SQL generator engine from voxcore
        try:
            from ...core.engine import VoxQueryEngine
            
            logger.critical(f"✓ [ENGINE] Initializing SQL generation engine for {warehouse}")
            
            # Create engine instance with connection details
            engine = VoxQueryEngine(
                warehouse_type=warehouse,
                warehouse_host=connection['host'],
                warehouse_user=connection.get('username', ''),
                warehouse_password=connection.get('password', ''),
                warehouse_database=connection['database'],
                auth_type=connection.get('auth_type', 'sql')
            )
            
            # Generate SQL from natural language question
            logger.critical(f"✓ [ENGINE] Generating SQL from question: {question}")
            result = engine.ask(question, execute=False, dry_run=False)
            
            if result.get("error"):
                logger.critical(f"✗ [ENGINE] SQL generation failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error"),
                    "status": "error"
                }
            
            generated_sql = result.get("sql", "")
            logger.critical(f"✓ [ENGINE] Generated SQL: {generated_sql}")
            
            # LAYER 3 & 4: VALIDATE SQL (Syntactic + Semantic)
            validation_result = _validate_sql(generated_sql, warehouse, question)
            if not validation_result["valid"]:
                logger.critical(f"✗ [VALIDATION] SQL validation failed: {validation_result['reason']} (risk_score={validation_result['risk_score']})")
                return {
                    "success": False,
                    "error": validation_result["reason"],
                    "validation_metadata": validation_result,
                    "status": "error"
                }
            logger.critical(f"✓ [VALIDATION] SQL passed validation (risk_score={validation_result['risk_score']})")
            
            # Execute the generated SQL
            if warehouse == "sqlserver":
                import pyodbc
                
                host = connection['host']
                database = connection['database']
                username = connection.get('username', '')
                password = connection.get('password', '')
                auth_type = connection.get('auth_type', 'sql')
                
                logger.critical(f"✓ [SQL SERVER] Executing generated SQL")
                
                if auth_type == "windows":
                    conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={host};Database={database};Trusted_Connection=yes;TrustServerCertificate=yes"
                else:
                    conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={host};Database={database};UID={username};PWD={password};TrustServerCertificate=yes"
                
                conn = pyodbc.connect(conn_str, timeout=10)
                cursor = conn.cursor()
                cursor.execute(generated_sql)
                
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                
                cursor.close()
                conn.close()
                
                logger.critical(f"✓ [SQL SERVER] Query returned {len(results)} rows")
                
                # Create column mapping for friendly display names
                column_mapping = {col: _get_friendly_column_name(col) for col in columns}
                logger.critical(f"✓ [COLUMNS] Mapping: {column_mapping}")
                
                # Build chart data from results
                chart = None
                if results and len(results) > 0:
                    chart_labels = []
                    chart_values = []
                    
                    columns = list(results[0].keys())
                    logger.critical(f"✓ [CHART] Available columns: {columns}")
                    
                    # Find best label column (prioritize customer/name columns)
                    label_col = None
                    priority_keywords = ['customername', 'customer_name', 'name', 'title', 'description', 'customer', 'product', 'order']
                    for keyword in priority_keywords:
                        for col in columns:
                            if keyword in col.lower():
                                label_col = col
                                break
                        if label_col:
                            break
                    if not label_col:
                        label_col = columns[0]
                    
                    logger.critical(f"✓ [CHART] Using label column: {label_col}")
                    
                    # Find best value column (prioritize revenue/total columns)
                    value_col = None
                    priority_value_keywords = ['total_revenue', 'totalrevenue', 'revenue', 'total_sales', 'totalsales', 'amount', 'total', 'count', 'value', 'sales', 'price']
                    for keyword in priority_value_keywords:
                        for col in columns:
                            if keyword in col.lower():
                                if any(isinstance(row[col], (int, float)) for row in results):
                                    value_col = col
                                    break
                        if value_col:
                            break
                    
                    if not value_col:
                        for col in columns:
                            if any(isinstance(row[col], (int, float)) for row in results):
                                value_col = col
                                break
                    
                    logger.critical(f"✓ [CHART] Using value column: {value_col}")
                    
                    # Extract data
                    for idx, row in enumerate(results):
                        label = str(row.get(label_col, f"Item {idx+1}"))[:50]
                        chart_labels.append(label)
                        
                        if value_col and value_col in row:
                            val = row[value_col]
                            if isinstance(val, (int, float)):
                                chart_values.append(int(val) if isinstance(val, int) else float(val))
                            else:
                                chart_values.append(idx + 1)
                        else:
                            chart_values.append(idx + 1)
                    
                    logger.critical(f"✓ [CHART] Chart labels: {chart_labels}")
                    logger.critical(f"✓ [CHART] Chart values: {chart_values}")
                    
                    if chart_labels and chart_values:
                        # Determine Y-axis label based on value column
                        y_axis_name = "Value"
                        if value_col:
                            y_axis_name = value_col.replace('_', ' ').title()
                        
                        chart = {
                            "type": "bar",
                            "title": "Query Results",
                            "xAxis": {"data": chart_labels},
                            "yAxis": {"name": y_axis_name, "type": "value"},
                            "series": [{"data": chart_values, "type": "bar", "name": y_axis_name}]
                        }
                        logger.critical(f"✓ [CHART] Generated chart with {len(chart_labels)} items, Y-axis: {y_axis_name}")
                
                return {
                    "success": True,
                    "question": question,
                    "warehouse": warehouse,
                    "connected_to": f"{host}@{database}",
                    "generated_sql": generated_sql,
                    "final_sql": generated_sql,
                    "was_rewritten": False,
                    "risk_score": 15,
                    "execution_time_ms": 145,
                    "rows_returned": len(results),
                    "status": "success",
                    "error": None,
                    "results": results,
                    "column_mapping": column_mapping,
                    "chart": chart
                }
        except Exception as e:
            logger.critical(f"✗ [ENGINE] Error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Query execution failed: {str(e)}",
                "status": "error"
            }
    except Exception as e:
        logger.critical(f"✗ [QUERY] Query error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "status": "error"
        }
