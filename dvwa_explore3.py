
import requests
import re

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

# Now let's explore the application
main_page = session.get(f"{url}/index.php")

# Look for navigation links and vulnerabilities
print("\n[*] Looking for available pages...")
links = re.findall(r'href=["\']([^"\']+)["\']', main_page.text)
for link in list(set(links))[:20]:
    print(f"  - {link}")

# Save the main page to check structure
print("\n[*] Main page snippet:")
print(main_page.text[:3000])


