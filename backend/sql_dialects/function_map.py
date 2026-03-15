# SQL Function Mapping Registry for VoxCore
# Maps logical function names to dialect-specific implementations

SQL_FUNCTION_MAP = {
    "current_date": {
        "postgres": "NOW()",
        "snowflake": "CURRENT_DATE",
        "sqlserver": "GETDATE()",
        "bigquery": "CURRENT_DATE",
        # Add more dialects as needed
    },
    "string_concat": {
        "postgres": "||",
        "snowflake": "||",
        "sqlserver": "+",
        "bigquery": "CONCAT",
    },
    "date_add": {
        "postgres": "+ INTERVAL",
        "snowflake": "DATEADD",
        "sqlserver": "DATEADD",
        "bigquery": "DATE_ADD",
    },
    # Add more function mappings as needed
}
