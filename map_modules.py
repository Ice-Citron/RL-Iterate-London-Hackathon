
import requests
import re
from urllib.parse import urljoin

target_url = "http://31.97.117.123/"
session = requests.Session()

# Login first
login_page = session.get(urljoin(target_url, "login.php"))
token_match = re.search(r"user_token' value='([^']+)'", login_page.text)
token = token_match.group(1)

login_data = {
    "username": "admin",
    "password": "password",
    "user_token": token,
    "Login": "Login"
}

response = session.post(urljoin(target_url, "login.php"), data=login_data)

# Get index page to see available modules
index_page = session.get(urljoin(target_url, "index.php"))

# Extract all links to vulnerability modules
links = re.findall(r'href=["\']?([^"\'\s>]+)["\']?', index_page.text)
vuln_links = [l for l in links if 'vulnerabilities' in l.lower() or 'sqli' in l.lower() or 'sql' in l.lower()]

print("[+] Available module links:")
for link in links[:30]:
    print(f"  - {link}")

print("\n\n[+] Index page snippet (looking for SQL Injection):")
if "SQL Injection" in index_page.text:
    idx = index_page.text.find("SQL Injection")
    print(index_page.text[max(0, idx-100):idx+200])
else:
    print("[!] SQL Injection not found in this snippet. Showing page structure:")
    print(index_page.text[:2000])

