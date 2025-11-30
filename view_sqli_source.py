
import requests
import re

base_url = "http://31.97.117.123"
login_url = f"{base_url}/login.php"

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
    
    # Get the source code
    print("[*] Attempting to view source code...")
    
    view_source_url = f"{base_url}/vulnerabilities/view_source.php"
    params = {
        "id": "sqli",
        "security": "low"
    }
    
    response = session.get(view_source_url, params=params, timeout=10)
    
    # Look for <pre> sections
    if "<pre>" in response.text:
        start = response.text.find("<pre>")
        end = response.text.find("</pre>") + 6
        print(response.text[start:end])
        
        # Also save it
        with open("/tmp/sqli_source.html", "w") as f:
            f.write(response.text)

