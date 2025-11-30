
import requests
import sys

# Try admin:admin
session = requests.Session()

# Get the page first to extract token
resp = session.get("http://31.97.117.123/login.php")
print("Initial response status:", resp.status_code)

# Try login with admin:admin
login_data = {
    "username": "admin",
    "password": "admin",
    "Login": "Login",
    "user_token": "574fcd28f93f57c93cb554ecaf3ca520"
}

resp = session.post("http://31.97.117.123/login.php", data=login_data)
print("\nLogin attempt response length:", len(resp.text))
print("Login response contains 'Welcome':", "Welcome" in resp.text)
print("Login response contains 'incorrect':", "incorrect" in resp.text)
print("\nFirst 500 chars of response:")
print(resp.text[:500])

