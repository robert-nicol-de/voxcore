"""
Production-grade connection manager for multi-user safe database connections.

Key features:
- Per-request/session engines (no global shared engine)
- Explicit USE DATABASE/SCHEMA statements for Snowflake
- Connection pooling with health checks
- Automatic cleanup on request end
"""

import logging
from typing import Dict, Optional, Any
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


def create_snowflake_engine(params: dict) -> Engine:
    """
    Builds SQLAlchemy engine for Snowflake using raw connector wrapped in SQLAlchemy.
    
    params: dict with 'account', 'user', 'password', 'warehouse', 'database', 'schema', 'role'
    Returns SQLAlchemy engine (per-user/session safe)
    
    APPROACH:
    - Use snowflake.connector.connect() directly to establish connection
    - Wrap it with SQLAlchemy using creator function
    - This avoids URL parsing issues with region-specific account identifiers
    """
    import snowflake.connector
    
    required = ['account', 'user', 'password']
    if missing := [k for k in required if k not in params or not params[k]]:
        raise ValueError(f"Missing required params: {', '.join(missing)}")

    account = params['account']
    user = params['user']
    password = params['password']
    warehouse = params.get('warehouse', 'COMPUTE_WH')
    database = params.get('database')  # can be None
    schema = params.get('schema', 'PUBLIC')
    role = params.get('role', 'ACCOUNTADMIN')
    
    # Use the database name as provided by the user
    database = database.strip().upper() if database else ''
    params['database'] = database
    logger.info(f"Using database: {database}")

    logger.info("Creating Snowflake connection: account=%s user=%s warehouse=%s role=%s database=%s schema=%s",
                account, user, warehouse, role, database, schema)

    # Create a connection factory function
    def get_snowflake_connection():
        """Factory function to create fresh Snowflake connections"""
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema,
            role=role,
        )
        logger.info("✓ Created new Snowflake connection")
        return conn
    
    try:
        # Test the connection factory
        logger.info("Testing connection factory...")
        test_conn = get_snowflake_connection()
        cursor = test_conn.cursor()
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE(), CURRENT_ROLE()")
        db, sch, wh, rl = cursor.fetchone()
        logger.critical("✓ VERIFIED CONTEXT: DB=%s | SCHEMA=%s | WH=%s | ROLE=%s", db, sch, wh, rl)
        cursor.close()
        test_conn.close()
        
        # Create SQLAlchemy engine with the connection factory
        engine = create_engine(
            "snowflake://",
            creator=get_snowflake_connection,
            poolclass=QueuePool,
            pool_size=3,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=1800,  # 30 min
        )
        
        logger.info("✓ Snowflake engine created successfully")
        return engine
    
    except Exception as e:
        logger.error("✗ Failed to create Snowflake engine: %s", repr(e), exc_info=True)
        raise


def cleanup_snowflake_connection(conn: Optional[Any]) -> None:
    """
    Safely close a Snowflake connection.
    
    Args:
        conn: Snowflake connection to close (can be None)
    """
    if conn:
        try:
            conn.close()
            logger.info("✓ Snowflake connection closed")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")


def get_sqlserver_engine(
    host: str,
    database: str,
    user: Optional[str] = None,
    password: Optional[str] = None,
    auth_type: str = "sql",
) -> Engine:
    """
    Create a SQL Server engine with connection pooling.
    
    Args:
        host: Server hostname or IP
        database: Database name
        user: Username (required for SQL auth)
        password: Password (required for SQL auth)
        auth_type: "sql" or "windows"
    
    Returns:
        SQLAlchemy Engine
    """
    
    logger.info(f"Creating SQL Server connection: host={host} database={database} auth_type={auth_type}")
    
    # Normalize server name
    server = host
    if server == ".":
        server = "(local)"
        logger.info("Converted server '.' to '(local)'")
    
    # Build connection URL
    if auth_type == "windows" or (auth_type == "sql" and (not user or not password)):
        # Use Windows authentication (default if no credentials provided)
        logger.info("Using Windows authentication for SQL Server")
        connection_url = (
            f"mssql+pyodbc:///?odbc_connect="
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={server};"
            f"Database={database};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes"
        )
    else:
        if not user or not password:
            raise ValueError("user and password required for SQL authentication")
        
        # URL encode password to handle special characters
        from urllib.parse import quote_plus
        encoded_password = quote_plus(password)
        
        # Use ODBC Driver 18 for SQL Server (newer, more reliable)
        # Add TrustServerCertificate=yes for local development
        logger.info("Using SQL authentication for SQL Server")
        connection_url = (
            f"mssql+pyodbc://{user}:{encoded_password}"
            f"@{server}/{database}"
            f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
        )
    
    try:
        engine = create_engine(
            connection_url,
            echo=False,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"timeout": 10}
        )
        
        logger.info("✓ SQL Server engine created successfully")
        return engine
    
    except Exception as e:
        logger.error(f"✗ Failed to create SQL Server engine: {e}")
        raise


def get_postgres_engine(
    host: str,
    database: str,
    user: str,
    password: str,
    port: int = 5432,
) -> Engine:
    """
    Create a PostgreSQL engine with connection pooling.
    
    Args:
        host: Server hostname
        database: Database name
        user: Username
        password: Password
        port: Port number (default: 5432)
    
    Returns:
        SQLAlchemy Engine
    """
    
    connection_url = (
        f"postgresql://{user}:{password}"
        f"@{host}:{port}/{database}"
    )
    
    try:
        engine = create_engine(
            connection_url,
            echo=False,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        logger.info("✓ PostgreSQL engine created successfully")
        return engine
    
    except Exception as e:
        logger.error(f"✗ Failed to create PostgreSQL engine: {e}")
        raise


def get_redshift_engine(
    host: str,
    database: str,
    user: str,
    password: str,
    port: int = 5439,
) -> Engine:
    """
    Create a Redshift engine with connection pooling.
    
    Args:
        host: Server hostname
        database: Database name
        user: Username
        password: Password
        port: Port number (default: 5439)
    
    Returns:
        SQLAlchemy Engine
    """
    
    connection_url = (
        f"redshift+psycopg2://{user}:{password}"
        f"@{host}:{port}/{database}"
    )
    
    try:
        engine = create_engine(
            connection_url,
            echo=False,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        logger.info("✓ Redshift engine created successfully")
        return engine
    
    except Exception as e:
        logger.error(f"✗ Failed to create Redshift engine: {e}")
        raise
