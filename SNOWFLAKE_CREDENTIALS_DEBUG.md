# Snowflake Credentials Debug

## Current Issue
Getting "Incorrect username or password was specified" error when trying to connect to Snowflake.

## What We Know
- Account: `we08391.af-south-1.aws` ✓ (correct format, reaches Snowflake)
- Username: `VOXQUERY` (from profile image)
- Password: `VoxQuery@2024` (from config file)
- Database: `VOXQUERYTRAININGPIN2025` (from your message)
- Schema: `PUBLIC`
- Warehouse: `COMPUTE_WH`
- Role: `ACCOUNTADMIN`

## The Problem
The credentials are being rejected at the Snowflake authentication level. This means either:
1. The password is wrong
2. The username is wrong
3. The account identifier is wrong (but we know it's correct because it reaches Snowflake)

## How to Debug

### Option 1: Test in Snowflake Web UI
1. Go to https://we08391.af-south-1.aws.snowflakecomputing.com
2. Try logging in with:
   - Username: `VOXQUERY`
   - Password: `VoxQuery@2024`
3. If it fails, the credentials are wrong
4. If it works, there might be a connection issue with the Python connector

### Option 2: Check Snowflake Account Settings
1. Log in to Snowflake as an admin
2. Go to Admin > Users & Roles > Users
3. Find the `VOXQUERY` user
4. Check if the password is correct
5. Check if the user has the right roles/permissions

### Option 3: Try Different Password
The password might have changed. Common variations:
- `VoxQuery@2025` (with 2025 instead of 2024)
- `VoxQuery@2024!` (with special character)
- Check if there's a password reset needed

## Next Steps

1. **Verify credentials in Snowflake Web UI** - This is the fastest way to confirm if the username/password is correct
2. **If credentials are correct**, then we need to check if there's an issue with the Python Snowflake connector
3. **If credentials are wrong**, update them in the config file and try again

## Files to Update
- `backend/config/snowflake.ini` - Update password if needed
- `backend/voxquery/core/connection_manager.py` - Already has detailed logging

## Current Backend Status
- Backend is running with enhanced logging
- When you click "Connect" in the UI, the backend logs will show:
  - Connection attempt
  - Available databases (if connection succeeds)
  - Which USE statement fails (if any)
