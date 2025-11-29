
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
    
    # Now access the SQL injection page
    print("[*] Accessing SQL injection page...")
    response = session.get(sqli_url)
    
    # Look for the query parameter
    if "User ID" in response.text:
        print("[+] Found SQL injection vulnerability page")
        
        # Save the page
        with open("/tmp/sqli_page.html", "w") as f:
            f.write(response.text)
        
        print(response.text[:2000])

