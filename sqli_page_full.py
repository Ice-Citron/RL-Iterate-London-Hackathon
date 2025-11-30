
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
    
    # Get the SQLi page
    response = session.get(sqli_url)
    
    # Save and print the full page
    with open("/tmp/sqli_full_page.html", "w") as f:
        f.write(response.text)
    
    # Look for form input areas
    print("[*] Searching for input fields...")
    if "<input" in response.text:
        # Extract form area
        start = response.text.find("<form")
        end = response.text.find("</form>") + 7
        if start > 0 and end > start:
            print(response.text[start:end])

