# SQL Dialect Registry for VoxCore
from .postgres_engine import PostgresEngine
from .snowflake_engine import SnowflakeEngine
# Add more imports as you implement more engines

SQL_DIALECT_REGISTRY = {
    "postgres": PostgresEngine(),
    "snowflake": SnowflakeEngine(),
    # Add more dialects here
}

def get_sql_engine(dialect: str):
    return SQL_DIALECT_REGISTRY.get(dialect)
