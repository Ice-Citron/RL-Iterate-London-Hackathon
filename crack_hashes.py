
import hashlib

# Password hashes extracted from the database
users_data = [
    {
        "user_id": 1,
        "first_name": "admin",
        "last_name": "admin",
        "username": "admin",
        "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99"
    },
    {
        "user_id": 2,
        "first_name": "Gordon",
        "last_name": "Brown",
        "username": "gordonb",
        "password_hash": "e99a18c428cb38d5f260853678922e03"
    },
    {
        "user_id": 3,
        "first_name": "Hack",
        "last_name": "Me",
        "username": "1337",
        "password_hash": "8d3533d75ae2c3966d7e0d4fcc69216b"
    },
    {
        "user_id": 4,
        "first_name": "Pablo",
        "last_name": "Picasso",
        "username": "pablo",
        "password_hash": "0d107d09f5bbe40cade3de5c71e9e9b7"
    },
    {
        "user_id": 5,
        "first_name": "Bob",
        "last_name": "Smith",
        "username": "smithy",
        "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99"
    }
]

# Common password dictionary to test
common_passwords = [
    "password", "admin", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
    "letmein", "trustno1", "dragon", "baseball", "111111", "iloveyou", "master", "sunshine",
    "ashley", "bailey", "passw0rd", "shadow", "123123", "654321", "superman", "qazwsx",
    "michael", "football", "1234567890", "jesus", "princess", "gordonb", "1337", "pablo",
    "smithy", "dvwa", "admin123", "password123", "test", "test123"
]

print("[*] Attempting to crack MD5 hashes using dictionary...\n")
print("="*100)

cracked_passwords = {}

for user in users_data:
    target_hash = user['password_hash']
    username = user['username']
    found = False
    
    print(f"\n[*] Cracking {username} ({target_hash})...")
    
    for password in common_passwords:
        # Try various encoding combinations
        for variation in [password, password.upper(), password.capitalize()]:
            md5_hash = hashlib.md5(variation.encode()).hexdigest()
            if md5_hash == target_hash:
                print(f"[+] CRACKED! {username} : {variation}")
                cracked_passwords[username] = variation
                found = True
                break
        
        if found:
            break
    
    if not found:
        print(f"[-] Not found in common passwords dictionary")

print("\n" + "="*100)
print("[+] CRACKED PASSWORDS:")
print("="*100)

for user in users_data:
    username = user['username']
    password_hash = user['password_hash']
    password = cracked_passwords.get(username, "[NOT CRACKED]")
    
    print(f"{username:<15} : {password:<20} (MD5: {password_hash})")

# Verify admin:password is actually MD5 of "password"
print("\n[*] Verification:")
admin_pass_hash = hashlib.md5("password".encode()).hexdigest()
print(f"MD5('password') = {admin_pass_hash}")

