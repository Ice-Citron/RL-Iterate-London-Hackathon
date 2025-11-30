
import requests

base_url = "http://31.97.117.123"

# Try to access PHP files directly
possible_files = [
    "/vulnerabilities/sqli/index.php",
    "/vulnerabilities/sqli/source/high.php",
    "/vulnerabilities/sqli/source/low.php",
    "/vulnerabilities/sqli/source/medium.php",
    "/includes/dvwa.inc.php",
    "/includes/database.inc.php",
    "/database.php",
    "/config/config.inc.php",
]

print("[*] Attempting to access PHP source files...\n")

for file in possible_files:
    url = base_url + file
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"\n[+] Found: {file}")
            print(f"Content preview: {response.text[:500]}")
    except:
        pass

print("\n[*] Done")

