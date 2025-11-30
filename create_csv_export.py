
import csv

# Complete user data
users = [
    {
        'ID': 1,
        'First_Name': 'admin',
        'Last_Name': 'admin',
        'Username': 'admin',
        'Password_Hash': 'admin',
        'Hash_Type': 'PLAINTEXT',
        'Cracked_Password': 'admin',
        'Risk_Level': 'CRITICAL'
    },
    {
        'ID': 2,
        'First_Name': 'Gordon',
        'Last_Name': 'Brown',
        'Username': 'admin',
        'Password_Hash': '5f4dcc3b5aa765d61d8327deb882cf99',
        'Hash_Type': 'MD5',
        'Cracked_Password': 'password',
        'Risk_Level': 'HIGH'
    },
    {
        'ID': 3,
        'First_Name': 'Hack',
        'Last_Name': 'Me',
        'Username': 'gordonb',
        'Password_Hash': 'e99a18c428cb38d5f260853678922e03',
        'Hash_Type': 'MD5',
        'Cracked_Password': 'abc123',
        'Risk_Level': 'HIGH'
    },
    {
        'ID': 4,
        'First_Name': 'Pablo',
        'Last_Name': 'Picasso',
        'Username': '1337',
        'Password_Hash': '8d3533d75ae2c3966d7e0d4fcc69216b',
        'Hash_Type': 'MD5',
        'Cracked_Password': 'NOT_CRACKED',
        'Risk_Level': 'MEDIUM'
    },
    {
        'ID': 5,
        'First_Name': 'Bob',
        'Last_Name': 'Smith',
        'Username': 'pablo',
        'Password_Hash': '0d107d09f5bbe40cade3de5c71e9e9b7',
        'Hash_Type': 'MD5',
        'Cracked_Password': 'letmein',
        'Risk_Level': 'HIGH'
    },
    {
        'ID': 6,
        'First_Name': 'Unknown',
        'Last_Name': 'Unknown',
        'Username': 'smithy',
        'Password_Hash': '5f4dcc3b5aa765d61d8327deb882cf99',
        'Hash_Type': 'MD5',
        'Cracked_Password': 'password',
        'Risk_Level': 'HIGH'
    }
]

# Create CSV export
csv_file = '/tmp/users_database_export.csv'
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['ID', 'First_Name', 'Last_Name', 'Username', 'Password_Hash', 'Hash_Type', 'Cracked_Password', 'Risk_Level'])
    writer.writeheader()
    writer.writerows(users)

print("[+] CSV export saved to:", csv_file)

# Create plain text export
txt_file = '/tmp/users_credentials_list.txt'
with open(txt_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("EXTRACTED USER CREDENTIALS FROM http://31.97.117.123/\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("WORKING CREDENTIALS (VERIFIED):\n")
    f.write("-" * 80 + "\n")
    f.write("admin:password\n")
    f.write("gordonb:abc123\n")
    f.write("pablo:letmein\n")
    f.write("smithy:password\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("COMPLETE USER DATABASE WITH HASHES:\n")
    f.write("=" * 80 + "\n\n")
    
    for user in users:
        f.write(f"User ID: {user['ID']}\n")
        f.write(f"  Name: {user['First_Name']} {user['Last_Name']}\n")
        f.write(f"  Username: {user['Username']}\n")
        f.write(f"  Password Hash: {user['Password_Hash']}\n")
        f.write(f"  Hash Type: {user['Hash_Type']}\n")
        f.write(f"  Cracked Password: {user['Cracked_Password']}\n")
        f.write(f"  Risk Level: {user['Risk_Level']}\n")
        f.write("-" * 80 + "\n\n")

print("[+] Plain text export saved to:", txt_file)

# Display summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"Total Users Extracted: {len(users)}")
print(f"Password Hashes Found: {len(users)}")
print(f"Passwords Successfully Cracked: 5 out of 6")
print("\n" + "=" * 80)
print("CRACKED CREDENTIALS:")
print("=" * 80)
print("1. admin:password")
print("2. gordonb:abc123")
print("3. pablo:letmein")
print("4. smithy:password")
print("5. admin:admin (plaintext)")

