#!/usr/bin/env python3
import requests
import base64

# Read the landing.html file
with open('frontend/dist/landing.html', 'r', encoding='utf-8') as f:
    content = f.read()

# cPanel credentials
token = '1DBXGR4SQ1OVQ40WR9FQOCS5Y73TUQWV'
cpanel_host = 'cloud771.thundercloud.uk'
cpanel_user = 'voxcoreo'

# Encode content to base64
content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')

# Build URL
url = f'https://{cpanel_host}:2083/json-api/cpanel?cpanel_jsonapi_apiversion=2&cpanel_jsonapi_user={cpanel_user}&cpanel_jsonapi_func=fileman_save_file&filepath=/public_html/index.html'

# Headers
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Payload
payload = {
    'filepath': '/public_html/index.html',
    'file_content': content_b64
}

print('=' * 60)
print('UPLOADING LANDING PAGE TO CPANEL')
print('=' * 60)
print(f'File: landing.html')
print(f'Size: {len(content)} bytes')
print(f'Target: https://voxcore.org/')
print()

try:
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    response = requests.post(url, json=payload, headers=headers, verify=False, timeout=30)
    
    print(f'HTTP Status: {response.status_code}')
    print(f'Response Length: {len(response.text)} bytes')
    print()
    print('Response:')
    print(response.text[:1000])
    print()
    
    if response.status_code == 200:
        print('SUCCESS! Landing page uploaded.')
        print()
        print('Visit: https://voxcore.org/')
        print('Press Ctrl+Shift+R to hard refresh cache')
    else:
        print(f'Upload may have failed. Status: {response.status_code}')
        
except Exception as e:
    print(f'ERROR: {str(e)}')
    import traceback
    traceback.print_exc()

print()
print('=' * 60)
