
import requests
import re

session = requests.Session()

# Get fresh token and login
resp = session.get("http://31.97.117.123/login.php")
match = re.search(r"user_token['\"] value=['\"](.*?)['\"]", resp.text)
token = match.group(1) if match else "574fcd28f93f57c93cb554ecaf3ca520"

# Login
login_data = {
    "username": "admin",
    "password": "password",
    "Login": "Login",
    "user_token": token
}

resp = session.post("http://31.97.117.123/login.php", data=login_data)

# Get index page
resp = session.get("http://31.97.117.123/index.php")
print("Main page response length:", len(resp.text))

# Extract all links/vulnerabilities available
links = re.findall(r'href=["\']([^"\']+)["\']', resp.text)
print("\nFound links:")
for link in links[:20]:
    print(f"  - {link}")

# Save the response to analyze structure
print("\n\nSearching for menu items...")
if "SQL Injection" in resp.text:
    print("Found SQL Injection vulnerability link")
if "User" in resp.text:
    print("Found User-related content")

print("\nFirst 3000 chars of page:")
print(resp.text[:3000])

