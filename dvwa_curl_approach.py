
import subprocess
import re

# First, let's get the session with curl
target = "http://31.97.117.123"

# Use curl to login and extract data
cmd = [
    'curl',
    '-s',
    '-c', '/tmp/cookies.txt',
    'http://31.97.117.123/login.php'
]

result = subprocess.run(cmd, capture_output=True, text=True)
print("[*] Got login page")

# Extract token from login page
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([a-f0-9]+)['\"]", result.stdout)
token = token_match.group(1) if token_match else None
print(f"[*] Token: {token}")

# Login with admin:password
cmd = [
    'curl',
    '-s',
    '-b', '/tmp/cookies.txt',
    '-c', '/tmp/cookies.txt',
    '-d', f'username=admin&password=password&user_token={token}&Login=Login',
    'http://31.97.117.123/login.php'
]

result = subprocess.run(cmd, capture_output=True, text=True)
print("[*] Attempted login")

# Now try to access SQL injection page
cmd = [
    'curl',
    '-s',
    '-b', '/tmp/cookies.txt',
    'http://31.97.117.123/vulnerabilities/sqli/?id=1'
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
print("[*] Accessing SQL injection page...")

# Look for the pre tag
if '<pre>' in result.stdout:
    start = result.stdout.find('<pre>')
    end = result.stdout.find('</pre>', start) + 6
    section = result.stdout[start:end]
    print("[+] Pre section:")
    print(section)
else:
    print("[-] No pre section found")
    print(result.stdout[-500:])

