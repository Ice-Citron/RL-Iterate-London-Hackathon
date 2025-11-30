
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

# Step 3: Try to access the source code view
print("\n[*] Accessing SQL injection source code...")

cmd = [
    'curl',
    '-s',
    '-b', '/tmp/cookies.txt',
    'http://31.97.117.123/vulnerabilities/view_source.php?id=sqli&security=low'
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

# Save to file
with open('/tmp/sqli_source.html', 'w') as f:
    f.write(result.stdout)

print("[*] Source code page saved to /tmp/sqli_source.html")

# Look for code section
if '<pre' in result.stdout or '<code' in result.stdout:
    # Find the source code
    start_idx = result.stdout.find('<pre')
    if start_idx == -1:
        start_idx = result.stdout.find('<code')
    
    if start_idx != -1:
        end_idx = result.stdout.find('</pre>', start_idx)
        if end_idx == -1:
            end_idx = result.stdout.find('</code>', start_idx)
        
        if end_idx != -1:
            code_section = result.stdout[start_idx:end_idx+7]
            # Unescape HTML
            code_unescaped = unescape(code_section)
            print("[+] Source code found:")
            print(code_unescaped[:2000])

