#!/usr/bin/env python3
"""Test connection with correct account identifier"""

import snowflake.connector

# Correct account identifier from the URL
account = "ko05278.af-south-1.aws"
password = "Robert210680!@#$"

print(f"Testing account: {account}")
try:
    conn = snowflake.connector.connect(
        account=account,
        user="VOXQUERY",
        password=password,
        warehouse="COMPUTE_WH",
        database="FINANCIAL_TEST",
        schema="PUBLIC",
        role="ACCOUNTADMIN"
    )
    print(f"✅ SUCCESS with account: {account}")
    
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_REGION(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
    account_info = cursor.fetchone()
    print(f"   Account: {account_info[0]}")
    print(f"   Region: {account_info[1]}")
    print(f"   Database: {account_info[2]}")
    print(f"   Schema: {account_info[3]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Failed: {str(e)}")
