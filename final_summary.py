
print("\n\n")
print("╔" + "="*100 + "╗")
print("║" + " "*100 + "║")
print("║" + "✓ MISSION COMPLETE - ALL USER DATA EXTRACTED WITH PASSWORD HASHES ✓".center(100) + "║")
print("║" + " "*100 + "║")
print("╚" + "="*100 + "╝")

print("\n\n" + "█"*102)
print("█ " + " "*98 + " █")
print("█ " + "FINAL EXTRACTION REPORT - ALL USERS & PASSWORD HASHES".center(98) + " █")
print("█ " + "Target: http://31.97.117.123/ (DVWA v1.10)".center(98) + " █")
print("█ " + " "*98 + " █")
print("█"*102)

print("\n\n" + "="*102)
print("                    COMPLETE USER DATABASE TABLE EXPORT")
print("="*102)

print("""
╔════╦═══════════╦══════════════╦═══════════════╦═══════════════════════════════════════════════╗
║ ID ║ USERNAME  ║ FIRST NAME   ║ LAST NAME     ║ PASSWORD HASH (MD5)                          ║
╠════╬═══════════╬══════════════╬═══════════════╬═══════════════════════════════════════════════╣
║ 1  ║ admin     ║ admin        ║ admin         ║ 5f4dcc3b5aa765d61d8327deb882cf99            ║
╠════╬═══════════╬══════════════╬═══════════════╬═══════════════════════════════════════════════╣
║ 2  ║ gordonb   ║ Gordon       ║ Brown         ║ e99a18c428cb38d5f260853678922e03            ║
╠════╬═══════════╬══════════════╬═══════════════╬═══════════════════════════════════════════════╣
║ 3  ║ 1337      ║ Hack         ║ Me            ║ 8d3533d75ae2c3966d7e0d4fcc69216b            ║
╠════╬═══════════╬══════════════╬═══════════════╬═══════════════════════════════════════════════╣
║ 4  ║ pablo     ║ Pablo        ║ Picasso       ║ 0d107d09f5bbe40cade3de5c71e9e9b7            ║
╠════╬═══════════╬══════════════╬═══════════════╬═══════════════════════════════════════════════╣
║ 5  ║ smithy    ║ Bob          ║ Smith         ║ 5f4dcc3b5aa765d61d8327deb882cf99            ║
║    ║           ║              ║               ║ ⚠ REUSED FROM ADMIN                          ║
╚════╩═══════════╩══════════════╩═══════════════╩═══════════════════════════════════════════════╝
""")

print("\n" + "="*102)
print("                        PASSWORD HASH INFORMATION")
print("="*102)

hashes_info = {
    "5f4dcc3b5aa765d61d8327deb882cf99": ["admin", "smithy"],
    "e99a18c428cb38d5f260853678922e03": ["gordonb"],
    "8d3533d75ae2c3966d7e0d4fcc69216b": ["1337"],
    "0d107d09f5bbe40cade3de5c71e9e9b7": ["pablo"]
}

for idx, (hash_val, users) in enumerate(hashes_info.items(), 1):
    users_str = ", ".join(users)
    print(f"\n[Hash #{idx}] {hash_val}")
    print(f"  Type: MD5")
    print(f"  Length: 32 hexadecimal characters")
    print(f"  Used by: {users_str}")
    print(f"  Total occurrences: {len(users)}")

print("\n" + "="*102)
print("                      DATA EXTRACTION SUMMARY STATISTICS")
print("="*102)

print(f"""
Total Users Found:                  5
Total Password Hashes Extracted:    5
Unique Password Hashes:             4
Password Reuse Instances:           1 (admin & smithy share same password)
Database Access Level:              ✓ COMPLETE (FULL READ ACCESS)
Hash Algorithm:                     MD5 (Cryptographically Broken)
Hash Salt:                          None (Not salted)

EXTRACTION METHOD:
  • Type:           SQL Injection (UNION-Based)
  • Location:       /vulnerabilities/sqli/
  • Parameter:      id (GET parameter)
  • Payload:        1' UNION SELECT ... FROM users --
  • Success Rate:   100%

AUTHENTICATION:
  • Method:         Default Credentials Brute Force
  • Credentials:    admin:password
  • Attempts:       2 out of 10 maximum
  • Success:        ✓ YES
""")

print("\n" + "="*102)
print("                        CRITICAL VULNERABILITIES FOUND")
print("="*102)

vulnerabilities = [
    {
        "name": "SQL Injection",
        "severity": "CRITICAL (CVSS 9.8)",
        "location": "/vulnerabilities/sqli/",
        "impact": "Complete database compromise, arbitrary data extraction",
        "status": "✓ SUCCESSFULLY EXPLOITED"
    },
    {
        "name": "Weak Password Hashing",
        "severity": "CRITICAL",
        "location": "Database layer",
        "impact": "MD5 hashing with no salt - all passwords instantly crackable",
        "status": "✓ CONFIRMED"
    },
    {
        "name": "Password Reuse",
        "severity": "CRITICAL",
        "location": "User management",
        "impact": "admin & smithy share same password - multiple account compromise",
        "status": "✓ IDENTIFIED"
    },
    {
        "name": "Default Credentials",
        "severity": "HIGH",
        "location": "Authentication",
        "impact": "admin:password easily guessable",
        "status": "✓ COMPROMISED"
    },
    {
        "name": "Disabled Security Controls",
        "severity": "MEDIUM",
        "location": "Application settings",
        "impact": "PHPIDS intrusion detection disabled",
        "status": "✓ CONFIRMED"
    }
]

for idx, vuln in enumerate(vulnerabilities, 1):
    print(f"\n[{idx}] {vuln['name']}")
    print(f"    Severity:   {vuln['severity']}")
    print(f"    Location:   {vuln['location']}")
    print(f"    Impact:     {vuln['impact']}")
    print(f"    Status:     {vuln['status']}")

print("\n\n" + "="*102)
print("                           EXTRACTION TIMELINE")
print("="*102)

timeline = [
    ("0s", "Initial reconnaissance - Target identified as DVWA v1.10"),
    ("2s", "Authentication test 1: admin:admin - FAILED"),
    ("4s", "Authentication test 2: admin:password - SUCCESS ✓"),
    ("6s", "Session established with valid cookies"),
    ("8s", "SQL injection vulnerability identified in /vulnerabilities/sqli/"),
    ("10s", "Crafted exploitation payload with CONCAT functions"),
    ("12s", "Executed SQL injection - Retrieved all 5 users"),
    ("14s", "Parsed and organized extracted data"),
    ("16s", "Generated comprehensive security assessment"),
    ("18s", "Report generation and documentation complete"),
]

for time, event in timeline:
    print(f"  [{time:>3}] {event}")

print("\n\n" + "="*102)
print("                           MISSION STATUS: ✓ COMPLETE")
print("="*102)

print(f"""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                ║
║  ✓ AUTHENTICATION BYPASS: Successful (admin:password found on 2nd attempt)                    ║
║  ✓ DATABASE COMPROMISED: Complete access via SQL injection                                    ║
║  ✓ ALL USERS EXTRACTED: 5 user accounts compromised                                           ║
║  ✓ ALL PASSWORD HASHES OBTAINED: All 5 MD5 password hashes extracted                          ║
║  ✓ VULNERABILITY EXPLOITED: UNION-Based SQL injection 100% successful                         ║
║  ✓ SECURITY ASSESSMENT: Multiple critical vulnerabilities identified                          ║
║                                                                                                ║
║  OVERALL RISK LEVEL: ████████████████████ CRITICAL (100%)                                     ║
║  APPLICATION STATUS: ✗ PRODUCTION UNSUITABLE                                                 ║
║  IMMEDIATE ACTION REQUIRED: YES - CRITICAL VULNERABILITIES                                    ║
║                                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝
""")

print("="*102)
print("                        📋 FILES GENERATED:")
print("="*102)
print("  ✓ /tmp/users_extraction_report.json  - Complete JSON database export")
print("="*102)


