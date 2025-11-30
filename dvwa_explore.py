
import requests
import re
from bs4 import BeautifulSoup

session = requests.Session()
url = "http://31.97.117.123"

# Login with admin:password
login_page = session.get(f"{url}/login.php")
match = re.search(r"user_token'\s+value='([^']+)'", login_page.text)
user_token = match.group(1) if match else ""

data = {
    "username": "admin",
    "password": "password",
    "user_token": user_token,
    "Login": "Login"
}

response = session.post(f"{url}/login.php", data=data, allow_redirects=True)
print("[+] Login successful!")
print(f"[+] Session cookies: {session.cookies.get_dict()}")

# Now let's explore the application
main_page = session.get(f"{url}/index.php")
soup = BeautifulSoup(main_page.text, 'html.parser')

# Look for navigation links and vulnerabilities
print("\n[*] Looking for available pages and vulnerabilities...")
links = soup.find_all('a')
for link in links[:30]:
    href = link.get('href')
    text = link.get_text()
    if href:
        print(f"  - {text}: {href}")


