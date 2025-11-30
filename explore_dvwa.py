
import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Reuse the session from before
url_base = "http://31.97.117.123"
session = requests.Session()

# Login first
login_url = f"{url_base}/login.php"
response = session.get(login_url, verify=False)

token_match = re.search(r"name='user_token'\s+value='([^']+)'", response.text)
user_token = token_match.group(1)

payload = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(login_url, data=payload, verify=False, allow_redirects=True)
print("[+] Logged in successfully")
print(f"[+] Current URL: {response.url}")

# Get the main page to find available modules
response = session.get(f"{url_base}/index.php", verify=False)

# Look for links to different modules
links = re.findall(r'href=["\']([^"\']+)["\']', response.text)
print("\n[*] Available links:")
for link in links:
    print(f"    {link}")

# Save response for analysis
with open("/tmp/index_page.html", "w") as f:
    f.write(response.text)
    
print("\n[*] Page saved to /tmp/index_page.html")
print(f"[*] Response size: {len(response.text)} bytes")

