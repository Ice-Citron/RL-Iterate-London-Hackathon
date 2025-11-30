
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
print("[+] Logged in successfully")
print(f"[+] Cookies: {session.cookies.get_dict()}\n")

# Now explore the vulnerable sections
dashboard = session.get(urljoin(target_url, "index.php"))
print("[+] Exploring available modules...\n")

# Check for vulnerabilities page
vulns_page = session.get(urljoin(target_url, "vulnerabilities.php"))
if "SQL Injection" in vulns_page.text:
    print("[+] Found SQL Injection module!")
    # Print relevant sections
    print(vulns_page.text[vulns_page.text.find("SQL Injection"):vulns_page.text.find("SQL Injection")+500])

