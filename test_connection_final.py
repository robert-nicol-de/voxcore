import requests
import json

# First, connect to the database
print('Step 1: Connecting to Snowflake...')
connect_response = requests.post('http://localhost:8000/api/v1/auth/connect', json={
    'database': 'snowflake',
    'credentials': {
        'host': 'we08391.af-south-1.aws',
        'username': 'VOXQUERY',
        'password': 'Robert210680!@#$',
        'database': 'VOXQUERYTRAININGPIN2025',
        'schema': 'PUBLIC',
        'warehouse': 'COMPUTE_WH',
        'role': 'ACCOUNTADMIN'
    }
})

print(f'Connect Status: {connect_response.status_code}')
if connect_response.status_code != 200:
    print('Connection failed!')
    print(connect_response.text)
    exit(1)

# Now test SQL generation and query execution
print('\nStep 2: Testing SQL generation and query execution...')
response = requests.post('http://localhost:8000/api/v1/query', json={
    'question': 'Show me the top 10 records',
    'warehouse': 'snowflake',
    'execute': True
})

print(f'Query Status: {response.status_code}')
if response.status_code == 200:
    print('✅ QUERY EXECUTION SUCCESSFUL!')
    result = response.json()
    print(json.dumps(result, indent=2, default=str))
else:
    print('❌ Query execution failed')
    print(response.text[:500])
