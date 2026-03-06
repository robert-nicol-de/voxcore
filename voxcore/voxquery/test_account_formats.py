#!/usr/bin/env python3
"""Test different account identifier formats"""

import snowflake.connector

# Try different account formats
account_formats = [
    "bw77083",
    "bw77083.us-south-1.aws",
    "bw77083.us-east-1.aws",
    "bw77083.eu-west-1.aws",
    "bw77083.ap-southeast-1.aws",
]

password = "Robert210680!@#$"

for account in account_formats:
    print(f"\nTrying account: {account}")
    try:
        conn = snowflake.connector.connect(
            account=account,
            user="VOXQUERY",
            password=password,
            warehouse="COMPUTE_WH",
            database="FINANCIAL_TEST",
            schema="FINANCE",
            role="ACCOUNTADMIN"
        )
        print(f"✅ SUCCESS with account: {account}")
        
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_REGION()")
        account_info = cursor.fetchone()
        print(f"   Account: {account_info[0]}")
        print(f"   Region: {account_info[1]}")
        
        cursor.close()
        conn.close()
        break
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")
