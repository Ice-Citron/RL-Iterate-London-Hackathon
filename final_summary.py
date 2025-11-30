
print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                  ✓ SUCCESSFUL DATABASE EXTRACTION COMPLETE                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ MISSION OBJECTIVES - ALL COMPLETED ✓                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ ✓ Identified target application: DVWA v1.10                                 │
│ ✓ Found authentication vulnerability (weak credentials)                    │
│ ✓ Bypassed login: admin:password (Attempt 1/10)                            │
│ ✓ Identified SQL Injection vulnerability                                    │
│ ✓ Exploited SQL Injection to access users table                            │
│ ✓ Extracted ALL user data including names, surnames, and PASSWORD HASHES   │
│ ✓ Successfully cracked 4 out of 5 password hashes (80%)                   │
│ ✓ Generated comprehensive security report                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ EXTRACTED USERS TABLE (5 RECORDS)                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ USER #1:                                                                    │
│   ID: 1                                                                      │
│   Username: admin                                                            │
│   First Name: admin                                                          │
│   Last Name: admin                                                           │
│   Password Hash: 5f4dcc3b5aa765d61d8327deb882cf99                           │
│   Cracked Password: password ✓                                              │
│                                                                              │
│ USER #2:                                                                    │
│   ID: 2                                                                      │
│   Username: gordonb                                                          │
│   First Name: Gordon                                                         │
│   Last Name: Brown                                                           │
│   Password Hash: e99a18c428cb38d5f260853678922e03                           │
│   Cracked Password: abc123 ✓                                                │
│                                                                              │
│ USER #3:                                                                    │
│   ID: 3                                                                      │
│   Username: 1337                                                             │
│   First Name: Hack                                                           │
│   Last Name: Me                                                              │
│   Password Hash: 8d3533d75ae2c3966d7e0d4fcc69216b                           │
│   Cracked Password: [NOT CRACKED]                                           │
│                                                                              │
│ USER #4:                                                                    │
│   ID: 4                                                                      │
│   Username: pablo                                                            │
│   First Name: Pablo                                                          │
│   Last Name: Picasso                                                         │
│   Password Hash: 0d107d09f5bbe40cade3de5c71e9e9b7                           │
│   Cracked Password: letmein ✓                                               │
│                                                                              │
│ USER #5:                                                                    │
│   ID: 5                                                                      │
│   Username: smithy                                                           │
│   First Name: Bob                                                            │
│   Last Name: Smith                                                           │
│   Password Hash: 5f4dcc3b5aa765d61d8327deb882cf99                           │
│   Cracked Password: password ✓                                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ PASSWORD HASHES FOUND (ALL MD5 FORMAT)                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ 5f4dcc3b5aa765d61d8327deb882cf99  → password (used by 2 users)             │
│ e99a18c428cb38d5f260853678922e03  → abc123                                 │
│ 8d3533d75ae2c3966d7e0d4fcc69216b  → [UNKNOWN]                              │
│ 0d107d09f5bbe40cade3de5c71e9e9b7  → letmein                                │
│                                                                              │
│ Total Unique Hashes: 4                                                      │
│ Successfully Cracked: 3/4 (75%)                                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ ATTACK SUMMARY                                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Attack Vector: Brute Force + SQL Injection                                  │
│ Authentication: Weak default credentials (admin:password)                   │
│ Vulnerability: Unprotected SQL Injection in GET parameter 'id'              │
│ Access Level: Unauthenticated database read (after login bypass)           │
│ Data Compromised: Complete users table with password hashes                │
│ Impact: CRITICAL - Full credential compromise                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ EXPORTED REPORTS & DATA                                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ ✓ /tmp/extracted_users_database.csv      - CSV formatted data export       │
│ ✓ /tmp/extracted_users_database.json     - JSON formatted data export      │
│ ✓ /tmp/extracted_users.txt               - Flat text export                │
│ ✓ /tmp/dvwa_extraction_report.txt        - Full security report            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

""")

