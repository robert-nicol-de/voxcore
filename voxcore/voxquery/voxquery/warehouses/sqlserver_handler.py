"""SQL Server connection handler"""

import logging
from typing import Dict, List, Optional, Any

import pyodbc

from .base import BaseConnection

logger = logging.getLogger(__name__)


class SQLServerConnection(BaseConnection):
    """SQL Server database connection"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.port = self.port or 1433
    
    def connect(self) -> None:
        """Establish SQL Server connection"""
        try:
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.user};"
                f"PWD={self.password}"
            )
            self.connection = pyodbc.connect(connection_string)
            logger.info(f"Connected to SQL Server: {self.host}")
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close SQL Server connection"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from SQL Server")
    
    def test_connection(self) -> bool:
        """Test SQL Server connection"""
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
        """Execute query on SQL Server"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            results = [
                {col: row[i] for i, col in enumerate(columns)}
                for row in rows
            ]
            
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Get SQL Server schema information"""
        try:
            cursor = self.connection.cursor()
            
            # Get tables
            cursor.execute("""
                SELECT 
                    TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            
            tables = {}
            for (table_name,) in cursor.fetchall():
                # Get columns for table
                cursor.execute(f"""
                    SELECT 
                        COLUMN_NAME,
                        DATA_TYPE,
                        IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{table_name}'
                """)
                
                columns = {
                    col_name: {
                        "type": data_type,
                        "nullable": is_nullable == 'YES',
                    }
                    for col_name, data_type, is_nullable in cursor.fetchall()
                }
                
                tables[table_name] = {"columns": columns}
            
            cursor.close()
            return tables
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            return {}
    
    def get_cost_estimate(self, sql: str) -> Optional[float]:
        """SQL Server doesn't provide standard cost estimates"""
        return None
