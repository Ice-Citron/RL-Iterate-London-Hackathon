
import hashlib

# The problematic hash for user 1337
target_hash = "8d3533d75ae2c3966d7e0d4fcc69216b"

# Expanded wordlist
wordlist = [
    "password", "admin", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
    "letmein", "trustno1", "dragon", "baseball", "111111", "iloveyou", "master", "sunshine",
    "ashley", "bailey", "passw0rd", "shadow", "123123", "654321", "superman", "qazwsx",
    "michael", "football", "1234567890", "jesus", "princess", "gordonb", "1337", "pablo",
    "smithy", "dvwa", "admin123", "password123", "test", "test123", "hacking", "hacker",
    "hack", "pass123", "123123", "root", "toor", "user", "admin123", "Password1",
    "123456789", "password1", "12345", "1234567", "1234", "123", "12", "11", "10",
    "charlie", "charlie123", "charlie1", "backdoor", "p@ssword", "P@ssw0rd",
    "qwe123", "asd123", "zxc123", "5555555", "777777", "888888", "9999999",
    "aaaaaa", "password!", "Password!", "123!", "!@#$%^", "computer",
]

# Try to find it with simple brute force
print("[*] Attempting to crack: 8d3533d75ae2c3966d7e0d4fcc69216b")
print("[*] Trying common passwords and variations...\n")

found = False
for password in wordlist:
    # Try various cases and encodings
    variations = [
        password,
        password.upper(),
        password.lower(),
        password.capitalize(),
        password.title(),
    ]
    
    for var in variations:
        md5 = hashlib.md5(var.encode()).hexdigest()
        if md5 == target_hash:
            print(f"[+] FOUND! Password is: {var}")
            found = True
            break
        
        # Also try with numbers appended
        for i in range(10):
            md5 = hashlib.md5(f"{var}{i}".encode()).hexdigest()
            if md5 == target_hash:
                print(f"[+] FOUND! Password is: {var}{i}")
                found = True
                break
        
        if found:
            break
    
    if found:
        break

if not found:
    print("[-] Could not find password in wordlist")
    print("\n[*] Let me try checking online databases or using rainbow tables...")
    
    # Try a brute force approach with all lowercase letters + digits
    import itertools
    print("\n[*] Trying a-z0-9 combinations (length 3-5)...")
    
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    for length in range(3, 6):
        print(f"    Trying length {length}...")
        for combo in itertools.combinations_with_replacement(chars, length):
            for perm in itertools.permutations(combo):
                password = ''.join(perm)
                md5 = hashlib.md5(password.encode()).hexdigest()
                if md5 == target_hash:
                    print(f"[+] FOUND! Password is: {password}")
                    found = True
                    break
            if found:
                break
        if found:
            break
        # Break after a bit to save time
        break
    
    if not found:
        print("\n[-] Password not found. It might be a custom password not in common wordlists.")
        print("[*] This hash could be checked using online tools like:")
        print("    - https://crackstation.net/")
        print("    - https://md5.gromweb.com/")
        print("    - https://www.md5online.org/")

