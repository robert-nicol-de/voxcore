"""AWS Redshift connection handler"""

import logging
from typing import Dict, List, Optional, Any

import psycopg2
from psycopg2.extras import RealDictCursor

from .base import BaseConnection

logger = logging.getLogger(__name__)


class RedshiftConnection(BaseConnection):
    """AWS Redshift data warehouse connection"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.port = self.port or 5439
    
    def connect(self) -> None:
        """Establish Redshift connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            logger.info(f"Connected to Redshift: {self.host}")
        except Exception as e:
            logger.error(f"Failed to connect to Redshift: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close Redshift connection"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from Redshift")
    
    def test_connection(self) -> bool:
        """Test Redshift connection"""
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
        """Execute query on Redshift"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Get Redshift schema information"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            # Get tables
            cursor.execute("""
                SELECT 
                    tablename,
                    schemaname
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            """)
            
            tables = {}
            for row in cursor.fetchall():
                table_name = row['tablename']
                
                # Get columns for table
                cursor.execute(f"""
                    SELECT 
                        attname,
                        typname,
                        attnotnull
                    FROM pg_attribute
                    JOIN pg_type ON pg_attribute.atttypid = pg_type.oid
                    WHERE attrelid = '{table_name}'::regclass
                        AND attnum > 0
                """)
                
                columns = {
                    col['attname']: {
                        "type": col['typname'],
                        "nullable": not col['attnotnull'],
                    }
                    for col in cursor.fetchall()
                }
                
                tables[table_name] = {"columns": columns}
            
            cursor.close()
            return tables
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            return {}
    
    def get_cost_estimate(self, sql: str) -> Optional[float]:
        """Redshift doesn't provide direct cost estimates"""
        return None
