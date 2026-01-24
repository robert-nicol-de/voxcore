# VoxQuery with AdventureWorks2022 Setup Guide

## Overview
VoxQuery has been updated to work with **SQL Server and AdventureWorks2022**. The backend now:
- ✅ Generates T-SQL queries for AdventureWorks
- ✅ Executes queries against your SQL Server database
- ✅ Returns real data from your AdventureWorks instance
- ✅ Generates interactive charts from the results

## Prerequisites

### 1. SQL Server Setup
- Have SQL Server with **AdventureWorks2022** database installed
- SSMS (SQL Server Management Studio) running
- Know your SQL Server details:
  - **Server name** (e.g., `localhost`, `COMPUTERNAME\SQLEXPRESS`, or IP)
  - **Port** (default: 1433)
  - **Database**: `AdventureWorks2022`
  - **Username** and **Password**

### 2. Python Dependencies
```bash
pip install pyodbc
```

### 3. ODBC Driver
- Ensure **ODBC Driver 17 for SQL Server** is installed on your system
- Download from: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

## How to Connect

### Step 1: Open VoxQuery
```bash
# Terminal 1 - Backend
cd c:\Users\USER\Documents\trae_projects\VoxQuery\backend
python main_simple.py

# Terminal 2 - Frontend
cd c:\Users\USER\Documents\trae_projects\VoxQuery\frontend
npm run dev
```

### Step 2: Configure Database Connection
1. Click **⚙️ Settings** in the left sidebar
2. Change **Database** dropdown to **🟦 SQL Server**
3. Fill in connection details:
   - **Host**: Your SQL Server name (e.g., `DESKTOP-ABC123\SQLEXPRESS`)
   - **Username**: Your SQL Server login (e.g., `sa`)
   - **Password**: Your SQL Server password
   - **Database**: `AdventureWorks2022`
   - **Port**: `1433` (or your custom port)

### Step 3: Test Connection
1. Click **🔗 Test Connection** button
2. You should see: `✅ Successfully connected to SQL Server!`
3. If it fails, check:
   - SQL Server is running
   - Credentials are correct
   - Database name is exactly `AdventureWorks2022`
   - ODBC Driver 17 is installed

### Step 4: Connect
1. Click **✅ Connect** button
2. VoxQuery is now connected to your AdventureWorks database
3. The **Connection Header** at top shows your current database

## Available Queries

### 1. Sales Trends
**Ask:** "Show me sales trends" or "Sales by quarter"
- Returns: Quarterly sales data with bar chart
- Tables: `Sales.SalesOrderHeader`, `Sales.SalesOrderDetail`

### 2. Revenue by Customer
**Ask:** "What's the revenue by customer?" or "Monthly revenue"
- Returns: Top 20 customers with monthly revenue and line chart
- Tables: `Sales.Customer`, `Person.Person`, `Sales.SalesOrderHeader`

### 3. Top Customers
**Ask:** "Who are the top customers?" or "Top customers by spending"
- Returns: Top 10 customers by total spent with doughnut chart
- Tables: `Sales.Customer`, `Sales.SalesOrderHeader`, `Sales.SalesOrderDetail`

### 4. Product Sales
**Ask:** "Product sales" or "Top products by revenue"
- Returns: Top 15 products by revenue
- Tables: `Production.Product`, `Sales.SalesOrderDetail`

## Connection Storage

Once connected, VoxQuery stores:
- ✅ Your last used database (loads on next startup)
- ✅ Per-database credentials (SQLServer creds separate from Snowflake, etc.)
- ✅ Connection status (shown in header)

All data is encrypted in browser localStorage.

## AdventureWorks Schema Reference

### Main Tables Used:
```sql
-- Customers
Sales.Customer (CustomerID, PersonID, TerritoryID)
Person.Person (BusinessEntityID, FirstName, LastName)

-- Orders
Sales.SalesOrderHeader (SalesOrderID, CustomerID, OrderDate, TotalDue)
Sales.SalesOrderDetail (SalesOrderID, ProductID, LineTotal, Quantity)

-- Products
Production.Product (ProductID, Name, ListPrice)
```

## Troubleshooting

### Connection Failed: "Invalid ODBC Driver"
```
Solution: Install ODBC Driver 17 for SQL Server
Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### Connection Failed: "Login Failed"
```
Solution: 
1. Check username/password in SSMS
2. Verify SQL Server Authentication is enabled (not Windows Auth only)
3. Check database name is exactly: AdventureWorks2022
```

### Connection Failed: "Cannot Connect to Server"
```
Solution:
1. Verify SQL Server is running: Services > SQL Server (MSSQLSERVER)
2. Check correct server name: Open SSMS, copy exact server name
3. Verify port: Usually 1433, check in SQL Server Configuration Manager
```

### Query Returns "No Results"
```
Solution:
1. Ensure connection was successful (check header)
2. Click "Test Connection" again to verify
3. Manually run query in SSMS to verify data exists
4. Check database name and tables exist
```

### "pyodbc module not found"
```
Solution: pip install pyodbc
Then restart the backend: python main_simple.py
```

## Example Connections

### Local SQL Server (Windows Auth)
```
Server: DESKTOP-XYZ123\SQLEXPRESS
Username: sa
Password: YourPassword
Database: AdventureWorks2022
Port: 1433
```

### Named Instance
```
Server: SERVERNAME\INSTANCENAME
Username: sa
Password: password
Database: AdventureWorks2022
Port: 1433
```

### Remote SQL Server
```
Server: 192.168.1.100
Username: sqladmin
Password: password
Database: AdventureWorks2022
Port: 1433
```

## Features Enabled

✅ Real data from AdventureWorks2022
✅ T-SQL query generation
✅ Interactive charts (bar, line, doughnut)
✅ Per-database login (SQL Server separate from Snowflake)
✅ Connection persistence across sessions
✅ Test connection validation
✅ Professional report viewer
✅ Print to PDF support

## Next Steps

1. **Connect to AdventureWorks2022**
2. **Ask natural language questions:**
   - "Show me sales trends"
   - "Top customers by revenue"
   - "Product sales analysis"
3. **View interactive reports with charts**
4. **Print or download results**

## Support

If you encounter issues:
1. Check SSMS can connect with your credentials
2. Verify AdventureWorks2022 database exists: `SELECT * FROM Sales.Customer LIMIT 5;`
3. Check backend logs for SQL errors
4. Ensure ODBC Driver 17 is installed
