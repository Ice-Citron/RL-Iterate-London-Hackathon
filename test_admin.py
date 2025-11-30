
import requests
import re

session = requests.Session()

# Get token and try admin:admin with lowercase
login_page = session.get('http://31.97.117.123/login.php')
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([^'\"]+)['\"]", login_page.text)
token = token_match.group(1) if token_match else ""

data = {
    'username': 'admin',
    'password': 'admin',
    'Login': 'Login',
    'user_token': token
}

response = session.post('http://31.97.117.123/login.php', data=data, allow_redirects=True)
print(f"Status: {response.status_code}")
print(f"URL after login: {response.url}")
print(f"Full response length: {len(response.text)}")

# Check for success indicators
if "welcome" in response.text.lower():
    print("✓ LOGIN SUCCESSFUL!")
    print("\nResponse snippet:")
    print(response.text[:2000])
else:
    print("Login page returned")
    # Check cookies
    print(f"\nCookies: {session.cookies.get_dict()}")
    
    # Try to follow redirect
    try:
        index_page = session.get('http://31.97.117.123/index.php')
        print(f"index.php status: {index_page.status_code}")
        print(f"index.php content (first 1000):")
        print(index_page.text[:1000])
    except:
        pass

