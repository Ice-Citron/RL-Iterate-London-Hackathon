
import requests
import re
from urllib.parse import urljoin

target_url = "http://31.97.117.123/"
session = requests.Session()

# Login first
login_page = session.get(urljoin(target_url, "login.php"))
token_match = re.search(r"user_token' value='([^']+)'", login_page.text)
token = token_match.group(1)

login_data = {
    "username": "admin",
    "password": "password",
    "user_token": token,
    "Login": "Login"
}

response = session.post(urljoin(target_url, "login.php"), data=login_data)

# Access the SQL Injection vulnerability
sqli_page = session.get(urljoin(target_url, "vulnerabilities/sqli/"))

print("[+] SQL Injection page loaded")
print("\n[+] Page content snippet:")
print(sqli_page.text)

