"""PostgreSQL connection handler"""

import logging
from typing import Dict, List, Optional, Any

import psycopg2
from psycopg2.extras import RealDictCursor

from voxquery.warehouses.base import BaseConnection

logger = logging.getLogger(__name__)


class PostgresConnection(BaseConnection):
    """PostgreSQL database connection"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.port = self.port or 5432
    
    def connect(self) -> None:
        """Establish PostgreSQL connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            logger.info(f"Connected to PostgreSQL: {self.host}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from PostgreSQL")
    
    def test_connection(self) -> bool:
        """Test PostgreSQL connection"""
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
        """Execute query on PostgreSQL"""
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
        """Get PostgreSQL schema information"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            # Get tables
            cursor.execute("""
                SELECT 
                    table_name,
                    table_schema
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            """)
            
            tables = {}
            for row in cursor.fetchall():
                table_name = row['table_name']
                
                # Get columns for table
                cursor.execute(f"""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable
                    FROM information_schema.columns
                    WHERE table_name = %s
                """, (table_name,))
                
                columns = {
                    col['column_name']: {
                        "type": col['data_type'],
                        "nullable": col['is_nullable'] == 'YES',
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
        """PostgreSQL doesn't provide cost estimates"""
        return None
