
import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url_base = "http://31.97.117.123"
session = requests.Session()

# Login
login_url = f"{url_base}/login.php"
response = session.get(login_url, verify=False)
token_match = re.search(r"name='user_token'\s+value='([^']+)'", response.text)
user_token = token_match.group(1)

payload = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(login_url, data=payload, verify=False, allow_redirects=True)
print("[+] Logged in successfully\n")

# Check SQL injection page
sqli_url = f"{url_base}/vulnerabilities/sqli/"
response = session.get(sqli_url, verify=False)

# Save the SQLi page
with open("/tmp/sqli_page.html", "w") as f:
    f.write(response.text)

print(f"[*] SQLi page fetched: {len(response.text)} bytes")
print("\n[*] Content preview:")
print(response.text[:1500])

