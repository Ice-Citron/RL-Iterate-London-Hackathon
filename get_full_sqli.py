
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

# Navigate to SQL injection page
resp = session.get("http://31.97.117.123/vulnerabilities/sqli/")
print("Full SQL Injection page:")
print(resp.text)

