#!/usr/bin/env python3
"""
Full Snowflake schema DDL for prompt injection.
Based on training dataset table references.
"""

SNOWFLAKE_SCHEMA_DDL = """
-- Full Snowflake Schema (Dimension & Fact Tables)
-- Use ONLY these tables and columns in your SQL

CREATE TABLE sales_fact (
    transaction_id VARCHAR(50) PRIMARY KEY,
    store_id INT NOT NULL,
    product_id INT NOT NULL,
    customer_id INT,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(20),  -- 'SALE' or 'RETURN'
    revenue_amount DECIMAL(18,2) NOT NULL,
    cogs_amount DECIMAL(18,2) NOT NULL,
    units INT NOT NULL,
    channel VARCHAR(50),  -- 'Retail', 'Online', 'Wholesale'
    FOREIGN KEY (store_id) REFERENCES store_dim(store_id),
    FOREIGN KEY (product_id) REFERENCES product_dim(product_id)
);

CREATE TABLE product_dim (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    supplier_id INT,
    cost_per_unit DECIMAL(18,2),
    list_price DECIMAL(18,2)
);

CREATE TABLE store_dim (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    store_format VARCHAR(50),  -- 'Flagship', 'Express', 'Outlet'
    square_meters DECIMAL(10,2)
);

CREATE TABLE store_details (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100),
    square_meters DECIMAL(10,2),
    FOREIGN KEY (store_id) REFERENCES store_dim(store_id)
);

CREATE TABLE inventory_snapshot (
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    on_hand_quantity INT NOT NULL,
    reorder_point INT,
    last_updated DATE,
    PRIMARY KEY (product_id, store_id),
    FOREIGN KEY (product_id) REFERENCES product_dim(product_id),
    FOREIGN KEY (store_id) REFERENCES store_dim(store_id)
);

CREATE TABLE sales_target (
    store_id INT NOT NULL,
    target_year INT NOT NULL,
    target_amount DECIMAL(18,2) NOT NULL,
    PRIMARY KEY (store_id, target_year),
    FOREIGN KEY (store_id) REFERENCES store_dim(store_id)
);

CREATE TABLE budget_plan (
    store_id INT NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    budget_year INT NOT NULL,
    budget_period VARCHAR(20),  -- 'YTD', 'MTD', 'QTD'
    budget_amount DECIMAL(18,2) NOT NULL,
    PRIMARY KEY (store_id, category_name, budget_year, budget_period),
    FOREIGN KEY (store_id) REFERENCES store_dim(store_id)
);

CREATE TABLE operating_expenses (
    expense_id VARCHAR(50) PRIMARY KEY,
    expense_date DATE NOT NULL,
    expense_amount DECIMAL(18,2) NOT NULL,
    expense_category VARCHAR(100),  -- 'OPERATING', 'INTEREST', 'TAX'
    department VARCHAR(100)
);

-- Key Snowflake Functions to Use:
-- DATE_TRUNC('year', date_col) - truncate to year start
-- DATE_TRUNC('month', date_col) - truncate to month start
-- DATE_TRUNC('quarter', date_col) - truncate to quarter start
-- DATE_TRUNC('week', date_col) - truncate to week start
-- DATEADD(year, -1, date_col) - subtract 1 year
-- DATEADD(month, -1, date_col) - subtract 1 month
-- DATEADD(day, -90, date_col) - subtract 90 days
-- CURRENT_DATE - today's date
-- DAYNAME(date_col) - day name (Monday, Tuesday, etc.)
-- DAYOFWEEK(date_col) - day of week (1-7)
-- QUALIFY ROW_NUMBER() OVER (...) <= N - top N rows per group
-- ROUND(value, 2) - round to 2 decimals
-- NULLIF(value, 0) - return NULL if value is 0
-- FULL OUTER JOIN - join with all rows from both tables
-- WITH cte_name AS (...) - common table expression
"""

def get_schema_ddl() -> str:
    """Return full schema DDL for prompt injection."""
    return SNOWFLAKE_SCHEMA_DDL
