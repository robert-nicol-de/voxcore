#!/usr/bin/env python3
"""Test different username formats"""

import snowflake.connector

account = "ko05278.af-south-1.aws"
password = "Robert210680!@#$"

# Try different username formats
usernames = [
    "bob joe",
    "BOB JOE",
    "bob_joe",
    "BOB_JOE",
    "bobjoe",
    "BOBJOE",
    '"bob joe"',
    "'bob joe'",
]

for username in usernames:
    print(f"\nTrying username: {username}")
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
        print(f"✅ SUCCESS with username: {username}")
        
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_USER()")
        user = cursor.fetchone()[0]
        print(f"   Current user: {user}")
        
        cursor.close()
        conn.close()
        break
    except Exception as e:
        error_msg = str(e)
        if "Incorrect username or password" in error_msg:
            print(f"❌ Wrong credentials")
        else:
            print(f"❌ Error: {error_msg[:80]}")
