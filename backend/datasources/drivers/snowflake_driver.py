"""
Snowflake database driver for VoxCore datasources.
Handles connections, schema discovery, and metadata queries.
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Snowflake connector is lazy-imported to allow optional dependency


class SnowflakeDriver:
    """Manages Snowflake connections and schema discovery."""

    MAX_DATABASES = 100
    MAX_SCHEMAS_PER_DB = 500
    MAX_TABLES = 1000
    MAX_COLUMNS_PER_TABLE = 200
    QUERY_TIMEOUT_SECONDS = 30

    def __init__(self, connection_params: Dict[str, Any]):
        """
        Initialize Snowflake driver.

        Connection params:
        - user: Snowflake username
        - password: Snowflake password
        - account: Snowflake account ID (e.g., 'xy12345')
        - warehouse: Warehouse name
        - database: Default database (optional)
        - schema: Default schema (optional)
        - role: Role name (optional)
        """
        self.params = connection_params
        self.conn = None

    def connect(self) -> bool:
        """Establish connection to Snowflake."""
        try:
            import snowflake.connector

            self.conn = snowflake.connector.connect(
                user=self.params.get("user"),
                password=self.params.get("password"),
                account=self.params.get("account"),
                warehouse=self.params.get("warehouse"),
                database=self.params.get("database"),
                schema=self.params.get("schema"),
                role=self.params.get("role"),
                login_timeout=self.QUERY_TIMEOUT_SECONDS,
            )
            return True
        except Exception as e:
            logger.error(f"Snowflake connection failed: {e}")
            return False

    def disconnect(self):
        """Close Snowflake connection."""
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                logger.warning(f"Error closing Snowflake connection: {e}")

    def discover_databases(self) -> List[str]:
        """List all Snowflake databases."""
        if not self.conn:
            raise ConnectionError("Not connected to Snowflake")

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"SHOW DATABASES LIMIT {self.MAX_DATABASES}"
            )
            rows = cursor.fetchall()
            return [row[1] for row in rows]  # Column 1 is database name
        except Exception as e:
            logger.error(f"Failed to list databases: {e}")
            raise

    def discover_schemas(self, database: str) -> List[str]:
        """List all schemas in a database."""
        if not self.conn:
            raise ConnectionError("Not connected to Snowflake")

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"SHOW SCHEMAS IN DATABASE {database} LIMIT {self.MAX_SCHEMAS_PER_DB}"
            )
            rows = cursor.fetchall()
            # Filter out system schemas
            return [
                row[1]
                for row in rows
                if row[1] not in ("INFORMATION_SCHEMA", "REPLICATION_DATABASE")
            ]
        except Exception as e:
            logger.error(f"Failed to list schemas for {database}: {e}")
            raise

    def discover_schema(
        self, database: str, schema: str = "public"
    ) -> Dict[str, Any]:
        """
        Discover full schema structure (tables and columns).

        Returns:
        {
          "database": "database_name",
          "schema": "schema_name",
          "tables": [
            {
              "name": "table_name",
              "rows_estimate": 1000,
              "columns": [
                {
                  "name": "col_name",
                  "type": "VARCHAR",
                  "nullable": true,
                  "primary_key": false,
                  "sensitive": null
                }
              ]
            }
          ]
        }
        """
        if not self.conn:
            raise ConnectionError("Not connected to Snowflake")

        try:
            cursor = self.conn.cursor()

            # Get list of tables
            cursor.execute(
                f"""
                SELECT TABLE_NAME, TABLE_ROWS
                FROM {database}.INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = '{schema}'
                  AND TABLE_TYPE = 'BASE TABLE'
                LIMIT {self.MAX_TABLES}
                """
            )
            tables_raw = cursor.fetchall()

            tables = []
            for table_name, row_count in tables_raw:
                # Get columns for this table
                columns = self._get_table_columns(database, schema, table_name)
                tables.append(
                    {
                        "name": table_name,
                        "rows_estimate": row_count or 0,
                        "columns": columns,
                    }
                )

            return {
                "database": database,
                "schema": schema,
                "tables": tables,
            }
        except Exception as e:
            logger.error(f"Schema discovery failed for {database}.{schema}: {e}")
            raise

    def _get_table_columns(
        self, database: str, schema: str, table_name: str
    ) -> List[Dict[str, Any]]:
        """Get column metadata for a table."""
        try:
            cursor = self.conn.cursor()

            # Query information_schema for columns
            cursor.execute(
                f"""
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    ORDINAL_POSITION
                FROM {database}.INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{schema}'
                  AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
                LIMIT {self.MAX_COLUMNS_PER_TABLE}
                """
            )
            columns_raw = cursor.fetchall()

            # Get primary key info
            pk_columns = self._get_primary_keys(database, schema, table_name)

            columns = []
            for col_name, col_type, is_nullable, _ in columns_raw:
                columns.append(
                    {
                        "name": col_name,
                        "type": col_type,
                        "nullable": is_nullable == "YES",
                        "primary_key": col_name in pk_columns,
                        "sensitive": None,
                    }
                )

            return columns
        except Exception as e:
            logger.error(
                f"Failed to get columns for {database}.{schema}.{table_name}: {e}"
            )
            return []

    def _get_primary_keys(self, database: str, schema: str, table_name: str) -> set:
        """Get primary key column names."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                SELECT COLUMN_NAME
                FROM {database}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                JOIN {database}.INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu
                  ON tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
                WHERE tc.TABLE_SCHEMA = '{schema}'
                  AND tc.TABLE_NAME = '{table_name}'
                  AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                """
            )
            return {row[0] for row in cursor.fetchall()}
        except Exception as e:
            logger.warning(
                f"Failed to get primary keys for {database}.{schema}.{table_name}: {e}"
            )
            return set()

    def test_connection(self) -> bool:
        """Test if connection is valid."""
        try:
            if not self.conn:
                return False
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception:
            return False
