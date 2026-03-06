"""Snowflake connection handler"""

import logging
from typing import Dict, List, Optional, Any

import snowflake.connector
from snowflake.connector.errors import DatabaseError, ProgrammingError

from .base import BaseConnection

logger = logging.getLogger(__name__)


class SnowflakeConnection(BaseConnection):
    """Snowflake data warehouse connection"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.account = kwargs.get("account", self.host)
        self.warehouse = kwargs.get("warehouse", "COMPUTE_WH")
        self.role = kwargs.get("role", "SYSADMIN")
    
    def connect(self) -> None:
        """Establish Snowflake connection"""
        try:
            # FORCE correct DB/schema for testing
            # This ensures we connect to the right database where tables were created
            database = self.database or "VOXQUERYTRAININGFIN2025"
            schema = self.schema or "PUBLIC"
            
            print(f"\n{'='*80}")
            print(f"SNOWFLAKE CONNECTION PARAMETERS:")
            print(f"  Account: {self.account}")
            print(f"  Database: {database}")
            print(f"  Schema: {schema}")
            print(f"  Warehouse: {self.warehouse}")
            print(f"  Role: {self.role}")
            print(f"{'='*80}\n")
            
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse,
                role=self.role,
            )
            
            # CRITICAL: Explicitly set session context with USE statements
            cursor = self.connection.cursor()
            
            if database:
                cursor.execute(f"USE DATABASE {database}")
                logger.info("Executed: USE DATABASE %s", database)
            
            if schema:
                cursor.execute(f"USE SCHEMA {schema}")
                logger.info("Executed: USE SCHEMA %s", schema)
            
            if self.warehouse:
                cursor.execute(f"USE WAREHOUSE {self.warehouse}")
                logger.info("Executed: USE WAREHOUSE %s", self.warehouse)
            
            if self.role:
                cursor.execute(f"USE ROLE {self.role}")
                logger.info("Executed: USE ROLE %s", self.role)
            
            # VERIFY: Check what we're actually connected to
            cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE(), CURRENT_ROLE()")
            db, sch, wh, rl = cursor.fetchone()
            print(f"\n{'='*80}")
            print(f"✓ VERIFIED SESSION CONTEXT:")
            print(f"  Database: {db}")
            print(f"  Schema: {sch}")
            print(f"  Warehouse: {wh}")
            print(f"  Role: {rl}")
            print(f"{'='*80}\n")
            logger.critical("VERIFIED SESSION CONTEXT: DB=%s, Schema=%s, WH=%s, Role=%s", db, sch, wh, rl)
            
            cursor.close()
            logger.info(f"Connected to Snowflake account: {self.account}")
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from Snowflake")
    
    def test_connection(self) -> bool:
        """Test Snowflake connection"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def execute_query(self, sql: str, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Execute query on Snowflake"""
        try:
            cursor = self.connection.cursor()
            
            # Execute query
            cursor.execute(sql)
            
            # Get schema
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Fetch results and convert to native Python types immediately
            results = cursor.fetchall()
            
            # Convert to list of dicts with native Python types
            data = []
            for row in results:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert Snowflake types to native Python types
                    if value is None:
                        row_dict[col] = None
                    elif isinstance(value, (int, float, str, bool)):
                        row_dict[col] = value
                    else:
                        # Convert other types to string
                        row_dict[col] = str(value)
                data.append(row_dict)
            
            cursor.close()
            return data
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Get Snowflake schema information"""
        try:
            cursor = self.connection.cursor()
            
            # Get tables
            cursor.execute(f"""
                SELECT 
                    TABLE_NAME,
                    TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = '{self.schema or "PUBLIC"}'
            """)
            
            tables = {}
            for table_name, table_type in cursor.fetchall():
                # Get columns for each table
                cursor.execute(f"""
                    SELECT 
                        COLUMN_NAME,
                        DATA_TYPE,
                        IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{table_name}'
                        AND TABLE_SCHEMA = '{self.schema or "PUBLIC"}'
                """)
                
                columns = {
                    col_name: {
                        "type": col_type,
                        "nullable": is_nullable == "YES",
                    }
                    for col_name, col_type, is_nullable in cursor.fetchall()
                }
                
                tables[table_name] = {
                    "type": table_type,
                    "columns": columns,
                }
            
            cursor.close()
            return tables
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            return {}
    
    def get_cost_estimate(self, sql: str) -> Optional[float]:
        """Snowflake doesn't provide direct cost estimates in standard SQL"""
        # Could integrate with Snowflake's query cost API in future
        return None
