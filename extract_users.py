
import requests
import re

url = "http://31.97.117.123/"
session = requests.Session()

# Login first
response = session.get(f"{url}login.php")
token_match = re.search(r"user_token'\s+value='([a-f0-9]+)'", response.text)
csrf_token = token_match.group(1)

login_data = {
    "username": "admin",
    "password": "password",
    "user_token": csrf_token,
    "Login": "Login"
}

session.post(f"{url}login.php", data=login_data)

# Now explore the application - check for user injection or admin panels
pages_to_check = [
    "/index.php",
    "/vulnerabilities/sqli/",
    "/vulnerabilities/sqli_blind/",
    "/vulnerabilities/user_info.php",
    "/admin/",
    "/user_info.php",
]

print("[*] Checking for accessible user information pages...")
for page in pages_to_check:
    response = session.get(f"{url}{page}")
    if response.status_code == 200:
        print(f"[+] Found accessible page: {page}")
        if "user" in response.text.lower() or "name" in response.text.lower() or "password" in response.text.lower():
            print(f"    Contains user-related data")
            print(f"    Response length: {len(response.text)} bytes")

# Also check for common user listing endpoints
print("\n[*] Checking for user listing pages...")
test_pages = [
    "/users.php",
    "/user_list.php",
    "/members.php",
    "/admin/users.php",
    "/admin/members.php",
]

for page in test_pages:
    response = session.get(f"{url}{page}")
    if response.status_code == 200:
        print(f"[+] Found: {page}")

