
import requests
import re

session = requests.Session()

# List of potential paths to check
paths = [
    '/phpinfo.php',
    '/info.php',
    '/dvwa/includes/dvwadb.inc.php',
    '/.git/config',
    '/config.php',
    '/db.php',
    '/database.php',
    '/backup.zip',
    '/backup.tar.gz',
    '/.env',
    '/source/',
    '/vulnerabilities/',
]

print("Scanning for accessible paths...\n")
for path in paths:
    try:
        response = requests.get(f'http://31.97.117.123{path}', timeout=5)
        if response.status_code != 404:
            print(f"✓ {path} - Status {response.status_code}")
            if response.status_code == 200:
                print(f"  Content preview: {response.text[:200]}")
    except:
        pass

# Let's also try to access the vulnerabilities section directly
print("\n\nTrying direct access to vulnerability paths...")
vulns = ['sql-injection', 'brute-force', 'users']
for vuln in vulns:
    try:
        url = f'http://31.97.117.123/vulnerabilities/{vuln}/'
        response = requests.get(url, timeout=5)
        print(f"\n{url} - Status {response.status_code}")
        if response.status_code == 200:
            print(f"Content (first 500 chars):\n{response.text[:500]}")
    except Exception as e:
        print(f"Error accessing {url}: {e}")

