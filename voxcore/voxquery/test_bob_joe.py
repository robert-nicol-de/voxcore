#!/usr/bin/env python3
"""Test connection with bob joe credentials"""

import snowflake.connector

account = "ko05278.af-south-1.aws"
username = "bob joe"
password = "Robert210680!@#$"

print(f"Testing account: {account}")
print(f"Username: {username}")

try:
    conn = snowflake.connector.connect(
        account=account,
        user=username,
        password=password,
        warehouse="COMPUTE_WH",
        database="FINANCIAL_TEST",
        schema="PUBLIC",
        role="ACCOUNTADMIN"
    )
    print(f"✅ SUCCESS!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_REGION(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_USER()")
    account_info = cursor.fetchone()
    print(f"   Account: {account_info[0]}")
    print(f"   Region: {account_info[1]}")
    print(f"   Database: {account_info[2]}")
    print(f"   Schema: {account_info[3]}")
    print(f"   User: {account_info[4]}")
    
    # Try a simple query
    print("\nTesting query execution...")
    cursor.execute("SELECT 1 AS test_col")
    result = cursor.fetchone()
    print(f"✅ Query executed: {result}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Failed: {str(e)}")
