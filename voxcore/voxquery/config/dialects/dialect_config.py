"""
Unified dialect configuration system
Supports SQL Server, Snowflake, PostgreSQL, BigQuery, Redshift
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class DialectConfig:
    """Complete dialect configuration"""
    name: str
    limit_syntax: str  # LIMIT or TOP
    top_position: str  # end_of_query or after_select
    date_current: str  # CURRENT_DATE or GETDATE()
    date_trunc: str  # DATE_TRUNC or DATEPART
    date_add: str  # DATEADD or DATE_ADD
    string_concat: str  # || or +
    schema_separator: str  # . or ::
    identifier_quote: str  # " or [ or `
    
    # Prompt rules
    dialect_lock: str
    forbidden_syntax: List[str]
    required_syntax: List[str]
    top_format: str
    date_format: str
    schema_required: bool
    
    # Schema mapping for finance queries
    accounts_table: str
    accounts_balance_col: str
    accounts_name_col: str
    accounts_id_col: str
    transactions_table: str
    holdings_table: str
    securities_table: str
    security_prices_table: str
    
    # Finance keywords
    finance_keywords: Dict[str, str]
    
    # Whitelist tables
    whitelist_tables: Dict[str, str]
    
    # Forbidden tables
    forbidden_tables: List[str]
    
    # Validation
    hard_reject_keywords: List[str]
    score_threshold: float
    fallback_on_fail: bool
    
    # Fallback query
    fallback_sql: str
    
    # Export options
    export_csv: bool
    export_excel: bool
    export_markdown: bool
    export_email: bool
    export_ssrs: bool


# SQL Server Configuration
SQLSERVER_CONFIG = DialectConfig(
    name="sqlserver",
    limit_syntax="TOP",
    top_position="after_select",
    date_current="GETDATE()",
    date_trunc="DATEPART",
    date_add="DATEADD",
    string_concat="+",
    schema_separator=".",
    identifier_quote="[",
    
    dialect_lock="You are connected to Microsoft SQL Server (T-SQL ONLY). NEVER use LIMIT, ALWAYS use TOP N.",
    forbidden_syntax=["LIMIT", "DATE_TRUNC", "EXTRACT", "CURRENT_DATE", "||"],
    required_syntax=["TOP", "GETDATE()", "DATEADD", "DATEPART"],
    top_format="SELECT TOP {n} ... FROM ... ORDER BY column DESC",
    date_format="Use GETDATE(). Use DATEADD(day, n, col). Use DATEPART(month, col).",
    schema_required=True,
    
    accounts_table="Sales.Customer",
    accounts_balance_col="TotalDue",
    accounts_name_col="FirstName + ' ' + LastName",
    accounts_id_col="CustomerID",
    transactions_table="Sales.SalesOrderHeader",
    holdings_table="Production.Product",
    securities_table="Production.Product",
    security_prices_table="Production.ProductListPriceHistory",
    
    finance_keywords={
        "balance": "Sales.SalesOrderHeader.TotalDue",
        "account": "Sales.Customer",
        "top_accounts": "Sales.Customer ORDER BY TotalDue DESC",
        "holdings": "Production.Product",
        "transactions": "Sales.SalesOrderHeader",
        "portfolio": "Production.Product",
        "securities": "Production.Product",
        "prices": "Production.ProductListPriceHistory",
    },
    
    whitelist_tables={
        "SALES.CUSTOMER": "Sales.Customer",
        "SALES.SALESORDERHEADER": "Sales.SalesOrderHeader",
        "PERSON.PERSON": "Person.Person",
        "PRODUCTION.PRODUCT": "Production.Product",
        "HUMANRESOURCES.EMPLOYEE": "HumanResources.Employee",
    },
    
    forbidden_tables=["sys.tables", "information_schema.tables", "DatabaseLog", "ErrorLog"],
    
    hard_reject_keywords=["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "LIMIT"],
    score_threshold=0.7,
    fallback_on_fail=True,
    
    fallback_sql="""
    SELECT TOP 10 c.CustomerID, p.FirstName + ' ' + p.LastName AS CustomerName, SUM(soh.TotalDue) AS total_balance
    FROM Sales.Customer c
    JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
    JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
    GROUP BY c.CustomerID, p.FirstName, p.LastName
    ORDER BY total_balance DESC
    """,
    
    export_csv=True,
    export_excel=True,
    export_markdown=True,
    export_email=True,
    export_ssrs=True,
)


# Snowflake Configuration
SNOWFLAKE_CONFIG = DialectConfig(
    name="snowflake",
    limit_syntax="LIMIT",
    top_position="end_of_query",
    date_current="CURRENT_DATE()",
    date_trunc="DATE_TRUNC",
    date_add="DATEADD",
    string_concat="||",
    schema_separator=".",
    identifier_quote='"',
    
    dialect_lock="You are connected to Snowflake SQL. Use standard Snowflake syntax.",
    forbidden_syntax=["TOP", "GETDATE", "DATEPART", "square bracket identifiers"],
    required_syntax=["LIMIT", "CURRENT_DATE()", "DATE_TRUNC()"],
    top_format="SELECT ... FROM ... ORDER BY column DESC LIMIT {n}",
    date_format="Use CURRENT_DATE(). Use DATE_TRUNC('month', col). Use DATEADD(day, n, col).",
    schema_required=True,
    
    accounts_table="ACCOUNTS",
    accounts_balance_col="BALANCE",
    accounts_name_col="ACCOUNT_NAME",
    accounts_id_col="ACCOUNT_ID",
    transactions_table="TRANSACTIONS",
    holdings_table="HOLDINGS",
    securities_table="SECURITIES",
    security_prices_table="SECURITY_PRICES",
    
    finance_keywords={
        "balance": "ACCOUNTS.BALANCE",
        "account": "ACCOUNTS",
        "top_accounts": "ACCOUNTS ORDER BY BALANCE DESC",
        "holdings": "HOLDINGS",
        "transactions": "TRANSACTIONS",
        "portfolio": "HOLDINGS",
        "securities": "SECURITIES",
        "prices": "SECURITY_PRICES",
    },
    
    whitelist_tables={
        "ACCOUNTS": "PUBLIC.ACCOUNTS",
        "TRANSACTIONS": "PUBLIC.TRANSACTIONS",
        "HOLDINGS": "PUBLIC.HOLDINGS",
        "SECURITIES": "PUBLIC.SECURITIES",
        "SECURITY_PRICES": "PUBLIC.SECURITY_PRICES",
    },
    
    forbidden_tables=["sys.tables", "information_schema.tables"],
    
    hard_reject_keywords=["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE"],
    score_threshold=0.7,
    fallback_on_fail=True,
    
    fallback_sql="""
    SELECT ACCOUNT_ID, ACCOUNT_NAME, BALANCE FROM PUBLIC.ACCOUNTS ORDER BY BALANCE DESC LIMIT 10
    """,
    
    export_csv=True,
    export_excel=True,
    export_markdown=True,
    export_email=True,
    export_ssrs=False,
)


# Registry of all dialect configurations
DIALECT_REGISTRY: Dict[str, DialectConfig] = {
    "sqlserver": SQLSERVER_CONFIG,
    "snowflake": SNOWFLAKE_CONFIG,
}

# Try to load SQL Server config from INI file
try:
    from voxquery.config.ini_loader import SQLSERVER_CONFIG_FROM_INI
    if SQLSERVER_CONFIG_FROM_INI:
        DIALECT_REGISTRY["sqlserver"] = SQLSERVER_CONFIG_FROM_INI
        print("✅ Using SQL Server config from INI file")
except Exception as e:
    print(f"⚠️  Could not load SQL Server config from INI: {e}")
    print("   Using hardcoded SQL Server config")


def get_dialect_config(dialect: str) -> Optional[DialectConfig]:
    """Get configuration for a dialect"""
    return DIALECT_REGISTRY.get(dialect.lower())


def get_runtime_rewrite_function(dialect: str):
    """Get the runtime rewrite function for a dialect"""
    config = get_dialect_config(dialect)
    if not config:
        return None
    
    if dialect.lower() == "sqlserver":
        from voxquery.core.sql_generator import SQLGenerator
        return SQLGenerator.force_tsql
    
    # Add other dialect rewrite functions as needed
    return None
