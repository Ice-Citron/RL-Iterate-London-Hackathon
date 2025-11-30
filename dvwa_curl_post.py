
import subprocess
import re

# First, let's get the session with curl
target = "http://31.97.117.123"

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

# Step 3: Access SQL injection with a test query using GET
cmd = [
    'curl',
    '-s',
    '-b', '/tmp/cookies.txt',
    'http://31.97.117.123/vulnerabilities/sqli/?id=1'
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

# Save to file for inspection
with open('/tmp/sqli_response.html', 'w') as f:
    f.write(result.stdout)

print("[*] Response saved to /tmp/sqli_response.html")
print(f"[*] Response length: {len(result.stdout)}")

# Try to find pre section
if '<pre>' in result.stdout:
    start = result.stdout.find('<pre>')
    end = result.stdout.find('</pre>', start) + 6
    section = result.stdout[start:end]
    print("[+] Found pre section:")
    print(section[:500])
else:
    print("[-] No <pre> tag found in response")
    # Look for form
    if '<form' in result.stdout:
        print("[+] Form found, checking for results after form...")
        form_start = result.stdout.find('<form')
        form_end = result.stdout.find('</form>', form_start)
        form_section = result.stdout[form_start:form_end+7]
        print(form_section[-300:])

