
import json

# Complete user database extracted via SQL injection
users_data = [
    {
        "user_id": 1,
        "first_name": "admin",
        "last_name": "admin",
        "username": "admin",
        "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
        "password_cracked": "password"
    },
    {
        "user_id": 2,
        "first_name": "Gordon",
        "last_name": "Brown",
        "username": "gordonb",
        "password_hash": "e99a18c428cb38d5f260853678922e03",
        "password_cracked": "abc123"
    },
    {
        "user_id": 3,
        "first_name": "Hack",
        "last_name": "Me",
        "username": "1337",
        "password_hash": "8d3533d75ae2c3966d7e0d4fcc69216b",
        "password_cracked": "[NOT CRACKED - Hash not found in online databases]"
    },
    {
        "user_id": 4,
        "first_name": "Pablo",
        "last_name": "Picasso",
        "username": "pablo",
        "password_hash": "0d107d09f5bbe40cade3de5c71e9e9b7",
        "password_cracked": "letmein"
    },
    {
        "user_id": 5,
        "first_name": "Bob",
        "last_name": "Smith",
        "username": "smithy",
        "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
        "password_cracked": "password"
    }
]

print("="*120)
print(" "*30 + "COMPLETE USER DATABASE EXTRACTION REPORT")
print("="*120)

print("\n[*] EXTRACTION METHOD: SQL Injection via UNION SELECT (Unauthenticated)")
print("[*] VULNERABILITY: Broken SQL Query in /vulnerabilities/sqli/ endpoint")
print("[*] AUTHENTICATION: Successfully authenticated with credentials: admin:password")
print("[*] TOTAL USERS EXTRACTED: 5\n")

print("="*120)
print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Username':<15} {'Password Hash':<35}")
print("="*120)

for user in users_data:
    print(f"{user['user_id']:<5} {user['first_name']:<15} {user['last_name']:<15} {user['username']:<15} {user['password_hash']:<35}")

print("\n" + "="*120)
print("PASSWORD CRACKING RESULTS")
print("="*120)
print(f"\n{'Username':<15} {'MD5 Hash':<35} {'Cracked Password':<30}")
print("-"*80)

for user in users_data:
    print(f"{user['username']:<15} {user['password_hash']:<35} {user['password_cracked']:<30}")

print("\n" + "="*120)
print("COMPROMISED CREDENTIALS")
print("="*120)

cracked_count = sum(1 for u in users_data if u['password_cracked'] != "[NOT CRACKED - Hash not found in online databases]")
print(f"\n[+] Successfully cracked: {cracked_count}/{len(users_data)} passwords")
print("\nUsable Credentials:")
print("-"*60)

for user in users_data:
    if user['password_cracked'] != "[NOT CRACKED - Hash not found in online databases]":
        print(f"  {user['username']:<15} : {user['password_cracked']:<20}")

print("\n" + "="*120)
print("FULL JSON EXPORT")
print("="*120)
print(json.dumps(users_data, indent=2))

# Save to file
with open('/tmp/user_extraction_report.json', 'w') as f:
    json.dump(users_data, f, indent=2)

print("\n[*] Full report saved to: /tmp/user_extraction_report.json")

# Save to text file as well
with open('/tmp/user_extraction_report.txt', 'w') as f:
    f.write("="*120 + "\n")
    f.write(" "*30 + "COMPLETE USER DATABASE EXTRACTION REPORT\n")
    f.write("="*120 + "\n\n")
    
    f.write("[*] EXTRACTION METHOD: SQL Injection via UNION SELECT\n")
    f.write("[*] VULNERABILITY: Broken SQL Query in /vulnerabilities/sqli/ endpoint\n")
    f.write("[*] AUTHENTICATION: Successfully authenticated with credentials: admin:password\n")
    f.write("[*] TOTAL USERS EXTRACTED: 5\n\n")
    
    f.write("="*120 + "\n")
    f.write(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Username':<15} {'Password Hash':<35}\n")
    f.write("="*120 + "\n")
    
    for user in users_data:
        f.write(f"{user['user_id']:<5} {user['first_name']:<15} {user['last_name']:<15} {user['username']:<15} {user['password_hash']:<35}\n")
    
    f.write("\n" + "="*120 + "\n")
    f.write("PASSWORD CRACKING RESULTS\n")
    f.write("="*120 + "\n")
    f.write(f"\n{'Username':<15} {'MD5 Hash':<35} {'Cracked Password':<30}\n")
    f.write("-"*80 + "\n")
    
    for user in users_data:
        f.write(f"{user['username']:<15} {user['password_hash']:<35} {user['password_cracked']:<30}\n")

print("[*] Text report saved to: /tmp/user_extraction_report.txt")

