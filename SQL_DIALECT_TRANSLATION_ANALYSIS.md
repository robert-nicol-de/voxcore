# SQL Dialect Translation Analysis - Snowflake vs SQL Server

## Problem
SQL generated for Snowflake doesn't work on SQL Server because of syntax differences.

## Key Differences Between Snowflake and SQL Server

### 1. LIMIT vs TOP
- **Snowflake**: `SELECT * FROM table LIMIT 10`
- **SQL Server**: `SELECT TOP 10 * FROM table`

### 2. String Functions
- **Snowflake**: `UPPER()`, `LOWER()`, `SUBSTRING()`, `LENGTH()`
- **SQL Server**: `UPPER()`, `LOWER()`, `SUBSTRING()`, `LEN()` (not LENGTH)

### 3. Date Functions
- **Snowflake**: `CURRENT_DATE()`, `CURRENT_TIMESTAMP()`, `DATE_TRUNC()`
- **SQL Server**: `GETDATE()`, `CAST(GETDATE() AS DATE)`, `DATEPART()`

### 4. Casting
- **Snowflake**: `CAST(col AS VARCHAR)`, `CAST(col AS INTEGER)`
- **SQL Server**: `CAST(col AS VARCHAR)`, `CAST(col AS INT)` (INT not INTEGER)

### 5. String Concatenation
- **Snowflake**: `||` operator
- **SQL Server**: `+` operator or `CONCAT()`

### 6. Window Functions
- **Snowflake**: Supports window functions inside aggregates
- **SQL Server**: Does NOT support window functions inside aggregates

### 7. OFFSET/LIMIT
- **Snowflake**: `OFFSET n LIMIT m`
- **SQL Server**: `OFFSET n ROWS FETCH NEXT m ROWS ONLY`

### 8. NULL Handling
- **Snowflake**: `ISNULL()` or `COALESCE()`
- **SQL Server**: `ISNULL()` or `COALESCE()`

### 9. Aggregate Functions
- **Snowflake**: `COUNT(DISTINCT col)`
- **SQL Server**: `COUNT(DISTINCT col)` (same)

### 10. Table/Column Quoting
- **Snowflake**: Double quotes for identifiers, case-insensitive by default
- **SQL Server**: Square brackets `[table].[column]` or double quotes

## Current Implementation Status

### What's Already Implemented
- `_translate_to_dialect()` method in SQLGenerator
- LIMIT → TOP conversion
- OFFSET/LIMIT → OFFSET/FETCH conversion
- Window function in aggregate detection

### What's Missing
- LENGTH() → LEN() conversion
- CURRENT_DATE() → CAST(GETDATE() AS DATE) conversion
- CURRENT_TIMESTAMP() → GETDATE() conversion
- DATE_TRUNC() → DATEPART() conversion
- String concatenation `||` → `+` conversion
- INTEGER → INT conversion
- Table/column quoting adjustments

## Solution Approach

Create a comprehensive dialect translator that:
1. Detects the target dialect (SQL Server, Snowflake, Postgres, etc.)
2. Applies dialect-specific transformations
3. Validates the output SQL
4. Falls back to original if translation fails

## Implementation Plan

1. Enhance `_translate_to_dialect()` method with comprehensive transformations
2. Add dialect-specific function mappings
3. Add dialect-specific operator mappings
4. Test with sample queries on both platforms
5. Add logging to track transformations
