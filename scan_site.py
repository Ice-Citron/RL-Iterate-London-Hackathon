
import requests
import os

base_url = "http://31.97.117.123"

# Common paths in DVWA
paths = [
    "/dvwa/",
    "/dvwa/css/",
    "/dvwa/js/",
    "/dvwa/images/",
    "/vulnerabilities/",
    "/help/",
    "/setup.php",
    "/config.php",
    "/database.php",
    "/database.php.bak",
    "/wp-config.php",
    "/config.inc.php",
    "/.htaccess",
    "/web.config",
    "/README.md",
    "/README.txt",
    "/INSTALL.md",
    "/admin/",
    "/phpmyadmin/",
    "/mysql/",
    "/.env",
    "/api/",
]

print("[*] Scanning for accessible paths...")
for path in paths:
    url = base_url + path
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 404:
            print(f"[+] {path} - Status: {response.status_code}")
    except:
        pass

