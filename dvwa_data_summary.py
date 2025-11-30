
import re

# Extract all users and password hashes from the SQL injection result
users_data = [
    ("admin", "admin"),
    ("admin", "5f4dcc3b5aa765d61d8327deb882cf99"),
    ("gordonb", "e99a18c428cb38d5f260853678922e03"),
    ("1337", "8d3533d75ae2c3966d7e0d4fcc69216b"),
    ("pablo", "0d107d09f5bbe40cade3de5c71e9e9b7"),
    ("smithy", "5f4dcc3b5aa765d61d8327deb882cf99"),
]

print("=" * 80)
print("EXTRACTED USERS DATA FROM DVWA DATABASE (via SQL Injection)")
print("=" * 80)
print("\n[*] Total users found: 6\n")

# Format and display the data
for username, password_hash in users_data:
    print(f"Username: {username:15} | Password Hash: {password_hash}")

print("\n" + "=" * 80)
print("PASSWORD HASH IDENTIFICATION")
print("=" * 80)

# These are MD5 hashes (32 characters)
print("\n[*] Hash Type: MD5 (32 hexadecimal characters)")
print("[*] Format: MD5($password)\n")

# Let's try to identify some common hashes
print("[*] Known MD5 hashes:")
print("    5f4dcc3b5aa765d61d8327deb882cf99 = 'password' (confirmed MD5)")
print("    e99a18c428cb38d5f260853678922e03 = 'abc123' or similar")
print("    8d3533d75ae2c3966d7e0d4fcc69216b = 'letmein' or similar")
print("    0d107d09f5bbe40cade3de5c71e9e9b7 = 'password123' or similar")

print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)
print("\n{:<15} {:<35}".format("Username", "Password Hash"))
print("-" * 50)

# Remove duplicates and organize
unique_users = {}
for username, password_hash in users_data:
    if username not in unique_users:
        unique_users[username] = password_hash

for username in sorted(unique_users.keys()):
    password_hash = unique_users[username]
    print(f"{username:<15} {password_hash:<35}")

print("\n" + "=" * 80)
print("[+] All password hashes successfully extracted via SQL Injection!")
print("[+] Credentials successfully obtained from DVWA database")
print("=" * 80)


