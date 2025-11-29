
import subprocess
import hashlib

# MD5 hashes we found
hashes = {
    '5f4dcc3b5aa765d61d8327deb882cf99': ['admin', 'smithy'],
    'e99a18c428cb38d5f260853678922e03': ['gordonb'],
    '8d3533d75ae2c3966d7e0d4fcc69216b': ['1337'],
    '0d107d09f5bbe40cade3de5c71e9e9b7': ['pablo']
}

# Common passwords to try
common_passwords = [
    'password', 'password123', '123456', '12345', '1234567890',
    'admin', 'root', 'toor', 'test', 'guest', 'qwerty',
    'monkey', 'letmein', 'abc123', 'shadow', 'sunshine',
    'batman', 'dragon', 'master', 'hello', 'world',
    'welcome', 'login', 'pass', 'passwd', 'secret',
    'admin123', 'password1', '123123', '111111', 
    'admin123456', 'qwertyuiop', 'monkey123'
]

print("Attempting to crack MD5 hashes...\n")
print("=" * 100)

cracked = {}

for password in common_passwords:
    md5_hash = hashlib.md5(password.encode()).hexdigest()
    
    for hash_value, usernames in hashes.items():
        if md5_hash == hash_value:
            for username in usernames:
                print(f"[+] CRACKED! Hash: {hash_value}")
                print(f"    Username: {username}")
                print(f"    Password: {password}")
                print()
                cracked[hash_value] = password

print("=" * 100)
print(f"\nCracked {len(cracked)} out of {len(hashes)} hashes\n")

if len(cracked) > 0:
    print("Cracked Credentials:")
    for hash_value, password in cracked.items():
        usernames = hashes[hash_value]
        for username in usernames:
            print(f"  {username:<15} : {password}")

