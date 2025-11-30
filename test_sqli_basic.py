
import requests
import re

# Create session and set cookies
session = requests.Session()
session.cookies.set('PHPSESSID', 'u1sbabk40idi42696eoie42qk7')
session.cookies.set('security', 'low')

url_base = "http://31.97.117.123"
sqli_url = f"{url_base}/vulnerabilities/sqli/"

print("[*] Testing basic SQL injection with ID=1\n")

try:
    response = session.get(sqli_url, params={'id': '1'}, timeout=10)
    
    # Look for the vulnerable area
    vulnerable_area = re.search(r'<div class="vulnerable_code_area">(.*?)</div>', response.text, re.DOTALL)
    if vulnerable_area:
        area_content = vulnerable_area.group(1)
        print("[+] Vulnerable Code Area Content:")
        print(area_content[:500])
        print("\n...")
    
    # Look for any user data
    user_data = re.search(r'First name:(.*?)(?:<br|$)', response.text)
    if user_data:
        print("\n[+] Found user data!")
        print(user_data.group(1))
    
    # Save full response
    with open('/tmp/basic_sqli_response.html', 'w') as f:
        f.write(response.text)
    print("\n[+] Full response saved to /tmp/basic_sqli_response.html")
    
except Exception as e:
    print(f"[-] Error: {e}")

