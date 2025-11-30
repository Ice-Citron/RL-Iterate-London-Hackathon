
import requests
import re

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

# Access SQL injection page
print("[*] Accessing SQL injection page...")
sqli_page = session.get(f"{target_url}/vulnerabilities/sqli/")

# Find the form/input area
if 'User ID' in sqli_page.text or 'user' in sqli_page.text.lower():
    print("[+] Found input form")
    
# Let's try a test query
print("\n[*] Testing basic query...")
test_params = {"id": "1", "Submit": "Submit"}
response = session.get(f"{target_url}/vulnerabilities/sqli/", params=test_params)

# Extract results
if "First name" in response.text:
    print("[+] Found user data!")
    # Extract the displayed user info
    match = re.search(r'First name:.*?<pre[^>]*>(.*?)</pre>', response.text, re.DOTALL)
    if match:
        print(match.group(1)[:500])

