
import requests
import re

session = requests.Session()
url = "http://31.97.117.123"

# Login with admin:password
login_page = session.get(f"{url}/login.php")
match = re.search(r"user_token'\s+value='([^']+)'", login_page.text)
user_token = match.group(1) if match else ""

data = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(f"{url}/login.php", data=data, allow_redirects=True)
print("[+] Login successful!")

# Get the source code - full version
source_page = session.get(f"{url}/vulnerabilities/view_source.php?id=sqli&security=low")
print("[*] Full source code:")
print(source_page.text)


