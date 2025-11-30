
import requests

# Create session and set cookies
session = requests.Session()
session.cookies.set('PHPSESSID', 'u1sbabk40idi42696eoie42qk7')
session.cookies.set('security', 'low')

url_base = "http://31.97.117.123"

print("[*] Checking source code of SQL injection page...\n")

try:
    response = session.get(
        f"{url_base}/vulnerabilities/view_source.php",
        params={'id': 'sqli', 'security': 'low'},
        timeout=10
    )
    
    print(f"[+] Status: {response.status_code}")
    print(f"[+] Response length: {len(response.text)} bytes\n")
    
    # Save the source code
    with open('/tmp/sqli_source.html', 'w') as f:
        f.write(response.text)
    
    print("[+] Source code saved to /tmp/sqli_source.html")
    print("\nFirst 2000 characters:")
    print(response.text[:2000])
    
except Exception as e:
    print(f"[-] Error: {e}")

