
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
    
    # Test with basic ID
    print("[*] Testing with basic ID...")
    params = {
        "id": "1",
        "Submit": "Submit"
    }
    
    response = session.get(sqli_url, params=params, timeout=10)
    
    # Look for user data
    if "First name:" in response.text:
        print("[+] Found user data!")
        start = response.text.find("First name:")
        end = response.text.find("</table>", start) + 8
        print(response.text[start:end])
    
    # Save full response
    with open("/tmp/sqli_test_id_1.html", "w") as f:
        f.write(response.text)

